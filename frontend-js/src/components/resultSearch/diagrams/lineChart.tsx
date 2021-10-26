import React, { ChangeEvent, ReactElement, useState } from 'react';
import { Benchmark, Result } from 'api';
import { Form } from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import { fetchSubkey, getSubkeyName } from 'components/resultSearch/jsonKeyHelpers';
import { Ordered } from 'components/ordered';
import { InputWithSuggestions } from 'components/inputWithSuggestions';

enum Mode {
    Simple,
    Linear,
    Logarithmic,
}

const CHART_COLORS = [
    'rgb(255, 99, 132)', // red
    'rgb(255, 159, 64)', // orange
    'rgb(255, 205, 86)', // yellow
    'rgb(75, 192, 192)', // green
    'rgb(54, 162, 235)', // blue
    'rgb(153, 102, 255)', // purple
    'rgb(201, 203, 207)', // gray
];

const BACKGROUND_COLORS = [
    'rgba(255, 99, 132, 0.5)', // red
    'rgba(255, 159, 64, 0.5)', // orange
    'rgba(255, 205, 86, 0.5)', // yellow
    'rgba(75, 192, 192, 0.5)', // green
    'rgba(54, 162, 235, 0.5)', // blue
    'rgba(153, 102, 255, 0.5)', // purple
    'rgba(201, 203, 207, 0.5)', // gray
];

function LineChart(props: {
    results: Ordered<Result>[];
    benchmark?: Benchmark;
    suggestions?: string[];
}): ReactElement {
    const [mode, setMode] = useState(Mode.Simple);

    const [grouping, setGrouping] = useState(false);

    const [xAxis, setXAxis] = useState('');
    const [yAxis, setYAxis] = useState('');

    function analyzeData(results: Ordered<Result>[]) {
        let sameSite = true;
        let columnsAreNumbers = true;

        // test if sites are the same all across and if it's an integer range
        if (results.length !== 0) {
            const siteId = results[0].site.id;
            for (const result of results) {
                sameSite = sameSite && result.site.id === siteId;
                columnsAreNumbers =
                    columnsAreNumbers && typeof fetchSubkey(result.json, xAxis) === 'number';
            }
        } else {
            sameSite = false;
            columnsAreNumbers = false;
        }

        return {
            sameSite,
            columnsAreNumbers,
        };
    }

    const properties = analyzeData(props.results);

    function processInput(results: Ordered<Result>[]) {
        const labels = []; // labels below graph
        const dataPoints = [];

        // grouping-by-site behaviour
        // Linear and Logarithmic mode require numeric x / column values
        if (grouping && (mode === Mode.Linear || mode === Mode.Logarithmic)) {
            const datasets = new Map<
                string,
                { siteName: string; data: { x: number; y: number }[] }
            >();
            const labelSet = new Set<number>();

            for (const result of results) {
                const x = fetchSubkey(result.json, xAxis) as number;
                const y = fetchSubkey(result.json, yAxis) as number;
                if (datasets.get(result.site.id) === undefined) {
                    datasets.set(result.site.id, { siteName: result.site.name, data: [] });
                }
                datasets.get(result.site.id)?.data.push({ x, y });
                dataPoints.push({ x, y });
                labelSet.add(x);
            }

            const data: Record<string, unknown>[] = [];
            let colorIndex = 0;
            datasets.forEach(function (dataMeta, site, _) {
                data.push({
                    label: dataMeta.siteName,
                    backgroundColor: BACKGROUND_COLORS[colorIndex],
                    borderColor: CHART_COLORS[colorIndex],
                    borderWidth: 1,
                    data: dataMeta.data,
                    spanGaps: true,
                });
                colorIndex++;
            });

            return {
                labels: Array.from(labelSet).sort((a, b) => a - b),
                datasets: data,
            };
        }

        // default behaviour
        for (const result of results) {
            const x = fetchSubkey(result.json, xAxis) as number | string;
            const y = fetchSubkey(result.json, yAxis) as number | string;
            if (x === undefined || y === undefined) {
                continue;
            }
            let label = x.toString();
            if (!properties.sameSite) {
                label += ' (' + result.site.name + ')';
            }
            dataPoints.push({ x: x, y });
            labels.push(label);
        }

        return {
            labels: labels,
            datasets: [
                {
                    label: getSubkeyName(yAxis),
                    backgroundColor: BACKGROUND_COLORS[0],
                    borderColor: CHART_COLORS[0],
                    borderWidth: 1,
                    data: dataPoints,
                    spanGaps: true,
                },
            ],
        };
    }

    return (
        <>
            <Form.Group className="mb-1">
                <Form.Select
                    onChange={(e: ChangeEvent<HTMLSelectElement>) => {
                        setMode(parseInt(e.target.value));
                    }}
                >
                    <option value={Mode.Simple}>Simple</option>
                    <option value={Mode.Linear} disabled={!properties.columnsAreNumbers}>
                        Linear
                    </option>
                    <option value={Mode.Logarithmic} disabled={!properties.columnsAreNumbers}>
                        Logarithmic
                    </option>
                </Form.Select>
            </Form.Group>
            <Form.Group className="mb-1">
                <Form.Check
                    type="switch"
                    label="Group values by site (only in linear & logarithmic mode)"
                    onChange={(e) => setGrouping(e.target.checked)}
                    disabled={mode !== Mode.Linear && mode !== Mode.Logarithmic}
                />
            </Form.Group>
            <Form.Group className="mb-1">
                <InputWithSuggestions
                    placeholder="x axis"
                    setInput={(i) => setXAxis(i)}
                    suggestions={props.suggestions}
                />
            </Form.Group>
            <Form.Group>
                <InputWithSuggestions
                    placeholder="y axis"
                    setInput={(i) => setYAxis(i)}
                    suggestions={props.suggestions}
                />
            </Form.Group>

            {xAxis.length > 0 && yAxis.length > 0 && (
                <Line
                    data={processInput(props.results)}
                    options={{
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'bottom',
                            },
                            title: {
                                display: true,
                                text: 'Line Graph',
                            },
                        },
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: xAxis,
                                },
                            },
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: yAxis,
                                },
                                type: mode === Mode.Logarithmic ? 'logarithmic' : 'linear',
                            },
                        },
                        elements: {
                            line: {
                                tension: 0,
                            },
                        },
                        tooltips: {
                            callbacks: {
                                title: function (
                                    tooltipItem: {
                                        label: string;
                                        xLabel: string;
                                        yLabel: string;
                                    }[],
                                    _: unknown
                                ) {
                                    return (
                                        tooltipItem[0].yLabel + ' (' + tooltipItem[0].label + ')'
                                    );
                                },
                            },
                        },
                    }}
                />
            )}

            {/* TODO: download png / csv buttons */}
        </>
    );
}

const LineChartMeta = {
    element: LineChart,
    name: 'Line Chart',
    id: '0',
};

export default LineChartMeta;
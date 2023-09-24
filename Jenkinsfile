// SPDX-FileCopyrightText: Copyright contributors to the Software Quality Assurance as a Service (SQAaaS) project <sqaaas@ibergrid.eu>
//
// SPDX-License-Identifier: GPL-3.0-only

@Library(['github.com/indigo-dc/jenkins-pipeline-library@2.1.1']) _

def projectConfig

pipeline {
    agent any

    environment {
        dockerhub_credentials = "o3as-dockerhub-vykozlov"
    }

    stages {
        stage('SQA baseline dynamic stages') {
            steps {
                script {
                    projectConfig = pipelineConfig(
                        configFile: '.sqa/config_custom.yml'
                    )
                    buildStages(projectConfig)
                }
            }
        stage('SQA baseline criterion: QC.Sec & QC.Sty') {
            steps {
                script {
                    projectConfig = pipelineConfig(
                        configFile: '.sqa/config.yml',
                        scmConfigs: [ localBranch: true ],
                        validatorDockerImage: 'eoscsynergy/jpl-validator:2.4.0'
                    )
                    buildStages(projectConfig)
                }
            }
            post {
                cleanup {
                    cleanWs()
                }
            }
        }
    }
}

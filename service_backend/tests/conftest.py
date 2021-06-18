"""Defines fixtures available to all tests.
See: https://pytest-flask.readthedocs.io/en/latest/features.html
"""
import logging
import os

from backend import create_app, database
from backend.extensions import flaat
from flaat import tokentools
from pytest import fixture
from pytest_postgresql.factories import DatabaseJanitor
from sqlalchemy import orm

TEST_DB = 'test_database'
VERSION = 12.2  # postgresql version number
Session = orm.scoped_session(orm.sessionmaker())


@fixture(scope='session')
def sql_database(postgresql_proc):
    """Create a temp Postgres database for the tests."""
    USER = postgresql_proc.user
    HOST = postgresql_proc.host
    PORT = postgresql_proc.port
    with DatabaseJanitor(USER, HOST, PORT, TEST_DB, VERSION) as db:
        yield db


@fixture(scope='session')
def session_environment(sql_database):
    """Patch fixture to set test env variables."""
    # Flask framework environments
    os.environ['SECRET_KEY'] = 'not-so-secret-for-testing'
    # Database environments
    os.environ['DB_ENGINE'] = 'postgresql'
    os.environ['DB_USER'] = str(sql_database.user)
    os.environ['DB_PASSWORD'] = ""
    os.environ['DB_HOST'] = str(sql_database.host)
    os.environ['DB_PORT'] = str(sql_database.port)
    os.environ['DB_NAME'] = str(sql_database.db_name)
    # OIDC environments
    os.environ['OIDC_CLIENT_ID'] = "eosc-perf"
    os.environ['OIDC_CLIENT_SECRET'] = "not-so-secret-for-testing"


@fixture(scope="session")
def app(session_environment):
    """Create application for the tests."""
    app = create_app(config_base="backend.settings", TESTING=True)
    app.logger.setLevel(logging.CRITICAL)
    return app


@fixture(scope='session')
def db(app):
    """Create database for the tests."""
    database.db.app = app
    Session.configure(bind=database.db.engine)
    database.db.session = Session
    database.db.create_all()
    yield database.db
    database.db.drop_all()


@fixture(scope='function')
def session(db):
    """Creates a new database session for a test."""
    session = Session()  # Prepare a new, clean session
    session.begin(nested=True)  # Rollback app commits
    yield session
    session.rollback()  # Discard test changes
    Session.remove()  # Next test gets a new Session()


@fixture(scope='function')
def grant_logged(monkeypatch):
    """Patch fixture to test function as logged user."""
    monkeypatch.setenv(
        "DISABLE_AUTHENTICATION_AND_ASSUME_AUTHENTICATED_USER",
        "YES"
    )


@fixture(scope='function')
def grant_admin(monkeypatch, grant_logged):
    """Patch fixture to test function as admin user."""
    monkeypatch.setenv(
        "DISABLE_AUTHENTICATION_AND_ASSUME_VALID_GROUPS",
        "YES"
    )


@fixture(scope='function')
def token_sub(request):
    """Returns the sub to include on the user token."""
    return request.param if hasattr(request, 'param') else None


@fixture(scope='function')
def token_iss(request):
    """Returns the iss to include on the user token."""
    return request.param if hasattr(request, 'param') else None


@fixture(scope='function')
def mock_token_info(monkeypatch, token_sub, token_iss):
    """Patch fixture to test function with valid oidc token."""
    monkeypatch.setattr(
        tokentools,
        "get_accesstoken_info",
        lambda _: {'body': {'sub': token_sub, 'iss': token_iss}}
    )


@fixture(scope='function')
def introspection_email(request):
    """Returns the email to be returned by the introspection endpoint."""
    return request.param if hasattr(request, 'param') else None


@fixture(scope='function')
def mock_introspection_info(monkeypatch, introspection_email):
    """Patch fixture to test function with valid oidc token."""
    monkeypatch.setattr(
        flaat,
        "get_info_from_introspection_endpoints",
        lambda _: {'email': introspection_email}
    )


@fixture(scope='function')
def endpoint(request):
    """Fixture that return the endpoint for the request."""
    return request.param


@fixture(scope='function')
def query(request):
    """Fixture that return the query for the request."""
    return request.param if hasattr(request, 'param') else {}


@fixture(scope='function')
def body(request):
    """Fixture that return the body for the request."""
    return request.param if hasattr(request, 'param') else {}


@fixture(scope='function')
def response_GET(client, url):
    """Fixture that return the result of a GET request."""
    return client.get(url)


@fixture(scope='function')
def response_POST(client, url, body):
    """Fixture that return the result of a POST request."""
    return client.post(url, json=body)


@fixture(scope='function')
def response_PUT(client, url, body):
    """Fixture that return the result of a PUT request."""
    return client.put(url, json=body)


@fixture(scope='function')
def response_DELETE(client, url):
    """Fixture that return the result of a DELETE request."""
    return client.delete(url)

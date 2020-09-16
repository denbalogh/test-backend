import pytest
import os
import csv

import main as healthcheck_backend
from main import app
from setup import mock_data
from database import db
from tempfile import mkstemp
from TestClient import TestClient


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        for marker in item.iter_markers(name="label"):
            label = marker.args[0]
            # item.user_properties.append(("label", label))
            item.add_report_section("call", "stdout", label)

@pytest.fixture(scope="module")
def unauthorized_client(tempdb):
    healthcheck_backend.app.test_client_class = TestClient
    healthcheck_backend.app.config['SQLALCHEMY_DATABASE_URI'] = tempdb
    client = healthcheck_backend.app.test_client()
    return client

@pytest.fixture(scope="module")
def client_factory(tempdb):
    healthcheck_backend.app.test_client_class = TestClient
    healthcheck_backend.app.config['SQLALCHEMY_DATABASE_URI'] = tempdb

    return healthcheck_backend.app.test_client

@pytest.fixture(scope="module")
def client(credentials, tempdb):
    healthcheck_backend.app.test_client_class = TestClient
    healthcheck_backend.app.config['SQLALCHEMY_DATABASE_URI'] = tempdb
    client = healthcheck_backend.app.test_client()

    client.login(credentials)

    yield client

    client.logout()

@pytest.fixture(scope="session")
def data():
    def _get_data_set(name):
        filename = f"{os.path.dirname(os.path.realpath(__file__))}/data/{name}.csv"
        with open(filename, "r") as datafile:
            return [dict(row) for row in csv.DictReader(datafile)]

    return _get_data_set

@pytest.fixture(scope="session")
def credentials(data):
    return data("credentials")[0]

@pytest.fixture(scope="module")
def tempdb():
    handler, path = mkstemp(suffix=".db")
    os.close(handler)

    db_connectstring = f"sqlite:///{path}"
    healthcheck_backend.app.config['SQLALCHEMY_DATABASE_URI'] = db_connectstring
    
    with healthcheck_backend.app.app_context():
        db.drop_all()
        db.create_all()
        mock_data()

    yield db_connectstring

    os.remove(path)
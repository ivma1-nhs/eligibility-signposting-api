import pytest
from faker import Faker
from flask import Flask
from flask.testing import FlaskClient

from eligibility_signposting_api.app import create_app


@pytest.fixture(scope="session")
def app() -> Flask:
    return create_app()


@pytest.fixture(scope="session")
def client(app) -> FlaskClient:
    return app.test_client()


@pytest.fixture(scope="session")
def faker() -> Faker:
    return Faker("en_UK")

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

import pytest
from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    """Client déjà connecté — évite de répéter le login dans chaque test."""
    client.post("/login", data={"username": "admin", "password": "admin123"})
    return client

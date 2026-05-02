import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    response = client.post(
        "/api/auth/signup",
        json={"name": "Ada", "email": "ada@example.com", "password": "strong-password"},
    )
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

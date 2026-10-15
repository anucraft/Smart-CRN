import pytest

from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models import Admin


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
    admin = Admin(email="owner@shop.test", name="Owner")
    admin.set_password("s3cret-pass")
    db.session.add(admin)
    db.session.commit()
    token = client.post("/api/auth/login", json={"email": "owner@shop.test", "password": "s3cret-pass"}).get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

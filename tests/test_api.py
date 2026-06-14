from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_token():
    response = client.post("/token", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_query_no_auth():
    response = client.post("/query/", json={"question": "test"})
    assert response.status_code == 401

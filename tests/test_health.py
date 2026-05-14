"""Tests FastAPI — C12 : tests automatisés avec TestClient."""
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_returns_project_name():
    response = client.get("/health")
    assert response.json()["project"] == "RITA"


def test_briefing_without_api_key_returns_403():
    response = client.post("/briefing?ticker=AAPL")
    assert response.status_code == 403

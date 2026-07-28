"""Tests FastAPI — C12 : tests automatisés avec TestClient."""
from unittest.mock import patch

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


def test_briefing_avec_cle_valide_retourne_le_briefing(monkeypatch):
    monkeypatch.setenv("RITA_API_KEY", "dev-key")
    resultat_simule = {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99,
                        "currency": "EUR", "briefing": "Texte du briefing.", "error": ""}
    with patch("api.main.generer_briefing_complet", return_value=resultat_simule):
        response = client.post("/briefing?ticker=MC.PA", headers={"X-API-Key": "dev-key"})

    assert response.status_code == 200
    assert response.json()["briefing"] == "Texte du briefing."


def test_briefing_retourne_502_si_erreur_scout(monkeypatch):
    monkeypatch.setenv("RITA_API_KEY", "dev-key")
    resultat_simule = {"ticker": "XXX.PA", "price": 0.0, "change_pct": 0.0,
                        "currency": "", "briefing": "", "error": "no data"}
    with patch("api.main.generer_briefing_complet", return_value=resultat_simule):
        response = client.post("/briefing?ticker=XXX.PA", headers={"X-API-Key": "dev-key"})

    assert response.status_code == 502

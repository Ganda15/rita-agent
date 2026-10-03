"""Le traçage ne fait jamais tomber un briefing, même quand Langfuse casse (C11, C20).

Revue Codex de la PR #58 (03/10/2026), remarque P1 : le module promettait l'isolation
(« le traçage ne doit jamais faire échouer un briefing ») mais ne la tenait que pour la
construction du client. Un `flush()` qui lève (exportateur en panne, réseau coupé, quota
dépassé) remontait depuis le `finally` de `briefing()` et transformait un briefing valide en
erreur 500 ; une ouverture d'observation ou un `update()` qui lève faisaient de même.

Règle testée : toute opération Langfuse qui échoue se dégrade en une ligne de journal
WARNING, et le briefing continue comme si le traçage était coupé.
"""
import logging
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from src import traces
from src.llm import generer_texte
from tests.conftest import CLE_DE_TEST

client_http = TestClient(app)


class _Observation:
    def __init__(self, casser_update=False):
        self.casser_update = casser_update

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def update(self, **kwargs):
        if self.casser_update:
            raise ConnectionError("exportateur injoignable (update)")

    def score_trace(self, **kwargs):
        if self.casser_update:
            raise ConnectionError("exportateur injoignable (score)")


class _ClientCasse:
    """Un client Langfuse dont une opération donnée échoue, les autres passent."""

    def __init__(self, casser="flush"):
        self.casser = casser

    def create_trace_id(self, seed=None):
        return "0" * 32

    def start_as_current_observation(self, **kwargs):
        if self.casser == "ouverture":
            raise RuntimeError("SDK Langfuse en panne (ouverture)")
        return _Observation(casser_update=(self.casser == "update"))

    def flush(self):
        if self.casser == "flush":
            raise ConnectionError("exportateur injoignable (flush)")


@pytest.fixture(autouse=True)
def _client_casse_par_defaut(monkeypatch):
    monkeypatch.delenv("LANGFUSE_TRACING_ENABLED", raising=False)
    traces.reinitialiser()
    yield
    traces.reinitialiser()


def _resultat():
    return {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99, "currency": "EUR",
            "error": "", "briefing": "Le titre recule de 1,99 % sur la séance."}


def _briefing_avec(client):
    with patch.object(traces, "client_traces", return_value=client), \
         patch("api.main.generer_briefing_complet", return_value=_resultat()):
        return client_http.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})


@pytest.mark.parametrize("casse", ["flush", "ouverture", "update"])
def test_une_panne_de_langfuse_ne_fait_pas_tomber_le_briefing(casse, caplog):
    with caplog.at_level(logging.WARNING, logger="src.traces"):
        reponse = _briefing_avec(_ClientCasse(casse))
    assert reponse.status_code == 200, reponse.text
    assert reponse.json()["briefing"].startswith("Le titre recule")
    assert any("Langfuse" in r.getMessage() for r in caplog.records), \
        "la panne doit laisser une ligne WARNING, pas disparaitre en silence"


@pytest.mark.parametrize("casse", ["flush", "ouverture", "update"])
def test_une_panne_de_langfuse_ne_fait_pas_tomber_generer_texte(casse, monkeypatch, caplog):
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    with patch.object(traces, "client_traces", return_value=_ClientCasse(casse)),          patch("src.llm._appel_anthropic", return_value="ok anthropic"),          caplog.at_level(logging.WARNING, logger="src.traces"):
        texte = generer_texte("prompt test")
    assert texte == "ok anthropic"
    assert any(r.levelno == logging.WARNING for r in caplog.records)


def test_vider_ne_propage_pas_une_erreur_d_export(caplog):
    with patch.object(traces, "client_traces", return_value=_ClientCasse("flush")), \
         caplog.at_level(logging.WARNING, logger="src.traces"):
        traces.vider()  # ne doit pas lever
    assert any("Langfuse" in r.getMessage() for r in caplog.records)


def test_une_erreur_de_la_route_remonte_toujours_meme_si_langfuse_casse():
    """L'isolation va dans un seul sens : on avale les erreurs du traçage, jamais celles du
    métier. Une 502 reste une 502 quand le flush casse en plus."""
    with patch.object(traces, "client_traces", return_value=_ClientCasse("flush")), \
         patch("api.main.generer_briefing_complet", return_value={**_resultat(), "error": "no data", "briefing": ""}):
        reponse = client_http.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})
    assert reponse.status_code == 502

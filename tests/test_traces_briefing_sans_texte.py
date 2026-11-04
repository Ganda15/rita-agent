"""Sprint 4, tâche B3 : les traces du briefing ne gardent que des métadonnées (décision D9, spec CA3.6).

La trace d'un briefing ne reçoit ni le prompt ni la réponse brute du modèle, y compris en cas d'erreur ou de sortie
refusée : seulement le modèle, les jetons, la durée (l'ouverture et la fermeture des étapes) et le motif.
L'enregistrement est empêché à la source : masquer après coup ne garantirait pas qu'aucune copie n'est partie. Des
textes fictifs reconnaissables le prouvent, et les métadonnées gardées ne les recopient pas, même en partie. Le client
Langfuse est remplacé par un double qui enregistre tout ; aucun réseau.
"""
import logging
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from src import traces
from src.llm import generer_texte
from tests.conftest import CLE_DE_TEST
from tests.test_trace_chemin import _briefing, _CollectionVide
from tests.test_traces import _FauxClient
from tests.test_traces_question import _EnregistreurAvecIdentifiant
from tests.test_workflow import scout_lvmh

MARQUEUR_PROMPT = "MARQUEUR-PROMPT-4d1e"
MARQUEUR_REPONSE = "MARQUEUR-REPONSE-8a7f"


@pytest.fixture(autouse=True)
def _sans_cles(monkeypatch):
    for variable in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_TRACING_ENABLED"):
        monkeypatch.delenv(variable, raising=False)
    traces.reinitialiser()


def _absents(journal) -> bool:
    """Ni les marqueurs, ni leurs 12 premiers caractères : une copie partielle compte aussi."""
    texte = repr(journal)
    return all(marqueur not in texte and marqueur[:12] not in texte for marqueur in (MARQUEUR_PROMPT, MARQUEUR_REPONSE))


def test_ni_prompt_ni_reponse_dans_la_trace_en_succes(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    client = _FauxClient()
    with patch("src.traces.client_traces", return_value=client), \
         patch("src.llm._appel_anthropic", return_value=MARQUEUR_REPONSE):
        assert generer_texte(f"Prompt du briefing {MARQUEUR_PROMPT}") == MARQUEUR_REPONSE
    # La trace a bien été écrite : sinon, l'absence des marqueurs ne prouverait rien.
    assert any(evenement == "ouvre" for evenement, _ in client.journal)
    assert _absents(client.journal)


def test_ni_prompt_ni_reponse_en_erreur(monkeypatch):
    # Le message d'une erreur peut recopier le prompt (un fournisseur qui le cite) : seul son type part.
    monkeypatch.setenv("LLM_ORDRE", "foundry,anthropic")
    client = _FauxClient()
    with patch("src.traces.client_traces", return_value=client), \
         patch("src.llm._appel_foundry", side_effect=RuntimeError(f"refus du fournisseur : {MARQUEUR_PROMPT}")), \
         patch("src.llm._appel_anthropic", return_value=MARQUEUR_REPONSE):
        generer_texte(f"Prompt du briefing {MARQUEUR_PROMPT}")
    erreurs = [k for (evenement, k) in client.journal if evenement == "update" and k.get("level") == "ERROR"]
    assert [e["status_message"] for e in erreurs] == ["RuntimeError"]
    assert _absents(client.journal)


def test_ni_prompt_ni_reponse_quand_la_sortie_est_refusee(monkeypatch):
    reponse, journal = _briefing(f"Nous recommandons l'achat de cette valeur. {MARQUEUR_REPONSE}", monkeypatch)
    assert reponse.json()["conforme_amf"] is False
    assert journal and _absents(journal)


def test_la_trace_garde_modele_jetons_et_duree(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    client = _FauxClient()
    reponse = traces.Reponse(texte=MARQUEUR_REPONSE, modele="claude-sonnet-5", usage={"input": 120, "output": 45})
    with patch("src.traces.client_traces", return_value=client), \
         patch("src.llm._appel_anthropic", return_value=reponse):
        generer_texte(f"Prompt du briefing {MARQUEUR_PROMPT}")
    mises_a_jour = [k for (evenement, k) in client.journal if evenement == "update"]
    assert any(k.get("model") == "claude-sonnet-5" for k in mises_a_jour)
    assert any(k.get("usage_details") == {"input": 120, "output": 45} for k in mises_a_jour)
    # La durée : chaque étape est ouverte puis fermée, Langfuse mesure l'écart.
    assert ("ferme", "llm-anthropic") in client.journal and ("ferme", "briefing-llm") in client.journal
    assert _absents(client.journal)


def test_ni_prompt_ni_reponse_quand_tous_les_fournisseurs_echouent(monkeypatch, caplog):
    """Revue de sécurité automatique du commit dc2b323 : quand tous les fournisseurs échouent, l'erreur finale remonte à
    travers les étapes `redacteur` et `briefing`. Son message, qui reprenait celui de chaque fournisseur, ne doit
    atteindre ni la trace ni le journal. Le double du SDK enregistre ce que reçoit la fermeture de chaque étape,
    exception comprise (tests/test_llm_json.py)."""
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    client = _EnregistreurAvecIdentifiant()
    with patch("src.traces.client_traces", return_value=client), \
         patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("rag.recherche._collection", return_value=_CollectionVide()), \
         patch("src.llm._appel_anthropic", side_effect=RuntimeError(f"refus du fournisseur : {MARQUEUR_PROMPT}")), \
         caplog.at_level(logging.DEBUG):
        reponse = TestClient(app).post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})
    # Refonte 001, tâche 3 (spécification R4, validée le 04/11) : tous les fournisseurs en panne donnent désormais 503
    # AUCUN_FOURNISSEUR, et non plus le 500 générique. La règle de sécurité de ce test ne change pas.
    assert reponse.status_code == 503
    assert reponse.json()["detail"]["code"] == "AUCUN_FOURNISSEUR"
    assert MARQUEUR_PROMPT not in reponse.text and MARQUEUR_PROMPT[:12] not in reponse.text
    # L'erreur a bien traversé les étapes tracées : sinon, l'absence du marqueur ne prouverait rien.
    noms = [options.get("name") for (evenement, options) in client.journal if evenement == "ouvre"]
    assert "briefing" in noms and "redacteur" in noms
    assert _absents(client.journal)
    assert MARQUEUR_PROMPT not in caplog.text and MARQUEUR_PROMPT[:12] not in caplog.text

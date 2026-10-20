"""Sprint 4, tâche B3 : les traces du briefing ne gardent que des métadonnées (décision D9, spec CA3.6).

La trace d'un briefing ne reçoit ni le prompt ni la réponse brute du modèle, y compris en cas d'erreur ou de sortie
refusée : seulement le modèle, les jetons, la durée (l'ouverture et la fermeture des étapes) et le motif.
L'enregistrement est empêché à la source : masquer après coup ne garantirait pas qu'aucune copie n'est partie. Des
textes fictifs reconnaissables le prouvent, et les métadonnées gardées ne les recopient pas, même en partie. Le client
Langfuse est remplacé par un double qui enregistre tout ; aucun réseau.
"""
from unittest.mock import patch

import pytest

from src import traces
from src.llm import generer_texte
from tests.test_trace_chemin import _briefing
from tests.test_traces import _FauxClient

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

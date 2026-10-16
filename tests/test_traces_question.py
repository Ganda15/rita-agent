"""Tâche A3 du sprint 3 : la racine de trace du parcours des questions ne porte que des métadonnées (spec CA4.3).

Le texte d'une question peut contenir une donnée personnelle tapée par un visiteur (décision D2) : la trace garde le
motif, la longueur, les identifiants des sources citées, jamais le texte.
"""
import pytest

from src import traces
from tests.test_llm_json import _Enregistreur


class _EnregistreurAvecIdentifiant(_Enregistreur):
    def create_trace_id(self, seed):
        return "0" * 32


def test_sans_client_la_racine_question_est_none():
    with traces.question("req-12345678") as racine:
        assert racine is None


def test_la_racine_question_ne_porte_que_des_metadonnees(monkeypatch):
    client = _EnregistreurAvecIdentifiant()
    monkeypatch.setattr(traces, "client_traces", lambda: client)
    with traces.question("req-12345678") as racine:
        traces.noter_issue_question(racine, "refus", "OUT_OF_CORPUS", 42, [])

    ouverture = next(options for genre, options in client.journal if genre == "ouvre")
    assert ouverture["name"] == "question"
    assert "input" not in ouverture and "output" not in ouverture
    assert ouverture["metadata"]["request_id"] == "req-12345678"

    issue = [champs for genre, champs in client.journal if genre == "update"][-1]
    assert issue["metadata"]["statut"] == "refus"
    assert issue["metadata"]["motif"] == "OUT_OF_CORPUS"
    assert issue["metadata"]["longueur"] == 42
    assert issue["metadata"]["ids"] == []
    assert issue["level"] == "WARNING"
    assert "input" not in issue and "output" not in issue
    assert ("flush", None) in client.journal


def test_une_exception_dans_la_racine_question_ne_passe_pas_au_sdk(monkeypatch):
    # Revue de sécurité des commits A1 à A3 (16/10/2026) : `_observation` transmet l'exception du corps au SDK, avec
    # son message. Sous la racine `question`, ce message peut recopier la question : seul son type doit partir.
    client = _EnregistreurAvecIdentifiant()
    monkeypatch.setattr(traces, "client_traces", lambda: client)
    with pytest.raises(RuntimeError):
        with traces.question("req-12345678"):
            raise RuntimeError("echec sur MARQUEUR-QUESTION-7f3a")
    assert "MARQUEUR-QUESTION-7f3a" not in repr(client.journal)
    assert ("ferme", (None, None, None)) in client.journal
    erreur = [champs for genre, champs in client.journal if genre == "update"][-1]
    assert erreur["level"] == "ERROR"
    assert erreur["status_message"] == "RuntimeError"

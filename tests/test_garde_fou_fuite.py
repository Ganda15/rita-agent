"""Sprint 4, tâches B1 et B2 : le contrôle de fuite après le modèle, sur les deux parcours (spec CA3.1, CA3.2, CA3.4,
CA3.5).

Une réponse qui laisserait sortir un secret, une valeur de configuration ou un morceau des consignes n'est jamais
servie. On le prouve avec des sorties dangereuses SIMULÉES et des secrets FICTIFS, construits ici par concaténation pour
que gitleaks ne les prenne pas pour de vrais secrets ; aucun secret réel n'est utilisé. Pour le parcours des questions,
la réponse, le journal et la trace sont vérifiés. Pour le briefing, la réponse et le journal : sa trace relève de la
tâche B3 (D9, CA3.6).
"""
import json
import logging

import pytest
from fastapi.testclient import TestClient

from agents import analyst, question
from api.main import app
from guardrails import sortie
from tests.conftest import CLE_DE_TEST
from tests.test_api_question import _parcours, _traces
from tests.test_trace_chemin import _briefing

CLE = {"X-API-Key": CLE_DE_TEST}
FAUSSE_CLE = "sk-" + "FAUX" * 6
FAUX_DSN = "postgresql://rita:" + "motdepasse-faux" + "@localhost:5433/rita"
QUESTION = "Combien de postes Netflix supprime-t-il ?"
BRIEFING_NORMAL = "Le titre recule de 1,10 % sur la séance."


def _poser(monkeypatch, texte):
    """Le vrai parcours, avec un modèle qui rend `texte` (une citation valide, l'extrait [1])."""
    _parcours(monkeypatch, json.dumps({"statut": "reponse", "texte": texte, "citations": [1]}))
    return TestClient(app).post("/question", json={"question": QUESTION}, headers=CLE)


# --- le parcours des questions ---------------------------------------------------------------------------------------

@pytest.mark.parametrize("secret", [FAUSSE_CLE, FAUX_DSN, "RITA_API_KEY=" + "valeur-fictive"],
                         ids=["forme_de_cle", "chaine_de_connexion", "nom_de_variable"])
def test_un_secret_dans_la_reponse_n_est_jamais_servi(monkeypatch, caplog, secret):
    journal_traces = _traces(monkeypatch)
    with caplog.at_level(logging.DEBUG):
        reponse = _poser(monkeypatch, f"Voici la valeur : {secret} [1].")
    corps = reponse.json()
    assert reponse.status_code == 200
    assert (corps["statut"], corps["motif"]) == ("refus", "FUITE_BLOQUEE")
    assert corps["texte"] == sortie.MESSAGE_REFUS_FUITE
    for endroit in (reponse.text, caplog.text, repr(journal_traces.journal)):
        assert secret not in endroit


def test_un_morceau_des_consignes_n_est_jamais_servi(monkeypatch):
    fragment = " ".join(question.CONSIGNES.split()[:10])
    corps = _poser(monkeypatch, f"{fragment} [1].").json()
    assert (corps["statut"], corps["motif"]) == ("refus", "FUITE_BLOQUEE")


@pytest.mark.parametrize("texte", ["L'entreprise a signalé une fuite de mots de passe de ses clients [1].",
                                   "La clé de l'accord est la baisse des droits de douane [1]."],
                         ids=["fuite_de_mots_de_passe", "cle_de_l_accord"])
def test_une_reponse_factuelle_avec_des_mots_sensibles_est_servie(monkeypatch, texte):
    # Point de vigilance du plan : parler d'une fuite ou d'une « clé » n'est pas divulguer un secret.
    corps = _poser(monkeypatch, texte).json()
    assert (corps["statut"], corps["motif"]) == ("reponse", "OK")


# --- le briefing -----------------------------------------------------------------------------------------------------

def test_un_briefing_normal_reste_servi(monkeypatch):
    # Le témoin des tests suivants : sans lui, un contrôle qui refuserait tout passerait.
    reponse, _ = _briefing(BRIEFING_NORMAL, monkeypatch)
    assert reponse.json()["briefing"] == BRIEFING_NORMAL


def test_le_briefing_ne_sert_pas_une_fuite(monkeypatch, caplog):
    normal, _ = _briefing(BRIEFING_NORMAL, monkeypatch)
    with caplog.at_level(logging.INFO):
        reponse, _ = _briefing(f"Le titre recule. La clé est {FAUSSE_CLE}.", monkeypatch)
    assert reponse.status_code == 200
    assert set(reponse.json()) == set(normal.json())          # la même forme de réponse (CA1.3)
    assert reponse.json()["briefing"] == sortie.MESSAGE_REFUS_FUITE
    assert "briefing refuse par le controle de fuite" in caplog.text and "motifs=forme_de_cle" in caplog.text
    assert FAUSSE_CLE not in reponse.text and FAUSSE_CLE not in caplog.text


def test_un_fragment_des_consignes_du_briefing_n_est_pas_servi(monkeypatch):
    fragment = " ".join(analyst.CONSIGNES_REDACTION.split()[:10])
    reponse, _ = _briefing(f"Le titre recule. {fragment}", monkeypatch)
    assert reponse.json()["briefing"] == sortie.MESSAGE_REFUS_FUITE

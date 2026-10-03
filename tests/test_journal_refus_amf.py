"""Un refus du garde-fou de sortie laisse une ligne dans le journal, sans le texte refusé.

Constat de l'audit du 02/10/2026 : quand /briefing refusait un texte, rien n'était écrit
nulle part. Le garde-fou protégeait l'utilisateur, mais personne ne pouvait savoir qu'il
avait servi, ni combien de fois, ni pour quel motif. Sorabel écrivait chaque appel autorisé
ou refusé ; RITA ne le faisait pas.

Deux règles testées :
  1. un refus écrit UNE ligne d'avertissement, avec la valeur et les motifs ;
  2. le texte refusé n'est JAMAIS recopié dans le journal (il serait relu, copié, envoyé).
Et un briefing conforme n'écrit rien : un journal qui crie à chaque appel ne se lit plus.
"""
import logging
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from tests.conftest import CLE_DE_TEST

client = TestClient(app)


def _appeler(texte_du_modele):
    resultat_simule = {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99,
                        "currency": "EUR", "error": "", "briefing": texte_du_modele}
    with patch("api.main.generer_briefing_complet", return_value=resultat_simule):
        return client.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})


def test_un_refus_ecrit_une_ligne_de_journal_sans_le_texte_refuse(caplog):
    with caplog.at_level(logging.WARNING, logger="api.main"):
        reponse = _appeler("Nous recommandons l'achat de cette valeur.")

    assert reponse.status_code == 200
    avertissements = [r for r in caplog.records
                      if r.name == "api.main" and r.levelno == logging.WARNING]
    assert len(avertissements) == 1, "un refus = une ligne, ni zéro ni plusieurs"
    message = avertissements[0].getMessage()
    assert "MC.PA" in message
    assert "recommandation_explicite_fr" in message
    assert "recommandons" not in message, "le texte refusé ne doit jamais entrer dans un journal"


def test_un_briefing_conforme_n_ecrit_aucun_avertissement(caplog):
    with caplog.at_level(logging.WARNING, logger="api.main"):
        reponse = _appeler("Le titre recule de 1,99 % sur la séance.")

    assert reponse.json()["conforme_amf"] is True
    assert [r for r in caplog.records if r.name == "api.main"] == []

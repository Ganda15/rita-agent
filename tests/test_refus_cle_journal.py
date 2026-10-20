"""Sprint 4, tâche C2 : le critère 4 du contrat du sprint 1 (spec CA6.3, décision D4).

« Étant donné une fausse clé, quand j'appelle une route protégée, alors je reçois un 403 et une ligne de journal le
dit. » La ligne porte l'identifiant de requête (celui de l'en-tête `X-Request-ID`), la route et le motif ; jamais la
clé, ni un morceau, ni sa longueur. La clé fictive est construite ici, pour ne ressembler à aucune vraie.
"""
import logging

import pytest
from fastapi.testclient import TestClient

from api.main import app

FAUSSE_CLE = "FAUSSE-CLE-" + "0" * 24
ROUTES = {
    "donnees": ("get", "/donnees/valeurs", {}),
    "question": ("post", "/question", {"json": {"question": "Combien de postes Netflix supprime-t-il ?"}}),
    "briefing": ("post", "/briefing?ticker=MC.PA", {}),
}


def _appeler(nom, entetes, caplog):
    methode, chemin, options = ROUTES[nom]
    with caplog.at_level(logging.WARNING):
        return getattr(TestClient(app), methode)(chemin, headers=entetes, **options)


@pytest.mark.parametrize("nom", ROUTES)
def test_une_fausse_cle_laisse_une_ligne_sans_la_cle(nom, caplog):
    reponse = _appeler(nom, {"X-API-Key": FAUSSE_CLE}, caplog)
    assert reponse.status_code == 403
    identifiant = reponse.headers["X-Request-ID"]
    lignes = [r.getMessage() for r in caplog.records if "cle d'API refusee" in r.getMessage()]
    assert len(lignes) == 1
    assert identifiant in lignes[0] and "motif=invalide" in lignes[0] and ROUTES[nom][1].split("?")[0] in lignes[0]
    # Ni la clé, ni un morceau reconnaissable, ni sa longueur. La longueur (35) se cherche dans la ligne SANS
    # l'identifiant : tiré au hasard, il contient « 35 » une fois sur dix environ, et le test échouait au hasard.
    assert FAUSSE_CLE not in caplog.text and "FAUSSE-CLE" not in caplog.text \
        and str(len(FAUSSE_CLE)) not in lignes[0].replace(identifiant, "")


def test_une_cle_absente_laisse_une_ligne(caplog):
    reponse = _appeler("donnees", {}, caplog)
    assert reponse.status_code == 403
    lignes = [r.getMessage() for r in caplog.records if "cle d'API refusee" in r.getMessage()]
    assert len(lignes) == 1 and "motif=absente" in lignes[0] and reponse.headers["X-Request-ID"] in lignes[0]


def test_une_bonne_cle_ne_laisse_aucune_ligne_de_refus(monkeypatch, caplog):
    # Le témoin : sans lui, une route qui journaliserait tout refus, même à tort, passerait les tests ci-dessus. La
    # recherche est remplacée par un refus hors corpus : ni index, ni modèle.
    from agents import question
    from rag.recherche import Resultat
    from tests.conftest import CLE_DE_TEST

    monkeypatch.setattr(question, "rechercher", lambda *a, **k: Resultat(False, "OUT_OF_CORPUS", [], 0))
    reponse = _appeler("question", {"X-API-Key": CLE_DE_TEST}, caplog)
    assert reponse.status_code == 200
    assert "cle d'API refusee" not in caplog.text

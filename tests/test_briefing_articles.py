"""Sprint 2, tâche 8 (choix A d'Era, 14/10) : le briefing dit combien d'articles distincts ont été transmis au modèle.

Relevé du serveur du 14/10 : la production n'avait aucun index d'articles, et le briefing est rédigé même sans article
(la recherche rend OUT_OF_CORPUS, le graphe continue). Sans ce compte, un index vide passait tous les contrôles. Le
script du serveur exige maintenant au moins un article pour `OR.PA`, en pré-test puis en production.
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from tests.conftest import CLE_DE_TEST

client = TestClient(app)


def _resultat(passages):
    return {"ticker": "OR.PA", "price": 380.0, "change_pct": 0.5, "currency": "EUR",
            "briefing": "Texte du briefing.", "error": "", "passages": passages}


def _briefing(resultat):
    with patch("api.main.generer_briefing_complet", return_value=resultat):
        return client.post("/briefing?ticker=OR.PA", headers={"X-API-Key": CLE_DE_TEST})


def test_le_briefing_compte_les_articles_distincts_transmis_au_modele():
    # Trois passages, dont deux du même article : deux articles distincts.
    passages = [{"article_id": 7, "texte": "a"}, {"article_id": 7, "texte": "b"}, {"article_id": 12, "texte": "c"}]
    reponse = _briefing(_resultat(passages))
    assert reponse.status_code == 200
    assert reponse.json()["articles_transmis"] == 2


def test_un_briefing_sans_article_l_annonce():
    reponse = _briefing(_resultat([]))
    assert reponse.status_code == 200
    assert reponse.json()["articles_transmis"] == 0


def test_un_resultat_sans_liste_de_passages_compte_zero():
    resultat = _resultat([])
    del resultat["passages"]
    assert _briefing(resultat).json()["articles_transmis"] == 0

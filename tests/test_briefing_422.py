"""Sprint 4, tâche C1 : le critère 3 du contrat du sprint 1 (spec CA6.2, décision D3).

« Étant donné une valeur inconnue ou de plus de 20 caractères, quand je demande un briefing, alors je reçois un 422 et
le modèle n'est pas appelé. » Un espion compte les appels au modèle. La présence de la valeur se lit dans le
référentiel (`valeur`) par une requête paramétrée, jamais concaténée.
"""
import logging

import pytest
from fastapi.testclient import TestClient

from api.main import app
from indicateurs import socle
from tests.conftest import CLE_DE_TEST, faux_resultat_texte
from tests.test_trace_chemin import _briefing

CLE = {"X-API-Key": CLE_DE_TEST}
CLES_DE_LA_REPONSE = {"ticker", "price", "change_pct", "currency", "briefing", "conforme_amf", "motifs_amf",
                      "articles_transmis", "diagnostic"}


@pytest.fixture
def espion_modele(monkeypatch):
    appels = []
    monkeypatch.setattr("agents.analyst.generer_texte_detaille",
                        lambda *a, **k: appels.append(1) or faux_resultat_texte("texte"))
    return appels


def _valeur_existe(monkeypatch, reponse):
    """Remplace la lecture du référentiel ; garde la trace des valeurs consultées."""
    consultees = []
    monkeypatch.setattr("api.main.valeur_existe", lambda ticker: consultees.append(ticker) or reponse, raising=False)
    return consultees


def test_une_valeur_de_21_caracteres_donne_422_sans_modele_ni_base(monkeypatch, espion_modele):
    consultees = _valeur_existe(monkeypatch, True)
    reponse = TestClient(app).post("/briefing?ticker=" + "A" * 21, headers=CLE)
    assert reponse.status_code == 422
    assert espion_modele == [] and consultees == []


def test_une_valeur_vide_donne_422(monkeypatch, espion_modele):
    _valeur_existe(monkeypatch, True)
    assert TestClient(app).post("/briefing?ticker=", headers=CLE).status_code == 422
    assert espion_modele == []


def test_une_valeur_inconnue_donne_422_sans_modele(monkeypatch, espion_modele, caplog):
    consultees = _valeur_existe(monkeypatch, False)
    with caplog.at_level(logging.WARNING):
        reponse = TestClient(app).post("/briefing?ticker=INCONNU.PA", headers=CLE)
    assert reponse.status_code == 422
    assert espion_modele == [] and consultees == ["INCONNU.PA"]
    assert "briefing refuse : valeur inconnue" in caplog.text


def test_une_valeur_connue_garde_la_meme_reponse(monkeypatch):
    # Le témoin : une valeur connue reçoit son briefing, avec la même forme de réponse qu'avant (CA1.3).
    reponse, _ = _briefing("Le titre recule de 1,10 % sur la séance.", monkeypatch)
    assert reponse.status_code == 200
    assert set(reponse.json()) == CLES_DE_LA_REPONSE


def test_valeur_existe_interroge_le_referentiel_sans_concatener(monkeypatch):
    requetes = []

    def faux_executer(sql, parametres=None):
        requetes.append((sql, parametres))
        return [{"present": 1}] if parametres == ("MC.PA",) else []

    monkeypatch.setattr(socle, "_executer", faux_executer)
    assert socle.valeur_existe("MC.PA") is True
    assert socle.valeur_existe("X'; DROP TABLE valeur; --") is False
    # La valeur passe en paramètre, jamais dans le texte SQL : une injection SQL ne peut rien y faire.
    assert all("MC.PA" not in sql and "DROP" not in sql for sql, _ in requetes)
    assert [parametres for _, parametres in requetes] == [("MC.PA",), ("X'; DROP TABLE valeur; --",)]

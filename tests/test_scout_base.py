"""Tests du Scout après bascule sur la base — chantier RAG-MCP, étape 4a.

⚠️ Même limite que `test_indicateurs_socle.py`, dite d'emblée : ces tests
remplacent `lire_socle` et `lire_volatilite_drawdown`. Ils vérifient ce que le
Scout FAIT des indicateurs, pas le SQL qui les produit — celui-ci est déjà
vérifié par exécution réelle dans `evidence/C14/preuve-indicateurs-lot1.md`.
"""
from datetime import date
from unittest.mock import patch

import pytest

from agents.scout import collect
from indicateurs.socle import IndicateursValeur
from indicateurs.risque import IndicateursRisqueValeur


@pytest.fixture(autouse=True)
def _le_rsi_ne_touche_pas_la_base(monkeypatch):
    """Depuis le 03/10/2026 le scout joint aussi le RSI (`lire_rsi`), une troisieme lecture en base.

    Quatre de ces tests ne remplacaient que les deux premieres : ils passaient sur le poste, ou un
    `.env` donne une vraie base, et tombaient en CI (« DATABASE_URL absente »), pendant neuf pushs de
    suite le 03/10. Un test du scout ne doit jamais dependre d'une base ; ceux qui parlent du RSI le
    remplacent eux-memes, apres cette fixture, par leur propre valeur."""
    monkeypatch.setattr("agents.scout.lire_rsi", lambda tickers: [])


def socle_lvmh(**surcharges):
    """Un lot 1 tel que `lire_socle` le rend, pour LVMH."""
    base = dict(
        ticker="MC.PA", nom_officiel="LVMH", devise="EUR", statut_qualite="OK",
        date_cours=date(2026, 8, 28), cours=545.2, fraicheur_jours=2,
        perf_1j_pct=-1.10, perf_1s_pct=2.40, perf_1m_pct=-3.80,
        perf_ytd_pct=5.20, perf_1a_pct=-11.10,
        ma20=552.3, ma50=561.9, adtv20=128456789.0,
        distance_plus_haut_1a_pct=-14.20,
    )
    base.update(surcharges)
    return IndicateursValeur(**base)


def risque_lvmh(**surcharges):
    """Un lot 3 tel que `lire_volatilite_drawdown` le rend."""
    base = dict(
        ticker="MC.PA", nom_officiel="LVMH", statut_qualite="OK",
        date_cours="2026-08-28", cours=545.2, fraicheur_jours=2,
        volatilite_annualisee_pct=24.7, drawdown_max_1a_pct=-18.3,
    )
    base.update(surcharges)
    return IndicateursRisqueValeur(**base)


# --- le Scout lit la base ------------------------------------------------------

def test_collect_prend_le_cours_dans_la_base_et_non_sur_le_reseau():
    """Le prix vient de la dernière cotation collectée, pas de yfinance."""
    with patch("agents.scout.lire_socle", return_value=[socle_lvmh()]), \
         patch("agents.scout.lire_volatilite_drawdown", return_value=[risque_lvmh()]):
        etat = collect("MC.PA")

    assert etat["price"] == 545.2
    assert etat["change_pct"] == -1.10
    assert etat["currency"] == "EUR"
    assert etat["error"] == ""


def test_collect_expose_adtv20_et_non_un_champ_nomme_volume():
    """`adtv20` est une MOYENNE sur 20 jours, pas le volume du jour.

    L'appeler `volume` serait une étiquette fausse — le rédacteur écrirait
    « volume échangé » sur une moyenne, et personne ne le verrait.
    """
    with patch("agents.scout.lire_socle", return_value=[socle_lvmh()]), \
         patch("agents.scout.lire_volatilite_drawdown", return_value=[risque_lvmh()]):
        etat = collect("MC.PA")

    assert etat["adtv20"] == 128456789.0
    assert "volume" not in etat


def test_collect_remonte_les_indicateurs_de_risque():
    """Volatilité et drawdown doivent arriver jusqu'au rédacteur."""
    with patch("agents.scout.lire_socle", return_value=[socle_lvmh()]), \
         patch("agents.scout.lire_volatilite_drawdown", return_value=[risque_lvmh()]):
        etat = collect("MC.PA")

    assert etat["indicateurs"]["volatilite_annualisee_pct"] == 24.7
    assert etat["indicateurs"]["drawdown_max_1a_pct"] == -18.3


# --- les refus -----------------------------------------------------------------

def test_collect_refuse_un_ticker_absent_de_la_base():
    """Un ticker inconnu rend une erreur — jamais une exception, jamais un zéro.

    Le graphe teste `state["error"]` pour sauter le rédacteur : une erreur muette
    produirait un briefing sur des chiffres à zéro.
    """
    with patch("agents.scout.lire_socle", return_value=[]), \
         patch("agents.scout.lire_volatilite_drawdown", return_value=[]):
        etat = collect("INEXISTANT.PA")

    assert etat["error"] != ""
    assert etat["price"] == 0.0


def test_collect_signale_une_cotation_perimee():
    """Une valeur radiée garde `statut_qualite = 'OK'` — seule la fraîcheur le dit.

    Le défaut corrigé le 19/08 sur l'API : `fraicheur_jours` était présent mais
    jamais exploité, et 3 valeurs radiées affichaient des chiffres de 2018.
    """
    vieux = socle_lvmh(fraicheur_jours=2000)
    with patch("agents.scout.lire_socle", return_value=[vieux]), \
         patch("agents.scout.lire_volatilite_drawdown", return_value=[risque_lvmh()]):
        etat = collect("MC.PA")

    assert etat["cotation_perimee"] is True
    assert etat["fraicheur_jours"] == 2000


def test_collect_ajoute_le_rsi_aux_indicateurs(monkeypatch):
    """Treizième indicateur : le RSI 14 était calculé (lot 3) mais jamais joint au dictionnaire du scout."""
    from agents import scout as module

    class _Socle:
        ticker, cours, perf_1j_pct, adtv20, devise, fraicheur_jours, cotation_perimee = "MC.PA", 378.55, -0.25, 1.0, "EUR", 1, False
        def en_dict(self):
            return {"ticker": "MC.PA", "cours": 378.55, "perf_1j_pct": -0.25, "ma20": 404.9}

    class _Risque:
        def en_dict(self):
            return {"volatilite_annualisee_pct": 22.5, "drawdown_max_1a_pct": -41.0}

    class _Rsi:
        rsi_14 = 38.4

    monkeypatch.setattr(module, "lire_socle", lambda tickers: [_Socle()])
    monkeypatch.setattr(module, "lire_volatilite_drawdown", lambda tickers: [_Risque()])
    monkeypatch.setattr(module, "lire_rsi", lambda tickers: [_Rsi()])
    etat = module.collect("MC.PA")
    assert etat["indicateurs"]["rsi_14"] == 38.4
    assert etat["indicateurs"]["volatilite_annualisee_pct"] == 22.5 and etat["indicateurs"]["ma20"] == 404.9


def test_collect_sans_rsi_ne_bloque_pas_le_briefing(monkeypatch):
    from agents import scout as module

    class _Socle:
        ticker, cours, perf_1j_pct, adtv20, devise, fraicheur_jours, cotation_perimee = "MC.PA", 378.55, -0.25, 1.0, "EUR", 1, False
        def en_dict(self):
            return {"ticker": "MC.PA"}

    monkeypatch.setattr(module, "lire_socle", lambda tickers: [_Socle()])
    monkeypatch.setattr(module, "lire_volatilite_drawdown", lambda tickers: [])
    monkeypatch.setattr(module, "lire_rsi", lambda tickers: [])
    etat = module.collect("MC.PA")
    assert etat["error"] == "" and "rsi_14" not in etat["indicateurs"]

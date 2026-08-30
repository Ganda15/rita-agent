"""Tests du graphe LangGraph — Scout puis Rédacteur (C8).

⚠️ Les faux états ci-dessous doivent rester **identiques** à ce que `collect` rend
vraiment (`agents/scout.ScoutState`). Un simulacre qui diverge du code produit des
tests verts sur du code cassé : c'est le défaut relevé le 28/08 (« test vert sur
corpus vide ») et le 30/08 (`volume` conservé dans le faux Scout alors que le
Scout ne le rendait plus).
"""
from unittest.mock import patch

from graph.workflow import generer_briefing_complet


def scout_lvmh(**surcharges):
    """Ce que `agents.scout.collect` rend réellement pour une valeur trouvée."""
    base = {
        "ticker": "MC.PA", "price": 545.2, "change_pct": -1.10,
        "adtv20": 128456789.0, "currency": "EUR",
        "fraicheur_jours": 2, "cotation_perimee": False,
        "indicateurs": {"ma20": 552.3, "volatilite_annualisee_pct": 24.7},
        "error": "",
    }
    base.update(surcharges)
    return base


def test_graphe_complet_scout_puis_redacteur():
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.generate_briefing", return_value="Briefing test.") as redacteur:
        resultat = generer_briefing_complet("MC.PA")

    assert resultat["briefing"] == "Briefing test."
    redacteur.assert_called_once()


def test_le_redacteur_recoit_adtv20_et_jamais_un_champ_volume():
    """Le graphe ne doit plus fabriquer de `volume` — il n'existe plus en amont.

    Sans ce test, `workflow.py` peut continuer à lire `state["volume"]` : la clé
    survit dans l'état initial à 0, le rédacteur écrit « volume : 0 », et aucun
    test ne le signale.
    """
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.generate_briefing", return_value="x") as redacteur:
        resultat = generer_briefing_complet("MC.PA")

    assert "volume" not in resultat
    assert redacteur.call_args.kwargs["adtv20"] == 128456789.0
    assert redacteur.call_args.kwargs["currency"] == "EUR"


def test_le_redacteur_est_prevenu_dune_cotation_perimee():
    """Une cotation de 2018 ne doit pas être rédigée comme celle d'hier."""
    with patch("graph.workflow.collect",
               return_value=scout_lvmh(fraicheur_jours=2000, cotation_perimee=True)), \
         patch("graph.workflow.generate_briefing", return_value="x") as redacteur:
        generer_briefing_complet("MC.PA")

    assert redacteur.call_args.kwargs["cotation_perimee"] is True
    assert redacteur.call_args.kwargs["fraicheur_jours"] == 2000


def test_graphe_saute_le_redacteur_si_erreur_scout():
    erreur = scout_lvmh(ticker="XXX.PA", price=0.0, change_pct=0.0, adtv20=None,
                        currency="", indicateurs={},
                        error="ticker absent de la base : XXX.PA")
    with patch("graph.workflow.collect", return_value=erreur), \
         patch("graph.workflow.generate_briefing") as redacteur:
        resultat = generer_briefing_complet("XXX.PA")

    assert resultat["briefing"] == ""
    redacteur.assert_not_called()

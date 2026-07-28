from unittest.mock import patch
from graph.workflow import generer_briefing_complet


def test_graphe_complet_scout_puis_redacteur():
    fake_scout = {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99,
                  "volume": 1_200_000, "currency": "EUR", "error": ""}
    with patch("graph.workflow.collect", return_value=fake_scout), \
         patch("graph.workflow.generate_briefing", return_value="Briefing test.") as mock_redacteur:
        resultat = generer_briefing_complet("MC.PA")

    assert resultat["briefing"] == "Briefing test."
    mock_redacteur.assert_called_once()


def test_graphe_saute_le_redacteur_si_erreur_scout():
    fake_scout = {"ticker": "XXX.PA", "price": 0.0, "change_pct": 0.0,
                  "volume": 0, "currency": "", "error": "no data"}
    with patch("graph.workflow.collect", return_value=fake_scout), \
         patch("graph.workflow.generate_briefing") as mock_redacteur:
        resultat = generer_briefing_complet("XXX.PA")

    assert resultat["briefing"] == ""
    mock_redacteur.assert_not_called()

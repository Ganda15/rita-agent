from unittest.mock import patch

from agents.analyst import generate_briefing


def prompt_produit(mock_llm) -> str:
    """Le prompt réellement envoyé au modèle."""
    return mock_llm.call_args[0][0]


def test_generate_briefing_appelle_le_llm_et_retourne_le_texte():
    with patch("agents.analyst.generer_texte", return_value="Texte du briefing.") as mock_llm:
        resultat = generate_briefing(ticker="MC.PA", price=457.5, change_pct=-1.99,
                                     adtv20=1_200_000.0, currency="EUR")

    assert resultat == "Texte du briefing."
    mock_llm.assert_called_once()
    assert "MC.PA" in prompt_produit(mock_llm)
    assert "AUCUNE recommandation" in prompt_produit(mock_llm)


def test_le_prompt_nomme_le_volume_comme_une_moyenne_20_seances():
    """Le modèle ne doit jamais pouvoir écrire « volume du jour » sur une moyenne."""
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="MC.PA", price=457.5, change_pct=-1.99,
                          adtv20=1_200_000.0, currency="EUR")

    prompt = prompt_produit(mock_llm)
    assert "Volume moyen sur 20 séances" in prompt
    assert "JAMAIS le volume moyen 20 séances comme le volume du jour" in prompt


def test_un_adtv20_absent_ne_produit_pas_un_zero_invente():
    """Un historique trop court rend `None` — écrire 0 serait un chiffre inventé."""
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="ALX.PA", price=12.0, change_pct=0.5,
                          adtv20=None, currency="EUR")

    assert "non disponible" in prompt_produit(mock_llm)


def test_une_cotation_perimee_est_dite_au_modele():
    """Défaut du 19/08 : la fraîcheur était calculée mais jamais transmise."""
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="ZC.PA", price=24.5, change_pct=0.0,
                          adtv20=None, currency="EUR",
                          fraicheur_jours=2000, cotation_perimee=True)

    prompt = prompt_produit(mock_llm)
    assert "2000 jours" in prompt
    assert "probablement radiée" in prompt

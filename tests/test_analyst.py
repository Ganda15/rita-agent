from unittest.mock import patch
from agents.analyst import generate_briefing


def test_generate_briefing_appelle_le_llm_et_retourne_le_texte():
    with patch("agents.analyst.generer_texte", return_value="Texte du briefing.") as mock_llm:
        resultat = generate_briefing("MC.PA", 457.5, -1.99, 1_200_000, "EUR")

    assert resultat == "Texte du briefing."
    mock_llm.assert_called_once()
    prompt_envoye = mock_llm.call_args[0][0]
    assert "MC.PA" in prompt_envoye
    assert "AUCUNE recommandation" in prompt_envoye

from unittest.mock import patch
from src.llm import generer_texte, _ordre_fournisseurs


def test_ordre_fournisseurs_lit_variable_environnement(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "anthropic,openrouter")
    assert _ordre_fournisseurs() == ["anthropic", "openrouter"]


def test_ordre_fournisseurs_defaut(monkeypatch):
    monkeypatch.delenv("LLM_ORDRE", raising=False)
    assert _ordre_fournisseurs() == ["foundry", "anthropic", "openrouter"]


def test_generer_texte_bascule_sur_le_fournisseur_suivant_si_echec(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,anthropic")
    with patch("src.llm._appel_foundry", side_effect=RuntimeError("indisponible")), \
         patch("src.llm._appel_anthropic", return_value="ok anthropic") as mock_anthropic:
        resultat = generer_texte("prompt test")

    assert resultat == "ok anthropic"
    mock_anthropic.assert_called_once()


def test_generer_texte_leve_erreur_si_tous_indisponibles(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    with patch("src.llm._appel_anthropic", side_effect=RuntimeError("panne")):
        try:
            generer_texte("prompt test")
            assert False, "devrait lever RuntimeError"
        except RuntimeError as erreur:
            assert "Aucun fournisseur" in str(erreur)

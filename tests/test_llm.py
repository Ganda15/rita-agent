import pytest
from unittest.mock import patch

from src import traces
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


def test_la_suite_de_tests_n_envoie_jamais_de_trace(monkeypatch):
    """Mesuré le 02/10/2026 dans Langfuse : 12 générations « prompt test » / « ok anthropic »
    venaient de CE fichier. `api/main.py` charge le fichier d'environnement à l'import ; dès
    qu'un test d'API a tourné, les vraies clés sont dans le processus et la cascade simulée
    trace pour de vrai. La suite doit couper le traçage pour tous, par `conftest.py`, même
    avec des clés présentes."""
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")
    traces.reinitialiser()
    assert traces.client_traces() is None


# --- Azure AI Foundry, point de terminaison compatible OpenAI (03/10/2026, décision d'Era) -----------
#
# La ressource Foundry d'Era sert l'API OpenAI (`.../openai/v1`), déploiement `gpt-5.4`, gratuite pour lui.
# Jusqu'ici `_appel_foundry` passait par le client Anthropic-sur-Foundry (`claude-opus-4-8`) : jamais une clé.
# Même forme d'appel qu'OpenRouter (httpx, chat completions), aucune dépendance nouvelle.

class _ReponseHttp:
    def __init__(self, corps):
        self._corps = corps
    def raise_for_status(self):
        return None
    def json(self):
        return self._corps


def test_appel_foundry_poste_sur_le_point_compatible_openai_avec_la_cle_et_le_deploiement(monkeypatch):
    from src import llm
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://ressource.services.ai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_FOUNDRY_API_KEY", "cle-de-test")
    monkeypatch.setenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-5.4")
    appels = {}

    def faux_post(url, headers, json, timeout):
        appels.update(url=url, headers=headers, json=json, timeout=timeout)
        return _ReponseHttp({"model": "gpt-5.4-2026-01", "choices": [{"message": {"content": "Paris."}}],
                             "usage": {"prompt_tokens": 12, "completion_tokens": 3}})

    monkeypatch.setattr(llm.httpx, "post", faux_post)
    r = llm._appel_foundry("Capitale de la France ?", 50)
    assert appels["url"] == "https://ressource.services.ai.azure.com/openai/v1/chat/completions"
    assert appels["headers"]["Authorization"] == "Bearer cle-de-test"
    assert appels["json"]["model"] == "gpt-5.4" and appels["json"]["max_tokens"] == 50
    assert appels["json"]["messages"] == [{"role": "user", "content": "Capitale de la France ?"}]
    assert r.texte == "Paris." and r.modele == "gpt-5.4-2026-01" and r.usage == {"input": 12, "output": 3}


def test_appel_foundry_sans_cle_est_une_indisponibilite_pas_une_reponse_vide(monkeypatch):
    from src import llm
    monkeypatch.delenv("AZURE_FOUNDRY_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://ressource.services.ai.azure.com/openai/v1")
    with pytest.raises(KeyError):
        llm._appel_foundry("x", 10)


def test_le_deploiement_foundry_par_defaut_est_gpt_5_4(monkeypatch):
    from src import llm
    monkeypatch.delenv("AZURE_FOUNDRY_DEPLOYMENT", raising=False)
    assert llm._modele_prevu("foundry") == "gpt-5.4"


def test_foundry_n_utilise_plus_le_client_anthropic():
    import inspect
    from src import llm
    assert "AnthropicFoundry" not in inspect.getsource(llm)

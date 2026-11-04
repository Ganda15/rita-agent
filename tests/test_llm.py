import pytest
from unittest.mock import patch

from src import traces
from src.llm import generer_texte, _ordre_fournisseurs


def test_ordre_fournisseurs_lit_variable_environnement(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "anthropic,openrouter")
    assert _ordre_fournisseurs() == ["anthropic", "openrouter"]


def test_ordre_fournisseurs_defaut(monkeypatch):
    """Règle UE seule (CONTINUITE.md, décision du 11/10) : sans configuration, Azure seul, aucun repli hors UE.

    Lu le 31/10 dans le conteneur de production : `foundry,anthropic,openrouter`, venu de cette valeur par défaut."""
    monkeypatch.delenv("LLM_ORDRE", raising=False)
    assert _ordre_fournisseurs() == ["foundry"]


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
    assert appels["json"]["model"] == "gpt-5.4" and appels["json"]["max_completion_tokens"] == 50
    assert "max_tokens" not in appels["json"], "refusé par les modèles GPT-5 (400 unsupported parameter)"
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


# --- L'origine d'un appel (03/10/2026, soir) --------------------------------------------------------
#
# Un déploiement Foundry « Global Standard » peut être traité dans n'importe quelle région Azure ; la région
# n'est donc pas une propriété de la ressource, c'est le résultat d'un appel, lisible dans l'en-tête `x-ms-region`.
# OpenRouter route vers sept points de sortie et nomme celui qui a répondu dans le champ `provider` du corps.
# Le banc C7 doit journaliser cette origine à chaque appel : une région supposée n'est pas une région mesurée.

class _ReponseHttpAvecEntetes(_ReponseHttp):
    def __init__(self, corps, headers=None):
        super().__init__(corps)
        self.headers = headers or {}


def test_appel_foundry_lit_la_region_dans_l_en_tete_x_ms_region(monkeypatch):
    from src import llm
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://ressource.services.ai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_FOUNDRY_API_KEY", "cle-de-test")
    corps = {"model": "gpt-5.4-2026-03-05", "choices": [{"message": {"content": "ok"}}],
             "usage": {"prompt_tokens": 11, "completion_tokens": 4}}
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttpAvecEntetes(corps, {"x-ms-region": "Sweden Central"}))
    assert llm._appel_foundry("Réponds : ok", 5).origine == "Sweden Central"


def test_appel_foundry_sans_en_tete_de_region_laisse_l_origine_inconnue(monkeypatch):
    from src import llm
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://ressource.services.ai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_FOUNDRY_API_KEY", "cle-de-test")
    corps = {"model": "gpt-5.4-2026-03-05", "choices": [{"message": {"content": "ok"}}]}
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttpAvecEntetes(corps))
    assert llm._appel_foundry("x", 5).origine is None


def test_appel_openrouter_lit_le_point_de_sortie_dans_le_champ_provider(monkeypatch):
    from src import llm
    monkeypatch.setenv("OPENROUTER_API_KEY", "cle-de-test")
    corps = {"model": "anthropic/claude-sonnet-4.5", "provider": "Anthropic",
             "choices": [{"message": {"content": "ok"}}], "usage": {"prompt_tokens": 9, "completion_tokens": 2}}
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttpAvecEntetes(corps))
    r = llm._appel_openrouter("x", 5)
    assert r.origine == "Anthropic" and r.modele == "anthropic/claude-sonnet-4.5"


# --- Le modèle dit qui a répondu (refonte 001, tâche 1, exigence R4) ---------------------------------
#
# L'écran du briefing affichera quel fournisseur et quel modèle ont répondu, et combien de tentatives il a fallu.
# Le modèle affiché est celui que le fournisseur a renvoyé (`Reponse.modele`), jamais celui que la configuration
# annonce (`_modele_prevu`) : une valeur supposée n'est pas une valeur mesurée. Une tentative ne garde jamais le
# message de son erreur, qui peut recopier le prompt (sprint 4, D9).

def test_detaille_dit_le_fournisseur_et_le_modele_reels(monkeypatch):
    from src import llm
    monkeypatch.setenv("LLM_ORDRE", "foundry")
    monkeypatch.setenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-5.4")
    with patch("src.llm._appel_foundry", return_value=traces.Reponse(texte="Texte.", modele="gpt-5.4-2026-03-05")):
        resultat = llm.generer_texte_detaille("prompt test")
    assert resultat.texte == "Texte."
    assert resultat.fournisseur == "foundry"
    assert resultat.modele == "gpt-5.4-2026-03-05", "le modèle renvoyé, pas celui de la configuration (gpt-5.4)"
    assert resultat.tentatives == [{"fournisseur": "foundry", "reussi": True}]


def test_modele_null_si_non_renvoye(monkeypatch):
    from src import llm
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    with patch("src.llm._appel_anthropic", return_value="texte seul"):
        resultat = llm.generer_texte_detaille("prompt test")
    assert resultat.fournisseur == "anthropic"
    assert resultat.modele is None, "un fournisseur qui ne dit pas son modèle : on n'invente pas"


def test_tentatives_sans_message_d_erreur(monkeypatch):
    from src import llm
    monkeypatch.setenv("LLM_ORDRE", "foundry,anthropic")
    recopie = "PROMPT RECOPIE DANS LE MESSAGE D ERREUR"
    with patch("src.llm._appel_foundry", side_effect=RuntimeError(recopie)), \
         patch("src.llm._appel_anthropic", return_value=traces.Reponse(texte="ok", modele="claude-sonnet-5")):
        resultat = llm.generer_texte_detaille("prompt test")
    assert resultat.tentatives == [{"fournisseur": "foundry", "reussi": False},
                                   {"fournisseur": "anthropic", "reussi": True}]
    assert resultat.fournisseur == "anthropic" and resultat.modele == "claude-sonnet-5"
    assert recopie not in repr(resultat)


def test_tous_en_panne_leve_aucun_fournisseur(monkeypatch):
    from src import llm
    monkeypatch.setenv("LLM_ORDRE", "foundry,anthropic")
    with patch("src.llm._appel_foundry", side_effect=RuntimeError("panne")), \
         patch("src.llm._appel_anthropic", side_effect=RuntimeError("panne")):
        with pytest.raises(llm.AucunFournisseur) as erreur:
            llm.generer_texte_detaille("prompt test")
    assert isinstance(erreur.value, RuntimeError), "les appelants qui attrapent RuntimeError restent justes"
    assert "Aucun fournisseur LLM disponible." in str(erreur.value)
    assert erreur.value.tentatives == [{"fournisseur": "foundry", "reussi": False},
                                       {"fournisseur": "anthropic", "reussi": False}]


def test_fournisseur_inconnu_absent_des_tentatives(monkeypatch):
    from src import llm
    monkeypatch.setenv("LLM_ORDRE", "inconnu,foundry")
    with patch("src.llm._appel_foundry", return_value="ok"):
        resultat = llm.generer_texte_detaille("prompt test")
    assert resultat.tentatives == [{"fournisseur": "foundry", "reussi": True}], "un nom ignoré n'est pas une tentative"

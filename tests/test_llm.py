import pytest
from unittest.mock import patch

from src import traces
from src.llm import generer_texte, _ordre_fournisseurs


def test_ordre_fournisseurs_lit_variable_environnement(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "mistral,foundry")
    assert _ordre_fournisseurs() == ["mistral", "foundry"]


def test_ordre_fournisseurs_defaut(monkeypatch):
    """Depuis la carte #82 (règle « UE seule » d'Era) : Azure en Data Zone EU, puis Mistral par son adresse
    européenne. Anthropic et OpenRouter ne sont plus dans la cascade."""
    monkeypatch.delenv("LLM_ORDRE", raising=False)
    assert _ordre_fournisseurs() == ["foundry", "mistral"]


def test_seuls_les_fournisseurs_approuves_ue_sont_connus():
    from src import llm
    assert llm._NOMS_VALIDES == {"foundry", "mistral"}


def test_le_module_ne_peut_plus_appeler_anthropic_ni_openrouter():
    """Aucun chemin de code vers un fournisseur sans garantie UE : ni fonction, ni bibliothèque, ni adresse."""
    import inspect
    from src import llm
    source = inspect.getsource(llm)
    assert not hasattr(llm, "_appel_anthropic") and not hasattr(llm, "_appel_openrouter")
    assert "import anthropic" not in source and "from anthropic" not in source
    assert "openrouter.ai" not in source
    assert "AnthropicFoundry" not in source


def test_generer_texte_bascule_sur_le_fournisseur_suivant_si_echec(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")
    with patch("src.llm._appel_foundry", side_effect=RuntimeError("indisponible")), \
         patch("src.llm._appel_mistral", return_value="ok mistral") as mock_mistral:
        resultat = generer_texte("prompt test")

    assert resultat == "ok mistral"
    mock_mistral.assert_called_once()


def test_un_fournisseur_hors_ue_dans_llm_ordre_est_ignore(monkeypatch):
    """Même si quelqu'un remet Anthropic ou OpenRouter dans `LLM_ORDRE`, la cascade ne les appelle pas."""
    monkeypatch.setenv("LLM_ORDRE", "openrouter,anthropic,mistral")
    with patch("src.llm._appel_mistral", return_value="ok mistral") as mock_mistral:
        assert generer_texte("prompt test") == "ok mistral"
    mock_mistral.assert_called_once()


def test_sans_fournisseur_approuve_aucun_appel_et_une_erreur(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "openrouter,anthropic")
    with pytest.raises(RuntimeError, match="Aucun fournisseur"):
        generer_texte("prompt test")


def test_generer_texte_leve_erreur_si_tous_indisponibles(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "mistral")
    with patch("src.llm._appel_mistral", side_effect=RuntimeError("panne")):
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
# La ressource Foundry d'Era sert l'API OpenAI (`.../openai/v1`), gratuite pour lui. Depuis le 09/10/2026, le
# déploiement est `gpt-5.4-dzs-eu` (même modèle `gpt-5.4`, Data Zone Standard EU) ; l'ancien `gpt-5.4` est supprimé.
# Même forme d'appel que Mistral (httpx, chat completions), aucune dépendance nouvelle.

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
    monkeypatch.setenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-5.4-dzs-eu")
    appels = {}

    def faux_post(url, headers, json, timeout):
        appels.update(url=url, headers=headers, json=json, timeout=timeout)
        return _ReponseHttp({"model": "gpt-5.4-2026-01", "choices": [{"message": {"content": "Paris."}}],
                             "usage": {"prompt_tokens": 12, "completion_tokens": 3}})

    monkeypatch.setattr(llm.httpx, "post", faux_post)
    r = llm._appel_foundry("Capitale de la France ?", 50)
    assert appels["url"] == "https://ressource.services.ai.azure.com/openai/v1/chat/completions"
    assert appels["headers"]["Authorization"] == "Bearer cle-de-test"
    assert appels["json"]["model"] == "gpt-5.4-dzs-eu" and appels["json"]["max_completion_tokens"] == 50
    assert "max_tokens" not in appels["json"], "refusé par les modèles GPT-5 (400 unsupported parameter)"
    assert appels["json"]["messages"] == [{"role": "user", "content": "Capitale de la France ?"}]
    assert r.texte == "Paris." and r.modele == "gpt-5.4-2026-01" and r.usage == {"input": 12, "output": 3}


def test_appel_foundry_sans_cle_est_une_indisponibilite_pas_une_reponse_vide(monkeypatch):
    from src import llm
    monkeypatch.delenv("AZURE_FOUNDRY_API_KEY", raising=False)
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://ressource.services.ai.azure.com/openai/v1")
    with pytest.raises(KeyError):
        llm._appel_foundry("x", 10)


def test_le_deploiement_foundry_par_defaut_est_celui_de_la_zone_ue(monkeypatch):
    """Le 09/10/2026, `gpt-5.4` (Global Standard) a été supprimé : la valeur par défaut doit viser le déploiement
    qui existe, `gpt-5.4-dzs-eu`, sinon une configuration sans la variable répond 404."""
    from src import llm
    monkeypatch.delenv("AZURE_FOUNDRY_DEPLOYMENT", raising=False)
    assert llm._modele_prevu("foundry") == "gpt-5.4-dzs-eu"


# --- L'origine d'un appel (03/10/2026, soir) --------------------------------------------------------
#
# Azure renvoie la région qui a traité l'appel dans l'en-tête `x-ms-region` ; depuis le 09/10/2026 le déploiement est
# en Data Zone Standard EU, et cet en-tête permet de le vérifier appel par appel. Mistral ne renvoie aucun en-tête de
# région : l'origine notée est l'adresse européenne appelée, et le lieu de traitement se prouve par son contrat.

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


# --- Mistral par son adresse européenne (carte #82, décision d'Era du 09/10/2026) ---------------------
#
# L'adresse `api.eu.mistral.ai` est écrite dans le code, pas dans un réglage : une variable mal posée ne peut pas
# envoyer la cascade hors de l'UE. Appel par httpx, sans SDK, comme Foundry.

def test_appel_mistral_poste_sur_l_adresse_europeenne_avec_la_cle_et_le_modele(monkeypatch):
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    monkeypatch.delenv("MISTRAL_MODEL", raising=False)
    appels = {}

    def faux_post(url, headers, json, timeout):
        appels.update(url=url, headers=headers, json=json, timeout=timeout)
        return _ReponseHttp({"model": "mistral-large-4-0", "choices": [{"message": {"content": "Paris."}}],
                             "usage": {"prompt_tokens": 14, "completion_tokens": 3}})

    monkeypatch.setattr(llm.httpx, "post", faux_post)
    r = llm._appel_mistral("Capitale de la France ?", 50)
    assert appels["url"] == "https://api.eu.mistral.ai/v1/chat/completions"
    assert appels["headers"]["Authorization"] == "Bearer cle-de-test"
    assert appels["json"]["model"] == "mistral-large-4-0" and appels["json"]["max_tokens"] == 50
    assert appels["json"]["messages"] == [{"role": "user", "content": "Capitale de la France ?"}]
    assert r.texte == "Paris." and r.modele == "mistral-large-4-0" and r.usage == {"input": 14, "output": 3}
    assert r.origine == "api.eu.mistral.ai"


def test_l_adresse_mistral_ne_se_regle_pas_par_l_environnement(monkeypatch):
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    monkeypatch.setenv("MISTRAL_SERVER", "https://api.mistral.ai")
    monkeypatch.setenv("MISTRAL_URL", "https://api.mistral.ai/v1/chat/completions")
    urls = []
    corps = {"model": "mistral-large-4-0", "choices": [{"message": {"content": "ok"}}]}

    def faux_post(url, **k):
        urls.append(url)
        return _ReponseHttp(corps)

    monkeypatch.setattr(llm.httpx, "post", faux_post)
    llm._appel_mistral("x", 5)
    assert urls == ["https://api.eu.mistral.ai/v1/chat/completions"]


def test_appel_mistral_sans_cle_est_une_indisponibilite_pas_une_reponse_vide(monkeypatch):
    from src import llm
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    with pytest.raises(KeyError):
        llm._appel_mistral("x", 10)


def test_le_modele_mistral_se_regle_par_mistral_model(monkeypatch):
    from src import llm
    monkeypatch.delenv("MISTRAL_MODEL", raising=False)
    assert llm._modele_prevu("mistral") == "mistral-large-4-0"
    monkeypatch.setenv("MISTRAL_MODEL", "mistral-large-latest")
    assert llm._modele_prevu("mistral") == "mistral-large-latest"


# --- Mistral Large 4 sans réflexion (10/10/2026, décision d'Era) ----------------------------------------
#
# Mesuré le 10/10 sur MC.PA (evidence/C8/preuve-briefing-mistral-2026-10-10.md) : Large 4 est un modèle à
# raisonnement. Par défaut il rend une LISTE de blocs (réflexion puis texte) ; avec la limite de 500 jetons du
# rédacteur, la réflexion consommait tout, aucun texte, et la liste faisait échouer le garde-fou (500 sans repli).
# Avec `reasoning_effort: "none"` (documentation Mistral), il rend une chaîne : 2,6 et 3,7 s, aucune date inventée.

def test_appel_mistral_demande_une_reponse_sans_reflexion(monkeypatch):
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    corps_envoyes = []

    def faux_post(url, headers, json, timeout):
        corps_envoyes.append(json)
        return _ReponseHttp({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(llm.httpx, "post", faux_post)
    llm._appel_mistral("x", 5)
    assert corps_envoyes[0]["reasoning_effort"] == "none"


def test_une_reponse_mistral_en_blocs_ne_garde_que_le_texte(monkeypatch):
    """Si la réflexion revient malgré tout (modèle changé par MISTRAL_MODEL), seul le texte final est gardé :
    la réflexion ne doit jamais arriver dans un briefing."""
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    blocs = [{"type": "thinking", "thinking": [{"type": "text", "text": "je réfléchis"}]},
             {"type": "text", "text": "Paris."}]
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttp({"choices": [{"message": {"content": blocs}}]}))
    assert llm._appel_mistral("x", 5).texte == "Paris."


def test_une_reponse_mistral_sans_texte_est_une_indisponibilite(monkeypatch):
    """Réflexion seule, coupée par la limite : c'est une panne du fournisseur, pas une réponse. L'erreur fait passer
    la cascade au suivant, au lieu d'un 500 plus loin dans le garde-fou."""
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    blocs = [{"type": "thinking", "thinking": [{"type": "text", "text": "je réfléchis encore"}]}]
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttp({"choices": [{"message": {"content": blocs}}]}))
    with pytest.raises(ValueError):
        llm._appel_mistral("x", 5)


def test_la_bibliotheque_anthropic_n_est_plus_une_dependance():
    """Plus aucun code ne l'importe (carte #82) : la garder, c'est une bibliothèque et une surface de plus dans l'image."""
    from pathlib import Path
    racine = Path(__file__).parent.parent
    for nom in ("requirements.txt", "requirements-api.txt"):
        lignes = [l.split("#")[0].strip().lower() for l in (racine / nom).read_text(encoding="utf-8").splitlines()]
        assert not [l for l in lignes if l.startswith("anthropic")], nom

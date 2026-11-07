"""L'appel de Mistral, pour le banc C7 seulement (demande d'Era du 07/11 : mesurer Mistral Large 4 contre Azure).

Repris de la PR #88 (branche `mistral-ue`, 10/10/2026) sans le reste de cette PR : on ajoute la fonction d'appel, on
ne change PAS la cascade. La production reste sur Azure seul (`LLM_ORDRE=foundry` par défaut) tant que le contrat de
Mistral n'est pas lu (règle UE seule, registre § 0). Le banc appelle un fournisseur par son nom
(`evals/benchmark_fournisseurs.py`, `appel_reel`) : il suffit que `_appel_mistral` existe.

L'adresse `api.eu.mistral.ai` est écrite dans le code, pas dans un réglage : une variable mal posée ne peut pas envoyer
l'appel hors de l'UE. Large 4 est un modèle à raisonnement : sans `reasoning_effort: "none"`, sa réflexion consommait
les 500 jetons du rédacteur et il ne rendait aucun texte (mesuré le 10/10, `evidence/C8/preuve-briefing-mistral-2026-10-10.md`
sur la branche `mistral-ue`).
"""
import pytest


class _ReponseHttp:
    def __init__(self, corps):
        self._corps = corps
        self.headers = {}

    def raise_for_status(self):
        return None

    def json(self):
        return self._corps


def test_appel_mistral_poste_sur_l_adresse_europeenne_avec_la_cle_et_le_modele(monkeypatch):
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    monkeypatch.delenv("MISTRAL_MODEL", raising=False)
    appels = {}

    def faux_post(url, headers, json, timeout):
        appels.update(url=url, headers=headers, json=json, timeout=timeout)
        return _ReponseHttp({"model": "mistral-large-2512", "choices": [{"message": {"content": "Paris."}}],
                             "usage": {"prompt_tokens": 14, "completion_tokens": 3}})

    monkeypatch.setattr(llm.httpx, "post", faux_post)
    r = llm._appel_mistral("Capitale de la France ?", 50)
    assert appels["url"] == "https://api.eu.mistral.ai/v1/chat/completions"
    assert appels["headers"]["Authorization"] == "Bearer cle-de-test"
    assert appels["json"]["model"] == "mistral-large-2512" and appels["json"]["max_tokens"] == 50
    assert appels["json"]["messages"] == [{"role": "user", "content": "Capitale de la France ?"}]
    assert r.texte == "Paris." and r.modele == "mistral-large-2512" and r.usage == {"input": 14, "output": 3}
    assert r.origine == "api.eu.mistral.ai"


def test_l_adresse_mistral_ne_se_regle_pas_par_l_environnement(monkeypatch):
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    monkeypatch.setenv("MISTRAL_SERVER", "https://api.mistral.ai")
    monkeypatch.setenv("MISTRAL_URL", "https://api.mistral.ai/v1/chat/completions")
    urls = []

    def faux_post(url, **k):
        urls.append(url)
        return _ReponseHttp({"model": "mistral-large-4-0", "choices": [{"message": {"content": "ok"}}]})

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
    assert llm._modele_prevu("mistral") == "mistral-large-2512"
    monkeypatch.setenv("MISTRAL_MODEL", "mistral-large-latest")
    assert llm._modele_prevu("mistral") == "mistral-large-latest"


# Mesuré le 07/11 : Mistral n'accepte plus `reasoning_effort: "none"` pour Large 4 (seulement low, medium, high), et
# même à `low` sa réflexion prend 499 des 500 jetons du rédacteur, sans texte. Large 3 (`mistral-large-2512`) n'a pas
# de réflexion et refuse ce paramètre (400 « not enabled for this model »). Choix d'Era du 07/11 : Large 3, même budget
# qu'Azure. Le paramètre n'est envoyé que si `MISTRAL_REASONING_EFFORT` le demande.

def _corps_envoyes(monkeypatch):
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    corps = []

    def faux_post(url, headers, json, timeout):
        corps.append(json)
        return _ReponseHttp({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(llm.httpx, "post", faux_post)
    return llm, corps


def test_appel_mistral_n_envoie_pas_de_reglage_de_reflexion_par_defaut(monkeypatch):
    llm, corps = _corps_envoyes(monkeypatch)
    monkeypatch.delenv("MISTRAL_REASONING_EFFORT", raising=False)
    llm._appel_mistral("x", 5)
    assert "reasoning_effort" not in corps[0]


def test_le_reglage_de_reflexion_s_envoie_seulement_s_il_est_demande(monkeypatch):
    llm, corps = _corps_envoyes(monkeypatch)
    monkeypatch.setenv("MISTRAL_REASONING_EFFORT", "low")
    llm._appel_mistral("x", 5)
    assert corps[0]["reasoning_effort"] == "low"


def test_une_reponse_mistral_en_blocs_ne_garde_que_le_texte(monkeypatch):
    """Si la réflexion revient malgré tout (modèle changé par MISTRAL_MODEL), seul le texte final est gardé."""
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    blocs = [{"type": "thinking", "thinking": [{"type": "text", "text": "je réfléchis"}]},
             {"type": "text", "text": "Paris."}]
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttp({"choices": [{"message": {"content": blocs}}]}))
    assert llm._appel_mistral("x", 5).texte == "Paris."


def test_une_reponse_mistral_sans_texte_est_une_indisponibilite(monkeypatch):
    from src import llm
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-de-test")
    blocs = [{"type": "thinking", "thinking": [{"type": "text", "text": "je réfléchis encore"}]}]
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttp({"choices": [{"message": {"content": blocs}}]}))
    with pytest.raises(ValueError):
        llm._appel_mistral("x", 5)


def test_la_production_reste_sur_azure_seul(monkeypatch):
    """Ajouter la fonction ne change pas la cascade : sans `LLM_ORDRE`, seul Azure est appelé."""
    from src import llm
    monkeypatch.delenv("LLM_ORDRE", raising=False)
    assert llm._ordre_fournisseurs() == ["foundry"]


def test_la_cascade_ignore_mistral_meme_si_le_reglage_le_nomme():
    """Mistral n'entre dans la cascade qu'après la lecture de son contrat : son nom n'est pas parmi les noms valides."""
    from src import llm
    assert "mistral" not in llm._NOMS_VALIDES

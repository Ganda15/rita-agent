"""Mistral en secours d'Azure, pour les briefings ET les questions (décision d'Era du 14/11/2026).

Le 13/11 vers 20 h, Azure a refusé la clé du serveur (HTTP 401, testé hors de RITA) : briefings et questions en panne en
production, et livraison refusée au pré-test, qui pose une vraie question. Les questions n'avaient aucun repli (décision
D5 du sprint 3 : Azure seul). Décision du 14/11 : Mistral, par son adresse européenne écrite dans le code, passe en
second, Azure restant le premier ; lecture du contrat : `docs/lecture-contrat-mistral-2026-11-13.md`.

Trois règles tenues ici :
- **éteint par défaut** : sans `LLM_ORDRE`, seul Azure est appelé, briefing comme question ; Mistral ne sert que si le
  réglage du serveur le nomme (`LLM_ORDRE=foundry,mistral`) ;
- **les questions restent dans l'UE** : seuls Azure (zone UE) et Mistral (adresse UE) peuvent y répondre ; Anthropic et
  OpenRouter, même nommés, n'y répondent jamais ;
- **aucun texte dans les traces**, quel que soit le fournisseur qui répond (D2, D9).
Aucun test ne parle au réseau : `httpx.post` et les fonctions d'appel sont remplacés par des doublures.
"""
from pathlib import Path

import httpx
import pytest

from src import llm, traces
from tests.test_llm_json import MARQUEUR_QUESTION, MARQUEUR_REPONSE, SCHEMA, _corps, _Enregistreur, _ReponseHttp

RACINE = Path(__file__).resolve().parent.parent
URL_AZURE = "https://ressource.services.ai.azure.com/openai/v1/chat/completions"


def _refus_401():
    reponse = httpx.Response(401, request=httpx.Request("POST", URL_AZURE))
    return httpx.HTTPStatusError("401", request=reponse.request, response=reponse)


@pytest.fixture
def deux_fournisseurs(monkeypatch):
    """Azure et Mistral configurés (fausses clés) ; Anthropic et OpenRouter interdits partout."""
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://ressource.services.ai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_FOUNDRY_API_KEY", "cle-de-test")
    monkeypatch.setenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-5.4")
    monkeypatch.setenv("MISTRAL_API_KEY", "cle-mistral-de-test")
    monkeypatch.delenv("MISTRAL_MODEL", raising=False)
    monkeypatch.delenv("MISTRAL_REASONING_EFFORT", raising=False)

    def interdit(*args, **kwargs):
        raise AssertionError("fournisseur hors UE appelé")

    monkeypatch.setattr(llm, "_appel_anthropic", interdit)
    monkeypatch.setattr(llm, "_appel_openrouter", interdit)


def _poste_azure_refuse(appels, contenu_mistral='{"texte": "ok"}', fin="stop"):
    """`httpx.post` : Azure répond 401, Mistral répond `contenu_mistral` ; chaque appel est noté."""
    def faux_post(url, headers, json, timeout):
        appels.append({"url": url, "headers": headers, "json": json})
        if url == URL_AZURE:
            return _ReponseHttp({}, statut=401)
        return _ReponseHttp(_corps(contenu_mistral, fin=fin))
    return faux_post


# --- le briefing --------------------------------------------------------------------------------------------------

def test_mistral_est_un_nom_valide_de_la_cascade():
    """Avant le 14/11, son nom était refusé tant que le contrat n'était pas lu (ancien test
    `test_la_cascade_ignore_mistral_meme_si_le_reglage_le_nomme`) : la lecture est faite, la décision prise."""
    assert "mistral" in llm._NOMS_VALIDES


def test_par_defaut_un_briefing_n_appelle_jamais_mistral(deux_fournisseurs, monkeypatch):
    monkeypatch.delenv("LLM_ORDRE", raising=False)

    def foundry_refuse(prompt, max_tokens):
        raise _refus_401()

    def mistral_interdit(prompt, max_tokens):
        raise AssertionError("Mistral appelé alors que LLM_ORDRE ne le nomme pas")

    monkeypatch.setattr(llm, "_appel_foundry", foundry_refuse)
    monkeypatch.setattr(llm, "_appel_mistral", mistral_interdit)
    with pytest.raises(llm.AucunFournisseur) as erreur:
        llm.generer_texte_detaille("prompt")
    assert erreur.value.tentatives == [{"fournisseur": "foundry", "reussi": False}]


def test_un_briefing_passe_a_mistral_quand_azure_refuse_la_cle(deux_fournisseurs, monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")

    def foundry_refuse(prompt, max_tokens):
        raise _refus_401()

    monkeypatch.setattr(llm, "_appel_foundry", foundry_refuse)
    monkeypatch.setattr(llm, "_appel_mistral",
                        lambda prompt, max_tokens: llm.Reponse(texte="briefing de secours", modele="mistral-large-2512"))
    resultat = llm.generer_texte_detaille("prompt")
    assert (resultat.texte, resultat.fournisseur, resultat.modele) == ("briefing de secours", "mistral",
                                                                       "mistral-large-2512")
    assert resultat.tentatives == [{"fournisseur": "foundry", "reussi": False}, {"fournisseur": "mistral", "reussi": True}]


def test_quand_azure_repond_mistral_n_est_pas_appele(deux_fournisseurs, monkeypatch):
    """« Les deux » : Azure reste le premier ; Mistral ne sert qu'en cas de panne."""
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")
    monkeypatch.setattr(llm, "_appel_foundry", lambda prompt, max_tokens: llm.Reponse(texte="par Azure"))
    monkeypatch.setattr(llm, "_appel_mistral", lambda *a: (_ for _ in ()).throw(AssertionError("Mistral appelé")))
    assert llm.generer_texte_detaille("prompt").fournisseur == "foundry"


# --- la question --------------------------------------------------------------------------------------------------

def test_par_defaut_une_question_n_appelle_qu_azure(deux_fournisseurs, monkeypatch):
    monkeypatch.delenv("LLM_ORDRE", raising=False)
    appels = []
    monkeypatch.setattr(llm.httpx, "post", _poste_azure_refuse(appels))
    with pytest.raises(llm.FournisseurIndisponible):
        llm.generer_json("prompt", SCHEMA, "reponse_rita")
    assert [a["url"] for a in appels] == [URL_AZURE]


def test_une_question_passe_a_mistral_quand_azure_refuse_la_cle(deux_fournisseurs, monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")
    appels = []
    monkeypatch.setattr(llm.httpx, "post", _poste_azure_refuse(appels, '{"texte": "par Mistral"}'))
    assert llm.generer_json("prompt", SCHEMA, "reponse_rita", max_tokens=300) == '{"texte": "par Mistral"}'
    assert [a["url"] for a in appels] == [URL_AZURE, llm.MISTRAL_URL]
    mistral = appels[1]
    assert mistral["url"] == "https://api.eu.mistral.ai/v1/chat/completions", "l'adresse européenne, écrite dans le code"
    assert mistral["headers"] == {"Authorization": "Bearer cle-mistral-de-test"}
    assert mistral["json"]["model"] == "mistral-large-2512"
    assert mistral["json"]["max_tokens"] == 300, "Mistral nomme la limite max_tokens (OpenAPI de Mistral)"
    assert "max_completion_tokens" not in mistral["json"]
    assert mistral["json"]["response_format"] == {
        "type": "json_schema", "json_schema": {"name": "reponse_rita", "strict": True, "schema": SCHEMA}}


def test_anthropic_et_openrouter_ne_repondent_jamais_a_une_question(deux_fournisseurs, monkeypatch):
    """Même nommés dans `LLM_ORDRE`, ils sont écartés du parcours des questions : seuls Azure et Mistral sont en UE."""
    monkeypatch.setenv("LLM_ORDRE", "anthropic,openrouter,foundry")
    appels = []
    monkeypatch.setattr(llm.httpx, "post", _poste_azure_refuse(appels))
    with pytest.raises(llm.FournisseurIndisponible):
        llm.generer_json("prompt", SCHEMA, "reponse_rita")
    assert [a["url"] for a in appels] == [URL_AZURE]


def test_un_ordre_sans_fournisseur_de_l_ue_garde_azure_pour_les_questions(deux_fournisseurs, monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    appels = []
    monkeypatch.setattr(llm.httpx, "post", _poste_azure_refuse(appels))
    with pytest.raises(llm.FournisseurIndisponible):
        llm.generer_json("prompt", SCHEMA, "reponse_rita")
    assert [a["url"] for a in appels] == [URL_AZURE]


@pytest.mark.parametrize("fin", ["length", "model_length"])
def test_une_reponse_mistral_tronquee_est_signalee(deux_fournisseurs, monkeypatch, fin):
    """`model_length` existe chez Mistral (énumération `finish_reason` de son OpenAPI) : une coupe aussi."""
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")
    monkeypatch.setattr(llm.httpx, "post", _poste_azure_refuse([], '{"texte": "coup', fin=fin))
    with pytest.raises(llm.ReponseTronquee):
        llm.generer_json("prompt", SCHEMA, "reponse_rita")


def test_si_les_deux_refusent_la_question_est_indisponible_sans_texte(deux_fournisseurs, monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")

    def tout_refuse(url, headers, json, timeout):
        raise httpx.ConnectError(f"connexion refusee pendant {MARQUEUR_QUESTION}")

    monkeypatch.setattr(llm.httpx, "post", tout_refuse)
    with pytest.raises(llm.FournisseurIndisponible) as erreur:
        llm.generer_json(MARQUEUR_QUESTION, SCHEMA, "reponse_rita")
    assert MARQUEUR_QUESTION not in str(erreur.value)


def test_sans_cle_mistral_la_question_est_indisponible(deux_fournisseurs, monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")
    monkeypatch.delenv("MISTRAL_API_KEY")
    appels = []
    monkeypatch.setattr(llm.httpx, "post", _poste_azure_refuse(appels))
    with pytest.raises(llm.FournisseurIndisponible):
        llm.generer_json("prompt", SCHEMA, "reponse_rita")
    assert [a["url"] for a in appels] == [URL_AZURE], "sans clé, Mistral n'est pas appelé"


def test_aucun_texte_dans_les_traces_quand_mistral_repond(deux_fournisseurs, monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")
    client = _Enregistreur()
    monkeypatch.setattr(traces, "client_traces", lambda: client)
    monkeypatch.setattr(llm.httpx, "post", _poste_azure_refuse([], '{"texte": "' + MARQUEUR_REPONSE + '"}'))
    llm.generer_json(MARQUEUR_QUESTION, SCHEMA, "reponse_rita")
    assert client.journal, "les deux tentatives doivent être tracées"
    assert MARQUEUR_QUESTION not in repr(client.journal)
    assert MARQUEUR_REPONSE not in repr(client.journal)


# --- le service ---------------------------------------------------------------------------------------------------

def test_compose_passe_la_cle_mistral_a_l_api_et_garde_azure_seul_par_defaut():
    """Compose liste les variables une à une : sans cette ligne, la clé posée sur le serveur n'atteindrait jamais
    l'API. Le défaut de `LLM_ORDRE` reste `foundry` : Mistral ne s'allume que par le réglage du serveur."""
    compose = (RACINE / "docker-compose.yml").read_text(encoding="utf-8")
    api = compose.split("\n  api:\n", 1)[1]
    assert "MISTRAL_API_KEY: ${MISTRAL_API_KEY:-}" in api
    assert "LLM_ORDRE: ${LLM_ORDRE:-foundry}" in api

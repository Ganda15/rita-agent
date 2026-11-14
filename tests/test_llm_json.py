"""Tâche A3 du sprint 3 : l'appel au modèle en JSON, par Azure seul, sans aucun texte dans les traces.

Spec CA2.4 : le parcours des questions n'appelle qu'un fournisseur approuvé (Azure en zone UE), sans repli ; une panne
est une erreur, distincte d'un refus. Spec CA4.3 : ni le texte de la question ni celui de la réponse ne partent dans
les traces, y compris quand une erreur survient. Aucun test ici ne parle au réseau : `httpx.post` et le client de
traces sont remplacés par des doublures qui enregistrent tout ce qu'elles reçoivent.
"""
import httpx
import pytest

from src import llm, traces

MARQUEUR_QUESTION = "MARQUEUR-QUESTION-7f3a"
MARQUEUR_REPONSE = "MARQUEUR-REPONSE-9b2c"
SCHEMA = {"type": "object", "properties": {"texte": {"type": "string"}}, "required": ["texte"],
          "additionalProperties": False}


class _ReponseHttp:
    """Ce que `httpx.post` rendrait : un statut, un corps JSON, un en-tête de région."""

    def __init__(self, corps, statut=200):
        self._corps, self.status_code, self.headers = corps, statut, {"x-ms-region": "Sweden Central"}

    def raise_for_status(self):
        if self.status_code >= 400:
            # Un message d'erreur qui recopie le prompt : le pire cas, celui qui ne doit jamais fuir.
            raise httpx.HTTPStatusError(f"{self.status_code} pour {MARQUEUR_QUESTION}", request=None, response=None)

    def json(self):
        return self._corps


def _corps(contenu, fin="stop"):
    return {"model": "gpt-5.4", "choices": [{"message": {"content": contenu}, "finish_reason": fin}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5}}


class _Observation:
    def __init__(self, journal, options):
        self.journal = journal
        journal.append(("ouvre", options))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        # `exc` contient l'exception éventuelle transmise au SDK : elle est enregistrée, pour vérifier qu'elle ne
        # transporte aucun texte.
        self.journal.append(("ferme", exc))
        return False

    def update(self, **champs):
        self.journal.append(("update", champs))


class _Enregistreur:
    """Double du client Langfuse : il garde tout ce qu'on lui envoie (même méthode que tests/test_traces.py)."""

    def __init__(self):
        self.journal = []

    def start_as_current_observation(self, **options):
        return _Observation(self.journal, options)

    def flush(self):
        self.journal.append(("flush", None))


@pytest.fixture
def azure(monkeypatch):
    """Azure configuré ; Anthropic et OpenRouter interdits : ce parcours ne doit jamais les appeler (D5)."""
    monkeypatch.setenv("AZURE_FOUNDRY_ENDPOINT", "https://ressource.services.ai.azure.com/openai/v1")
    monkeypatch.setenv("AZURE_FOUNDRY_API_KEY", "cle-de-test")
    monkeypatch.setenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-5.4")
    # Depuis le 14/11, les questions suivent `LLM_ORDRE` (Azure, puis Mistral s'il est nommé) : le `.env` local, chargé
    # par `api/main.py`, ne doit pas changer l'ordre de ces tests, ni faire partir un vrai appel vers Mistral.
    monkeypatch.delenv("LLM_ORDRE", raising=False)

    def interdit(*args, **kwargs):
        raise AssertionError("fournisseur non approuvé appelé par le parcours des questions")

    monkeypatch.setattr(llm, "_appel_anthropic", interdit)
    monkeypatch.setattr(llm, "_appel_openrouter", interdit)


def test_generer_json_n_appelle_qu_azure(azure, monkeypatch):
    appels = {}

    def faux_post(url, headers, json, timeout):
        appels.update(url=url, json=json)
        return _ReponseHttp(_corps('{"texte": "ok"}'))

    monkeypatch.setattr(llm.httpx, "post", faux_post)
    brut = llm.generer_json("prompt", SCHEMA, "reponse_rita", max_tokens=300)
    assert brut == '{"texte": "ok"}'
    assert appels["url"] == "https://ressource.services.ai.azure.com/openai/v1/chat/completions"
    format_demande = appels["json"]["response_format"]
    assert format_demande["type"] == "json_schema"
    assert format_demande["json_schema"]["name"] == "reponse_rita"
    assert format_demande["json_schema"]["strict"] is True
    assert format_demande["json_schema"]["schema"] == SCHEMA
    assert appels["json"]["max_completion_tokens"] == 300


def test_sans_configuration_azure_le_fournisseur_est_indisponible(azure, monkeypatch):
    monkeypatch.delenv("AZURE_FOUNDRY_ENDPOINT")
    with pytest.raises(llm.FournisseurIndisponible):
        llm.generer_json("prompt", SCHEMA, "reponse_rita")


def test_une_erreur_http_donne_fournisseur_indisponible_sans_le_corps(azure, monkeypatch):
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttp({}, statut=503))
    with pytest.raises(llm.FournisseurIndisponible) as erreur:
        llm.generer_json(MARQUEUR_QUESTION, SCHEMA, "reponse_rita")
    assert MARQUEUR_QUESTION not in str(erreur.value)


def test_un_delai_depasse_donne_fournisseur_indisponible(azure, monkeypatch):
    def trop_long(*args, **kwargs):
        raise httpx.ReadTimeout("delai depasse")

    monkeypatch.setattr(llm.httpx, "post", trop_long)
    with pytest.raises(llm.FournisseurIndisponible):
        llm.generer_json("prompt", SCHEMA, "reponse_rita")


def test_une_reponse_tronquee_est_signalee(azure, monkeypatch):
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttp(_corps('{"texte": "coup', fin="length")))
    with pytest.raises(llm.ReponseTronquee):
        llm.generer_json("prompt", SCHEMA, "reponse_rita")


def test_aucun_texte_dans_les_traces(azure, monkeypatch):
    client = _Enregistreur()
    monkeypatch.setattr(traces, "client_traces", lambda: client)
    monkeypatch.setattr(llm.httpx, "post",
                        lambda *a, **k: _ReponseHttp(_corps('{"texte": "' + MARQUEUR_REPONSE + '"}')))
    llm.generer_json(MARQUEUR_QUESTION, SCHEMA, "reponse_rita")
    assert client.journal, "l'appel au modèle doit être tracé"
    assert MARQUEUR_QUESTION not in repr(client.journal)
    assert MARQUEUR_REPONSE not in repr(client.journal)


def test_une_erreur_dont_le_message_contient_le_prompt_ne_passe_pas_aux_traces(azure, monkeypatch):
    client = _Enregistreur()
    monkeypatch.setattr(traces, "client_traces", lambda: client)

    def panne(*args, **kwargs):
        raise httpx.ConnectError(f"connexion refusee pendant {MARQUEUR_QUESTION}")

    monkeypatch.setattr(llm.httpx, "post", panne)
    with pytest.raises(llm.FournisseurIndisponible) as erreur:
        llm.generer_json(MARQUEUR_QUESTION, SCHEMA, "reponse_rita")
    assert MARQUEUR_QUESTION not in str(erreur.value)
    assert MARQUEUR_QUESTION not in repr(client.journal)

"""Traçage des appels au modèle (C11, carte #39) : un appel = une génération Langfuse.

Sans clés Langfuse (CI, tests, poste sans compte), le traçage est un no-op silencieux : un
briefing ne doit jamais échouer parce que l'observabilité est absente. Aucun test ici ne
parle au réseau : le client Langfuse est remplacé par un double qui enregistre les appels.
"""
from unittest.mock import patch

import pytest

from src import traces
from src.llm import generer_texte


class _FausseGeneration:
    def __init__(self, journal, **kwargs):
        self.journal, self.kwargs, self.mises_a_jour = journal, kwargs, []

    def __enter__(self):
        self.journal.append(("ouvre", self.kwargs))
        return self

    def __exit__(self, *exc):
        self.journal.append(("ferme", self.kwargs["name"]))
        return False

    def update(self, **kwargs):
        self.mises_a_jour.append(kwargs)
        self.journal.append(("update", kwargs))


class _FauxClient:
    def __init__(self):
        self.journal, self.flushs = [], 0

    def start_as_current_observation(self, **kwargs):
        return _FausseGeneration(self.journal, **kwargs)

    def flush(self):
        self.flushs += 1


@pytest.fixture(autouse=True)
def _sans_cles(monkeypatch):
    for v in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_TRACING_ENABLED"):
        monkeypatch.delenv(v, raising=False)
    traces.reinitialiser()


# --- sans clés : rien ne casse, rien ne part --------------------------------

def test_sans_cles_le_client_est_absent():
    assert traces.client_traces() is None


def test_sans_cles_generer_texte_fonctionne_normalement(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "mistral")
    with patch("src.llm._appel_mistral", return_value="ok"):
        assert generer_texte("prompt") == "ok"


def test_tracing_desactive_par_variable_meme_avec_cles(monkeypatch):
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")
    monkeypatch.setenv("LANGFUSE_TRACING_ENABLED", "false")
    traces.reinitialiser()
    assert traces.client_traces() is None


# --- avec un client : une génération par tentative --------------------------

def test_un_appel_reussi_produit_un_trace_et_une_generation_complete(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "mistral")
    monkeypatch.setenv("MISTRAL_MODEL", "mistral-large-2512")
    client = _FauxClient()
    with patch("src.traces.client_traces", return_value=client),          patch("src.llm._appel_mistral", return_value="texte du briefing"):
        generer_texte("prompt public")

    ouvertures = [k for (ev, k) in client.journal if ev == "ouvre"]
    racines = [k for k in ouvertures if k["as_type"] == "span"]
    generations = [k for k in ouvertures if k["as_type"] == "generation"]
    # Un appel = UN trace (le span racine), qui contient les tentatives : une ligne par
    # briefing dans Langfuse, pas une par fournisseur (mesuré le 02/10 : 9 racines pour 3 appels).
    assert [r["name"] for r in racines] == ["briefing-llm"]
    assert racines[0]["input"] == "prompt public"
    assert len(generations) == 1
    assert generations[0]["name"] == "llm-mistral"
    assert generations[0]["model"] == "mistral-large-2512"
    assert generations[0]["input"] == "prompt public"
    assert generations[0]["metadata"]["fournisseur"] == "mistral"
    sorties = [k for (ev, k) in client.journal if ev == "update" and "output" in k]
    assert [s["output"] for s in sorties] == ["texte du briefing", "texte du briefing"]  # génération puis racine
    assert client.flushs == 1


def test_une_cascade_produit_une_generation_par_tentative_avec_l_echec_marque(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,mistral")
    client = _FauxClient()
    with patch("src.traces.client_traces", return_value=client), \
         patch("src.llm._appel_foundry", side_effect=RuntimeError("quota")), \
         patch("src.llm._appel_mistral", return_value="ok"):
        generer_texte("prompt")

    ouvertures = [k for (ev, k) in client.journal if ev == "ouvre"]
    generations = [k for k in ouvertures if k["as_type"] == "generation"]
    assert [g["name"] for g in generations] == ["llm-foundry", "llm-mistral"]
    assert [g["metadata"]["fournisseur"] for g in generations] == ["foundry", "mistral"]
    assert sum(1 for k in ouvertures if k["as_type"] == "span") == 1
    erreurs = [k for (ev, k) in client.journal if ev == "update" and k.get("level") == "ERROR"]
    assert len(erreurs) == 1
    assert "quota" in erreurs[0]["status_message"]


def test_l_usage_en_tokens_est_transmis_quand_le_fournisseur_le_donne(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "mistral")
    client = _FauxClient()
    reponse = traces.Reponse(texte="ok", modele="claude-sonnet-5",
                            usage={"input": 120, "output": 45})
    with patch("src.traces.client_traces", return_value=client), \
         patch("src.llm._appel_mistral", return_value=reponse):
        assert generer_texte("prompt") == "ok"

    mises_a_jour = [k for (ev, k) in client.journal if ev == "update"]
    assert any(k.get("usage_details") == {"input": 120, "output": 45} for k in mises_a_jour)


def test_la_trace_ne_porte_aucune_cle_d_api(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "mistral")
    monkeypatch.setenv("MISTRAL_API_KEY", "mistral-SECRET-cle")
    client = _FauxClient()
    with patch("src.traces.client_traces", return_value=client), \
         patch("src.llm._appel_mistral", return_value="ok"):
        generer_texte("prompt")
    assert "mistral-SECRET-cle" not in repr(client.journal)

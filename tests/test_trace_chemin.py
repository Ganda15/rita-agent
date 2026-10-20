"""Une trace montre tout le chemin d'un briefing, pas seulement l'appel au modèle (C11, C17).

Audit du 02/10/2026 : la trace Langfuse ne contenait que la cascade de fournisseurs. Le jury
ne pouvait voir ni où passe le temps (Scout, RAG, Rédacteur), ni si un garde-fou a parlé.
Leçon Kaldera : tester la TRACE (qui, dans quel ordre, combien de fois), parce que le texte
d'un modèle varie et que la trace, elle, ne varie pas.

Le chemin est réel (graphe, recherche, garde-fous, cascade) ; seuls le Scout (base), la
collection ChromaDB (vide) et le fournisseur du modèle sont simulés. Aucun réseau.
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from rag.recherche import rechercher
from tests.conftest import CLE_DE_TEST
from tests.test_workflow import scout_lvmh

client_http = TestClient(app)
TEXTE_CONFORME = "Le titre recule de 1,10 % sur la séance."
TEXTE_INTERDIT = "Nous recommandons l'achat de cette valeur."
# Sprint 4 (tâche A3) : toute recherche passe d'abord par le garde-fou de détournement, celle du briefing comprise.
ORDRE_ATTENDU = ["briefing", "scout", "rag", "garde-fou-detournement", "garde-fou-entree", "redacteur",
                 "briefing-llm", "llm-anthropic", "garde-fou-sortie"]


class _FausseObs:
    def __init__(self, journal, kwargs):
        self.journal, self.nom = journal, kwargs["name"]
        journal.append(("ouvre", self.nom, kwargs))
    def __enter__(self): return self
    def __exit__(self, *exc):
        self.journal.append(("ferme", self.nom, {})); return False
    def update(self, **kwargs): self.journal.append(("update", self.nom, kwargs))
    def score_trace(self, **kwargs): self.journal.append(("score", self.nom, kwargs))


class _FauxClient:
    def __init__(self): self.journal = []
    def create_trace_id(self, *, seed=None): return "trace-" + str(seed)
    def start_as_current_observation(self, **kwargs): return _FausseObs(self.journal, kwargs)
    def flush(self): self.journal.append(("flush", "", {}))


class _CollectionVide:
    def get(self, include=None): return {"ids": [], "documents": [], "metadatas": []}


def _briefing(texte, monkeypatch, client=True):
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    faux = _FauxClient() if client else None
    with patch("src.traces.client_traces", return_value=faux), \
         patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("rag.recherche._collection", return_value=_CollectionVide()), \
         patch("src.llm._appel_anthropic", return_value=texte):
        reponse = client_http.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})
    return reponse, (faux.journal if faux else [])


def _updates(journal, nom):
    fusion = {}
    for (g, n, k) in journal:
        if g == "update" and n == nom:
            fusion.update(k)
    return fusion


def test_un_briefing_ouvre_un_span_par_etape_dans_l_ordre_chacun_une_fois(monkeypatch):
    reponse, journal = _briefing(TEXTE_CONFORME, monkeypatch)
    assert reponse.status_code == 200
    ouvertures = [n for (g, n, _k) in journal if g == "ouvre"]
    assert ouvertures == ORDRE_ATTENDU


def test_chaque_etape_est_fermee_avant_la_racine(monkeypatch):
    _, journal = _briefing(TEXTE_CONFORME, monkeypatch)
    evenements = [(g, n) for (g, n, _k) in journal]
    fin_racine = evenements.index(("ferme", "briefing"))
    for nom in ORDRE_ATTENDU[1:]:
        assert evenements.index(("ferme", nom)) < fin_racine, f"{nom} fermé après la racine"


def test_le_span_rag_dit_combien_de_passages_et_pourquoi(monkeypatch):
    _, journal = _briefing(TEXTE_CONFORME, monkeypatch)
    rag = _updates(journal, "rag")["output"]
    assert rag["motif"] == "OUT_OF_CORPUS" and rag["nb_passages"] == 0


def test_le_span_scout_porte_la_fraicheur_et_aucune_donnee_de_portefeuille(monkeypatch):
    _, journal = _briefing(TEXTE_CONFORME, monkeypatch)
    scout = _updates(journal, "scout")["output"]
    assert scout["fraicheur_jours"] == 2 and scout["cotation_perimee"] is False
    assert not {"position", "pru", "quantite"} & set(map(str.lower, scout))


def test_le_garde_fou_de_sortie_est_un_span_avec_son_verdict_sans_le_texte(monkeypatch):
    _, journal = _briefing(TEXTE_INTERDIT, monkeypatch)
    sortie = _updates(journal, "garde-fou-sortie")
    assert sortie["metadata"]["bloque"] is True
    assert "recommandation_explicite_fr" in sortie["metadata"]["motifs"]
    assert sortie["level"] == "WARNING"
    assert "recommandons" not in str([e for e in journal if e[1] == "garde-fou-sortie"])


def test_un_briefing_conforme_laisse_le_garde_fou_de_sortie_sans_avertissement(monkeypatch):
    _, journal = _briefing(TEXTE_CONFORME, monkeypatch)
    sortie = _updates(journal, "garde-fou-sortie")
    assert sortie["metadata"]["bloque"] is False and "level" not in sortie


def test_le_garde_fou_d_entree_est_un_span_et_bloque_avant_la_base():
    faux = _FauxClient()
    def base_interdite(*a, **k): raise AssertionError("la base ne doit pas être ouverte après un refus")
    with patch("src.traces.client_traces", return_value=faux), \
         patch("rag.recherche._collection", side_effect=base_interdite):
        resultat = rechercher("dois-je acheter MC.PA ?", ticker="MC.PA")
    assert resultat.motif == "INTENTION_INTERDITE"
    entree = _updates(faux.journal, "garde-fou-entree")
    assert entree["metadata"]["bloque"] is True and entree["metadata"]["motifs"]
    assert entree["level"] == "WARNING"


def test_sans_client_langfuse_le_chemin_tourne_sans_aucun_span(monkeypatch):
    reponse, journal = _briefing(TEXTE_CONFORME, monkeypatch, client=False)
    assert reponse.status_code == 200 and reponse.json()["conforme_amf"] is True
    assert journal == []

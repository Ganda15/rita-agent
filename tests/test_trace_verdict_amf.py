"""Le verdict du garde-fou de sortie est lisible DANS Langfuse (C11, C20, C17).

Constat de l'audit du 02/10/2026 : la trace gardait le texte brut du modèle, mais ne disait
pas si l'API l'avait diffusé ou refusé. Un refus était donc invisible dans l'outil même qui
sert à surveiller. Et le contrôle (api/main.py) se passe APRÈS l'appel au modèle : le span de
l'appel est déjà fermé quand le verdict existe.

Structure retenue : l'API ouvre une racine `briefing` ; l'appel au modèle (`briefing-llm`) et
ses tentatives se rangent dessous (mesuré le 02/10 : le contexte OpenTelemetry traverse bien
LangGraph) ; le verdict est posé sur cette racine, en métadonnées, en niveau WARNING si refus,
et en note booléenne `conforme_amf` (1 ou 0) qu'un tableau ou une alerte peut compter.

Aucun test ici ne parle au réseau : le client Langfuse est un double qui note l'ordre des
événements.
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from src.llm import generer_texte
from tests.conftest import CLE_DE_TEST

client_http = TestClient(app)

TEXTE_INTERDIT = "Nous recommandons l'achat de cette valeur."
TEXTE_CONFORME = "Le titre recule de 1,99 % sur la séance."


class _FausseObservation:
    def __init__(self, journal, kwargs):
        self.journal, self.kwargs = journal, kwargs
        self.nom = kwargs["name"]

    def __enter__(self):
        self.journal.append(("ouvre", self.nom, self.kwargs))
        return self

    def __exit__(self, *exc):
        self.journal.append(("ferme", self.nom, {}))
        return False

    def update(self, **kwargs):
        self.journal.append(("update", self.nom, kwargs))

    def score_trace(self, **kwargs):
        self.journal.append(("score", self.nom, kwargs))


class _FauxClient:
    def __init__(self):
        self.journal = []

    def create_trace_id(self, *, seed=None):
        return "trace-" + str(seed)

    def start_as_current_observation(self, **kwargs):
        return _FausseObservation(self.journal, kwargs)

    def flush(self):
        self.journal.append(("flush", "", {}))


def _modele_simule(texte):
    """Remplace tout le graphe : l'appel au modèle se fait pour de vrai (donc tracé par
    `generer_texte`), seul le fournisseur est simulé. Même chemin qu'en production."""
    def _graphe(ticker):
        brut = generer_texte("prompt")
        return {"ticker": ticker, "price": 457.5, "change_pct": -1.99,
                "currency": "EUR", "error": "", "briefing": brut}
    return _graphe


def _appeler(texte, monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "anthropic")
    faux = _FauxClient()
    with patch("src.traces.client_traces", return_value=faux), \
         patch("src.llm._appel_anthropic", return_value=texte), \
         patch("api.main.generer_briefing_complet", side_effect=_modele_simule(texte)):
        reponse = client_http.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})
    return reponse, faux.journal


def _evenements(journal, genre, nom=None):
    return [(g, n, k) for (g, n, k) in journal if g == genre and (nom is None or n == nom)]


def test_l_appel_au_modele_est_range_sous_la_racine_briefing(monkeypatch):
    _, journal = _appeler(TEXTE_CONFORME, monkeypatch)

    ordre = [(g, n) for (g, n, _k) in journal if g in ("ouvre", "ferme") and n in ("briefing", "briefing-llm")]
    assert ordre == [("ouvre", "briefing"), ("ouvre", "briefing-llm"),
                     ("ferme", "briefing-llm"), ("ferme", "briefing")], \
        "briefing-llm doit s'ouvrir et se fermer à l'intérieur de la racine briefing"


def test_un_refus_est_marque_sur_la_racine_sans_recopier_le_texte(monkeypatch):
    reponse, journal = _appeler(TEXTE_INTERDIT, monkeypatch)

    assert reponse.json()["conforme_amf"] is False
    mises_a_jour = _evenements(journal, "update", "briefing")
    assert mises_a_jour, "le verdict doit être posé sur la racine briefing"
    tout = {}
    for (_g, _n, k) in mises_a_jour:
        tout.update(k)
    assert tout["metadata"]["conforme_amf"] is False
    assert "recommandation_explicite_fr" in tout["metadata"]["motifs_amf"]
    assert tout["level"] == "WARNING"
    # le texte refusé reste dans la génération (utile pour comprendre le motif), mais pas sur la racine
    assert "recommandons" not in str(mises_a_jour)


def test_un_refus_ajoute_la_note_conforme_amf_a_zero(monkeypatch):
    _, journal = _appeler(TEXTE_INTERDIT, monkeypatch)

    notes = _evenements(journal, "score", "briefing")
    assert len(notes) == 1
    note = notes[0][2]
    assert note["name"] == "conforme_amf"
    assert note["value"] == 0.0
    assert note["data_type"] == "BOOLEAN"


def test_un_briefing_conforme_ajoute_la_note_a_un_sans_avertissement(monkeypatch):
    reponse, journal = _appeler(TEXTE_CONFORME, monkeypatch)

    assert reponse.json()["conforme_amf"] is True
    notes = _evenements(journal, "score", "briefing")
    assert len(notes) == 1 and notes[0][2]["value"] == 1.0
    niveaux = [k.get("level") for (_g, _n, k) in _evenements(journal, "update", "briefing")]
    assert "WARNING" not in niveaux, "un briefing conforme ne doit pas être marqué en avertissement"


def test_la_trace_est_envoyee_apres_la_fermeture_de_la_racine(monkeypatch):
    """Un span encore ouvert n'est pas exporté : le flush doit venir après `ferme briefing`."""
    _, journal = _appeler(TEXTE_CONFORME, monkeypatch)

    evenements = [(g, n) for (g, n, _k) in journal]
    position_fermeture = evenements.index(("ferme", "briefing"))
    assert ("flush", "") in evenements[position_fermeture + 1:], \
        "aucun flush après la fermeture de la racine : le verdict ne partirait jamais"


def test_une_erreur_scout_ferme_quand_meme_la_racine_et_envoie_la_trace(monkeypatch):
    faux = _FauxClient()
    en_erreur = {"ticker": "XXX.PA", "price": 0.0, "change_pct": 0.0,
                 "currency": "", "briefing": "", "error": "no data"}
    with patch("src.traces.client_traces", return_value=faux), \
         patch("api.main.generer_briefing_complet", return_value=en_erreur):
        reponse = client_http.post("/briefing?ticker=XXX.PA", headers={"X-API-Key": CLE_DE_TEST})

    assert reponse.status_code == 502
    evenements = [(g, n) for (g, n, _k) in faux.journal]
    assert ("ferme", "briefing") in evenements
    assert ("flush", "") in evenements[evenements.index(("ferme", "briefing")) + 1:]
    assert _evenements(faux.journal, "score") == [], "pas de verdict AMF quand il n'y a pas de texte"

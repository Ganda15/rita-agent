"""Sprint 5, étape 1 : les compteurs de la vigie (plan du sprint 5, § 2 « Mesures » et « Ce qu'on compte »).

Chaque appel à `/question` ou `/briefing` laisse une observation en mémoire : sa catégorie (six possibles), son motif,
sa durée et ses jetons. Jamais de texte. `/question` refuse en HTTP 200 : on compte le résultat métier, pas le code
HTTP. Le compte reste juste quand plusieurs appels arrivent en même temps (verrou), et la mémoire est bornée deux
fois : 24 h, et 20 000 observations au plus (les rejets 403 et 422 ne passent pas par le quota).
"""
import contextvars
import logging
import re
import threading
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from agents import question
from api import limiteur
from api.main import app
from monitorage import compteurs
from monitorage.compteurs import Compteurs, categorie
from src import llm
from src.traces import Reponse
from tests.conftest import CLE_DE_TEST
from tests.test_llm_json import SCHEMA, _corps, _ReponseHttp, azure  # noqa: F401, `azure` est une fixture

CLE = {"X-API-Key": CLE_DE_TEST}
MARQUEUR = "MARQUEUR-QUESTION-5e1d"


class _Horloge:
    """Une horloge qu'on avance à la main."""

    def __init__(self, t=1_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def mesures(monkeypatch):
    """Des compteurs neufs pour ce test, à la place de ceux du module."""
    neufs = Compteurs()
    monkeypatch.setattr(compteurs, "COMPTEURS", neufs)
    return neufs


def _repondre(monkeypatch, resultat=None, erreur=None):
    """Le parcours des questions remplacé : la route seule est testée ici."""
    def faux(texte, *args, **kwargs):
        if erreur is not None:
            raise erreur
        return resultat

    monkeypatch.setattr(question, "repondre", faux)


def _briefing(texte_du_modele, erreur=""):
    resultat = {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99, "currency": "EUR", "error": erreur,
                "briefing": texte_du_modele}
    with patch("api.main.generer_briefing_complet", return_value=resultat):
        return TestClient(app).post("/briefing?ticker=MC.PA", headers=CLE)


# --- les six catégories ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("code, statut, motif, attendu", [
    (200, "reponse", "OK", "reponse"),
    (200, "refus", "TENTATIVE_DETOURNEMENT", "refus_securite"),
    (200, "refus", "INTENTION_INTERDITE", "refus_securite"),
    (200, "refus", "FUITE_BLOQUEE", "refus_securite"),
    (200, "refus", "SORTIE_NON_CONFORME", "refus_securite"),
    (200, "refus", "OUT_OF_CORPUS", "refus_corpus"),
    (200, "refus", "ABSTENTION", "refus_corpus"),
    (200, "refus", "CITATIONS_INVALIDES", "refus_qualite"),
    (200, "refus", "NOMBRE_NON_SOURCE", "refus_qualite"),
    (503, "erreur", "FOURNISSEUR_INDISPONIBLE", "erreur_technique"),
    (500, "erreur", "ERREUR_INTERNE", "erreur_technique"),
    (502, "erreur", None, "erreur_technique"),
    (403, None, None, "rejet_acces_saisie"),
    (422, None, None, "rejet_acces_saisie"),
    (429, None, None, "rejet_acces_saisie"),
])
def test_chaque_issue_a_sa_categorie(code, statut, motif, attendu):
    assert categorie(code, statut, motif) == attendu


def test_chaque_motif_de_refus_du_parcours_a_une_categorie():
    # Relevé dans le code : un motif de refus ajouté au parcours sans être rangé ici ferait échouer ce test.
    source = Path(question.__file__).read_text(encoding="utf-8")
    noms = set(re.findall(r"_refus\(([A-Z_]+)", source))
    motifs = {getattr(question, nom) for nom in noms} | set(question.TEXTES_REFUS)
    assert len(motifs) >= 7
    for motif in motifs:
        assert categorie(200, "refus", motif) != "erreur_technique", motif


def test_un_motif_inconnu_n_est_jamais_compte_comme_sain(caplog):
    with caplog.at_level(logging.WARNING):
        assert categorie(200, "refus", "MOTIF_INVENTE") == "erreur_technique"
    assert "motif inconnu" in caplog.text


# --- la mémoire : verrou, 24 h, 20 000 -------------------------------------------------------------------------------

def test_aucun_compte_perdu_quand_huit_fils_comptent_en_meme_temps():
    mesures = Compteurs()

    def compter():
        for _ in range(1000):
            mesures.noter("/question", 200, "reponse", "OK", 5)

    fils = [threading.Thread(target=compter) for _ in range(8)]
    for un_fil in fils:
        un_fil.start()
    for un_fil in fils:
        un_fil.join()
    assert len(mesures.observations()) == 8000


def test_une_observation_de_plus_de_24_h_est_oubliee():
    horloge = _Horloge()
    mesures = Compteurs(horloge=horloge)
    mesures.noter("/question", 200, "reponse", "OK", 5)
    horloge.t += 24 * 3600 + 1
    assert mesures.observations() == []


def test_le_debut_de_la_periode_suit_ce_qui_est_oublie():
    # « mesures depuis HH:MM » : le démarrage tant que rien n'est oublié, puis l'heure de la dernière observation oubliée.
    horloge = _Horloge(1000.0)
    mesures = Compteurs(horloge=horloge)
    assert mesures.debut() == 1000.0
    horloge.t = 2000.0
    mesures.noter("/question", 200, "reponse", "OK", 5)
    horloge.t = 2000.0 + 24 * 3600 + 1
    mesures.observations()
    assert mesures.debut() == 2000.0


def test_la_20_001e_observation_fait_partir_la_plus_ancienne():
    mesures = Compteurs()
    for i in range(20_001):
        mesures.noter("/question", 200, "reponse", "OK", i)
    observations = mesures.observations()
    assert len(observations) == 20_000
    assert observations[0].duree_ms == 1


# --- les jetons : toutes les tentatives -------------------------------------------------------------------------------

def test_les_jetons_de_deux_tentatives_s_additionnent():
    def appel():
        compteurs.debuter_consommation()
        compteurs.ajouter_jetons(100, 20)
        compteurs.ajouter_jetons(50, 10)
        return compteurs.consommation()

    assert contextvars.Context().run(appel) == (150, 30)


def test_des_jetons_hors_d_un_appel_ne_vont_nulle_part():
    def hors_appel():
        compteurs.ajouter_jetons(5, 5)
        return compteurs.consommation()

    assert contextvars.Context().run(hors_appel) == (0, 0)


def test_generer_json_ajoute_les_jetons_de_l_appel(azure, monkeypatch):  # noqa: F811
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: _ReponseHttp(_corps('{"texte": "ok"}')))

    def appel():
        compteurs.debuter_consommation()
        llm.generer_json("prompt", SCHEMA, "reponse_rita")
        return compteurs.consommation()

    assert contextvars.Context().run(appel) == (10, 5)


def test_generer_texte_ajoute_les_jetons_de_la_tentative_qui_en_rend(monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry,anthropic")

    def en_panne(prompt, max_tokens):
        raise RuntimeError("panne simulée")

    monkeypatch.setattr(llm, "_appel_foundry", en_panne)
    monkeypatch.setattr(llm, "_appel_anthropic",
                        lambda prompt, max_tokens: Reponse(texte="ok", usage={"input": 30, "output": 7}))

    def appel():
        compteurs.debuter_consommation()
        llm.generer_texte("prompt")
        return compteurs.consommation()

    assert contextvars.Context().run(appel) == (30, 7)


# --- les routes : chaque appel laisse une observation, sans texte ---------------------------------------------------

@pytest.mark.parametrize("resultat, code, attendu", [
    (question.ReponseQuestion("reponse", "OK", "texte"), 200, "reponse"),
    (question.ReponseQuestion("refus", "TENTATIVE_DETOURNEMENT", "texte"), 200, "refus_securite"),
    (question.ReponseQuestion("erreur", "FOURNISSEUR_INDISPONIBLE", "texte"), 503, "erreur_technique"),
])
def test_une_question_laisse_une_observation_sans_texte(monkeypatch, mesures, resultat, code, attendu):
    _repondre(monkeypatch, resultat)
    reponse = TestClient(app).post("/question", json={"question": f"Qui reprend TAP ? {MARQUEUR}"}, headers=CLE)
    assert reponse.status_code == code
    [observation] = mesures.observations()
    assert (observation.route, observation.categorie, observation.motif) == ("/question", attendu, resultat.motif)
    assert MARQUEUR not in repr(mesures.observations())


def test_une_erreur_imprevue_de_question_est_comptee(monkeypatch, mesures):
    _repondre(monkeypatch, erreur=RuntimeError(MARQUEUR))
    reponse = TestClient(app).post("/question", json={"question": "Qui reprend TAP ?"}, headers=CLE)
    assert reponse.status_code == 500
    [observation] = mesures.observations()
    assert (observation.categorie, observation.motif) == ("erreur_technique", "ERREUR_INTERNE")
    assert MARQUEUR not in repr(mesures.observations())


def test_les_rejets_d_acces_et_de_saisie_sont_comptes(monkeypatch, mesures):
    client = TestClient(app)
    _repondre(monkeypatch, question.ReponseQuestion("reponse", "OK", "texte"))
    assert client.post("/question", json={"question": "Qui reprend TAP ?"}).status_code == 403
    assert client.post("/question", json={"question": "ab"}, headers=CLE).status_code == 422
    # Relevé en écrivant ce test (22/10) : une saisie refusée en 422 consomme quand même une place du quota, car FastAPI
    # passe par le limiteur avant de rejeter la saisie. Le quota de 1 est donc posé après le 422.
    monkeypatch.setattr(limiteur, "LIMITEUR", limiteur.Limiteur(1))
    assert client.post("/question", json={"question": "Qui reprend TAP ?"}, headers=CLE).status_code == 200
    assert client.post("/question", json={"question": "Qui reprend TAP ?"}, headers=CLE).status_code == 429
    assert [o.categorie for o in mesures.observations()] == [
        "rejet_acces_saisie", "rejet_acces_saisie", "reponse", "rejet_acces_saisie"]


def test_un_rejet_hors_des_deux_routes_n_est_pas_compte(mesures):
    assert TestClient(app).get("/donnees/valeurs").status_code == 403
    assert mesures.observations() == []


@pytest.mark.parametrize("texte, erreur, code, attendu, motif", [
    ("Le titre recule de 1,10 % sur la séance.", "", 200, "reponse", "OK"),
    ("Nous recommandons l'achat de cette valeur.", "", 200, "refus_securite", "SORTIE_NON_CONFORME"),
    ("", "modele indisponible", 502, "erreur_technique", "BRIEFING_INDISPONIBLE"),
])
def test_un_briefing_laisse_une_observation(mesures, texte, erreur, code, attendu, motif):
    assert _briefing(texte, erreur).status_code == code
    [observation] = mesures.observations()
    assert (observation.route, observation.categorie, observation.motif) == ("/briefing", attendu, motif)


def test_un_briefing_pour_une_valeur_inconnue_est_un_rejet(monkeypatch, mesures):
    monkeypatch.setattr("api.main.valeur_existe", lambda ticker: False)
    assert TestClient(app).post("/briefing?ticker=INCONNU.PA", headers=CLE).status_code == 422
    [observation] = mesures.observations()
    assert (observation.route, observation.categorie) == ("/briefing", "rejet_acces_saisie")

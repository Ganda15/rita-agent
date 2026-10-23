"""Sprint 5, étape 6 : la panne simulée (plan du sprint 5, § 2 « Panne simulée » ; grille de l'atelier 5, critère 4).

Une panne posée et retirée par commande, sûre et réversible : protégée par une clé d'exercice distincte de la clé des
questions, elle se termine seule après 20 minutes au plus. Pendant la panne, `/question` répond 503 comme si le
fournisseur du modèle était tombé, sans appeler le parcours ni le modèle ; l'erreur est comptée, et c'est ce compte
qui fera franchir le seuil. `/sante` dit qu'un exercice est en cours, qui l'a posé et pourquoi. Sans
`RITA_CLE_EXERCICE`, les routes refusent : aucune panne ne se pose sans la clé de l'opérateur.
"""
import logging

import pytest
from fastapi.testclient import TestClient

from agents import question
from api.main import app
from monitorage import compteurs, exercice
from monitorage.compteurs import Compteurs
from tests.conftest import CLE_DE_TEST

CLE_EXERCICE = "cle-d-exercice-de-test-32-caracteres"
CLE_QUESTIONS = {"X-API-Key": CLE_DE_TEST}
ENTETE = {"X-Cle-Exercice": CLE_EXERCICE}
DEMANDE = {"nom": "Era", "motif": "répétition atelier 5"}


class _Horloge:
    def __init__(self, t=1_000_000.0):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def horloge(monkeypatch):
    """Un exercice neuf, sur une horloge qu'on avance à la main ; la clé d'exercice posée."""
    horloge = _Horloge()
    monkeypatch.setattr(exercice, "EXERCICE", exercice.Exercice(horloge=horloge))
    monkeypatch.setenv("RITA_CLE_EXERCICE", CLE_EXERCICE)
    return horloge


@pytest.fixture
def mesures(monkeypatch):
    neufs = Compteurs()
    monkeypatch.setattr(compteurs, "COMPTEURS", neufs)
    return neufs


# --- l'état de l'exercice --------------------------------------------------------------------------------------------

def test_un_exercice_pose_se_termine_seul_apres_sa_duree():
    horloge = _Horloge()
    etat = exercice.Exercice(horloge=horloge)
    etat.poser("Era", "répétition", 20 * 60)
    assert etat.etat()["nom"] == "Era"
    horloge.t += 20 * 60
    assert etat.etat() is None


def test_un_exercice_se_termine_a_la_main():
    etat = exercice.Exercice(horloge=_Horloge())
    etat.poser("Era", "répétition", 600)
    assert etat.finir()["motif"] == "répétition"
    assert etat.etat() is None and etat.finir() is None


@pytest.mark.parametrize("duree_s", [0, 20 * 60 + 1])
def test_une_duree_hors_bornes_est_refusee(duree_s):
    with pytest.raises(ValueError):
        exercice.Exercice(horloge=_Horloge()).poser("Era", "répétition", duree_s)


def test_un_second_exercice_pendant_le_premier_est_refuse():
    etat = exercice.Exercice(horloge=_Horloge())
    etat.poser("Era", "répétition", 600)
    with pytest.raises(exercice.ExerciceEnCours):
        etat.poser("Binôme", "autre", 600)


# --- les routes, et leur clé ---------------------------------------------------------------------------------------------

def test_sans_cle_d_exercice_configuree_les_exercices_sont_desactives(horloge, monkeypatch):
    monkeypatch.delenv("RITA_CLE_EXERCICE")
    reponse = TestClient(app).post("/exercice/panne", json=DEMANDE, headers=ENTETE)
    assert reponse.status_code == 503 and "désactivés" in reponse.json()["detail"]
    assert exercice.EXERCICE.etat() is None


@pytest.mark.parametrize("entetes", [{}, {"X-Cle-Exercice": "mauvaise-cle-mauvaise-cle"},
                                     {"X-Cle-Exercice": CLE_DE_TEST}, CLE_QUESTIONS])
def test_sans_la_bonne_cle_d_exercice_la_panne_est_refusee(horloge, entetes):
    # La clé des questions ne suffit pas : ni dans l'en-tête de l'exercice, ni dans le sien.
    assert TestClient(app).post("/exercice/panne", json=DEMANDE, headers=entetes).status_code == 403
    assert exercice.EXERCICE.etat() is None


@pytest.mark.parametrize("demande", [{"nom": "Era", "motif": "ok"}, {"nom": "", "motif": "répétition"},
                                     {"nom": "Era", "motif": "répétition", "duree_min": 21},
                                     {"nom": "Era", "motif": "[clic ici](https://piege.test)"},
                                     {"nom": "Era", "motif": "répétition", "autre": 1}])
def test_une_demande_invalide_est_refusee(horloge, demande):
    assert TestClient(app).post("/exercice/panne", json=demande, headers=ENTETE).status_code == 422


def test_la_panne_se_pose_puis_se_retire(horloge):
    client = TestClient(app)
    pose = client.post("/exercice/panne", json={**DEMANDE, "duree_min": 10}, headers=ENTETE)
    assert pose.status_code == 200 and pose.json()["nom"] == "Era"
    assert client.post("/exercice/panne", json=DEMANDE, headers=ENTETE).status_code == 409
    fin = client.post("/exercice/fin", json={"nom": "Era", "motif": "fin de la répétition"}, headers=ENTETE)
    assert fin.status_code == 200 and fin.json()["statut"] == "exercice terminé"
    assert client.post("/exercice/fin", json={"nom": "Era", "motif": "encore"}, headers=ENTETE).json()["statut"] \
        == "aucun exercice en cours"


def test_le_journal_dit_qui_et_pourquoi_jamais_la_cle(horloge, caplog):
    client = TestClient(app)
    with caplog.at_level(logging.WARNING):
        client.post("/exercice/panne", json=DEMANDE, headers=ENTETE)
        client.post("/exercice/fin", json={"nom": "Era", "motif": "fin de la répétition"}, headers=ENTETE)
        client.post("/exercice/panne", json=DEMANDE, headers={"X-Cle-Exercice": "mauvaise-cle-mauvaise-cle"})
    assert "exercice de panne pose" in caplog.text and "exercice de panne termine" in caplog.text
    assert "'Era'" in caplog.text and "répétition atelier 5" in caplog.text
    assert "cle d'exercice refusee" in caplog.text
    assert CLE_EXERCICE not in caplog.text and "mauvaise-cle-mauvaise-cle" not in caplog.text


# --- pendant la panne -------------------------------------------------------------------------------------------------------

def test_pendant_la_panne_question_repond_503_sans_appeler_le_modele(horloge, mesures, monkeypatch):
    appels = []
    monkeypatch.setattr(question, "repondre", lambda *a, **k: appels.append(1))
    client = TestClient(app)
    client.post("/exercice/panne", json=DEMANDE, headers=ENTETE)
    reponse = client.post("/question", json={"question": "Comment Airbus répartit-il ses chaînes ?"},
                          headers=CLE_QUESTIONS)
    assert reponse.status_code == 503
    corps = reponse.json()
    assert corps["motif"] == "FOURNISSEUR_INDISPONIBLE" and "panne simulée" in corps["exercice"]
    assert appels == []
    [observation] = mesures.observations()
    assert (observation.categorie, observation.motif) == ("erreur_technique", "FOURNISSEUR_INDISPONIBLE")


def test_apres_la_fin_question_repond_normalement(horloge, mesures, monkeypatch):
    monkeypatch.setattr(question, "repondre", lambda *a, **k: question.ReponseQuestion("reponse", "OK", "texte"))
    client = TestClient(app)
    client.post("/exercice/panne", json=DEMANDE, headers=ENTETE)
    client.post("/exercice/fin", json={"nom": "Era", "motif": "fin"}, headers=ENTETE)
    reponse = client.post("/question", json={"question": "Comment Airbus répartit-il ses chaînes ?"},
                          headers=CLE_QUESTIONS)
    assert reponse.status_code == 200 and "exercice" not in reponse.json()


def test_la_panne_se_termine_seule_meme_si_personne_ne_la_retire(horloge, mesures, monkeypatch):
    monkeypatch.setattr(question, "repondre", lambda *a, **k: question.ReponseQuestion("reponse", "OK", "texte"))
    client = TestClient(app)
    client.post("/exercice/panne", json={**DEMANDE, "duree_min": 5}, headers=ENTETE)
    horloge.t += 5 * 60
    reponse = client.post("/question", json={"question": "Comment Airbus répartit-il ses chaînes ?"},
                          headers=CLE_QUESTIONS)
    assert reponse.status_code == 200


def test_sante_dit_qu_un_exercice_est_en_cours(horloge, monkeypatch):
    from monitorage import signaux
    monkeypatch.setattr(signaux, "lire_fraicheur_par_valeur", lambda dsn=None: None)
    client = TestClient(app)
    assert client.get("/sante", headers=CLE_QUESTIONS).json()["exercice"] is None
    client.post("/exercice/panne", json=DEMANDE, headers=ENTETE)
    etat = client.get("/sante", headers=CLE_QUESTIONS).json()["exercice"]
    assert (etat["nom"], etat["motif"]) == ("Era", "répétition atelier 5")
    assert etat["depuis"] and etat["fin_au_plus_tard"]


def test_le_message_503_donne_les_heures_avec_leur_fuseau(horloge, mesures, monkeypatch):
    # Le serveur ne connaît pas le fuseau du lecteur : le message donne l'horodatage complet, avec son décalage, au lieu
    # d'une heure « HH:MM » sans fuseau (relevé à l'étape 11 : 16:58 lu pour 18:58 à Paris).
    monkeypatch.setattr(question, "repondre", lambda *a, **k: None)
    client = TestClient(app)
    pose = client.post("/exercice/panne", json=DEMANDE, headers=ENTETE).json()
    corps = client.post("/question", json={"question": "Comment Airbus répartit-il ses chaînes ?"},
                        headers=CLE_QUESTIONS).json()
    assert pose["depuis"] in corps["exercice"] and pose["fin_au_plus_tard"] in corps["exercice"]

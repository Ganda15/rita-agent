"""Le frein des essais de clé (constat S3 de la revue OWASP du 03/10 ; carte #75, point 4 ; plan validé par Era le 07/11).

Pourquoi : rien ne freinait les essais de clé. La clé de production est longue, la deviner par essais n'est pas
réaliste ; le risque réel est un flot d'essais qui remplit le journal et occupe le service (OWASP API4:2023). Au-delà de
10 mauvaises clés en 15 minutes depuis une même adresse, l'API répond 429 sans même comparer la clé.

L'adresse IP est une donnée personnelle : gardée en mémoire 15 minutes au plus, jamais écrite dans le journal
(registre RGPD, traitement T9). Une clé absente ne compte pas : ce n'est pas un essai, et l'interface n'envoie jamais de
clé vide. Une bonne clé ne compte pas non plus.
"""
import logging

import pytest
from fastapi.testclient import TestClient

from api import limiteur
from api.limiteur import FreinDesEssais
from tests.conftest import CLE_DE_TEST

ROUTE = "/donnees/valeurs"


class Horloge:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


# --- La classe, avec une horloge simulée ------------------------------------------------------------------------------

def test_neuf_mauvaises_cles_ne_bloquent_pas_la_dixieme_bloque():
    frein = FreinDesEssais(seuil=10, fenetre_s=900, horloge=Horloge())
    for _ in range(9):
        frein.noter_echec("198.51.100.7")
    assert frein.bloquee("198.51.100.7") == (False, 0)
    frein.noter_echec("198.51.100.7")
    bloquee, attente = frein.bloquee("198.51.100.7")
    assert bloquee and 1 <= attente <= 900


def test_une_autre_adresse_passe_encore():
    frein = FreinDesEssais(seuil=10, fenetre_s=900, horloge=Horloge())
    for _ in range(10):
        frein.noter_echec("198.51.100.7")
    assert frein.bloquee("203.0.113.9") == (False, 0)


def test_apres_quinze_minutes_l_adresse_repasse():
    horloge = Horloge()
    frein = FreinDesEssais(seuil=10, fenetre_s=900, horloge=horloge)
    for _ in range(10):
        frein.noter_echec("198.51.100.7")
    horloge.t += 899
    assert frein.bloquee("198.51.100.7")[0]
    horloge.t += 1
    assert frein.bloquee("198.51.100.7") == (False, 0)


def test_seul_l_echec_qui_franchit_le_seuil_declenche_le_blocage():
    """Pour n'écrire qu'une ligne de journal par blocage, pas une par essai."""
    frein = FreinDesEssais(seuil=3, fenetre_s=900, horloge=Horloge())
    assert [frein.noter_echec("198.51.100.7") for _ in range(5)] == [False, False, True, False, False]


def test_le_nombre_d_adresses_suivies_est_borne():
    """Un flot d'adresses différentes ne fait pas grossir la mémoire sans fin : les plus anciennes sont oubliées."""
    frein = FreinDesEssais(seuil=1, fenetre_s=900, max_adresses=3, horloge=Horloge())
    for adresse in ("192.0.2.1", "192.0.2.2", "192.0.2.3", "192.0.2.4"):
        frein.noter_echec(adresse)
    assert len(frein) == 3
    assert frein.bloquee("192.0.2.1") == (False, 0)
    assert frein.bloquee("192.0.2.4")[0]


def test_un_seuil_invalide_est_refuse():
    with pytest.raises(ValueError):
        FreinDesEssais(seuil=0)


# --- Dans l'API ----------------------------------------------------------------------------------------------------

@pytest.fixture
def client(monkeypatch):
    """Un frein au seuil du plan (10), neuf pour ce test ; le reste de la suite a un seuil qui ne gêne jamais."""
    from api.main import app

    monkeypatch.setattr(limiteur, "FREIN", FreinDesEssais(seuil=10, fenetre_s=900))
    return TestClient(app)


def test_la_onzieme_mauvaise_cle_recoit_429_meme_avec_la_bonne_ensuite(client):
    codes = [client.get(ROUTE, headers={"X-API-Key": f"mauvaise-cle-numero-{i:02d}-xxxxxxxx"}).status_code
             for i in range(10)]
    assert codes == [403] * 10
    reponse = client.get(ROUTE, headers={"X-API-Key": "mauvaise-cle-numero-11-xxxxxxxx"})
    assert reponse.status_code == 429
    assert int(reponse.headers["Retry-After"]) >= 1
    assert reponse.json()["detail"]["motif"] == "TROP_D_ESSAIS"
    assert reponse.headers.get("X-Request-ID")
    # Bloquée, l'adresse n'est plus comparée : la bonne clé ne passe pas non plus, et n'apprend rien à qui essaie.
    assert client.get(ROUTE, headers={"X-API-Key": CLE_DE_TEST}).status_code == 429


def test_une_cle_absente_ne_compte_pas(client):
    assert [client.get(ROUTE).status_code for _ in range(15)] == [403] * 15
    assert client.get(ROUTE, headers={"X-API-Key": CLE_DE_TEST}).status_code != 429


def test_une_bonne_cle_ne_compte_pas(client):
    for _ in range(15):
        assert client.get(ROUTE, headers={"X-API-Key": CLE_DE_TEST}).status_code != 429
    for i in range(9):
        client.get(ROUTE, headers={"X-API-Key": f"mauvaise-cle-numero-{i:02d}-xxxxxxxx"})
    assert client.get(ROUTE, headers={"X-API-Key": CLE_DE_TEST}).status_code != 429


def test_le_blocage_laisse_une_seule_ligne_sans_cle_ni_adresse(client, caplog):
    caplog.set_level(logging.WARNING)
    for i in range(14):
        client.get(ROUTE, headers={"X-API-Key": f"mauvaise-cle-numero-{i:02d}-xxxxxxxx"})
    lignes = [r.getMessage() for r in caplog.records if "essais de cle bloques" in r.getMessage()]
    assert len(lignes) == 1, lignes
    assert "mauvaise-cle" not in lignes[0]
    assert "testclient" not in lignes[0]   # l'adresse que le client de test présente
    assert "request_id=" in lignes[0] and f"route={ROUTE}" in lignes[0]


def test_le_seuil_se_regle_par_l_environnement(monkeypatch):
    monkeypatch.setenv("RITA_ESSAIS_DE_CLE_MAX", "25")
    assert limiteur.frein_depuis_l_environnement().seuil == 25
    monkeypatch.delenv("RITA_ESSAIS_DE_CLE_MAX")
    assert limiteur.frein_depuis_l_environnement().seuil == 10


def test_le_contrat_annonce_le_frein():
    """Le client lit dans le contrat qu'une adresse trop insistante reçoit 429 (OWASP API9, inventaire)."""
    from api.main import DESCRIPTION

    authentification = DESCRIPTION.split("### Authentification", 1)[1].split("###", 1)[0]
    assert "TROP_D_ESSAIS" in authentification and "15 minutes" in authentification


# --- La clé d'exercice (revue de sécurité automatique du 07/11 : même frein sur la route sœur) -----------------------

def test_la_cle_d_exercice_a_le_meme_frein(client, monkeypatch):
    """`/exercice/*` a sa propre clé (`X-Cle-Exercice`) : sans frein, elle restait la seule porte à essais illimités.
    Même compteur par adresse que la clé d'API : 10 mauvaises clés, quelle que soit la porte, puis 429."""
    monkeypatch.setenv("RITA_CLE_EXERCICE", "cle-d-exercice-de-test-32-caracteres")
    demande = {"nom": "Era", "motif": "essai du frein"}
    codes = [client.post("/exercice/panne", json=demande,
                         headers={"X-Cle-Exercice": f"mauvaise-cle-exercice-{i:02d}-xxxxxx"}).status_code
             for i in range(10)]
    assert codes == [403] * 10
    reponse = client.post("/exercice/panne", json=demande, headers={"X-Cle-Exercice": "mauvaise-cle-exercice-11-xxxxxx"})
    assert reponse.status_code == 429 and reponse.json()["detail"]["motif"] == "TROP_D_ESSAIS"
    # Le compteur est commun : l'adresse est aussi bloquée sur les routes de données.
    assert client.get(ROUTE, headers={"X-API-Key": CLE_DE_TEST}).status_code == 429


def test_une_cle_d_exercice_absente_ne_compte_pas(client, monkeypatch):
    monkeypatch.setenv("RITA_CLE_EXERCICE", "cle-d-exercice-de-test-32-caracteres")
    demande = {"nom": "Era", "motif": "essai du frein"}
    assert [client.post("/exercice/panne", json=demande).status_code for _ in range(12)] == [403] * 12

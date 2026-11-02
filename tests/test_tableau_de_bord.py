"""Sprint 5, étape 5 : le tableau de bord, lu comme du texte (plan du sprint 5, § 3, étape 5 ; grille, critère 2).

Les mêmes règles que les autres écrans (`tests/test_frontend.py`) : la clé saisie par l'utilisateur et gardée en
`sessionStorage`, jamais écrite dans le code ; un rendu par `textContent`, jamais par `innerHTML` (OWASP A03) ; les
marqueurs d'accessibilité. Propre à cet écran : seul le résumé est annoncé (`aria-live`), pas les sept cartes à chaque
actualisation ; un appel ne reste jamais pendu (délai de 5 secondes) ; la carte du service garde la même consigne que
`monitorage/seuils.json`. Le comportement dans un vrai navigateur est dans `tests/test_smoke_tableau_de_bord.py`.
"""
import json
import re

import pytest
from fastapi.testclient import TestClient

from api.main import app
from monitorage import seuils
from tests.test_frontend import FRONTEND, code_sans_commentaires

PAGE = "tableau-de-bord.html"
SCRIPT = "tableau-de-bord.js"


@pytest.fixture
def client():
    return TestClient(app)


def test_la_page_et_son_script_sont_servis(client):
    reponse = client.get(f"/{PAGE}")
    assert reponse.status_code == 200 and "text/html" in reponse.headers["content-type"]
    assert "<title>RITA : tableau de bord</title>" in reponse.text
    assert client.get(f"/{SCRIPT}").status_code == 200


def test_la_cle_est_saisie_jamais_ecrite_ni_gardee_durablement():
    code = code_sans_commentaires(SCRIPT)
    assert "sessionStorage" in code and "localStorage" not in code
    assert "dev-key" not in code and "X-API-Key" in code


def test_le_rendu_n_utilise_jamais_innerhtml():
    code = code_sans_commentaires(SCRIPT)
    assert "innerHTML" not in code and "textContent" in code


def test_seul_le_resume_est_annonce_aux_lecteurs_d_ecran():
    html = (FRONTEND / PAGE).read_text(encoding="utf-8")
    assert html.count('aria-live="polite"') == 1
    assert re.search(r'<p id="resume"[^>]*aria-live="polite"', html)


@pytest.mark.parametrize("marqueur, regle", [
    ('lang="fr"', "RGAA 8.3 : langue de la page"),
    ('<label for="cle">', "RGAA 11.1 : le champ de la clé a son étiquette"),
    ('<nav aria-label=', "RGAA 12.6 : la navigation est une zone nommée"),
    ('<span aria-current="page">Tableau de bord</span>', "la page courante est marquée"),
    ('id="actualiser"', "le bouton Actualiser existe"),
])
def test_les_marqueurs_d_accessibilite(marqueur, regle):
    assert marqueur in (FRONTEND / PAGE).read_text(encoding="utf-8"), regle


@pytest.mark.parametrize("page", ["index.html", "indicateurs.html", "briefing.html", "question.html"])
def test_chaque_ecran_mene_au_tableau_de_bord(page):
    assert f'href="{PAGE}"' in (FRONTEND / page).read_text(encoding="utf-8")


def test_l_etat_est_ecrit_en_mots_pas_seulement_en_couleur():
    code = code_sans_commentaires(SCRIPT)
    for mot in ("SAIN", "ATTENTION", "PROBLÈME", "INCONNU"):
        assert f'"{mot}"' in code, mot


def test_un_appel_ne_reste_jamais_pendu():
    code = code_sans_commentaires(SCRIPT)
    assert "AbortController" in code and "5000" in code


def test_les_trois_heures_sont_distinguees():
    code = code_sans_commentaires(SCRIPT)
    for libelle in ("Tableau actualisé à", "Mesures calculées à", "Coût cumulé depuis"):
        assert libelle in code, libelle


def test_la_carte_du_service_garde_la_consigne_des_seuils():
    # La carte du service doit rester lisible quand /sante ne répond plus : sa consigne est donc dans le script, et ce
    # test vérifie qu'elle reste celle de monitorage/seuils.json (une seule source de vérité).
    consigne = seuils.charger()["signaux"]["service"]["que_faire"]
    assert json.dumps(consigne, ensure_ascii=False) in (FRONTEND / SCRIPT).read_text(encoding="utf-8")


def test_la_page_a_un_bandeau_pour_l_exercice_de_panne():
    # Étape 6 : pendant une panne simulée, le tableau le dit, pour qu'on ne la prenne pas pour une vraie panne.
    html = (FRONTEND / PAGE).read_text(encoding="utf-8")
    assert '<p id="bandeau-exercice"' in html and "hidden" in html.split('id="bandeau-exercice"')[1].split(">")[0]


# --- 02/11/2026 : spécification de l'écran 5 (`evidence/C14/preuve-specifications-ecrans-4-et-5.md`), deux écarts ----

def test_un_bouton_permet_de_suspendre_l_actualisation_automatique():
    """Critère T17, WCAG 2.2.2 : un contenu qui se met à jour seul doit pouvoir être suspendu. Bouton à bascule : son
    nom reste le même, son état passe par `aria-pressed` ; un texte visible dit si l'actualisation tourne."""
    html = (FRONTEND / PAGE).read_text(encoding="utf-8")
    assert re.search(r'<button id="suspendre" type="button" aria-pressed="false">\s*'
                     r"Suspendre l'actualisation automatique\s*</button>", html)
    assert 'id="etat-actualisation"' in html


def test_le_pied_de_page_ne_dit_plus_prototype_local():
    """L'écran est en production depuis le 23/10 : « Prototype local du sprint 5 » était faux (rapport E4, § 1.7)."""
    pied = (FRONTEND / PAGE).read_text(encoding="utf-8").split("<footer>")[1].split("</footer>")[0]
    assert "Prototype" not in pied
    assert "jamais présenté comme sain" in pied

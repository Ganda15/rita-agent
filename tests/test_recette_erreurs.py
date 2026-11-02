"""Recette des cinq écrans : les situations d'erreur que seule la lecture du code vérifiait (C17.3, écart E3, 02/11/2026).

La recette du 02/11 (`evidence/C17/recette-2026-11-02/README.md`) a relevé ces cas, vérifiés jusque-là par lecture
seulement : la panne et la clé refusée sur Portefeuille et sur Indicateurs, la panne du lot 3 des indicateurs, l'encart
d'erreur de Question. Ces tests les jouent dans un vrai navigateur. Les réponses de l'API sont fabriquées sur les formes
réelles : c'est un **test simulé**, pas une preuve de production. Chaque route ajoutée ici passe avant celles de la
fixture `onglet`, qui répond 200 partout : Playwright essaie les routes de la dernière enregistrée à la première.
"""
import json

import pytest

from tests.test_recette_clavier import CLE, onglet  # noqa: F401, onglet est une fixture
from tests.test_smoke_ui import page, serveur  # noqa: F401, ce sont des fixtures

# Écran : (fichier, route de l'appel principal de l'écran)
ECRANS = {
    "portefeuille": ("index.html", "**/donnees/portefeuille*"),
    "indicateurs": ("indicateurs.html", "**/donnees/indicateurs"),
}


def _ouvrir_avec_cle(onglet, serveur, fichier):  # noqa: F811
    """Ouvre l'écran avec une clé déjà gardée dans l'onglet : l'appel part dès le chargement."""
    onglet.goto(f"{serveur}/{fichier}")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE}')")
    onglet.goto(f"{serveur}/{fichier}", wait_until="networkidle")


def _attendre_statut(onglet, texte):
    onglet.wait_for_function(f"document.getElementById('statut').textContent.includes({json.dumps(texte)})",
                             timeout=5_000)


def _cle_gardee(onglet):
    return onglet.evaluate("sessionStorage.getItem('rita_api_key')")


@pytest.mark.parametrize("ecran", ECRANS)
def test_une_reponse_en_erreur_est_dite_et_rien_ne_s_affiche(onglet, serveur, ecran):  # noqa: F811
    fichier, route = ECRANS[ecran]
    onglet.route(route, lambda r: r.fulfill(status=500, content_type="application/json", body='{"detail": "panne"}'))
    _ouvrir_avec_cle(onglet, serveur, fichier)
    _attendre_statut(onglet, "Erreur 500")
    assert onglet.locator("#resultat").is_hidden()


@pytest.mark.parametrize("ecran", ECRANS)
def test_un_serveur_qui_ne_repond_pas_est_dit(onglet, serveur, ecran):  # noqa: F811
    fichier, route = ECRANS[ecran]
    onglet.route(route, lambda r: r.abort())
    _ouvrir_avec_cle(onglet, serveur, fichier)
    _attendre_statut(onglet, "Le serveur ne répond pas")
    assert onglet.locator("#resultat").is_hidden()


@pytest.mark.parametrize("ecran", ECRANS)
def test_une_cle_refusee_est_oubliee_et_redemandee(onglet, serveur, ecran):  # noqa: F811
    fichier, route = ECRANS[ecran]
    onglet.route(route, lambda r: r.fulfill(status=403, content_type="application/json",
                                            body='{"detail": "Clé API invalide ou absente"}'))
    _ouvrir_avec_cle(onglet, serveur, fichier)
    _attendre_statut(onglet, "Clé d'API refusée")
    assert onglet.locator("#connexion").is_visible()
    assert _cle_gardee(onglet) is None, "une clé refusée doit être oubliée"


def test_une_panne_du_lot_3_laisse_le_lot_1_lisible(onglet, serveur):  # noqa: F811
    # Une passerelle en panne répond souvent une page HTML, pas du JSON : l'écran ne doit pas tenter de la lire.
    onglet.route("**/donnees/indicateurs-risque*",
                 lambda r: r.fulfill(status=502, content_type="text/html", body="<html>Bad Gateway</html>"))
    _ouvrir_avec_cle(onglet, serveur, "indicateurs.html")
    onglet.wait_for_selector("#lignes tr", timeout=5_000)
    cellules = onglet.locator("#lignes tr").first.locator("th, td").all_inner_texts()
    assert cellules[0] == "MC.PA"
    assert cellules[-3:] == ["—", "—", "—"], "volatilité, pire baisse et RSI : un tiret quand le lot 3 manque"
    assert onglet.locator("#statut").inner_text() == ""


def test_une_panne_s_affiche_dans_l_encart_d_erreur_et_pas_comme_un_refus(onglet, serveur):  # noqa: F811
    # Forme réelle de la réponse 503 de `POST /question` (`api/question.py`).
    corps = {"statut": "erreur", "motif": "FOURNISSEUR_INDISPONIBLE",
             "texte": "Le service n'a pas pu répondre pour le moment. Réessayez plus tard."}
    onglet.route("**/question", lambda r: r.fulfill(status=503, content_type="application/json",
                                                    body=json.dumps(corps)))
    _ouvrir_avec_cle(onglet, serveur, "question.html")
    onglet.fill("#question", "Combien de postes Netflix va-t-il supprimer ?")
    onglet.click("#form-question button[type=submit]")   # Entrée dans la zone de texte va à la ligne, n'envoie pas
    onglet.wait_for_selector("#erreur", state="visible", timeout=5_000)
    assert onglet.locator("#refus").is_hidden()
    assert "Réessayez plus tard" in onglet.locator("#texte-erreur").inner_text()
    assert "Code HTTP 503" in onglet.locator("#motif-erreur").inner_text()

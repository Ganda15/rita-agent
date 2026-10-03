"""Smoke test du front dans un vrai navigateur — C17 (le « l'API marche mais l'écran est cassé »).

`tests/test_frontend.py` lit le HTML et le JS comme du texte. Ici, un navigateur charge la page
servie par l'API, exécute le JavaScript, et on vérifie ce qu'un utilisateur verrait : le titre,
le formulaire de clé, l'écran sans erreur JavaScript. Un seul parcours, le plus court.
Item 7 du harnais (rapport Agentic SD, 19/09/2026). Chrome installé en local (canal `chrome`,
aucun téléchargement de navigateur) ; Chromium de Playwright en CI.
"""
import os
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright


def port_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def serveur():
    port = port_libre()
    env = dict(os.environ, RITA_API_KEY="cle-de-test-smoke-ui-32-caracteres-x")
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--port", str(port), "--log-level", "warning"],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            urllib.request.urlopen(url + "/health", timeout=1)
            break
        except Exception:
            time.sleep(0.2)
    else:
        proc.kill()
        pytest.fail("l'API n'a pas démarré en 10 s")
    yield url
    proc.kill()


@pytest.fixture(scope="module")
def page(serveur):
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        navigateur = p.chromium.launch(headless=True, **canal)
        pg = navigateur.new_page()
        erreurs = []
        pg.on("pageerror", lambda e: erreurs.append(str(e)))
        pg.goto(serveur + "/", wait_until="networkidle")
        pg.erreurs_js = erreurs
        yield pg
        navigateur.close()


def test_la_page_d_accueil_se_charge_avec_son_titre(page):
    assert page.title() == "RITA — Mon portefeuille"


def test_le_formulaire_de_cle_est_visible_et_vide(page):
    assert page.locator("#form-cle").is_visible()
    assert page.locator("#cle").input_value() == ""  # jamais de clé pré-remplie (OWASP)


def test_aucune_erreur_javascript_au_chargement(page):
    assert page.erreurs_js == []


def test_une_mauvaise_cle_est_refusee_a_l_ecran(page):
    page.fill("#cle", "mauvaise-cle")
    page.click("#form-cle button[type=submit], #form-cle button")
    page.wait_for_timeout(1500)
    statut = page.locator("#statut").inner_text().lower()
    assert statut, "le statut doit dire quelque chose après une clé refusée"
    assert "401" in statut or "refus" in statut or "invalide" in statut or "erreur" in statut


def test_une_position_sans_taux_affiche_indisponible_a_l_ecran(page):
    """Plan 65 (cas D06) dans un vrai navigateur : l'API est remplacée par des réponses figées
    (interception des trois appels), parce que la base réelle n'a aucune position sans taux.
    Une valorisation nulle doit s'afficher « indisponible », jamais « 0,00 € »."""
    import json

    def repondre(route, corps):
        route.fulfill(status=200, content_type="application/json", body=json.dumps(corps))

    portefeuille = {"nb": 2, "total_eur": None, "positions_sans_taux": 1, "positions": [
        {"ticker": "MC.PA", "nom_officiel": "LVMH", "statut_qualite": "OK", "quantite": 12, "pru": 632.4,
         "devise": "EUR", "cours": 466.8, "investi_eur": 7588.8, "valorisation_eur": 5601.6,
         "performance_pct": -26.19, "taux_manquant": False},
        {"ticker": "AAPL", "nom_officiel": "Apple", "statut_qualite": "OK", "quantite": 6, "pru": 178.45,
         "devise": "USD", "cours": 212.5, "investi_eur": None, "valorisation_eur": None,
         "performance_pct": 19.08, "taux_manquant": True}]}
    indicateurs = {"nb": 2, "total_eur": None, "complet": False, "exposition": [], "lignes": [
        {"ticker": "MC.PA", "nom_officiel": "LVMH", "devise": "EUR", "quantite": 12,
         "valorisation_eur": 5601.6, "poids_pct": None},
        {"ticker": "AAPL", "nom_officiel": "Apple", "devise": "USD", "quantite": 6,
         "valorisation_eur": None, "poids_pct": None}]}
    fraicheur = {"statut": "vert", "message": "Donnees du 02/10/2026", "retard_jours_ouvres": 0}
    page.route("**/donnees/portefeuille*", lambda route: repondre(route, portefeuille))
    page.route("**/donnees/indicateurs-portefeuille*", lambda route: repondre(route, indicateurs))
    page.route("**/donnees/fraicheur*", lambda route: repondre(route, fraicheur))

    page.fill("#cle", "cle-de-test-smoke-ui-32-caracteres-x")
    page.click("#form-cle button[type=submit], #form-cle button")
    page.wait_for_selector("#lignes tr", timeout=5000)

    total = page.locator("#total").inner_text().lower()
    assert "indisponible" in total and "1 position" in total, total
    ligne_aapl = page.locator("#lignes tr", has_text="AAPL").inner_text().lower()
    assert ligne_aapl.count("indisponible") == 2, ligne_aapl
    assert "0,00" not in ligne_aapl
    assert page.erreurs_js == []

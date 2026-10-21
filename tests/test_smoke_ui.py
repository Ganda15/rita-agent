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


def test_l_ecran_briefing_affiche_le_texte_et_le_verdict(page, serveur):
    """Écran 3 dans un vrai navigateur, `/briefing` intercepté : aucun appel payant au modèle.
    Ce qu'un utilisateur voit : le texte en paragraphes, le cours, le verdict du garde-fou en mots."""
    import json

    corps = {"ticker": "MC.PA", "price": 378.55, "change_pct": -0.25, "currency": "EUR",
             "briefing": "LVMH clôture à 378,55 EUR, en légère baisse de 0,25 %.\n\nAucune actualité récente.",
             "conforme_amf": True, "motifs_amf": []}
    page.route("**/briefing?ticker=*", lambda route: route.fulfill(
        status=200, content_type="application/json", headers={"X-Request-ID": "abcdef1234567890"},
        body=json.dumps(corps)))
    page.goto(serveur + "/briefing.html", wait_until="networkidle")
    page.evaluate("sessionStorage.setItem('rita_api_key', 'cle-de-test-smoke-ui-32-caracteres-x')")
    page.goto(serveur + "/briefing.html", wait_until="networkidle")

    page.fill("#ticker", "MC.PA")
    page.click("#form-briefing button[type=submit], #form-briefing button")
    page.wait_for_selector("#texte p", timeout=5000)

    texte = page.locator("#texte").inner_text()
    assert "378,55" in texte and page.locator("#texte p").count() == 2
    verdict = page.locator("#verdict").inner_text().lower()
    assert "conforme" in verdict and "retenu" not in verdict
    assert "abcdef1234567890" in page.locator("#reference").inner_text()
    assert page.erreurs_js == []


def test_l_ecran_briefing_dit_quand_le_ticker_est_introuvable(page, serveur):
    page.route("**/briefing?ticker=*", lambda route: route.fulfill(
        status=502, content_type="application/json", body='{"detail": "ticker absent de la base : XXX"}'))
    page.goto(serveur + "/briefing.html", wait_until="networkidle")
    page.evaluate("sessionStorage.setItem('rita_api_key', 'cle-de-test-smoke-ui-32-caracteres-x')")
    page.goto(serveur + "/briefing.html", wait_until="networkidle")
    page.fill("#ticker", "XXX")
    page.click("#form-briefing button[type=submit], #form-briefing button")
    page.wait_for_timeout(1500)
    statut = page.locator("#statut").inner_text().lower()
    assert "introuvable" in statut, statut
    assert page.erreurs_js == []


# --- Revue Codex de la PR #112 (20/10/2026) : l'écran comprend les réponses ajoutées au sprint 4 ------------------------

def _statut_du_briefing(page, serveur, ticker, statut_http, corps, entetes=None):
    """Sert la réponse donnée à la place de `/briefing`, saisit le code et rend le message affiché."""
    import json

    page.route("**/briefing?ticker=*", lambda route: route.fulfill(
        status=statut_http, content_type="application/json", headers=entetes or {}, body=json.dumps(corps)))
    page.goto(serveur + "/briefing.html", wait_until="networkidle")
    page.evaluate("sessionStorage.setItem('rita_api_key', 'cle-de-test-smoke-ui-32-caracteres-x')")
    page.goto(serveur + "/briefing.html", wait_until="networkidle")
    page.fill("#ticker", ticker)
    page.click("#form-briefing button[type=submit], #form-briefing button")
    page.wait_for_timeout(1500)
    return page.locator("#statut").inner_text().lower()


def test_l_ecran_briefing_dit_quand_la_valeur_est_inconnue(page, serveur):
    # Depuis la tâche C1, une valeur absente du référentiel donne un 422, plus un 502.
    statut = _statut_du_briefing(page, serveur, "XXX", 422,
                                 {"detail": "Valeur inconnue : aucun briefing n'est possible pour ce code."})
    assert "introuvable" in statut, statut
    assert page.erreurs_js == []


def test_l_ecran_briefing_affiche_le_refus_de_debit(page, serveur):
    # Tâche C3 : au-delà du quota, 429 et un refus poli, rangé sous `detail` par FastAPI.
    refus = {"statut": "refus", "motif": "LIMITE_DE_DEBIT",
             "texte": "Trop de demandes en peu de temps. Réessayez dans une minute."}
    statut = _statut_du_briefing(page, serveur, "MC.PA", 429, {"detail": refus}, {"Retry-After": "42"})
    assert "trop de demandes" in statut, statut
    assert page.erreurs_js == []


def _ecran_question(page, serveur, statut_http, corps, entetes=None):
    """Sert la réponse donnée à la place de `/question`, pose une question et rend ce que montrent les encarts."""
    import json

    page.route("**/question", lambda route: route.fulfill(
        status=statut_http, content_type="application/json", headers=entetes or {}, body=json.dumps(corps)))
    page.goto(serveur + "/question.html", wait_until="networkidle")
    page.evaluate("sessionStorage.setItem('rita_api_key', 'cle-de-test-smoke-ui-32-caracteres-x')")
    page.goto(serveur + "/question.html", wait_until="networkidle")
    page.fill("#question", "Combien de postes Netflix va-t-il supprimer ?")
    page.click("#form-question button[type=submit], #form-question button")
    page.wait_for_timeout(1500)
    return {"refus_visible": page.locator("#refus").is_visible(),
            "erreur_visible": page.locator("#erreur").is_visible(),
            "texte_refus": page.locator("#texte-refus").inner_text(),
            "motif_refus": page.locator("#motif-refus").inner_text().lower()}


def test_l_ecran_question_affiche_le_refus_de_debit(page, serveur):
    # Tâche C3 : une limite de débit est un refus poli, pas une panne ; FastAPI range le refus sous `detail`.
    refus = {"statut": "refus", "motif": "LIMITE_DE_DEBIT",
             "texte": "Trop de demandes en peu de temps. Réessayez dans une minute."}
    ecran = _ecran_question(page, serveur, 429, {"detail": refus}, {"Retry-After": "42"})
    assert ecran["refus_visible"] and not ecran["erreur_visible"], ecran
    assert "Trop de demandes" in ecran["texte_refus"], ecran
    assert "trop de demandes en une minute" in ecran["motif_refus"], ecran
    assert page.erreurs_js == []


@pytest.mark.parametrize("motif, mots", [
    ("TENTATIVE_DETOURNEMENT", "détourner le service"),
    ("FUITE_BLOQUEE", "informations internes"),
    ("NOMBRE_NON_SOURCE", "chiffre absent"),
])
def test_l_ecran_question_dit_le_motif_en_mots(page, serveur, motif, mots):
    # Les motifs du sprint 4 se lisent en mots, comme ceux du sprint 3, et non comme un code brut.
    ecran = _ecran_question(page, serveur, 200,
                            {"statut": "refus", "motif": motif, "texte": "Je ne peux pas traiter cette demande."})
    assert ecran["refus_visible"], ecran
    assert mots in ecran["motif_refus"], ecran
    assert page.erreurs_js == []

"""Refonte 001, tâche 5 (exigences R5 et R7) : `commun.js`, ce que les cinq écrans partagent, et le mode simulation.

`window.RITA` porte la clé (gardée seulement après une réponse réussie, oubliée sur 401 ou 403 : correctif #73) et le
mode simulation (choix explicite par le bouton « Mode simulation » de l'en-tête, le réel par défaut). En simulation,
aucun écran n'appelle RITA : un écran sans données d'exemple se suspend (décision D1) et `commun.js` bloque en plus tout
appel vers une route de RITA. Changer de mode recharge la page : les résultats affichés disparaissent dans les deux sens.
"""
import os
import re
from urllib.parse import urlparse
from pathlib import Path

import pytest

from tests.test_frontend import code_sans_commentaires
from tests.test_smoke_ui import serveur  # noqa: F401  (fixture : l'API servie en local)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
ECRANS = {"index.html": "app.js", "indicateurs.html": "indicateurs.js", "briefing.html": "briefing.js",
          "question.html": "question.js", "tableau-de-bord.html": "tableau-de-bord.js"}
CLE_SERVEUR = "cle-de-test-smoke-ui-32-caracteres-x"   # tests/test_smoke_ui.py, fixture `serveur`
MENTION = "Simulation : données d'exemple, aucun modèle appelé"
ROUTES_RITA = ("/briefing", "/question", "/donnees", "/sante", "/health", "/audit", "/exercice")
REPONSE = {"statut": "reponse", "texte": "Netflix supprime 2 000 postes [1].", "index": {"empreinte": "abc"},
           "references": [{"n": 1, "titre": "Netflix réduit ses effectifs", "source": "Les Échos", "table": "article",
                           "id": 42, "date": "2026-10-28", "lien": "https://www.lesechos.fr/"}]}   # test_recette_clavier.py


# --- le fichier et les pages, sans navigateur -----------------------------------------------------------------------------

@pytest.mark.parametrize("fichier, script", ECRANS.items())
def test_chaque_page_charge_commun_js_avant_son_script(fichier, script):
    page = (FRONTEND / fichier).read_text(encoding="utf-8")
    assert '<script src="commun.js"></script>' in page, fichier
    assert page.index('<script src="commun.js"></script>') < page.index(f'<script src="{script}"></script>'), fichier


@pytest.mark.parametrize("fichier", ECRANS)
def test_bouton_simulation_dans_l_en_tete(fichier):
    entete = re.search(r"<header\b.*?</header>", (FRONTEND / fichier).read_text(encoding="utf-8"), re.S).group(0)
    bouton = re.search(r'<button\b[^>]*\bid="bascule-simulation"[^>]*>([^<]*)</button>', entete)
    assert bouton, fichier
    assert 'type="button"' in bouton.group(0) and " hidden" in bouton.group(0) and 'aria-pressed="false"' in bouton.group(0)
    assert bouton.group(1) == "Mode simulation"


def test_commun_js_sans_localstorage_ni_html_insere():
    code = code_sans_commentaires("commun.js")
    assert "sessionStorage" in code and "localStorage" not in code
    for interdit in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write"):
        assert interdit not in code, interdit


# --- dans un vrai navigateur ------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


@pytest.fixture
def onglet(navigateur):
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.erreurs_js = []
    page.on("pageerror", lambda e: page.erreurs_js.append(str(e)))
    yield page
    contexte.close()


def appels_rita(adresses, routes=ROUTES_RITA):
    """Les adresses qui sont des routes de RITA : le chemin exact, ou suivi de « / ». Une page (`question.html`) ou un
    script (`question.js`) n'en est pas une, même si son nom commence pareil."""
    return [a for a in adresses
            if any(urlparse(a).path == r or urlparse(a).path.startswith(r + "/") for r in routes)]


def test_le_filtre_des_appels_ne_confond_pas_page_et_route():
    adresses = ["http://h/question.html", "http://h/question.js", "http://h/question", "http://h/donnees/articles/42",
                "http://h/sante", "http://h/style.css"]
    assert appels_rita(adresses) == ["http://h/question", "http://h/donnees/articles/42", "http://h/sante"]


def _cle(page):
    return page.evaluate("sessionStorage.getItem('rita_api_key')")


def test_cle_gardee_seulement_apres_succes(onglet, serveur):  # noqa: F811
    onglet.route("**/donnees/fraicheur", lambda r: r.fulfill(status=500, body="{}"))
    onglet.goto(serveur + "/question.html")
    onglet.evaluate("sessionStorage.removeItem('rita_api_key')")
    statut = onglet.evaluate("RITA.appeler('/donnees/fraicheur', {cle: 'cle-en-essai-0123456789'}).then(r => r.status)")
    assert statut == 500 and _cle(onglet) is None, "une réponse en échec ne garde pas la clé"
    onglet.unroute("**/donnees/fraicheur")
    onglet.route("**/donnees/fraicheur", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    onglet.evaluate("RITA.appeler('/donnees/fraicheur', {cle: 'cle-en-essai-0123456789'})")
    assert _cle(onglet) == "cle-en-essai-0123456789", "la clé est gardée après une réponse réussie"


@pytest.mark.parametrize("code", [401, 403])
def test_cle_oubliee_sur_403(onglet, serveur, code):  # noqa: F811
    onglet.route("**/donnees/fraicheur", lambda r: r.fulfill(status=code, body="{}"))
    onglet.goto(serveur + "/question.html")
    onglet.evaluate("sessionStorage.setItem('rita_api_key', 'cle-perimee-0123456789')")
    onglet.evaluate("RITA.appeler('/donnees/fraicheur')")
    assert _cle(onglet) is None


def test_mode_reel_par_defaut(onglet, serveur):  # noqa: F811
    onglet.goto(serveur + "/index.html")
    assert onglet.evaluate("RITA.estSimulation()") is False
    assert onglet.locator("#mention-simulation").count() == 0
    bouton = onglet.locator("#bascule-simulation")
    assert bouton.is_visible() and bouton.get_attribute("aria-pressed") == "false"


@pytest.mark.parametrize("fichier", ECRANS)
def test_mention_simulation_visible_sur_chaque_ecran(onglet, serveur, fichier):  # noqa: F811
    onglet.goto(serveur + "/" + fichier)
    onglet.evaluate("sessionStorage.setItem('rita_simulation', 'oui')")
    onglet.goto(serveur + "/" + fichier)
    mention = onglet.locator("#mention-simulation")
    assert mention.is_visible() and mention.inner_text() == MENTION
    assert onglet.locator("#bascule-simulation").get_attribute("aria-pressed") == "true"
    assert onglet.erreurs_js == []


def test_le_bouton_de_l_en_tete_active_la_simulation(onglet, serveur):  # noqa: F811
    onglet.goto(serveur + "/index.html")
    onglet.locator("#bascule-simulation").click()
    onglet.wait_for_selector("#mention-simulation")
    assert onglet.evaluate("RITA.estSimulation()") is True


def test_simulation_bloque_les_routes_de_rita(onglet, serveur):  # noqa: F811
    """Deuxième barrière : même un appel oublié par un écran ne part pas vers RITA sous la mention « Simulation »."""
    onglet.goto(serveur + "/index.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_SERVEUR}'); sessionStorage.setItem('rita_simulation', 'oui')")
    vues = []
    onglet.on("request", lambda r: vues.append(r.url))
    onglet.goto(serveur + "/index.html")
    for route in ("/donnees/valeurs?limite=5", "/briefing?ticker=MC.PA", "/question", "/sante", "/health"):
        refus = onglet.evaluate(f"fetch('{route}').then(() => 'parti', e => e.message)")
        assert refus.startswith("Simulation"), (route, refus)
    assert appels_rita(vues) == [], vues


def test_question_et_tableau_suspendus_en_simulation(onglet, serveur):  # noqa: F811
    onglet.clock.install()
    onglet.goto(serveur + "/question.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_SERVEUR}'); sessionStorage.setItem('rita_simulation', 'oui')")
    vues = []
    onglet.on("request", lambda r: vues.append(r.url))
    for fichier, cache in (("question.html", "#form-question"), ("tableau-de-bord.html", "#tableau")):
        onglet.goto(serveur + "/" + fichier)
        assert onglet.locator("#suspension").is_visible(), fichier
        assert "Simulation non disponible pour cet écran" in onglet.locator("#suspension").inner_text()
        assert onglet.locator("#quitter-simulation").is_visible()
        assert not onglet.locator(cache).is_visible(), f"{fichier} : rien de réel sous la mention"
        # Envoi au clavier ou par programme : bloqué, aucune navigation.
        adresse = onglet.url
        onglet.evaluate("document.querySelectorAll('form').forEach(f => f.requestSubmit())")
        onglet.clock.run_for(61_000)   # deux périodes d'actualisation du tableau de bord
        assert onglet.url == adresse
    assert appels_rita(vues, ("/question", "/sante", "/health", "/donnees")) == [], vues
    assert onglet.erreurs_js == []


def test_quitter_la_simulation_rend_le_mode_reel(onglet, serveur):  # noqa: F811
    onglet.goto(serveur + "/question.html")
    onglet.evaluate("sessionStorage.setItem('rita_simulation', 'oui')")
    onglet.goto(serveur + "/question.html")
    onglet.locator("#quitter-simulation").click()
    onglet.wait_for_selector("#suspension", state="detached")
    assert onglet.evaluate("RITA.estSimulation()") is False
    assert onglet.locator("#mention-simulation").count() == 0
    assert onglet.locator("#connexion").is_visible() or onglet.locator("#demande").is_visible()


def test_bascule_efface_les_resultats(onglet, serveur):  # noqa: F811
    """Dans les deux sens : un résultat réel disparaît en passant en simulation, et rien ne réapparaît en revenant."""
    import json
    onglet.route("**/question", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(REPONSE)))
    onglet.goto(serveur + "/question.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_SERVEUR}')")
    onglet.goto(serveur + "/question.html")
    onglet.fill("#question", "Que fait Netflix ?")
    onglet.locator("#form-question button[type=submit]").click()
    onglet.wait_for_selector("#resultat:not([hidden])")
    assert "Netflix supprime" in onglet.locator("#resultat").inner_text()
    onglet.locator("#bascule-simulation").click()              # réel vers simulation
    onglet.wait_for_selector("#suspension")
    assert not onglet.locator("#resultat").is_visible()
    onglet.locator("#quitter-simulation").click()              # simulation vers réel
    onglet.wait_for_selector("#suspension", state="detached")
    assert not onglet.locator("#resultat").is_visible(), "l'ancien résultat ne revient pas"


def test_navigation_des_cinq_pages_avec_une_cle_gardee(onglet, serveur):  # noqa: F811
    onglet.goto(serveur + "/index.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_SERVEUR}')")
    for fichier in ECRANS:
        onglet.goto(serveur + "/" + fichier)
        assert onglet.evaluate("typeof window.RITA") == "object", fichier
        assert onglet.evaluate("RITA.lireCle()") == CLE_SERVEUR, f"{fichier} : la clé est perdue"
    assert onglet.erreurs_js == []

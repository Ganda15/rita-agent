"""Refonte 001, tâche 4 : le thème dans un vrai navigateur (décision d'Era du 04/11 : sombre par défaut, clair au choix).

À l'ouverture, le site est sombre et le bouton du thème est visible. Le bouton passe au clair, à la souris comme au
clavier ; le choix tient d'un écran à l'autre pendant la session ; une nouvelle session repart en sombre. Les couleurs de
fond lues ici sont celles calculées par le navigateur, pas celles du fichier.
"""
import os

import pytest

from tests.test_smoke_ui import serveur  # noqa: F401  (fixture : l'API servie en local)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

ECRANS = ["index.html", "indicateurs.html", "briefing.html", "question.html", "tableau-de-bord.html"]
FOND_SOMBRE = "rgb(11, 42, 77)"     # #0b2a4d, couleur de secours sous le dégradé
FOND_CLAIR = "rgb(240, 244, 249)"   # #f0f4f9


@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


def _theme(page):
    return page.evaluate("document.documentElement.getAttribute('data-theme')")


def _fond(page):
    """La couleur de fond de la page (sous le dégradé), et la preuve que le dégradé est bien peint."""
    couleur, image = page.evaluate("[getComputedStyle(document.documentElement).backgroundColor,"
                                   " getComputedStyle(document.documentElement).backgroundImage]")
    assert "linear-gradient" in image, image
    return couleur


def _logo(page):
    return page.evaluate("getComputedStyle(document.querySelector('.logo')).backgroundImage")


def test_sombre_a_l_ouverture_et_bouton_visible(navigateur, serveur):  # noqa: F811
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.goto(serveur + "/index.html")
    assert _theme(page) is None and _fond(page) == FOND_SOMBRE
    assert "logo-rita-sombre.png" in _logo(page)
    assert page.evaluate("getComputedStyle(document.body).backgroundColor") == "rgba(0, 0, 0, 0)", \
        "le corps est transparent : le dégradé se voit sur toute la page"
    bouton = page.locator("#bascule-theme")
    assert bouton.is_visible() and bouton.get_attribute("aria-pressed") == "false"
    contexte.close()


def test_bascule_du_theme_suit_la_navigation(navigateur, serveur):  # noqa: F811
    contexte = navigateur.new_context()
    page = contexte.new_page()
    erreurs = []
    page.on("pageerror", lambda e: erreurs.append(str(e)))
    page.goto(serveur + "/index.html")
    page.locator("#bascule-theme").click()
    assert _theme(page) == "clair" and _fond(page) == FOND_CLAIR
    assert "logo-rita-clair.png" in _logo(page)
    assert page.locator("#bascule-theme").get_attribute("aria-pressed") == "true"
    for fichier in ECRANS[1:]:
        page.goto(serveur + "/" + fichier)
        assert _theme(page) == "clair", f"{fichier} : le choix du clair est perdu"
        assert _fond(page) == FOND_CLAIR, fichier
        assert page.locator("#bascule-theme").get_attribute("aria-pressed") == "true", fichier
    # Au clavier : le bouton se focalise et s'actionne avec Entrée, sans souris.
    page.locator("#bascule-theme").focus()
    page.keyboard.press("Enter")
    assert _theme(page) is None and _fond(page) == FOND_SOMBRE
    assert page.locator("#bascule-theme").get_attribute("aria-pressed") == "false"
    assert erreurs == []
    contexte.close()


def test_une_nouvelle_session_repart_en_sombre(navigateur, serveur):  # noqa: F811
    premier = navigateur.new_context()
    page = premier.new_page()
    page.goto(serveur + "/index.html")
    page.locator("#bascule-theme").click()
    assert _theme(page) == "clair"
    premier.close()
    second = navigateur.new_context()
    page = second.new_page()
    page.goto(serveur + "/index.html")
    assert _theme(page) is None and _fond(page) == FOND_SOMBRE
    second.close()


@pytest.mark.parametrize("largeur", [320, 280])
@pytest.mark.parametrize("fichier", ECRANS)
def test_aucun_defilement_horizontal_a_320_px(navigateur, serveur, fichier, largeur):  # noqa: F811
    """WCAG 1.4.10 (redistribution) : à 320 px de large, la page tient sans défilement horizontal. La carte du contenu
    (refonte 001) ajoute des marges ; elles ne doivent pas pousser le champ de la clé hors de l'écran. 280 px en plus :
    le panneau de navigateur de l'application, mesuré le 04/11 à 278 px, débordait de 17 px (champ de clé de 256 px)."""
    contexte = navigateur.new_context(viewport={"width": largeur, "height": 800})
    page = contexte.new_page()
    page.goto(serveur + "/" + fichier)
    largeurs = page.evaluate("[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
    contexte.close()
    assert largeurs[0] <= largeurs[1], f"{fichier} : page de {largeurs[0]} px pour un écran de {largeurs[1]} px"


def test_retour_arriere_depuis_le_cache_reapplique_le_theme(navigateur, serveur):  # noqa: F811
    """Bouton Précédent : Chrome peut rendre une page depuis son cache d'aller-retour (bfcache), telle qu'on l'a quittée,
    sans relancer theme.js. Si le clair a été choisi entre-temps sur une autre page, la page rendue doit le reprendre.
    On simule ici l'événement que le navigateur envoie dans ce cas (`pageshow` avec `persisted`)."""
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.goto(serveur + "/index.html")
    assert _theme(page) is None
    # Le clair a été choisi ailleurs pendant que cette page dormait dans le cache.
    page.evaluate("sessionStorage.setItem('rita_theme', 'clair')")
    page.evaluate("window.dispatchEvent(new PageTransitionEvent('pageshow', {persisted: true}))")
    assert _theme(page) == "clair"
    assert page.locator("#bascule-theme").get_attribute("aria-pressed") == "true"
    contexte.close()

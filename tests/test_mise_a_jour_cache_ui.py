"""Refonte 001 (R5, R6), 04/11/2026 : une mise à jour de l'interface quand le navigateur a déjà l'ancienne version en cache.

Le scénario de la demande de relecture : ouvrir l'ancienne version, livrer la nouvelle, recharger normalement (pas
Ctrl+F5), vérifier que c'est le nouveau script qui tourne. Un navigateur neuf ne prouverait rien : le défaut du 04/11
(page neuve, script ancien, chiffres décalés d'une colonne) n'arrive qu'avec un cache déjà rempli.

L'ancienne version est servie comme le faisait le serveur d'avant `Cache-Control: no-cache` : des fichiers anciens, avec
`Last-Modified` et sans consigne de cache, que Chrome garde plusieurs jours (péremption « heuristique »). La nouvelle est
servie par la vraie classe de l'API (`InterfaceToujoursRevalidee`). Aucune réponse n'est interceptée par `page.route` :
Playwright coupe le cache HTTP quand une route est posée, ce qui rendrait le test vide.
"""
import os
import re
import shutil
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from starlette.staticfiles import StaticFiles

from api.main import InterfaceToujoursRevalidee
from tests.test_smoke_ui import port_libre

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
PAGES = [("indicateurs.html", "indicateurs.js"), ("index.html", "app.js"), ("briefing.html", "briefing.js"),
         ("question.html", "question.js"), ("tableau-de-bord.html", "tableau-de-bord.js")]
VIEUX = 1767225600   # 01/01/2026 : un fichier ancien, donc une péremption heuristique longue côté navigateur
MARQUEUR = "window.ancienneVersion = true;\n"


def _sans_version(dossier: Path) -> None:
    for page in dossier.glob("*.html"):
        page.write_bytes(re.sub(rb'(\.(?:js|css))\?v=[0-9a-f]+', rb"\1", page.read_bytes()))


@pytest.fixture(scope="module")
def sites(tmp_path_factory):
    racine = tmp_path_factory.mktemp("sites")
    avant, sans_version = racine / "avant", racine / "apres-sans-version"
    for dossier in (avant, sans_version):
        shutil.copytree(FRONTEND, dossier)
        _sans_version(dossier)
    # L'ancienne version : chaque script d'écran remplacé par un marqueur, tous les fichiers vieillis.
    for _, script in PAGES:
        (avant / script).write_text(MARQUEUR, encoding="utf-8")
    for f in avant.iterdir():
        os.utime(f, (VIEUX, VIEUX))
    return {"avant": avant, "apres": FRONTEND, "apres-sans-version": sans_version}


class Bascule:
    """Un seul serveur, une seule adresse : on change de version comme un déploiement, sans changer d'origine."""

    def __init__(self, sites):
        self.phase = "avant"
        self.applications = {"avant": StaticFiles(directory=sites["avant"], html=True),   # l'ancien : aucun Cache-Control
                             "apres": InterfaceToujoursRevalidee(directory=sites["apres"], html=True),
                             "apres-sans-version": InterfaceToujoursRevalidee(directory=sites["apres-sans-version"], html=True)}

    async def __call__(self, scope, receive, send):
        await self.applications[self.phase](scope, receive, send)


@pytest.fixture(scope="module")
def serveur_bascule(sites):
    bascule, port = Bascule(sites), port_libre()
    serveur = uvicorn.Server(uvicorn.Config(bascule, host="127.0.0.1", port=port, log_level="warning", ws="none"))
    fil = threading.Thread(target=serveur.run, daemon=True)
    fil.start()
    for _ in range(100):
        if serveur.started:
            break
        time.sleep(0.05)
    else:
        pytest.fail("le serveur d'essai n'a pas démarré en 5 s")
    yield bascule, f"http://127.0.0.1:{port}"
    serveur.should_exit = True
    fil.join(timeout=5)


@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


def _livrer(bascule, version):
    bascule.phase = version


def _ouvrir_l_ancienne_version(navigateur, bascule, url, page_html):
    _livrer(bascule, "avant")
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.goto(f"{url}/{page_html}")
    assert page.evaluate("window.ancienneVersion") is True, "l'ancienne version doit tourner avant la mise à jour"
    return contexte, page


def test_le_cas_de_controle_sans_version_garde_l_ancien_script(navigateur, serveur_bascule):
    """Le défaut du 04/11, reproduit : même livraison, mais des adresses sans version. Si ce test échoue, le cache de
    ce navigateur n'est pas actif et les autres tests de ce fichier ne prouveraient rien."""
    bascule, url = serveur_bascule
    contexte, page = _ouvrir_l_ancienne_version(navigateur, bascule, url, "indicateurs.html")
    _livrer(bascule, "apres-sans-version")
    page.reload()
    assert page.evaluate("window.ancienneVersion") is True, "le script ancien devrait rester en cache : mélange constaté"
    contexte.close()


@pytest.mark.parametrize("page_html,script", PAGES, ids=[p for p, _ in PAGES])
def test_apres_une_livraison_un_rechargement_normal_charge_le_nouveau_script(navigateur, serveur_bascule, page_html, script):
    bascule, url = serveur_bascule
    contexte, page = _ouvrir_l_ancienne_version(navigateur, bascule, url, page_html)
    _livrer(bascule, "apres")
    page.reload()   # F5, pas Ctrl+F5
    assert page.evaluate("window.ancienneVersion") is None, f"{script} : l'ancienne version tourne encore"
    assert page.evaluate("typeof window.RITA") == "object", "le nouveau commun.js doit tourner"
    chargees = page.evaluate("performance.getEntriesByType('resource').map(r => r.name)")
    assert any(re.search(rf"/{re.escape(script)}\?v=[0-9a-f]+$", nom) for nom in chargees), (script, chargees)
    contexte.close()

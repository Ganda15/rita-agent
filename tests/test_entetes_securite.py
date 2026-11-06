"""Carte #75, constat S1 de la revue OWASP Top 10:2025 du 03/10 : les en-têtes de sécurité (06/11/2026).

Pourquoi : la revue (`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`) a relevé qu'aucune réponse ne portait d'en-tête
de sécurité et que le serveur s'annonçait (`Server: uvicorn`). Relevé de nouveau en production le 06/11 : même état.
L'interface n'a ni script en ligne, ni style en ligne, ni ressource externe : une politique de contenu `default-src 'self'`
tient sans rien casser, ce que le test en navigateur vérifie sur les cinq écrans.

Les pages de documentation de FastAPI (`/docs`, `/redoc`) chargent leur script depuis un CDN avec un script en ligne :
elles gardent les autres en-têtes, sans politique de contenu (leur exposition est la décision D7 d'Era, constat S2).
"""
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)
RACINE = Path(__file__).resolve().parent.parent

POLITIQUE = "default-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
COMMUNS = {
    "strict-transport-security": "max-age=31536000",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "no-referrer",
}


def _communs_presents(reponse):
    for nom, valeur in COMMUNS.items():
        assert reponse.headers.get(nom) == valeur, nom


def test_une_page_de_l_interface_porte_la_politique_de_contenu_et_les_en_tetes():
    reponse = client.get("/index.html")
    assert reponse.status_code == 200
    assert reponse.headers.get("content-security-policy") == POLITIQUE
    _communs_presents(reponse)


def test_un_refus_de_cle_porte_aussi_les_en_tetes():
    reponse = client.get("/donnees/portefeuille")
    assert reponse.status_code == 403
    assert reponse.headers.get("content-security-policy") == POLITIQUE
    _communs_presents(reponse)


def test_une_reponse_json_porte_les_en_tetes():
    reponse = client.get("/health")
    assert reponse.status_code == 200
    _communs_presents(reponse)


@pytest.mark.parametrize("chemin", ["/docs", "/redoc"])
def test_la_documentation_garde_sa_page_sans_politique_de_contenu(chemin):
    reponse = client.get(chemin)
    assert reponse.status_code == 200
    assert "content-security-policy" not in reponse.headers
    _communs_presents(reponse)


def test_un_chemin_qui_commence_comme_la_documentation_garde_la_politique():
    # Relecture de sécurité du 06/11 : l'exception vaut pour les pages de documentation exactes, pas pour un préfixe.
    reponse = client.get("/docs-inexistant.html")
    assert reponse.headers.get("content-security-policy") == POLITIQUE


def test_l_image_de_production_n_annonce_pas_son_serveur():
    commande = [ligne for ligne in (RACINE / "Dockerfile").read_text(encoding="utf-8").splitlines()
                if ligne.startswith("CMD [")]
    assert len(commande) == 1
    assert '"--no-server-header"' in commande[0]


# --- Dans un vrai navigateur : la politique ne bloque rien sur les cinq écrans -----------------------------------------

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
ECRANS = ["index.html", "indicateurs.html", "briefing.html", "question.html", "tableau-de-bord.html"]


def _port_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def serveur():
    port = _port_libre()
    env = dict(os.environ, RITA_API_KEY="cle-de-test-entetes-securite-32-car", LANGFUSE_TRACING_ENABLED="false")
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


@pytest.mark.parametrize("ecran", ECRANS)
def test_la_politique_ne_bloque_rien_sur_l_ecran_en_simulation(serveur, ecran):
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        navigateur = p.chromium.launch(headless=True, **canal)
        page = navigateur.new_page()
        bloques, erreurs = [], []
        page.on("console", lambda m: bloques.append(m.text) if re.search("Content Security Policy", m.text) else None)
        page.on("pageerror", lambda e: erreurs.append(str(e)))
        page.goto(f"{serveur}/{ecran}", wait_until="networkidle")
        page.evaluate("sessionStorage.setItem('rita_simulation', 'oui')")
        page.reload(wait_until="networkidle")
        page.wait_for_timeout(800)
        navigateur.close()
    assert bloques == []
    assert erreurs == []

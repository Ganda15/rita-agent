"""Refonte 001, tâche 7 : le parcours du briefing à travers la VRAIE API (conception § 9, revue du plan du 04/11).

Le serveur FastAPI tourne dans le processus du test (un fil `uvicorn.Server`) : les remplacements des bords (base,
recherche, fournisseur) s'appliquent donc à lui. Le navigateur parle au vrai `/briefing`, au vrai graphe et au vrai
garde-fou : **aucune réponse `/briefing` n'est fabriquée par le navigateur**. Ce test prouve que l'écran comprend la
vraie réponse (champs, en-têtes, formats), ce qu'une interception ne prouve pas. Aucun appel au modèle, aucun appel payant.
"""
import os
import socket
import threading
import time
from datetime import date
from unittest.mock import patch

import pytest
import uvicorn

import api.main
from api.main import app
from src.traces import Reponse
from tests.conftest import CLE_DE_TEST
from tests.test_briefing_diagnostic import passage, resultat_rag, scout

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

TEXTE = "LVMH clôture à 378,55 EUR, en légère baisse de 0,25 %.\n\nLes ventes publiées restent stables."
RECOMMANDATION = "Nous recommandons d'acheter le titre."   # refusé par guardrails/sortie.py (recommandation_explicite_fr)


@pytest.fixture(scope="module")
def api_reelle():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    # ws="none" : RITA n'a pas de WebSocket ; sans ce réglage, uvicorn charge une couche dépréciée de `websockets`.
    serveur = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning", ws="none"))
    fil = threading.Thread(target=serveur.run, daemon=True)
    fil.start()
    for _ in range(100):
        if serveur.started:
            break
        time.sleep(0.1)
    else:
        pytest.fail("le serveur de test n'a pas démarré en 10 s")
    yield f"http://127.0.0.1:{port}"
    serveur.should_exit = True
    fil.join(timeout=10)


@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


@pytest.fixture
def ecran(navigateur, api_reelle, monkeypatch):
    monkeypatch.setenv("LLM_ORDRE", "foundry")
    monkeypatch.setattr(api.main, "aujourd_hui_a_paris", lambda: date(2026, 11, 4))
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.erreurs_js = []
    page.on("pageerror", lambda e: page.erreurs_js.append(str(e)))
    page.goto(api_reelle + "/briefing.html")
    page.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_DE_TEST}')")
    page.goto(api_reelle + "/briefing.html")
    page.wait_for_selector("#demande:not([hidden])")
    yield page
    contexte.close()


def _rediger(page, fournisseur):
    """Demande le briefing de MC.PA ; rend la vraie réponse HTTP de `/briefing` (pour lire son X-Request-ID)."""
    passages = [passage(1, "LVMH publie ses ventes", lien="https://exemple.test/lvmh")]
    with patch("graph.workflow.collect", return_value=scout("MC.PA", date_cours="2026-10-30")), \
         patch("graph.workflow.rechercher", return_value=resultat_rag(passages)), \
         patch("src.llm._appel_foundry", side_effect=fournisseur):
        page.fill("#ticker", "MC.PA")
        with page.expect_response(lambda r: "/briefing?ticker=" in r.url and r.request.method == "POST") as attente:
            page.click("#form-briefing button[type=submit]")
        reponse = attente.value
        page.wait_for_function("document.getElementById('statut').textContent.length > 0"
                               " || !document.getElementById('resultat').hidden")
    return reponse


def test_parcours_reel_diagnostic_sources_et_reference(ecran):
    reponse = _rediger(ecran, lambda prompt, n: Reponse(texte=TEXTE, modele="gpt-5.4-2026-03-05"))
    assert reponse.status == 200
    ecran.wait_for_selector("#texte p")
    comprendre = ecran.locator("#comprendre").inner_text()
    for attendu in ("Azure AI Foundry", "gpt-5.4-2026-03-05", "1er essai réussi", "30/10/2026", "5 jours calendaires",
                    "3 jours de bourse écoulés depuis (calendrier Euronext)", "1 source fournie au modèle"):
        assert attendu in comprendre, attendu
    assert reponse.headers["x-request-id"] in comprendre, "la référence affichée est celle de la vraie réponse"
    assert ecran.evaluate("[...document.querySelectorAll('#sources a')].map(a => a.getAttribute('href'))") == \
        ["https://exemple.test/lvmh"]
    assert ecran.erreurs_js == []


def test_parcours_reel_refus_du_garde_fou(ecran):
    reponse = _rediger(ecran, lambda prompt, n: Reponse(texte=RECOMMANDATION, modele="gpt-5.4-2026-03-05"))
    assert reponse.status == 200 and reponse.json()["conforme_amf"] is False
    ecran.wait_for_selector("#texte p")
    assert RECOMMANDATION not in ecran.locator("body").inner_text(), "le texte retenu n'est jamais affiché"
    assert "retenu par le garde-fou" in ecran.locator("#texte").inner_text()
    assert "recommandation_explicite_fr" in ecran.locator("#verdict").inner_text()


def test_parcours_reel_aucun_fournisseur(ecran):
    def en_panne(prompt, n):
        raise RuntimeError("panne du fournisseur")
    reponse = _rediger(ecran, en_panne)
    assert reponse.status == 503
    assert "Aucun fournisseur de modèle n'a répondu" in ecran.locator("#statut").inner_text()
    assert ecran.locator("#texte p").count() == 0

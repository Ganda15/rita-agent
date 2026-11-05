"""Refonte 001, tâche 8 (exigence R2) : l'écran Indicateurs, dans un vrai navigateur, API interceptée.

Comparer les valeurs suivies et lire un indicateur comme un fait. La carte des performances se lit sans la couleur ; le
RSI s'écrit « RSI 14 : 41. Repères : 30 et 70. », jamais comme un signal ; au choix d'une valeur, sa courbe ; le nombre
de valeurs vient des données. Chaque bloc a sa panne : le tableau reste si le risque ou la courbe échouent.
"""
import json
import os
import re
from pathlib import Path

import pytest

from tests.test_briefing_ui import cotations
from tests.test_smoke_ui import serveur  # noqa: F401  (fixture : l'API servie en local)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
CLE = "cle-de-test-smoke-ui-32-caracteres-x"


def valeur(ticker, nom, perf_1m, **autres):
    base = {"ticker": ticker, "nom_officiel": nom, "devise": "EUR", "statut_qualite": "OK", "date_cours": "2026-11-03",
            "cours": 100.0, "fraicheur_jours": 1, "perf_1j_pct": -0.25, "perf_1s_pct": 1.2, "perf_1m_pct": perf_1m,
            "perf_ytd_pct": -10.1, "perf_1a_pct": 5.4, "ma20": 388.1775, "ma50": 404.115, "adtv20": 2.5e8,
            "distance_plus_haut_1a_pct": -20.0, "cotation_perimee": False}
    base.update(autres)
    return base


INDICATEURS = {"nb": 3, "seuil_perime_jours": 40, "nb_perimees": 1, "indicateurs": [
    valeur("MC.PA", "LVMH MOET VUITTON", -3.86, cours=401.5),
    valeur("AI.PA", "AIR LIQUIDE", 5.2, perf_1j_pct=1.99),
    valeur("VK.PA", "VALLOUREC ANCIEN", None, date_cours="2018-05-02", cotation_perimee=True, perf_1j_pct=None)]}
RISQUE = {"nb": 3, "indicateurs": [
    {"ticker": "MC.PA", "volatilite_annualisee_pct": 24.7, "drawdown_max_1a_pct": -30.2, "rsi_14": 44.1},
    {"ticker": "AI.PA", "volatilite_annualisee_pct": 18.0, "drawdown_max_1a_pct": -12.5, "rsi_14": 63.0},
    {"ticker": "VK.PA", "volatilite_annualisee_pct": None, "drawdown_max_1a_pct": None, "rsi_14": None}]}


@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


def servir(page, motif, statut, corps, delai_ms=0):
    def repondre(route):
        if delai_ms:
            page.wait_for_timeout(delai_ms)
        route.fulfill(status=statut, content_type="application/json", body=json.dumps(corps))
    page.route(motif, repondre)


def ouvrir(navigateur, serveur, indicateurs=INDICATEURS, risque=(200, RISQUE), courbe=(200, None)):  # noqa: F811
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.erreurs_js = []
    page.on("pageerror", lambda e: page.erreurs_js.append(str(e)))
    page.envois = []
    page.on("request", lambda r: page.envois.append(r.url) if r.method == "POST" else None)
    servir(page, "**/donnees/indicateurs", 200, indicateurs)
    servir(page, "**/donnees/indicateurs-risque", risque[0], risque[1])
    servir(page, "**/donnees/cotations?*", courbe[0], courbe[1] if courbe[1] is not None else cotations(179))
    page.goto(serveur + "/indicateurs.html")
    page.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE}')")
    page.goto(serveur + "/indicateurs.html")
    page.wait_for_selector("#lignes tr")
    return contexte, page


@pytest.fixture
def ecran(navigateur, serveur):  # noqa: F811
    contexte, page = ouvrir(navigateur, serveur)
    yield page
    contexte.close()


def ligne(page, ticker):
    return page.locator(f"#lignes tr[data-ticker='{ticker}']")


def choisir(page, ticker):
    ligne(page, ticker).locator("button.choisir-valeur").click()
    page.wait_for_selector("#detail:not([hidden])")


# --- la carte des performances --------------------------------------------------------------------------------------------

def test_carte_des_performances_lisible_sans_couleur(ecran):
    cellules = ligne(ecran, "MC.PA").locator("td.perf")
    textes = cellules.all_inner_texts()
    assert "▼ -0,25 %" in textes and "▲ +1,20 %" in textes and "▼ -3,86 %" in textes, textes
    classes = ecran.evaluate("[...document.querySelectorAll(\"#lignes tr[data-ticker='MC.PA'] td.perf\")].map(c => c.className)")
    assert any("perf-baisse" in c for c in classes) and any("perf-hausse" in c for c in classes)
    assert "la couleur ne fait que le répéter" in ecran.locator("#legende-couleurs").inner_text()
    assert ecran.erreurs_js == []


def test_nombre_de_valeurs_lu_dans_la_reponse(navigateur, serveur):  # noqa: F811
    deux = dict(INDICATEURS, nb=2, nb_perimees=0, indicateurs=INDICATEURS["indicateurs"][:2])
    contexte, page = ouvrir(navigateur, serveur, indicateurs=deux)
    assert page.locator("#nb-valeurs").inner_text() == "2 valeurs"
    contexte.close()
    html = (FRONTEND / "indicateurs.html").read_text(encoding="utf-8").lower()
    assert "trois valeurs" not in html and not re.search(r"\b111\b", html), "aucun nombre de valeurs écrit à la main"


def test_recherche_filtre_le_tableau(ecran):
    ecran.fill("#recherche", "air")
    assert ecran.locator("#lignes tr").count() == 1 and ligne(ecran, "AI.PA").count() == 1
    assert ecran.locator("#nb-valeurs").inner_text() == "1 valeur"


def test_tri_par_performance(ecran):
    ecran.uncheck("#masquer-perimees")   # 04/11 : les périmées sont masquées par défaut ; ce test trie aussi l'absent
    ecran.select_option("#tri", "perf_1m_pct")
    ordre = ecran.evaluate("[...document.querySelectorAll('#lignes tr')].map(tr => tr.dataset.ticker)")
    assert ordre == ["AI.PA", "MC.PA", "VK.PA"], "de la plus forte hausse à la plus forte baisse, l'absent à la fin"


def test_cotation_perimee_sans_rsi(ecran):
    ecran.uncheck("#masquer-perimees")   # 04/11 : masquées par défaut
    nom = ligne(ecran, "VK.PA").inner_text()
    assert "cotation périmée" in nom
    choisir(ecran, "VK.PA")
    assert "RSI 14 : non disponible" in ecran.locator("#detail").inner_text()


# --- le détail de la valeur choisie ------------------------------------------------------------------------------------------

def test_rsi_ecrit_comme_un_fait(ecran):
    choisir(ecran, "MC.PA")
    detail = ecran.locator("#detail").inner_text()
    assert "RSI 14 : 44,1. Repères : 30 et 70." in detail
    for interdit in ("survendu", "suracheté", "signal d'achat", "signal de vente", "achetez", "vendez"):
        assert interdit not in detail.lower(), interdit


def test_courbe_au_choix_d_une_valeur(navigateur, serveur):  # noqa: F811
    contexte, page = ouvrir(navigateur, serveur, courbe=(200, cotations(15)))
    choisir(page, "AI.PA")
    page.wait_for_selector("#detail-courbe svg")
    assert "moyennes indisponibles (moins de 20 séances)" in page.locator("#detail-courbe").inner_text()
    for attendu in ("MM20 : 388,18", "volatilité annualisée (20 séances) : 18,00 %", "pire baisse (1 an) : -12,50 %"):
        assert attendu in page.locator("#detail").inner_text(), attendu
    contexte.close()


def test_un_bloc_en_panne_n_efface_pas_les_autres(navigateur, serveur):  # noqa: F811
    contexte, page = ouvrir(navigateur, serveur, risque=(500, {"detail": "panne"}), courbe=(500, {"detail": "panne"}))
    assert page.locator("#lignes tr").count() == 2, "le tableau reste (les deux valeurs à jour, la périmée est masquée)"
    assert "▼ -3,86 %" in ligne(page, "MC.PA").inner_text()
    assert "indisponibles pour le moment" in page.locator("#note-risque").inner_text()
    choisir(page, "MC.PA")
    page.wait_for_selector("#detail-courbe:has-text('Courbe indisponible pour le moment')")
    assert "RSI 14 : non disponible" in page.locator("#detail").inner_text()
    assert page.erreurs_js == []
    contexte.close()


def test_reponse_tardive_ignoree(navigateur, serveur):  # noqa: F811
    contexte, page = ouvrir(navigateur, serveur)
    page.unroute("**/donnees/cotations?*")
    servir(page, "**/donnees/cotations?ticker=MC.PA*", 200, cotations(60, depart=100.0), delai_ms=1500)
    servir(page, "**/donnees/cotations?ticker=AI.PA*", 200, cotations(60, depart=900.0, ticker="AI.PA"))
    ligne(page, "MC.PA").locator("button.choisir-valeur").click()
    ligne(page, "AI.PA").locator("button.choisir-valeur").click()
    page.wait_for_selector("#detail-courbe svg")
    page.wait_for_timeout(1800)
    courbe = page.locator("#detail-courbe").inner_text()
    assert "900" in courbe and "100,00" not in courbe, courbe
    assert "AIR LIQUIDE" in page.locator("#detail").inner_text()
    contexte.close()


def test_lien_vers_le_briefing_preremplit_sans_envoyer(ecran, serveur):  # noqa: F811
    choisir(ecran, "MC.PA")
    lien = ecran.locator("#detail a.vers-briefing")
    assert lien.get_attribute("href") == "briefing.html?ticker=MC.PA"
    lien.click()
    ecran.wait_for_selector("#demande:not([hidden])")
    assert ecran.locator("#ticker").input_value() == "MC.PA"
    ecran.wait_for_timeout(800)
    assert [u for u in ecran.envois if "/briefing" in u] == [], "rien n'est envoyé tout seul : un appel payant attend un clic"


def test_tout_s_actionne_au_clavier(ecran):
    ligne(ecran, "MC.PA").locator("button.choisir-valeur").focus()
    ecran.keyboard.press("Enter")
    ecran.wait_for_selector("#detail:not([hidden])")
    assert ecran.evaluate("document.activeElement.id") == "detail", "le focus va au détail ouvert"
    assert ecran.erreurs_js == []

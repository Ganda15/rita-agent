"""Refonte 001, tâche 9 (exigence R1) : l'écran Portefeuille, dans un vrai navigateur, API interceptée.

Voir la répartition et les gains d'un coup d'œil : un anneau des poids, des barres de gain ou de perte, chacun avec les
mêmes chiffres écrits à côté. Une valorisation incomplète ne donne jamais d'anneau trompeur. La fraîcheur du jeu est
affichée, et chaque ligne garde la date de son cours. Aucune performance globale n'est inventée : l'API n'en fournit pas.
Les montants arrivent en texte décimal (« 11004.00 »), comme l'API les rend (mesuré le 04/11).
"""
import json
import os
import re

import pytest

from tests.test_frontend import code_sans_commentaires
from tests.test_smoke_ui import serveur  # noqa: F401  (fixture : l'API servie en local)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

CLE = "cle-de-test-smoke-ui-32-caracteres-x"


def position(ticker, nom, perf, valo, date="2026-11-03", devise="EUR", taux_manquant=False):
    return {"ticker": ticker, "nom_officiel": nom, "statut_qualite": "OK", "quantite": "10.0000", "pru": "100.0000",
            "devise": devise, "date_cours": date, "cours": "120.0000", "investi_eur": None if taux_manquant else "1000.00",
            "valorisation_eur": None if taux_manquant else valo, "performance_pct": perf,
            "taux_pour_eur": None if taux_manquant else "1", "taux_manquant": taux_manquant}


PORTEFEUILLE = {"nb": 3, "total_eur": 3200.0, "positions_sans_taux": 0, "positions_closes": 1, "positions": [
    position("BNP.PA", "BNP PARIBAS", "53.30", "1600.00"),
    position("AI.PA", "AIR LIQUIDE", "15.36", "960.00"),
    position("MC.PA", "LVMH MOET VUITTON", "-36.51", "640.00", date="2026-10-30")]}
INDICATEURS = {"nb": 3, "total_eur": 3200.0, "complet": True, "lignes": [
    {"ticker": "BNP.PA", "nom_officiel": "BNP PARIBAS", "devise": "EUR", "quantite": 10, "valorisation_eur": 1600.0, "poids_pct": 50.0},
    {"ticker": "AI.PA", "nom_officiel": "AIR LIQUIDE", "devise": "EUR", "quantite": 10, "valorisation_eur": 960.0, "poids_pct": 30.0},
    {"ticker": "MC.PA", "nom_officiel": "LVMH MOET VUITTON", "devise": "EUR", "quantite": 10, "valorisation_eur": 640.0, "poids_pct": 20.0}],
    "exposition": [{"devise": "EUR", "nb_lignes": 3, "valorisation_eur": 3200.0, "exposition_pct": 100.0}]}
FRAICHEUR = {"aujourdhui": "2026-11-04", "derniere_seance": "2026-11-03", "retard_jours_ouvres": 1, "statut": "vert",
             "message": "Données à jour, dernière séance du 03/11/2026."}


@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


def servir(page, motif, statut, corps):
    page.route(motif, lambda r: r.fulfill(status=statut, content_type="application/json", body=json.dumps(corps)))


def ouvrir(navigateur, serveur, portefeuille=PORTEFEUILLE, indicateurs=(200, INDICATEURS)):  # noqa: F811
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.erreurs_js = []
    page.on("pageerror", lambda e: page.erreurs_js.append(str(e)))
    servir(page, "**/donnees/portefeuille", 200, portefeuille)
    servir(page, "**/donnees/indicateurs-portefeuille", indicateurs[0], indicateurs[1])
    servir(page, "**/donnees/fraicheur", 200, FRAICHEUR)
    page.goto(serveur + "/index.html")
    page.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE}')")
    page.goto(serveur + "/index.html")
    page.wait_for_selector("#lignes tr")
    return contexte, page


@pytest.fixture
def ecran(navigateur, serveur):  # noqa: F811
    contexte, page = ouvrir(navigateur, serveur)
    yield page
    contexte.close()


def test_anneau_et_barres_avec_les_memes_chiffres(ecran):
    anneau = ecran.locator("#anneau").inner_text()
    for attendu in ("BNP PARIBAS : 50,0 %", "AIR LIQUIDE : 30,0 %", "LVMH MOET VUITTON : 20,0 %"):
        assert attendu in anneau, attendu
    assert ecran.locator("#anneau svg [data-serie='part']").count() == 3
    barres = ecran.locator("#barres").inner_text()
    for attendu in ("BNP PARIBAS : ▲ +53,30 %", "AIR LIQUIDE : ▲ +15,36 %", "LVMH MOET VUITTON : ▼ -36,51 %"):
        assert attendu in barres, attendu
    # Les mêmes chiffres que le tableau détaillé, qui reste sous les graphiques.
    tableau = ecran.locator("#lignes").inner_text()
    assert "+53,30 %" in tableau and "-36,51 %" in tableau.replace("−", "-")
    assert ecran.erreurs_js == []


def test_pas_d_anneau_si_incomplet(navigateur, serveur):  # noqa: F811
    incomplet = dict(PORTEFEUILLE, total_eur=None, positions_sans_taux=1, positions=PORTEFEUILLE["positions"][:2] + [
        position("AAPL", "APPLE", "19.08", None, devise="USD", taux_manquant=True)])
    indic = dict(INDICATEURS, total_eur=None, complet=False,
                 lignes=[dict(l, poids_pct=None) for l in INDICATEURS["lignes"]])
    contexte, page = ouvrir(navigateur, serveur, portefeuille=incomplet, indicateurs=(200, indic))
    assert page.locator("#anneau svg").count() == 0, "aucun anneau trompeur"
    assert "Poids non calculables : 1 ligne sans taux de change" in page.locator("#anneau").inner_text()
    assert page.locator("#lignes tr").count() == 3, "le tableau détaillé reste"
    assert page.locator("#carte-total").inner_text() == "non calculable"
    contexte.close()


def test_fraicheur_du_jeu_et_date_par_ligne(ecran):
    assert "dernière séance du 03/11/2026" in ecran.locator("#fraicheur").inner_text()
    dates = ecran.evaluate("[...document.querySelectorAll('#lignes tr')].map(tr => tr.querySelector('td.date-cours').textContent)")
    assert dates == ["03/11/2026", "03/11/2026", "30/10/2026"], "chaque ligne garde la date de SON cours"


def test_aucune_performance_globale_inventee(ecran):
    page_entiere = ecran.locator("main").inner_text().lower()
    for mot in ("performance globale", "performance totale", "gain total", "plus-value totale", "rendement global"):
        assert mot not in page_entiere, mot
    code = code_sans_commentaires("app.js")
    assert "reduce(" not in code, "aucune somme des montants : le total vient de l'API (total_eur)"


def test_chiffres_cles(ecran):
    assert ecran.locator("#carte-total").inner_text().replace(" ", " ").replace("\xa0", " ") == "3 200,00 €"
    assert ecran.locator("#carte-lignes").inner_text() == "3"
    assert ecran.locator("#carte-sans-taux").inner_text() == "0 ligne"
    assert ecran.locator("#carte-closes").inner_text() == "1"


def test_un_bloc_en_panne_n_efface_pas_les_autres(navigateur, serveur):  # noqa: F811
    contexte, page = ouvrir(navigateur, serveur, indicateurs=(500, {"detail": "panne"}))
    assert "Poids indisponibles pour le moment" in page.locator("#anneau").inner_text()
    assert page.locator("#barres svg").count() == 1, "les barres viennent du portefeuille, elles restent"
    assert page.locator("#lignes tr").count() == 3
    assert page.erreurs_js == []
    contexte.close()


def test_l_en_tete_de_date_est_dans_la_page():
    from pathlib import Path
    html = (Path(__file__).resolve().parent.parent / "frontend" / "index.html").read_text(encoding="utf-8")
    assert '<th scope="col">Date du cours</th>' in html
    assert not re.search(r"performance (globale|totale)", html.lower())


# --- l'écran doute de ses données (R1, critère 5, 04/11/2026 au soir) ------------------------------------------------------
# Viridien à +4 856,76 % en première place, 34 % du portefeuille : un prix de revient resté à l'échelle d'avant un
# regroupement d'actions. Le calcul était juste, la donnée fausse. L'écran le dit en texte, comme une chose à vérifier.

def _texte_propre(page, selecteur):
    return page.locator(selecteur).inner_text().replace("\u202f", " ").replace("\xa0", " ")


def test_une_performance_hors_du_commun_est_signalee_comme_a_verifier(navigateur, serveur):  # noqa: F811
    extreme = dict(PORTEFEUILLE, nb=4, positions=[position("VIRI.PA", "CGG BS", "4856.76", "11004.00")] + PORTEFEUILLE["positions"])
    contexte, page = ouvrir(navigateur, serveur, portefeuille=extreme)
    alerte = page.locator("#alertes-donnees")
    assert alerte.is_visible()
    texte = _texte_propre(page, "#alertes-donnees")
    assert "CGG BS" in texte and "+4 856,76 %" in texte
    assert "à vérifier" in texte and "regroupement" in texte, "la cause possible est dite comme une question à vérifier"
    for interdit in ("acheter", "vendre", "conseil", "recommand"):
        assert interdit not in texte.lower(), interdit
    # Au-dessus des dessins, pour être lue avant eux ; le dessin n'est ni caché ni plafonné.
    avant = page.evaluate("!!(document.getElementById('alertes-donnees').compareDocumentPosition("
                          "document.querySelector('.graphiques-portefeuille')) & Node.DOCUMENT_POSITION_FOLLOWING)")
    assert avant
    assert "CGG BS : ▲ +4 856,76 %" in _texte_propre(page, "#barres")
    contexte.close()


def test_aucune_alerte_pour_des_performances_ordinaires(ecran):
    assert ecran.locator("#alertes-donnees").is_hidden()


@pytest.mark.parametrize("performance, signalee", [
    ("899.99", False), ("900.00", True), ("-89.99", False), ("-90.00", True), ("0.00", False), (None, False)])
def test_les_seuils_de_l_alerte_sont_ceux_de_la_specification(navigateur, serveur, performance, signalee):  # noqa: F811
    """Un prix multiplié ou divisé par dix : +900 % ou -90 %. Le seuil est une convention déclarée, pas une mesure."""
    unique = dict(PORTEFEUILLE, nb=1, positions=[position("X.PA", "VALEUR X", performance, "1000.00")])
    contexte, page = ouvrir(navigateur, serveur, portefeuille=unique)
    assert page.locator("#alertes-donnees").is_visible() is signalee
    contexte.close()


def test_le_seuil_est_ecrit_une_fois_dans_le_code():
    code = code_sans_commentaires("app.js")
    assert "SEUIL_HAUT_PCT = 900" in code and "SEUIL_BAS_PCT = -90" in code

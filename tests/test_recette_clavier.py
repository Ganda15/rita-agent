"""Recette des cinq écrans au clavier, dans un vrai navigateur (C17.3, recette du 02/11/2026).

Les autres tests de l'interface vérifient le comportement à la souris ou par lecture du code. Ceux-ci parcourent chaque
écran comme une personne qui n'a qu'un clavier : atteindre le champ de clé par Tab, le voir focalisé, l'envoyer par
Entrée, puis faire le geste principal de l'écran. Les réponses de l'API sont remplacées par des réponses fabriquées sur
les formes réelles (aucun appel payant au modèle, aucune base) : c'est un **test simulé**, pas une preuve de production.
Chaque test a son propre contexte de navigateur : la page partagée des autres tests n'est pas touchée.
"""
import json

import pytest

from tests.test_smoke_ui import page, serveur  # noqa: F401, ce sont des fixtures
from tests.test_vigie import SAIN, _sante

CLE = "cle-de-test-smoke-ui-32-caracteres-x"
ECRANS = ["index.html", "indicateurs.html", "briefing.html", "question.html", "tableau-de-bord.html"]

PORTEFEUILLE = {"nb": 1, "total_eur": 5601.6, "positions_sans_taux": 0, "positions_closes": 0, "positions": [
    {"ticker": "MC.PA", "nom_officiel": "LVMH", "statut_qualite": "OK", "quantite": 12, "pru": 632.4, "devise": "EUR",
     "cours": 466.8, "investi_eur": 7588.8, "valorisation_eur": 5601.6, "performance_pct": -26.19,
     "taux_manquant": False}]}
INDICATEURS_PORTEFEUILLE = {"nb": 1, "total_eur": 5601.6, "complet": True, "exposition": [], "lignes": [
    {"ticker": "MC.PA", "nom_officiel": "LVMH", "devise": "EUR", "quantite": 12, "valorisation_eur": 5601.6,
     "poids_pct": 100.0}]}
FRAICHEUR = {"statut": "vert", "message": "Donnees du 30/10/2026", "retard_jours_ouvres": 0}
INDICATEURS = {"nb": 1, "indicateurs": [{"ticker": "MC.PA", "nom_officiel": "LVMH", "statut_qualite": "OK",
                                         "cotation_perimee": False, "date_cours": "2026-10-30", "cours": 466.8}]}
RISQUE = {"nb": 1, "indicateurs": [{"ticker": "MC.PA", "volatilite_annualisee_pct": 22.1,
                                    "drawdown_max_1a_pct": -41.0, "rsi_14": 43.99}]}
VALEURS = {"nb": 1, "valeurs": [{"ticker": "MC.PA", "nom_officiel": "LVMH"}]}
BRIEFING = {"ticker": "MC.PA", "price": 466.8, "change_pct": -0.25, "currency": "EUR",
            "briefing": "LVMH clôture à 466,80 EUR.\n\nAucune actualité récente.",
            "conforme_amf": True, "motifs_amf": []}
REPONSE = {"statut": "reponse", "texte": "Netflix supprime 2 000 postes [1].", "index": {"empreinte": "abc"},
           "references": [{"n": 1, "titre": "Netflix réduit ses effectifs", "source": "Les Échos", "table": "article",
                           "id": 42, "date": "2026-10-28", "lien": "https://www.lesechos.fr/"}]}
FICHE = {"table": "article", "id": 42, "titre": "Netflix réduit ses effectifs", "source": "Les Échos",
         "publie_le": "2026-10-28", "collecte_le": "2026-10-29", "extrait": "Netflix supprime 2 000 postes.",
         "lien": "https://www.lesechos.fr/"}

# Ce que montre chaque écran une fois la clé envoyée, et où doit être le focus (None : pas de focus imposé).
APRES_LA_CLE = {
    "index.html": ("#lignes tr", None),
    "indicateurs.html": ("tbody tr", None),
    "briefing.html": ("#demande", "ticker"),
    "question.html": ("#demande", "question"),
    "tableau-de-bord.html": ("#cartes .carte, #cartes [data-signal]", None),
}


def _servir(onglet, appels):
    """Répond à la place de l'API ; `appels` compte les lectures de `/sante`."""
    def repondre(corps, compter=None):
        def gestion(route):
            if compter is not None:
                compter.append(route.request.url)
            route.fulfill(status=200, content_type="application/json", body=json.dumps(corps))
        return gestion

    onglet.route("**/donnees/portefeuille*", repondre(PORTEFEUILLE))
    onglet.route("**/donnees/indicateurs-portefeuille*", repondre(INDICATEURS_PORTEFEUILLE))
    onglet.route("**/donnees/fraicheur*", repondre(FRAICHEUR))
    onglet.route("**/donnees/indicateurs-risque*", repondre(RISQUE))
    onglet.route("**/donnees/indicateurs", repondre(INDICATEURS))
    onglet.route("**/donnees/valeurs*", repondre(VALEURS))
    onglet.route("**/briefing?ticker=*", repondre(BRIEFING))
    onglet.route("**/question", repondre(REPONSE))
    onglet.route("**/donnees/articles/*", repondre(FICHE))
    onglet.route("**/health", repondre({"status": "ok"}))
    onglet.route("**/sante", repondre(_sante(*SAIN).json(), appels))


@pytest.fixture
def onglet(page, serveur):  # noqa: F811
    contexte = page.context.browser.new_context()
    nouvel_onglet = contexte.new_page()
    nouvel_onglet.appels_sante = []
    _servir(nouvel_onglet, nouvel_onglet.appels_sante)
    yield nouvel_onglet
    contexte.close()


def _actif(onglet):
    return onglet.evaluate("document.activeElement && document.activeElement.id")


def _tabuler_jusqu_a(onglet, condition, maximum=25):
    """Appuie sur Tab jusqu'à ce que `condition` (une expression JavaScript sur l'élément actif) soit vraie."""
    for _ in range(maximum):
        onglet.keyboard.press("Tab")
        if onglet.evaluate(f"(() => {{ const el = document.activeElement; return !!el && ({condition}); }})()"):
            return True
    return False


def _ouvrir_sans_cle(onglet, serveur, ecran):  # noqa: F811
    onglet.goto(f"{serveur}/{ecran}", wait_until="networkidle")
    onglet.wait_for_selector("#cle", state="visible")


@pytest.mark.parametrize("ecran", ECRANS)
def test_au_clavier_le_champ_de_cle_est_atteint_nomme_et_son_focus_se_voit(onglet, serveur, ecran):  # noqa: F811
    _ouvrir_sans_cle(onglet, serveur, ecran)
    onglet.evaluate("document.activeElement && document.activeElement.blur()")
    assert _tabuler_jusqu_a(onglet, "el.id === 'cle'"), f"{ecran} : le champ de clé n'est pas atteint par Tab"
    nom = onglet.evaluate("document.activeElement.labels[0].textContent.trim()")
    assert nom == "Clé d'API", nom
    contour = onglet.evaluate("getComputedStyle(document.activeElement).outlineStyle")
    assert contour != "none", f"{ecran} : le focus du champ de clé ne se voit pas"


@pytest.mark.parametrize("ecran", ECRANS)
def test_a_l_ouverture_sans_cle_le_focus_est_sur_le_champ_de_cle(onglet, serveur, ecran):  # noqa: F811
    # Écart E2 de la recette du 02/11 : le tableau de bord était le seul écran à ne pas le faire.
    _ouvrir_sans_cle(onglet, serveur, ecran)
    assert _actif(onglet) == "cle", f"{ecran} : le focus est sur « {_actif(onglet)} », pas sur le champ de clé"


@pytest.mark.parametrize("ecran", ECRANS)
def test_au_clavier_entree_envoie_la_cle_et_ouvre_l_ecran(onglet, serveur, ecran):  # noqa: F811
    _ouvrir_sans_cle(onglet, serveur, ecran)
    onglet.focus("#cle")
    onglet.keyboard.type(CLE)
    onglet.keyboard.press("Enter")
    selecteur, focus_attendu = APRES_LA_CLE[ecran]
    onglet.wait_for_selector(selecteur, state="visible", timeout=10_000)
    if focus_attendu:
        onglet.wait_for_function(f"document.activeElement && document.activeElement.id === '{focus_attendu}'")


def test_au_clavier_un_briefing_se_demande_et_le_resultat_recoit_le_focus(onglet, serveur):  # noqa: F811
    _ouvrir_sans_cle(onglet, serveur, "briefing.html")
    onglet.focus("#cle")
    onglet.keyboard.type(CLE)
    onglet.keyboard.press("Enter")
    onglet.wait_for_function("document.activeElement && document.activeElement.id === 'ticker'")
    onglet.keyboard.type("MC.PA")
    onglet.keyboard.press("Enter")
    onglet.wait_for_selector("#texte p", timeout=10_000)
    onglet.wait_for_function("document.activeElement && document.activeElement.id === 'resultat'")


def test_au_clavier_une_question_se_pose_et_la_fiche_s_ouvre(onglet, serveur):  # noqa: F811
    _ouvrir_sans_cle(onglet, serveur, "question.html")
    onglet.focus("#cle")
    onglet.keyboard.type(CLE)
    onglet.keyboard.press("Enter")
    onglet.wait_for_function("document.activeElement && document.activeElement.id === 'question'")
    onglet.keyboard.type("Combien de postes Netflix va-t-il supprimer ?")
    assert _tabuler_jusqu_a(onglet, "el.textContent.trim() === 'Poser la question'", maximum=3)
    onglet.keyboard.press("Enter")
    onglet.wait_for_selector("#references li", timeout=10_000)
    assert _tabuler_jusqu_a(onglet, "el.textContent.startsWith('Voir la fiche de la source 1')")
    onglet.keyboard.press("Enter")
    onglet.wait_for_selector("#fiche", state="visible", timeout=10_000)
    onglet.wait_for_function("document.activeElement && document.activeElement.id === 'fiche'")


def test_au_clavier_le_tableau_de_bord_s_actualise_et_se_suspend(onglet, serveur):  # noqa: F811
    onglet.goto(f"{serveur}/tableau-de-bord.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE}')")
    onglet.goto(f"{serveur}/tableau-de-bord.html")
    onglet.wait_for_function("document.body.dataset.etat === 'pret'")
    avant = len(onglet.appels_sante)
    assert _tabuler_jusqu_a(onglet, "el.id === 'actualiser'")
    onglet.keyboard.press("Enter")
    onglet.wait_for_function("document.body.dataset.etat === 'pret'")
    for _ in range(40):
        if len(onglet.appels_sante) > avant:
            break
        onglet.wait_for_timeout(50)
    assert len(onglet.appels_sante) == avant + 1, "Entrée sur « Actualiser » relit /sante une fois"
    assert _tabuler_jusqu_a(onglet, "el.id === 'suspendre'", maximum=3)
    onglet.keyboard.press("Space")
    assert onglet.get_attribute("#suspendre", "aria-pressed") == "true"


def test_au_clavier_la_zone_du_tableau_des_indicateurs_est_atteinte(onglet, serveur):  # noqa: F811
    onglet.goto(f"{serveur}/indicateurs.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE}')")
    onglet.goto(f"{serveur}/indicateurs.html", wait_until="networkidle")
    onglet.wait_for_selector("tbody tr", timeout=10_000)
    assert _tabuler_jusqu_a(onglet, "el.classList.contains('tableau-large')"), "zone qui défile non atteinte"
    contour = onglet.evaluate("getComputedStyle(document.activeElement).outlineStyle")
    assert contour != "none", "le focus de la zone qui défile ne se voit pas"

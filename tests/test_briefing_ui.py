"""Refonte 001, tâche 7 (exigence R3) : l'écran Briefing, dans un vrai navigateur, API interceptée (aucun appel payant).

Flux vertical, dans l'ordre où RITA travaille : chiffres clés, courbe, texte, « Comprendre ce résultat », « Sources
fournies au modèle ». Un clic donne un seul envoi. Un texte retenu par le garde-fou n'est jamais affiché. Chaque panne a
son message, et une panne n'efface jamais ce qui fonctionne. Textes : conception § 7 et § 8, contraintes globales du plan.
"""
import json
import os
from datetime import date, timedelta

import pytest

from tests.test_smoke_ui import serveur  # noqa: F401  (fixture : l'API servie en local)
from tests.attente import attendre_que  # noqa: E402  (06/11 : la politique de contenu refuse wait_for_function)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

CLE = "cle-de-test-smoke-ui-32-caracteres-x"
VERDICT = "Aucune recommandation d'achat ou de vente détectée"
DIAGNOSTIC = {"fournisseur": "foundry", "modele": "gpt-5.4-2026-03-05",
              "tentatives": [{"fournisseur": "foundry", "reussi": True}], "duree_ms": 6240,
              "date_cours": "2026-10-30", "age_calendaire_jours": 5, "jours_bourse_ecoules": 3, "calendrier": "Euronext",
              "sources": [{"titre": "LVMH publie ses ventes", "source": "Les Échos", "publie_le": "2026-10-28",
                           "lien": "https://www.lesechos.fr/lvmh"},
                          {"titre": "Article sans lien", "source": "Boursorama", "publie_le": "2026-10-27", "lien": None}]}
BRIEFING = {"ticker": "MC.PA", "price": 401.5, "change_pct": -0.25, "currency": "EUR",
            "briefing": "LVMH clôture à 401,50 EUR, en légère baisse de 0,25 %.\n\nLes ventes publiées restent stables.",
            "conforme_amf": True, "motifs_amf": [], "articles_transmis": 2, "diagnostic": DIAGNOSTIC}
INDICATEURS = {"nb": 1, "indicateurs": [{"ticker": "MC.PA", "date_cours": "2026-10-30", "perf_1m_pct": -3.86,
                                         "rsi_14": 44.1, "ma20": 388.1775, "ma50": 404.115}]}


def cotations(n, depart=400.0, ticker="MC.PA"):
    jours, jour = [], date(2026, 5, 4)
    for i in range(n):
        while jour.weekday() >= 5:
            jour += timedelta(days=1)
        jours.append({"ticker": ticker, "date_seance": jour.isoformat(), "cloture": f"{depart + i * 0.5:.4f}"})
        jour += timedelta(days=1)
    return {"ticker": ticker, "nb": n, "cotations": list(reversed(jours))}


@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


@pytest.fixture
def ecran(navigateur, serveur):  # noqa: F811
    """L'écran Briefing avec une clé gardée, et des réponses par défaut pour les trois lectures de données."""
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.erreurs_js = []
    page.on("pageerror", lambda e: page.erreurs_js.append(str(e)))
    page.envois = []
    page.on("request", lambda r: page.envois.append(r.url) if r.method == "POST" and "/briefing" in r.url else None)
    servir(page, "**/donnees/valeurs?*", 200, {"nb": 1, "valeurs": [{"ticker": "MC.PA", "nom_officiel": "LVMH"}]})
    servir(page, "**/donnees/indicateurs?*", 200, INDICATEURS)
    servir(page, "**/donnees/cotations?*", 200, cotations(179))
    page.goto(serveur + "/briefing.html")
    page.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE}')")
    page.goto(serveur + "/briefing.html")
    page.wait_for_selector("#demande:not([hidden])")
    yield page
    contexte.close()


def servir(page, motif, statut, corps, entetes=None, delai_ms=0):
    def repondre(route):
        if delai_ms:
            page.wait_for_timeout(delai_ms)
        route.fulfill(status=statut, content_type="application/json", headers=entetes or {}, body=json.dumps(corps))
    page.route(motif, repondre)


def demander(page, ticker="MC.PA"):
    page.fill("#ticker", ticker)
    page.click("#form-briefing button[type=submit]")


def attendre_resultat(page):
    page.wait_for_selector("#resultat:not([hidden]) #texte p")


def attendre_la_fin_de_la_demande(page):
    """Le message de fin, pas le message d'attente : « Rédaction en cours » s'écrit dans `#statut` dès l'envoi (04/11/2026,
    course trouvée dans la CI ; attendre un `#statut` non vide lisait parfois ce message-là)."""
    attendre_que(page, "(() => { const t = document.getElementById('statut').textContent;"
                           " return t.length > 0 && !t.startsWith('Rédaction en cours'); })()")


# --- le flux et ce qu'il dit ------------------------------------------------------------------------------------------------

def test_flux_vertical_dans_l_ordre(ecran):
    servir(ecran, "**/briefing?*", 200, BRIEFING, {"X-Request-ID": "ref0123456789abcd"})
    demander(ecran)
    attendre_resultat(ecran)
    ecran.wait_for_selector("#courbe svg")
    ordre = ecran.evaluate("""['#chiffres', '#bloc-courbe', '#bloc-texte', '#comprendre', '#sources'].map(s => {
        const e = document.querySelector(s); return e ? e.getBoundingClientRect().top : null; })""")
    assert None not in ordre and ordre == sorted(ordre), ordre
    assert ecran.locator("#texte p").count() == 2
    assert ecran.erreurs_js == []


def test_chiffres_cles(ecran):
    servir(ecran, "**/briefing?*", 200, BRIEFING)
    demander(ecran)
    attendre_resultat(ecran)
    ecran.wait_for_selector("#chiffre-mois:has-text('%')")
    chiffres = ecran.locator("#chiffres").inner_text()
    for attendu in ("401,50 EUR", "▼ -0,25 %", "▼ -3,86 %", VERDICT):
        assert attendu in chiffres, attendu


def test_verdict_mot_pour_mot(ecran):
    servir(ecran, "**/briefing?*", 200, BRIEFING)
    demander(ecran)
    attendre_resultat(ecran)
    assert ecran.locator("#verdict").inner_text() == VERDICT
    page_entiere = ecran.locator("main").inner_text().lower()
    assert "vérifié" not in page_entiere and "approuvé" not in page_entiere


def test_comprendre_ce_resultat_affiche_le_diagnostic(ecran):
    servir(ecran, "**/briefing?*", 200, BRIEFING, {"X-Request-ID": "ref0123456789abcd"})
    demander(ecran)
    attendre_resultat(ecran)
    texte = ecran.locator("#comprendre").inner_text()
    for attendu in ("Azure AI Foundry", "gpt-5.4-2026-03-05", "1er essai réussi", "30/10/2026", "5 jours calendaires",
                    "3 jours de bourse écoulés depuis (calendrier Euronext)", "2 sources fournies au modèle", "6,2 s",
                    "ref0123456789abcd", VERDICT):
        assert attendu in texte, attendu
    sources = ecran.locator("#sources").inner_text()
    assert "LVMH publie ses ventes" in sources and "Les Échos" in sources and "28/10/2026" in sources


def test_les_essais_echoues_sont_dits_sans_message(ecran):
    diag = dict(DIAGNOSTIC, fournisseur="anthropic", modele=None,
                tentatives=[{"fournisseur": "foundry", "reussi": False}, {"fournisseur": "anthropic", "reussi": True}])
    servir(ecran, "**/briefing?*", 200, dict(BRIEFING, diagnostic=diag))
    demander(ecran)
    attendre_resultat(ecran)
    texte = ecran.locator("#comprendre").inner_text()
    assert "Azure AI Foundry : échec" in texte and "Anthropic : réussi" in texte
    assert "modèle non communiqué par le fournisseur" in texte


def test_hors_euronext_seul_l_age_est_donne(ecran):
    diag = dict(DIAGNOSTIC, jours_bourse_ecoules=None, calendrier=None)
    servir(ecran, "**/briefing?*", 200, dict(BRIEFING, diagnostic=diag))
    demander(ecran)
    attendre_resultat(ecran)
    texte = ecran.locator("#comprendre").inner_text()
    assert "5 jours calendaires" in texte and "séances non comptées (place hors Euronext)" in texte


def test_lien_null_non_cliquable(ecran):
    diag = dict(DIAGNOSTIC, sources=[{"titre": "Sans lien", "source": "A", "publie_le": "2026-10-27", "lien": None},
                                     {"titre": "Piégé", "source": "B", "publie_le": "2026-10-27", "lien": "javascript:alert(1)"},
                                     {"titre": "Sûr", "source": "C", "publie_le": "2026-10-27", "lien": "https://exemple.test/a"}])
    servir(ecran, "**/briefing?*", 200, dict(BRIEFING, diagnostic=diag))
    demander(ecran)
    attendre_resultat(ecran)
    liens = ecran.evaluate("[...document.querySelectorAll('#sources a')].map(a => [a.textContent, a.getAttribute('href')])")
    assert liens == [["Sûr", "https://exemple.test/a"]]
    assert "Sans lien" in ecran.locator("#sources").inner_text() and "Piégé" in ecran.locator("#sources").inner_text()


# --- l'envoi ------------------------------------------------------------------------------------------------------------------

def test_un_seul_envoi_par_clic(ecran):
    servir(ecran, "**/briefing?*", 200, BRIEFING, delai_ms=800)
    ecran.fill("#ticker", "MC.PA")
    bouton = ecran.locator("#form-briefing button[type=submit]")
    bouton.click()
    assert bouton.is_disabled(), "le bouton est inactif pendant la rédaction"
    ecran.evaluate("document.getElementById('form-briefing').requestSubmit()")   # un second envoi, au clavier par exemple
    attendre_resultat(ecran)
    assert len(ecran.envois) == 1, ecran.envois
    assert not bouton.is_disabled()


def test_texte_refuse_jamais_affiche(ecran):
    """Même si une réponse refusée portait encore le texte du modèle, l'écran ne l'affiche pas : seulement le refus."""
    refuse = dict(BRIEFING, conforme_amf=False, motifs_amf=["recommandation_achat"],
                  briefing="ACHETEZ LVMH MAINTENANT, signal d'achat fort.")
    servir(ecran, "**/briefing?*", 200, refuse, {"X-Request-ID": "refrefus0123456789"})
    demander(ecran)
    attendre_resultat(ecran)
    page_entiere = ecran.locator("body").inner_text()
    assert "ACHETEZ" not in page_entiere and "signal d'achat" not in page_entiere
    assert "retenu par le garde-fou" in ecran.locator("#texte").inner_text()
    assert "recommandation_achat" in ecran.locator("#verdict").inner_text()
    assert "refrefus0123456789" in ecran.locator("#comprendre").inner_text()


# --- les pannes ---------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("statut, corps, attendu", [
    (422, {"detail": "Valeur inconnue : aucun briefing n'est possible pour ce code."}, "Valeur introuvable : « XXX.PA »"),
    (502, {"detail": "ticker absent de la base : XXX.PA"}, "Données indisponibles pour « XXX.PA »"),
    (503, {"detail": {"code": "AUCUN_FOURNISSEUR", "message": "Aucun fournisseur de modèle n'a répondu."}},
     "Aucun fournisseur de modèle n'a répondu"),
    (500, {"detail": "Erreur interne. Identifiant de requete : ref500"}, "Le briefing n'a pas pu être produit"),
    (429, {"detail": {"statut": "refus", "motif": "LIMITE_DE_DEBIT", "texte": "Trop de demandes en peu de temps."}},
     "Trop de demandes en peu de temps."),
])
def test_un_message_par_panne(ecran, statut, corps, attendu):
    servir(ecran, "**/briefing?*", statut, corps, {"X-Request-ID": "refpanne0123456789"})
    demander(ecran, "XXX.PA")
    attendre_la_fin_de_la_demande(ecran)
    message = ecran.locator("#statut").inner_text()
    assert attendu in message, message
    if statut == 500:
        assert "refpanne0123456789" in message, "la référence de la requête, pour retrouver la panne"
    assert not ecran.locator("#form-briefing button[type=submit]").is_disabled()


def test_le_message_de_panne_remplace_le_message_d_attente_meme_avec_une_reponse_lente(ecran):
    """04/11/2026 : `test_un_message_par_panne` échouait au hasard dans la CI (deux cas sur cinq au push de `develop` en
    `55b9687`, aucun dans la PR sur le même commit). Cause : il attendait un `#statut` non vide, or « Rédaction en cours »
    s'y écrit dès l'envoi ; sur une machine chargée, le test lisait ce message avant l'arrivée de la panne. Reproduit ici
    à coup sûr par une réponse retardée de 600 ms."""
    servir(ecran, "**/briefing?*", 503, {"detail": {"code": "AUCUN_FOURNISSEUR",
                                                    "message": "Aucun fournisseur de modèle n'a répondu."}}, delai_ms=600)
    demander(ecran, "XXX.PA")
    attendre_la_fin_de_la_demande(ecran)
    assert "Aucun fournisseur de modèle n'a répondu" in ecran.locator("#statut").inner_text()


def test_cle_refusee_redemandee_et_oubliee(ecran):
    servir(ecran, "**/briefing?*", 403, {"detail": "Clé API invalide ou absente"})
    demander(ecran)
    ecran.wait_for_selector("#connexion:not([hidden])")
    assert "Clé d'API refusée" in ecran.locator("#statut").inner_text()
    assert ecran.evaluate("sessionStorage.getItem('rita_api_key')") is None


def test_serveur_muet(ecran):
    ecran.route("**/briefing?*", lambda route: route.abort())
    demander(ecran)
    attendre_que(ecran, "document.getElementById('statut').textContent.includes('Le serveur ne répond pas')")
    assert not ecran.locator("#form-briefing button[type=submit]").is_disabled(), "le bouton redevient actif"


def test_une_panne_de_la_courbe_n_efface_pas_le_briefing(ecran):
    ecran.unroute("**/donnees/cotations?*")
    servir(ecran, "**/donnees/cotations?*", 500, {"detail": "panne"})
    servir(ecran, "**/briefing?*", 200, BRIEFING)
    demander(ecran)
    attendre_resultat(ecran)
    ecran.wait_for_selector("#courbe:has-text('Courbe indisponible pour le moment')")
    assert ecran.locator("#texte p").count() == 2


def test_un_briefing_en_panne_n_efface_pas_la_courbe(ecran):
    servir(ecran, "**/briefing?*", 503, {"detail": {"code": "AUCUN_FOURNISSEUR",
                                                    "message": "Aucun fournisseur de modèle n'a répondu."}})
    demander(ecran)
    ecran.wait_for_selector("#courbe svg")
    assert "Aucun fournisseur de modèle n'a répondu" in ecran.locator("#statut").inner_text()
    assert ecran.locator("#texte p").count() == 0


def test_reponse_tardive_ignoree(ecran):
    """La courbe d'une valeur demandée avant ne s'affiche jamais sous la valeur demandée ensuite."""
    ecran.unroute("**/donnees/cotations?*")
    servir(ecran, "**/donnees/cotations?ticker=MC.PA*", 200, cotations(60, depart=100.0), delai_ms=1500)
    servir(ecran, "**/donnees/cotations?ticker=AI.PA*", 200, cotations(60, depart=900.0, ticker="AI.PA"))
    servir(ecran, "**/briefing?ticker=MC.PA", 200, BRIEFING)
    servir(ecran, "**/briefing?ticker=AI.PA", 200, dict(BRIEFING, ticker="AI.PA"))
    demander(ecran, "MC.PA")
    attendre_resultat(ecran)
    demander(ecran, "AI.PA")                       # la courbe de MC.PA n'est pas encore arrivée
    ecran.wait_for_selector("#courbe svg")
    ecran.wait_for_timeout(1800)                   # la réponse tardive de MC.PA arrive
    alternative = ecran.locator("#courbe").inner_text()
    assert "900" in alternative and "100,00" not in alternative, alternative


# --- clavier et focus ---------------------------------------------------------------------------------------------------------

def test_focus_va_au_resultat_ou_a_l_erreur(ecran):
    servir(ecran, "**/briefing?ticker=MC.PA", 200, BRIEFING)
    demander(ecran, "MC.PA")
    attendre_resultat(ecran)
    assert ecran.evaluate("document.activeElement.id") == "resultat"
    servir(ecran, "**/briefing?ticker=XXX.PA", 422, {"detail": "Valeur inconnue"})
    demander(ecran, "XXX.PA")
    attendre_que(ecran, "document.getElementById('statut').textContent.includes('introuvable')")
    assert ecran.evaluate("document.activeElement.id") == "statut"


def test_tout_s_actionne_au_clavier(ecran):
    servir(ecran, "**/briefing?*", 200, BRIEFING)
    ecran.focus("#ticker")
    ecran.keyboard.type("MC.PA")
    ecran.keyboard.press("Enter")
    attendre_resultat(ecran)
    assert ecran.locator("#texte p").count() == 2
    assert ecran.erreurs_js == []


def test_courbe_lisible_sur_mobile(navigateur, serveur):  # noqa: F811
    """À 412 px, la courbe (640 unités de large) est réduite de moitié : ses étiquettes de 12 unités feraient 6 px.
    La légende grandit, et les axes restent : une graduation sur deux s'efface, les autres grandissent (avant le 13/11,
    tous les repères s'effaçaient ; l'oral blanc a relevé une courbe sans axes ni échelle)."""
    contexte = navigateur.new_context(viewport={"width": 412, "height": 900})
    page = contexte.new_page()
    servir(page, "**/donnees/valeurs?*", 200, {"nb": 0, "valeurs": []})
    servir(page, "**/donnees/indicateurs?*", 200, INDICATEURS)
    servir(page, "**/donnees/cotations?*", 200, cotations(179))
    servir(page, "**/briefing?*", 200, BRIEFING)
    page.goto(serveur + "/briefing.html")
    page.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE}')")
    page.goto(serveur + "/briefing.html")
    page.fill("#ticker", "MC.PA")
    page.click("#form-briefing button[type=submit]")
    page.wait_for_selector("#courbe svg")
    hauteurs = page.evaluate("[...document.querySelectorAll('#courbe .legende')].map(t => t.getBoundingClientRect().height)")
    assert hauteurs and min(hauteurs) >= 9, hauteurs
    principales = page.evaluate("""[...document.querySelectorAll('#courbe .graduation:not(.secondaire)')]
        .map(t => getComputedStyle(t).display === 'none' ? 0 : t.getBoundingClientRect().height)""")
    assert len(principales) >= 4 and min(principales) >= 9, f"au moins 2 prix et 2 dates lisibles : {principales}"
    assert page.evaluate("""[...document.querySelectorAll('#courbe .graduation.secondaire')]
        .every(t => getComputedStyle(t).display === 'none')""")
    assert page.evaluate("document.querySelectorAll('#courbe line.axe-x, #courbe line.axe-y').length") == 2
    largeur_champ = page.evaluate("document.getElementById('ticker').getBoundingClientRect().width")
    assert largeur_champ >= 200, f"le champ du code reste utilisable sur un téléphone ({largeur_champ} px)"
    contexte.close()

"""#73 (recette du 01/11/2026) : la clé d'API n'est gardée qu'après avoir fonctionné, sur Briefing comme sur Question.

La règle est écrite dans les deux écrans (`frontend/briefing.js` et `frontend/question.js` : « la clé n'est gardée
qu'après avoir fonctionné ») et dans le critère I8 des écrans 2 et 3 (`evidence/C14/`). Les deux écrans la gardent
pourtant dès l'envoi du formulaire de clé, avant tout appel. Ces tests le montrent dans un vrai navigateur, l'API
interceptée : aucun appel au modèle.

Quatre cas, sur chaque écran : clé saisie mais pas encore vérifiée ; clé refusée (403) ; clé acceptée ; service
indisponible (503), qui ne dit pas que la clé est mauvaise et ne doit donc pas effacer une clé déjà vérifiée.
"""
import json
import os

import pytest

from tests.test_smoke_ui import serveur  # noqa: F401  (fixture : l'API servie en local)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

CLE = "rita_api_key"
CLE_VERIFIEE = "cle-de-test-smoke-ui-32-caracteres-x"

# Pour chaque écran : sa page, l'appel à intercepter, le champ à remplir, le formulaire et un corps de réponse réussie.
ECRANS = {
    "briefing": ("/briefing.html", "**/briefing?ticker=*", "#ticker", "MC.PA", "#form-briefing",
                 {"ticker": "MC.PA", "price": 378.55, "change_pct": -0.25, "currency": "EUR",
                  "briefing": "LVMH clôture à 378,55 EUR.", "conforme_amf": True, "motifs_amf": []}),
    "question": ("/question.html", "**/question", "#question", "Que disent les articles sur LVMH ?", "#form-question",
                 {"statut": "refus", "motif": "INTENTION_INTERDITE", "texte": "Je ne peux pas traiter cette demande."}),
}


@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


@pytest.fixture
def page(navigateur):
    contexte = navigateur.new_context()   # un sessionStorage neuf à chaque test
    pg = contexte.new_page()
    yield pg
    contexte.close()


def _cle_gardee(page):
    return page.evaluate(f"sessionStorage.getItem('{CLE}')")


def _saisir_cle(page, serveur, ecran, cle):
    chemin = ECRANS[ecran][0]
    page.goto(serveur + chemin, wait_until="networkidle")
    page.fill("#cle", cle)
    page.click("#form-cle button[type=submit]")


def _envoyer(page, ecran, statut, corps):
    _, motif, champ, valeur, formulaire, _ = ECRANS[ecran]
    page.route(motif, lambda route: route.fulfill(status=statut, content_type="application/json", body=json.dumps(corps)))
    page.fill(champ, valeur)
    page.click(f"{formulaire} button[type=submit]")
    page.wait_for_timeout(1000)


@pytest.mark.parametrize("ecran", ECRANS)
def test_une_cle_saisie_n_est_pas_gardee_avant_un_appel_reussi(page, serveur, ecran):  # noqa: F811
    _saisir_cle(page, serveur, ecran, "cle-pas-encore-verifiee")
    assert _cle_gardee(page) is None


@pytest.mark.parametrize("ecran", ECRANS)
def test_une_cle_refusee_n_est_pas_gardee(page, serveur, ecran):  # noqa: F811
    _saisir_cle(page, serveur, ecran, "cle-refusee")
    _envoyer(page, ecran, 403, {"detail": "Clé d'API invalide"})
    assert _cle_gardee(page) is None


@pytest.mark.parametrize("ecran", ECRANS)
def test_une_cle_acceptee_est_gardee(page, serveur, ecran):  # noqa: F811
    _saisir_cle(page, serveur, ecran, CLE_VERIFIEE)
    _envoyer(page, ecran, 200, ECRANS[ecran][5])
    assert _cle_gardee(page) == CLE_VERIFIEE


@pytest.mark.parametrize("ecran", ECRANS)
def test_une_panne_du_service_n_efface_pas_une_cle_deja_verifiee(page, serveur, ecran):  # noqa: F811
    chemin = ECRANS[ecran][0]
    page.goto(serveur + chemin, wait_until="networkidle")
    page.evaluate(f"sessionStorage.setItem('{CLE}', '{CLE_VERIFIEE}')")
    page.goto(serveur + chemin, wait_until="networkidle")
    _envoyer(page, ecran, 503, {"detail": "service indisponible"})
    assert _cle_gardee(page) == CLE_VERIFIEE


@pytest.mark.parametrize("panne", ["503", "reseau"])
@pytest.mark.parametrize("ecran", ECRANS)
def test_une_panne_au_premier_essai_ne_garde_pas_une_cle_jamais_verifiee(page, serveur, ecran, panne):  # noqa: F811
    """Revue du 01/11 : une nouvelle clé, puis un 503 ou une panne réseau au premier appel. La panne ne dit pas que la
    clé est mauvaise, mais elle ne dit pas non plus qu'elle est bonne : la clé n'est toujours pas gardée."""
    _saisir_cle(page, serveur, ecran, "cle-nouvelle-jamais-verifiee")
    if panne == "503":
        _envoyer(page, ecran, 503, {"detail": "service indisponible"})
    else:
        _, motif, champ, valeur, formulaire, _ = ECRANS[ecran]
        page.route(motif, lambda route: route.abort())
        page.fill(champ, valeur)
        page.click(f"{formulaire} button[type=submit]")
        page.wait_for_timeout(1000)
    assert _cle_gardee(page) is None

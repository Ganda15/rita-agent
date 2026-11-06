"""Sprint 5, étape 5 : le tableau de bord dans un vrai navigateur (grille, critère 2 : « compris sans explication »).

Le même dispositif que `tests/test_smoke_ui.py` : l'API servie par uvicorn, Chrome piloté par Playwright. `/sante` et
`/health` sont remplacés par des réponses fabriquées, une par état ; elles sont construites par le vrai code
(`api.sante.construire`, aides de `tests/test_vigie.py`), donc elles suivent le contrat réel. Aucune attente fixe :
chaque test attend que la page dise elle-même qu'elle a fini (`document.body.dataset.etat === "pret"`).
"""
import json
from datetime import datetime

import pytest

from tests.test_smoke_ui import page, serveur  # noqa: F401, ce sont des fixtures
from tests.test_vigie import ATTAQUE, SAIN, _sante
from tests.attente import attendre_que  # noqa: E402  (06/11 : la politique de contenu refuse wait_for_function)

CLE = "cle-de-test-smoke-ui-32-caracteres-x"
CARTES = ["service", "erreurs_techniques", "refus_securite", "latence_p95_ms", "cout_24h", "fraicheur",
          "rejets_15_min"]


def _tableau(page, serveur, sante, statut_sante=200, statut_health=200, cle=CLE):  # noqa: F811
    """Affiche le tableau de bord avec les réponses données ; rend ce que montrent le résumé et les cartes."""
    corps = sante if isinstance(sante, str) else json.dumps(sante)
    page.route("**/sante", lambda route: route.fulfill(status=statut_sante, content_type="application/json",
                                                       body=corps))
    page.route("**/health", lambda route: route.fulfill(status=statut_health, content_type="application/json",
                                                        body='{"status": "ok"}'))
    try:
        page.goto(serveur + "/tableau-de-bord.html", wait_until="networkidle")
        page.evaluate(f"sessionStorage.setItem('rita_api_key', '{cle}')")
        page.goto(serveur + "/tableau-de-bord.html", wait_until="networkidle")
        attendre_que(page, "document.body.dataset.etat === 'pret'", timeout=10_000)
        cartes = {}
        for signal in CARTES:
            carte = page.locator(f'[data-signal="{signal}"]')
            cartes[signal] = {"etat": carte.locator(".etat").inner_text() if carte.count() else None,
                              "texte": carte.inner_text() if carte.count() else ""}
        return {"resume": page.locator("#resume").inner_text(), "cartes": cartes,
                "horodatages": page.locator("#horodatages").inner_text() if page.locator("#horodatages").count()
                else "", "connexion_visible": page.locator("#connexion").is_visible()}
    finally:
        page.unroute("**/sante")
        page.unroute("**/health")


def test_tout_va_bien_et_les_sept_cartes_le_disent(page, serveur):  # noqa: F811
    ecran = _tableau(page, serveur, _sante(*SAIN).json())
    assert ecran["resume"] == "Tout va bien."
    assert [ecran["cartes"][s]["etat"] for s in CARTES] == ["SAIN"] * 7
    assert page.erreurs_js == []


def test_un_probleme_dit_quoi_faire(page, serveur):  # noqa: F811
    ecran = _tableau(page, serveur, _sante(*ATTAQUE).json())
    carte = ecran["cartes"]["refus_securite"]
    assert carte["etat"] == "PROBLÈME"
    assert "12 sur 14" in carte["texte"] and "Que faire" in carte["texte"]
    assert ecran["resume"] == "1 signal demande une action."


def test_une_attention_dit_aussi_quoi_faire(page, serveur):  # noqa: F811
    erreur = [(60, 503, "erreur", "FOURNISSEUR_INDISPONIBLE")] + [(60, 200, "reponse", "OK")] * 5
    carte = _tableau(page, serveur, _sante(*erreur).json())["cartes"]["erreurs_techniques"]
    assert carte["etat"] == "ATTENTION" and "Que faire" in carte["texte"]


def test_sans_trafic_les_cartes_disent_inconnu_et_pourquoi_sans_consigne(page, serveur):  # noqa: F811
    ecran = _tableau(page, serveur, _sante().json())
    carte = ecran["cartes"]["refus_securite"]
    assert carte["etat"] == "INCONNU"
    assert "Pas assez de questions pour juger" in carte["texte"] and "Que faire" not in carte["texte"]
    assert ecran["resume"].startswith("Mesures incomplètes")


def test_les_trois_heures_sont_affichees(page, serveur):  # noqa: F811
    ecran = _tableau(page, serveur, _sante(*SAIN).json())
    assert "Tableau actualisé à" in ecran["horodatages"] and "Mesures calculées à" in ecran["horodatages"]
    assert "Coût cumulé depuis" in ecran["cartes"]["cout_24h"]["texte"]
    assert "€" in ecran["cartes"]["cout_24h"]["texte"] and "USD" not in ecran["cartes"]["cout_24h"]["texte"]


def test_sante_en_panne_et_health_sain(page, serveur):  # noqa: F811
    ecran = _tableau(page, serveur, {"detail": "erreur"}, statut_sante=500)
    assert "n'a pas pu lire les mesures" in ecran["resume"]
    assert ecran["cartes"]["service"]["etat"] == "SAIN"
    assert {ecran["cartes"][s]["etat"] for s in CARTES[1:]} == {"INCONNU"}
    assert page.erreurs_js == []


def test_health_en_panne_et_sante_lisible(page, serveur):  # noqa: F811
    ecran = _tableau(page, serveur, _sante(*SAIN).json(), statut_health=503)
    assert ecran["cartes"]["service"]["etat"] == "PROBLÈME" and "Que faire" in ecran["cartes"]["service"]["texte"]
    assert ecran["cartes"]["erreurs_techniques"]["etat"] == "SAIN"


@pytest.mark.parametrize("corps", ["ceci n'est pas du JSON", {"verdicts": {"refus_securite": {"etat": "bizarre"}}}])
def test_une_reponse_mal_formee_ne_casse_pas_la_page(page, serveur, corps):  # noqa: F811
    ecran = _tableau(page, serveur, corps)
    assert ecran["cartes"]["service"]["etat"] == "SAIN"
    assert ecran["cartes"]["refus_securite"]["etat"] == "INCONNU"
    assert page.erreurs_js == []


def test_une_cle_refusee_ramene_au_formulaire(page, serveur):  # noqa: F811
    ecran = _tableau(page, serveur, {"detail": "Cle d'API invalide ou absente"}, statut_sante=403, cle="mauvaise-cle")
    assert ecran["connexion_visible"] and "refusée" in ecran["resume"]
    assert page.evaluate("sessionStorage.getItem('rita_api_key')") is None


def test_sur_un_ecran_de_telephone_rien_ne_deborde(page, serveur):  # noqa: F811
    page.set_viewport_size({"width": 375, "height": 800})
    try:
        _tableau(page, serveur, _sante(*ATTAQUE).json())
        assert page.evaluate("document.documentElement.scrollWidth") <= 375
    finally:
        page.set_viewport_size({"width": 1280, "height": 720})


def test_pendant_le_chargement_le_bouton_est_bloque_et_un_seul_appel_part(page, serveur):  # noqa: F811
    # Revue du 22/10 : codé mais pas testé. La réponse de /sante est retenue le temps de vérifier que le bouton est
    # désactivé et qu'un second déclenchement (appel direct de la fonction, le bouton étant désactivé) ne part pas.
    corps = json.dumps(_sante(*SAIN).json())
    retenues, requetes = [], []

    def retenir(route):
        requetes.append(route.request.url)
        retenues.append(route)

    _tableau(page, serveur, _sante(*SAIN).json())          # premier affichage, normal
    page.route("**/health", lambda route: route.fulfill(status=200, content_type="application/json",
                                                        body='{"status": "ok"}'))
    page.route("**/sante", retenir)
    try:
        bouton = page.locator("#actualiser")
        bouton.click()
        attendre_que(page, "document.body.dataset.etat === 'chargement'")
        assert bouton.is_disabled() and bouton.inner_text() == "Actualisation…"
        page.evaluate("actualiser()")
        assert len(requetes) == 1
        for route in retenues:
            route.fulfill(status=200, content_type="application/json", body=corps)
        attendre_que(page, "document.body.dataset.etat === 'pret'")
        assert bouton.is_enabled() and bouton.inner_text() == "Actualiser"
        assert len(requetes) == 1
    finally:
        page.unroute("**/sante")
        page.unroute("**/health")


def test_pendant_un_exercice_le_bandeau_le_dit(page, serveur):  # noqa: F811
    sante = _sante(*SAIN).json()
    sante["exercice"] = {"nom": "Era", "motif": "répétition atelier 5", "depuis": "2026-10-22T16:05:00+02:00",
                         "fin_au_plus_tard": "2026-10-22T16:25:00+02:00"}
    _tableau(page, serveur, sante)
    bandeau = page.locator("#bandeau-exercice")
    assert bandeau.is_visible()
    texte = bandeau.inner_text()
    # Le navigateur affiche l'heure dans le fuseau de la machine : le test calcule la même, à Paris comme en UTC.
    depuis, fin = (datetime.fromisoformat(h).astimezone().strftime("%H:%M")
                   for h in ("2026-10-22T16:05:00+02:00", "2026-10-22T16:25:00+02:00"))
    assert f"Exercice de panne en cours depuis {depuis}" in texte and "Era" in texte and fin in texte


def test_sans_exercice_le_bandeau_est_cache(page, serveur):  # noqa: F811
    _tableau(page, serveur, _sante(*SAIN).json())
    assert not page.locator("#bandeau-exercice").is_visible()


def test_l_actualisation_automatique_se_suspend_et_reprend(page, serveur):  # noqa: F811
    """Critère T17, WCAG 2.2.2 (02/11/2026). Horloge simulée de Playwright, dans un contexte à part : les autres tests
    partagent la page du module et gardent l'heure réelle. On compte les vrais appels à `/sante`."""
    from playwright.sync_api import expect

    corps = json.dumps(_sante(*SAIN).json())
    appels = []

    def sante(route):
        appels.append(route.request.url)
        route.fulfill(status=200, content_type="application/json", body=corps)

    def attendre(n):
        for _ in range(100):
            if len(appels) >= n:
                break
            onglet.wait_for_timeout(50)
        expect(onglet.locator("body")).to_have_attribute("data-etat", "pret")

    contexte = page.context.browser.new_context()
    onglet = contexte.new_page()
    try:
        onglet.clock.install()
        onglet.route("**/sante", sante)
        onglet.route("**/health", lambda route: route.fulfill(status=200, content_type="application/json",
                                                              body='{"status": "ok"}'))
        onglet.goto(serveur + "/tableau-de-bord.html")
        onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE}')")
        onglet.goto(serveur + "/tableau-de-bord.html")
        attendre(1)
        assert len(appels) == 1

        onglet.clock.run_for(31_000)                  # témoin : sans pause, le tableau s'actualise seul
        attendre(2)
        assert len(appels) == 2

        bouton = onglet.locator("#suspendre")
        bouton.click()
        expect(bouton).to_have_attribute("aria-pressed", "true")
        assert "suspendue" in onglet.locator("#etat-actualisation").inner_text()
        onglet.clock.run_for(61_000)
        onglet.wait_for_timeout(300)
        assert len(appels) == 2, "suspendu : aucune actualisation automatique en une minute"

        onglet.locator("#actualiser").click()         # à la main : un appel, sans relancer l'automatique
        attendre(3)
        onglet.clock.run_for(61_000)
        onglet.wait_for_timeout(300)
        assert len(appels) == 3

        bouton.click()                                # reprise : un appel aussitôt, puis toutes les 30 secondes
        expect(bouton).to_have_attribute("aria-pressed", "false")
        attendre(4)
        onglet.clock.run_for(31_000)
        attendre(5)
        assert len(appels) == 5
    finally:
        contexte.close()

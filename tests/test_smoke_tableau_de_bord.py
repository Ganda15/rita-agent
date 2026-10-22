"""Sprint 5, étape 5 : le tableau de bord dans un vrai navigateur (grille, critère 2 : « compris sans explication »).

Le même dispositif que `tests/test_smoke_ui.py` : l'API servie par uvicorn, Chrome piloté par Playwright. `/sante` et
`/health` sont remplacés par des réponses fabriquées, une par état ; elles sont construites par le vrai code
(`api.sante.construire`, aides de `tests/test_vigie.py`), donc elles suivent le contrat réel. Aucune attente fixe :
chaque test attend que la page dise elle-même qu'elle a fini (`document.body.dataset.etat === "pret"`).
"""
import json

import pytest

from tests.test_smoke_ui import page, serveur  # noqa: F401, ce sont des fixtures
from tests.test_vigie import ATTAQUE, SAIN, _sante

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
        page.wait_for_function("document.body.dataset.etat === 'pret'", timeout=10_000)
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
        page.wait_for_function("document.body.dataset.etat === 'chargement'")
        assert bouton.is_disabled() and bouton.inner_text() == "Actualisation…"
        page.evaluate("actualiser()")
        assert len(requetes) == 1
        for route in retenues:
            route.fulfill(status=200, content_type="application/json", body=corps)
        page.wait_for_function("document.body.dataset.etat === 'pret'")
        assert bouton.is_enabled() and bouton.inner_text() == "Actualiser"
        assert len(requetes) == 1
    finally:
        page.unroute("**/sante")
        page.unroute("**/health")

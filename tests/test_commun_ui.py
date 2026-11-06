"""Refonte 001, tâche 5 (exigences R5 et R7) : `commun.js`, ce que les cinq écrans partagent, et le mode simulation.

`window.RITA` porte la clé (gardée seulement après une réponse réussie, oubliée sur 401 ou 403 : correctif #73) et le
mode simulation (choix explicite par le bouton « Mode simulation » de l'en-tête, le réel par défaut). En simulation,
aucun écran n'appelle RITA : un écran sans données d'exemple se suspend (décision D1) et `commun.js` bloque en plus tout
appel vers une route de RITA. Changer de mode recharge la page : les résultats affichés disparaissent dans les deux sens.
"""
import os
import re
from urllib.parse import urlparse
from pathlib import Path

import pytest

from tests.test_frontend import code_sans_commentaires
from tests.test_smoke_ui import serveur  # noqa: F401  (fixture : l'API servie en local)
from tests.attente import attendre_que  # noqa: E402  (06/11 : la politique de contenu refuse wait_for_function)

sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
ECRANS = {"index.html": "app.js", "indicateurs.html": "indicateurs.js", "briefing.html": "briefing.js",
          "question.html": "question.js", "tableau-de-bord.html": "tableau-de-bord.js"}
CLE_SERVEUR = "cle-de-test-smoke-ui-32-caracteres-x"   # tests/test_smoke_ui.py, fixture `serveur`
MENTION = "Simulation : données d'exemple, aucun modèle appelé"
ROUTES_RITA = ("/briefing", "/question", "/donnees", "/sante", "/health", "/audit", "/exercice")
REPONSE = {"statut": "reponse", "texte": "Netflix supprime 2 000 postes [1].", "index": {"empreinte": "abc"},
           "references": [{"n": 1, "titre": "Netflix réduit ses effectifs", "source": "Les Échos", "table": "article",
                           "id": 42, "date": "2026-10-28", "lien": "https://www.lesechos.fr/"}]}   # test_recette_clavier.py


# --- le fichier et les pages, sans navigateur -----------------------------------------------------------------------------

@pytest.mark.parametrize("fichier, script", ECRANS.items())
def test_chaque_page_charge_commun_js_avant_son_script(fichier, script):
    page = (FRONTEND / fichier).read_text(encoding="utf-8")
    # 04/11/2026 : chaque adresse porte sa version (`commun.js?v=...`) ; tests/test_interface_versionnee.py la contrôle.
    def balise(nom):
        return re.search(rf'<script src="{re.escape(nom)}(\?v=[0-9a-f]+)?"></script>', page)
    assert balise("commun.js"), fichier
    assert balise("commun.js").start() < balise(script).start(), fichier


@pytest.mark.parametrize("fichier", ECRANS)
def test_bouton_simulation_dans_l_en_tete(fichier):
    entete = re.search(r"<header\b.*?</header>", (FRONTEND / fichier).read_text(encoding="utf-8"), re.S).group(0)
    bouton = re.search(r'<button\b[^>]*\bid="bascule-simulation"[^>]*>([^<]*)</button>', entete)
    assert bouton, fichier
    assert 'type="button"' in bouton.group(0) and " hidden" in bouton.group(0) and 'aria-pressed="false"' in bouton.group(0)
    assert bouton.group(1) == "Mode simulation"


def test_commun_js_sans_localstorage_ni_html_insere():
    code = code_sans_commentaires("commun.js")
    assert "sessionStorage" in code and "localStorage" not in code
    for interdit in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write"):
        assert interdit not in code, interdit


# --- dans un vrai navigateur ------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def navigateur():
    with sync_playwright() as p:
        canal = {} if os.environ.get("CI") else {"channel": "chrome"}
        nav = p.chromium.launch(headless=True, **canal)
        yield nav
        nav.close()


@pytest.fixture
def onglet(navigateur):
    contexte = navigateur.new_context()
    page = contexte.new_page()
    page.erreurs_js = []
    page.on("pageerror", lambda e: page.erreurs_js.append(str(e)))
    yield page
    contexte.close()


def appels_rita(adresses, routes=ROUTES_RITA):
    """Les adresses qui sont des routes de RITA : le chemin exact, ou suivi de « / ». Une page (`question.html`) ou un
    script (`question.js`) n'en est pas une, même si son nom commence pareil."""
    return [a for a in adresses
            if any(urlparse(a).path == r or urlparse(a).path.startswith(r + "/") for r in routes)]


def test_le_filtre_des_appels_ne_confond_pas_page_et_route():
    adresses = ["http://h/question.html", "http://h/question.js", "http://h/question", "http://h/donnees/articles/42",
                "http://h/sante", "http://h/style.css"]
    assert appels_rita(adresses) == ["http://h/question", "http://h/donnees/articles/42", "http://h/sante"]


def _cle(page):
    return page.evaluate("sessionStorage.getItem('rita_api_key')")


def test_cle_gardee_seulement_apres_succes(onglet, serveur):  # noqa: F811
    onglet.route("**/donnees/fraicheur", lambda r: r.fulfill(status=500, body="{}"))
    onglet.goto(serveur + "/question.html")
    onglet.evaluate("sessionStorage.removeItem('rita_api_key')")
    statut = onglet.evaluate("RITA.appeler('/donnees/fraicheur', {cle: 'cle-en-essai-0123456789'}).then(r => r.status)")
    assert statut == 500 and _cle(onglet) is None, "une réponse en échec ne garde pas la clé"
    onglet.unroute("**/donnees/fraicheur")
    onglet.route("**/donnees/fraicheur", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    onglet.evaluate("RITA.appeler('/donnees/fraicheur', {cle: 'cle-en-essai-0123456789'})")
    assert _cle(onglet) == "cle-en-essai-0123456789", "la clé est gardée après une réponse réussie"


@pytest.mark.parametrize("code", [401, 403])
def test_cle_oubliee_sur_403(onglet, serveur, code):  # noqa: F811
    onglet.route("**/donnees/fraicheur", lambda r: r.fulfill(status=code, body="{}"))
    onglet.goto(serveur + "/question.html")
    onglet.evaluate("sessionStorage.setItem('rita_api_key', 'cle-perimee-0123456789')")
    onglet.evaluate("RITA.appeler('/donnees/fraicheur')")
    assert _cle(onglet) is None


def test_mode_reel_par_defaut(onglet, serveur):  # noqa: F811
    onglet.goto(serveur + "/index.html")
    assert onglet.evaluate("RITA.estSimulation()") is False
    assert onglet.locator("#mention-simulation").count() == 0
    bouton = onglet.locator("#bascule-simulation")
    assert bouton.is_visible() and bouton.get_attribute("aria-pressed") == "false"


@pytest.mark.parametrize("fichier", ECRANS)
def test_mention_simulation_visible_sur_chaque_ecran(onglet, serveur, fichier):  # noqa: F811
    onglet.goto(serveur + "/" + fichier)
    onglet.evaluate("sessionStorage.setItem('rita_simulation', 'oui')")
    onglet.goto(serveur + "/" + fichier)
    mention = onglet.locator("#mention-simulation")
    assert mention.is_visible() and mention.inner_text() == MENTION
    assert onglet.locator("#bascule-simulation").get_attribute("aria-pressed") == "true"
    assert onglet.erreurs_js == []


def test_le_bouton_de_l_en_tete_active_la_simulation(onglet, serveur):  # noqa: F811
    onglet.goto(serveur + "/index.html")
    onglet.locator("#bascule-simulation").click()
    onglet.wait_for_selector("#mention-simulation")
    assert onglet.evaluate("RITA.estSimulation()") is True


def test_simulation_bloque_les_routes_de_rita(onglet, serveur):  # noqa: F811
    """Deuxième barrière : même un appel oublié par un écran ne part pas vers RITA sous la mention « Simulation »."""
    onglet.goto(serveur + "/index.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_SERVEUR}'); sessionStorage.setItem('rita_simulation', 'oui')")
    vues = []
    onglet.on("request", lambda r: vues.append(r.url))
    onglet.goto(serveur + "/index.html")
    for route in ("/donnees/valeurs?limite=5", "/briefing?ticker=MC.PA", "/question", "/sante", "/health"):
        refus = onglet.evaluate(f"fetch('{route}').then(() => 'parti', e => e.message)")
        assert refus.startswith("Simulation"), (route, refus)
    assert appels_rita(vues) == [], vues


def test_question_et_tableau_suspendus_en_simulation(onglet, serveur):  # noqa: F811
    onglet.clock.install()
    onglet.goto(serveur + "/question.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_SERVEUR}'); sessionStorage.setItem('rita_simulation', 'oui')")
    vues = []
    onglet.on("request", lambda r: vues.append(r.url))
    for fichier, cache in (("question.html", "#form-question"), ("tableau-de-bord.html", "#tableau")):
        onglet.goto(serveur + "/" + fichier)
        assert onglet.locator("#suspension").is_visible(), fichier
        assert "Simulation non disponible pour cet écran" in onglet.locator("#suspension").inner_text()
        assert onglet.locator("#quitter-simulation").is_visible()
        assert not onglet.locator(cache).is_visible(), f"{fichier} : rien de réel sous la mention"
        # Envoi au clavier ou par programme : bloqué, aucune navigation.
        adresse = onglet.url
        onglet.evaluate("document.querySelectorAll('form').forEach(f => f.requestSubmit())")
        onglet.clock.run_for(61_000)   # deux périodes d'actualisation du tableau de bord
        assert onglet.url == adresse
    assert appels_rita(vues, ("/question", "/sante", "/health", "/donnees")) == [], vues
    assert onglet.erreurs_js == []


def test_quitter_la_simulation_rend_le_mode_reel(onglet, serveur):  # noqa: F811
    onglet.goto(serveur + "/question.html")
    onglet.evaluate("sessionStorage.setItem('rita_simulation', 'oui')")
    onglet.goto(serveur + "/question.html")
    onglet.locator("#quitter-simulation").click()
    onglet.wait_for_selector("#suspension", state="detached")
    assert onglet.evaluate("RITA.estSimulation()") is False
    assert onglet.locator("#mention-simulation").count() == 0
    assert onglet.locator("#connexion").is_visible() or onglet.locator("#demande").is_visible()


def test_bascule_efface_les_resultats(onglet, serveur):  # noqa: F811
    """Dans les deux sens : un résultat réel disparaît en passant en simulation, et rien ne réapparaît en revenant."""
    import json
    onglet.route("**/question", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(REPONSE)))
    onglet.goto(serveur + "/question.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_SERVEUR}')")
    onglet.goto(serveur + "/question.html")
    onglet.fill("#question", "Que fait Netflix ?")
    onglet.locator("#form-question button[type=submit]").click()
    onglet.wait_for_selector("#resultat:not([hidden])")
    assert "Netflix supprime" in onglet.locator("#resultat").inner_text()
    onglet.locator("#bascule-simulation").click()              # réel vers simulation
    onglet.wait_for_selector("#suspension")
    assert not onglet.locator("#resultat").is_visible()
    onglet.locator("#quitter-simulation").click()              # simulation vers réel
    onglet.wait_for_selector("#suspension", state="detached")
    assert not onglet.locator("#resultat").is_visible(), "l'ancien résultat ne revient pas"


def test_navigation_des_cinq_pages_avec_une_cle_gardee(onglet, serveur):  # noqa: F811
    onglet.goto(serveur + "/index.html")
    onglet.evaluate(f"sessionStorage.setItem('rita_api_key', '{CLE_SERVEUR}')")
    for fichier in ECRANS:
        onglet.goto(serveur + "/" + fichier)
        assert onglet.evaluate("typeof window.RITA") == "object", fichier
        assert onglet.evaluate("RITA.lireCle()") == CLE_SERVEUR, f"{fichier} : la clé est perdue"
    assert onglet.erreurs_js == []


def test_une_cle_refusee_n_est_pas_regardee_par_un_appel_parallele(onglet, serveur):  # noqa: F811
    """Trouvé par la recette du 02/11 rejouée le 04/11 : deux appels partent ensemble avec la même clé ; l'un est refusé
    (403), l'autre réussit. Sans garde, le succès arrivé après le refus regardait la clé refusée. Une clé refusée une
    fois n'est plus jamais gardée dans la page, quel que soit l'ordre des réponses."""
    onglet.route("**/donnees/indicateurs", lambda r: r.fulfill(status=403, body="{}"))
    onglet.route("**/donnees/fraicheur", lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    onglet.goto(serveur + "/question.html")
    onglet.evaluate("sessionStorage.removeItem('rita_api_key')")
    onglet.evaluate("""async () => {
        const cle = 'cle-en-essai-0123456789';
        await RITA.appeler('/donnees/indicateurs', {cle});   // refusée d'abord
        await RITA.appeler('/donnees/fraicheur', {cle});     // puis un succès avec la même clé
    }""")
    assert _cle(onglet) is None


# --- 04/11/2026 : Précédent ou Suivant après un changement de mode (trouvaille P2 de la revue de la PR #180) --------------
#
# Le navigateur peut rendre une page depuis son cache d'aller-retour, telle qu'on l'a quittée, sans relancer ses scripts :
# la barrière contre les appels à RITA reste celle posée au chargement. Une page quittée en mode réel puis rendue après
# une bascule en simulation sur un autre écran laissait partir des appels réels ; une page quittée en simulation puis
# rendue après un retour au réel les bloquait. Ces tests passent par un VRAI Précédent ou Suivant : Playwright coupe ce
# cache par défaut (`--disable-back-forward-cache`) et on le rétablit. Mesuré le 04/11 : sans ce réglage, Précédent
# recharge la page ; avec, la page est rendue telle quelle et reçoit `pageshow` avec `persisted`.

PAGE_TEMOIN = "<!doctype html><meta charset='utf-8'><title>Témoin {}</title><p>Page témoin {}, sans script.</p>"


@pytest.fixture(scope="module")
def site_temoin(tmp_path_factory):
    """Deux pages minimales, sans script, servies par un petit serveur à part : la sonde du cache ne dépend pas de RITA.
    Relecture de la PR #182 (04/11/2026) : sondée sur `briefing.html`, une régression de `commun.js` qui recharge la page
    faisait conclure « cache absent » et sauter les huit tests faits pour l'attraper (démontré par une régression simulée)."""
    import functools
    import http.server
    import threading
    dossier = tmp_path_factory.mktemp("temoin")
    for nom in ("a", "b"):
        (dossier / f"temoin-{nom}.html").write_text(PAGE_TEMOIN.format(nom, nom), encoding="utf-8")
    gestion = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(dossier))
    gestion.log_message = lambda *a, **k: None
    serveur_temoin = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestion)
    fil = threading.Thread(target=serveur_temoin.serve_forever, daemon=True)
    fil.start()
    yield f"http://127.0.0.1:{serveur_temoin.server_address[1]}"
    serveur_temoin.shutdown()


def _le_cache_joue(nav, adresse_temoin):
    """Sonde sur la page témoin : une marque posée survit-elle à Précédent ? Sinon, la page a été rechargée, pas rendue."""
    contexte = nav.new_context()
    page = contexte.new_page()
    page.goto(adresse_temoin + "/temoin-a.html")
    page.evaluate("window.__sonde = 'cache'")
    page.goto(adresse_temoin + "/temoin-b.html")
    page.go_back(wait_until="commit")
    page.wait_for_timeout(1000)
    garde = page.evaluate("window.__sonde || null") == "cache"
    contexte.close()
    return garde


def choisir_navigateur(lancer, canaux, cache_joue):
    """Le premier canal qui se lance ET où le cache joue ; rend (navigateur ou None, raisons des canaux écartés).

    Un échec de lancement n'est jamais pris pour une simple absence de cache : sa cause est gardée, et si AUCUN navigateur
    ne se lance, c'est une erreur (une installation cassée doit faire échouer la suite, pas la faire sauter)."""
    raisons, un_navigateur_lance = [], False
    for canal in canaux:
        nom = canal.get("channel", "chromium par défaut")
        try:
            nav = lancer(canal)
        except Exception as erreur:
            premiere_ligne = (str(erreur).splitlines() or [""])[0][:160]
            raisons.append(f"{nom} : lancement impossible ({type(erreur).__name__} : {premiere_ligne})")
            continue
        un_navigateur_lance = True
        if cache_joue(nav):
            return nav, raisons
        nav.close()
        raisons.append(f"{nom} : lancé, mais le cache d'aller-retour ne joue pas sur la page témoin")
    if not un_navigateur_lance:
        raise RuntimeError("aucun navigateur ne s'est lancé : " + " ; ".join(raisons))
    return None, raisons


@pytest.fixture(scope="module")
def navigateur_avec_cache(navigateur, site_temoin):
    """Le même Playwright que `navigateur` (deux instances synchrones ne peuvent pas cohabiter), le cache rétabli.

    Dans la CI : on essaie d'abord le Chromium complet (canal `chromium`), car le « headless shell » par défaut ne rend
    aucune page depuis ce cache ; en local, le Chrome installé (canal `chrome`). La sonde se fait sur la page témoin. Les
    huit tests, eux, restent sur les vraies pages de RITA : si le cache joue sur le témoin et que RITA recharge à tort,
    ils échouent. Saut seulement si un navigateur se lance mais que le cache ne joue pas sur le témoin, avec ses raisons.
    """
    canaux = [{"channel": "chromium"}, {}] if os.environ.get("CI") else [{"channel": "chrome"}]

    def lancer(canal):
        return navigateur.browser_type.launch(headless=True, ignore_default_args=["--disable-back-forward-cache"],
                                              **canal)
    try:
        nav, raisons = choisir_navigateur(lancer, canaux, lambda n: _le_cache_joue(n, site_temoin))
    except RuntimeError as erreur:
        pytest.fail(str(erreur))
    if nav is None:
        pytest.skip("cache d'aller-retour indisponible : " + " ; ".join(raisons))
    yield nav
    nav.close()


@pytest.fixture
def onglet_avec_cache(navigateur_avec_cache):
    contexte = navigateur_avec_cache.new_context()
    page = contexte.new_page()
    page.erreurs_js = []
    page.on("pageerror", lambda e: page.erreurs_js.append(str(e)))
    page.chargements = []
    page.on("load", lambda: page.chargements.append(page.url))
    page.vues = []
    page.on("request", lambda r: page.vues.append(r.url))
    yield page
    contexte.close()


def _poser_le_mode(page, serveur, mode):
    page.goto(serveur + "/index.html")
    page.evaluate("sessionStorage.setItem('rita_simulation', 'oui')" if mode == "simulation"
                  else "sessionStorage.removeItem('rita_simulation')")


def _basculer(page):
    with page.expect_navigation():
        page.locator("#bascule-simulation").click()


def _attendre_la_page(page):
    """Une page rendue par le cache n'émet pas `load` : `wait_for_load_state` l'attendrait sans fin (constaté le 04/11).
    On laisse le temps d'un éventuel rechargement, puis on attend que le document affiché soit complet."""
    page.wait_for_timeout(1500)
    attendre_que(page, "document.readyState === 'complete'")


def _revenir(page, sens):
    """Précédent ou Suivant, en attendant seulement l'engagement de la navigation."""
    page.chargements.clear()
    page.vues.clear()
    (page.go_back if sens == "precedent" else page.go_forward)(wait_until="commit")
    _attendre_la_page(page)


def _scenario(page, serveur, sens, depart, changer=True):
    """La page A (briefing) est quittée dans le mode `depart` ; le mode change ou non sur la page B (index) ; on revient
    sur A par Précédent ou Suivant."""
    _poser_le_mode(page, serveur, depart)
    if sens == "precedent":
        page.goto(serveur + "/briefing.html")
        page.evaluate("window.__marque = 'cache'")
        page.goto(serveur + "/index.html")
        if changer:
            _basculer(page)
    else:
        page.goto(serveur + "/index.html")
        page.goto(serveur + "/briefing.html")
        page.evaluate("window.__marque = 'cache'")
        page.go_back(wait_until="commit")
        _attendre_la_page(page)
        if changer:
            _basculer(page)
    _revenir(page, sens)
    assert page.url.endswith("/briefing.html"), page.url


def _appel(page, route="/health"):
    return page.evaluate(f"fetch('{route}').then(r => 'parti ' + r.status, e => e.message)")


@pytest.mark.parametrize("sens", ["precedent", "suivant"])
def test_reel_puis_simulation_ailleurs_aucun_appel_reel_au_retour(onglet_avec_cache, serveur, sens):  # noqa: F811
    page = onglet_avec_cache
    _scenario(page, serveur, sens, "reel")
    assert page.evaluate("RITA.estSimulation()") is True
    assert _appel(page).startswith("Simulation"), "en simulation, la barrière doit refuser l'appel"
    assert appels_rita(page.vues) == [], page.vues
    assert page.locator("#mention-simulation").count() == 1
    assert page.erreurs_js == []


@pytest.mark.parametrize("sens", ["precedent", "suivant"])
def test_simulation_puis_reel_ailleurs_les_appels_repartent_au_retour(onglet_avec_cache, serveur, sens):  # noqa: F811
    page = onglet_avec_cache
    _scenario(page, serveur, sens, "simulation")
    assert page.evaluate("RITA.estSimulation()") is False
    assert page.locator("#mention-simulation").count() == 0
    assert _appel(page) == "parti 200", "en mode réel, l'appel doit partir de nouveau"
    assert any(a.endswith("/health") for a in page.vues), page.vues
    assert page.erreurs_js == []


@pytest.mark.parametrize("depart", ["reel", "simulation"])
def test_un_changement_de_mode_recharge_une_seule_fois(onglet_avec_cache, serveur, depart):  # noqa: F811
    """Aucune boucle : un seul rechargement au retour, puis plus rien."""
    page = onglet_avec_cache
    _scenario(page, serveur, "precedent", depart)
    page.wait_for_timeout(1500)
    assert len(page.chargements) == 1, page.chargements
    assert page.evaluate("window.__marque || null") is None, "la page a bien été rechargée"


@pytest.mark.parametrize("sens", ["precedent", "suivant"])
def test_sans_changement_de_mode_la_page_rendue_par_le_cache_est_gardee(onglet_avec_cache, serveur, sens):  # noqa: F811
    """Témoin : sans bascule, la page revient du cache telle quelle, sans rechargement. Il prouve aussi que le cache
    d'aller-retour joue bien dans ces tests (sans lui, les tests ci-dessus passeraient sans rien prouver)."""
    page = onglet_avec_cache
    _scenario(page, serveur, sens, "reel", changer=False)
    page.wait_for_timeout(1000)
    assert page.evaluate("window.__marque || null") == "cache"
    assert page.chargements == []


# --- 04/11/2026 : le choix du navigateur des tests du cache, testé sans navigateur (relecture de la PR #182) -------------

class _FauxNavigateur:
    def __init__(self, nom, cache):
        self.nom, self.cache, self.ferme = nom, cache, False

    def close(self):
        self.ferme = True


def test_aucun_navigateur_lance_est_un_echec_avec_sa_cause():
    def lancer(canal):
        raise RuntimeError("Executable doesn't exist at /chemin/chrome")
    with pytest.raises(RuntimeError, match="aucun navigateur ne s'est lancé.*Executable doesn't exist"):
        choisir_navigateur(lancer, [{"channel": "chromium"}, {}], lambda nav: True)


def test_un_navigateur_lance_sans_cache_rend_ses_raisons_et_se_ferme():
    lances = []

    def lancer(canal):
        lances.append(_FauxNavigateur(canal.get("channel"), cache=False))
        return lances[-1]
    nav, raisons = choisir_navigateur(lancer, [{"channel": "chromium"}], lambda n: n.cache)
    assert nav is None
    assert raisons == ["chromium : lancé, mais le cache d'aller-retour ne joue pas sur la page témoin"]
    assert lances[0].ferme


def test_le_premier_canal_qui_marche_est_garde_et_l_echec_precedent_est_dit():
    def lancer(canal):
        if canal.get("channel") == "chromium":
            raise RuntimeError("navigateur complet absent")
        return _FauxNavigateur("defaut", cache=True)
    nav, raisons = choisir_navigateur(lancer, [{"channel": "chromium"}, {}], lambda n: n.cache)
    assert nav.nom == "defaut" and not nav.ferme
    assert raisons == ["chromium : lancement impossible (RuntimeError : navigateur complet absent)"]

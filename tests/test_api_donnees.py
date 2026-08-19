"""Tests de l'API de mise à disposition du jeu de données (C5) — base simulée.

Le critère central de C5 est **« l'API restreint par une autorisation l'accès aux
données »**. C'est donc la première chose testée, et sur *chaque* point de terminaison :
un contrôle d'accès qui protège 5 routes sur 6 ne protège rien.
"""
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from sources.database import Extraction

from tests.conftest import CLE_DE_TEST

CLE = {"X-API-Key": CLE_DE_TEST}

ROUTES_PROTEGEES = [
    "/donnees/valeurs",
    "/donnees/cotations?ticker=MC.PA",
    "/donnees/portefeuille",
    "/donnees/mouvements",
    "/donnees/volumes-anormaux",
    "/donnees/articles",
    "/donnees/indicateurs",
    "/donnees/indicateurs-portefeuille",
    "/donnees/indicateurs-risque",
]


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def base_simulee():
    """Remplace toute lecture de base par un jeu figé."""
    def faux(sql, nom, dsn=None, **params):
        return Extraction(nom=nom, lignes=[{"ticker": "MC.PA", "cloture": 466.80}], nb=1)

    with patch("sources.database._executer", side_effect=faux):
        yield


# --- le critère central : l'autorisation --------------------------------------

@pytest.mark.parametrize("route", ROUTES_PROTEGEES)
def test_sans_cle_l_acces_est_refuse(client, route):
    assert client.get(route).status_code == 403


@pytest.mark.parametrize("route", ROUTES_PROTEGEES)
def test_avec_mauvaise_cle_l_acces_est_refuse(client, route):
    assert client.get(route, headers={"X-API-Key": "pas-la-bonne"}).status_code == 403


def test_health_reste_public(client):
    """Le seul point non protégé — il ne révèle aucune donnée."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["project"] == "RITA"


def test_toute_route_donnees_est_protegee(client):
    """Garde-fou de conception : la dépendance est posée sur le routeur entier,
    donc un nouveau point de terminaison ne peut pas naître non protégé."""
    ouvertes = [r.path for r in app.routes
                if getattr(r, "path", "").startswith("/donnees")
                and client.get(r.path.replace("{ticker}", "X")).status_code != 403]
    assert ouvertes == []


# --- fonctionnement -----------------------------------------------------------

def test_valeurs_retourne_le_compte(client, base_simulee):
    r = client.get("/donnees/valeurs", headers=CLE)
    assert r.status_code == 200 and r.json()["nb"] == 1


def test_cotations_exige_un_ticker(client):
    """Sans ticker, la requête balaierait 273 611 lignes — 422 côté FastAPI."""
    assert client.get("/donnees/cotations", headers=CLE).status_code == 422


def test_cotations_ticker_inconnu_renvoie_404(client):
    vide = Extraction(nom="cotations", lignes=[], nb=0)
    with patch("sources.database._executer", return_value=vide):
        r = client.get("/donnees/cotations?ticker=NEXISTEPAS", headers=CLE)
    assert r.status_code == 404


def test_portefeuille_expose_le_total_en_euros(client):
    lignes = [{"valorisation_eur": 1000}, {"valorisation_eur": 500}]
    with patch("sources.database.portefeuille",
               return_value=Extraction("portefeuille", lignes, 2)):
        r = client.get("/donnees/portefeuille", headers=CLE)
    assert r.json()["total_eur"] == 1500


# --- garde-fous de conception -------------------------------------------------

@pytest.mark.parametrize("route, borne", [
    ("/donnees/valeurs?limite=99999", 422),
    ("/donnees/cotations?ticker=MC.PA&limite=99999", 422),
    ("/donnees/mouvements?limite=999", 422),
])
def test_la_limite_est_plafonnee_cote_serveur(client, route, borne):
    """Un client ne doit pas pouvoir demander 273 611 lignes."""
    assert client.get(route, headers=CLE).status_code == borne


def test_les_articles_bloques_ne_sortent_jamais(client):
    """`bloque_injection = FALSE` est codé en dur, pas paramétrable."""
    captures = {}

    def capturer(sql, nom, dsn=None, **params):
        captures["sql"] = sql
        return Extraction(nom, [], 0)

    with patch("sources.database._executer", side_effect=capturer):
        client.get("/donnees/articles", headers=CLE)

    assert "bloque_injection = FALSE" in captures["sql"]


# --- contrat OpenAPI (critère « standards du modèle choisi ») ------------------

def test_openapi_est_genere_et_complet(client):
    o = client.get("/openapi.json").json()
    assert o["openapi"].startswith("3.")
    for route in ("/donnees/valeurs", "/donnees/portefeuille", "/donnees/cotations",
                  "/donnees/mouvements", "/donnees/volumes-anormaux",
                  "/donnees/articles", "/donnees/indicateurs",
                  "/donnees/indicateurs-portefeuille", "/donnees/indicateurs-risque",
                  "/briefing", "/health"):
        assert route in o["paths"], f"{route} absent du contrat OpenAPI"


def test_chaque_route_a_un_resume_documente(client):
    """Critère C5 : « la documentation couvre TOUS les points de terminaison »."""
    o = client.get("/openapi.json").json()
    sans_resume = [chemin for chemin, methodes in o["paths"].items()
                   for m in methodes.values() if not m.get("summary")]
    assert sans_resume == []


def test_le_schema_de_securite_est_declare(client):
    """L'authentification doit apparaître dans le contrat, pas seulement dans le code."""
    o = client.get("/openapi.json").json()
    schemas = o.get("components", {}).get("securitySchemes", {})
    assert any(s.get("name") == "X-API-Key" for s in schemas.values())


# --- /donnees/indicateurs (lot 1) ---------------------------------------------

def _ligne_indicateur(**surcharges):
    """Une ligne telle que `db/indicateurs.sql` la rend."""
    base = {
        "ticker": "MC.PA", "nom_officiel": "LVMH", "statut_qualite": "OK",
        "date_cours": date(2026, 8, 18), "cours": Decimal("545.2000"),
        "fraicheur_jours": 0,
        "perf_1j_pct": Decimal("-1.10"), "perf_1s_pct": Decimal("2.40"),
        "perf_1m_pct": Decimal("-3.80"), "perf_ytd_pct": Decimal("5.20"),
        "perf_1a_pct": Decimal("-11.10"),
        "ma20": Decimal("552.3000"), "ma50": Decimal("561.9000"),
        "adtv20": Decimal("128456789"),
        "distance_plus_haut_1a_pct": Decimal("-14.20"),
    }
    base.update(surcharges)
    return base


@pytest.fixture
def indicateurs_simules():
    """Deux valeurs : une fraîche, une radiée depuis 2018."""
    lignes = [
        _ligne_indicateur(),
        _ligne_indicateur(ticker="ZC.PA", nom_officiel="ZODIAC AEROSPACE",
                          statut_qualite="OK", date_cours=date(2018, 3, 22),
                          fraicheur_jours=3071, perf_1a_pct=None, ma50=None),
    ]
    with patch("indicateurs.socle._executer", return_value=lignes):
        yield


def test_indicateurs_retourne_le_compte_et_le_seuil(client, indicateurs_simules):
    r = client.get("/donnees/indicateurs", headers=CLE)
    assert r.status_code == 200
    d = r.json()
    assert d["nb"] == 2
    assert d["seuil_perime_jours"] == 40
    assert [i["ticker"] for i in d["indicateurs"]] == ["MC.PA", "ZC.PA"]


def test_une_valeur_radiee_sort_signalee_et_non_masquee(client, indicateurs_simules):
    """LE test qui compte. Zodiac est radiée depuis 2018 et porte `statut_qualite = OK`.
    L'API la renvoie — avec le drapeau. On montre le chiffre, on signale le doute."""
    d = client.get("/donnees/indicateurs", headers=CLE).json()
    zodiac = next(i for i in d["indicateurs"] if i["ticker"] == "ZC.PA")

    assert zodiac["statut_qualite"] == "OK"        # le statut ne dit rien de la fraîcheur
    assert zodiac["cotation_perimee"] is True      # le drapeau, lui, le dit
    assert d["nb_perimees"] == 1


def test_masquer_perimees_les_ecarte(client, indicateurs_simules):
    d = client.get("/donnees/indicateurs?masquer_perimees=true", headers=CLE).json()
    assert d["nb"] == 1
    assert d["nb_perimees"] == 0
    assert [i["ticker"] for i in d["indicateurs"]] == ["MC.PA"]


def test_un_historique_court_sort_en_null_et_non_en_zero(client, indicateurs_simules):
    """`null` signifie « pas calculable », `0` signifierait « aucune variation ».
    Confondre les deux ferait afficher une performance nulle là où il n'y en a pas."""
    d = client.get("/donnees/indicateurs", headers=CLE).json()
    zodiac = next(i for i in d["indicateurs"] if i["ticker"] == "ZC.PA")
    assert zodiac["perf_1a_pct"] is None
    assert zodiac["ma50"] is None


def test_le_filtre_par_ticker_est_repetable(client):
    """`?ticker=A&ticker=B` — la liste doit arriver entière jusqu'à la requête."""
    vu = {}

    def espion(tickers=None):
        vu["tickers"] = tickers
        return []

    with patch("indicateurs.socle.lire_socle", side_effect=espion):
        r = client.get("/donnees/indicateurs?ticker=MC.PA&ticker=OR.PA", headers=CLE)

    assert r.status_code == 200
    assert vu["tickers"] == ["MC.PA", "OR.PA"]


def test_sans_ticker_aucun_filtre_n_est_transmis(client):
    """Une liste vide et « pas de filtre » ne sont pas la même chose : la première
    ne renverrait rien du tout."""
    vu = {}

    def espion(tickers=None):
        vu["tickers"] = tickers
        return []

    with patch("indicateurs.socle.lire_socle", side_effect=espion):
        client.get("/donnees/indicateurs", headers=CLE)

    assert vu["tickers"] is None


def test_les_decimal_sortent_en_json_natif(client, indicateurs_simules):
    """Un `Decimal` n'est pas sérialisable en JSON. La conversion doit avoir lieu
    avant la réponse, pas dans un encodeur de dernière minute."""
    d = client.get("/donnees/indicateurs", headers=CLE).json()
    lvmh = d["indicateurs"][0]
    assert isinstance(lvmh["cours"], float)
    assert isinstance(lvmh["ma20"], float)
    assert lvmh["date_cours"] == "2026-08-18"


# --- /donnees/indicateurs-portefeuille (lot 2) --------------------------------

@pytest.fixture
def portefeuille_simule():
    """Deux lignes, deux devises — le cas que les données réelles n'exercent pas :
    les 7 positions d'Era sont toutes en euros."""
    poids = [
        {"ticker": "MC.PA", "nom_officiel": "LVMH", "devise": "EUR",
         "quantite": Decimal("12"), "valorisation_eur": Decimal("3000.00"),
         "poids_pct": Decimal("75.00"), "total_eur": Decimal("4000.00")},
        {"ticker": "AAPL", "nom_officiel": "APPLE", "devise": "USD",
         "quantite": Decimal("5"), "valorisation_eur": Decimal("1000.00"),
         "poids_pct": Decimal("25.00"), "total_eur": Decimal("4000.00")},
    ]
    exposition = [
        {"devise": "EUR", "nb_lignes": 1, "valorisation_eur": Decimal("3000.00"),
         "exposition_pct": Decimal("75.00")},
        {"devise": "USD", "nb_lignes": 1, "valorisation_eur": Decimal("1000.00"),
         "exposition_pct": Decimal("25.00")},
    ]
    appels = {"n": 0}

    def faux(sql, parametres=None):
        # La route appelle les deux requêtes : poids d'abord, exposition ensuite.
        appels["n"] += 1
        return poids if appels["n"] == 1 else exposition

    with patch("indicateurs.socle._executer", side_effect=faux):
        yield


def test_le_poids_et_l_exposition_sortent_ensemble(client, portefeuille_simule):
    """Un seul appel rend les deux : l'écran en a besoin en même temps, et deux
    allers-retours pour une même vue seraient du gaspillage."""
    r = client.get("/donnees/indicateurs-portefeuille", headers=CLE)
    assert r.status_code == 200
    d = r.json()
    assert d["nb"] == 2
    assert d["total_eur"] == 4000.00
    assert [l["ticker"] for l in d["lignes"]] == ["MC.PA", "AAPL"]
    assert {e["devise"]: e["exposition_pct"] for e in d["exposition"]} == {"EUR": 75.0, "USD": 25.0}


def test_la_somme_des_poids_fait_cent(client, portefeuille_simule):
    """Le contrôle que la spécification demande explicitement (§6.1)."""
    d = client.get("/donnees/indicateurs-portefeuille", headers=CLE).json()
    assert sum(l["poids_pct"] for l in d["lignes"]) == pytest.approx(100.0, abs=0.05)


def test_le_total_est_renvoye_et_non_laisse_a_l_appelant(client, portefeuille_simule):
    """Additionner soi-même les valorisations reviendrait à refaire un calcul déjà
    fait par la vue — et deux calculs de la même chose finissent par diverger."""
    d = client.get("/donnees/indicateurs-portefeuille", headers=CLE).json()
    assert d["total_eur"] == 4000.00
    assert d["total_eur"] != d["lignes"][0]["valorisation_eur"]


def test_aucun_seuil_ni_classement_de_risque_n_est_renvoye(client, portefeuille_simule):
    """⚠️ Garde-fou AMF, verrouillé par un test.

    Un poids de 75 % est un **fait**. « Concentration excessive », « à alléger » ou
    un drapeau `alerte` seraient des **conseils** — ce que l'interdit AMF proscrit.
    Ce test échouera si un champ de ce genre apparaît un jour dans la réponse.
    """
    d = client.get("/donnees/indicateurs-portefeuille", headers=CLE).json()
    interdits = {"alerte", "risque", "recommandation", "conseil", "seuil", "action"}
    for ligne in d["lignes"]:
        assert not (interdits & set(ligne)), f"champ de conseil dans la réponse : {ligne}"
    assert not (interdits & set(d))


# --- /donnees/indicateurs-risque (lot 3) --------------------------------------

@pytest.fixture
def risque_simule():
    """Deux valeurs : une fraîche, une radiée depuis 2018."""
    volat = [
        {"ticker": "MC.PA", "nom_officiel": "LVMH", "statut_qualite": "OK",
         "date_cours": date(2026, 8, 18), "cours": Decimal("449.65"),
         "fraicheur_jours": 1, "volatilite_annualisee_pct": Decimal("22.14"),
         "drawdown_max_1a_pct": Decimal("-18.30")},
        {"ticker": "ZC.PA", "nom_officiel": "ZODIAC AEROSPACE", "statut_qualite": "OK",
         "date_cours": date(2018, 3, 22), "cours": Decimal("24.83"),
         "fraicheur_jours": 3072, "volatilite_annualisee_pct": Decimal("16.70"),
         "drawdown_max_1a_pct": Decimal("-24.78")},
    ]
    # rsi_wilder exige plus de 14 variations : 20 points de cours, en hausse.
    rsi = [{"ticker": "MC.PA", "date_seance": date(2026, 7, 20) + timedelta(days=i),
            "cloture": Decimal(str(440 + i))} for i in range(20)]

    def espion(sql, parametres=None):
        # lire_volatilite_drawdown appelle sans parametres ; lire_rsi passe {"tickers": ...}.
        return volat if parametres is None else rsi

    with patch("indicateurs.socle._executer", side_effect=espion):
        yield


def test_indicateurs_risque_combine_volatilite_drawdown_et_rsi(client, risque_simule):
    r = client.get("/donnees/indicateurs-risque", headers=CLE)
    assert r.status_code == 200
    d = r.json()
    assert d["nb"] == 2
    mc = next(x for x in d["indicateurs"] if x["ticker"] == "MC.PA")
    assert mc["volatilite_annualisee_pct"] == 22.14
    assert mc["rsi_14"] == 100.0  # 20 séances strictement haussières


def test_indicateurs_risque_valeur_radiee_a_rsi_null(client, risque_simule):
    """⚠️ Le test de la découverte du 19/08 : une valeur radiée doit ressortir
    signalée (`cotation_perimee`) et sans RSI (`rsi_14 = null`), pas avec un
    RSI daté de 2018 présenté comme actuel."""
    d = client.get("/donnees/indicateurs-risque", headers=CLE).json()
    zc = next(x for x in d["indicateurs"] if x["ticker"] == "ZC.PA")
    assert zc["cotation_perimee"] is True
    assert zc["rsi_14"] is None
    assert zc["volatilite_annualisee_pct"] == 16.70   # la mesure reste affichée


def test_indicateurs_risque_aucun_conseil_dans_la_reponse(client, risque_simule):
    """Garde-fou AMF, même exigence que pour le lot 2 : aucun seuil, aucune
    recommandation dans un point de terminaison qui expose un RSI."""
    d = client.get("/donnees/indicateurs-risque", headers=CLE).json()
    interdits = {"alerte", "risque_niveau", "recommandation", "conseil", "seuil", "action", "signal"}
    for ligne in d["indicateurs"]:
        assert not (interdits & set(ligne)), f"champ de conseil : {ligne}"

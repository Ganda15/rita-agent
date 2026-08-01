"""Tests de l'API de mise à disposition du jeu de données (C5) — base simulée.

Le critère central de C5 est **« l'API restreint par une autorisation l'accès aux
données »**. C'est donc la première chose testée, et sur *chaque* point de terminaison :
un contrôle d'accès qui protège 5 routes sur 6 ne protège rien.
"""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from sources.database import Extraction

CLE = {"X-API-Key": "dev-key"}

ROUTES_PROTEGEES = [
    "/donnees/valeurs",
    "/donnees/cotations?ticker=MC.PA",
    "/donnees/portefeuille",
    "/donnees/mouvements",
    "/donnees/volumes-anormaux",
    "/donnees/articles",
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
                  "/donnees/articles", "/briefing", "/health"):
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

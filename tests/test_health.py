"""Tests FastAPI — C12 : tests automatisés avec TestClient."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from api.main import app
from tests.conftest import CLE_DE_TEST

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_returns_project_name():
    response = client.get("/health")
    assert response.json()["project"] == "RITA"


def test_briefing_without_api_key_returns_403():
    response = client.post("/briefing?ticker=AAPL")
    assert response.status_code == 403


def test_briefing_avec_cle_valide_retourne_le_briefing(monkeypatch):
    resultat_simule = {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99,
                        "currency": "EUR", "briefing": "Texte du briefing.", "error": ""}
    with patch("api.main.generer_briefing_complet", return_value=resultat_simule):
        response = client.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})

    assert response.status_code == 200
    assert response.json()["briefing"] == "Texte du briefing."


def test_briefing_retourne_502_si_erreur_scout(monkeypatch):
    resultat_simule = {"ticker": "XXX.PA", "price": 0.0, "change_pct": 0.0,
                        "currency": "", "briefing": "", "error": "no data"}
    with patch("api.main.generer_briefing_complet", return_value=resultat_simule):
        response = client.post("/briefing?ticker=XXX.PA", headers={"X-API-Key": CLE_DE_TEST})

    assert response.status_code == 502


# --- OWASP API2 : plus aucune clé par défaut ----------------------------------

def test_l_api_refuse_de_servir_sans_cle_configuree(sans_cle_api):
    """⚠️ Corrigé le 18/08/2026 — OWASP API2 (authentification défaillante).

    Le code disait `os.getenv("RITA_API_KEY", "dev-key")`. La variable n'étant pas
    définie, l'API acceptait en réalité la chaîne `dev-key`, **écrite en clair dans
    `api/main.py`** — donc lisible par le formateur et le jury.

    *Une clé par défaut n'est pas une clé : c'est une porte ouverte documentée.*

    Le défaut est remplacé par une panne explicite : mieux vaut une API qui refuse
    de servir qu'une API qui sert n'importe qui.
    """
    from api.main import cle_attendue

    with pytest.raises(RuntimeError) as erreur:
        cle_attendue()

    message = str(erreur.value)
    assert "RITA_API_KEY" in message
    assert "secrets.token_urlsafe" in message, \
        "le message doit dire COMMENT générer une clé — un garde-fou qui bloque " \
        "sans expliquer se contourne"


def test_une_cle_trop_courte_est_refusee(monkeypatch):
    """Une clé de 4 caractères se force en quelques secondes."""
    from api.main import cle_attendue

    monkeypatch.setenv("RITA_API_KEY", "abc")
    with pytest.raises(RuntimeError, match="trop courte"):
        cle_attendue()


def test_dev_key_n_est_plus_acceptee_par_defaut():
    """Non-régression : personne ne doit pouvoir remettre une valeur de repli sans
    que la suite le signale.

    ⚠️ Le test ne regarde que le **code exécuté**. La docstring de `cle_attendue()`
    cite `"dev-key"` pour expliquer le défaut corrigé — chercher la chaîne dans la
    source entière ferait échouer le test sur la phrase qui documente la correction.

    C'est la **troisième fois** que ce piège se présente dans ce projet : `LAG(` dans
    un commentaire SQL, `innerHTML` dans un commentaire JavaScript, et maintenant
    ceci. **Un test doit porter sur le code exécuté, jamais sur ce qui l'explique.**
    """
    import ast
    import inspect

    from api import main

    arbre = ast.parse(inspect.getsource(main.cle_attendue))
    fonction = arbre.body[0]
    if (fonction.body and isinstance(fonction.body[0], ast.Expr)
            and isinstance(fonction.body[0].value, ast.Constant)):
        fonction.body.pop(0)                      # retire la docstring

    corps = ast.unparse(fonction)
    assert "dev-key" not in corps, \
        "une valeur par défaut est réapparue dans le code de cle_attendue()"
    assert "os.getenv('RITA_API_KEY')" in corps or 'os.getenv("RITA_API_KEY")' in corps, \
        "la clé doit être lue SANS second argument — le second argument EST le défaut"


def test_la_comparaison_des_cles_est_a_temps_constant():
    """`compare_digest` et non `!=` : une comparaison ordinaire s'arrête au premier
    caractère différent, et son temps d'exécution renseigne un attaquant sur le
    nombre de caractères déjà devinés. La parade est gratuite."""
    import inspect

    from api import main

    source = inspect.getsource(main.verify_api_key)
    assert "compare_digest" in source


# --- C9, C17 : le garde-fou de sortie est branché sur la route ----------------

def test_briefing_interdit_est_remplace_par_le_message_de_refus():
    """Ajouté le 02/10/2026 (audit) : le garde-fou de sortie est testé seul, mais
    aucun test ne prouvait qu'il est BRANCHÉ sur /briefing. Retirer l'appel dans
    api/main.py laissait toute la suite verte.

    Le modèle est simulé : on lui fait produire une recommandation d'achat, et on
    vérifie que l'API ne la diffuse pas."""
    from guardrails.sortie import MESSAGE_REFUS

    resultat_simule = {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99,
                        "currency": "EUR", "error": "",
                        "briefing": "Nous recommandons l'achat de cette valeur."}
    with patch("api.main.generer_briefing_complet", return_value=resultat_simule):
        response = client.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})

    assert response.status_code == 200          # un refus n'est pas une panne
    corps = response.json()
    assert corps["conforme_amf"] is False
    assert corps["briefing"] == MESSAGE_REFUS
    assert "recommandons" not in corps["briefing"], "le texte interdit ne doit jamais sortir"
    assert "recommandation_explicite_fr" in corps["motifs_amf"]

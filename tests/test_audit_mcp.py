"""Le journal d'audit des appels MCP, table `mcp_calls` (plan 62, C20, chapitre « Données » §3.7).

Décisions d'Era du 03/10/2026 : D1, seuls les appels qui portent `X-Client-Id` sont journalisés (le
navigateur d'Era n'est pas un client MCP) ; D2, les refus locaux de la passerelle sont remontés par
`POST /audit/mcp` ; D3, une panne d'écriture se voit par un compteur dans `/donnees/fraicheur` et une
ligne WARNING. Un seul écrivain : l'API. La passerelle ne touche jamais la base.

Aucun test ici ne touche PostgreSQL : la connexion est simulée. La base réelle est dans
`tests/test_audit_mcp_base.py`.
"""
import logging
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from api.main import app
from db import audit_mcp
from tests.conftest import CLE_DE_TEST

client_http = TestClient(app)
EN_TETES_MCP = {"X-API-Key": CLE_DE_TEST, "X-Client-Id": "passerelle-mcp", "X-Outil": "rita_fraicheur"}


def _connexion_simulee():
    cur = MagicMock()
    cur.__enter__ = MagicMock(return_value=cur)
    cur.__exit__ = MagicMock(return_value=False)
    conn = MagicMock()
    conn.cursor.return_value = cur
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock(return_value=False)
    conn._curseur = cur
    return conn


@pytest.fixture(autouse=True)
def _compteur_a_zero():
    audit_mcp.reinitialiser_compteur()
    yield
    audit_mcp.reinitialiser_compteur()


# --- 1. l'écrivain ------------------------------------------------------------------------------

def test_enregistrer_ecrit_les_huit_champs_en_parametres_lies():
    conn = _connexion_simulee()
    with patch("db.audit_mcp.database._connexion", return_value=conn):
        ok = audit_mcp.enregistrer(request_id="a" * 32, client_id="passerelle-mcp", outil="rita_indicateurs",
                                   statut="succes", code_erreur=None, duree_ms=12)
    assert ok is True
    sql, params = conn._curseur.execute.call_args.args
    assert "INSERT INTO mcp_calls" in sql
    assert "%(request_id)s" in sql and "%(version_politique)s" in sql
    assert params["statut"] == "succes" and params["duree_ms"] == 12 and params["code_erreur"] is None
    assert params["version_politique"] == audit_mcp.VERSION_POLITIQUE
    assert set(params) == {"request_id", "client_id", "outil", "statut", "code_erreur", "duree_ms", "version_politique"}


def test_un_statut_hors_liste_est_une_erreur_de_programmation():
    with pytest.raises(ValueError):
        audit_mcp.enregistrer(request_id="a" * 32, client_id="x", outil="y", statut="bizarre")


def test_un_identifiant_ou_un_outil_douteux_est_neutralise_pas_recopie():
    """Un client qui envoie `<script>` ou 500 caractères dans `X-Outil` n'écrit pas ça en base."""
    conn = _connexion_simulee()
    with patch("db.audit_mcp.database._connexion", return_value=conn):
        audit_mcp.enregistrer(request_id="a" * 32, client_id="<script>alert(1)</script>",
                              outil="x" * 500, statut="refuse", code_erreur="NOT_AUTHORIZED")
    params = conn._curseur.execute.call_args.args[1]
    assert params["client_id"] == "invalide"
    assert len(params["outil"]) <= 60


def test_une_panne_d_ecriture_ne_leve_pas_mais_se_voit(caplog):
    """Règle 7 du chapitre : une défaillance de journalisation doit être détectable (D3)."""
    with patch("db.audit_mcp.database._connexion", side_effect=OSError("base injoignable")), \
         caplog.at_level(logging.WARNING, logger="db.audit_mcp"):
        ok = audit_mcp.enregistrer(request_id="a" * 32, client_id="passerelle-mcp", outil="rita_fraicheur",
                                   statut="succes")
    assert ok is False
    assert audit_mcp.echecs() == 1
    assert any("audit mcp non ecrit" in r.getMessage() for r in caplog.records)


@pytest.mark.parametrize("code_http, attendu", [
    (200, ("succes", None)), (403, ("refuse", "NOT_AUTHORIZED")), (404, ("refuse", "NOT_FOUND")),
    (422, ("refuse", "PARAMETRE_INVALIDE")), (500, ("erreur", "ERREUR_API")), (502, ("erreur", "SERVICE_INDISPONIBLE")),
])
def test_le_statut_se_deduit_du_code_http(code_http, attendu):
    assert audit_mcp.statut_depuis_code(code_http) == attendu


# --- 2. le middleware : chaque appel d'un client MCP laisse une ligne ------------------------------

def _appels(mock):
    return [c.kwargs for c in mock.call_args_list]


def test_un_appel_reussi_d_un_client_mcp_est_journalise_avec_son_request_id():
    with patch("api.main.audit_mcp.enregistrer") as ecrire:
        r = client_http.get("/health", headers=EN_TETES_MCP)
    assert r.status_code == 200
    (appel,) = _appels(ecrire)
    assert appel["request_id"] == r.headers["X-Request-ID"]
    assert appel["client_id"] == "passerelle-mcp" and appel["outil"] == "rita_fraicheur"
    assert appel["statut"] == "succes" and appel["code_erreur"] is None
    assert isinstance(appel["duree_ms"], int) and appel["duree_ms"] >= 0


def test_un_refus_403_d_un_client_mcp_est_journalise_refuse():
    with patch("api.main.audit_mcp.enregistrer") as ecrire:
        r = client_http.get("/donnees/fraicheur", headers={**EN_TETES_MCP, "X-API-Key": "mauvaise-cle-mais-longue-x"})
    assert r.status_code == 403
    (appel,) = _appels(ecrire)
    assert appel["statut"] == "refuse" and appel["code_erreur"] == "NOT_AUTHORIZED"


def test_une_erreur_500_d_un_client_mcp_est_journalisee_erreur():
    tolerant = TestClient(app, raise_server_exceptions=False)
    with patch("api.main.audit_mcp.enregistrer") as ecrire, \
         patch("api.main.generer_briefing_complet", side_effect=RuntimeError("panne")):
        r = tolerant.post("/briefing?ticker=MC.PA", headers={**EN_TETES_MCP, "X-Outil": "briefing"})
    assert r.status_code == 500
    (appel,) = _appels(ecrire)
    assert appel["statut"] == "erreur" and appel["request_id"] == r.headers["X-Request-ID"]


def test_sans_x_client_id_rien_n_est_journalise():
    """D1 : le navigateur d'Era n'est pas un client MCP ; sa navigation n'entre pas en base."""
    with patch("api.main.audit_mcp.enregistrer") as ecrire:
        client_http.get("/health")
        client_http.get("/donnees/fraicheur", headers={"X-API-Key": "mauvaise-cle-mais-longue-x"})
    ecrire.assert_not_called()


def test_aucun_parametre_de_requete_n_entre_dans_la_ligne():
    """Un ticker est un intérêt personnel : seul le nom de l'outil est journalisé, jamais la question."""
    with patch("api.main.audit_mcp.enregistrer") as ecrire:
        client_http.get("/donnees/indicateurs?ticker=MC.PA", headers={**EN_TETES_MCP, "X-Outil": "rita_indicateurs",
                                                                       "X-API-Key": "mauvaise-cle-mais-longue-x"})
    (appel,) = _appels(ecrire)
    assert "MC.PA" not in str(appel)


# --- 3. les refus locaux de la passerelle remontent par POST /audit/mcp (D2) ------------------------

def test_le_post_audit_exige_la_cle():
    r = client_http.post("/audit/mcp", json={"outil": "rita_portefeuille", "statut": "refuse", "code_erreur": "NOT_AUTHORIZED"})
    assert r.status_code == 403


def test_le_post_audit_ecrit_un_refus_local_avec_son_client():
    with patch("api.main.audit_mcp.enregistrer", return_value=True) as ecrire:
        r = client_http.post("/audit/mcp", headers=EN_TETES_MCP,
                             json={"outil": "rita_portefeuille", "statut": "refuse", "code_erreur": "NOT_AUTHORIZED",
                                   "request_id": "b" * 32})
    assert r.status_code == 200 and r.json() == {"enregistre": True}
    (appel,) = _appels(ecrire)      # une seule ligne : l'appel au POST lui-même n'est PAS journalisé en plus
    assert appel["outil"] == "rita_portefeuille" and appel["statut"] == "refuse"
    assert appel["code_erreur"] == "NOT_AUTHORIZED" and appel["request_id"] == "b" * 32
    assert appel["client_id"] == "passerelle-mcp"


@pytest.mark.parametrize("corps", [
    {"outil": "rita_portefeuille", "statut": "bizarre"},
    {"outil": "rita_portefeuille", "statut": "refuse", "code_erreur": "message libre avec espaces"},
    {"outil": "rita_portefeuille", "statut": "refuse", "parametres": {"ticker": "MC.PA"}},
    {"outil": "", "statut": "refuse"},
])
def test_le_post_audit_refuse_tout_champ_hors_contrat(corps):
    with patch("api.main.audit_mcp.enregistrer") as ecrire:
        r = client_http.post("/audit/mcp", headers=EN_TETES_MCP, json=corps)
    assert r.status_code == 422
    ecrire.assert_not_called()


# --- 4. la défaillance se voit dans le vecteur C20 (D3) -------------------------------------------

def test_le_compteur_d_echecs_est_expose_par_la_fraicheur():
    faux = MagicMock()
    faux.en_dict.return_value = {"statut": "vert", "message": "x"}
    with patch("db.audit_mcp.database._connexion", side_effect=OSError("base injoignable")):
        audit_mcp.enregistrer(request_id="a" * 32, client_id="passerelle-mcp", outil="rita_fraicheur", statut="succes")
    with patch("api.donnees.monitorage_fraicheur.lire", return_value=faux):
        corps = client_http.get("/donnees/fraicheur", headers={"X-API-Key": CLE_DE_TEST}).json()
    assert corps["audit_mcp_echecs"] == 1

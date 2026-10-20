"""Sprint 4, tâche C3 : la limite de débit sur `/briefing` et `/question` (décision D6, spec CA1.4).

Annoncée pour le sprint 4 par le plan du sprint 1 (« débit, refus journalisés »). Un petit limiteur écrit dans le projet,
en mémoire : un seul compteur, partagé par les deux routes qui appellent le modèle, sur une fenêtre glissante de 60 s.
Condition vérifiée le 20/10/2026 sur le serveur : l'API de production tourne avec un seul processus `uvicorn` (pas de
`--workers`, pas de `WEB_CONCURRENCY`) ; plusieurs processus ne partageraient pas leurs compteurs. Limite écrite : le
compteur repart à zéro à chaque redémarrage.
"""
import ast
import importlib
import inspect
import logging
import threading
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from tests.conftest import CLE_DE_TEST

CLE = {"X-API-Key": CLE_DE_TEST}


def _module():
    """Importé dans chaque test : tant que le module n'existe pas, chacun échoue pour cette raison."""
    return importlib.import_module("api.limiteur")


class _Horloge:
    def __init__(self):
        self.maintenant = 1000.0

    def __call__(self):
        return self.maintenant


# --- le limiteur seul ------------------------------------------------------------------------------------------------

def test_le_quota_est_respecte_puis_se_libere():
    horloge = _Horloge()
    limiteur = _module().Limiteur(3, fenetre_s=60.0, horloge=horloge)
    assert [limiteur.autoriser()[0] for _ in range(3)] == [True, True, True]
    accepte, attente = limiteur.autoriser()
    assert accepte is False and 1 <= attente <= 60
    horloge.maintenant += 60.5          # la fenêtre a glissé : les trois premiers appels ne comptent plus
    assert limiteur.autoriser()[0] is True


def test_vingt_appels_simultanes_pour_dix_places():
    # Point de vigilance du plan : sans verrou, deux fils pourraient lire le même compte et passer tous les deux.
    limiteur = _module().Limiteur(10)
    depart = threading.Barrier(20)
    resultats = []

    def appeler():
        depart.wait()
        resultats.append(limiteur.autoriser()[0])

    fils = [threading.Thread(target=appeler) for _ in range(20)]
    for f in fils:
        f.start()
    for f in fils:
        f.join()
    assert resultats.count(True) == 10 and resultats.count(False) == 10


# --- les routes ------------------------------------------------------------------------------------------------------

def _routes_simulees(monkeypatch):
    """Ni index, ni base, ni modèle : la recherche refuse hors corpus, le graphe du briefing rend un résultat figé."""
    from agents import question
    from rag.recherche import Resultat

    monkeypatch.setattr(question, "rechercher", lambda *a, **k: Resultat(False, "OUT_OF_CORPUS", [], 0))
    resultat = {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99, "currency": "EUR", "error": "",
                "briefing": "Le titre recule de 1,99 % sur la séance."}
    return patch("api.main.generer_briefing_complet", return_value=resultat)


def _question(client, entetes=CLE):
    return client.post("/question", json={"question": "Combien de postes Netflix supprime-t-il ?"}, headers=entetes)


def test_le_quota_est_partage_entre_briefing_et_question(monkeypatch, caplog):
    monkeypatch.setattr(_module(), "LIMITEUR", _module().Limiteur(2))
    client = TestClient(app)
    with _routes_simulees(monkeypatch), caplog.at_level(logging.WARNING):
        assert _question(client).status_code == 200
        assert client.post("/briefing?ticker=MC.PA", headers=CLE).status_code == 200
        refus = _question(client)
    assert refus.status_code == 429
    assert int(refus.headers["Retry-After"]) >= 1
    detail = refus.json()["detail"]
    assert (detail["statut"], detail["motif"]) == ("refus", "LIMITE_DE_DEBIT")
    assert detail["texte"] == "Trop de demandes en peu de temps. Réessayez dans une minute."
    assert "limite de debit atteinte" in caplog.text and refus.headers["X-Request-ID"] in caplog.text


def test_une_fausse_cle_ne_consomme_pas_le_quota(monkeypatch):
    monkeypatch.setattr(_module(), "LIMITEUR", _module().Limiteur(2))
    client = TestClient(app)
    with _routes_simulees(monkeypatch):
        assert [_question(client, {"X-API-Key": "FAUSSE-CLE-" + "0" * 24}).status_code for _ in range(5)] == [403] * 5
        assert [_question(client).status_code for _ in range(2)] == [200, 200]


def test_health_n_est_jamais_limite(monkeypatch):
    monkeypatch.setattr(_module(), "LIMITEUR", _module().Limiteur(1))
    client = TestClient(app)
    assert [client.get("/health").status_code for _ in range(5)] == [200] * 5


# --- le réglage du quota ---------------------------------------------------------------------------------------------

def test_le_module_charge_le_env_avant_de_lire_le_quota():
    # Revue Codex de la PR #111 (20/10/2026) : le .env n'était chargé avant LIMITEUR que grâce à l'ordre des imports
    # d'api/main.py (sources.database, indicateurs.socle et monitorage.fraicheur le chargent plus haut). Comme eux, le
    # module le charge lui-même : déplacer un import ne doit pas faire ignorer RITA_QUOTA_PAR_MINUTE en silence.
    arbre = ast.parse(inspect.getsource(_module()))
    chargements = [n.lineno for n in ast.walk(arbre)
                   if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "load_dotenv"]
    creation = next(n.lineno for n in arbre.body if isinstance(n, ast.Assign)
                    and any(getattr(cible, "id", None) == "LIMITEUR" for cible in n.targets))
    assert chargements and min(chargements) < creation


def test_le_quota_se_regle_par_la_variable(monkeypatch):
    # Le témoin : la variable, quand elle est présente au chargement du module, fixe le quota.
    monkeypatch.setenv("RITA_QUOTA_PAR_MINUTE", "3")
    module = importlib.reload(_module())
    try:
        assert module.LIMITEUR.quota == 3
    finally:
        monkeypatch.delenv("RITA_QUOTA_PAR_MINUTE")
        importlib.reload(module)

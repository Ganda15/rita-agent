"""Un identifiant par requête, repris dans la réponse, le journal et la trace Langfuse (C20, C11, C9).

Constat de l'audit du 02/10/2026 : aucun `request_id` dans le code. Sans lui, une ligne de
journal, une trace Langfuse et un incident ne se rejoignent pas : on lit « briefing refusé »
quelque part, « trace lente » ailleurs, et rien ne dit que c'est le même appel. C'est aussi
la leçon du brief Kaldera-A2A (un identifiant de corrélation par échange) et de Mardik ②.

Règles testées :
  1. toute réponse porte `X-Request-ID`, y compris les 403 et les 502 ;
  2. un identifiant valide envoyé par le client est repris ; un identifiant douteux est remplacé
     (sinon un tiers choisit ce qui s'écrit dans nos journaux : injection de journal) ;
  3. le même identifiant est dans la ligne de journal du briefing, dans celle d'un refus, et
     devient l'identifiant de trace Langfuse (cherchable aussi dans les métadonnées).
"""
import logging
import re
import subprocess
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient

from api.main import app
from tests.conftest import CLE_DE_TEST

client_http = TestClient(app)

IDENTIFIANT_GENERE = re.compile(r"^[0-9a-f]{32}$")
TEXTE_CONFORME = "Le titre recule de 1,99 % sur la séance."
TEXTE_INTERDIT = "Nous recommandons l'achat de cette valeur."


def _resultat(texte=TEXTE_CONFORME, erreur=""):
    return {"ticker": "MC.PA", "price": 457.5, "change_pct": -1.99, "currency": "EUR",
            "error": erreur, "briefing": texte}


def _briefing(texte=TEXTE_CONFORME, entetes=None, erreur=""):
    en_tetes = {"X-API-Key": CLE_DE_TEST, **(entetes or {})}
    with patch("api.main.generer_briefing_complet", return_value=_resultat(texte, erreur)):
        return client_http.post("/briefing?ticker=MC.PA", headers=en_tetes)


# --- 1. l'identifiant est sur toute réponse -----------------------------------

def test_chaque_reponse_porte_un_identifiant_de_requete():
    reponse = client_http.get("/health")
    assert IDENTIFIANT_GENERE.match(reponse.headers["X-Request-ID"])


def test_deux_requetes_ont_deux_identifiants():
    premier = client_http.get("/health").headers["X-Request-ID"]
    second = client_http.get("/health").headers["X-Request-ID"]
    assert premier != second


def test_un_refus_d_authentification_porte_aussi_l_identifiant():
    reponse = client_http.post("/briefing?ticker=MC.PA")
    assert reponse.status_code == 403
    assert IDENTIFIANT_GENERE.match(reponse.headers["X-Request-ID"])


def test_une_erreur_502_porte_aussi_l_identifiant():
    reponse = _briefing(erreur="no data")
    assert reponse.status_code == 502
    assert IDENTIFIANT_GENERE.match(reponse.headers["X-Request-ID"])


# --- 2. identifiant du client : repris s'il est sain, remplacé sinon ---------

def test_un_identifiant_valide_du_client_est_repris():
    reponse = client_http.get("/health", headers={"X-Request-ID": "client-req_12345678"})
    assert reponse.headers["X-Request-ID"] == "client-req_12345678"


def test_un_identifiant_douteux_est_remplace_par_un_identifiant_genere():
    for douteux in ("court", "a" * 65, "a b;c<script>", "../../etc/passwd", "id avec espace 123"):
        reponse = client_http.get("/health", headers={"X-Request-ID": douteux})
        recu = reponse.headers["X-Request-ID"]
        assert recu != douteux, f"{douteux!r} ne doit pas être repris"
        assert IDENTIFIANT_GENERE.match(recu)


# --- 3. le même identifiant dans le journal et dans la trace ------------------

def test_la_ligne_de_journal_du_briefing_porte_l_identifiant_sans_le_texte(caplog):
    with caplog.at_level(logging.INFO, logger="api.main"):
        reponse = _briefing()

    identifiant = reponse.headers["X-Request-ID"]
    lignes = [r.getMessage() for r in caplog.records
              if r.name == "api.main" and r.levelno == logging.INFO]
    assert len(lignes) == 1, "une ligne de journal par briefing servi"
    ligne = lignes[0]
    assert identifiant in ligne
    assert "ticker='MC.PA'" in ligne
    assert "conforme_amf=True" in ligne
    assert re.search(r"duree_ms=\d+", ligne)
    assert "recule" not in ligne, "le texte du briefing n'entre jamais dans un journal"


def test_la_ligne_d_un_refus_porte_l_identifiant(caplog):
    with caplog.at_level(logging.WARNING, logger="api.main"):
        reponse = _briefing(texte=TEXTE_INTERDIT)

    identifiant = reponse.headers["X-Request-ID"]
    avertissements = [r.getMessage() for r in caplog.records
                      if r.name == "api.main" and r.levelno == logging.WARNING]
    assert len(avertissements) == 1 and identifiant in avertissements[0]


def test_la_ligne_d_une_erreur_502_porte_l_identifiant(caplog):
    with caplog.at_level(logging.WARNING, logger="api.main"):
        reponse = _briefing(erreur="no data")

    identifiant = reponse.headers["X-Request-ID"]
    avertissements = [r.getMessage() for r in caplog.records
                      if r.name == "api.main" and r.levelno == logging.WARNING]
    assert len(avertissements) == 1
    assert identifiant in avertissements[0] and "502" in avertissements[0]


class _FausseObservation:
    def __init__(self, journal, kwargs):
        self.journal, self.kwargs = journal, kwargs

    def __enter__(self):
        self.journal.append(("ouvre", self.kwargs))
        return self

    def __exit__(self, *exc):
        return False

    def update(self, **kwargs):
        self.journal.append(("update", kwargs))

    def score_trace(self, **kwargs):
        pass


class _FauxClient:
    def __init__(self):
        self.journal = []

    def create_trace_id(self, *, seed=None):
        return "trace-" + str(seed)

    def start_as_current_observation(self, **kwargs):
        return _FausseObservation(self.journal, kwargs)

    def flush(self):
        pass


def test_l_identifiant_de_requete_devient_l_identifiant_de_trace_langfuse():
    faux = _FauxClient()
    with patch("src.traces.client_traces", return_value=faux):
        reponse = _briefing()

    identifiant = reponse.headers["X-Request-ID"]
    racine = [k for (ev, k) in faux.journal if ev == "ouvre" and k["name"] == "briefing"][0]
    assert racine["trace_context"] == {"trace_id": "trace-" + identifiant}
    assert racine["metadata"]["request_id"] == identifiant, "cherchable aussi dans les métadonnées"
    verdict = [k for (ev, k) in faux.journal if ev == "update"][-1]
    assert verdict["metadata"]["request_id"] == identifiant, \
        "la mise à jour du verdict ne doit pas effacer l'identifiant"


# --- 4. en production, la ligne INFO s'écrit vraiment -------------------------

def test_sous_uvicorn_les_lignes_info_de_l_api_sont_visibles():
    """Sans configuration, Python n'écrit que les avertissements : la ligne « briefing servi »
    serait invisible en production. On le mesure dans un processus propre, sans pytest."""
    code = ("import logging, api.main; r = logging.getLogger(); "
            "print(r.isEnabledFor(logging.INFO), bool(r.handlers))")
    sortie = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                            timeout=120, env={**__import__("os").environ, "LANGFUSE_TRACING_ENABLED": "false"})
    assert sortie.stdout.strip().splitlines()[-1] == "True True", sortie.stderr[-500:]


# --- 5. une erreur inattendue (500) porte aussi l'identifiant ------------------
# Revue Codex de la PR #58 (03/10/2026), remarque P2 : quand une route levait une exception
# non prévue, `call_next` la propageait à travers le `finally` du middleware et la ligne qui
# pose l'en-tête n'était jamais atteinte. Le 500 fabriqué par Starlette partait sans
# `X-Request-ID` : précisément la panne qu'on a le plus besoin de retrouver dans les journaux.

def test_une_erreur_inattendue_500_porte_aussi_l_identifiant(caplog):
    client_tolerant = TestClient(app, raise_server_exceptions=False)
    with patch("api.main.generer_briefing_complet", side_effect=RuntimeError("panne imprevue")), \
         caplog.at_level(logging.ERROR, logger="api.main"):
        reponse = client_tolerant.post("/briefing?ticker=MC.PA", headers={"X-API-Key": CLE_DE_TEST})
    assert reponse.status_code == 500
    identifiant = reponse.headers.get("X-Request-ID", "")
    assert IDENTIFIANT_GENERE.match(identifiant), "le 500 doit porter l'identifiant comme les autres"
    assert "panne imprevue" not in reponse.text, "le detail d'une exception interne ne sort jamais au client"
    erreurs = [r.getMessage() for r in caplog.records if r.levelno == logging.ERROR]
    assert erreurs and identifiant in erreurs[0], "la ligne ERROR doit porter le meme identifiant"

"""API REST de RITA — mise à disposition des données (C5) et du briefing (C9).

Deux familles de points de terminaison, et la distinction est celle du référentiel :

    /donnees/*    le JEU DE DONNÉES brut, filtrable            -> C5
    /briefing     un TEXTE rédigé par un modèle d'IA           -> C9

Documentation interactive : http://127.0.0.1:8000/docs
Contrat OpenAPI :           http://127.0.0.1:8000/openapi.json
"""
import contextvars
import logging
import os
import re
import secrets
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.background import BackgroundTask, BackgroundTasks
from typing import Literal
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles

from api.donnees import routeur as routeur_donnees
from db import audit_mcp
from graph.workflow import generer_briefing_complet
from guardrails.sortie import verifier_sortie
from rag import indexation
from src import traces

load_dotenv()

# Sans configuration, Python n'écrit que les avertissements : la ligne « briefing servi »
# (INFO) serait invisible sous uvicorn. `basicConfig` ne fait rien si quelqu'un a déjà
# configuré la racine (pytest, un script) : on ne marche sur les pieds de personne.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

# --- Un identifiant par requête (C20, Mardik 2, Kaldera-A2A) ------------------------------
# Le même identifiant se lit dans l'en-tête `X-Request-ID` de la réponse, dans chaque ligne
# de journal de la requête, et comme identifiant de la trace Langfuse. Sans lui, un journal,
# une trace et un incident ne se rejoignent jamais.
#
# Un identifiant fourni par le client est repris SEULEMENT s'il est sain : 8 à 64 caractères
# parmi lettres, chiffres, `-` et `_`. Sinon un tiers choisirait ce qui s'écrit dans nos
# journaux (retours à la ligne, balises : injection de journal). On le remplace sans bruit.
IDENTIFIANT_CLIENT_SAIN = re.compile(r"^[A-Za-z0-9_-]{8,64}$")
_request_id_courant: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


def request_id_courant() -> str:
    """L'identifiant de la requête en cours, ou une chaîne vide hors requête."""
    return _request_id_courant.get()

DESCRIPTION = """
API de **RITA** — *Retrieval Intelligence pour le Tracking et l'Analyse*.

### Authentification
Tous les points de terminaison sauf `/health` exigent l'en-tête **`X-API-Key`**.
Une clé absente ou invalide renvoie **403**.

### Deux familles
| Préfixe | Contenu | Compétence |
|---|---|---|
| `/donnees/*` | le jeu de données brut, filtrable | C5 |
| `/briefing` | un texte rédigé par un modèle | C9 |

### ⚠️ Données personnelles
`/donnees/portefeuille` expose des données financières personnelles (RGPD, traitement T1).
"""

app = FastAPI(
    title="RITA API",
    version="1.1.0",
    description=DESCRIPTION,
    contact={"name": "RITA — projet fil rouge RNCP 37827"},
)

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


@app.middleware("http")
async def attribuer_un_identifiant_de_requete(request: Request, call_next):
    """Pose `X-Request-ID` sur TOUTE réponse, y compris 403 et 502 : une erreur sans
    identifiant est une erreur qu'on ne retrouve pas."""
    debut = time.perf_counter()
    propose = request.headers.get("X-Request-ID", "")
    identifiant = propose if IDENTIFIANT_CLIENT_SAIN.match(propose) else uuid.uuid4().hex
    jeton = _request_id_courant.set(identifiant)
    try:
        reponse = await call_next(request)
    except Exception as erreur:  # noqa: BLE001
        # Revue automatisée de la PR #58 (03/10/2026) : une exception imprévue traversait ce bloc et
        # Starlette fabriquait un 500 SANS identifiant, précisément la panne qu'on doit retrouver.
        # On la journalise avec l'identifiant (type et message, jamais vers le client) et on
        # répond nous-mêmes, l'en-tête posé.
        logger.error("erreur interne : request_id=%s chemin=%s %s", identifiant,
                     request.url.path, f"{type(erreur).__name__}: {erreur}"[:300])
        reponse = JSONResponse(
            status_code=500,
            content={"detail": f"Erreur interne. Identifiant de requete : {identifiant}"},
        )
    finally:
        _request_id_courant.reset(jeton)
    reponse.headers["X-Request-ID"] = identifiant
    # Plan 62 (03/10/2026, décision D1) : un appel qui se déclare client automatique (`X-Client-Id`,
    # la passerelle MCP) laisse une ligne dans `mcp_calls`, écrite APRÈS l'envoi de la réponse : le
    # client ne paie pas l'écriture. Le navigateur d'Era ne se déclare pas : rien n'est écrit.
    # `/audit/mcp` est exclu : la route écrit elle-même, sinon chaque refus ferait deux lignes.
    client_id = request.headers.get("X-Client-Id", "")
    if client_id and request.url.path != "/audit/mcp":
        statut, code_erreur = audit_mcp.statut_depuis_code(reponse.status_code)
        tache = BackgroundTask(
            audit_mcp.enregistrer, request_id=identifiant, client_id=client_id,
            outil=request.headers.get("X-Outil") or request.url.path, statut=statut,
            code_erreur=code_erreur, duree_ms=int((time.perf_counter() - debut) * 1000))
        reponse.background = BackgroundTasks([reponse.background, tache]) if reponse.background else tache
    return reponse


LONGUEUR_MINIMALE_CLE = 16


def cle_attendue() -> str:
    """La clé d'API, lue dans l'environnement — **sans valeur par défaut**.

    ⚠️ **Corrigé le 18/08/2026 — OWASP API2 (authentification défaillante).**
    Ce code disait `os.getenv("RITA_API_KEY", "dev-key")`. La variable n'étant pas
    définie, l'API acceptait en réalité la chaîne **`dev-key`, écrite en clair dans
    ce fichier** — donc dans un dépôt que le formateur et le jury vont lire.
    *Une clé par défaut n'est pas une clé : c'est une porte ouverte documentée.*

    Le remplacement volontaire d'un défaut par une **panne au démarrage** : mieux vaut
    une API qui refuse de servir qu'une API qui sert n'importe qui. Le message dit
    exactement quoi faire — un garde-fou qui bloque sans expliquer se contourne.
    """
    cle = os.getenv("RITA_API_KEY")
    if not cle:
        raise RuntimeError(
            "RITA_API_KEY absente. L'API refuse de demarrer sans cle : une valeur par "
            "defaut serait devinable par quiconque lit le code (OWASP API2).\n"
            "  Generer une cle :  python -c \"import secrets; print(secrets.token_urlsafe(32))\"\n"
            "  Puis l'ajouter au fichier .env :  RITA_API_KEY=<la cle generee>"
        )
    if len(cle) < LONGUEUR_MINIMALE_CLE:
        raise RuntimeError(
            f"RITA_API_KEY trop courte ({len(cle)} caracteres, minimum "
            f"{LONGUEUR_MINIMALE_CLE}). Une cle courte se devine ou se force."
        )
    return cle


def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Autorisation par clé d'API.

    Volontairement simple : une seule clé, comparée à `RITA_API_KEY`. RITA est
    mono-utilisateur (décision D10) — un système de comptes serait de la complexité sans
    besoin. La contrepartie est assumée : pas de révocation partielle, pas de traçabilité
    par appelant.
    """
    # `compare_digest` et non `!=` : une comparaison de chaînes ordinaire s'arrête au
    # premier caractère différent, et son temps d'exécution renseigne donc un attaquant
    # sur le nombre de caractères devinés. La différence est infime, la parade gratuite.
    if api_key is None or not secrets.compare_digest(api_key, cle_attendue()):
        raise HTTPException(status_code=403, detail="Cle d'API invalide ou absente")
    return api_key


class EvenementMcp(BaseModel):
    """Un refus survenu dans la passerelle MCP, avant tout appel métier (plan 62, décision D2).
    Contrat fermé : aucun champ libre, aucun paramètre, aucun message. `extra="forbid"` refuse tout
    ce qui n'est pas listé : un client qui tente d'y glisser un ticker reçoit 422."""
    model_config = ConfigDict(extra="forbid")
    outil: str = Field(min_length=1, max_length=60, pattern=r"^[A-Za-z0-9_.\-]+$")
    statut: Literal["succes", "refuse", "erreur"]
    code_erreur: str | None = Field(default=None, max_length=40, pattern=r"^[A-Z_]+$")
    request_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_-]{8,64}$")
    duree_ms: int | None = Field(default=None, ge=0)


@app.post("/audit/mcp", tags=["service"], summary="Journaliser un refus survenu dans la passerelle MCP")
def journaliser_evenement_mcp(evenement: EvenementMcp, request: Request,
                              api_key: str = Security(verify_api_key)) -> dict:
    """La passerelle ne touche jamais la base : quand elle refuse un appel avant de l'exécuter
    (portefeuille hors démonstration, par exemple), elle le dit ici et l'API écrit la ligne."""
    ok = audit_mcp.enregistrer(
        request_id=evenement.request_id or request_id_courant(),
        client_id=request.headers.get("X-Client-Id", "inconnu"),
        outil=evenement.outil, statut=evenement.statut,
        code_erreur=evenement.code_erreur, duree_ms=evenement.duree_ms)
    return {"enregistre": ok}


@app.get("/health", tags=["service"], summary="Vérifier que le service répond")
def health():
    """Seul point de terminaison **non protégé** : il ne révèle aucune donnée.

    Il annonce aussi la version servie (commit et date de construction), posées dans l'image par le
    Dockerfile ; « inconnu » hors de l'image (poste, tests). Lues à chaque appel, pas au chargement.

    Sprint 3, tâche A1 : il annonce aussi l'identité de l'index servi (`index`), car une ingestion change
    l'index sans changer le commit. Des comptes et une empreinte, aucun article : rien à protéger.
    `None` quand l'index n'a pas encore d'identité.
    """
    return {
        "status": "ok",
        "project": "RITA",
        "commit": os.getenv("RITA_GIT_SHA", "inconnu"),
        "construit_le": os.getenv("RITA_CONSTRUIT_LE", "inconnu"),
        "index": indexation.lire_identite(),
    }


# --- C5 : le jeu de données -------------------------------------------------
# La dépendance est posée sur le ROUTEUR entier : impossible d'ajouter un point de
# terminaison non protégé par oubli. C'est un garde-fou de conception, pas de discipline.
app.include_router(routeur_donnees, dependencies=[Depends(verify_api_key)])


# --- C9 : le briefing rédigé ------------------------------------------------
@app.post("/briefing", tags=["briefing IA"],
          summary="Générer un briefing rédigé pour une valeur")
def briefing(ticker: str, api_key: str = Security(verify_api_key)):
    """Produit un texte en français à partir des données de la valeur.

    Relève de **C9** (exposer un modèle), pas de C5 : la sortie est une rédaction, pas de
    la donnée. Le garde-fou AMF s'applique — aucune recommandation d'achat ou de vente.
    """
    request_id = request_id_courant()
    debut = time.perf_counter()
    # Une racine de trace par briefing (C11) : tout ce qui suit, y compris l'appel au modèle,
    # se range dessous, et le verdict du garde-fou y est posé. Sans clés Langfuse, `racine`
    # vaut None et rien ne change (src/traces.py). L'identifiant de requête devient celui
    # de la trace : journal et trace se retrouvent par le même identifiant.
    with traces.briefing(ticker, request_id=request_id) as racine:
        resultat = generer_briefing_complet(ticker)
        if resultat["error"]:
            logger.warning("briefing en erreur 502 : request_id=%s ticker=%r",
                           request_id, ticker)
            raise HTTPException(status_code=502, detail=resultat["error"])

        # Garde-fou de SORTIE (C17) — l'interdit AMF s'applique au texte produit, pas
        # seulement au prompt. Le prompt demande déjà « aucune recommandation » ; un prompt
        # est une consigne, pas un contrôle. Ajouté le 17/08/2026 : il était invoqué par le
        # docstring de guardrails/injection.py sans exister. Fail-closed : en cas de doute,
        # on ne diffuse pas.
        with traces.etape("garde-fou-sortie") as span_sortie:
            verdict = verifier_sortie(resultat["briefing"])
            traces.noter_garde_fou(span_sortie, not verdict["conforme"], verdict["motifs_detectes"])
        traces.noter_verdict_amf(racine, resultat["ticker"], verdict["conforme"],
                                 verdict["motifs_detectes"], request_id=request_id)

    # Un refus laisse UNE ligne dans le journal (audit du 02/10/2026) : sans elle, personne ne sait
    # que le garde-fou a servi, ni pour quel motif. Jamais le texte refusé : il serait relu et
    # recopié. `%r` entoure la valeur de guillemets et neutralise les retours à la ligne, pour
    # qu'une valeur saisie par un tiers ne puisse pas forger de fausses lignes de journal.
    if not verdict["conforme"]:
        logger.warning("briefing refuse par le garde-fou de sortie : request_id=%s ticker=%r motifs=%s",
                       request_id, resultat["ticker"], ",".join(verdict["motifs_detectes"]))

    # Une ligne INFO par briefing servi : identifiant, valeur, verdict, durée. Jamais le texte.
    # C'est la matière première du monitorage (C20) : combien, pour qui, en combien de temps.
    logger.info("briefing servi : request_id=%s ticker=%r conforme_amf=%s duree_ms=%d",
                request_id, resultat["ticker"], verdict["conforme"],
                int((time.perf_counter() - debut) * 1000))

    return {
        "ticker": resultat["ticker"],
        "price": resultat["price"],
        "change_pct": resultat["change_pct"],
        "currency": resultat["currency"],
        "briefing": verdict["texte_diffusable"],
        "conforme_amf": verdict["conforme"],
        "motifs_amf": verdict["motifs_detectes"],
        # Sprint 2 (14/10) : le nombre d'articles distincts transmis au modèle. Un briefing est rédigé même sans
        # article ; sans ce compte, un index vide en production passait tous les contrôles du script du serveur.
        "articles_transmis": len({p["article_id"] for p in resultat.get("passages") or []}),
    }


# --- L'interface (C10, C17) --------------------------------------------------
# Servie par la MÊME application que l'API : même origine, donc aucune règle CORS
# à ouvrir. Une porte de moins à justifier dans la revue OWASP.
#
# ⚠️ Ce montage doit rester la DERNIÈRE instruction du fichier : `/` capture toutes
# les adresses restantes. Placé plus haut, il masquerait /donnees et /briefing.
app.mount("/", StaticFiles(directory=Path(__file__).parent.parent / "frontend",
                           html=True), name="interface")

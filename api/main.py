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
from datetime import date, datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Security
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.background import BackgroundTask, BackgroundTasks
from typing import Literal
from fastapi.security.api_key import APIKeyHeader
from fastapi.staticfiles import StaticFiles

from agents.analyst import CONSIGNES_REDACTION, ROLE_REDACTEUR, articles_surs
from api.donnees import routeur as routeur_donnees
from api.exercice import routeur as routeur_exercice, verifier_cle_exercice
from api.limiteur import limiter_debit, noter_mauvaise_cle, refuser_si_bloquee
from api.question import routeur as routeur_question
from api.sante import routeur as routeur_sante
from db import audit_mcp
from graph.workflow import generer_briefing_complet
from guardrails.sortie import verifier_fuite, verifier_sortie
from indicateurs.socle import valeur_existe
from monitorage import compteurs
from monitorage.fraicheur import jours_ouvres_ecoules
from rag import indexation
from sources.marches import place_de_cotation
from src import traces
from src.llm import AucunFournisseur

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
Deux clés, chacune dans son en-tête, jamais l'une pour l'autre.

| Routes | En-tête exigé | Sans clé valide |
|---|---|---|
| `/health` | aucun : il ne rend aucune donnée | sans objet |
| `/donnees/*`, `/briefing`, `/question`, `/sante`, `/audit/mcp` | **`X-API-Key`** (`RITA_API_KEY`) | 403 |
| `/exercice/*` | **`X-Cle-Exercice`** (`RITA_CLE_EXERCICE`, la clé de l'opérateur) | 403 ; 503 si le serveur n'a pas de clé d'exercice |

`/briefing` et `/question` appellent le modèle : au-delà du quota (`RITA_QUOTA_PAR_MINUTE`, 10 appels par minute
par défaut), la réponse est **429** avec `Retry-After`. Chaque réponse, erreur comprise, porte un `X-Request-ID`.

Après 10 clés refusées en 15 minutes depuis une même adresse, toute route protégée répond **429** à cette adresse,
quelle que soit la clé, avec `Retry-After` et le motif `TROP_D_ESSAIS`. Une clé absente ne compte pas.

### Les familles de routes
| Préfixe | Contenu |
|---|---|
| `/donnees/*` | le jeu de données brut, filtrable (C5) |
| `/briefing` | un texte rédigé par un modèle sur une valeur (C9) |
| `/question` | une réponse tirée des articles collectés, avec ses sources, ou un refus |
| `/sante` | les signaux de la vigie et leurs verdicts |
| `/exercice/*` | poser ou retirer une panne simulée du fournisseur du modèle, 20 minutes au plus |
| `/audit/mcp` | journaliser un refus survenu dans la passerelle MCP |
| `/health` | le service répond, et il annonce la version et l'index qu'il sert |

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

# Carte #75, constat S1 de la revue OWASP du 03/10 (06/11/2026) : aucune réponse ne portait d'en-tête de sécurité.
# L'interface n'a ni script ni style en ligne, ni ressource externe : `default-src 'self'` tient sur les cinq écrans
# (`tests/test_entetes_securite.py`, en navigateur). Les pages de documentation de FastAPI chargent leur script depuis un
# CDN avec un script en ligne : elles gardent les autres en-têtes, sans politique de contenu (décision D7, constat S2).
POLITIQUE_DE_CONTENU = "default-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
ENTETES_DE_SECURITE = {
    "Strict-Transport-Security": "max-age=31536000",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}
# Les pages exactes, pas un préfixe (relecture de sécurité du 06/11) : `/docs-x` garde la politique.
PAGES_DE_DOCUMENTATION = frozenset({"/docs", "/docs/oauth2-redirect", "/redoc"})


def poser_les_entetes_de_securite(reponse, chemin: str) -> None:
    for nom, valeur in ENTETES_DE_SECURITE.items():
        reponse.headers[nom] = valeur
    if chemin not in PAGES_DE_DOCUMENTATION:
        reponse.headers["Content-Security-Policy"] = POLITIQUE_DE_CONTENU


# Éco-conception, carte #74 (F1) : la compression est déclarée AVANT le middleware ci-dessous, pour être la plus proche
# de l'application : elle voit la réponse entière et respecte son seuil de 1 000 octets. Déclarée après, elle recevait
# la réponse en morceaux et compressait tout, même les 388 octets de `/health` (mesuré le 06/11).
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def attribuer_un_identifiant_de_requete(request: Request, call_next):
    """Pose `X-Request-ID` sur TOUTE réponse, y compris 403 et 502 : une erreur sans
    identifiant est une erreur qu'on ne retrouve pas."""
    debut = time.perf_counter()
    propose = request.headers.get("X-Request-ID", "")
    identifiant = propose if IDENTIFIANT_CLIENT_SAIN.match(propose) else uuid.uuid4().hex
    jeton = _request_id_courant.set(identifiant)
    echappee = False
    try:
        reponse = await call_next(request)
    except Exception as erreur:  # noqa: BLE001
        echappee = True
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
    poser_les_entetes_de_securite(reponse, request.url.path)
    # Sprint 5 (étape 1) : les appels qui n'entrent jamais dans la route (403 de la clé, 422 de la saisie, 429 du
    # débit) et les erreurs qui s'en échappent sont comptés ICI ; tout le reste l'est par la route elle-même, qui connaît
    # le résultat métier (monitorage/compteurs.py). Un 422 levé dans `/briefing` (valeur inconnue) n'y est pas compté.
    if request.url.path in compteurs.ROUTES_MESUREES:
        duree_ms = int((time.perf_counter() - debut) * 1000)
        if echappee:
            compteurs.COMPTEURS.noter(request.url.path, 500, "erreur", "ERREUR_INTERNE", duree_ms)
        elif reponse.status_code in compteurs.CODES_DE_REJET:
            compteurs.COMPTEURS.noter(request.url.path, reponse.status_code, None, f"HTTP_{reponse.status_code}",
                                      duree_ms)
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

    Le remplacement volontaire d'un défaut par un **refus à l'authentification** : mieux vaut
    une API qui refuse de servir qu'une API qui sert n'importe qui. Le message dit
    exactement quoi faire — un garde-fou qui bloque sans expliquer se contourne.
    """
    cle = os.getenv("RITA_API_KEY")
    if not cle:
        raise RuntimeError(
            "RITA_API_KEY absente. L'API ne peut autoriser aucun acces protege sans cle : une valeur par "
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


def verify_api_key(request: Request, api_key: str = Security(API_KEY_HEADER)):
    """Autorisation par clé d'API.

    Volontairement simple : une seule clé, comparée à `RITA_API_KEY`. RITA est
    mono-utilisateur (décision D10) — un système de comptes serait de la complexité sans
    besoin. La contrepartie est assumée : pas de révocation partielle, pas de traçabilité
    par appelant.
    """
    # `compare_digest` et non `!=` : une comparaison de chaînes ordinaire s'arrête au
    # premier caractère différent, et son temps d'exécution renseigne donc un attaquant
    # sur le nombre de caractères devinés. La différence est infime, la parade gratuite.
    # Constat S3 (07/11/2026) : une adresse qui a envoyé trop de mauvaises clés reçoit 429 avant toute comparaison.
    refuser_si_bloquee(request)
    if not api_key or not secrets.compare_digest(api_key, cle_attendue()):
        # Sprint 4 (C2) : critère 4 du contrat du sprint 1. Un refus laisse UNE ligne de journal : l'identifiant de
        # requête (le même que l'en-tête X-Request-ID), la route et le motif. Jamais la clé, ni un morceau, ni sa
        # longueur : elle pourrait être une vraie clé mal collée, et la journaliser la ferait fuiter.
        motif = "absente" if not api_key else "invalide"
        logger.warning("cle d'API refusee : request_id=%s route=%s motif=%s",
                       request_id_courant(), request.url.path, motif)
        if api_key:   # une clé absente n'est pas un essai : l'interface n'envoie jamais de clé vide
            noter_mauvaise_cle(request)
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

# --- Sprint 3 : les questions libres (tâche A5) ----------------------------------------------------------------------
# Même garde-fou de conception : la clé est posée sur le routeur entier. Le montage des fichiers statiques sur « / »
# reste le DERNIER de ce fichier, sinon il capterait `/question` avant la route.
# Sprint 4 (C3) : la limite de débit vient APRÈS la clé, dans cet ordre : un appel sans clé valide ne consomme pas le
# quota. Le même compteur sert `/briefing` (api/limiteur.py).
app.include_router(routeur_question, dependencies=[Depends(verify_api_key), Depends(limiter_debit)])

# --- Sprint 5 (étape 2) : les signaux de la vigie --------------------------------------------------------------------
# La clé sur le routeur entier, comme pour /donnees ; pas de limite de débit : /sante n'appelle jamais le modèle.
app.include_router(routeur_sante, dependencies=[Depends(verify_api_key)])

# --- Sprint 5 (étape 6) : la panne simulée ----------------------------------------------------------------------------
# Une clé à part (X-Cle-Exercice), jamais la clé des questions ; sans RITA_CLE_EXERCICE, les routes sont désactivées.
app.include_router(routeur_exercice, dependencies=[Depends(verifier_cle_exercice)])


# --- Refonte 001, tâche 3 (exigence R4) : le diagnostic du briefing --------------------------------------------------
# L'écran du briefing montre qui a rédigé, d'après quel cours et quelles sources. Tout vient de ce que le graphe a
# réellement fait : rien n'est reconstruit, rien n'est deviné ; ce qui manque vaut `null`.

FUSEAU_DE_REFERENCE = ZoneInfo("Europe/Paris")   # `tzdata` est une dépendance de pandas : présent dans l'image aussi
TEXTE_AUCUN_FOURNISSEUR = "Aucun fournisseur de modèle n'a répondu."


def aujourd_hui_a_paris() -> date:
    """La date de référence de l'âge du cours : le jour à Paris au moment de la réponse (remplacée dans les tests)."""
    return datetime.now(FUSEAU_DE_REFERENCE).date()


def _lien_sur(lien) -> str | None:
    """Un lien n'est rendu que s'il est http(s) et nomme un hôte : `javascript:`, `data:` et le reste deviennent null,
    pour qu'aucun lien piégé ne devienne cliquable à l'écran."""
    if not isinstance(lien, str) or not lien:
        return None
    try:
        morceaux = urlparse(lien)
    except ValueError:
        return None
    return lien if morceaux.scheme.lower() in ("http", "https") and morceaux.netloc else None


def sources_du_prompt(passages: list[dict] | None) -> list[dict]:
    """Un élément par article réellement transmis au modèle, dans l'ordre : le même filtre que le prompt
    (`articles_surs`), puis un seul élément par `article_id`. Deux articles distincts ne sont jamais fusionnés, même
    sans lien. Jamais le texte de l'article."""
    vus: set = set()
    sources = []
    for passage in articles_surs(passages):
        article_id = passage.get("article_id")
        if article_id is not None and article_id in vus:
            continue
        vus.add(article_id)
        sources.append({"titre": passage.get("titre"), "source": passage.get("source"),
                        "publie_le": passage.get("publie_le"), "lien": _lien_sur(passage.get("lien"))})
    return sources


def _date_iso(valeur) -> date | None:
    if isinstance(valeur, date):
        return valeur
    try:
        return date.fromisoformat(valeur) if isinstance(valeur, str) else None
    except ValueError:
        return None


def construire_diagnostic(resultat: dict, duree_ms: int, reference: date) -> dict:
    """Le bloc `diagnostic` de la réponse : qui a rédigé (`modele_info`, rempli par le graphe), la date du cours telle
    que la base l'a enregistrée, son âge par rapport à `reference`, et les sources transmises au modèle.

    Les séances écoulées ne se comptent qu'avec le calendrier Euronext, le seul que RITA modélise : pour Londres ou
    New York, `jours_bourse_ecoules` et `calendrier` valent null, et l'âge en jours de calendrier reste donné.
    """
    info = resultat.get("modele_info") or {}
    date_cours = _date_iso((resultat.get("indicateurs") or {}).get("date_cours"))
    try:
        euronext = place_de_cotation(resultat.get("ticker") or "") == "Euronext"
    except ValueError:
        euronext = False
    compter = date_cours is not None and euronext
    return {
        "fournisseur": info.get("fournisseur"),
        "modele": info.get("modele"),
        "tentatives": info.get("tentatives") or [],
        "duree_ms": duree_ms,
        "date_cours": date_cours.isoformat() if date_cours else None,
        "age_calendaire_jours": (reference - date_cours).days if date_cours else None,
        "jours_bourse_ecoules": jours_ouvres_ecoules(date_cours, reference) if compter else None,
        "calendrier": "Euronext" if compter else None,
        "sources": sources_du_prompt(resultat.get("passages")),
    }


class TentativeModele(BaseModel):
    fournisseur: str = Field(description="foundry, anthropic ou openrouter")
    reussi: bool = Field(description="jamais le message de l'erreur, qui peut recopier le prompt")


class SourceBriefing(BaseModel):
    titre: str | None
    source: str | None
    publie_le: str | None
    lien: str | None = Field(description="http(s) seulement ; null pour tout autre lien (javascript:, data:...)")


class DiagnosticBriefing(BaseModel):
    fournisseur: str | None = Field(description="le fournisseur qui a rédigé le texte")
    modele: str | None = Field(description="le modèle renvoyé par le fournisseur, null s'il ne le dit pas")
    tentatives: list[TentativeModele]
    duree_ms: int = Field(ge=0)
    date_cours: str | None = Field(description="date de la dernière séance, telle que la base l'enregistre (ISO)")
    age_calendaire_jours: int | None = Field(description="jours de calendrier entre la séance et aujourd'hui à Paris")
    jours_bourse_ecoules: int | None = Field(description="séances Euronext écoulées depuis ; null hors Euronext")
    calendrier: Literal["Euronext"] | None
    sources: list[SourceBriefing] = Field(description="un élément par article transmis au modèle, sans son texte")


class ReponseBriefing(BaseModel):
    ticker: str
    price: float
    change_pct: float
    currency: str
    briefing: str
    conforme_amf: bool
    motifs_amf: list[str]
    articles_transmis: int
    diagnostic: DiagnosticBriefing


# --- C9 : le briefing rédigé ------------------------------------------------
@app.post("/briefing", tags=["briefing IA"],
          summary="Générer un briefing rédigé pour une valeur",
          responses={
              200: {"model": ReponseBriefing, "description": "Le briefing, son verdict AMF et son diagnostic"},
              503: {"description": "Aucun fournisseur de modèle n'a répondu (code AUCUN_FOURNISSEUR)",
                    "content": {"application/json": {"example": {"detail": {
                        "code": "AUCUN_FOURNISSEUR", "message": TEXTE_AUCUN_FOURNISSEUR}}}}},
              500: {"description": "Erreur interne imprévue ; le corps donne l'identifiant de requête"},
          })
def briefing(ticker: str = Query(min_length=1, max_length=20), api_key: str = Security(verify_api_key),
             _debit: None = Depends(limiter_debit)):
    """Produit un texte en français à partir des données de la valeur.

    Relève de **C9** (exposer un modèle), pas de C5 : la sortie est une rédaction, pas de
    la donnée. Le garde-fou AMF s'applique — aucune recommandation d'achat ou de vente.
    """
    request_id = request_id_courant()
    debut = time.perf_counter()
    # Sprint 4 (C1) : critère 3 du contrat du sprint 1. La longueur (1 à 20 caractères) est contrôlée par FastAPI avant
    # d'entrer ici ; une valeur absente du référentiel est refusée maintenant, avant tout appel au modèle, avec une ligne
    # de journal. `%r` neutralise une valeur saisie qui voudrait forger de fausses lignes.
    if not valeur_existe(ticker):
        logger.warning("briefing refuse : valeur inconnue : request_id=%s ticker=%r", request_id, ticker)
        raise HTTPException(status_code=422, detail="Valeur inconnue : aucun briefing n'est possible pour ce code.")
    # Une racine de trace par briefing (C11) : tout ce qui suit, y compris l'appel au modèle,
    # se range dessous, et le verdict du garde-fou y est posé. Sans clés Langfuse, `racine`
    # vaut None et rien ne change (src/traces.py). L'identifiant de requête devient celui
    # de la trace : journal et trace se retrouvent par le même identifiant.
    # Sprint 5 (étape 1) : les jetons de toutes les tentatives de ce briefing s'additionnent ici.
    compteurs.debuter_consommation()
    with traces.briefing(ticker, request_id=request_id) as racine:
        try:
            resultat = generer_briefing_complet(ticker)
        except AucunFournisseur:
            # Refonte 001 (R4) : tous les fournisseurs ont échoué. Ce n'est pas un défaut de RITA (500) mais un service
            # dont elle dépend qui ne répond pas : 503, avec un code stable que l'écran sait lire. Le message de
            # l'exception (types d'erreur par fournisseur) reste dans le journal du serveur, jamais dans la réponse.
            logger.warning("briefing en erreur 503 : aucun fournisseur : request_id=%s ticker=%r", request_id, ticker)
            compteurs.COMPTEURS.noter("/briefing", 503, "erreur", "AUCUN_FOURNISSEUR",
                                      int((time.perf_counter() - debut) * 1000), compteurs.consommation())
            raise HTTPException(status_code=503, detail={"code": "AUCUN_FOURNISSEUR",
                                                         "message": TEXTE_AUCUN_FOURNISSEUR}) from None
        if resultat["error"]:
            logger.warning("briefing en erreur 502 : request_id=%s ticker=%r",
                           request_id, ticker)
            compteurs.COMPTEURS.noter("/briefing", 502, "erreur", "BRIEFING_INDISPONIBLE",
                                      int((time.perf_counter() - debut) * 1000), compteurs.consommation())
            raise HTTPException(status_code=502, detail=resultat["error"])

        # Garde-fou de SORTIE (C17) — l'interdit AMF s'applique au texte produit, pas
        # seulement au prompt. Le prompt demande déjà « aucune recommandation » ; un prompt
        # est une consigne, pas un contrôle. Ajouté le 17/08/2026 : il était invoqué par le
        # docstring de guardrails/injection.py sans exister. Fail-closed : en cas de doute,
        # on ne diffuse pas.
        #
        # Sprint 4 (B2) : dans la même étape, le contrôle de fuite. Un briefing qui laisserait sortir un secret, une
        # valeur de configuration ou un morceau des consignes du rédacteur n'est pas diffusé (CA3.1, CA3.2).
        with traces.etape("garde-fou-sortie") as span_sortie:
            verdict = verifier_sortie(resultat["briefing"])
            fuite = verifier_fuite(resultat["briefing"], (ROLE_REDACTEUR, CONSIGNES_REDACTION))
            traces.noter_garde_fou(span_sortie, not (verdict["conforme"] and fuite["conforme"]),
                                   verdict["motifs_detectes"] + fuite["motifs_detectes"])
        traces.noter_verdict_amf(racine, resultat["ticker"], verdict["conforme"],
                                 verdict["motifs_detectes"], request_id=request_id)

    # Un refus laisse UNE ligne dans le journal (audit du 02/10/2026) : sans elle, personne ne sait
    # que le garde-fou a servi, ni pour quel motif. Jamais le texte refusé : il serait relu et
    # recopié. `%r` entoure la valeur de guillemets et neutralise les retours à la ligne, pour
    # qu'une valeur saisie par un tiers ne puisse pas forger de fausses lignes de journal.
    if not verdict["conforme"]:
        logger.warning("briefing refuse par le garde-fou de sortie : request_id=%s ticker=%r motifs=%s",
                       request_id, resultat["ticker"], ",".join(verdict["motifs_detectes"]))
    if not fuite["conforme"]:
        logger.warning("briefing refuse par le controle de fuite : request_id=%s ticker=%r motifs=%s",
                       request_id, resultat["ticker"], ",".join(fuite["motifs_detectes"]))
    # Une fuite l'emporte sur tout : son message remplace le texte, même si le contrôle AMF l'acceptait.
    texte_diffuse = verdict["texte_diffusable"] if fuite["conforme"] else fuite["texte_diffusable"]

    # Une ligne INFO par briefing servi : identifiant, valeur, verdict, durée. Jamais le texte.
    # C'est la matière première du monitorage (C20) : combien, pour qui, en combien de temps.
    duree_ms = int((time.perf_counter() - debut) * 1000)
    logger.info("briefing servi : request_id=%s ticker=%r conforme_amf=%s duree_ms=%d",
                request_id, resultat["ticker"], verdict["conforme"], duree_ms)
    # Le même ordre que le texte diffusé : une fuite l'emporte sur la non-conformité AMF.
    if not fuite["conforme"]:
        statut, motif = "refus", "FUITE_BLOQUEE"
    elif not verdict["conforme"]:
        statut, motif = "refus", "SORTIE_NON_CONFORME"
    else:
        statut, motif = "reponse", "OK"
    compteurs.COMPTEURS.noter("/briefing", 200, statut, motif, duree_ms, compteurs.consommation())

    return {
        "ticker": resultat["ticker"],
        "price": resultat["price"],
        "change_pct": resultat["change_pct"],
        "currency": resultat["currency"],
        "briefing": texte_diffuse,
        "conforme_amf": verdict["conforme"],
        "motifs_amf": verdict["motifs_detectes"],
        # Sprint 2 (14/10) : le nombre d'articles distincts transmis au modèle. Un briefing est rédigé même sans
        # article ; sans ce compte, un index vide en production passait tous les contrôles du script du serveur.
        "articles_transmis": len({p["article_id"] for p in resultat.get("passages") or []}),
        # Refonte 001 (R4) : qui a rédigé, d'après quel cours et quelles sources (construire_diagnostic).
        "diagnostic": construire_diagnostic(resultat, duree_ms, aujourd_hui_a_paris()),
    }


# --- Éco-conception, carte #74 (mesure Lighthouse et EcoIndex du 03/10, constats F1 et F3) ---------------------------
# F1 : compresser les réponses quand le navigateur l'accepte ; gain mesuré le 03/10 en gzip : statique -62 %, JSON des
# indicateurs -84 %. Sous 1 000 octets, la compression coûterait plus qu'elle ne fait gagner (`/health` reste brut).
# F3 : `favicon.ico` répondait 404 (une erreur dans la console à chaque page) ; le logo de RITA sert d'icône.
# La compression elle-même est déclarée plus haut, avant `attribuer_un_identifiant_de_requete` (voir là-bas).
@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse(Path(__file__).parent.parent / "frontend" / "logo-rita-clair.png", media_type="image/png")


# --- L'interface (C10, C17) --------------------------------------------------
# Servie par la MÊME application que l'API : même origine, donc aucune règle CORS
# à ouvrir. Une porte de moins à justifier dans la revue OWASP.
#
# Refonte 001, tâche 5 (mesuré le 04/11) : sans `Cache-Control`, Chrome gardait l'ancien `tableau-de-bord.js` à côté
# du nouveau `commun.js`, et la page montrait le vrai tableau sous la mention « Simulation ». `no-cache` : le navigateur
# demande à chaque visite si le fichier a changé ; s'il n'a pas changé, la réponse est un 304 sans corps (éco-conception).
class InterfaceToujoursRevalidee(StaticFiles):
    async def get_response(self, path, scope):
        reponse = await super().get_response(path, scope)
        reponse.headers["Cache-Control"] = "no-cache"
        return reponse


# ⚠️ Ce montage doit rester la DERNIÈRE instruction du fichier : `/` capture toutes
# les adresses restantes. Placé plus haut, il masquerait /donnees et /briefing.
app.mount("/", InterfaceToujoursRevalidee(directory=Path(__file__).parent.parent / "frontend",
                                          html=True), name="interface")

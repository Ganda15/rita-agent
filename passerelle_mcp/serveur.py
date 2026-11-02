"""Serveur MCP de RITA — trois outils de lecture, exposés à un client LLM.

Livrable visé : **E4** (C10, C15, C17) — *« intégrer l'API dans une application »*.
Consigne formateur du 28/08/2026 : le MCP est **obligatoire**.
Plan : `docs/PLAN-RAG-MCP.md`, étape 1.

## La décision qui structure tout ce fichier : on passe par HTTP

Ce serveur pourrait appeler directement `indicateurs.socle`, `sources.database`, etc. —
c'est plus court et plus rapide. **On ne le fait pas**, pour trois raisons :

1. **C10 demande d'intégrer l'API dans une application**, pas de contourner l'API.
   En passant par HTTP, cette passerelle devient un vrai **client** de RITA, exactement
   comme `frontend/app.js`. Le critère parle de *« communication avec l'API »* et
   d'*« étapes d'authentification intégrées correctement »* — appeler les modules en
   direct ne prouverait ni l'une ni l'autre.
2. **Le garde-fou 403 reste en vigueur.** Un appel sans clé échoue ici comme ailleurs.
   Une passerelle qui court-circuite l'authentification annulerait la correction OWASP
   API2 du 18/08 (`evidence/C21/INC-001`).
3. **Un seul chemin à tester.** Deux chemins d'accès aux données, c'est deux
   comportements qui divergent le jour où l'un change.

Le coût est un aller-retour HTTP local — quelques millisecondes. C'est le prix de la
preuve.

## Le portefeuille : démonstration déclarée ET vérifiée (chapitre « Données », cas A04)

Jusqu'au 03/10/2026, `rita_portefeuille` rendait ce que l'API rendait, et sa description
promettait un « jeu de démonstration anonymisé » sans rien vérifier. Or la table `position`
contient ce qu'on y a importé : le jeu d'exemple, ou le portefeuille réel d'Era, qui sont des
données personnelles financières. La matrice d'accès du chapitre (§3.3) dit : application hôte
MCP → portefeuille réel **REFUS par défaut**, portefeuille fictif seulement « si connecté au jeu
fictif vérifié ». Deux verrous, donc :

1. **Déclaré** : la variable `RITA_MCP_PORTEFEUILLE=demo` dans l'environnement de la passerelle.
   Absente ou autre : refus `NOT_AUTHORIZED` **sans appeler l'API**.
2. **Vérifié** : les positions rendues par l'API doivent être exactement le jeu attendu,
   `passerelle_mcp/jeu_demo_attendu.csv`. Sinon : refus, et **aucune donnée rendue**, pas même le
   total. Une phrase dans une description n'est pas une preuve ; une comparaison l'est.

### #152 (recette du 01/11/2026) : ce que « exactement » veut dire

Jusqu'au 01/11, le verrou comparait des **ensembles** de couples (ticker, quantité) aux dix lignes de
`data/positions-exemple.csv`. Deux défauts : il refusait le jeu réellement importé (l'import en garde
sept : TTE.PA, AAPL et MSFT sont hors univers), et il acceptait les mêmes tickers et quantités avec
d'autres prix de revient, ou une ligne en double. Depuis :

- **La référence** est le jeu tel que l'import le produit, versionné : sept positions, toutes
  reconnues par leur ticker, aucune par un alias. `tests/test_jeu_demo_mcp_base.py` rejoue le vrai
  import sur la base de test et vérifie que ce fichier en est le résultat.
- **La comparaison** porte sur quatre champs (ticker, quantité, prix de revient, devise), en décimal
  exact, et compte les doublons (`Counter`, pas `set`). Aucun arrondi : un flottant reçu est relu par
  `str()`, sa représentation la plus courte, celle-là même que le JSON a transportée.
- **La réponse est reconstruite** : les treize champs de la requête R1, nommés un par un ; un champ
  ajouté demain à l'API ne sort pas par cette passerelle sans être ajouté ici. Le total est recalculé
  sur les positions vérifiées, jamais repris de l'API.
- **Le contenu est vérifié, pas seulement le nom des champs** (seconde revue du 01/11) : chaque champ
  a le type que la requête R1 produit, et les champs ne se contredisent pas (un cours sans date, un taux
  manquant avec une valorisation chiffrée). Une valeur légitimement indisponible reste `null`.
- **Le doute vaut refus** : jeu attendu absent ou vide, champ indispensable manquant ou mal formé,
  compte annoncé différent des lignes rendues, position close dans la base (mode strict : une position
  close n'est pas forcément personnelle, mais elle n'appartient pas au jeu attendu).

## Le contrat d'erreur

Repris du brief Sorabel : chaque réponse porte `success`, et une erreur porte un **code
typé** plutôt qu'un texte libre. Un modèle qui lit `NOT_AUTHORIZED` sait quoi faire ;
un modèle qui lit « quelque chose s'est mal passé » réessaie au hasard.
"""
from __future__ import annotations

import csv
import logging
import math
import os
import uuid
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

# ⚠️ Sans cette ligne, le serveur ne lit pas le `.env` : ni l'adresse de l'API, ni la
# clé. C'est le défaut qui s'est répété trois fois dans ce dépôt — `db/importer.py`
# le 17/08, `indicateurs/socle.py`, `monitorage/fraicheur.py` le 25/08.
# *Un module qui ne trouve pas sa configuration n'est pas fonctionnel.*
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

URL_API = os.getenv("RITA_API_URL", "http://127.0.0.1:8000")
logger = logging.getLogger(__name__)

# Identité TECHNIQUE posée par le système, jamais une autorisation fondée sur un nom fourni par
# le modèle (chapitre « Données » §3.7). L'API journalise les appels qui la portent (plan 62).
CLIENT_ID = "passerelle-mcp"

# Délai volontairement court : ces trois outils lisent des données déjà calculées.
# Au-delà, c'est que l'API ne répond pas — mieux vaut le dire que faire patienter.
DELAI_SECONDES = 15.0

# Le seul mot qui autorise `rita_portefeuille` (voir la docstring du module, cas A04).
VARIABLE_PORTEFEUILLE = "RITA_MCP_PORTEFEUILLE"


def _demonstration_declaree() -> bool:
    return os.getenv(VARIABLE_PORTEFEUILLE, "").strip().lower() == "demo"


# #152 : la référence du verrou (voir la docstring du module), et ce qui en sort.
JEU_DEMO_ATTENDU = Path(__file__).resolve().parent / "jeu_demo_attendu.csv"
CHAMPS_SERVIS = ("ticker", "nom_officiel", "statut_qualite", "quantite", "pru", "devise", "date_cours", "cours",
                 "investi_eur", "valorisation_eur", "performance_pct", "taux_pour_eur", "taux_manquant")


def _decimal(valeur: Any) -> Decimal | None:
    """Un nombre en décimal exact, ou None s'il n'en est pas un (booléen, texte vide, NaN, infini)."""
    if valeur is None or isinstance(valeur, bool):
        return None
    try:
        nombre = Decimal(str(valeur))
    except (InvalidOperation, ValueError):
        return None
    return nombre if nombre.is_finite() else None


def _entier(valeur: Any) -> int | None:
    return valeur if isinstance(valeur, int) and not isinstance(valeur, bool) else None


def _quadruplet(position: dict[str, Any]) -> tuple[str, Decimal, Decimal, str] | None:
    """Ce qui identifie une position : ticker, quantité, prix de revient, devise ; None si l'un manque."""
    ticker, devise = position.get("ticker"), position.get("devise")
    quantite, pru = _decimal(position.get("quantite")), _decimal(position.get("pru"))
    if not isinstance(ticker, str) or not isinstance(devise, str) or quantite is None or pru is None:
        return None
    return ticker, quantite, pru, devise


def _jeu_attendu() -> Counter:
    """Le jeu versionné ; une ligne illisible lève une erreur, que l'appelant traite comme un refus."""
    with JEU_DEMO_ATTENDU.open(encoding="utf-8", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    attendu: Counter = Counter()
    for ligne in lignes:
        quadruplet = _quadruplet(ligne)
        if quadruplet is None:
            raise ValueError(f"ligne illisible dans {JEU_DEMO_ATTENDU.name}")
        attendu[quadruplet] += 1
    return attendu


def _nombre_json(valeur: Any) -> bool:
    return isinstance(valeur, (int, float)) and not isinstance(valeur, bool) and math.isfinite(valeur)


def _date_iso(valeur: Any) -> bool:
    if not isinstance(valeur, str) or len(valeur) != 10:
        return False
    try:
        date.fromisoformat(valeur)
    except ValueError:
        return False
    return True


def _position_coherente(p: dict[str, Any]) -> bool:
    """Le contenu de chaque champ et leur cohérence, tels que la requête R1 les produit (#152, seconde revue du 01/11).

    Une valeur légitimement indisponible reste `null` ; un objet ou un texte à la place d'un nombre, ou deux champs qui
    se contredisent, font refuser : la passerelle ne transmet pas ce qu'elle ne sait pas expliquer.
    """
    if not all(isinstance(p[c], str) and p[c] for c in ("ticker", "nom_officiel", "statut_qualite", "devise")):
        return False
    if not (_nombre_json(p["quantite"]) and _nombre_json(p["pru"]) and isinstance(p["taux_manquant"], bool)):
        return False
    if not all(p[c] is None or _nombre_json(p[c])
               for c in ("cours", "investi_eur", "valorisation_eur", "performance_pct", "taux_pour_eur")):
        return False
    if not (p["date_cours"] is None or _date_iso(p["date_cours"])):
        return False
    # Le cours et sa date vont ensemble (jointure latérale) ; sans cours, ni valorisation ni performance.
    sans_cours = p["cours"] is None
    if (p["date_cours"] is None) != sans_cours or (sans_cours and p["valorisation_eur"] is not None):
        return False
    if sans_cours != (p["performance_pct"] is None):
        return False
    # Le taux : l'euro se convertit par 1 ; un taux manquant rend les montants en euros indisponibles, et lui seul.
    if p["devise"] == "EUR" and (p["taux_manquant"] or p["taux_pour_eur"] != 1):
        return False
    if p["taux_manquant"] != (p["taux_pour_eur"] is None):
        return False
    if p["taux_manquant"]:
        return p["investi_eur"] is None and p["valorisation_eur"] is None
    return p["investi_eur"] is not None and (sans_cours or p["valorisation_eur"] is not None)


def _total_eur(positions: list[dict[str, Any]]) -> float | None:
    """La somme des valorisations des positions vérifiées ; None dès qu'une ligne n'en a pas (plan 65)."""
    valeurs = [_decimal(p["valorisation_eur"]) for p in positions]
    if any(v is None for v in valeurs):
        return None
    return float(sum(valeurs, Decimal(0)))


def _reponse_de_demonstration(donnees: Any) -> dict[str, Any] | None:
    """La réponse à servir si l'API rend exactement le jeu de démonstration attendu ; sinon None, et c'est un refus."""
    try:
        attendu = _jeu_attendu()
    except Exception:  # noqa: BLE001, un doute sur la référence se résout par un refus
        return None
    if not attendu or not isinstance(donnees, dict):
        return None
    positions = donnees.get("positions")
    if not isinstance(positions, list) or _entier(donnees.get("nb")) != len(positions):
        return None
    if _entier(donnees.get("positions_closes")) != 0:
        return None
    servies: Counter = Counter()
    for position in positions:
        if not isinstance(position, dict) or any(champ not in position for champ in CHAMPS_SERVIS):
            return None
        if not _position_coherente(position):
            return None
        quadruplet = _quadruplet(position)
        if quadruplet is None:
            return None
        servies[quadruplet] += 1
    if servies != attendu:
        return None
    verifiees = [{champ: p[champ] for champ in CHAMPS_SERVIS} for p in positions]
    return {"nb": len(verifiees), "total_eur": _total_eur(verifiees),
            "positions_sans_taux": sum(1 for p in verifiees if p["taux_manquant"] is True),
            "positions": verifiees}

serveur = MCPServer(
    name="rita",
    title="RITA — suivi et analyse de portefeuille",
    instructions=(
        "Outils de lecture sur RITA. Le portefeuille n'est servi qu'en démonstration "
        "déclarée et vérifiée (jeu d'exemple du dépôt) ; un portefeuille réel ne sort "
        "jamais par cette passerelle. RITA fournit des indicateurs, des faits "
        "chiffrés — et ne formule JAMAIS de recommandation d'achat ou de vente. "
        "Toujours vérifier la fraîcheur des données avant de commenter un chiffre."
    ),
)

# Ces trois outils lisent et ne modifient rien. Les annotations le déclarent au client,
# qui peut alors les appeler sans demander de confirmation à l'utilisateur.
LECTURE_SEULE = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    idempotent_hint=True,
    open_world_hint=True,   # les données viennent d'un service externe (l'API RITA)
)


def _cle_api() -> str:
    """La clé d'API, lue dans l'environnement — **sans valeur par défaut**.

    Même règle que `api/main.py` depuis la correction OWASP API2 du 18/08 : une clé
    par défaut n'est pas une clé, c'est une porte ouverte documentée. Le serveur
    refuse de démarrer plutôt que de servir n'importe qui.
    """
    cle = os.getenv("RITA_API_KEY")
    if not cle:
        raise RuntimeError(
            "RITA_API_KEY absente. La passerelle MCP refuse de demarrer sans cle : "
            "elle transmet l'identite a l'API, elle ne la remplace pas.\n"
            "  Ajouter RITA_API_KEY=<votre cle> au fichier .env"
        )
    return cle


def _erreur(code: str, message: str) -> dict[str, Any]:
    """Une erreur typée, jamais un texte libre."""
    return {"success": False, "error": {"code": code, "message": message}}


def _entetes(outil: str) -> dict[str, str]:
    """La clé (l'identité transmise à l'API) et, depuis le plan 62, qui appelle et pour quel outil."""
    return {"X-API-Key": _cle_api(), "X-Client-Id": CLIENT_ID, "X-Outil": outil}


async def _signaler_refus(outil: str, code: str) -> None:
    """Un refus pris ici, avant tout appel métier, part quand même au journal : par l'API
    (`POST /audit/mcp`), jamais par du SQL d'ici (plan 62, décision D2). Fail-safe : une panne
    du signalement ne change pas la réponse à l'utilisateur, elle laisse une ligne WARNING."""
    try:
        async with httpx.AsyncClient(timeout=DELAI_SECONDES) as client:
            await client.post(f"{URL_API}/audit/mcp", headers=_entetes(outil),
                              json={"outil": outil, "statut": "refuse", "code_erreur": code,
                                    "request_id": uuid.uuid4().hex})
    except Exception as erreur:  # noqa: BLE001
        logger.warning("refus MCP non signale a l'API : outil=%s code=%s : %s", outil, code,
                       f"{type(erreur).__name__}: {erreur}"[:120])


async def _lire(chemin: str, params: dict[str, Any] | None = None, outil: str = "") -> dict[str, Any]:
    """Appelle un point de terminaison de RITA et rend une réponse structurée.

    Toute la gestion d'erreur est ici, pas dupliquée dans chaque outil : trois outils
    qui traitent les erreurs chacun à leur façon, ce sont trois comportements qui
    divergeront.
    """
    entetes = _entetes(outil or chemin)
    url = f"{URL_API}{chemin}"

    try:
        async with httpx.AsyncClient(timeout=DELAI_SECONDES) as client:
            reponse = await client.get(url, headers=entetes, params=params)
    except httpx.ConnectError:
        return _erreur(
            "SERVICE_INDISPONIBLE",
            f"L'API RITA ne repond pas sur {URL_API}. Verifier qu'elle est demarree "
            f"(uvicorn api.main:app) ou ajuster RITA_API_URL.",
        )
    except httpx.TimeoutException:
        return _erreur(
            "DELAI_DEPASSE",
            f"L'API RITA n'a pas repondu en {DELAI_SECONDES:.0f} s sur {chemin}.",
        )

    if reponse.status_code == 403:
        return _erreur(
            "NOT_AUTHORIZED",
            "Cle d'API refusee par RITA. Verifier RITA_API_KEY dans le .env.",
        )
    if reponse.status_code == 404:
        return _erreur("NOT_FOUND", f"Aucune donnee pour {chemin}.")
    if reponse.status_code >= 400:
        return _erreur(
            "ERREUR_API",
            f"L'API RITA a repondu {reponse.status_code} sur {chemin}.",
        )

    return {"success": True, "data": reponse.json()}


@serveur.tool(
    name="rita_fraicheur",
    title="Fraîcheur des données de RITA",
    description=(
        "Indique de quand datent les données de RITA : dernière séance de bourse "
        "enregistrée, retard en jours ouvrés, et nombre de lignes par table. "
        "À appeler EN PREMIER avant de commenter un chiffre : des indicateurs "
        "calculés sur des cours périmés induisent en erreur."
    ),
    annotations=LECTURE_SEULE,
)
async def rita_fraicheur() -> dict[str, Any]:
    return await _lire("/donnees/fraicheur", outil="rita_fraicheur")


@serveur.tool(
    name="rita_portefeuille",
    title="Portefeuille valorisé",
    description=(
        "Les positions du portefeuille de démonstration, valorisées et converties en "
        "euros, avec le total. Servi seulement si la passerelle est déclarée en "
        "démonstration (RITA_MCP_PORTEFEUILLE=demo) ET si les positions sont bien le jeu "
        "d'exemple du dépôt ; sinon NOT_AUTHORIZED, sans aucune donnée."
    ),
    annotations=LECTURE_SEULE,
)
async def rita_portefeuille() -> dict[str, Any]:
    # Verrou 1 : déclaré. Refus AVANT tout appel : l'API n'a même pas à répondre.
    if not _demonstration_declaree():
        await _signaler_refus("rita_portefeuille", "NOT_AUTHORIZED")
        return _erreur(
            "NOT_AUTHORIZED",
            f"Le portefeuille n'est servi qu'en demonstration declaree : poser "
            f"{VARIABLE_PORTEFEUILLE}=demo dans l'environnement de la passerelle. Un portefeuille "
            f"reel ne sort jamais par MCP (matrice d'acces du chapitre Donnees, section 3.3).",
        )
    reponse = await _lire("/donnees/portefeuille", outil="rita_portefeuille")
    if not reponse.get("success"):
        return reponse
    # Verrou 2 : vérifié. Si ce n'est pas le jeu attendu, rien ne sort, pas même le total.
    servie = _reponse_de_demonstration(reponse["data"])
    if servie is None:
        await _signaler_refus("rita_portefeuille", "NOT_AUTHORIZED")
        return _erreur(
            "NOT_AUTHORIZED",
            "Les positions servies par l'API ne sont pas le jeu de demonstration attendu "
            "(passerelle_mcp/jeu_demo_attendu.csv, import de data/positions-exemple.csv) : refus, "
            "aucune donnee rendue. Importer le jeu d'exemple dans une base sans autre position, "
            "ou retirer la declaration de demonstration.",
        )
    return {"success": True, "data": servie}


@serveur.tool(
    name="rita_indicateurs",
    title="Indicateurs de marché",
    description=(
        "Indicateurs par valeur : cours, performances (1 jour, 1 semaine, 1 mois, "
        "depuis le 1er janvier, 1 an), moyennes mobiles 20 et 50 séances, volume "
        "moyen, distance au plus haut sur un an. "
        "Le champ 'cotation_perimee' signale une valeur dont la dernière cotation "
        "est ancienne (radiée) : ses performances ne veulent alors plus rien dire. "
        "RITA rend des FAITS, jamais un conseil d'achat ou de vente."
    ),
    annotations=LECTURE_SEULE,
)
async def rita_indicateurs(ticker: str | None = None) -> dict[str, Any]:
    """Indicateurs pour un ticker (ex. « MC.PA »), ou pour toutes les valeurs si omis."""
    return await _lire("/donnees/indicateurs", {"ticker": ticker} if ticker else None, outil="rita_indicateurs")


def main() -> None:
    """Démarre la passerelle sur l'entrée/sortie standard (*stdio*).

    `stdio` et non HTTP : le client LLM (Claude Desktop, un agent local) lance ce
    programme comme un sous-processus et lui parle par ses tubes d'entrée/sortie.
    Rien n'est exposé sur le réseau — c'est le transport le plus sûr pour un serveur
    local, et il ne demande aucun port ouvert.
    """
    _cle_api()      # panne au démarrage si la clé manque, pas au premier appel
    serveur.run(transport="stdio")


if __name__ == "__main__":
    main()

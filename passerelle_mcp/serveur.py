"""Serveur MCP de RITA — trois outils de lecture, exposés à un client LLM.

Livrable visé : **E4** (C10, C15, C17) — *« intégrer l'API dans une application »*.
Consigne formateur du 28/08/2026 : le MCP est **obligatoire**.
Plan : `docs/PLAN-RAG-MCP.md`, étape E1.

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

## Le contrat d'erreur

Repris du brief Sorabel : chaque réponse porte `success`, et une erreur porte un **code
typé** plutôt qu'un texte libre. Un modèle qui lit `NOT_AUTHORIZED` sait quoi faire ;
un modèle qui lit « quelque chose s'est mal passé » réessaie au hasard.
"""
from __future__ import annotations

import os
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

# Délai volontairement court : ces trois outils lisent des données déjà calculées.
# Au-delà, c'est que l'API ne répond pas — mieux vaut le dire que faire patienter.
DELAI_SECONDES = 15.0

serveur = MCPServer(
    name="rita",
    title="RITA — suivi et analyse de portefeuille",
    instructions=(
        "Outils de lecture sur le portefeuille RITA (données de démonstration "
        "anonymisées, valeurs françaises). RITA fournit des indicateurs — des faits "
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


async def _lire(chemin: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Appelle un point de terminaison de RITA et rend une réponse structurée.

    Toute la gestion d'erreur est ici, pas dupliquée dans chaque outil : trois outils
    qui traitent les erreurs chacun à leur façon, ce sont trois comportements qui
    divergeront.
    """
    entetes = {"X-API-Key": _cle_api()}
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
    return await _lire("/donnees/fraicheur")


@serveur.tool(
    name="rita_portefeuille",
    title="Portefeuille valorisé",
    description=(
        "Les positions du portefeuille, valorisées et converties en euros, avec le "
        "total. Jeu de démonstration anonymisé — ce n'est pas un portefeuille réel."
    ),
    annotations=LECTURE_SEULE,
)
async def rita_portefeuille() -> dict[str, Any]:
    return await _lire("/donnees/portefeuille")


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
    return await _lire("/donnees/indicateurs", {"ticker": ticker} if ticker else None)


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

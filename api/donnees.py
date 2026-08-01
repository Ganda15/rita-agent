"""API REST de mise à disposition du jeu de données (C5).

C5 : « Développer une API mettant à disposition **le jeu de données** en utilisant
l'architecture REST afin de permettre l'exploitation du jeu de données par les autres
composants du projet. »

## La distinction qui compte

`/briefing` expose un **texte rédigé par un modèle** — c'est C9 (exposer un modèle d'IA).
Les points de terminaison ci-dessous exposent **la donnée elle-même**, brute et filtrable,
pour qu'un autre composant puisse la consommer. C'est ce que C5 demande.

## Les 5 critères de C5 et où ils sont traités

| Critère | Où |
|---|---|
| Documentation couvre **tous** les points de terminaison | docstrings + `summary` -> OpenAPI |
| Documentation couvre l'authentification / l'autorisation | `verify_api_key` + `dependencies=` |
| Documentation respecte un standard (**OpenAPI**) | généré par FastAPI sur `/openapi.json` |
| API fonctionnelle : **restreint** l'accès par autorisation | 403 sans en-tête `X-API-Key` |
| API fonctionnelle : permet de récupérer **l'ensemble** des données nécessaires | 6 points de terminaison couvrant les 4 tables du jeu |

## Pourquoi la pagination est obligatoire, pas optionnelle

`cotation` compte 273 611 lignes. Un `GET /donnees/cotations` sans limite renverrait des
dizaines de mégaoctets et ferait tomber le client comme le serveur. `limite` est **plafonnée
côté serveur** — un client ne peut pas demander l'impossible.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException, Query

from sources import database

routeur = APIRouter(prefix="/donnees", tags=["jeu de données"])

LIMITE_MAX = 1000


@routeur.get("/valeurs", summary="Liste des valeurs de l'univers suivi")
def valeurs(
    statut: str | None = Query(None, description="Filtrer sur le statut qualité : "
                                                 "OK, A_VERIFIER, INCOHERENT, DELISTEE"),
    limite: int = Query(100, ge=1, le=LIMITE_MAX),
) -> dict:
    """Les sociétés suivies, avec leur statut qualité et leurs bornes d'historique.

    Le champ `statut_qualite` permet à l'appelant d'écarter lui-même les valeurs
    incohérentes — on expose l'information plutôt que de décider à sa place.
    """
    sql = """
        SELECT ticker, isin, nom_officiel, devise, statut_qualite,
               premiere_cotation, derniere_cotation
        FROM   valeur
        WHERE  (%(statut)s IS NULL OR statut_qualite = %(statut)s)
        ORDER  BY ticker
        LIMIT  %(limite)s
    """
    e = database._executer(sql, "valeurs", None, statut=statut, limite=limite)
    return {"nb": e.nb, "valeurs": e.lignes}


@routeur.get("/cotations", summary="Historique des cotations d'une valeur")
def cotations(
    ticker: str = Query(..., min_length=1, max_length=16, description="Ex. : MC.PA"),
    depuis: date | None = Query(None, description="Date de début, format AAAA-MM-JJ"),
    limite: int = Query(250, ge=1, le=LIMITE_MAX),
) -> dict:
    """Les séances d'une valeur, de la plus récente à la plus ancienne.

    `ticker` est **obligatoire** : sans lui, la requête balaierait les 273 611 lignes.
    C'est une contrainte de conception, pas un oubli — l'index `(ticker, date_seance)`
    n'est utilisable que si le ticker est fourni.
    """
    sql = """
        SELECT ticker, date_seance, ouverture, haut, bas, cloture, volume
        FROM   cotation
        WHERE  ticker = %(ticker)s
          AND  (%(depuis)s IS NULL OR date_seance >= %(depuis)s)
        ORDER  BY date_seance DESC
        LIMIT  %(limite)s
    """
    e = database._executer(sql, "cotations", None,
                           ticker=ticker, depuis=depuis, limite=limite)
    if e.nb == 0:
        raise HTTPException(status_code=404,
                            detail=f"Aucune cotation pour le ticker '{ticker}'")
    return {"ticker": ticker, "nb": e.nb, "cotations": e.lignes}


@routeur.get("/portefeuille", summary="Portefeuille valorisé, converti en euros")
def portefeuille() -> dict:
    """Chaque ligne détenue avec son dernier cours, sa valorisation et sa performance.

    ⚠️ **Données personnelles** (RGPD) — quantités et prix de revient. L'accès est restreint
    par la clé d'API au niveau du routeur. Traitement T1 du registre.
    """
    e = database.portefeuille()
    return {"nb": e.nb,
            "total_eur": float(database.total_portefeuille(e)),
            "positions": e.lignes}


@routeur.get("/mouvements", summary="Plus fortes variations de la dernière séance")
def mouvements(limite: int = Query(5, ge=1, le=50)) -> dict:
    """Les valeurs qui ont le plus bougé. Les valeurs `INCOHERENT` sont exclues."""
    e = database.mouvements(limite=limite)
    return {"nb": e.nb, "mouvements": e.lignes}


@routeur.get("/volumes-anormaux", summary="Volumes très supérieurs à la moyenne 20 séances")
def volumes(
    seuil: float = Query(2.0, ge=1.0, le=100.0, description="Multiple de la moyenne"),
    limite: int = Query(10, ge=1, le=50),
) -> dict:
    """Signal pour l'agent Technique : un fait observable, **pas une recommandation**."""
    e = database.volumes_anormaux(seuil=seuil, limite=limite)
    return {"nb": e.nb, "seuil": seuil, "volumes_anormaux": e.lignes}


@routeur.get("/articles", summary="Actualités collectées par flux RSS")
def articles(limite: int = Query(20, ge=1, le=200)) -> dict:
    """Les articles récents.

    `bloque_injection = FALSE` est **codé en dur**, ce n'est pas un paramètre : un article
    porteur d'injection ne doit jamais sortir de l'API, même si un appelant le demande.
    Il reste consultable en base pour audit — pas ici.
    """
    sql = """
        SELECT id, source, titre, lien, publie_le, resume
        FROM   article
        WHERE  bloque_injection = FALSE
        ORDER  BY publie_le DESC NULLS LAST
        LIMIT  %(limite)s
    """
    e = database._executer(sql, "articles", None, limite=limite)
    return {"nb": e.nb, "articles": e.lignes}

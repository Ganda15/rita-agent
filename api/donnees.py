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

# ⚠️ Alias obligatoire, pas cosmétique. Ce fichier définit plus bas une FONCTION
# `portefeuille()` — la route `/donnees/portefeuille`. Un `from indicateurs import
# portefeuille` serait donc écrasé par cette définition au chargement du module, et
# l'appel échouerait à l'exécution avec « 'function' object has no attribute
# 'lire_poids' ». Constaté le 19/08/2026.
#
# Renommer la route aurait été l'autre solution ; l'alias est plus sûr, car le nom
# de la fonction de route apparaît ailleurs (tests, OpenAPI).
from db import audit_mcp
from indicateurs import portefeuille as indicateurs_portefeuille_module
from indicateurs import risque as indicateurs_risque_module
from indicateurs import socle

# Même piège que ci-dessus : la route `/donnees/fraicheur` définit une FONCTION
# `fraicheur()`. Sans alias, elle écraserait le module au chargement.
from monitorage import fraicheur as monitorage_fraicheur
from sources import database
from sources.fred import SERIES

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


@routeur.get("/macro", summary="Séries macroéconomiques FRED (taux US 10 ans, inflation US, taux Fed)")
def macro(
    serie: str = Query(..., description="Code FRED : DGS10, CPIAUCSL ou DFF"),
    limite: int = Query(60, ge=1, le=LIMITE_MAX),
) -> dict:
    """Les observations d'une série macro, de la plus récente à la plus ancienne (issue #52).

    La série est vérifiée contre la liste fermée de `sources/fred.py` : une valeur hors
    liste vaut 422, jamais une requête sur un code inventé.
    """
    if serie not in SERIES:
        raise HTTPException(status_code=422,
                            detail=f"Série inconnue '{serie}'. Séries suivies : {sorted(SERIES)}")
    sql = """
        SELECT serie, date_observation, valeur
        FROM   macro_observation
        WHERE  serie = %(serie)s
        ORDER  BY date_observation DESC
        LIMIT  %(limite)s
    """
    e = database._executer(sql, "macro", None, serie=serie, limite=limite)
    return {"serie": serie, "libelle": SERIES[serie], "nb": e.nb, "observations": e.lignes}


@routeur.get("/portefeuille", summary="Portefeuille valorisé, converti en euros")
def portefeuille() -> dict:
    """Chaque ligne détenue avec son dernier cours, sa valorisation et sa performance.

    ⚠️ **Données personnelles** (RGPD) — quantités et prix de revient. L'accès est restreint
    par la clé d'API au niveau du routeur. Traitement T1 du registre.
    """
    e = database.portefeuille()
    total = database.total_portefeuille(e)
    # Plan 65 (03/10/2026, décision D1 d'Era) : une ligne sans taux de change rend le total
    # indisponible (null) et `positions_sans_taux` dit combien ; un total partiel présenté
    # comme total serait le même mensonge à une autre échelle.
    return {"nb": e.nb,
            "total_eur": float(total) if total is not None else None,
            "positions_sans_taux": database.positions_sans_taux(e),
            # Plan 66 (decision D3) : les positions closes sont comptees ici, jamais servies.
            "positions_closes": database.positions_closes(),
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


@routeur.get("/indicateurs", summary="Indicateurs de marché du lot 1 (socle)")
def indicateurs(
    ticker: list[str] | None = Query(
        None, description="Restreindre à certaines valeurs. Répétable : "
                          "?ticker=MC.PA&ticker=OR.PA. Absent = tout l'univers (111)."),
    masquer_perimees: bool = Query(
        False, description="Écarter les valeurs dont la dernière cotation dépasse "
                           "le seuil de péremption. Par défaut elles sont RENVOYÉES, "
                           "avec le drapeau cotation_perimee à vrai."),
) -> dict:
    """Les 11 indicateurs du socle, par valeur : dernier cours, 5 performances
    (1 jour, 1 semaine, 1 mois, depuis le 1ᵉʳ janvier, 1 an), MA20, MA50, ADTV20,
    et la distance au plus haut sur un an.

    **Des faits, jamais des conseils.** Chaque champ est un nombre, son unité et sa
    date. Aucun verbe d'action, aucun classement « meilleures valeurs », aucun seuil
    d'alerte : ce serait une recommandation, ce que l'interdit AMF proscrit.

    **Un champ à `null` n'est pas un zéro** : il signifie que l'historique ne remonte
    pas assez loin pour ce calcul. Une MA50 sur 30 séances serait un chiffre inventé.

    ⚠️ **`cotation_perimee`** vaut vrai quand la dernière séance connue dépasse
    `SEUIL_PERIME_JOURS`. Trois valeurs de l'univers sont radiées depuis 2018-2019 et
    portent pourtant `statut_qualite = "OK"` — le statut décrit la **qualité** de
    l'historique, pas sa **fraîcheur**. Les deux champs sont donc exposés séparément,
    et les lignes sont renvoyées par défaut : *on montre le chiffre, on signale le doute.*
    """
    lignes = socle.lire_socle(ticker or None)
    if masquer_perimees:
        lignes = [i for i in lignes if not i.cotation_perimee]

    return {
        "nb": len(lignes),
        "seuil_perime_jours": socle.SEUIL_PERIME_JOURS,
        "nb_perimees": sum(i.cotation_perimee for i in lignes),
        "indicateurs": [i.en_dict() for i in lignes],
    }


@routeur.get("/indicateurs-portefeuille",
             summary="Poids de chaque ligne et exposition par devise (lot 2)")
def indicateurs_portefeuille() -> dict:
    """Le poids de chaque ligne détenue dans le total, et l'exposition par devise.

    ⚠️ **Données personnelles (RGPD)** — ces chiffres décrivent la répartition du
    patrimoine de l'utilisateur. Traitement **T1** du registre ; l'accès est restreint
    par la clé d'API au niveau du routeur, comme `/donnees/portefeuille`.

    **Des faits, pas des conseils.** Un poids de 34,83 % est un fait. « Vous êtes trop
    concentré » serait une recommandation, que l'interdit AMF proscrit : aucun seuil
    d'alerte n'est renvoyé, aucun classement « à surveiller ».

    ⚠️ **`exposition` mesure la devise de COTATION, pas l'exposition économique.**
    LVMH est cotée en euros mais réalise une part importante de son chiffre d'affaires
    en dollars. Un portefeuille « 100 % EUR » ici peut être fortement exposé au dollar
    dans les faits — la distinction est dans la documentation parce que, sans elle, le
    chiffre se lit de travers.

    Le `total_eur` est renvoyé avec les lignes plutôt que laissé à l'appelant :
    additionner soi-même les valorisations reviendrait à refaire un calcul déjà fait,
    et deux calculs de la même chose finissent par diverger.
    """
    r = indicateurs_portefeuille_module.lire_poids_detail()
    return {
        "nb": len(r.lignes),
        "total_eur": r.total_eur,
        # Plan 65 (décision D2) : faux dès qu'une ligne n'a pas de taux ; tous les poids sont alors null.
        "complet": r.complet,
        "lignes": [l.en_dict() for l in r.lignes],
        "exposition": [e.en_dict() for e in indicateurs_portefeuille_module.lire_exposition()],
    }


@routeur.get("/indicateurs-risque", summary="Volatilité, drawdown et RSI (lot 3)")
def indicateurs_risque(
    ticker: list[str] | None = Query(
        None, description="Restreindre à certaines valeurs. Répétable : "
                          "?ticker=MC.PA&ticker=OR.PA. Absent = tout l'univers."),
) -> dict:
    """La volatilité annualisée (20 séances), le drawdown maximal (1 an) et le
    RSI 14 de chaque valeur.

    **Des faits, jamais des conseils.** « RSI = 71 » est un indicateur. « RSI > 70
    → vendre » serait une recommandation — l'exemple même que le référentiel donne
    de ce que l'interdit AMF proscrit. Aucun seuil n'est renvoyé, aucune couleur.

    **Deux méthodes de calcul, documentées parce qu'elles ne sont pas les seules
    possibles** : la volatilité utilise un rendement **logarithmique** (pas un
    rendement simple) ; le RSI utilise le lissage **récursif de Wilder** (pas une
    moyenne mobile simple). Les deux variantes circulent tout autant et donnent des
    chiffres différents — voir `db/indicateurs_risque.sql` et `indicateurs/risque.py`.

    Un champ à `null` signifie que l'historique est trop court pour ce calcul —
    jamais un zéro. `cotation_perimee` signale une dernière séance ancienne
    (> 40 jours) : la volatilité et le drawdown restent affichés (une mesure
    passée reste valide), mais `rsi_14` devient `null` — un RSI « actuel »
    calculé sur des données de 2018 ne dirait rien d'utile sur aujourd'hui.
    """
    volat = {v.ticker: v for v in indicateurs_risque_module.lire_volatilite_drawdown(ticker)}
    rsi = {r.ticker: r.rsi_14 for r in indicateurs_risque_module.lire_rsi(ticker)}

    lignes = []
    for t, v in volat.items():
        d = v.en_dict()
        d["rsi_14"] = rsi.get(t)
        lignes.append(d)

    return {"nb": len(lignes), "indicateurs": lignes}


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


@routeur.get("/fraicheur", summary="Fraîcheur du jeu de données (C20)")
def fraicheur() -> dict:
    """Répond à « vos données sont-elles à jour ? » — sans rien relancer.

    `/health` dit que le **service** tourne. Ce point de terminaison dit que
    la **donnée** vaut quelque chose : un service en ligne qui sert des cours
    vieux de trois mois est en panne, silencieusement.

    `retard_jours_ouvres` ne compte ni le samedi ni le dimanche : la Bourse de
    Paris ne cote pas le week-end, et une jauge qui passe au rouge chaque
    samedi est une jauge qu'on cesse de regarder. `statut` vaut `vert`
    (≤ 1 jour ouvré), `orange` (≤ 3) ou `rouge` au-delà.

    Le seuil vert tolère 1 jour parce que la séance du jour n'entre en base
    qu'après la collecte de 19h00 — la Bourse clôture à 17h35.
    """
    reponse = monitorage_fraicheur.lire().en_dict()
    # Plan 62 (décision D3) : une panne du journal des appels MCP se voit ici, le vecteur C20 que
    # l'écran et l'outil MCP lisent déjà ; zéro est la valeur normale.
    reponse["audit_mcp_echecs"] = audit_mcp.echecs()
    return reponse

"""Pipeline d'agrégation — toutes les sources vers un jeu de données unique (C3).

C3 : « Développer des règles d'agrégation de données issues de différentes sources en
programmant, sous forme de script, la suppression des entrées corrompues et en programmant
l'homogénéisation des formats des données afin de préparer le stockage du jeu de données
final. »

## Pourquoi ce script existe

Chaque module de `sources/` sait collecter **sa** source. Aucun ne sait les réunir. Ce
script est le seul endroit où les sources deviennent **un** jeu de données cohérent, dans
une base unique.

C'est aussi le seul endroit où l'ordre compte : les cotations ne peuvent pas entrer avant
les valeurs (clé étrangère), et les taux de change doivent exister avant qu'on valorise un
portefeuille multi-devises.

## Répartition avec db/importer.py

    db/importer.py    -> le socle : univers, alias, historique Parquet, positions CSV
    pipelines/ingest.py -> le quotidien : taux BCE, articles RSS, cours scrapés

Le socle se reconstruit rarement (32 s de téléchargement). Le quotidien tourne chaque jour.

## Structure exigée par C1

Le critère demande « un point de lancement, l'initialisation des dépendances et des
connexions externes, les règles logiques de traitement, la gestion des erreurs et des
exceptions, la fin du traitement et la sauvegarde des résultats ». Les six sont repérés
par des commentaires `# [n]`.

Usage :
    python -m pipelines.ingest                    # tout
    python -m pipelines.ingest --etapes ecb,rss   # une partie
    python -m pipelines.ingest --simulation       # sans rien écrire
"""
from __future__ import annotations

import argparse
import functools
import json
import logging
import os
import re
import subprocess
import sys
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

DSN_DEFAUT = "postgresql://rita:rita_dev_local@localhost:5432/rita"
DEVISES_SUIVIES = ("USD", "GBP", "CHF", "JPY")


@dataclass
class Bilan:
    """Ce qu'une étape a fait — ou pourquoi elle a échoué."""
    etape: str
    lues: int = 0
    ecrites: int = 0
    rejetees: int = 0
    erreur: str | None = None
    details: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.erreur is None


# =============================================================================
# [3] RÈGLES LOGIQUES DE TRAITEMENT — une fonction par source
# =============================================================================

def etape_taux_change(cur, simulation: bool,
                      periode: tuple[str, str] | None = None) -> Bilan:
    """BCE -> table `taux_change`. Homogénéisation : 1 EUR = N unités de devise.

    `periode=(debut, fin)` : rattrapage d'une plage de jours, une ligne par jour publié.
    Sans période : la dernière observation, comportement nocturne inchangé.
    """
    from sources.ecb import fetch_taux_change, fetch_taux_change_periode

    b = Bilan("taux_change (BCE)")
    lignes = []
    for devise in DEVISES_SUIVIES:
        try:
            recus = (fetch_taux_change_periode(devise, *periode) if periode
                     else [fetch_taux_change(devise)])
            lignes.extend((t["devise"], t["date"], t["valeur"]) for t in recus)
            b.lues += len(recus)
        except Exception as erreur:                       # noqa: BLE001
            b.rejetees += 1
            b.details.append(f"{devise} : {type(erreur).__name__}")

    # L'euro vaut 1 euro. Évident — mais sans cette ligne, la jointure de valorisation
    # ne trouve aucun taux pour les positions en EUR et retombe sur le COALESCE.
    # Une ligne PAR jour présent : la jointure cherche le taux du jour, pas « un » taux.
    for jour in sorted({l[1] for l in lignes}):
        lignes.append(("EUR", jour, 1.0))

    if lignes and not simulation:
        execute_values(cur, """
            INSERT INTO taux_change (devise, date_taux, valeur_pour_eur) VALUES %s
            ON CONFLICT (devise, date_taux) DO UPDATE
              SET valeur_pour_eur = EXCLUDED.valeur_pour_eur
        """, lignes)
        b.ecrites = len(lignes)
    return b


# Assez d'observations pour rattraper une semaine de collecte manquée (séries quotidiennes)
# et plusieurs mois pour l'inflation, mensuelle. `ON CONFLICT DO UPDATE` rend l'étape rejouable.
OBSERVATIONS_FRED_PAR_SERIE = 10


def etape_fred(cur, simulation: bool) -> Bilan:
    """FRED -> table `macro_observation` (issue #52, 27/09/2026).

    `sources/fred.py` récupérait déjà DGS10, CPIAUCSL et DFF, mais rien ne les stockait
    ni ne les collectait : « RITA sait collecter FRED » était vrai, « RITA a les données
    FRED » était faux. Une série en échec n'emporte pas les autres.
    """
    from datetime import date

    from sources.fred import SERIES, fetch_indicateur

    b = Bilan("macro (FRED)")
    lignes = []
    for serie in SERIES:
        try:
            recus = fetch_indicateur(serie, limite=OBSERVATIONS_FRED_PAR_SERIE)
            lignes.extend((serie, date.fromisoformat(o["date"]), o["valeur"]) for o in recus)
            b.lues += len(recus)
        except Exception as erreur:                       # noqa: BLE001
            b.rejetees += 1
            b.details.append(f"{serie} : {type(erreur).__name__}")

    # Revue automatisée, PR #54 : clé absente ou FRED indisponible, chaque série est attrapée
    # ci-dessus, mais l'étape passait pour réussie sans une ligne écrite, et /donnees/macro
    # pouvait rester vide indéfiniment avec un résumé du soir au vert. Succès partiel
    # conservé (une série sur trois suffit) ; zéro ligne = échec déclaré.
    if not lignes:
        b.erreur = "aucune observation FRED recue (" + "; ".join(b.details or ["aucune serie"]) + ")"
        return b

    if lignes and not simulation:
        execute_values(cur, """
            INSERT INTO macro_observation (serie, date_observation, valeur) VALUES %s
            ON CONFLICT (serie, date_observation) DO UPDATE
              SET valeur = EXCLUDED.valeur
        """, lignes)
        b.ecrites = len(lignes)
    return b


def etape_cotations(cur, simulation: bool) -> Bilan:
    """yfinance -> table `cotation`. Rafraîchissement **incrémental** des 111 valeurs.

    C'est l'étape qui « pérennise » la collecte au sens de C1 : elle ne retélécharge pas
    l'historique, elle comble l'écart entre la dernière séance en base et aujourd'hui.

    Trois choix à défendre :

    * **Par groupe de dernière séance.** Les tickers sont regroupés par date de dernière
      cotation connue, un téléchargement par groupe. Sans ce regroupement, une valeur
      retirée de la cote en 2018 (ZC.PA, GTO.PA…) ferait retélécharger 8 ans à *tout* le
      monde.
    * **Borne de départ INCLUSIVE.** La dernière séance en base peut avoir été capturée
      avant la clôture — mesuré : MC.PA au 29/07 valait 466,80 en base contre 467,95 à la
      clôture réelle. On la re-télécharge pour l'écraser.
    * **`ON CONFLICT DO UPDATE`.** L'étape est **rejouable** : la lancer deux fois dans la
      journée ne crée pas de doublon et corrige une capture partielle.
    """
    from collections import defaultdict

    from sources.cotations import fetch_cotations

    b = Bilan("cotations (yfinance)")

    # Dernière séance connue, valeur par valeur. LEFT JOIN : une valeur sans aucune
    # cotation doit apparaître aussi, sinon elle ne serait jamais alimentée.
    cur.execute("""
        SELECT v.ticker, MAX(c.date_seance), v.statut_qualite
        FROM   valeur v
        LEFT   JOIN cotation c ON c.ticker = v.ticker
        GROUP  BY v.ticker, v.statut_qualite
    """)
    par_date: dict = defaultdict(list)
    radiees = []
    for ticker, derniere, statut in cur.fetchall():
        # 27/09/2026 (#48) : une valeur radiée n'a plus de cours à demander. ZC.PA,
        # ELE.PA et GTO.PA échouaient chaque soir (« possibly delisted »).
        if statut == "DELISTEE":
            radiees.append(ticker)
            continue
        par_date[derniere].append(ticker)
    if radiees:
        b.details.append(f"{len(radiees)} valeur(s) radiee(s) non demandee(s) : "
                         f"{', '.join(sorted(radiees))}")

    if not par_date:
        b.erreur = "aucune valeur en base — lancer db.importer d'abord"
        return b

    lignes = []
    for derniere, tickers in par_date.items():
        if derniere is None:                    # jamais alimentée : on ne devine pas
            b.rejetees += len(tickers)
            b.details.append(f"{len(tickers)} valeur(s) sans historique — voir db.importer")
            continue
        try:
            recu = fetch_cotations(tickers, derniere)
            lignes.extend(recu)
            b.lues += len(recu)
        except Exception as erreur:                       # noqa: BLE001
            b.rejetees += len(tickers)
            b.details.append(f"depuis {derniere} : {type(erreur).__name__}")

    if lignes and not simulation:
        execute_values(cur, """
            INSERT INTO cotation
                (ticker, date_seance, ouverture, haut, bas, cloture, volume)
            VALUES %s
            ON CONFLICT (ticker, date_seance) DO UPDATE
              SET ouverture = EXCLUDED.ouverture,
                  haut      = EXCLUDED.haut,
                  bas       = EXCLUDED.bas,
                  cloture   = EXCLUDED.cloture,
                  volume    = EXCLUDED.volume
        """, [(l["ticker"], l["date_seance"], l["ouverture"], l["haut"],
               l["bas"], l["cloture"], l["volume"]) for l in lignes])
        b.ecrites = len(lignes)

    if lignes:
        b.details.append(f"seances du {min(l['date_seance'] for l in lignes)} "
                         f"au {max(l['date_seance'] for l in lignes)}")
    return b


def etape_articles(cur, simulation: bool, periode: tuple[str, str] | None = None,
                   limite_par_flux: int | None = None) -> Bilan:
    """RSS -> table `article`.

    Les articles porteurs d'injection sont **conservés et marqués**, pas supprimés :
    la colonne `bloque_injection` permet de les auditer, l'index partiel les exclut
    des lectures destinées au LLM.

    `periode=(debut, fin)` : rattrapage — les flux Google News par entreprise reçoivent
    une fenêtre `after:`/`before:` (voir `flux_par_entreprise`). Les trois flux généraux
    ne savent pas remonter dans le temps : ils rendent ce qu'ils rendent ce jour-là.
    """
    from sources.rss import collecter, flux_par_entreprise

    b = Bilan("articles (RSS)")

    # Un flux Google News par entreprise DÉTENUE, en plus des trois flux d'économie
    # générale. Mesuré le 28/08 : sur 163 articles, 22 seulement citaient une valeur
    # suivie — le RAG interrogé sur « les résultats de LVMH » ne trouvait donc rien.
    #
    # Les positions, pas les 111 valeurs suivies : 111 flux, ce seraient 111 requêtes
    # chaque soir pour des titres sur lesquels RITA ne rédige jamais.
    #
    # ⚠️ Si la lecture des positions échoue, la collecte générale continue. Une source
    # d'enrichissement ne doit pas faire tomber la collecte qu'elle enrichit — même
    # principe que le front, où une panne des indicateurs n'emporte pas le portefeuille.
    flux_entreprises: dict[str, str] = {}
    try:
        cur.execute("""
            SELECT DISTINCT v.nom_officiel
            FROM   position p
            JOIN   valeur   v ON v.ticker = p.ticker
            WHERE  v.nom_officiel IS NOT NULL
        """)
        flux_entreprises = flux_par_entreprise([l[0] for l in cur.fetchall()], periode=periode)
    except Exception as erreur:              # noqa: BLE001 — dégradation volontaire
        b.details.append(f"flux entreprises indisponibles ({type(erreur).__name__})")

    # 10 items par flux suffisent chaque soir ; sur une période de plusieurs jours,
    # Google News en rend jusqu'à 100 — on les prend tous, le dédoublonnage trie.
    if limite_par_flux is None:
        limite_par_flux = 100 if periode else 10
    r = collecter(flux_supplementaires=flux_entreprises, limite_par_flux=limite_par_flux)
    retenus, bloques = r["articles"], r["articles_bloques"]
    b.lues = r["total"]
    total_flux = len(r["flux_ok"]) + len(r["flux_echec"])
    b.details.append(f"flux OK {len(r['flux_ok'])}/{total_flux}"
                     f" (dont {len(flux_entreprises)} par entreprise)")

    lignes = [(a.source, a.titre, a.lien, a.publie_le or None, a.resume,
               a.bloque, a.motifs_injection or None)
              for a in retenus + bloques if a.lien]

    # Dédoublonnage AVANT insertion, sur DEUX clés :
    #  - le lien (deux flux reprennent souvent la même dépêche) — depuis l'origine ;
    #  - (titre normalisé, jour) — depuis le 06/09/2026, voir `cle_article`. Contre le lot
    #    ET contre ce que la base contient déjà pour les mêmes jours : deux jumeaux
    #    peuvent arriver à deux collectes différentes.
    jours = sorted({l[3][:10] for l in lignes if l[3]})
    deja_en_base: set[tuple[str, str]] = set()
    if jours:
        cur.execute("""
            SELECT titre, publie_le::date
            FROM   article
            WHERE  publie_le::date = ANY(%s::date[])
        """, (jours,))
        deja_en_base = {cle_article(titre, str(jour)) for titre, jour in cur.fetchall()}

    vus_liens, vus_cles, uniques = set(), set(), []
    for l in lignes:
        cle = cle_article(l[1], l[3])
        if l[2] in vus_liens or cle in vus_cles or cle in deja_en_base:
            continue
        vus_liens.add(l[2])
        vus_cles.add(cle)
        uniques.append(l)
    b.rejetees = len(lignes) - len(uniques)

    if uniques and not simulation:
        execute_values(cur, """
            INSERT INTO article (source, titre, lien, publie_le, resume,
                                 bloque_injection, motifs_injection)
            VALUES %s ON CONFLICT (lien) DO NOTHING
        """, uniques)
        b.ecrites = len(uniques)
    if bloques:
        b.details.append(f"{len(bloques)} bloque(s) par le garde-fou d'injection")
    return b


def cle_article(titre: str, publie_le: str | None) -> tuple[str, str]:
    """La clé d'unicité MÉTIER d'un article : (titre normalisé, jour de publication).

    Le lien ne suffit pas. Mesuré le 06/09/2026 sur 566 articles : **26 lignes en trop**
    portaient le même titre sous deux liens (Google News fournit parfois deux adresses
    pour un même papier). Deux jumeaux dans l'index occupent deux places du top-k et
    doublent le poids BM25 d'un même texte.

    Pourquoi le JOUR fait partie de la clé : 25 groupes de doublons sur 26 partagent le
    jour de publication ; le 26ᵉ — « BNP PARIBAS : la tendance baissière peut reprendre »,
    le 28/08 puis le 02/09 — est une analyse récurrente, deux papiers distincts. Sans le
    jour, on l'aurait supprimé à tort.

    Normalisation : majuscules, sans accents, tout ce qui n'est pas lettre ou chiffre
    devient un espace — « L'Oréal » et « L’Oreal » donnent la même clé.
    """
    decompose = unicodedata.normalize("NFD", (titre or "").upper())
    sans_accents = "".join(c for c in decompose if unicodedata.category(c) != "Mn")
    return (re.sub(r"[^A-Z0-9]+", " ", sans_accents).strip(), (publie_le or "")[:10])


def etape_cours_scrapes(cur, simulation: bool) -> Bilan:
    """Scraping -> table `cotation`, en complément de l'historique Parquet.

    Le scraping donne le cours du JOUR ; yfinance ne le fournit qu'avec un délai. Les deux
    sources écrivent dans la même table — c'est l'agrégation multi-source exigée par C3.
    `ON CONFLICT DO NOTHING` arbitre : l'historique officiel fait foi.

    Le rapprochement se fait par la table `SYMBOLES` du scraper : Boursorama emploie ses
    propres identifiants (`1rPMC`), Yahoo les siens (`MC.PA`). L'ISIN aurait été la clé
    naturelle, mais l'univers CSV ne le contient pas — mesuré le 01/08, `valeur.isin` était
    vide sur 111 lignes et le rapprochement échouait 3 fois sur 3.
    Le scraping, lui, fournit l'ISIN : on l'écrit donc dans `valeur` au passage.
    """
    from sources.marches import date_de_seance, derniere_seance
    from sources.scraper import SYMBOLES, collecter

    b = Bilan("cours du jour (scraping)")
    r = collecter()
    b.lues = len(r["cotations"])
    for _, nom, cause in r["echecs"]:
        b.rejetees += 1
        b.details.append(f"{nom} : {cause[:40]}")

    lignes = []
    for c in r["cotations"]:
        # Une cotation incomplète est écartée : la base impose NOT NULL sur l'OHLCV.
        if None in (c.ouverture, c.haut, c.bas, c.dernier) or not c.isin:
            b.rejetees += 1
            b.details.append(f"{c.symbole} : champs incomplets")
            continue
        ticker = SYMBOLES.get(c.symbole)
        cur.execute("SELECT ticker, isin FROM valeur WHERE ticker = %s", (ticker,))
        trouve = cur.fetchone()
        if not trouve:
            b.rejetees += 1
            b.details.append(f"{c.symbole} -> {ticker} hors univers")
            continue

        # Homogénéisation C3 : l'univers CSV ne contient pas les ISIN, le scraping oui.
        # On enrichit la fiche valeur au passage — la donnée manquante est comblée par
        # la source qui la possède, sans écraser une valeur déjà connue.
        if c.isin and not trouve[1] and not simulation:
            cur.execute("UPDATE valeur SET isin = %s WHERE ticker = %s", (c.isin, ticker))
            b.details.append(f"{ticker} : ISIN {c.isin} ajoute")

        # 27/09/2026 (#49) : `collecte_le[:10]` était la date UTC de la collecte. Un samedi,
        # la page montre la clôture du vendredi, rangée sous le samedi : une séance fictive.
        # La séance est la dernière séance Euronext à ou avant le jour de collecte à Paris.
        seance = derniere_seance(date_de_seance(c.collecte_le, trouve[0]))
        lignes.append((trouve[0], seance, c.ouverture, c.haut,
                       c.bas, c.dernier, c.volume or 0))

    if lignes and not simulation:
        execute_values(cur, """
            INSERT INTO cotation (ticker, date_seance, ouverture, haut, bas, cloture, volume)
            VALUES %s ON CONFLICT (ticker, date_seance) DO NOTHING
        """, lignes)
        b.ecrites = len(lignes)
    return b


def etape_indexation(cur, simulation: bool, dsn: str | None = None) -> Bilan:
    """Réindexe le corpus pour le RAG, après que les articles ont été écrits.

    ## Le défaut que cette étape corrige

    Mesuré le 02/09/2026 : **309 documents indexés pour 439 articles en base**. La
    collecte de 19h00 écrivait des articles tous les soirs et **rien ne réindexait
    jamais** — ni le pipeline, ni `scripts/collecte-quotidienne.cmd`. Le RAG cherchait
    donc dans un corpus périmé d'un peu plus chaque jour, sans qu'aucun signal ne le
    dise. `rag/indexation.py` annonçait pourtant, dans sa propre docstring, qu'elle est
    *« idempotente, on peut donc la relancer après chaque collecte de 19h00 »*.

    L'ordre compte : cette étape vient **après** `rss` et `scraping`, sinon elle
    indexerait le corpus d'avant la collecte du soir.

    ## Pourquoi l'import est tardif — ce n'est pas un détail de style

    `rag.indexation` importe `chromadb`, qui tire `opentelemetry`, qui tire `grpc`. Sur
    le poste d'Era, **Smart App Control refuse de charger `cygrpc`** (roue `cp314` sans
    réputation). Un import en tête de module rendrait `pipelines/ingest.py` entièrement
    inimportable, et la collecte quotidienne — taux, cotations, articles, scraping —
    **s'arrêterait complètement**. Avec l'import ici, seule cette étape échoue ; le
    pipeline attrape l'erreur, la journalise, et les autres étapes passent.

    C'est la même convention que `bigdata/session_spark.py`, qui n'importe `pyspark`
    qu'à l'intérieur d'une fonction pour la même raison.

    Le curseur n'est pas utilisé : `indexer()` ouvre sa propre connexion, parce qu'elle
    relit la table `article` entière et n'a rien à écrire en base.
    """
    del cur

    if simulation:
        return Bilan("indexation", details=["simulation : index laisse intact"])

    from rag.indexation import indexer          # tardif — voir la docstring

    # Revue automatisée, PR #1 (19/09/2026) : sans `dsn`, l'index se reconstruisait depuis
    # DATABASE_URL alors que les étapes précédentes avaient écrit dans la base de `--dsn`.
    resultat = indexer(dsn=dsn)
    return Bilan(
        "indexation",
        lues=resultat.lus,
        ecrites=resultat.indexes,
        rejetees=resultat.ignores_bloques,
        details=[f"{resultat.avec_ticker} citant une valeur suivie"],
    )


# Les étapes qui savent rattraper une période (argument `periode=(debut, fin)`).
# `cotations` n'en a pas besoin : elle est déjà incrémentale depuis la dernière séance.
ETAPES_AVEC_PERIODE = ("ecb", "rss")
# Étapes qui ouvrent leur propre connexion : le DSN du pipeline doit leur parvenir (revue automatisée, PR #1).
ETAPES_AVEC_DSN = {"indexation"}

ETAPES = {
    "ecb": etape_taux_change,
    "fred": etape_fred,
    "cotations": etape_cotations,
    "rss": etape_articles,
    "scraping": etape_cours_scrapes,
    # Après rss et scraping : on indexe ce qui vient d'être collecté, pas l'état d'avant.
    "indexation": etape_indexation,
}


# =============================================================================
# [1] POINT DE LANCEMENT · [2] CONNEXIONS · [4] ERREURS · [5] FIN · [6] SAUVEGARDE
# =============================================================================

def code_de_sortie(resultat: dict, strict: bool) -> int:
    """Code de sortie du processus : 0 toujours en mode normal (le pipeline nocturne tolère une
    étape en panne — une BCE indisponible ne doit pas marquer la nuit en échec), 1 en mode strict
    si une étape a échoué. Revue automatisée, PR #13 : `docker compose run --rm indexation` rendait 0
    avec un volume resté vide, invisible pour un opérateur ou un script."""
    if strict and any(not b.ok for b in resultat["bilans"]):
        return 1
    return 0


def executer(dsn: str | None = None, etapes: list[str] | None = None,
             simulation: bool = False, periode: tuple[str, str] | None = None) -> dict:
    """Lance le pipeline d'agrégation.

    Une étape qui échoue **n'interrompt pas** les autres : une panne de la BCE ne doit pas
    priver le briefing des actualités. Chaque étape a sa transaction — un échec en fin de
    parcours n'annule pas ce qui a réussi avant.

    `periode=(debut, fin)` : rattrapage d'une plage de jours, transmis aux seules étapes
    de `ETAPES_AVEC_PERIODE` ; les autres sont appelées exactement comme chaque soir.
    """
    choisies = etapes or list(ETAPES)
    inconnues = [e for e in choisies if e not in ETAPES]
    if inconnues:
        raise ValueError(f"Etape(s) inconnue(s) : {inconnues}. Connues : {list(ETAPES)}")

    debut = time.perf_counter()
    bilans: list[Bilan] = []

    # [2] initialisation des connexions externes
    conn = psycopg2.connect(dsn or os.getenv("DATABASE_URL", DSN_DEFAUT))
    try:
        for nom in choisies:
            try:
                fonction = ETAPES[nom]
                if periode and nom in ETAPES_AVEC_PERIODE:
                    fonction = functools.partial(fonction, periode=periode)
                if nom in ETAPES_AVEC_DSN:
                    fonction = functools.partial(fonction, dsn=dsn)
                with conn.cursor() as cur:
                    bilans.append(fonction(cur, simulation))
                # [6] sauvegarde : un commit PAR étape
                conn.rollback() if simulation else conn.commit()
            except Exception as erreur:                   # noqa: BLE001
                # [4] gestion des erreurs : on trace, on annule l'étape, on continue
                conn.rollback()
                logger.warning("Etape %s en echec — %s", nom, erreur)
                bilans.append(Bilan(nom, erreur=f"{type(erreur).__name__}: {erreur}"[:90]))
    finally:
        conn.close()                                      # [5] fin du traitement

    return {"bilans": bilans, "simulation": simulation,
            "duree_s": round(time.perf_counter() - debut, 1),
            "etapes_ok": sum(1 for b in bilans if b.ok)}


def configurer_journal() -> None:
    """Le journal du pipeline : INFO pour nous, WARNING pour `httpx`.

    Mesuré le 02/10/2026 : 6 des 40 journaux nocturnes contenaient la clé FRED en clair.
    Ce n'est pas notre code qui l'écrivait, c'est `httpx`, qui journalise chaque requête avec
    son URL complète au niveau INFO, et FRED impose la clé dans l'URL. On garde ses erreurs
    (WARNING), on coupe ses succès (INFO). Un journal qu'on ne lit pas est quand même un
    fichier que quelqu'un peut lire.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)


# =============================================================================
# [7] LE MANIFESTE DE COLLECTE : un fichier de faits par exécution (chapitre « Données » §1.3,
#     issue #64 ; sert C1 « toutes les données visées sont récupérées » et C20 « surveiller »)
# =============================================================================
#
# Le journal raconte ; le manifeste compte. Par étape : lues, écrites, rejetées, erreur, détails ;
# pour l'exécution : mode, période, durée, commit, version de Python. Rien d'autre : jamais un
# texte d'article, jamais une clé. Il part dans `logs/` (ignoré par Git) à côté du journal du soir.

VERSION_MANIFESTE = 1
_CLE_DANS_URL = re.compile(r"(api_key=)[^&\s\"']+", re.IGNORECASE)


def _sans_cle(texte: str | None) -> str | None:
    """Une erreur recopiée peut contenir une URL, et FRED met la clé dans l'URL (mesuré le 02/10 :
    6 journaux sur 40). On masque la valeur, on garde le reste du message."""
    return None if texte is None else _CLE_DANS_URL.sub(r"\1***", texte)


def _commit_courant() -> str | None:
    """Le commit du code qui a tourné, ou None si Git n'est pas là (conteneur, poste sans Git)."""
    try:
        sortie = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                                text=True, timeout=5, cwd=Path(__file__).resolve().parent.parent)
        return sortie.stdout.strip() or None
    except Exception:  # noqa: BLE001, l'absence de Git n'est pas une erreur de collecte
        return None


def ecrire_manifeste(resultat: dict, dossier: Path | str, maintenant: datetime | None = None,
                     periode: tuple[str, str] | None = None,
                     etapes_demandees: list[str] | None = None) -> str:
    """Écrit `manifeste-AAAA-MM-JJ-HHMMSS.json` dans `dossier` et rend son chemin.

    Le nom porte l'heure : un rattrapage l'après-midi n'écrase pas la collecte du soir.
    `maintenant` est le début de l'exécution ; la fin s'en déduit par `duree_s`.
    """
    debut = maintenant or datetime.now()
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    etapes = []
    for b in resultat["bilans"]:
        d = asdict(b)
        d["ok"] = b.ok
        d["nom"] = d.pop("etape")
        d["erreur"] = _sans_cle(d["erreur"])
        d["details"] = [_sans_cle(x) for x in d["details"]]
        etapes.append(d)
    contenu = {
        "version_manifeste": VERSION_MANIFESTE,
        "debut": debut.isoformat(timespec="seconds"),
        "duree_s": resultat.get("duree_s"),
        "mode": "simulation" if resultat.get("simulation") else "execution",
        "periode": list(periode) if periode else None,
        "etapes_demandees": etapes_demandees or list(ETAPES),
        "code": {"commit": _commit_courant(), "python": sys.version.split()[0]},
        "etapes": etapes,
        "etapes_ok": resultat.get("etapes_ok"),
        "etapes_total": len(etapes),
    }
    chemin = dossier / f"manifeste-{debut:%Y-%m-%d-%H%M%S}.json"
    chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=1), encoding="utf-8")
    return str(chemin)


def ecrire_manifeste_sans_casser(resultat: dict, dossier: Path | str, **kw) -> str | None:
    """La collecte a réussi ; le manifeste est un bonus. Une panne d'écriture (disque plein,
    dossier illisible) vaut une ligne WARNING, jamais une exception après 25 minutes de collecte."""
    try:
        return ecrire_manifeste(resultat, dossier, **kw)
    except Exception as erreur:  # noqa: BLE001
        logger.warning("manifeste non ecrit dans %s : %s", dossier, f"{type(erreur).__name__}: {erreur}"[:160])
        return None


def lire_dernier_manifeste(dossier: Path | str) -> dict | None:
    """Le manifeste le plus récent du dossier, ou None s'il n'y en a aucun. Pour l'API et la
    surveillance : « dernière collecte : 90 articles lus, 51 nouveaux, 39 rejetés »."""
    fichiers = sorted(Path(dossier).glob("manifeste-*.json"))
    if not fichiers:
        return None
    return json.loads(fichiers[-1].read_text(encoding="utf-8"))


if __name__ == "__main__":                                # [1] point de lancement
    configurer_journal()

    # Le fichier .env n'est lu QU'ICI, au lancement en ligne de commande — jamais à
    # l'import. Un module qui lit des fichiers quand on l'importe est imprévisible en
    # test. C'est aussi ce qui permet à la tâche planifiée de trouver DATABASE_URL :
    # le Planificateur Windows ne connaît pas les variables d'un terminal.
    try:
        from pathlib import Path

        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    except ImportError:                                   # python-dotenv absent
        logger.warning("python-dotenv absent : .env ignoré")

    parseur = argparse.ArgumentParser(description="Pipeline d'agregation RITA (C3)")
    parseur.add_argument("--dsn", default=None)
    parseur.add_argument("--etapes", default=None,
                         help="liste separee par des virgules : " + ",".join(ETAPES))
    parseur.add_argument("--simulation", action="store_true", help="n'ecrit rien en base")
    parseur.add_argument("--du", default=None, help="rattrapage : premier jour, AAAA-MM-JJ")
    parseur.add_argument("--au", default=None, help="rattrapage : dernier jour, AAAA-MM-JJ")
    parseur.add_argument("--strict", action="store_true",
                         help="code de sortie 1 si une etape echoue (conteneur one-shot)")
    args = parseur.parse_args()
    if bool(args.du) != bool(args.au):
        parseur.error("--du et --au vont ensemble")

    debut_execution = datetime.now()
    r = executer(args.dsn,
                 args.etapes.split(",") if args.etapes else None,
                 args.simulation,
                 periode=(args.du, args.au) if args.du else None)
    chemin_manifeste = ecrire_manifeste_sans_casser(
        r, Path(__file__).resolve().parent.parent / "logs", maintenant=debut_execution,
        periode=(args.du, args.au) if args.du else None,
        etapes_demandees=args.etapes.split(",") if args.etapes else None)

    mode = "SIMULATION (rien n'est ecrit)" if r["simulation"] else "EXECUTION"
    if args.du:
        mode += f"  --  RATTRAPAGE du {args.du} au {args.au}"
    print("\n" + "=" * 68)
    print(f"PIPELINE D'AGREGATION  --  {mode}")
    print("=" * 68)
    for b in r["bilans"]:
        if not b.ok:
            print(f"\n  !! {b.etape:<28} ECHEC : {b.erreur}")
            continue
        print(f"\n  {b.etape:<28} lues {b.lues:>4} | ecrites {b.ecrites:>4} "
              f"| rejetees {b.rejetees:>3}")
        for d in b.details:
            print(f"      - {d}")
    print(f"\n  Etapes reussies : {r['etapes_ok']}/{len(r['bilans'])}"
          f"   Duree : {r['duree_s']} s")
    print(f"  Manifeste : {chemin_manifeste or 'non ecrit (voir WARNING)'}\n")
    sys.exit(code_de_sortie(r, args.strict))

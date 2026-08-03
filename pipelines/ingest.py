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
import logging
import os
import time
from dataclasses import dataclass, field

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

def etape_taux_change(cur, simulation: bool) -> Bilan:
    """BCE -> table `taux_change`. Homogénéisation : 1 EUR = N unités de devise."""
    from sources.ecb import fetch_taux_change

    b = Bilan("taux_change (BCE)")
    lignes = []
    for devise in DEVISES_SUIVIES:
        try:
            t = fetch_taux_change(devise)
            lignes.append((t["devise"], t["date"], t["valeur"]))
            b.lues += 1
        except Exception as erreur:                       # noqa: BLE001
            b.rejetees += 1
            b.details.append(f"{devise} : {type(erreur).__name__}")

    # L'euro vaut 1 euro. Évident — mais sans cette ligne, la jointure de valorisation
    # ne trouve aucun taux pour les positions en EUR et retombe sur le COALESCE.
    if lignes:
        lignes.append(("EUR", lignes[0][1], 1.0))

    if lignes and not simulation:
        execute_values(cur, """
            INSERT INTO taux_change (devise, date_taux, valeur_pour_eur) VALUES %s
            ON CONFLICT (devise, date_taux) DO UPDATE
              SET valeur_pour_eur = EXCLUDED.valeur_pour_eur
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
        SELECT v.ticker, MAX(c.date_seance)
        FROM   valeur v
        LEFT   JOIN cotation c ON c.ticker = v.ticker
        GROUP  BY v.ticker
    """)
    par_date: dict = defaultdict(list)
    for ticker, derniere in cur.fetchall():
        par_date[derniere].append(ticker)

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


def etape_articles(cur, simulation: bool) -> Bilan:
    """RSS -> table `article`.

    Les articles porteurs d'injection sont **conservés et marqués**, pas supprimés :
    la colonne `bloque_injection` permet de les auditer, l'index partiel les exclut
    des lectures destinées au LLM.
    """
    from sources.rss import collecter

    b = Bilan("articles (RSS)")
    r = collecter()
    retenus, bloques = r["articles"], r["articles_bloques"]
    b.lues = r["total"]
    total_flux = len(r["flux_ok"]) + len(r["flux_echec"])
    b.details.append(f"flux OK {len(r['flux_ok'])}/{total_flux}")

    lignes = [(a.source, a.titre, a.lien, a.publie_le or None, a.resume,
               a.bloque, a.motifs_injection or None)
              for a in retenus + bloques if a.lien]

    # Dédoublonnage AVANT insertion : deux flux reprennent souvent la même dépêche.
    vus, uniques = set(), []
    for l in lignes:
        if l[2] not in vus:
            vus.add(l[2])
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

        lignes.append((trouve[0], c.collecte_le[:10], c.ouverture, c.haut,
                       c.bas, c.dernier, c.volume or 0))

    if lignes and not simulation:
        execute_values(cur, """
            INSERT INTO cotation (ticker, date_seance, ouverture, haut, bas, cloture, volume)
            VALUES %s ON CONFLICT (ticker, date_seance) DO NOTHING
        """, lignes)
        b.ecrites = len(lignes)
    return b


ETAPES = {
    "ecb": etape_taux_change,
    "cotations": etape_cotations,
    "rss": etape_articles,
    "scraping": etape_cours_scrapes,
}


# =============================================================================
# [1] POINT DE LANCEMENT · [2] CONNEXIONS · [4] ERREURS · [5] FIN · [6] SAUVEGARDE
# =============================================================================

def executer(dsn: str | None = None, etapes: list[str] | None = None,
             simulation: bool = False) -> dict:
    """Lance le pipeline d'agrégation.

    Une étape qui échoue **n'interrompt pas** les autres : une panne de la BCE ne doit pas
    priver le briefing des actualités. Chaque étape a sa transaction — un échec en fin de
    parcours n'annule pas ce qui a réussi avant.
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
                with conn.cursor() as cur:
                    bilans.append(ETAPES[nom](cur, simulation))
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


if __name__ == "__main__":                                # [1] point de lancement
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

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
    args = parseur.parse_args()

    r = executer(args.dsn,
                 args.etapes.split(",") if args.etapes else None,
                 args.simulation)

    mode = "SIMULATION (rien n'est ecrit)" if r["simulation"] else "EXECUTION"
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
          f"   Duree : {r['duree_s']} s\n")

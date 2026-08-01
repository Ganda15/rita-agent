"""Extraction programmatique depuis un système big data (C1 — étape 3/4).

C1, activités : « Connexion programmatique (Python, R, etc.) à un système de gestion de
base de données **et à un système big data** (Hive, Apache Impala, etc.) » et « Exécution
programmatique des requêtes d'extraction depuis un système big data ».

Le moteur retenu est **Apache Spark**, nommé par le référentiel dans les activités de C2
(« un système big data (Hive, **Spark**, etc.) »). Utiliser la technologie citée évite
d'avoir à défendre un équivalent.

## Ce que ce script démontre, et ce qu'il ne démontre pas

| ✅ Démontré | ❌ Non démontré |
|---|---|
| Connexion programmatique à Spark | Un cluster distribué réel |
| Lecture native d'un jeu Parquet partitionné | La tolérance aux pannes d'un cluster |
| *Partition pruning* visible dans le plan physique | Que le volume justifie Spark |
| Extraction filtrée sans lire tout le jeu | |

**276 168 lignes ne sont pas du big data** — 13,3 Mo tiennent en mémoire. Ce qui est
démontré, c'est la **méthode** : elle serait identique sur des téraoctets.

Usage :
    python -m bigdata.extract_spark
    python -m bigdata.extract_spark --annee 2024
"""
from __future__ import annotations

import argparse
import re
import time

from bigdata.session_spark import charger_cotations, creer_session


def extraire(annee: int | None = None, limite: int = 10) -> dict:
    """Extrait des cotations depuis le jeu Parquet via Spark.

    Args:
        annee: si fourni, déclenche le *partition pruning* — Spark ne lit que ce répertoire.
    """
    spark = creer_session("RITA-extraction")
    try:
        t0 = time.perf_counter()
        df = charger_cotations(spark)
        colonnes = df.columns
        partitions_lues = df.rdd.getNumPartitions()

        if annee is not None:
            df = df.filter(df.annee == annee)

        # `count()` force l'exécution : Spark est paresseux, sans action rien ne s'exécute.
        lignes = df.count()
        duree = time.perf_counter() - t0

        plan = df._jdf.queryExecution().simpleString()
        echantillon = [r.asDict() for r in
                       df.select("ticker", "date", "cloture", "volume", "annee")
                         .orderBy("date", ascending=False).limit(limite).collect()]

        tickers = df.select("ticker").distinct().count()
        return {"lignes": lignes, "tickers": tickers, "colonnes": colonnes,
                "partitions_rdd": partitions_lues, "duree_s": round(duree, 2),
                "annee": annee, "plan": plan, "echantillon": echantillon}
    finally:
        spark.stop()


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(description="Extraction Spark depuis le jeu Parquet")
    parseur.add_argument("--annee", type=int, default=None,
                         help="filtrer sur une annee (declenche le partition pruning)")
    parseur.add_argument("--limite", type=int, default=10)
    args = parseur.parse_args()

    r = extraire(args.annee, args.limite)

    print("\n" + "=" * 70)
    print("EXTRACTION SPARK — systeme big data (C1)")
    print("=" * 70)
    print(f"  Filtre           : {'annee = ' + str(r['annee']) if r['annee'] else 'aucun'}")
    print(f"  Lignes extraites : {r['lignes']:,}")
    print(f"  Valeurs          : {r['tickers']}")
    print(f"  Partitions RDD   : {r['partitions_rdd']}")
    print(f"  Duree            : {r['duree_s']} s")
    print(f"  Colonnes         : {', '.join(r['colonnes'])}")

    print(f"\n  Echantillon ({len(r['echantillon'])} lignes les plus recentes) :")
    print(f"    {'ticker':<10}{'date':<12}{'cloture':>10}{'volume':>14}{'annee':>7}")
    for l in r["echantillon"]:
        print(f"    {l['ticker']:<10}{str(l['date'])[:10]:<12}"
              f"{l['cloture']:>10.2f}{l['volume']:>14,}{l['annee']:>7}")

    if r["annee"]:
        print("\n  Plan d'execution — la preuve du partition pruning :")
        trouve = re.search(r"PartitionFilters:\s*(\[[^\]]*\])", r["plan"])
        print("    PartitionFilters:", trouve.group(1) if trouve else "ABSENT")
        chemins = re.search(r"InMemoryFileIndex\((\d+) paths\)", r["plan"])
        if chemins:
            print(f"    Fichiers connus de Spark : {chemins.group(1)}"
                  f"  ->  seule la partition annee={r['annee']} est lue")
    print()

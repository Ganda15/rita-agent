"""Requêtes Spark SQL sur le système big data (C2 — étape 4/4).

C2 : « Développer des requêtes de type SQL d'extraction des données depuis un système de
gestion de base de données **et un système big data** en appliquant le langage de requête
propre au système. »

Les requêtes de `db/requetes.sql` couvrent la première moitié (PostgreSQL). Celles-ci
couvrent la seconde : **Spark SQL**, le langage propre au système big data.

## Ce qui change par rapport à PostgreSQL

| PostgreSQL | Spark SQL |
|---|---|
| Index B-tree sur `(ticker, date_seance)` | **Partition pruning** sur `annee` |
| `EXPLAIN ANALYZE` | `explain()` — plan physique |
| Optimisation = choisir le bon index | Optimisation = **ne pas lire les partitions inutiles** |
| Une machine, un processus | `local[*]` : un exécuteur par cœur |

L'optimisation ne se pense pas de la même façon : en base relationnelle on cherche le bon
chemin d'accès, en big data on cherche **à ne pas lire**.

Usage :
    python -m bigdata.query_spark
    python -m bigdata.query_spark --requete volumetrie
"""
from __future__ import annotations

import argparse
import re
import time

from bigdata.session_spark import charger_cotations, creer_session

# =============================================================================
# S1 — Volumétrie par année
# =============================================================================
# OBJECTIF   Vérifier l'équilibre des partitions et la couverture temporelle.
# CHOIX      GROUP BY sur `annee`, qui est la COLONNE DE PARTITIONNEMENT. Spark lit le nom
#            du répertoire, pas le contenu des fichiers, pour connaître les valeurs.
# OPTIMISATION  Aucune lecture de colonne n'est nécessaire pour compter les lignes d'une
#            partition — le format colonnaire évite de charger les prix.
S1_VOLUMETRIE = """
    SELECT annee,
           COUNT(*)                        AS lignes,
           COUNT(DISTINCT ticker)          AS valeurs,
           ROUND(AVG(cloture), 2)          AS cloture_moyenne
    FROM   cotation
    GROUP  BY annee
    ORDER  BY annee
"""

# =============================================================================
# S2 — Amplitude moyenne : quelles valeurs bougent le plus ?
# =============================================================================
# OBJECTIF   Classer les valeurs par volatilité intraséance — un fait observable qui
#            alimente l'agent Technique. Pas une recommandation (garde-fou AMF).
# CHOIX DE FILTRAGE  `annee >= 2024` déclenche le PARTITION PRUNING : Spark n'ouvre que
#            3 répertoires sur 11. C'est l'optimisation majeure du monde big data.
# CHOIX DE CONDITION  `bas > 0` évite une division par zéro — l'analyse exploratoire avait
#            mesuré des cours à 0,01 et des volumes nuls.
# CHOIX      HAVING sur le nombre de séances : une valeur avec 12 séances n'est pas
#            comparable à une valeur avec 500.
S2_AMPLITUDE = """
    SELECT ticker,
           COUNT(*)                                         AS seances,
           ROUND(AVG((haut - bas) / bas * 100), 2)          AS amplitude_moy_pct,
           ROUND(MAX((haut - bas) / bas * 100), 2)          AS amplitude_max_pct,
           ROUND(AVG(volume))                               AS volume_moyen
    FROM   cotation
    WHERE  annee >= 2024 AND bas > 0
    GROUP  BY ticker
    HAVING COUNT(*) >= 200
    ORDER  BY amplitude_moy_pct DESC
    LIMIT  10
"""

# =============================================================================
# S3 — Meilleure et pire séance de chaque valeur (fonction de fenêtrage)
# =============================================================================
# OBJECTIF   Situer une séance dans l'historique de sa propre valeur.
# CHOIX      LAG() puis RANK() OVER (PARTITION BY ticker) : le même vocabulaire que
#            PostgreSQL, exécuté par un moteur distribué. C'est ce qui rend Spark SQL
#            enseignable — on ne réapprend pas un langage.
# ⚠️ COÛT    PARTITION BY ticker provoque un SHUFFLE : Spark redistribue les données entre
#            exécuteurs pour regrouper chaque ticker. C'est l'opération la plus coûteuse du
#            monde distribué. D'où `spark.sql.shuffle.partitions = 8` au lieu de 200.
S3_EXTREMES = """
    WITH variations AS (
        SELECT ticker, date, cloture, annee,
               LAG(cloture) OVER (PARTITION BY ticker ORDER BY date) AS veille
        FROM   cotation
        WHERE  annee >= 2025
    ),
    calcul AS (
        SELECT ticker, date, cloture, veille,
               (cloture - veille) / veille * 100 AS variation_pct
        FROM   variations
        WHERE  veille IS NOT NULL AND veille > 0
    ),
    classe AS (
        SELECT c.*,
               RANK() OVER (PARTITION BY ticker ORDER BY variation_pct DESC) AS rang_hausse
        FROM   calcul c
    )
    SELECT ticker, DATE(date) AS seance,
           ROUND(veille, 2)        AS cloture_veille,
           ROUND(cloture, 2)       AS cloture,
           ROUND(variation_pct, 2) AS variation_pct
    FROM   classe
    WHERE  rang_hausse = 1
    ORDER  BY variation_pct DESC
    LIMIT  10
"""

REQUETES = {
    "volumetrie": ("S1 · Volumetrie par annee", S1_VOLUMETRIE),
    "amplitude": ("S2 · Amplitude moyenne (pruning : annee >= 2024)", S2_AMPLITUDE),
    "extremes": ("S3 · Meilleure seance de chaque valeur (fenetrage + shuffle)", S3_EXTREMES),
}


def executer(nom: str | None = None) -> dict:
    """Exécute une ou toutes les requêtes Spark SQL, avec mesure et plan."""
    choisies = [nom] if nom else list(REQUETES)
    inconnues = [n for n in choisies if n not in REQUETES]
    if inconnues:
        raise ValueError(f"Requete(s) inconnue(s) : {inconnues}. Connues : {list(REQUETES)}")

    spark = creer_session("RITA-sparksql")
    resultats = []
    try:
        charger_cotations(spark).createOrReplaceTempView("cotation")

        for cle in choisies:
            titre, sql = REQUETES[cle]
            t0 = time.perf_counter()
            df = spark.sql(sql)
            lignes = [r.asDict() for r in df.collect()]     # `collect` force l'exécution
            duree = time.perf_counter() - t0
            plan = df._jdf.queryExecution().simpleString()

            pruning = re.search(r"PartitionFilters:\s*(\[[^\]]*\])", plan)
            resultats.append({
                "cle": cle, "titre": titre, "lignes": lignes,
                "duree_s": round(duree, 2),
                "pruning": pruning.group(1) if pruning else None,
                "shuffle": "Exchange" in plan,
            })
    finally:
        spark.stop()
    return {"resultats": resultats}


def _afficher(lignes: list[dict]) -> None:
    if not lignes:
        print("    (aucune ligne)")
        return
    colonnes = list(lignes[0])
    largeurs = {c: max(len(c), max(len(f"{l[c]}") for l in lignes)) + 2 for c in colonnes}
    print("    " + "".join(c.ljust(largeurs[c]) for c in colonnes))
    print("    " + "-" * sum(largeurs.values()))
    for l in lignes:
        print("    " + "".join(f"{l[c]}".ljust(largeurs[c]) for c in colonnes))


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(description="Requetes Spark SQL (C2 - big data)")
    parseur.add_argument("--requete", choices=list(REQUETES), default=None)
    args = parseur.parse_args()

    r = executer(args.requete)

    print("\n" + "=" * 74)
    print("SPARK SQL — requetes sur le systeme big data (C2)")
    print("=" * 74)
    for res in r["resultats"]:
        print(f"\n  {res['titre']}   [{res['duree_s']} s]")
        if res["pruning"]:
            print(f"    -> PARTITION PRUNING : {res['pruning']}")
        if res["shuffle"]:
            print("    -> SHUFFLE declenche (redistribution entre executeurs)")
        print()
        _afficher(res["lignes"])
    print()

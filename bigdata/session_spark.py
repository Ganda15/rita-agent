"""Session Spark partagée — et le contournement Windows qui la rend possible.

## Le problème Windows, et pourquoi ce fichier existe

Spark s'appuie sur les bibliothèques Hadoop. Sous Windows, lister le contenu d'un
répertoire passe par du code natif (`NativeIO$Windows.access0`) fourni par deux binaires
absents d'une installation standard : `winutils.exe` et `hadoop.dll`.

    spark.read.parquet("data/bigdata/ohlcv")
    -> java.lang.UnsatisfiedLinkError: 'boolean org.apache.hadoop.io.nativeio.
       NativeIO$Windows.access0(java.lang.String, int)'

**La solution habituelle est de télécharger ces binaires depuis un dépôt communautaire.**
Écartée ici : ce sont des exécutables non signés, chargés dans la JVM, provenant d'un tiers
non officiel. Sur un projet qui documente par ailleurs le RGPD et les garde-fous, installer
une DLL de provenance incertaine serait incohérent.

## Le contournement retenu

Le code natif n'est appelé que pour **lister un répertoire**. En passant la **liste
explicite des fichiers**, on n'y touche jamais.

    fichiers = glob("data/bigdata/ohlcv/*/*.parquet")     # listage par Python
    spark.read.option("basePath", base).parquet(*fichiers) # lecture native par Spark

`basePath` est indispensable : sans lui, Spark ne sait pas que `annee=2024` est une
partition et la colonne `annee` disparaît — donc le *partition pruning* aussi.

Vérifié : `PartitionFilters: [isnotnull(annee), (annee = 2024)]` apparaît bien dans le
plan physique. Le pruning fonctionne.

## Prérequis

    JAVA_HOME  ->  un JDK 21 (Eclipse Temurin, verifie par SHA256)
    pyspark    ->  4.2.0
"""
from __future__ import annotations

import glob
import os
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PARQUET = RACINE / "data" / "bigdata" / "ohlcv"

# Chemin par défaut du JDK installé le 02/08/2026 (Temurin 21.0.12, SHA256 vérifié).
JAVA_HOME_DEFAUT = Path.home() / "Tools" / "jdk-21.0.12+8"


def preparer_environnement() -> None:
    """Renseigne JAVA_HOME et PYSPARK_PYTHON s'ils manquent.

    Sans PYSPARK_PYTHON, Spark lance `python` — qui peut être un autre interpréteur que
    celui qui exécute le script. Sur cette machine, `python` n'est même pas dans le PATH.
    """
    if not os.environ.get("JAVA_HOME") and JAVA_HOME_DEFAUT.exists():
        os.environ["JAVA_HOME"] = str(JAVA_HOME_DEFAUT)
    os.environ.setdefault("PYSPARK_PYTHON", r"C:\Python314\python.exe")
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", r"C:\Python314\python.exe")


def fichiers_parquet() -> list[str]:
    """URI `file:///` de chaque fichier Parquet — listage fait par Python, pas par Hadoop."""
    motif = str(PARQUET / "*" / "*.parquet")
    return [f"file:///{os.path.abspath(p)}".replace("\\", "/")
            for p in sorted(glob.glob(motif))]


def creer_session(nom: str = "RITA-bigdata"):
    """Ouvre une session Spark locale.

    `local[*]` : un exécuteur par cœur, sur cette machine. C'est un cluster d'une seule
    machine — assumé et dit tel quel. La logique est celle d'un cluster réel ; seule
    l'échelle diffère.
    """
    preparer_environnement()
    from pyspark.sql import SparkSession

    spark = (SparkSession.builder
             .appName(nom)
             .master("local[*]")
             .config("spark.ui.enabled", "false")          # pas d'interface web ici
             .config("spark.sql.shuffle.partitions", "8")  # défaut 200 : absurde en local
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def charger_cotations(spark):
    """Lit le jeu Parquet partitionné, colonne de partition `annee` incluse."""
    fichiers = fichiers_parquet()
    if not fichiers:
        raise FileNotFoundError(
            f"Aucun fichier Parquet sous {PARQUET}\n"
            "Le construire avec : python -m bigdata.build_parquet"
        )
    base = f"file:///{os.path.abspath(PARQUET)}".replace("\\", "/")
    return spark.read.option("basePath", base).parquet(*fichiers)

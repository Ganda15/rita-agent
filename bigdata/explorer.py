"""Analyse exploratoire du jeu Parquet partitionné (preuve C1 attendue par le jury).

Le règlement spécifique RNCP37827 (p. 53, « Exemples d'éléments de preuves attendus »)
demande pour le Bloc 1, en plus du script d'extraction :

    « les résultats de l'analyse exploratoire permettant la bonne compréhension
      du jeu de données récupéré »

Cette exigence n'apparaît dans AUCUN des 135 critères d'évaluation — c'est une page
distincte du règlement. D'où ce script.

L'objectif n'est pas de faire de la data science : c'est de **prouver qu'on a regardé la
donnée avant de la stocker**. On répond à six questions qu'un ingénieur data se pose
toujours avant de modéliser une base :

    1. Combien de lignes, combien de valeurs, sur quelle période ?
    2. Comment le volume se répartit-il par partition ?
    3. Y a-t-il des trous (valeurs manquantes) ?
    4. Y a-t-il des doublons sur ce qui devrait être une clé unique ?
    5. Toutes les valeurs ont-elles le même historique ?
    6. Y a-t-il des valeurs aberrantes (prix négatif, volume nul) ?

Chaque réponse a une conséquence directe sur le schéma de la base (C4) : la clé primaire,
les colonnes NOT NULL, les index. C'est le lien entre l'exploration et la conception.

Usage :
    python -m bigdata.explorer
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "data" / "bigdata" / "ohlcv"

COLONNES_NUMERIQUES = ["ouverture", "haut", "bas", "cloture", "volume"]


def charger() -> pd.DataFrame:
    """Lit le Parquet partitionné en entier."""
    if not SOURCE.exists():
        raise FileNotFoundError(
            f"Jeu absent : {SOURCE}\n"
            "Le regenerer avec : python -m bigdata.build_parquet"
        )
    return pd.read_parquet(SOURCE)


def vue_generale(df: pd.DataFrame) -> dict:
    """Question 1 — volumétrie et couverture temporelle."""
    return {
        "lignes": len(df),
        "tickers_distincts": df["ticker"].nunique(),
        "noms_distincts": df["nom"].nunique(),
        "date_min": df["date"].min(),
        "date_max": df["date"].max(),
        "colonnes": list(df.columns),
    }


def par_partition(df: pd.DataFrame) -> pd.DataFrame:
    """Question 2 — répartition par année (= par partition physique)."""
    g = df.groupby("annee").agg(
        lignes=("ticker", "size"),
        tickers=("ticker", "nunique"),
    )
    g["part_%"] = (g["lignes"] / len(df) * 100).round(1)
    return g


def valeurs_manquantes(df: pd.DataFrame) -> pd.DataFrame:
    """Question 3 — trous par colonne."""
    n = df.isna().sum()
    return pd.DataFrame({"manquantes": n, "taux_%": (n / len(df) * 100).round(3)})


def doublons(df: pd.DataFrame) -> dict:
    """Question 4 — doublons sur (ticker, date), la clé métier naturelle.

    C'est ce test qui a révélé le cas CGG : deux lignes de l'univers (« CGG BS » et
    « CGG RGPT ») pointent vers le même ticker VIRI.PA. Le téléchargement les traite
    comme deux valeurs, mais ce sont deux instruments de la MÊME société.
    """
    masque = df.duplicated(subset=["ticker", "date"], keep=False)
    doubles = df[masque]
    detail = {}
    if not doubles.empty:
        for tk, grp in doubles.groupby("ticker"):
            detail[tk] = {
                "lignes_en_double": len(grp),
                "noms_concernes": sorted(grp["nom"].unique().tolist()),
            }
    return {
        "lignes_en_double": int(masque.sum()),
        "cles_uniques": int(df[["ticker", "date"]].drop_duplicates().shape[0]),
        "detail": detail,
    }


def couverture_historique(df: pd.DataFrame) -> pd.DataFrame:
    """Question 5 — les valeurs n'ont pas toutes le même historique."""
    c = df.groupby("ticker").agg(
        lignes=("date", "size"),
        debut=("date", "min"),
        fin=("date", "max"),
    )
    return c.sort_values("lignes")


def anomalies(df: pd.DataFrame) -> dict:
    """Question 6 — valeurs aberrantes métier."""
    return {
        "cloture_nulle_ou_negative": int((df["cloture"] <= 0).sum()),
        "volume_zero": int((df["volume"] == 0).sum()),
        "haut_inferieur_au_bas": int((df["haut"] < df["bas"]).sum()),
        "cloture_hors_bornes": int(
            ((df["cloture"] > df["haut"]) | (df["cloture"] < df["bas"])).sum()
        ),
    }


def main() -> None:
    df = charger()

    print("=" * 72)
    print("ANALYSE EXPLORATOIRE — jeu Parquet partitionne (preuve C1)")
    print("=" * 72)

    g = vue_generale(df)
    print("\n[1] VUE GENERALE")
    print(f"  Lignes              : {g['lignes']:,}")
    print(f"  Tickers distincts   : {g['tickers_distincts']}")
    print(f"  Noms distincts      : {g['noms_distincts']}")
    print(f"  Periode             : {g['date_min']:%Y-%m-%d} -> {g['date_max']:%Y-%m-%d}")
    print(f"  Colonnes ({len(g['colonnes'])})       : {', '.join(g['colonnes'])}")

    print("\n[2] REPARTITION PAR PARTITION (annee)")
    print(par_partition(df).to_string())

    print("\n[3] VALEURS MANQUANTES")
    vm = valeurs_manquantes(df)
    print(vm.to_string())
    total_nan = int(vm["manquantes"].sum())
    print(f"  -> total : {total_nan} valeur(s) manquante(s)")

    print("\n[4] DOUBLONS SUR LA CLE (ticker, date)")
    d = doublons(df)
    print(f"  Lignes en double    : {d['lignes_en_double']:,}")
    print(f"  Cles uniques        : {d['cles_uniques']:,}")
    for tk, info in d["detail"].items():
        print(f"  !! {tk} : {info['lignes_en_double']} lignes, "
              f"noms = {info['noms_concernes']}")

    print("\n[5] COUVERTURE HISTORIQUE (5 plus courts / 3 plus longs)")
    c = couverture_historique(df)
    for tk, r in c.head(5).iterrows():
        print(f"  {tk:12s} {r['lignes']:>5} lignes  {r['debut']:%Y-%m-%d} -> {r['fin']:%Y-%m-%d}")
    print("  ...")
    for tk, r in c.tail(3).iterrows():
        print(f"  {tk:12s} {r['lignes']:>5} lignes  {r['debut']:%Y-%m-%d} -> {r['fin']:%Y-%m-%d}")

    print("\n[6] ANOMALIES METIER")
    for cle, val in anomalies(df).items():
        marque = "OK " if val == 0 else "!! "
        print(f"  {marque}{cle:30s} : {val}")

    print("\n[7] STATISTIQUES DESCRIPTIVES")
    print(df[COLONNES_NUMERIQUES].describe().round(2).to_string())

    print("\n" + "=" * 72)
    print("CONSEQUENCES POUR LE SCHEMA DE BASE (C4)")
    print("=" * 72)
    print("  - Cle primaire (ticker, date) : NON utilisable seule -> doublon VIRI.PA")
    print("  - Colonnes OHLCV              : NOT NULL (aucune valeur manquante mesuree)")
    print("  - Colonne 'annee'             : cle de partitionnement, a indexer")
    print("  - Table 'valeur' separee      : un ticker peut porter plusieurs noms")


if __name__ == "__main__":
    main()

"""Construit le jeu Parquet partitionné du laboratoire big data (C1).

Lit `data/univers-155.csv` (univers réel d'Era, tickers vérifiés le 29/07/2026), télécharge
10 ans d'historique quotidien pour chaque valeur exploitable, et écrit en Parquet
**partitionné par année** :

    data/bigdata/ohlcv/annee=2016/part-0.parquet
    data/bigdata/ohlcv/annee=2017/part-0.parquet
    ...

Pourquoi le partitionnement par année est le vrai geste « big data » :
un moteur distribué (Spark) qui reçoit `WHERE annee = 2024` ne lit QUE ce répertoire —
c'est le *predicate pushdown*. Le volume ici (~276 000 lignes) ne l'exige pas, mais la
méthode est rigoureusement celle qu'on appliquerait sur des téraoctets. C'est la méthode
qui prouve la compétence, pas la taille du fichier.

Usage :
    python -m bigdata.build_parquet
"""
from __future__ import annotations

import csv
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

RACINE = Path(__file__).resolve().parent.parent
UNIVERS = RACINE / "data" / "univers-155.csv"
DEST = RACINE / "data" / "bigdata" / "ohlcv"


def charger_univers() -> list[tuple[str, str]]:
    """Retourne [(nom, ticker)] des seules valeurs exploitables (statut OK*)."""
    with open(UNIVERS, encoding="utf-8") as f:
        return [
            (r["nom"], r["ticker"])
            for r in csv.DictReader(f)
            if r["statut"].startswith("OK")
        ]


def telecharger(ticker: str, nom: str) -> pd.DataFrame:
    """Télécharge 10 ans d'OHLCV pour un ticker. DataFrame vide si indisponible."""
    hist = yf.Ticker(ticker).history(period="10y", interval="1d")
    if hist.empty:
        return pd.DataFrame()

    df = hist.reset_index()[["Date", "Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["date", "ouverture", "haut", "bas", "cloture", "volume"]
    df["ticker"] = ticker
    df["nom"] = nom
    df["date"] = pd.to_datetime(df["date"], utc=True)  # homogénéisation UTC (C3)
    df["annee"] = df["date"].dt.year
    return df


def construire() -> dict:
    """Télécharge tout l'univers et écrit le Parquet partitionné par année."""
    univers = charger_univers()
    DEST.mkdir(parents=True, exist_ok=True)

    morceaux, echecs = [], []
    debut = time.perf_counter()

    for i, (nom, ticker) in enumerate(univers, 1):
        try:
            df = telecharger(ticker, nom)
            if df.empty:
                echecs.append((nom, ticker, "aucune donnee"))
            else:
                morceaux.append(df)
        except Exception as erreur:                       # noqa: BLE001
            echecs.append((nom, ticker, str(erreur)[:60]))
        if i % 20 == 0:
            print(f"  {i}/{len(univers)} traites...", flush=True)

    if not morceaux:
        raise RuntimeError("Aucune donnee telechargee — verifier la connexion reseau.")

    complet = pd.concat(morceaux, ignore_index=True)
    complet.to_parquet(DEST, partition_cols=["annee"], index=False)

    duree = time.perf_counter() - debut
    annees = sorted(complet["annee"].unique())
    taille_mo = sum(p.stat().st_size for p in DEST.rglob("*.parquet")) / 1_048_576

    return {
        "valeurs_demandees": len(univers),
        "valeurs_recuperees": len(morceaux),
        "echecs": echecs,
        "lignes": len(complet),
        "partitions": len(annees),
        "annees": f"{annees[0]}-{annees[-1]}",
        "taille_mo": round(taille_mo, 1),
        "duree_s": round(duree, 1),
    }


if __name__ == "__main__":
    r = construire()
    print("\n=== JEU PARQUET PARTITIONNE — LABORATOIRE BIG DATA ===")
    print(f"Valeurs recuperees : {r['valeurs_recuperees']} / {r['valeurs_demandees']}")
    print(f"Lignes             : {r['lignes']:,}")
    print(f"Partitions (annees): {r['partitions']}  ({r['annees']})")
    print(f"Taille sur disque  : {r['taille_mo']} Mo")
    print(f"Duree              : {r['duree_s']} s")
    print(f"Destination        : {DEST}")
    if r["echecs"]:
        print(f"\nEchecs ({len(r['echecs'])}) :")
        for nom, tk, cause in r["echecs"]:
            print(f"  {tk:12s} {nom:28s} {cause}")

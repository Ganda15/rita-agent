"""Import des données préparées vers PostgreSQL (C4 — script d'import).

Critère C4 : « Le script d'import fourni est fonctionnel : il permet l'insertion des
données dans le système mis en place. »

Le script applique **au moment de l'import** les règles de nettoyage établies par
l'analyse exploratoire (`bigdata/explorer.py`, 31/07/2026) :

  - dédoublonnage sur (ticker, date_seance) — 2 560 lignes redondantes mesurées
  - marquage des valeurs incohérentes plutôt que suppression (STLAP.PA, ALJXR.PA)
  - résolution des alias de portefeuille vers un ticker unique (cas CGG -> VIRI.PA)

Connexion : variable `DATABASE_URL`, ou `--dsn` en ligne de commande.

    postgresql://rita:rita_dev_local@localhost:5432/rita     (docker compose)

Usage :
    python -m db.importer                      # tout
    python -m db.importer --dsn "postgresql://..." --limite-annees 3
"""
from __future__ import annotations

import argparse
import csv
import logging
import os
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values

# Sans cette ligne, le script ne lit PAS le .env et retombe sur DSN_DEFAUT, qui
# pointe le port 5432 du docker-compose — alors que le PostgreSQL réel écoute sur
# 5433. Constaté le 16/08/2026 : l'import échouait avec « Connection refused » sur
# un port que personne n'écoutait. Seul api/main.py chargeait le .env.
load_dotenv()

logger = logging.getLogger(__name__)

RACINE = Path(__file__).resolve().parent.parent
PARQUET = RACINE / "data" / "bigdata" / "ohlcv"
UNIVERS = RACINE / "data" / "univers-155.csv"

DSN_DEFAUT = "postgresql://rita:rita_dev_local@localhost:5432/rita"

# Valeurs écartées du calcul mais CONSERVÉES en base, avec leur cause.
# Constats mesurés, pas suppositions — voir evidence/C1/preuve-09-analyse-exploratoire.md
QUALITE = {
    "STLAP.PA": ("INCOHERENT",
                 "1142 clotures hors bornes + 1143 volumes nuls (explorer.py 31/07/2026)"),
    "ALJXR.PA": ("INCOHERENT",
                 "prix max 7 156 748 EUR - echelle aberrante (ligne de droits non ajustee)"),
}


def charger_univers() -> tuple[dict[str, dict], list[tuple[str, str]]]:
    """Lit l'univers et sépare les valeurs de leurs alias de portefeuille.

    Retourne (valeurs par ticker, liste d'alias). C'est ici que le cas CGG se résout :
    deux libellés (« CGG BS », « CGG RGPT ») produisent UNE valeur et DEUX alias.
    """
    valeurs: dict[str, dict] = {}
    alias: list[tuple[str, str]] = []

    with open(UNIVERS, encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            if not ligne["statut"].startswith("OK"):
                continue
            ticker, nom = ligne["ticker"], ligne["nom"]
            alias.append((nom, ticker))
            if ticker not in valeurs:
                statut, note = QUALITE.get(ticker, ("OK", None))
                valeurs[ticker] = {"ticker": ticker, "nom": nom,
                                   "statut": statut, "note": note}

    return valeurs, alias


def importer_valeurs(cur, valeurs: dict[str, dict], alias: list[tuple[str, str]]) -> None:
    execute_values(cur, """
        INSERT INTO valeur (ticker, nom_officiel, statut_qualite, note_qualite)
        VALUES %s
        ON CONFLICT (ticker) DO UPDATE
          SET nom_officiel   = EXCLUDED.nom_officiel,
              statut_qualite = EXCLUDED.statut_qualite,
              note_qualite   = EXCLUDED.note_qualite
    """, [(v["ticker"], v["nom"], v["statut"], v["note"]) for v in valeurs.values()])

    execute_values(cur, """
        INSERT INTO alias_valeur (alias, ticker) VALUES %s
        ON CONFLICT (alias) DO NOTHING
    """, alias)


def importer_cotations(cur, limite_annees: int | None = None) -> dict:
    """Charge le Parquet, dédoublonne, insère en lot."""
    if not PARQUET.exists():
        raise FileNotFoundError(
            f"Jeu Parquet absent : {PARQUET}\n"
            "Le construire avec : python -m bigdata.build_parquet"
        )

    df = pd.read_parquet(PARQUET)
    lues = len(df)

    if limite_annees:
        seuil = int(df["annee"].max()) - limite_annees + 1
        df = df[df["annee"] >= seuil]

    # --- Dédoublonnage C3 : la règle établie dans evidence/C3/ ---
    avant = len(df)
    df = df.drop_duplicates(subset=["ticker", "date"], keep="first")
    retirees = avant - len(df)

    # Les tickers absents de `valeur` ne peuvent pas entrer (clé étrangère).
    cur.execute("SELECT ticker FROM valeur")
    connus = {r[0] for r in cur.fetchall()}
    orphelins = set(df["ticker"].unique()) - connus
    if orphelins:
        logger.warning("%d ticker(s) hors univers ignore(s) : %s",
                       len(orphelins), sorted(orphelins)[:5])
        df = df[df["ticker"].isin(connus)]

    lignes = [
        (r.ticker, r.date.date(), float(r.ouverture), float(r.haut),
         float(r.bas), float(r.cloture), int(r.volume))
        for r in df.itertuples()
    ]

    execute_values(cur, """
        INSERT INTO cotation
              (ticker, date_seance, ouverture, haut, bas, cloture, volume)
        VALUES %s
        ON CONFLICT (ticker, date_seance) DO NOTHING
    """, lignes, page_size=5000)

    # Bornes de cotation : servent la détection du biais de survie (requête « perf 10 ans »)
    cur.execute("""
        UPDATE valeur v SET premiere_cotation = b.mini, derniere_cotation = b.maxi
        FROM (SELECT ticker, min(date_seance) mini, max(date_seance) maxi
              FROM cotation GROUP BY ticker) b
        WHERE b.ticker = v.ticker
    """)

    return {"lues": lues, "dedoublonnees": retirees, "inserees": len(lignes)}


def importer_positions(cur) -> int:
    """Importe le portefeuille en résolvant les alias vers le ticker canonique."""
    from sources.positions import lire

    portefeuille = lire()
    lignes, ignorees = [], []

    for p in portefeuille.positions:
        cur.execute("SELECT ticker FROM valeur WHERE ticker = %s", (p.ticker,))
        if cur.fetchone():
            cible = p.ticker
        else:
            cur.execute("SELECT ticker FROM alias_valeur WHERE alias = %s", (p.nom,))
            trouve = cur.fetchone()
            if not trouve:
                ignorees.append(p.ticker)
                continue
            cible = trouve[0]
        lignes.append((cible, p.quantite, p.pru, p.devise, p.date_achat or None))

    if ignorees:
        logger.warning("%d position(s) sans valeur correspondante : %s",
                       len(ignorees), ignorees)

    if lignes:
        execute_values(cur, """
            INSERT INTO position (ticker, quantite, pru, devise, date_achat)
            VALUES %s
        """, lignes)

    return len(lignes)


def importer(dsn: str, limite_annees: int | None = None) -> dict:
    valeurs, alias = charger_univers()

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            importer_valeurs(cur, valeurs, alias)
            stats = importer_cotations(cur, limite_annees)
            stats["valeurs"] = len(valeurs)
            stats["alias"] = len(alias)
            stats["positions"] = importer_positions(cur)
        conn.commit()

    return stats


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parseur = argparse.ArgumentParser(description="Import RITA -> PostgreSQL")
    parseur.add_argument("--dsn", default=os.getenv("DATABASE_URL", DSN_DEFAUT))
    parseur.add_argument("--limite-annees", type=int, default=None,
                         help="n'importer que les N dernieres annees")
    args = parseur.parse_args()

    r = importer(args.dsn, args.limite_annees)

    print("\n=== IMPORT POSTGRESQL ===")
    print(f"Valeurs            : {r['valeurs']}")
    print(f"Alias portefeuille : {r['alias']}   (> valeurs = cas CGG resolu)")
    print(f"Cotations lues     : {r['lues']:,}")
    print(f"  dedoublonnees    : {r['dedoublonnees']:,}")
    print(f"  inserees         : {r['inserees']:,}")
    print(f"Positions          : {r['positions']}")

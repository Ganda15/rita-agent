"""Sprint 2, tâche 4 : extraire les valeurs et les cours du jeu de démonstration depuis la base du poste.

Écrit `valeurs.csv` et `cotations.csv` (UTF-8, séparateur `;`) dans le dossier donné. Les articles et les positions
du jeu sont écrits à la main (contenu synthétique, marqué comme tel). La connexion se fait en session de lecture
seule : la base refuse toute écriture, quel que soit le compte.

Ligne de commande : `python scripts/extraire_jeu_demo.py [--dossier data/demo]`. Elle lit `RITA_DSN_LECTURE` (le compte
en lecture seule) et s'arrête s'il manque, sans repli vers `DATABASE_URL`.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from datetime import date
from pathlib import Path

import psycopg2

TICKERS = ["OR.PA", "MC.PA", "AIR.PA"]
DEBUT, FIN = date(2026, 7, 1), date(2026, 10, 14)


def _ecrire(chemin: Path, en_tete: list[str], lignes) -> int:
    with open(chemin, "w", encoding="utf-8", newline="") as fichier:
        ecrivain = csv.writer(fichier, delimiter=";", lineterminator="\n")
        ecrivain.writerow(en_tete)
        n = 0
        for ligne in lignes:
            ecrivain.writerow(["" if v is None else (v.isoformat() if isinstance(v, date) else v) for v in ligne])
            n += 1
    return n


def extraire(dsn: str, tickers: list[str], debut: date, fin: date, dossier: Path) -> dict[str, int]:
    """Écrit valeurs.csv et cotations.csv ; rend le nombre de lignes écrites dans chacun."""
    dossier.mkdir(parents=True, exist_ok=True)
    cnx = psycopg2.connect(dsn)
    cnx.set_session(readonly=True)
    try:
        with cnx.cursor() as cur:
            cur.execute("SELECT ticker, nom_officiel, isin, devise, place_cotation FROM valeur "
                        "WHERE ticker = ANY(%s) ORDER BY ticker", (tickers,))
            valeurs = cur.fetchall()
            cur.execute("SELECT ticker, date_seance, ouverture, haut, bas, cloture, volume FROM cotation "
                        "WHERE ticker = ANY(%s) AND date_seance BETWEEN %s AND %s ORDER BY ticker, date_seance",
                        (tickers, debut, fin))
            cotations = cur.fetchall()
    finally:
        cnx.close()
    return {
        "valeurs": _ecrire(dossier / "valeurs.csv", ["ticker", "nom_officiel", "isin", "devise", "place_cotation"],
                           valeurs),
        "cotations": _ecrire(dossier / "cotations.csv",
                             ["ticker", "date_seance", "ouverture", "haut", "bas", "cloture", "volume"], cotations),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dossier", default="data/demo")
    args = parser.parse_args(argv)
    dsn = os.environ.get("RITA_DSN_LECTURE")
    if not dsn:
        print("RITA_DSN_LECTURE absente : l'extraction se fait avec le compte en lecture seule, sans repli.",
              file=sys.stderr)
        return 2
    print(extraire(dsn, TICKERS, DEBUT, FIN, Path(args.dossier)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Extraction de données depuis PostgreSQL (C1 — base de données · C2 — requêtes SQL).

**Cinquième et dernier type de source exigé par C1** : *« une base de données »*.

C1 demande la « connexion programmatique (Python, R, etc.) à un système de gestion de base
de données » et l'« exécution programmatique des requêtes d'extraction de type SQL ». Ce
module fait exactement cela : il ouvre une connexion, exécute les requêtes de
`db/requetes.sql` et rend des objets Python exploitables par les agents.

## Pourquoi un module séparé plutôt que du SQL dans les agents

Trois raisons, dans l'ordre d'importance :

1. **Les requêtes sont un livrable** (C2). Elles vivent dans `db/requetes.sql`, documentées,
   relisibles par un jury. Les disperser dans le code des agents les rendrait invisibles.
2. **Une requête se teste seule.** On vérifie la forme du résultat sans lancer un agent.
3. **Le SQL change plus vite que les agents.** Un index ajouté, une jointure revue : rien
   à toucher côté agent.

Usage :
    python -m sources.database
    python -m sources.database --dsn "postgresql://..." --requete portefeuille
"""
from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from decimal import Decimal

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

DSN_DEFAUT = "postgresql://rita:rita_dev_local@localhost:5432/rita"


# =============================================================================
# R1 — le portefeuille valorisé, converti en euros
# =============================================================================
# Forme LATERAL et non CTE DISTINCT ON : mesuré 250× plus rapide sur les données
# réelles (1,19 ms contre 295,19 ms). Détail du raisonnement dans db/requetes.sql.
SQL_PORTEFEUILLE = """
WITH taux_du_jour AS (
    SELECT DISTINCT ON (devise) devise, valeur_pour_eur
    FROM   taux_change
    ORDER  BY devise, date_taux DESC
)
SELECT  v.ticker, v.nom_officiel, v.statut_qualite,
        p.quantite, p.pru, p.devise,
        d.date_seance AS date_cours, d.cloture AS cours,
        ROUND(p.quantite * p.pru / COALESCE(t.valeur_pour_eur, 1), 2)      AS investi_eur,
        ROUND(p.quantite * d.cloture / COALESCE(t.valeur_pour_eur, 1), 2)  AS valorisation_eur,
        ROUND((d.cloture - p.pru) / p.pru * 100, 2)                        AS performance_pct
FROM        position p
JOIN        valeur   v ON v.ticker = p.ticker
LEFT JOIN LATERAL (
    SELECT c.date_seance, c.cloture FROM cotation c
    WHERE  c.ticker = p.ticker ORDER BY c.date_seance DESC LIMIT 1
) d ON TRUE
LEFT JOIN   taux_du_jour t ON t.devise = p.devise
ORDER BY    performance_pct DESC NULLS LAST
"""

# =============================================================================
# R2 — les plus forts mouvements de la dernière séance
# =============================================================================
# `derniere_seance` est calculée PAR TICKER : mesuré le 01/08, le 2026-07-29 ne
# compte que 2 valeurs (cotées aux États-Unis) contre 106 le 2026-07-28.
SQL_MOUVEMENTS = """
WITH derniere_seance AS (
    SELECT ticker, max(date_seance) AS derniere FROM cotation GROUP BY ticker
),
deux_seances AS (
    SELECT c.ticker, c.date_seance, c.cloture,
           LAG(c.cloture) OVER (PARTITION BY c.ticker ORDER BY c.date_seance) AS cloture_veille
    FROM   cotation c
    JOIN   derniere_seance d ON d.ticker = c.ticker
    WHERE  c.date_seance >= d.derniere - INTERVAL '10 days'
)
SELECT  s.ticker, v.nom_officiel, s.date_seance, s.cloture_veille, s.cloture,
        ROUND((s.cloture - s.cloture_veille) / s.cloture_veille * 100, 2) AS variation_pct
FROM        deux_seances    s
JOIN        valeur          v ON v.ticker = s.ticker
JOIN        derniere_seance d ON d.ticker = s.ticker AND d.derniere = s.date_seance
WHERE       s.cloture_veille IS NOT NULL
  AND       v.statut_qualite = 'OK'
ORDER BY    variation_pct DESC
LIMIT %(limite)s
"""

# =============================================================================
# R3 — volumes anormaux
# =============================================================================
SQL_VOLUMES = """
WITH derniere_seance AS (
    SELECT ticker, max(date_seance) AS derniere FROM cotation GROUP BY ticker
),
recent AS (
    SELECT c.ticker, c.date_seance, c.volume, c.cloture
    FROM   cotation c
    JOIN   derniere_seance d ON d.ticker = c.ticker
    WHERE  c.date_seance >= d.derniere - INTERVAL '60 days'
),
avec_moyenne AS (
    SELECT r.*, AVG(r.volume) OVER (PARTITION BY r.ticker ORDER BY r.date_seance
                                    ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS moyenne_20j
    FROM   recent r
)
SELECT  a.ticker, v.nom_officiel, a.date_seance, a.volume,
        ROUND(a.moyenne_20j)               AS moyenne_20j,
        ROUND(a.volume / a.moyenne_20j, 2) AS ratio,
        a.cloture
FROM        avec_moyenne    a
JOIN        valeur          v ON v.ticker = a.ticker
JOIN        derniere_seance d ON d.ticker = a.ticker AND d.derniere = a.date_seance
WHERE       a.moyenne_20j > 0
  AND       a.volume / a.moyenne_20j > %(seuil)s
  AND       v.statut_qualite = 'OK'
ORDER BY    ratio DESC
LIMIT %(limite)s
"""


@dataclass
class Extraction:
    """Le résultat d'une requête, avec de quoi le tracer."""
    nom: str
    lignes: list[dict]
    nb: int

    def __len__(self) -> int:
        return self.nb


def _connexion(dsn: str | None = None):
    return psycopg2.connect(dsn or os.getenv("DATABASE_URL", DSN_DEFAUT))


def _executer(sql: str, nom: str, dsn: str | None = None, **params) -> Extraction:
    """Exécute une requête et retourne des dictionnaires Python.

    `RealDictCursor` renvoie des dicts au lieu de tuples : le code appelant nomme les
    colonnes au lieu de les compter. Un `ligne[3]` devient faux dès qu'on ajoute une
    colonne au SELECT ; un `ligne["cours"]` reste juste.
    """
    with _connexion(dsn) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params or None)
            lignes = [dict(r) for r in cur.fetchall()]

    logger.info("Requete %s : %d ligne(s)", nom, len(lignes))
    return Extraction(nom=nom, lignes=lignes, nb=len(lignes))


def portefeuille(dsn: str | None = None) -> Extraction:
    """R1 — le portefeuille valorisé, converti en euros."""
    return _executer(SQL_PORTEFEUILLE, "portefeuille", dsn)


def mouvements(dsn: str | None = None, limite: int = 5) -> Extraction:
    """R2 — les plus fortes variations de la dernière séance."""
    return _executer(SQL_MOUVEMENTS, "mouvements", dsn, limite=limite)


def volumes_anormaux(dsn: str | None = None, seuil: float = 2.0,
                     limite: int = 10) -> Extraction:
    """R3 — les valeurs dont le volume dépasse `seuil` fois leur moyenne 20 séances."""
    return _executer(SQL_VOLUMES, "volumes_anormaux", dsn, seuil=seuil, limite=limite)


def total_portefeuille(extraction: Extraction) -> Decimal:
    """Somme des valorisations, en euros — donc additionnable, contrairement au CSV brut."""
    return sum((l["valorisation_eur"] or Decimal(0)) for l in extraction.lignes)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    parseur = argparse.ArgumentParser(description="Extraction SQL depuis PostgreSQL (C1/C2)")
    parseur.add_argument("--dsn", default=None)
    parseur.add_argument("--requete", choices=["portefeuille", "mouvements", "volumes", "tout"],
                         default="tout")
    args = parseur.parse_args()

    if args.requete in ("portefeuille", "tout"):
        e = portefeuille(args.dsn)
        print("\n=== R1 · PORTEFEUILLE VALORISE (converti en EUR) ===")
        print(f"{'Ticker':<10}{'Nom':<22}{'Qte':>7}{'PRU':>10}{'Cours':>10}"
              f"{'Valo EUR':>12}{'Perf %':>10}")
        print("-" * 81)
        for l in e.lignes:
            print(f"{l['ticker']:<10}{(l['nom_officiel'] or '')[:21]:<22}"
                  f"{l['quantite']:>7.0f}{l['pru']:>10.2f}"
                  f"{(l['cours'] or 0):>10.2f}{(l['valorisation_eur'] or 0):>12,.2f}"
                  f"{(l['performance_pct'] or 0):>10.2f}")
        print("-" * 81)
        print(f"{'TOTAL':<49}{total_portefeuille(e):>12,.2f} EUR")

    if args.requete in ("mouvements", "tout"):
        e = mouvements(args.dsn)
        print("\n=== R2 · PLUS FORTS MOUVEMENTS DE LA DERNIERE SEANCE ===")
        for l in e.lignes:
            print(f"  {l['ticker']:<10}{(l['nom_officiel'] or '')[:24]:<26}"
                  f"{l['cloture_veille']:>10.2f} -> {l['cloture']:>10.2f}"
                  f"{l['variation_pct']:>9.2f} %")

    if args.requete in ("volumes", "tout"):
        e = volumes_anormaux(args.dsn)
        print("\n=== R3 · VOLUMES ANORMAUX (> 2x la moyenne 20 seances) ===")
        if not e.lignes:
            print("  aucun signal sur la derniere seance")
        for l in e.lignes:
            print(f"  {l['ticker']:<10}{(l['nom_officiel'] or '')[:24]:<26}"
                  f"volume {l['volume']:>10,}  moy {l['moyenne_20j']:>10,}"
                  f"  ratio {l['ratio']:>6.2f}x")
    print()

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
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

# ⚠️ Le `.env` se charge ICI, dans le module qui ouvre réellement la connexion.
#
# Avant le 28/08/2026, il se chargeait dans les APPELANTS — six modules le faisaient
# à la place de celui qui en avait besoin. Résultat : chaque nouvel appelant devait y
# penser, et **quatre l'ont oublié** : `db/importer.py` (17/08, commit a7a3dba),
# `indicateurs/socle.py`, `monitorage/fraicheur.py` (25/08), puis un script d'analyse
# le 28/08. À chaque fois le même symptôme — connexion tentée sur le port **5432**
# au lieu de **5433**, parce que `DATABASE_URL` était absente et que `DSN_DEFAUT`
# prenait le relais.
#
# Corriger le quatrième symptôme aurait garanti un cinquième. La cause était
# architecturale : *le module qui a besoin d'une configuration doit la charger
# lui-même, pas compter sur ses appelants pour le faire.*
#
# `load_dotenv` est idempotent et ne remplace pas une variable déjà définie : les
# appels des six modules restent inoffensifs, et l'environnement du conteneur Docker
# (où `DATABASE_URL` est posée par `docker-compose`) garde la priorité.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ⚠️ Ce défaut vise le port **5432**, alors que la base tourne sur **5433**.
# Il n'est atteint que si `DATABASE_URL` est absente — c'est-à-dire quand la
# configuration manque. Il produit alors une erreur de connexion plutôt qu'un
# silence, ce qui est le comportement voulu. **Ne pas le "corriger" en 5433** :
# une valeur par défaut qui marche masquerait l'absence de configuration, exactement
# comme la clé `dev-key` masquait l'absence de `RITA_API_KEY` (evidence/C21/INC-001).
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
        ROUND(p.quantite * p.pru / CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END, 2)     AS investi_eur,
        ROUND(p.quantite * d.cloture / CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END, 2) AS valorisation_eur,
        ROUND((d.cloture - p.pru) / p.pru * 100, 2)                        AS performance_pct,
        -- Plan 65 (03/10/2026, cas D06 du chapitre Donnees) : l'euro se convertit par 1 sans lire
        -- taux_change ; une devise etrangere sans taux rend NULL et le dit, au lieu de diviser par 1
        -- et d'afficher un montant en dollars comme des euros. La ligne reste visible (LEFT JOIN).
        CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END       AS taux_pour_eur,
        (p.devise <> 'EUR' AND t.valeur_pour_eur IS NULL)                  AS taux_manquant
FROM        position p
JOIN        valeur   v ON v.ticker = p.ticker
LEFT JOIN LATERAL (
    SELECT c.date_seance, c.cloture FROM cotation c
    WHERE  c.ticker = p.ticker ORDER BY c.date_seance DESC LIMIT 1
) d ON TRUE
LEFT JOIN   taux_du_jour t ON t.devise = p.devise
WHERE       p.date_cloture IS NULL
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


def dsn_api() -> str:
    """L'adresse de la base pour l'API (carte #76, 06/11/2026) : `POSTGRES_DSN_API`, le rôle `rita_api` (lecture, plus
    l'ajout au journal d'audit), sinon `DATABASE_URL`, le poste de développement. Le préfixe `POSTGRES_` est voulu : le
    pré-test de la livraison l'écarte déjà (`deploy/deployer.py`, `env_du_pretest`)."""
    return os.getenv("POSTGRES_DSN_API") or os.getenv("DATABASE_URL", DSN_DEFAUT)


def _connexion(dsn: str | None = None):
    return psycopg2.connect(dsn or dsn_api())


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


def positions_closes(dsn: str | None = None) -> int:
    """Combien de positions sont closes (plan 66) : comptees par l'API, jamais servies."""
    e = _executer("SELECT count(*) AS nb FROM position WHERE date_cloture IS NOT NULL", "positions_closes", dsn)
    return int(e.lignes[0]["nb"]) if e.lignes else 0


def positions_sans_taux(extraction: Extraction) -> int:
    """Combien de lignes n'ont pas de taux de change (plan 65, cas D06)."""
    return sum(1 for l in extraction.lignes if l.get("taux_manquant"))


def total_portefeuille(extraction: Extraction) -> Decimal | None:
    """Somme des valorisations, en euros, donc additionnable, contrairement au CSV brut.

    `None` dès qu'une ligne n'a pas de taux (décision D1 d'Era, 03/10/2026) : un total partiel
    présenté comme total est le même mensonge à une autre échelle. Avant, un `NULL` comptait 0.
    """
    if positions_sans_taux(extraction):
        return None
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

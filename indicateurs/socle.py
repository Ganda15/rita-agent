"""Indicateurs de marché — lot 1 « socle ».

Spécification : `docs/indicateurs/CONCEPTION.md` §5
Requête       : `db/indicateurs.sql`
Livrable      : E4 — alimente l'écran 2 de l'application.

⚠️ **RITA calcule des indicateurs, jamais des stratégies.**
Un indicateur est un fait (« le cours est 5 % sous son plus haut »).
Une stratégie est un conseil (« RSI > 70 → vendre »). Ce module ne produit
que des faits : un nombre, son unité, sa fenêtre, sa date. Aucun verbe
d'action, aucun classement « meilleures valeurs ». Contrainte AMF.

Le calcul vit dans le SQL, pas ici. Ce module ne fait que trois choses :
lire la requête, l'exécuter, et convertir le résultat en objets Python
utilisables par l'API. C'est délibéré — dupliquer la logique de fenêtrage
en Python créerait deux vérités qui divergeraient.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, asdict
from decimal import Decimal
from datetime import date
from pathlib import Path
from typing import Any

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Sans cette ligne, le module ne lit PAS le `.env` : `DATABASE_URL` est absente et
# rien ne fonctionne hors du serveur d'API (seul `api/main.py` appelait
# `load_dotenv()`). C'est exactement le défaut corrigé le 17/08 sur `db/importer.py`
# (commit a7a3dba) — un module qui ne trouve pas sa propre configuration n'est pas
# fonctionnel, quelle que soit la qualité de son code.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Au-delà de ce délai, la dernière cotation d'une valeur est jugée périmée.
# 40 jours : plus long qu'un pont ou qu'une suspension de cotation courte,
# assez court pour attraper une radiation. Mesuré le 18/08/2026 — 3 valeurs
# de l'univers dépassent ce seuil (Zodiac 2018, Euler Hermes 2018, Gemalto 2019).
SEUIL_PERIME_JOURS = 40

_REQUETE = Path(__file__).parent.parent / "db" / "indicateurs.sql"


@dataclass(frozen=True)
class IndicateursValeur:
    """Les 11 indicateurs du lot 1, pour une valeur, à une date.

    Tout champ peut valoir None : un historique trop court ne permet pas de
    calculer une performance 1 an, et rendre 0 serait un chiffre inventé.
    """

    ticker: str
    nom_officiel: str
    devise: str
    statut_qualite: str
    date_cours: date
    cours: float | None

    fraicheur_jours: int

    perf_1j_pct: float | None
    perf_1s_pct: float | None
    perf_1m_pct: float | None
    perf_ytd_pct: float | None
    perf_1a_pct: float | None

    ma20: float | None
    ma50: float | None
    adtv20: float | None
    distance_plus_haut_1a_pct: float | None

    @property
    def cotation_perimee(self) -> bool:
        """La dernière cotation est-elle trop ancienne pour être lue telle quelle ?

        Une valeur radiée garde `statut_qualite = 'OK'` : le statut décrit la
        qualité de l'historique, pas sa fraîcheur. Les deux notions sont
        distinctes et doivent le rester.
        """
        return self.fraicheur_jours > SEUIL_PERIME_JOURS

    def en_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["date_cours"] = self.date_cours.isoformat()
        d["cotation_perimee"] = self.cotation_perimee
        return d


def _nombre(valeur: Any) -> float | None:
    """PostgreSQL rend du NUMERIC, que psycopg2 traduit en Decimal.

    On normalise une seule fois, ici. Laisser des Decimal remonter jusqu'à
    l'API obligerait chaque appelant à s'en méfier.
    """
    if valeur is None:
        return None
    if isinstance(valeur, Decimal):
        return float(valeur)
    return float(valeur)


def construire(ligne: dict[str, Any]) -> IndicateursValeur:
    """Convertit une ligne de la requête en objet. Séparé de l'accès à la base
    pour être testable sans PostgreSQL."""
    return IndicateursValeur(
        ticker=ligne["ticker"],
        nom_officiel=ligne["nom_officiel"],
        devise=ligne["devise"],
        statut_qualite=ligne["statut_qualite"],
        date_cours=ligne["date_cours"],
        cours=_nombre(ligne["cours"]),
        fraicheur_jours=int(ligne["fraicheur_jours"]),
        perf_1j_pct=_nombre(ligne["perf_1j_pct"]),
        perf_1s_pct=_nombre(ligne["perf_1s_pct"]),
        perf_1m_pct=_nombre(ligne["perf_1m_pct"]),
        perf_ytd_pct=_nombre(ligne["perf_ytd_pct"]),
        perf_1a_pct=_nombre(ligne["perf_1a_pct"]),
        ma20=_nombre(ligne["ma20"]),
        ma50=_nombre(ligne["ma50"]),
        adtv20=_nombre(ligne["adtv20"]),
        distance_plus_haut_1a_pct=_nombre(ligne["distance_plus_haut_1a_pct"]),
    )


def _executer(sql: str, parametres: tuple | None = None) -> list[dict[str, Any]]:
    """Le seul point d'accès à la base de ce module.

    Isolé dans sa propre fonction pour que les tests puissent le remplacer sans
    PostgreSQL. ⚠️ C'est aussi la limite connue de ces tests : ils vérifient la
    conversion et les règles métier, **pas** le SQL lui-même. Le SQL est vérifié
    par exécution réelle, tracée dans `evidence/`.
    """
    # Carte #76 : la même adresse que le reste de l'API (`POSTGRES_DSN_API`, le rôle `rita_api`, sinon `DATABASE_URL`).
    url = os.environ.get("POSTGRES_DSN_API") or os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL absente. Voir .env.example — le serveur écoute sur le port 5433."
        )
    with psycopg2.connect(url) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # `None` et non `()` : psycopg2 n'interpole QUE si le second argument
            # n'est pas None. Avec un tuple vide, il tente l'interpolation et
            # échoue sur le moindre « % » du SQL — y compris dans un commentaire.
            cur.execute(sql, parametres)
            return [dict(l) for l in cur.fetchall()]


def valeur_existe(ticker: str) -> bool:
    """La valeur est-elle dans le référentiel ? (sprint 4, tâche C1 ; critère 3 du contrat du sprint 1)

    Lue par la route `/briefing` avant tout appel au modèle. La valeur passe en paramètre de la requête, jamais dans son
    texte : une valeur comme « X'; DROP TABLE valeur; -- » ne peut rien y faire.
    """
    return bool(_executer("SELECT 1 AS present FROM valeur WHERE ticker = %s", (ticker,)))


def lire_socle(tickers: list[str] | None = None) -> list[IndicateursValeur]:
    """Les 11 indicateurs du lot 1, pour tout l'univers ou pour une sélection.

    Args:
        tickers: si fourni, restreint le résultat. Le filtre s'applique **après**
            le calcul : les fenêtres glissantes ont besoin de l'historique complet
            de chaque valeur, jamais de celui des autres.
    """
    sql = _REQUETE.read_text(encoding="utf-8")

    if tickers:
        # La requête se termine par `ORDER BY r.ticker;` — on insère le filtre
        # avant, plutôt que d'envelopper : envelopper masquerait le plan
        # d'exécution derrière une sous-requête et rendrait EXPLAIN illisible.
        sql = sql.rstrip().rstrip(";")
        sql = sql.replace("ORDER BY    r.ticker", "WHERE r.ticker = ANY(%s)\nORDER BY    r.ticker")
        return [construire(l) for l in _executer(sql, (tickers,))]

    return [construire(l) for l in _executer(sql)]


if __name__ == "__main__":
    lignes = lire_socle()
    perimees = [i for i in lignes if i.cotation_perimee]

    print("=" * 78)
    print("INDICATEURS - LOT 1 (socle)")
    print("=" * 78)
    print(f"  valeurs                  : {len(lignes)}")
    print(f"  cotations perimees       : {len(perimees)}  (> {SEUIL_PERIME_JOURS} jours)")
    print()
    print(f"  {'ticker':<9} {'cours':>10} {'1j %':>8} {'1a %':>8} {'MA20':>10} {'/haut %':>9}")
    print("  " + "-" * 60)
    for i in lignes[:8]:
        f = lambda v: "     -" if v is None else f"{v:>6.2f}"
        print(f"  {i.ticker:<9} {i.cours:>10.2f} {f(i.perf_1j_pct):>8} "
              f"{f(i.perf_1a_pct):>8} {i.ma20:>10.2f} {f(i.distance_plus_haut_1a_pct):>9}")

    if perimees:
        print()
        print("  COTATIONS PERIMEES - a signaler a l'ecran, jamais a masquer :")
        for i in perimees:
            print(f"    {i.ticker:<9} {i.nom_officiel:<22} "
                  f"derniere seance {i.date_cours} ({i.fraicheur_jours} jours)")

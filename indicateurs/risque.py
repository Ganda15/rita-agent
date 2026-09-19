"""Indicateurs de marché — lot 3 « risque ».

Spécification : `docs/indicateurs/CONCEPTION.md` §7
Requête SQL   : `db/indicateurs_risque.sql` (volatilité, drawdown)
Ce module     : le RSI 14 — calcul récursif, non exprimable en SQL simple
Livrable      : E4 — alimente l'écran 2.

⚠️ **Des indicateurs, jamais des stratégies.** Un RSI de 71 est un **fait**.
« RSI > 70 → vendre » serait un **conseil** — l'exemple même donné par la
spécification pour illustrer l'interdit. Aucun seuil, aucune couleur d'alerte.

⚠️ **`quant_metrics.py` (dépôt `daily-stock-analysis-era`) a été relu le 19/08/2026
et n'a PAS été réutilisé — deuxième fois pour ce projet.** Sa fonction `_rsi` utilise
une **moyenne mobile simple** (`.rolling(period).mean()`), pas le **lissage de
Wilder** que la spécification impose explicitement :

    « la variante "moyenne simple" circule partout et donne des valeurs
      DIFFÉRENTES. Écrire laquelle est implémentée, sinon le chiffre n'est pas
      reproductible. Décision : Python, avec une moyenne exponentielle de
      facteur 1/14. »

Ses fonctions `_annualized_vol` et `_max_drawdown_pct` utilisent `pct_change()`
(rendement SIMPLE) et `cummax()` (maximum incluant le jour COURANT) — la
spécification impose un rendement LOGARITHMIQUE et un maximum arrêté à la VEILLE.
D'où `db/indicateurs_risque.sql`, écrit en SQL plutôt que porté.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from indicateurs import socle

PERIODE_RSI = 14

_REQUETE = Path(__file__).parent.parent / "db" / "indicateurs_risque.sql"
_MARQUEUR = re.compile(r"^--\s*@@REQUETE\s+(\w+)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class IndicateursRisqueValeur:
    """Volatilité et drawdown pour une valeur — I4 et I5, calculés en SQL."""

    ticker: str
    nom_officiel: str
    statut_qualite: str
    date_cours: str
    cours: float | None
    fraicheur_jours: int
    volatilite_annualisee_pct: float | None
    drawdown_max_1a_pct: float | None

    @property
    def cotation_perimee(self) -> bool:
        """Même seuil et même raisonnement que le lot 1 (`socle.SEUIL_PERIME_JOURS`).

        ⚠️ **Trouvé en vérifiant l'API le 19/08/2026** : sans ce drapeau, les 3
        valeurs radiées affichaient une volatilité et un drawdown calculés sur
        leur historique de **2018**, avec `fraicheur_jours` présent mais jamais
        exploité — le même angle mort que celui corrigé sur le lot 1 le 18/08.
        """
        return self.fraicheur_jours > socle.SEUIL_PERIME_JOURS

    def en_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["date_cours"] = self.date_cours
        d["cotation_perimee"] = self.cotation_perimee
        return d


def _charger_requete() -> str:
    texte = _REQUETE.read_text(encoding="utf-8")
    m = _MARQUEUR.search(texte)
    if not m:
        raise RuntimeError(f"Aucun marqueur @@REQUETE dans {_REQUETE}")
    return texte[m.end():].strip().rstrip(";")


def lire_volatilite_drawdown(tickers: list[str] | None = None) -> list[IndicateursRisqueValeur]:
    """I4 (volatilité annualisée 20 séances) et I5 (drawdown max 1 an).

    Les deux sont exprimables en fonctions fenêtre SQL — voir
    `db/indicateurs_risque.sql`, qui documente le piège de conception qui a
    cassé la première version (fonctions fenêtre placées après le filtre sur
    la dernière séance, réduisant la fenêtre à une seule ligne).
    """
    lignes = socle._executer(_charger_requete())
    if tickers:
        lignes = [l for l in lignes if l["ticker"] in tickers]
    return [
        IndicateursRisqueValeur(
            ticker=l["ticker"],
            nom_officiel=l["nom_officiel"],
            statut_qualite=l["statut_qualite"],
            date_cours=l["date_cours"].isoformat(),
            cours=socle._nombre(l["cours"]),
            fraicheur_jours=int(l["fraicheur_jours"]),
            volatilite_annualisee_pct=socle._nombre(l["volatilite_annualisee_pct"]),
            drawdown_max_1a_pct=socle._nombre(l["drawdown_max_1a_pct"]),
        )
        for l in lignes
    ]


@dataclass(frozen=True)
class RSI:
    """Le RSI 14 d'une valeur, à la date la plus récente disponible."""

    ticker: str
    date_cours: str
    rsi_14: float | None

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


def rsi_wilder(cours: Sequence[float], periode: int = PERIODE_RSI) -> float | None:
    """Le RSI, avec le lissage RÉCURSIF de Wilder — pas une moyenne mobile simple.

    Chaque moyenne dépend de la précédente :
        moyenne_t = (moyenne_{t-1} × (période − 1) + valeur_t) / période

    C'est ce qui rend le calcul impossible à exprimer en une fonction fenêtre SQL
    ordinaire (`AVG(...) OVER (...)` ne regarde jamais son propre résultat
    précédent) — la spécification écarte volontairement un CTE récursif, jugé
    illisible, au profit de ce calcul en Python.

    Args:
        cours: clôtures dans l'ordre chronologique (la plus ancienne en premier).
        periode: 14 par défaut — le RSI « classique ».

    Returns:
        Le RSI (0 à 100), ou `None` si l'historique est trop court pour calculer
        ne serait-ce que la première moyenne.
    """
    if len(cours) <= periode:
        return None

    variations = [cours[i] - cours[i - 1] for i in range(1, len(cours))]
    hausses = [max(v, 0.0) for v in variations]
    baisses = [max(-v, 0.0) for v in variations]

    # Amorce de Wilder : une moyenne simple sur les `periode` premières
    # variations. C'est ELLE que le test « 14 hausses consécutives ⇒ 100 »
    # (§7.3 de la spec) vérifie directement — avec exactement 14 variations,
    # l'amorce EST le résultat final, rien à lisser après.
    moyenne_hausses = sum(hausses[:periode]) / periode
    moyenne_baisses = sum(baisses[:periode]) / periode

    # Puis le lissage récursif sur le reste de l'historique disponible.
    for i in range(periode, len(variations)):
        moyenne_hausses = (moyenne_hausses * (periode - 1) + hausses[i]) / periode
        moyenne_baisses = (moyenne_baisses * (periode - 1) + baisses[i]) / periode

    if moyenne_baisses == 0.0:
        # ⚠️ Piège 3 de la spec : 14 séances sans AUCUNE baisse ⇒ division par
        # zéro ⇒ RSI = 100 PAR CONVENTION. Codé explicitement, pas laissé
        # remonter comme une exception — une division par zéro non gérée ici
        # ferait planter le calcul pour la valeur la plus haussière du jour,
        # ce qui serait absurde.
        return 100.0

    rs = moyenne_hausses / moyenne_baisses
    return round(100.0 - 100.0 / (1.0 + rs), 2)


def lire_rsi(tickers: list[str] | None = None) -> list[RSI]:
    """Le RSI 14 de chaque valeur, à sa dernière séance connue.

    ⚠️ **Fenêtre calée sur le `MAX(date_seance)` GLOBAL**, pas sur la dernière
    séance de chaque ticker — à la différence de `lire_volatilite_drawdown()`.
    Conséquence assumée : les valeurs radiées (dernière séance en 2018-2019)
    **n'apparaissent pas** ici, faute de donnée dans les 400 derniers jours
    calendaires. Un RSI daté de 2018 ne dirait rien d'utile sur « aujourd'hui » ;
    l'absence est plus honnête qu'un chiffre resservi hors de son contexte.
    `lire_volatilite_drawdown()`, elle, les inclut avec `cotation_perimee=True` :
    la volatilité passée reste une mesure valide de ce qui s'est produit, même
    ancienne — ce n'est pas le même type d'affirmation qu'un RSI « actuel ».

    Args:
        tickers: si fourni, restreint le calcul à ces valeurs. Absent = tout
            l'univers (111).
    """
    sql = """
        SELECT ticker, date_seance, cloture
        FROM   cotation
        WHERE  date_seance >= (SELECT MAX(date_seance) FROM cotation) - INTERVAL '400 days'
          AND  (%(tickers)s::text[] IS NULL OR ticker = ANY(%(tickers)s))
        ORDER  BY ticker, date_seance
    """
    lignes = socle._executer(sql, {"tickers": tickers})

    par_ticker: dict[str, list[dict]] = {}
    for l in lignes:
        par_ticker.setdefault(l["ticker"], []).append(l)

    resultats = []
    for ticker, historique in par_ticker.items():
        cours = [socle._nombre(l["cloture"]) for l in historique]
        resultats.append(RSI(
            ticker=ticker,
            date_cours=historique[-1]["date_seance"].isoformat(),
            rsi_14=rsi_wilder(cours),
        ))
    return sorted(resultats, key=lambda r: r.ticker)

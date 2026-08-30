"""Scout — lit dans la BASE les indicateurs de la valeur (C1, C8).

Jusqu'au 30/08/2026 ce module appelait **yfinance sur le réseau**, avec dix tickers
écrits en dur. Le briefing ignorait donc les 275 000 cotations collectées, la
conception Merise et les indicateurs calculés : le seul endroit où RITA rédige
allait chercher son prix ailleurs.

Il lit désormais la base **par les mêmes modules que l'API** — `indicateurs.socle`
et `indicateurs.risque`. Un seul chemin d'accès aux données, donc un seul
comportement à tester et à défendre.

⚠️ Conséquence assumée : le prix n'est plus le cours *live* mais celui de la
**dernière séance collectée** (19h00 chaque jour). C'est plus lent, et bien plus
défendable : chaque chiffre remonte à une ligne de la base, et `fraicheur_jours`
dit à voix haute quel âge il a.
"""
from typing import Any, TypedDict

from indicateurs.risque import lire_volatilite_drawdown
from indicateurs.socle import lire_socle


class ScoutState(TypedDict):
    """Ce que le Scout rend au graphe.

    ⚠️ Il n'y a **pas** de champ `volume` : la base rend `adtv20`, la *moyenne*
    des volumes sur 20 séances. Appeler une moyenne « volume » ferait écrire au
    rédacteur « volume échangé » sur une moyenne mobile, sans que rien ne le
    signale. Le nom dit la mesure.
    """

    ticker: str
    price: float
    change_pct: float
    adtv20: float | None
    currency: str
    fraicheur_jours: int
    cotation_perimee: bool
    indicateurs: dict[str, Any]
    error: str


def _sans_donnees(ticker: str, motif: str) -> ScoutState:
    """L'état de refus. `error` non vide fait sauter le rédacteur (`graph/workflow.py`).

    Rendre des zéros avec `error` vide produirait un briefing rédigé sur une valeur
    qui n'existe pas — une erreur muette est pire qu'une erreur bruyante.
    """
    return {"ticker": ticker, "price": 0.0, "change_pct": 0.0, "adtv20": None,
            "currency": "", "fraicheur_jours": 0, "cotation_perimee": False,
            "indicateurs": {}, "error": motif}


def collect(ticker: str) -> ScoutState:
    """Les indicateurs de la valeur, lus en base.

    Args:
        ticker: code boursier, ex. 'MC.PA'.

    Returns:
        L'état du Scout. En cas de ticker absent, `error` est rempli et les
        chiffres restent à zéro.
    """
    lignes = lire_socle([ticker])
    if not lignes:
        return _sans_donnees(ticker, f"ticker absent de la base : {ticker}")

    socle = lignes[0]
    indicateurs = socle.en_dict()

    # Le lot 3 est facultatif : une valeur au trop court historique n'a ni
    # volatilité ni drawdown. Son absence n'est pas une erreur — le briefing
    # se rédige sans, il ne se rédige pas sans cours.
    risque = lire_volatilite_drawdown([ticker])
    if risque:
        mesures = risque[0].en_dict()
        indicateurs["volatilite_annualisee_pct"] = mesures["volatilite_annualisee_pct"]
        indicateurs["drawdown_max_1a_pct"] = mesures["drawdown_max_1a_pct"]

    return {
        "ticker": socle.ticker,
        "price": socle.cours if socle.cours is not None else 0.0,
        "change_pct": socle.perf_1j_pct if socle.perf_1j_pct is not None else 0.0,
        "adtv20": socle.adtv20,
        "currency": socle.devise,
        "fraicheur_jours": socle.fraicheur_jours,
        "cotation_perimee": socle.cotation_perimee,
        "indicateurs": indicateurs,
        "error": "",
    }

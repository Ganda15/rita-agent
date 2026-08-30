"""État partagé du graphe LangGraph — passé de nœud en nœud (C8)."""
from typing import Any, TypedDict


class RitaState(TypedDict):
    """⚠️ Doit rester aligné sur `agents.scout.ScoutState`, plus `briefing`.

    Pas de champ `volume` : la base rend `adtv20`, une *moyenne* sur 20 séances.
    Voir `agents/scout.py` — le nom dit la mesure.
    """

    ticker: str
    price: float
    change_pct: float
    adtv20: float | None
    currency: str
    fraicheur_jours: int
    cotation_perimee: bool
    indicateurs: dict[str, Any]
    briefing: str
    error: str

"""État partagé du graphe LangGraph — passé de nœud en nœud (C8)."""
from typing import TypedDict


class RitaState(TypedDict):
    ticker: str
    price: float
    change_pct: float
    volume: int
    currency: str
    briefing: str
    error: str

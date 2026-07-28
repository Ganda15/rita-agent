"""Superviseur — StateGraph LangGraph : Scout puis Rédacteur (C8, C14)."""
from langgraph.graph import StateGraph, END

from agents.analyst import generate_briefing
from agents.scout import collect
from graph.state import RitaState


def noeud_scout(state: RitaState) -> RitaState:
    donnees = collect(state["ticker"])
    return {**state, **donnees}


def noeud_redacteur(state: RitaState) -> RitaState:
    if state["error"]:
        return {**state, "briefing": ""}
    texte = generate_briefing(
        state["ticker"], state["price"], state["change_pct"],
        state["volume"], state["currency"],
    )
    return {**state, "briefing": texte}


def construire_graphe():
    graphe = StateGraph(RitaState)
    graphe.add_node("scout", noeud_scout)
    graphe.add_node("redacteur", noeud_redacteur)
    graphe.set_entry_point("scout")
    graphe.add_edge("scout", "redacteur")
    graphe.add_edge("redacteur", END)
    return graphe.compile()


def generer_briefing_complet(ticker: str) -> RitaState:
    """Point d'entrée : exécute Scout → Rédacteur pour un ticker donné."""
    app = construire_graphe()
    return app.invoke({
        "ticker": ticker, "price": 0.0, "change_pct": 0.0,
        "volume": 0, "currency": "", "briefing": "", "error": "",
    })

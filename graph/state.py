"""État partagé du graphe LangGraph — passé de nœud en nœud (C8)."""
from typing import Any, TypedDict


class RitaState(TypedDict):
    """⚠️ Doit rester aligné sur `agents.scout.ScoutState`, plus `briefing` et `modele_info`.

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

    # Ce que le RAG a trouvé — étape 4c. `motif_rag` vaut "OK", "OUT_OF_CORPUS"
    # (aucune preuve suffisante) ou "NON_APPELE" (le Scout avait déjà échoué).
    # ⚠️ Un corpus sans article n'est PAS une erreur : `error` reste vide et le
    # briefing chiffré se rédige quand même.
    passages: list[dict[str, Any]]
    motif_rag: str

    briefing: str
    # Qui a écrit le briefing (refonte 001, exigence R4) : `fournisseur`, `modele` (celui que le fournisseur a renvoyé,
    # None s'il ne le dit pas) et `tentatives` ([{"fournisseur": str, "reussi": bool}], sans message d'erreur).
    # Vide quand le rédacteur est sauté : personne n'a écrit, il n'y a personne à nommer.
    modele_info: dict[str, Any]
    error: str

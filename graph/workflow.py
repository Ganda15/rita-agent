"""Superviseur — StateGraph LangGraph : Scout puis Rédacteur (C8, C14)."""
from langgraph.graph import StateGraph, END

from agents.analyst import articles_surs, generate_briefing_detaille
from agents.scout import collect
from graph.state import RitaState
from rag.recherche import rechercher
from src import traces
from src.llm import ResultatTexte


def noeud_scout(state: RitaState) -> RitaState:
    with traces.etape("scout") as span:
        donnees = collect(state["ticker"])
        # Résumé seulement : des données de marché publiques, jamais une position ni un PRU.
        traces.terminer_etape(span, output={
            "ticker": donnees.get("ticker"), "fraicheur_jours": donnees.get("fraicheur_jours"),
            "cotation_perimee": donnees.get("cotation_perimee"), "erreur": donnees.get("error") or None})
    return {**state, **donnees}


def noeud_rag(state: RitaState) -> RitaState:
    """Cherche les articles de la valeur — recherche hybride, filtrée par ticker.

    Le filtre par ticker est **déterministe et appliqué avant la recherche** : le
    ticker est connu, donc on ne cherche pas la valeur par ressemblance de sens.
    C'est la règle du brief Sorabel — quand l'information exacte est disponible,
    un filtre exact vaut mieux qu'une similarité.

    Si le Scout a échoué, on ne cherche pas : balayer le corpus pour un briefing
    qui ne sera jamais rédigé serait du travail pur perdu.
    """
    with traces.etape("rag", "retriever") as span:
        return _noeud_rag(state, span)


def _noeud_rag(state: RitaState, span) -> RitaState:
    if state["error"]:
        traces.terminer_etape(span, output={"motif": "NON_APPELE", "nb_passages": 0})
        return {**state, "passages": [], "motif_rag": "NON_APPELE"}

    # ⚠️ Le NOM COURT, jamais la raison sociale. `valeur.nom_officiel` vaut
    # « LVMH MOET VUITTON » ; la presse écrit « LVMH ». Mesuré le 30/08 :
    #     'actualite LVMH MOET VUITTON' -> OUT_OF_CORPUS  0 passage / 10 candidats
    #     'actualite LVMH'              -> OK             3 passages / 10 candidats
    # La règle de refus exige la moitié des mots significatifs, et « MOET » comme
    # « VUITTON » n'apparaissent dans aucun article. C'est la même cause que le
    # défaut de détection du 28/08 : le nom légal n'est pas le nom d'usage.
    #
    # Le premier mot suffit ICI — et seulement ici — parce que le filtre par
    # ticker a déjà garanti que les candidats citent la valeur. La question n'a
    # qu'à les CLASSER, pas à prouver leur pertinence. (Un « CREDIT » isolé serait
    # dangereux pour étiqueter un article ; il ne l'est pas pour ordonner 9
    # articles dont on sait déjà qu'ils parlent de Crédit Agricole.)
    nom = state["indicateurs"].get("nom_officiel") or state["ticker"]
    resultat = rechercher(f"actualite {nom.split()[0]}", ticker=state["ticker"])
    # Sprint 4 (A4) : un article piégé n'est pas transmis ; le compte et les sources de la trace le disent.
    passages = articles_surs([p.en_dict() for p in resultat.passages])
    # Le compte et les sources, pas le texte des articles : il est déjà dans la génération.
    traces.terminer_etape(span, output={"motif": resultat.motif, "nb_passages": len(passages),
                                        "sources": [p.get("source") for p in passages]})

    return {**state, "passages": passages, "motif_rag": resultat.motif}


def noeud_redacteur(state: RitaState) -> RitaState:
    with traces.etape("redacteur") as span:
        if state["error"]:
            traces.terminer_etape(span, output={"saute": True})
            return {**state, "briefing": "", "modele_info": {}}
        redaction = _rediger(state)
        # La longueur seulement : le texte est dans la génération, et il n'est pas encore
        # passé par le garde-fou de sortie (api/main.py).
        traces.terminer_etape(span, output={"longueur": len(redaction.texte)})
    return {**state, "briefing": redaction.texte,
            "modele_info": {"fournisseur": redaction.fournisseur, "modele": redaction.modele,
                            "tentatives": redaction.tentatives}}


def _rediger(state: RitaState) -> ResultatTexte:
    return generate_briefing_detaille(
        ticker=state["ticker"],
        price=state["price"],
        change_pct=state["change_pct"],
        adtv20=state["adtv20"],
        currency=state["currency"],
        fraicheur_jours=state["fraicheur_jours"],
        cotation_perimee=state["cotation_perimee"],
        passages=state["passages"],
        indicateurs=state.get("indicateurs") or None,
    )


def construire_graphe():
    graphe = StateGraph(RitaState)
    graphe.add_node("scout", noeud_scout)
    graphe.add_node("rag", noeud_rag)
    graphe.add_node("redacteur", noeud_redacteur)
    graphe.set_entry_point("scout")
    graphe.add_edge("scout", "rag")
    graphe.add_edge("rag", "redacteur")
    graphe.add_edge("redacteur", END)
    return graphe.compile()


def generer_briefing_complet(ticker: str) -> RitaState:
    """Point d'entrée : exécute Scout → Rédacteur pour un ticker donné."""
    app = construire_graphe()
    return app.invoke({
        "ticker": ticker, "price": 0.0, "change_pct": 0.0, "adtv20": None,
        "currency": "", "fraicheur_jours": 0, "cotation_perimee": False,
        "indicateurs": {}, "passages": [], "motif_rag": "",
        "briefing": "", "modele_info": {}, "error": "",
    })

"""Tests du graphe LangGraph — Scout puis Rédacteur (C8).

⚠️ Les faux états ci-dessous doivent rester **identiques** à ce que `collect` rend
vraiment (`agents/scout.ScoutState`). Un simulacre qui diverge du code produit des
tests verts sur du code cassé : c'est le défaut relevé le 28/08 (« test vert sur
corpus vide ») et le 30/08 (`volume` conservé dans le faux Scout alors que le
Scout ne le rendait plus).
"""
from unittest.mock import patch

from graph.workflow import generer_briefing_complet
from tests.conftest import faux_resultat_texte


def scout_lvmh(**surcharges):
    """Ce que `agents.scout.collect` rend réellement pour une valeur trouvée."""
    base = {
        "ticker": "MC.PA", "price": 545.2, "change_pct": -1.10,
        "adtv20": 128456789.0, "currency": "EUR",
        "fraicheur_jours": 2, "cotation_perimee": False,
        "indicateurs": {"ma20": 552.3, "volatilite_annualisee_pct": 24.7},
        "error": "",
    }
    base.update(surcharges)
    return base


def test_graphe_complet_scout_puis_redacteur():
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("Briefing test.")) as redacteur:
        resultat = generer_briefing_complet("MC.PA")

    assert resultat["briefing"] == "Briefing test."
    redacteur.assert_called_once()


def test_le_redacteur_recoit_adtv20_et_jamais_un_champ_volume():
    """Le graphe ne doit plus fabriquer de `volume` — il n'existe plus en amont.

    Sans ce test, `workflow.py` peut continuer à lire `state["volume"]` : la clé
    survit dans l'état initial à 0, le rédacteur écrit « volume : 0 », et aucun
    test ne le signale.
    """
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("x")) as redacteur:
        resultat = generer_briefing_complet("MC.PA")

    assert "volume" not in resultat
    assert redacteur.call_args.kwargs["adtv20"] == 128456789.0
    assert redacteur.call_args.kwargs["currency"] == "EUR"


def test_le_redacteur_est_prevenu_dune_cotation_perimee():
    """Une cotation de 2018 ne doit pas être rédigée comme celle d'hier."""
    with patch("graph.workflow.collect",
               return_value=scout_lvmh(fraicheur_jours=2000, cotation_perimee=True)), \
         patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("x")) as redacteur:
        generer_briefing_complet("MC.PA")

    assert redacteur.call_args.kwargs["cotation_perimee"] is True
    assert redacteur.call_args.kwargs["fraicheur_jours"] == 2000


def test_graphe_saute_le_redacteur_si_erreur_scout():
    erreur = scout_lvmh(ticker="XXX.PA", price=0.0, change_pct=0.0, adtv20=None,
                        currency="", indicateurs={},
                        error="ticker absent de la base : XXX.PA")
    with patch("graph.workflow.collect", return_value=erreur), \
         patch("graph.workflow.generate_briefing_detaille") as redacteur:
        resultat = generer_briefing_complet("XXX.PA")

    assert resultat["briefing"] == ""
    redacteur.assert_not_called()


# --- étape 4c : le nœud RAG ----------------------------------------------------

def passage_lvmh():
    """Un passage tel que `rag.recherche.rechercher` le rend."""
    from rag.recherche import Passage
    return Passage(
        article_id=379,
        texte="LVMH publie des resultats en hausse",
        titre="LVMH publie des resultats semestriels en hausse",
        source="Boursorama", lien="https://exemple.test/lvmh",
        publie_le="2026-08-29", tickers=["MC.PA"],
        rang_dense=0, rang_lexical=0, distance_dense=0.31, score_lexical=8.2,
    )


def resultat_rag(trouve=True, motif="OK", passages=None):
    from rag.recherche import Resultat
    return Resultat(trouve=trouve, motif=motif,
                    passages=passages if passages is not None else [passage_lvmh()],
                    nb_candidats=12)


def test_le_noeud_rag_filtre_par_ticker_avant_de_chercher():
    """Règle Sorabel : quand l'information exacte existe, un filtre exact vaut
    mieux qu'une similarité. Le ticker est connu — on ne cherche que dedans."""
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.rechercher", return_value=resultat_rag()) as moteur, \
         patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("x")):
        generer_briefing_complet("MC.PA")

    assert moteur.call_args.kwargs["ticker"] == "MC.PA"


def test_les_passages_trouves_arrivent_dans_letat():
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.rechercher", return_value=resultat_rag()), \
         patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("x")):
        resultat = generer_briefing_complet("MC.PA")

    assert resultat["motif_rag"] == "OK"
    assert len(resultat["passages"]) == 1
    assert resultat["passages"][0]["source"] == "Boursorama"
    assert resultat["passages"][0]["lien"] == "https://exemple.test/lvmh"


def test_un_refus_out_of_corpus_ne_bloque_pas_le_briefing():
    """Aucun article n'est pas une erreur : le briefing chiffré reste utile.

    Confondre « pas de source » et « pas de donnée » priverait l'utilisateur
    d'un briefing parfaitement valide.
    """
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.rechercher",
               return_value=resultat_rag(trouve=False, motif="OUT_OF_CORPUS", passages=[])), \
         patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("Briefing sans article.")):
        resultat = generer_briefing_complet("MC.PA")

    assert resultat["briefing"] == "Briefing sans article."
    assert resultat["motif_rag"] == "OUT_OF_CORPUS"
    assert resultat["passages"] == []
    assert resultat["error"] == ""


def test_le_rag_nest_jamais_appele_si_le_ticker_est_absent_de_la_base():
    """Le cas TotalEnergies : hors univers, le Scout refuse AVANT la recherche.

    Chercher des articles pour une valeur que RITA ne suit pas coûterait un
    balayage de corpus pour un briefing qui ne sera jamais rédigé.
    """
    erreur = scout_lvmh(ticker="TTE.PA", error="ticker absent de la base : TTE.PA")
    with patch("graph.workflow.collect", return_value=erreur), \
         patch("graph.workflow.rechercher") as moteur, \
         patch("graph.workflow.generate_briefing_detaille") as redacteur:
        resultat = generer_briefing_complet("TTE.PA")

    moteur.assert_not_called()
    redacteur.assert_not_called()
    assert resultat["passages"] == []


def test_le_redacteur_recoit_les_passages_trouves_par_le_rag():
    """Le dernier fil : sans ça, le RAG cherche et personne ne lit le résultat.

    C'est le point exact où l'étape 4 devient réelle — jusque-là les passages
    dorment dans l'état sans jamais atteindre le prompt.
    """
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.rechercher", return_value=resultat_rag()), \
         patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("x")) as redacteur:
        generer_briefing_complet("MC.PA")

    passages = redacteur.call_args.kwargs["passages"]
    assert len(passages) == 1
    assert passages[0]["source"] == "Boursorama"


def test_la_question_du_rag_utilise_le_nom_court_pas_la_raison_sociale():
    """Récidive du défaut LVMH, mesurée le 30/08.

    `valeur.nom_officiel` vaut « LVMH MOET VUITTON » ; la presse écrit « LVMH ».
    Interrogé avec la raison sociale, le moteur refusait TOUT :

        'actualite LVMH MOET VUITTON' -> OUT_OF_CORPUS   0 passage / 10 candidats
        'actualite LVMH'              -> OK              3 passages / 10 candidats

    La règle de refus exige la moitié des mots significatifs : « MOET » et
    « VUITTON » n'apparaissent dans aucun article, donc 1 mot sur 4 < 2 requis.
    Le filtre par ticker garantit déjà que les candidats citent la valeur — la
    question n'a qu'à les CLASSER, pas à prouver leur pertinence.
    """
    lvmh = scout_lvmh(indicateurs={"nom_officiel": "LVMH MOET VUITTON"})
    with patch("graph.workflow.collect", return_value=lvmh), \
         patch("graph.workflow.rechercher", return_value=resultat_rag()) as moteur, \
         patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("x")):
        generer_briefing_complet("MC.PA")

    question = moteur.call_args[0][0]
    assert "LVMH" in question
    assert "MOET" not in question
    assert "VUITTON" not in question


def test_le_redacteur_recoit_les_indicateurs_du_scout():
    """Les 13 indicateurs calculés par le scout vont jusqu'au rédacteur, pas seulement quatre nombres."""
    indicateurs = {"ma20": 404.9, "rsi_14": 38.4, "volatilite_annualisee_pct": 22.5}
    with patch("graph.workflow.collect", return_value=scout_lvmh(indicateurs=indicateurs)),          patch("graph.workflow.generate_briefing_detaille", return_value=faux_resultat_texte("x")) as redacteur:
        generer_briefing_complet("MC.PA")
    assert redacteur.call_args.kwargs["indicateurs"] == indicateurs



# --- Refonte 001, tâche 2 (exigence R4) : le graphe garde qui a rédigé --------------------------------

def test_redacteur_range_le_diagnostic_dans_l_etat():
    """L'écran du briefing affichera le fournisseur, le modèle et les tentatives : le graphe les garde dans l'état,
    sous `modele_info`, tels que la cascade les a rendus (`src.llm.ResultatTexte`)."""
    from src.llm import ResultatTexte
    redaction = ResultatTexte(texte="Briefing test.", fournisseur="anthropic", modele="claude-sonnet-5",
                              tentatives=[{"fournisseur": "foundry", "reussi": False},
                                          {"fournisseur": "anthropic", "reussi": True}])
    with patch("graph.workflow.collect", return_value=scout_lvmh()), \
         patch("graph.workflow.rechercher", return_value=resultat_rag(passages=[])), \
         patch("graph.workflow.generate_briefing_detaille", return_value=redaction):
        resultat = generer_briefing_complet("MC.PA")

    assert resultat["briefing"] == "Briefing test."
    assert resultat["modele_info"] == {"fournisseur": "anthropic", "modele": "claude-sonnet-5",
                                       "tentatives": [{"fournisseur": "foundry", "reussi": False},
                                                      {"fournisseur": "anthropic", "reussi": True}]}


def test_redacteur_saute_laisse_un_diagnostic_vide():
    """Une valeur absente : le rédacteur n'est pas appelé, il n'y a donc personne à nommer."""
    erreur = scout_lvmh(ticker="XXX.PA", price=0.0, change_pct=0.0, adtv20=None,
                        currency="", indicateurs={}, error="ticker absent de la base : XXX.PA")
    with patch("graph.workflow.collect", return_value=erreur), \
         patch("graph.workflow.generate_briefing_detaille") as redacteur:
        resultat = generer_briefing_complet("XXX.PA")

    redacteur.assert_not_called()
    assert resultat["modele_info"] == {}

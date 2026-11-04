from unittest.mock import patch

from agents.analyst import generate_briefing
from tests.conftest import faux_resultat_texte


def prompt_produit(mock_llm) -> str:
    """Le prompt réellement envoyé au modèle."""
    return mock_llm.call_args[0][0]


def test_generate_briefing_appelle_le_llm_et_retourne_le_texte():
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("Texte du briefing.")) as mock_llm:
        resultat = generate_briefing(ticker="MC.PA", price=457.5, change_pct=-1.99,
                                     adtv20=1_200_000.0, currency="EUR")

    assert resultat == "Texte du briefing."
    mock_llm.assert_called_once()
    assert "MC.PA" in prompt_produit(mock_llm)
    assert "AUCUNE recommandation" in prompt_produit(mock_llm)


def test_le_prompt_nomme_les_capitaux_moyens_avec_leur_devise_et_jamais_un_volume():
    """Carte #57 : `adtv20` est AVG(volume × clôture), des capitaux en devise, pas un nombre de titres.
    Le prompt disait « Volume moyen » : le modèle écrivait « 299 millions d'unités » (banc C7 du 03/10, HSBA.L).
    Le nom dit la mesure, et la devise est à côté du nombre ; le mot « volume » ne doit plus nommer ce chiffre."""
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="MC.PA", price=457.5, change_pct=-1.99,
                          adtv20=1_200_000.0, currency="EUR")

    prompt = prompt_produit(mock_llm)
    assert "Capitaux échangés en moyenne par séance sur 20 séances : 1,200,000 EUR" in prompt
    assert "Volume moyen sur 20 séances" not in prompt
    assert "ni comme un volume du jour, ni comme un nombre de titres" in prompt


def test_un_adtv20_absent_ne_produit_pas_un_zero_invente():
    """Un historique trop court rend `None` — écrire 0 serait un chiffre inventé."""
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="ALX.PA", price=12.0, change_pct=0.5,
                          adtv20=None, currency="EUR")

    assert "non disponible" in prompt_produit(mock_llm)


def test_une_cotation_perimee_est_dite_au_modele():
    """Défaut du 19/08 : la fraîcheur était calculée mais jamais transmise."""
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="ZC.PA", price=24.5, change_pct=0.0,
                          adtv20=None, currency="EUR",
                          fraicheur_jours=2000, cotation_perimee=True)

    prompt = prompt_produit(mock_llm)
    assert "2000 jours" in prompt
    assert "pas à jour" in prompt
    # Sprint 5, étape 8 (critère 1 du contrat, docs/sprint-4/CONTRAT.md § 3) : une cotation ancienne ne prouve pas une
    # radiation ; en production, OR.PA n'avait plus de cours parce que la collecte ne tournait pas. Le prompt ne pousse
    # plus le modèle vers cette conclusion : il lui interdit d'en tirer une.
    assert "radiée" not in prompt
    assert "N'en déduis rien" in prompt


# --- étape 4d : les articles entrent dans le prompt ----------------------------

def passages_exemple():
    return [{"texte": "LVMH publie des resultats en hausse",
             "source": "Boursorama", "lien": "https://exemple.test/lvmh",
             "publie_le": "2026-08-29", "tickers": ["MC.PA"],
             "rang_dense": 0, "rang_lexical": 0,
             "distance_dense": 0.31, "score_lexical": 8.2}]


def test_les_passages_entrent_dans_le_prompt_avec_leur_source_et_leur_date():
    """Un passage sans sa source est inutilisable : le briefing doit pouvoir citer."""
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="MC.PA", price=545.2, change_pct=-1.1,
                          adtv20=1_000_000.0, currency="EUR",
                          passages=passages_exemple())

    prompt = prompt_produit(mock_llm)
    assert "LVMH publie des resultats en hausse" in prompt
    assert "Boursorama" in prompt
    assert "2026-08-29" in prompt


def test_sans_article_le_prompt_interdit_den_inventer():
    """Le trou le plus dangereux : un modèle privé de sources en invente.

    Le silence ne suffit pas — il faut une consigne explicite.
    """
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="MC.PA", price=545.2, change_pct=-1.1,
                          adtv20=1_000_000.0, currency="EUR", passages=[])

    prompt = prompt_produit(mock_llm)
    assert "aucun article pertinent n'a été trouvé" in prompt
    assert "N'invente AUCUNE actualité" in prompt


def test_le_prompt_exige_la_citation_de_la_source():
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="MC.PA", price=545.2, change_pct=-1.1,
                          adtv20=1_000_000.0, currency="EUR",
                          passages=passages_exemple())

    assert "cite la source et la date" in prompt_produit(mock_llm)


def test_la_regle_amf_survit_a_larrivee_des_articles():
    """Non-régression : les articles ne doivent pas diluer l'interdit AMF."""
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="MC.PA", price=545.2, change_pct=-1.1,
                          adtv20=1_000_000.0, currency="EUR",
                          passages=passages_exemple())

    assert "AUCUNE recommandation" in prompt_produit(mock_llm)


def test_le_prompt_ne_pretend_jamais_que_les_articles_sont_recents():
    """Mesuré le 30/08 : le corpus rend des articles de 2023 pour MC.PA.

    Le RAG classe par pertinence, JAMAIS par date — rien ne garantit qu'un
    passage retrouvé soit récent. Écrire « Articles récents » au-dessus d'une
    dépêche de 2023 est une affirmation fausse produite par le code lui-même.
    La date de chaque passage est affichée : le modèle peut la lire, à condition
    qu'on ne lui ait pas dit le contraire dans l'en-tête.
    """
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="MC.PA", price=545.2, change_pct=-1.1,
                          adtv20=1_000_000.0, currency="EUR",
                          passages=passages_exemple())

    prompt = prompt_produit(mock_llm)
    assert "Articles récents" not in prompt
    assert "Articles retrouvés" in prompt
    assert "vérifie leur date" in prompt


# --- plan C7 (03/10/2026) : le prompt se construit sans appeler le modèle --------------------------

def test_construire_prompt_est_exactement_ce_que_le_redacteur_envoie():
    """Le banc C7 doit mesurer les fournisseurs sur le prompt réel, pas sur une copie qui dériverait."""
    from agents.analyst import construire_prompt
    arguments = dict(ticker="MC.PA", price=378.55, change_pct=-0.25, adtv20=1234.0, currency="EUR",
                     fraicheur_jours=1, cotation_perimee=False, passages=[])
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("ok")) as generer:
        generate_briefing(**arguments)
    assert generer.call_args.args[0] == construire_prompt(**arguments)
    assert generer.call_args.kwargs.get("max_tokens") == 500


# --- Les 13 indicateurs dans le prompt (décision d'Era, 03/10/2026) ---------------------------------
#
# Le scout calculait treize indicateurs et le rédacteur n'en recevait que quatre nombres (cours, variation
# du jour, capitaux moyens, devise). Les neuf autres vivaient sur l'écran 2 sans jamais atteindre le modèle.

INDICATEURS = {"perf_1s_pct": -4.61, "perf_1m_pct": -13.77, "perf_ytd_pct": -40.06, "perf_1a_pct": -28.52, "ma20": 404.865, "ma50": 438.61, "distance_plus_haut_1a_pct": -41.2, "volatilite_annualisee_pct": 22.5, "drawdown_max_1a_pct": -41.0, "rsi_14": 38.4}


def _prompt_avec(indicateurs):
    with patch("agents.analyst.generer_texte_detaille", return_value=faux_resultat_texte("x")) as mock_llm:
        generate_briefing(ticker="MC.PA", price=378.55, change_pct=-0.25, adtv20=259273190.0,
                          currency="EUR", fraicheur_jours=1, indicateurs=indicateurs)
    return prompt_produit(mock_llm)


def test_les_neuf_autres_indicateurs_entrent_dans_le_prompt_avec_leur_unite():
    prompt = _prompt_avec(INDICATEURS)
    assert "Indicateurs calculés sur l'historique" in prompt
    for attendu in ("1 semaine : -4,61 %", "1 mois : -13,77 %", "depuis le 1er janvier : -40,06 %", "1 an : -28,52 %",
                    "Moyenne mobile 20 séances : 404.87 EUR", "Moyenne mobile 50 séances : 438.61 EUR",
                    "plus haut sur 1 an : -41,20 %", "Volatilité annualisée : 22,50 %",
                    "Drawdown maximal sur 1 an : -41,00 %", "RSI 14 : 38.4"):
        assert attendu in prompt, attendu


def test_un_indicateur_absent_est_dit_non_disponible_jamais_zero():
    prompt = _prompt_avec({"perf_1m_pct": -13.77})
    assert "1 mois : -13,77 %" in prompt
    assert "RSI 14 : non disponible" in prompt and "Volatilité annualisée : non disponible" in prompt
    assert "RSI 14 : 0" not in prompt


def test_les_indicateurs_sont_des_faits_a_decrire_jamais_des_signaux():
    """La contrainte AMF, répétée là où le risque naît : un RSI ou une moyenne mobile se lisent
    comme des signaux dans la presse financière ; le prompt l'interdit en toutes lettres."""
    prompt = _prompt_avec(INDICATEURS)
    assert "Ces indicateurs sont des faits à décrire, jamais des signaux" in prompt
    assert "ne tire d'aucun d'eux une recommandation d'achat ou de vente" in prompt
    assert "RSI" in prompt


def test_sans_dictionnaire_d_indicateurs_le_prompt_reste_celui_d_avant():
    """Compatibilité : un appelant qui ne fournit pas les indicateurs (banc C7 sur un jeu figé ancien,
    tests existants) obtient le prompt d'avant, sans bloc vide ni « non disponible » à la chaîne."""
    prompt = _prompt_avec(None)
    assert "Indicateurs calculés" not in prompt
    assert "non disponible" not in prompt


# --- Refonte 001, tâche 2 (exigence R4) : le rédacteur dit qui a écrit -----------------------------

def test_generate_briefing_detaille_rend_qui_a_repondu():
    """Le rédacteur rend le texte et qui l'a écrit ; `generate_briefing` garde le texte seul, sur le même prompt."""
    from agents.analyst import construire_prompt, generate_briefing_detaille
    from src.llm import ResultatTexte
    attendu = ResultatTexte(texte="Texte.", fournisseur="anthropic", modele="claude-sonnet-5",
                            tentatives=[{"fournisseur": "foundry", "reussi": False},
                                        {"fournisseur": "anthropic", "reussi": True}])
    arguments = dict(ticker="MC.PA", price=378.55, change_pct=-0.25, adtv20=1234.0, currency="EUR",
                     fraicheur_jours=1, cotation_perimee=False, passages=[])
    with patch("agents.analyst.generer_texte_detaille", return_value=attendu) as generer:
        assert generate_briefing_detaille(**arguments) is attendu
        assert generate_briefing(**arguments) == "Texte."
    assert generer.call_count == 2
    assert generer.call_args.args[0] == construire_prompt(**arguments)
    assert generer.call_args.kwargs.get("max_tokens") == 500

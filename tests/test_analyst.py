from unittest.mock import patch

from agents.analyst import generate_briefing


def prompt_produit(mock_llm) -> str:
    """Le prompt réellement envoyé au modèle."""
    return mock_llm.call_args[0][0]


def test_generate_briefing_appelle_le_llm_et_retourne_le_texte():
    with patch("agents.analyst.generer_texte", return_value="Texte du briefing.") as mock_llm:
        resultat = generate_briefing(ticker="MC.PA", price=457.5, change_pct=-1.99,
                                     adtv20=1_200_000.0, currency="EUR")

    assert resultat == "Texte du briefing."
    mock_llm.assert_called_once()
    assert "MC.PA" in prompt_produit(mock_llm)
    assert "AUCUNE recommandation" in prompt_produit(mock_llm)


def test_le_prompt_nomme_le_volume_comme_une_moyenne_20_seances():
    """Le modèle ne doit jamais pouvoir écrire « volume du jour » sur une moyenne."""
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="MC.PA", price=457.5, change_pct=-1.99,
                          adtv20=1_200_000.0, currency="EUR")

    prompt = prompt_produit(mock_llm)
    assert "Volume moyen sur 20 séances" in prompt
    assert "JAMAIS le volume moyen 20 séances comme le volume du jour" in prompt


def test_un_adtv20_absent_ne_produit_pas_un_zero_invente():
    """Un historique trop court rend `None` — écrire 0 serait un chiffre inventé."""
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="ALX.PA", price=12.0, change_pct=0.5,
                          adtv20=None, currency="EUR")

    assert "non disponible" in prompt_produit(mock_llm)


def test_une_cotation_perimee_est_dite_au_modele():
    """Défaut du 19/08 : la fraîcheur était calculée mais jamais transmise."""
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="ZC.PA", price=24.5, change_pct=0.0,
                          adtv20=None, currency="EUR",
                          fraicheur_jours=2000, cotation_perimee=True)

    prompt = prompt_produit(mock_llm)
    assert "2000 jours" in prompt
    assert "probablement radiée" in prompt


# --- étape 4d : les articles entrent dans le prompt ----------------------------

def passages_exemple():
    return [{"texte": "LVMH publie des resultats en hausse",
             "source": "Boursorama", "lien": "https://exemple.test/lvmh",
             "publie_le": "2026-08-29", "tickers": ["MC.PA"],
             "rang_dense": 0, "rang_lexical": 0,
             "distance_dense": 0.31, "score_lexical": 8.2}]


def test_les_passages_entrent_dans_le_prompt_avec_leur_source_et_leur_date():
    """Un passage sans sa source est inutilisable : le briefing doit pouvoir citer."""
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
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
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="MC.PA", price=545.2, change_pct=-1.1,
                          adtv20=1_000_000.0, currency="EUR", passages=[])

    prompt = prompt_produit(mock_llm)
    assert "aucun article pertinent n'a été trouvé" in prompt
    assert "N'invente AUCUNE actualité" in prompt


def test_le_prompt_exige_la_citation_de_la_source():
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="MC.PA", price=545.2, change_pct=-1.1,
                          adtv20=1_000_000.0, currency="EUR",
                          passages=passages_exemple())

    assert "cite la source et la date" in prompt_produit(mock_llm)


def test_la_regle_amf_survit_a_larrivee_des_articles():
    """Non-régression : les articles ne doivent pas diluer l'interdit AMF."""
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
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
    with patch("agents.analyst.generer_texte", return_value="x") as mock_llm:
        generate_briefing(ticker="MC.PA", price=545.2, change_pct=-1.1,
                          adtv20=1_000_000.0, currency="EUR",
                          passages=passages_exemple())

    prompt = prompt_produit(mock_llm)
    assert "Articles récents" not in prompt
    assert "Articles retrouvés" in prompt
    assert "vérifie leur date" in prompt

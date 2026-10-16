"""Tâche A2 du sprint 3 : le contrat de sortie du modèle et le contrôle des citations (spec CA1.3, CA2.3).

Le modèle doit répondre dans un format imposé (statut, texte, citations), que l'application valide toujours elle-même.
Une citation n'est valide que si chaque numéro du texte est déclaré, que si chaque numéro déclaré est dans le texte, et
que si chacun renvoie à un extrait réellement envoyé. Ce contrôle porte sur la FORME : savoir si l'extrait soutient
vraiment la phrase relève de l'évaluation (tâche D1).
"""
import re

import pytest
from pydantic import ValidationError

from agents.question import SCHEMA_SORTIE, SortieModele, citations_valides, construire_prompt
from rag.recherche import Passage


def _passage(numero, texte, source="Le Monde", publie_le="2026-10-14T08:00:00"):
    """Un passage tel que la recherche le rend (rag/recherche.py)."""
    return Passage(article_id=2780 + numero, texte=texte, titre=texte, source=source,
                   lien=f"https://exemple.test/{numero}", publie_le=publie_le, tickers=[],
                   rang_dense=numero, rang_lexical=numero, distance_dense=0.3, score_lexical=1.0)


def test_le_schema_est_strict():
    assert SCHEMA_SORTIE["additionalProperties"] is False
    assert set(SCHEMA_SORTIE["required"]) == {"statut", "texte", "citations"}


@pytest.mark.parametrize("brut", [
    '{"statut": "oui"}',                                                              # champs manquants, statut inconnu
    '{"statut": "reponse", "texte": "T [1].", "citations": [1], "lien": "x"}',        # un champ en trop
    'pas du JSON',
])
def test_une_sortie_au_mauvais_format_est_rejetee(brut):
    with pytest.raises(ValidationError):
        SortieModele.model_validate_json(brut)


@pytest.mark.parametrize("texte, citations, nb_extraits, attendu", [
    ("Texte [1].", [1], 3, True),
    ("Texte [1] et encore [1].", [1], 3, True),       # le même numéro cité deux fois reste valide
    ("Texte [1] [2].", [1], 3, False),                # [2] est dans le texte mais pas déclaré
    ("Texte.", [], 3, False),                         # aucune citation
    ("", [1], 3, False),                              # texte vide
    ("Texte [4].", [4], 3, False),                    # seulement 3 extraits envoyés
    ("Texte [0].", [0], 3, False),                    # les extraits commencent à 1
])
def test_citations_valides(texte, citations, nb_extraits, attendu):
    sortie = SortieModele(statut="reponse", texte=texte, citations=citations)
    assert citations_valides(sortie, nb_extraits) is attendu


def test_le_prompt_numerote_les_extraits_et_isole_la_question():
    question = "Combien de postes Netflix va-t-il supprimer ?"
    prompt = construire_prompt(question, [_passage(1, "Netflix va supprimer 1 000 postes"),
                                          _passage(2, "La croissance francaise limitee en 2027")])
    assert "[1]" in prompt and "[2]" in prompt
    assert prompt.count(question) == 1
    assert re.search(r"<question>\s*" + re.escape(question) + r"\s*</question>", prompt)
    assert "abstention" in prompt

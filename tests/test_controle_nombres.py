"""Le contrôle des nombres avant de servir une réponse (sprint 4, suite du rejeu en production du 20/10/2026).

Q4 (« Combien de postes Netflix va-t-il supprimer ? ») a été servie en production avec « 1 0 postes », pour un passage
qui dit « 1 000 postes ». La cause exacte n'est pas établie : le passage stocké est le même qu'en local (vérifié), et
22 essais locaux sur 22 étaient justes ; le chiffre s'abîme dans la réponse du modèle. Plutôt que de deviner, la réponse
est contrôlée avant d'être servie : chaque nombre qu'elle contient doit figurer dans un des articles cités, sinon elle
est refusée poliment (motif NOMBRE_NON_SOURCE). Les espaces Unicode sont toutes ramenées à une espace simple, et les
numéros de citation « [1] » ne comptent pas.
"""
import importlib
import json
import logging

import pytest

from agents import question
from rag.recherche import Passage, Resultat

INSECABLE, FINE, FINE_ORDINAIRE = chr(0xA0), chr(0x202F), chr(0x2009)
SOURCE_NETFLIX = f"Netflix va supprimer 1{INSECABLE}000{INSECABLE}postes dans le monde, soit 6{INSECABLE}% de ses effectifs"


def _nombres():
    """Importé dans chaque test : tant que le module n'existe pas, chacun échoue pour cette raison."""
    return importlib.import_module("guardrails.nombres")


# --- la fonction seule -----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("abime", ["1 00", "1 0"])
def test_un_chiffre_abime_est_absent_des_sources(abime):
    # Les deux formes observées : « 1 00 » (mesure locale de 18h33), « 1 0 » (production, 21h53).
    texte = f"Netflix va supprimer {abime} postes dans le monde, soit 6 % de ses effectifs. [1]"
    assert _nombres().nombres_absents(texte, [SOURCE_NETFLIX]) == [abime]


@pytest.mark.parametrize("espace", [" ", INSECABLE, FINE, FINE_ORDINAIRE], ids=["ordinaire", "insecable", "fine",
                                                                              "fine_ordinaire"])
def test_les_chiffres_justes_passent_quelle_que_soit_l_espace(espace):
    texte = f"Netflix va supprimer 1{espace}000 postes, soit 6{espace}% de ses effectifs. [1]"
    assert _nombres().nombres_absents(texte, [SOURCE_NETFLIX]) == []


def test_les_numeros_de_citation_ne_comptent_pas():
    assert _nombres().nombres_absents("Un fait établi [1][2].", ["Un fait établi sans aucun chiffre."]) == []


def test_un_nombre_decimal_ou_une_annee_se_cherchent_entiers():
    sources = ["La croissance ne dépasserait pas 0,5 % en 2027, selon l'institut."]
    assert _nombres().nombres_absents("La croissance ne dépasserait pas 0,5 % en 2027. [1]", sources) == []
    assert _nombres().nombres_absents("La croissance atteindrait 0,55 % en 2027. [1]", sources) == ["0,55"]


# --- le parcours des questions ---------------------------------------------------------------------------------------

def _passage(texte):
    return Passage(article_id=2788, texte=texte, titre=texte, source="Le Monde", lien="https://exemple.test/2788",
                   publie_le="2026-10-14T18:04:00+02:00", tickers=[], rang_dense=1, rang_lexical=1,
                   distance_dense=0.3, score_lexical=1.0)


def _repondre(monkeypatch, texte_du_modele):
    monkeypatch.setattr(question, "rechercher", lambda *a, **k: Resultat(True, "OK", [_passage(SOURCE_NETFLIX)], 1))
    sortie = {"statut": "reponse", "texte": texte_du_modele, "citations": [1]}
    monkeypatch.setattr(question, "generer_json", lambda *a, **k: json.dumps(sortie, ensure_ascii=False))
    return question.repondre("Combien de postes Netflix va-t-il supprimer ?")


def test_une_reponse_au_chiffre_absent_des_sources_est_refusee(monkeypatch, caplog):
    with caplog.at_level(logging.WARNING):
        reponse = _repondre(monkeypatch, "Netflix va supprimer 1 0 postes dans le monde, soit 6 % de ses effectifs. [1]")
    assert (reponse.statut, reponse.motif) == ("refus", "NOMBRE_NON_SOURCE")
    assert "1 0 postes" not in reponse.texte and reponse.references == []
    assert "controle des nombres" in caplog.text and "postes" not in caplog.text


def test_une_reponse_aux_chiffres_justes_est_servie(monkeypatch):
    # Le témoin : sans lui, un contrôle qui refuserait tout passerait le test précédent.
    reponse = _repondre(monkeypatch, "Netflix va supprimer 1 000 postes dans le monde, soit 6 % de ses effectifs. [1]")
    assert (reponse.statut, reponse.motif) == ("reponse", "OK")


def test_le_prompt_ramene_toutes_les_espaces_unicode_a_une_espace_simple():
    # En défense : la correction du 20/10 ne traitait que l'insécable ordinaire et l'insécable fine.
    prompt = question.construire_prompt("Combien ?", [_passage(f"Netflix va supprimer 1{FINE_ORDINAIRE}000 postes")])
    assert FINE_ORDINAIRE not in prompt and "1 000 postes" in prompt

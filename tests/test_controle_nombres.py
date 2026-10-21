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


# --- revue Codex de la PR #114 (21/10/2026) : le signe, et ce que le modèle a reçu ------------------------------------

MOINS = chr(0x2212)   # le vrai signe moins, que certains textes emploient à la place du trait d'union


def test_un_signe_inverse_est_signale():
    # P1 : « -5 % » face à « +5 % » passait. En finance, une hausse devenait une baisse sous une source juste.
    assert _nombres().nombres_absents("La variation est de -5 %. [1]", ["La variation est de +5 % sur la séance."]) == ["-5"]


@pytest.mark.parametrize("texte, source", [
    ("Le titre progresse de +3,00 %. [1]", "Le titre progresse de +3,00 % sur la semaine."),
    ("Le titre recule de 5 %. [1]", "Le titre recule de -5 % sur la semaine."),
    ("Sur la période 2026-2027. [1]", "Les prévisions portent sur la période 2026-2027."),
    (f"Le titre recule de {MOINS}3,00 %. [1]", "Le titre recule de -3,00 % sur la semaine."),
], ids=["meme_signe", "sans_signe_dans_la_reponse", "trait_d_union_entre_deux_nombres", "vrai_signe_moins"])
def test_les_signes_justes_passent(texte, source):
    # Les témoins du test précédent : un signe juste, une réponse sans signe, un trait d'union qui n'est pas un signe.
    assert _nombres().nombres_absents(texte, [source]) == []


def test_une_date_de_publication_recue_par_le_modele_est_acceptee(monkeypatch):
    # P2 : le modèle reçoit la source et la date de chaque extrait (« [1] (Le Monde, 2026-10-14) ... ») ; une date de
    # publication juste était refusée, parce que seul le texte de l'article servait de source.
    reponse = _repondre(monkeypatch, "L'article est publié le 14 octobre 2026. [1]")
    assert (reponse.statut, reponse.motif) == ("reponse", "OK")


def test_une_date_de_publication_fausse_est_refusee(monkeypatch):
    # Le témoin : la date ajoutée aux sources ne doit pas faire passer n'importe quelle date.
    reponse = _repondre(monkeypatch, "L'article est publié le 15 octobre 2026. [1]")
    assert (reponse.statut, reponse.motif) == ("refus", "NOMBRE_NON_SOURCE")


# --- seconde revue Codex de la PR #114 (21/10/2026) : le point décimal ------------------------------------------------

@pytest.mark.parametrize("texte, source, absent", [
    ("Le taux est 2.5 %. [1]", "Le taux est 5.2 %.", "2.5"),
    ("Le taux est 2.7 %. [1]", "Le taux est 2.5 % et le délai de 7 jours.", "2.7"),
], ids=["parties_inversees", "decimale_changee"])
def test_un_nombre_a_point_decimal_se_cherche_entier(texte, source, absent):
    # P2 : « 2.5 » était coupé en « 2 » et « 5 » ; un taux inversé ou changé passait dès que les morceaux figuraient
    # ailleurs dans l'article. Le point entre deux chiffres est une décimale, comme la virgule.
    assert _nombres().nombres_absents(texte, [source]) == [absent]


@pytest.mark.parametrize("texte, source", [
    ("Le taux est 2.5 %. [1]", "Le taux est 2.5 % sur un an."),
    ("La croissance est prévue en 2027. [1]", "La croissance en 2027 sera faible."),
], ids=["meme_decimale", "point_de_fin_de_phrase"])
def test_un_point_decimal_juste_ou_un_point_final_passent(texte, source):
    # Les témoins : une décimale juste passe ; un point de fin de phrase n'est pas une décimale.
    assert _nombres().nombres_absents(texte, [source]) == []

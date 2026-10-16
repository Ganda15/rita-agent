"""Tâche A4 du sprint 3 : répondre à une question, de bout en bout dans le code (spec US1, US2).

Un refus (« je ne peux pas répondre sur le fond ») et une erreur technique (« le service n'a pas pu fonctionner ») sont
deux choses différentes : le premier est une issue normale, la seconde une panne. Le modèle n'est jamais appelé quand
la recherche ne retient aucun passage. Les références montrées viennent des données stockées, jamais du modèle.

La recherche et le modèle sont remplacés par des doublures : aucun réseau. Un dernier test passe par un vrai index.
"""
import pytest

from agents import question
from rag.recherche import Resultat
from src.llm import FournisseurIndisponible, ReponseTronquee
from tests.test_identite_index import _indexer, _ligne
from tests.test_question_contrat import _passage

PASSAGES = [_passage(1, "Netflix va supprimer 1 000 postes"),
            _passage(2, "Lufthansa designee pour reprendre TAP"),
            _passage(3, "La croissance francaise limitee en 2027")]


def _recherche(monkeypatch, resultat):
    monkeypatch.setattr(question, "rechercher", lambda *args, **kwargs: resultat)


def _modele(monkeypatch, brut=None, erreur=None):
    """Le modèle rend `brut` (un texte JSON), ou lève `erreur`."""
    def faux(*args, **kwargs):
        if erreur is not None:
            raise erreur
        return brut
    monkeypatch.setattr(question, "generer_json", faux)


def _modele_interdit(monkeypatch):
    def interdit(*args, **kwargs):
        raise AssertionError("le modèle ne doit pas être appelé")
    monkeypatch.setattr(question, "generer_json", interdit)


def _trouve(passages=PASSAGES):
    return Resultat(True, "OK", passages, len(passages))


def test_hors_corpus_refuse_sans_appeler_le_modele(monkeypatch):
    _recherche(monkeypatch, Resultat(False, "OUT_OF_CORPUS", [], 0))
    _modele_interdit(monkeypatch)
    r = question.repondre("Quelle est la recette de la tarte Tatin ?")
    assert (r.statut, r.motif, r.references) == ("refus", "OUT_OF_CORPUS", [])
    assert r.texte


def test_intention_interdite_refusee_sans_modele(monkeypatch):
    _recherche(monkeypatch, Resultat(False, "INTENTION_INTERDITE", [], 0))
    _modele_interdit(monkeypatch)
    r = question.repondre("Faut-il acheter des actions Sanofi maintenant ?")
    assert (r.statut, r.motif, r.references) == ("refus", "INTENTION_INTERDITE", [])


def test_abstention_donne_un_refus_sans_reference(monkeypatch):
    _recherche(monkeypatch, _trouve())
    _modele(monkeypatch, '{"statut": "abstention", "texte": "Les extraits ne le disent pas.", "citations": []}')
    r = question.repondre("Que prevoit le plan BEYOND ?")
    assert (r.statut, r.motif, r.references) == ("refus", "ABSTENTION", [])


def test_citations_invalides_donnent_un_refus(monkeypatch):
    _recherche(monkeypatch, _trouve())
    _modele(monkeypatch, '{"statut": "reponse", "texte": "Une affirmation [5].", "citations": [5]}')
    r = question.repondre("Combien de postes Netflix supprime-t-il ?")
    assert (r.statut, r.motif, r.references) == ("refus", "CITATIONS_INVALIDES", [])


def test_format_invalide_est_une_erreur_pas_un_refus(monkeypatch):
    _recherche(monkeypatch, _trouve())
    _modele(monkeypatch, "pas du JSON")
    r = question.repondre("Combien de postes Netflix supprime-t-il ?")
    assert (r.statut, r.motif, r.references) == ("erreur", "FORMAT_INVALIDE", [])


@pytest.mark.parametrize("panne, motif", [
    (FournisseurIndisponible("fournisseur indisponible (ConnectError)"), "FOURNISSEUR_INDISPONIBLE"),
    (ReponseTronquee("reponse tronquee"), "REPONSE_TRONQUEE"),
])
def test_une_panne_du_modele_est_une_erreur(monkeypatch, panne, motif):
    _recherche(monkeypatch, _trouve())
    _modele(monkeypatch, erreur=panne)
    r = question.repondre("Combien de postes Netflix supprime-t-il ?")
    assert (r.statut, r.motif, r.references) == ("erreur", motif, [])


def test_sortie_non_conforme_amf_est_refusee(monkeypatch):
    _recherche(monkeypatch, _trouve())
    _modele(monkeypatch, '{"statut": "reponse", "texte": "Achetez des actions Netflix [1].", "citations": [1]}')
    r = question.repondre("Que se passe-t-il chez Netflix ?")
    assert (r.statut, r.motif, r.references) == ("refus", "SORTIE_NON_CONFORME", [])
    assert "Achetez" not in r.texte


def test_les_references_viennent_des_donnees_stockees(monkeypatch):
    _recherche(monkeypatch, _trouve())
    _modele(monkeypatch, '{"statut": "reponse", "texte": "Netflix supprime 1 000 postes [1], '
                         'voir https://faux.example/lien-invente.", "citations": [1]}')
    r = question.repondre("Combien de postes Netflix supprime-t-il ?")
    assert (r.statut, r.motif) == ("reponse", "OK")
    reference = r.references[0]
    passage = PASSAGES[0]
    assert reference.n == 1
    assert reference.table == "article"
    assert reference.id == passage.article_id
    assert reference.titre == passage.titre
    assert reference.source == passage.source
    assert reference.date == passage.publie_le
    assert reference.lien == passage.lien
    assert reference.extrait == passage.texte


def test_seuls_les_extraits_cites_deviennent_des_references(monkeypatch):
    _recherche(monkeypatch, _trouve())
    _modele(monkeypatch, '{"statut": "reponse", "texte": "Lufthansa reprend TAP [2].", "citations": [2]}')
    r = question.repondre("Qui reprend TAP ?")
    assert [reference.n for reference in r.references] == [2]
    assert r.references[0].id == PASSAGES[1].article_id


def test_une_question_de_mots_vides_est_refusee_proprement(monkeypatch, tmp_path):
    # Point de vigilance du plan : une question sans aucun mot porteur de sens, sur un vrai index.
    _indexer(monkeypatch, tmp_path, [_ligne(1, "Netflix va supprimer 1 000 postes", "Soit 6 % de ses effectifs"),
                                     _ligne(2, "Lufthansa designee pour reprendre TAP", "Face a Air France-KLM")])
    _modele_interdit(monkeypatch)
    r = question.repondre("le la les ?", chemin_index=tmp_path)
    assert (r.statut, r.motif, r.references) == ("refus", "OUT_OF_CORPUS", [])

"""Tâche A5 du sprint 3 : la route `POST /question` et la fiche `GET /donnees/articles/{article_id}`.

Spec CA1.1 (protégée par la clé), CA1.5 (la fiche de la source), CA1.8 (la fiche montre le passage réellement
transmis au modèle), CA2.4 (une panne est une erreur 503, distincte d'un refus), CA4.3 (aucun texte de question ni de
réponse dans les journaux ni dans les traces, y compris quand une erreur survient, même imprévue).
"""
import logging
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from agents import question
from api.main import app
from rag import indexation
from rag.indexation import editeur, texte_indexable
from rag.recherche import Resultat
from src import traces
from src.llm import FournisseurIndisponible
from tests.conftest import CLE_DE_TEST
from tests.test_identite_index import _indexer, _ligne
from tests.test_question_contrat import _passage
from tests.test_traces_question import _EnregistreurAvecIdentifiant

CLE = {"X-API-Key": CLE_DE_TEST}
MARQUEUR_QUESTION = "MARQUEUR-QUESTION-7f3a"
MARQUEUR_REPONSE = "MARQUEUR-REPONSE-9b2c"
PASSAGE = _passage(8, "Netflix va supprimer 1 000 postes")      # article 2788
LIGNE_2788 = {"id": 2788, "source": "Le Monde", "titre": "Netflix va supprimer 1 000 postes",
              "lien": "https://exemple.test/8", "publie_le": datetime(2026, 10, 14, 8, 0),
              "resume": "", "collecte_le": datetime(2026, 10, 14, 19, 0)}


@pytest.fixture
def client():
    return TestClient(app)


def _base(monkeypatch, lignes):
    """La fiche lit la base par `database._executer` : remplacé par un jeu figé ; la requête est gardée."""
    requetes = []

    class _Extraction:
        def __init__(self, lignes):
            self.lignes, self.nb = lignes, len(lignes)

    def faux(sql, nom, dsn=None, **params):
        requetes.append((sql, params))
        return _Extraction(lignes)

    monkeypatch.setattr("api.donnees.database._executer", faux)
    return requetes


def _parcours(monkeypatch, brut=None, erreur=None, passages=(PASSAGE,)):
    """Le vrai parcours, avec la recherche et le modèle remplacés."""
    monkeypatch.setattr(question, "rechercher", lambda *a, **k: Resultat(True, "OK", list(passages), len(passages)))

    def modele(*args, **kwargs):
        if erreur is not None:
            raise erreur
        return brut

    monkeypatch.setattr(question, "generer_json", modele)


def _traces(monkeypatch):
    client_traces = _EnregistreurAvecIdentifiant()
    monkeypatch.setattr(traces, "client_traces", lambda: client_traces)
    return client_traces


# --- la route /question --------------------------------------------------------------------------------------------

def test_question_sans_cle_403(client):
    assert client.post("/question", json={"question": "Qui reprend TAP ?"}).status_code == 403


@pytest.mark.parametrize("longueur, attendu", [(2, 422), (501, 422), (500, 200)])
def test_longueur_de_la_question(client, monkeypatch, longueur, attendu):
    monkeypatch.setattr(question, "rechercher", lambda *a, **k: Resultat(False, "OUT_OF_CORPUS", [], 0))
    assert client.post("/question", json={"question": "x" * longueur}, headers=CLE).status_code == attendu


def test_une_erreur_technique_rend_503(client, monkeypatch):
    _parcours(monkeypatch, erreur=FournisseurIndisponible("fournisseur indisponible (ConnectError)"))
    reponse = client.post("/question", json={"question": "Combien de postes Netflix supprime-t-il ?"}, headers=CLE)
    assert reponse.status_code == 503
    assert reponse.json()["statut"] == "erreur"
    assert reponse.json()["motif"] == "FOURNISSEUR_INDISPONIBLE"


def test_un_refus_rend_200_avec_son_motif(client, monkeypatch):
    monkeypatch.setattr(question, "rechercher", lambda *a, **k: Resultat(False, "OUT_OF_CORPUS", [], 0))
    reponse = client.post("/question", json={"question": "Quelle est la recette de la tarte Tatin ?"}, headers=CLE)
    assert reponse.status_code == 200
    assert (reponse.json()["statut"], reponse.json()["motif"], reponse.json()["references"]) == \
        ("refus", "OUT_OF_CORPUS", [])


def test_une_reponse_rend_les_references_et_l_identite_de_l_index(client, monkeypatch):
    identite = {"empreinte": "0" * 64, "identifiant": "essai", "nb_articles": 1}
    monkeypatch.setattr(indexation, "lire_identite", lambda chemin=None: identite)
    _parcours(monkeypatch, '{"statut": "reponse", "texte": "Netflix supprime 1 000 postes [1].", "citations": [1]}')
    reponse = client.post("/question", json={"question": "Combien de postes Netflix supprime-t-il ?"}, headers=CLE)
    assert reponse.status_code == 200
    corps = reponse.json()
    assert (corps["statut"], corps["motif"]) == ("reponse", "OK")
    assert corps["references"][0]["id"] == 2788
    assert corps["references"][0]["table"] == "article"
    assert corps["references"][0]["extrait"] == PASSAGE.texte
    assert corps["index"] == identite


@pytest.mark.parametrize("cas, statut_http", [("reponse", 200), ("panne", 503), ("json_invalide", 503)])
def test_aucun_texte_dans_les_journaux_ni_les_traces(client, monkeypatch, caplog, cas, statut_http):
    journal_traces = _traces(monkeypatch)
    if cas == "reponse":
        _parcours(monkeypatch, '{"statut": "reponse", "texte": "' + MARQUEUR_REPONSE + ' [1].", "citations": [1]}')
    elif cas == "panne":
        _parcours(monkeypatch, erreur=FournisseurIndisponible("fournisseur indisponible (ConnectError)"))
    else:
        _parcours(monkeypatch, '{"statut": "' + MARQUEUR_REPONSE + '"')
    with caplog.at_level(logging.DEBUG):
        reponse = client.post("/question", json={"question": f"Que dit {MARQUEUR_QUESTION} ?"}, headers=CLE)
    # Le parcours a bien tourné et a bien été tracé : sinon, l'absence de fuite ne prouverait rien.
    assert reponse.status_code == statut_http
    assert any(genre == "ouvre" and options.get("name") == "question" for genre, options in journal_traces.journal)
    for marqueur in (MARQUEUR_QUESTION, MARQUEUR_REPONSE):
        assert marqueur not in caplog.text
        assert marqueur not in repr(journal_traces.journal)


def test_une_exception_imprevue_contenant_la_question_ne_fuit_pas(client, monkeypatch, caplog):
    journal_traces = _traces(monkeypatch)

    def recherche_en_panne(texte, *args, **kwargs):
        raise RuntimeError(f"echec de la recherche sur {texte}")

    monkeypatch.setattr(question, "rechercher", recherche_en_panne)
    with caplog.at_level(logging.DEBUG):
        reponse = client.post("/question", json={"question": f"Que dit {MARQUEUR_QUESTION} ?"}, headers=CLE)
    assert reponse.status_code == 500
    assert reponse.json() == {"statut": "erreur", "motif": "ERREUR_INTERNE"}
    assert MARQUEUR_QUESTION not in caplog.text
    assert MARQUEUR_QUESTION not in repr(journal_traces.journal)


# --- la fiche d'une source -----------------------------------------------------------------------------------------

def test_fiche_d_un_article_existant(client, monkeypatch):
    requetes = _base(monkeypatch, [LIGNE_2788])
    reponse = client.get("/donnees/articles/2788", headers=CLE)
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["table"] == "article"
    assert corps["id"] == 2788
    assert corps["extrait"] == texte_indexable(LIGNE_2788["titre"], LIGNE_2788["resume"])
    sql, params = requetes[0]
    assert "bloque_injection = FALSE" in sql
    assert params == {"id": 2788}


def test_fiche_d_un_article_bloque_ou_inconnu_404(client, monkeypatch):
    requetes = _base(monkeypatch, [])
    assert client.get("/donnees/articles/999999", headers=CLE).status_code == 404
    # La base a bien été interrogée, avec le filtre des articles bloqués : ce 404 vient de la route, pas d'une
    # adresse inconnue.
    assert requetes and "bloque_injection = FALSE" in requetes[0][0]


def test_la_fiche_ne_rend_jamais_un_lien_qui_n_est_pas_http(client, monkeypatch):
    # Même règle que pour les références (revue de sécurité du commit A4, 16/10/2026) : la fiche est le second endroit
    # où l'écran peut rendre un lien venu d'un flux RSS.
    _base(monkeypatch, [{**LIGNE_2788, "lien": "javascript:alert(1)"}])
    assert client.get("/donnees/articles/2788", headers=CLE).json()["lien"] == ""


def test_fiche_avec_un_identifiant_non_numerique_422(client, monkeypatch):
    _base(monkeypatch, [LIGNE_2788])
    assert client.get("/donnees/articles/abc", headers=CLE).status_code == 422


def test_la_fiche_correspond_a_la_reference(client, monkeypatch):
    _parcours(monkeypatch, '{"statut": "reponse", "texte": "Netflix supprime 1 000 postes [1].", "citations": [1]}')
    reference = client.post("/question", json={"question": "Combien de postes Netflix supprime-t-il ?"},
                            headers=CLE).json()["references"][0]
    _base(monkeypatch, [LIGNE_2788])
    fiche = client.get(f"/donnees/articles/{reference['id']}", headers=CLE).json()
    assert reference["titre"] == fiche["titre"]
    assert reference["lien"] == fiche["lien"]
    assert reference["date"][:10] == fiche["publie_le"][:10]


def test_la_fiche_cite_l_editeur_et_garde_le_flux(client, monkeypatch):
    # Revue automatique de la PR #100 (P2) : la référence nomme l'éditeur (`editeur`, appliqué à l'indexation), la
    # fiche rendait l'identifiant brut du flux. Les deux doivent nommer la même source ; le flux reste, pour le
    # diagnostic, sous son propre nom.
    _base(monkeypatch, [{**LIGNE_2788, "source": "lemonde_eco"}])
    fiche = client.get("/donnees/articles/2788", headers=CLE).json()
    assert fiche["source"] == editeur("lemonde_eco", LIGNE_2788["titre"]) == "Le Monde Éco"
    assert fiche["flux"] == "lemonde_eco"


def test_la_source_de_la_fiche_est_celle_de_la_reference(client, monkeypatch, tmp_path):
    # Même vérification de bout en bout : un vrai index, une vraie référence, puis la fiche du même article. Un
    # article d'entreprise vient du flux `ent_<société>` et cite l'éditeur écrit à la fin de son titre.
    lignes = [_ligne(2788, "Netflix va supprimer 1 000 postes - Boursorama", "Soit 6 % de ses effectifs",
                     source="ent_netflix")]
    monkeypatch.setattr(question, "generer_json", lambda *a, **k:
                        '{"statut": "reponse", "texte": "Netflix supprime 1 000 postes [1].", "citations": [1]}')
    _indexer(monkeypatch, tmp_path, lignes)
    reference = question.repondre("Combien de postes Netflix va supprimer ?", chemin_index=tmp_path).references[0]
    _base(monkeypatch, [{**lignes[0], "collecte_le": datetime(2026, 10, 14, 19, 0)}])
    fiche = client.get("/donnees/articles/2788", headers=CLE).json()
    assert reference.source == fiche["source"] == "Boursorama"
    assert fiche["flux"] == "ent_netflix"


def test_l_extrait_presente_est_celui_transmis_au_modele(client, monkeypatch, tmp_path):
    lignes = [_ligne(2788, "Netflix va supprimer 1 000 postes", "Soit 6 % de ses effectifs")]
    prompts = []

    def modele(prompt, *args, **kwargs):
        prompts.append(prompt)
        return '{"statut": "reponse", "texte": "Netflix supprime 1 000 postes [1].", "citations": [1]}'

    monkeypatch.setattr(question, "generer_json", modele)
    _indexer(monkeypatch, tmp_path, lignes)
    avant = question.repondre("Combien de postes Netflix va supprimer ?", chemin_index=tmp_path).references[0]
    assert avant.extrait in prompts[-1]
    _base(monkeypatch, [{**lignes[0], "collecte_le": datetime(2026, 10, 14, 19, 0)}])
    assert client.get("/donnees/articles/2788", headers=CLE).json()["extrait"] == avant.extrait

    # Une nouvelle indexation ajoute des articles : l'extrait de cet article ne change pas (lignes jamais modifiées).
    _indexer(monkeypatch, tmp_path, lignes + [_ligne(2799, "Sanofi evite une amende", "Bruxelles accepte")])
    apres = question.repondre("Combien de postes Netflix va supprimer ?", chemin_index=tmp_path).references[0]
    assert apres.extrait == avant.extrait

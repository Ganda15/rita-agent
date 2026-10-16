"""Tâche B2 du sprint 3 : le jeu de questions de démonstration et son rejeu (spec CA6.1 à CA6.5, CA3.6).

Le jeu (`rag/questions_demo.json`) est la version 2 du § 5 de la spec, révisée par Era le 16/10/2026 après mesure. Le
rejeu (`python -m rag.controle_questions`) le repasse sur un index, **sans appel au modèle** : il ne contrôle que la
recherche. Un refus attendu doit rester un refus ; une question couverte doit rendre au moins une source validée. Le
rapport porte l'identité de l'index sous la clé `index`, comme `/health` : c'est le contrat lu par le script du
serveur avant toute mise en service (tâche B3).

Le test du corpus figé construit un index jetable avec les vrais articles de la copie du 16/10/2026
(`tests/donnees/corpus-fige-2026-10-16.json`). Si une question couverte y échoue, on s'arrête et on le dit à Era :
pas de reformulation en silence (CA6.5).
"""
import json
from datetime import datetime
from pathlib import Path

import pytest

from rag import controle_questions, indexation
from rag.recherche import Passage, Resultat

DONNEES = Path(__file__).parent / "donnees" / "corpus-fige-2026-10-16.json"
IDENTITE = {"nb_articles": 18, "id_max": 2803, "empreinte": "e" * 64, "identifiant": "id-essai"}


def _passage(article_id):
    return Passage(article_id=article_id, texte=f"texte {article_id}", titre=f"titre {article_id}", source="essai",
                   lien=f"https://exemple.test/{article_id}", publie_le="2026-10-14T08:00:00", tickers=[],
                   rang_dense=1, rang_lexical=1, distance_dense=0.3, score_lexical=1.0)


def _recherche(monkeypatch, par_question):
    """La recherche est remplacée : `par_question` donne, pour chaque texte de question, le résultat à rendre."""
    def faux(question, *args, **kwargs):
        return par_question[question]
    monkeypatch.setattr(controle_questions, "rechercher", faux)


def _trouve(*ids):
    return Resultat(True, "OK", [_passage(i) for i in ids], len(ids))


def _question(identifiant, attendu, sources=(), motif=None):
    question = {"id": identifiant, "question": f"Question {identifiant} ?", "attendu": attendu,
                "sources_attendues": list(sources), "sources_validees": list(sources),
                "faits_attendus": ["un fait"] if attendu != "refus" else []}
    if motif:
        question["motif_attendu"] = motif
    return question


def _jeu(*questions):
    return {"version": 2, "choisi_le": "2026-10-15", "revise_le": "2026-10-16", "corpus": {}, "questions": list(questions)}


# --- le jeu lui-même ----------------------------------------------------------------------------------------------

def test_le_jeu_respecte_la_spec():
    # CA6.1 et CA6.2 : 5 à 10 questions, au moins 3 couvertes, au moins 2 hors corpus ; chaque question couverte a ses
    # sources et ses faits ; une source validée par Era englobe toujours les sources attendues.
    jeu = controle_questions.charger_jeu()
    questions = jeu["questions"]
    assert 5 <= len(questions) <= 10
    assert len({q["id"] for q in questions}) == len(questions)
    assert sum(q["attendu"] == "reponse" for q in questions) >= 3
    assert sum(q["attendu"] == "refus" and q["motif_attendu"] == "OUT_OF_CORPUS" for q in questions) >= 2
    for q in questions:
        if q["attendu"] != "refus":
            assert q["sources_attendues"] and q["faits_attendus"], q["id"]
            assert set(q["sources_attendues"]) <= set(q["sources_validees"]), q["id"]


def test_le_jeu_est_la_version_2_de_la_spec():
    # CA6.4 et CA6.5 : le jeu est lié à une version identifiée du corpus et de l'index ; la reformulation de Q2 garde
    # la question d'origine et sa raison ; les sources de Q3 validées par Era le 16/10 y sont.
    jeu = controle_questions.charger_jeu()
    assert jeu["version"] == 2 and jeu["revise_le"] == "2026-10-16"
    assert (jeu["corpus"]["nb_articles"], jeu["corpus"]["id_max"]) == (2052, 2809)
    assert jeu["corpus"]["index_identifiant"] == "18c122a9972c4a389e643d67762b4eb1"
    par_id = {q["id"]: q for q in jeu["questions"]}
    assert par_id["Q2"]["question"] == "Qui a été désigné pour la reprise de TAP face à Air France-KLM ?"
    assert par_id["Q2"]["formulation_d_origine"] == "Qui reprend la compagnie aérienne TAP, et face à quel concurrent ?"
    assert par_id["Q2"]["raison"]
    assert par_id["Q3"]["attendu"] == "reponse_ou_abstention"
    assert {2795, 2370, 2376, 2429} <= set(par_id["Q3"]["sources_validees"])
    assert par_id["Q8"]["motif_attendu"] == "INTENTION_INTERDITE"


@pytest.mark.parametrize("defaut", ["attendu_inconnu", "reponse_sans_source", "source_attendue_non_validee",
                                    "refus_sans_motif", "identifiant_en_double"])
def test_un_jeu_mal_forme_est_refuse(tmp_path, defaut):
    questions = [_question("Q1", "reponse", [1]), _question("Q2", "refus", motif="OUT_OF_CORPUS")]
    if defaut == "attendu_inconnu":
        questions[0]["attendu"] = "peut-etre"
    elif defaut == "reponse_sans_source":
        questions[0]["sources_attendues"] = questions[0]["sources_validees"] = []
    elif defaut == "source_attendue_non_validee":
        questions[0]["sources_validees"] = [2]
    elif defaut == "refus_sans_motif":
        del questions[1]["motif_attendu"]
    else:
        questions[1]["id"] = "Q1"
    chemin = tmp_path / "jeu.json"
    chemin.write_text(json.dumps(_jeu(*questions)), encoding="utf-8")
    with pytest.raises(ValueError):
        controle_questions.charger_jeu(chemin)


# --- le rejeu sur un vrai index, construit avec les articles réels -----------------------------------------------

def test_le_rejeu_passe_sur_un_corpus_fige(monkeypatch, tmp_path):
    articles = json.loads(DONNEES.read_text(encoding="utf-8"))["articles"]
    lignes = [{**a, "lien": f"https://exemple.test/{a['id']}", "publie_le": datetime.fromisoformat(a["publie_le"])}
              for a in articles]

    def faux(sql, nom, dsn=None, **kw):
        class Extraction:
            pass
        e = Extraction()
        e.lignes = lignes if "bloque_injection" in sql else []
        return e

    monkeypatch.setattr(indexation.database, "_executer", faux)
    indexation.indexer(chemin=tmp_path)
    ecarts = controle_questions.rejouer(controle_questions.charger_jeu(), chemin_index=tmp_path)
    assert [e for e in ecarts if e.bloquant] == []


# --- les règles du rejeu, avec une recherche remplacée -----------------------------------------------------------

def test_un_refus_attendu_qui_trouve_un_passage_est_bloquant(monkeypatch):
    jeu = _jeu(_question("Q6", "refus", motif="OUT_OF_CORPUS"))
    _recherche(monkeypatch, {"Question Q6 ?": _trouve(2799)})
    (ecart,) = controle_questions.rejouer(jeu)
    assert (ecart.id, ecart.bloquant) == ("Q6", True)


def test_un_refus_pour_un_autre_motif_est_bloquant(monkeypatch):
    jeu = _jeu(_question("Q8", "refus", motif="INTENTION_INTERDITE"))
    _recherche(monkeypatch, {"Question Q8 ?": Resultat(False, "OUT_OF_CORPUS", [], 0)})
    (ecart,) = controle_questions.rejouer(jeu)
    assert ecart.bloquant and "INTENTION_INTERDITE" in ecart.message


def test_une_question_couverte_sans_passage_valide_est_bloquante(monkeypatch):
    # Des passages sont rendus, mais aucun n'est une source validée : c'est le cas mesuré de Q2 version 1 (article 661).
    jeu = _jeu(_question("Q2", "reponse", [2778, 2784]))
    _recherche(monkeypatch, {"Question Q2 ?": _trouve(661)})
    (ecart,) = controle_questions.rejouer(jeu)
    assert ecart.bloquant and "aucun passage justificatif" in ecart.message


def test_une_question_couverte_refusee_est_bloquante(monkeypatch):
    jeu = _jeu(_question("Q4", "reponse", [2788]))
    _recherche(monkeypatch, {"Question Q4 ?": Resultat(False, "OUT_OF_CORPUS", [], 0)})
    (ecart,) = controle_questions.rejouer(jeu)
    assert ecart.bloquant and "OUT_OF_CORPUS" in ecart.message


@pytest.mark.parametrize("ordre", [(2784, 2778), (2778, 2784), (2784, 661), (661, 2778)])
def test_un_changement_de_classement_entre_sources_validees_n_est_pas_un_ecart(monkeypatch, ordre):
    jeu = _jeu(_question("Q2", "reponse", [2778, 2784]))
    _recherche(monkeypatch, {"Question Q2 ?": _trouve(*ordre)})
    assert controle_questions.rejouer(jeu) == []


@pytest.mark.parametrize("resultat", [Resultat(False, "OUT_OF_CORPUS", [], 0), _trouve(9999)])
def test_reponse_ou_abstention_n_est_jamais_bloquante(monkeypatch, resultat):
    jeu = _jeu(_question("Q3", "reponse_ou_abstention", [2795]))
    _recherche(monkeypatch, {"Question Q3 ?": resultat})
    (ecart,) = controle_questions.rejouer(jeu)
    assert (ecart.id, ecart.bloquant) == ("Q3", False)


# --- le module en ligne de commande, et son rapport ---------------------------------------------------------------

def _lancer(monkeypatch, tmp_path, jeu, par_question, identite=IDENTITE, sortie=None):
    chemin_jeu = tmp_path / "jeu.json"
    chemin_jeu.write_text(json.dumps(jeu), encoding="utf-8")
    _recherche(monkeypatch, par_question)
    monkeypatch.setattr(controle_questions, "lire_identite", lambda chemin=None: identite)
    sortie = sortie or tmp_path / "rapport.json"
    code = controle_questions.main(["--sortie", str(sortie), "--jeu", str(chemin_jeu)])
    return code, sortie


def test_le_rapport_est_ecrit_dans_le_fichier_demande(monkeypatch, tmp_path):
    jeu = _jeu(_question("Q2", "reponse", [2778, 2784]), _question("Q6", "refus", motif="OUT_OF_CORPUS"))
    code, sortie = _lancer(monkeypatch, tmp_path, jeu, {"Question Q2 ?": _trouve(2784, 661),
                                                        "Question Q6 ?": Resultat(False, "OUT_OF_CORPUS", [], 0)})
    assert code == 0
    rapport = json.loads(sortie.read_text(encoding="utf-8"))
    # Le contrat avec le script du serveur (tâche B3) : l'identité de l'index sous la clé `index`, comme /health.
    assert rapport["index"] == IDENTITE
    assert rapport["bloquant"] is False and rapport["ecarts"] == []
    q2 = next(q for q in rapport["questions"] if q["id"] == "Q2")
    assert q2["passages"] == [2784, 661] and q2["hors_sources_validees"] == [661]
    assert rapport["jeu"]["version"] == 2


def test_le_module_rend_1_quand_un_ecart_bloque(monkeypatch, tmp_path):
    jeu = _jeu(_question("Q4", "reponse", [2788]))
    code, sortie = _lancer(monkeypatch, tmp_path, jeu, {"Question Q4 ?": _trouve(1866)})
    assert code == 1
    rapport = json.loads(sortie.read_text(encoding="utf-8"))   # le rapport d'un rejeu en échec est écrit quand même
    assert rapport["bloquant"] is True and rapport["ecarts"][0]["id"] == "Q4"


def test_le_module_rend_1_si_le_rapport_ne_peut_pas_etre_ecrit(monkeypatch, tmp_path):
    jeu = _jeu(_question("Q4", "reponse", [2788]))
    code, _ = _lancer(monkeypatch, tmp_path, jeu, {"Question Q4 ?": _trouve(2788)},
                      sortie=tmp_path / "dossier-absent" / "rapport.json")
    assert code == 1


def test_un_index_sans_identite_est_bloquant(monkeypatch, tmp_path):
    # Sans identité, le script du serveur ne pourrait pas vérifier l'index servi après la bascule (tâche B3).
    jeu = _jeu(_question("Q4", "reponse", [2788]))
    code, sortie = _lancer(monkeypatch, tmp_path, jeu, {"Question Q4 ?": _trouve(2788)}, identite=None)
    assert code == 1
    assert json.loads(sortie.read_text(encoding="utf-8"))["bloquant"] is True

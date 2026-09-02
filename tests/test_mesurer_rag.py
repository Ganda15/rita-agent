"""Le banc d'ablation du RAG : lecture du jeu annoté et calcul des métriques (C17).

Ces tests portent sur les **fonctions pures** du banc — celles qui ne touchent ni la
base ni l'index. Elles décident si une mesure est juste ; elles doivent donc être
vérifiées seules, sans dépendre d'un corpus qui change tous les jours.

La partie qui interroge réellement les quatre bras (D0/D1/H0/H1) est une intégration :
elle vient après, et elle s'appuie sur ces fonctions-ci.
"""
from __future__ import annotations

import pytest

from evals import mesurer_rag


# =============================================================================
# Le parseur du jeu annoté
# =============================================================================

def test_une_question_annotee_est_lue_avec_ses_identifiants(tmp_path):
    fichier = tmp_path / "q.txt"
    fichier.write_text(
        "Que disent les articles sur LVMH ? | MC.PA | 379,643 | ticker\n",
        encoding="utf-8",
    )

    questions = mesurer_rag.charger_questions(fichier)

    assert len(questions) == 1
    q = questions[0]
    assert q.question == "Que disent les articles sur LVMH ?"
    assert q.ticker == "MC.PA"
    assert q.ids_attendus == [379, 643]
    assert q.famille == "ticker"


def test_les_commentaires_et_les_lignes_vides_sont_ignores(tmp_path):
    fichier = tmp_path / "q.txt"
    fichier.write_text(
        "# un commentaire\n"
        "\n"
        "Question reelle ? | - | 12 | theme\n"
        "   # commentaire indente\n",
        encoding="utf-8",
    )

    assert len(mesurer_rag.charger_questions(fichier)) == 1


def test_un_tiret_signifie_refus_attendu_et_non_absence_d_annotation(tmp_path):
    """« - » est une annotation : la bonne réponse est de ne RIEN rendre.
    C'est mesurable, contrairement à « ? » — voir le test suivant."""
    fichier = tmp_path / "q.txt"
    fichier.write_text(
        "Quel sera le cours dans six mois ? | MC.PA | - | hors_corpus\n",
        encoding="utf-8",
    )

    q = mesurer_rag.charger_questions(fichier)[0]

    assert q.ids_attendus == []
    assert q.annotee is True


def test_un_point_d_interrogation_marque_une_question_NON_annotee(tmp_path):
    """⚠️ La distinction qui protège la mesure. « ? » veut dire « je n'ai pas encore
    tranché » ; le confondre avec « - » ferait compter une question sans vérité
    terrain comme un refus réussi — donc gonflerait le score sans rien prouver."""
    fichier = tmp_path / "q.txt"
    fichier.write_text(
        "Question trop vague ? | - | ? | theme\n",
        encoding="utf-8",
    )

    q = mesurer_rag.charger_questions(fichier)[0]

    assert q.annotee is False
    assert q.ids_attendus == []


def test_une_ligne_mal_formee_leve_une_erreur_qui_nomme_la_ligne(tmp_path):
    """Un jeu annoté silencieusement tronqué est pire qu'un jeu absent : on mesure
    sur moins de questions qu'on croit, sans jamais le voir."""
    fichier = tmp_path / "q.txt"
    fichier.write_text("il manque des colonnes | MC.PA\n", encoding="utf-8")

    with pytest.raises(ValueError, match="ligne 1"):
        mesurer_rag.charger_questions(fichier)


def test_le_vrai_jeu_du_depot_se_charge():
    """Le fichier réel doit rester lisible : s'il casse, les tests le disent."""
    questions = mesurer_rag.charger_questions(mesurer_rag.FICHIER_QUESTIONS)

    assert len(questions) >= 10
    assert {q.famille for q in questions} <= {
        "ticker", "theme", "reference", "hors_corpus", "hors_perimetre_amf"
    }


# =============================================================================
# Les métriques
# =============================================================================

def test_hit_at_k_vrai_quand_un_attendu_est_dans_les_k_premiers():
    assert mesurer_rag.hit_at_k([999, 379], attendus=[379], k=2) is True


def test_hit_at_k_faux_quand_l_attendu_arrive_apres_le_rang_k():
    """Hit@1 et Hit@5 ne mesurent pas la même chose : un moteur qui place le bon
    document en 3ᵉ position réussit Hit@5 et échoue Hit@1."""
    assert mesurer_rag.hit_at_k([999, 888, 379], attendus=[379], k=1) is False


def test_hit_at_k_vrai_des_qu_un_seul_des_attendus_est_trouve():
    """Une question au pluriel a plusieurs bonnes réponses ; en trouver une suffit."""
    assert mesurer_rag.hit_at_k([643], attendus=[379, 643, 289], k=1) is True


def test_le_rang_reciproque_vaut_l_inverse_du_premier_bon_rang():
    assert mesurer_rag.rang_reciproque([999, 379], attendus=[379]) == pytest.approx(0.5)


def test_le_rang_reciproque_vaut_zero_sans_aucun_bon_document():
    assert mesurer_rag.rang_reciproque([999, 888], attendus=[379]) == 0.0


def test_un_refus_attendu_et_obtenu_compte_comme_correct():
    assert mesurer_rag.refus_correct(ids_rendus=[], attendus=[]) is True


def test_repondre_a_une_question_hors_corpus_est_un_echec():
    """Le défaut le plus grave du RAG : inventer une réponse là où il n'y en a pas.
    Rendre un passage quand la vérité terrain dit « - » doit compter comme un échec."""
    assert mesurer_rag.refus_correct(ids_rendus=[999], attendus=[]) is False


def test_se_taire_sur_une_question_qui_avait_une_reponse_est_un_echec():
    assert mesurer_rag.refus_correct(ids_rendus=[], attendus=[379]) is False


# =============================================================================
# L'agrégation d'un bras
# =============================================================================
# `evaluer_bras` reçoit la fonction de recherche en paramètre plutôt que d'appeler
# `rag.recherche` elle-même. C'est ce qui permet de la tester sans ChromaDB, sans
# base et sans corpus — donc de vérifier le CALCUL indépendamment du moteur.

def _question(ids, famille="ticker", annotee=True):
    return mesurer_rag.Question(
        question="q", ticker=None, ids_attendus=ids, famille=famille, annotee=annotee
    )


def test_un_bras_parfait_obtient_1_partout():
    questions = [_question([10]), _question([20])]
    chercher = {("q", (10,)): ([10], 5.0), ("q", (20,)): ([20], 5.0)}

    score = mesurer_rag.evaluer_bras(
        "H0", questions, lambda q: chercher[("q", tuple(q.ids_attendus))]
    )

    assert score.hit_1 == 1.0
    assert score.mrr == 1.0
    assert score.refus_correct == 1.0
    assert score.n_questions == 2


def test_les_questions_NON_annotees_sont_exclues_du_score_et_comptees_a_part():
    """⚠️ La règle qui empêche de gonfler un résultat. Une question laissée à « ? »
    n'a pas de vérité terrain : la compter, dans un sens ou dans l'autre, invente
    une mesure. Elle est donc écartée du calcul **et signalée**, pour que personne
    ne croie avoir évalué 10 questions quand il en a évalué 9."""
    questions = [_question([10]), _question([], annotee=False)]

    score = mesurer_rag.evaluer_bras("H0", questions, lambda q: ([10], 1.0))

    assert score.n_questions == 1
    assert score.n_non_annotees == 1
    assert score.hit_1 == 1.0


def test_hit_5_recompense_ce_que_hit_1_rate():
    questions = [_question([99])]

    score = mesurer_rag.evaluer_bras("D0", questions, lambda q: ([1, 2, 3, 4, 99], 1.0))

    assert score.hit_1 == 0.0
    assert score.hit_5 == 1.0
    assert score.mrr == pytest.approx(0.2)


def test_les_latences_sont_rendues_en_p50_et_p95():
    """Une moyenne de latence cache les pics ; le p95 est ce qu'un utilisateur
    ressent réellement quand ça rame."""
    questions = [_question([1]) for _ in range(10)]
    latences = iter([10, 10, 10, 10, 10, 10, 10, 10, 10, 500])

    score = mesurer_rag.evaluer_bras("H0", questions, lambda q: ([1], next(latences)))

    assert score.latence_p50_ms == pytest.approx(10)
    assert score.latence_p95_ms == pytest.approx(500)

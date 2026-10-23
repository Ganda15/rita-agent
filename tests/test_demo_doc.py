"""Sprint 5, étape 13 : le scénario de la démo des 10 minutes (grille de l'atelier 5, critère 6).

Le brief demande « le scénario de démo écrit et répété » : parcours principal, une livraison automatique, une alerte
déclenchée. Ces tests vérifient le scénario contre le code : la somme des segments tient en 10 minutes ; chaque
commande citée existe ; les questions citées sont celles vérifiées sur la copie le 22/10 ; le plan B existe. Ils ne
remplacent pas les deux répétitions chronométrées.
"""
import re
from pathlib import Path

import pytest

from monitorage.exercer import QUESTIONS_DE_TEST

RACINE = Path(__file__).parent.parent
DEMO = RACINE / "docs" / "sprint-5" / "DEMO.md"
QUESTIONS_VERIFIEES = (QUESTIONS_DE_TEST[0], QUESTIONS_DE_TEST[3])        # réponse citée, vérifiées le 22/10
HORS_CORPUS = "Quelle est la recette de la tarte Tatin ?"                  # refus OUT_OF_CORPUS, vérifié le 22/10


@pytest.fixture(scope="module")
def demo():
    return DEMO.read_text(encoding="utf-8")


def _durees_s(texte: str) -> list[int]:
    """Les durées de la table du déroulé : une ligne par segment, « | 0:00 | 20 s | ... »."""
    return [int(d) for d in re.findall(r"^\| \d+:\d\d \| (\d+) s \|", texte, flags=re.MULTILINE)]


def test_le_deroule_tient_en_dix_minutes(demo):
    durees = _durees_s(demo)
    assert len(durees) >= 5, durees
    assert sum(durees) <= 600, sum(durees)


def test_les_trois_exigences_du_critere_6_ont_leur_segment(demo):
    for segment in ("Parcours principal", "Livraison", "Alerte déclenchée"):
        assert f"| {segment} |" in demo, segment


def test_les_questions_citees_sont_celles_verifiees_sur_la_copie(demo):
    for question in (*QUESTIONS_VERIFIEES, HORS_CORPUS):
        assert question in demo, question


def test_chaque_commande_citee_existe(demo):
    actions = set(re.findall(r"copie_sprint5\.py (\w+)", demo))
    assert actions and actions <= {"deployer", "revenir", "initialiser", "collecter", "etat"}
    exercices = set(re.findall(r"monitorage\.exercer (\w+)", demo))
    assert exercices and exercices <= {"panne", "fin", "appels", "derive"} and "derive" in exercices
    assert "python.exe -m monitorage.vigie" in demo and "--github" in demo


def test_la_livraison_de_production_est_citee_et_dite_non_rejouee(demo):
    assert "actions/runs/39983152061" in demo     # N16 : la livraison qui a mis le sprint 5 en production
    assert "pas rejouée" in demo


def test_le_scenario_a_sa_liste_de_controle_et_son_plan_b(demo):
    assert "## Avant la démo" in demo and "## Plan B" in demo and "## Après la démo" in demo


def test_le_scenario_n_a_aucun_tiret_cadratin(demo):
    assert chr(0x2014) not in demo

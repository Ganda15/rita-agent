"""Sprint 4, tâche A0 : les tests qui écrivent dans PostgreSQL n'écrivent que dans la base de test déclarée.

Certains tests écrivent vraiment, puis annulent leur transaction (`tests/test_vue_valorisation.py`, `DELETE FROM
taux_change`). Ils obtiennent leur adresse de connexion par une seule fonction, `dsn_de_test()` : elle ne la rend que
si le nom de la base est celui déclaré dans `RITA_BASE_DE_TEST`. Sinon, ces tests sont sautés, avec une raison qui
nomme la base, jamais l'adresse : elle contient le mot de passe.
"""
import importlib
import re
from pathlib import Path

import pytest

DOSSIER_TESTS = Path(__file__).resolve().parent
URL_REELLE = "postgresql://rita:secret-fictif@localhost:5433/rita"
URL_DE_TEST = "postgresql://rita_sprint4:secret-fictif@localhost:5433/rita_sprint4"


def _garde():
    """Le module est importé dans chaque test : tant qu'il n'existe pas, chacun échoue pour cette raison."""
    return importlib.import_module("tests.garde_base")


def test_le_nom_de_base_se_lit_sans_connexion():
    assert _garde().nom_de_base(URL_DE_TEST) == "rita_sprint4"


def test_la_base_declaree_rend_l_adresse(monkeypatch):
    # Le témoin des sauts ci-dessous : sans lui, une fonction qui saute toujours passerait tous les tests.
    monkeypatch.setenv("DATABASE_URL", URL_DE_TEST)
    monkeypatch.setenv("RITA_BASE_DE_TEST", "rita_sprint4")
    assert _garde().adresse_de_la_base_de_test() == URL_DE_TEST


def test_une_base_non_declaree_est_sautee_sans_montrer_l_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", URL_REELLE)
    monkeypatch.setenv("RITA_BASE_DE_TEST", "rita_sprint4")
    with pytest.raises(pytest.skip.Exception) as saut:
        _garde().adresse_de_la_base_de_test()
    assert "rita" in str(saut.value)
    assert "secret-fictif" not in str(saut.value)


def test_sans_base_declaree_tout_est_saute(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", URL_DE_TEST)
    monkeypatch.delenv("RITA_BASE_DE_TEST", raising=False)
    with pytest.raises(pytest.skip.Exception):
        _garde().adresse_de_la_base_de_test()


def test_sans_database_url_tout_est_saute(monkeypatch):
    # Le cas de la CI : aucune base, donc aucun test d'écriture.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("RITA_BASE_DE_TEST", "rita_sprint4")
    with pytest.raises(pytest.skip.Exception):
        _garde().adresse_de_la_base_de_test()


# Une lecture directe contournerait le garde-fou : l'adresse lue dans l'environnement ou dans `.env`, ou une fonction
# de connexion propre à un fichier de tests.
LECTURES_DIRECTES = re.compile(
    r"""os\.environ\s*\[\s*["']DATABASE_URL["']\s*\]"""
    r"""|os\.environ\.get\(\s*["']DATABASE_URL["']"""
    r"""|os\.getenv\(\s*["']DATABASE_URL["']"""
    r"""|RACINE\s*/\s*["']\.env["']"""
    r"""|def\s+dsn_proprietaire\b""")
AUTORISES = {"garde_base.py", Path(__file__).name}


def test_aucun_test_ne_lit_database_url_directement():
    fautifs = [f"{chemin.name}:{numero}"
               for chemin in sorted(DOSSIER_TESTS.glob("*.py")) if chemin.name not in AUTORISES
               for numero, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), start=1)
               if LECTURES_DIRECTES.search(ligne)]
    assert fautifs == []


# --- 02/11/2026 : un test qui demande la base porte le marqueur `postgresql` -----------------------------------------
#
# Le job `base` de la CI choisissait ses fichiers par la recherche du mot `dsn_de_test` : fragile, un fichier qui citait
# le mot y entrait (`tests/test_ci_base.py`). Il choisit désormais les tests marqués `postgresql`. Ce garde-fou empêche
# l'oubli du marqueur : un tel test serait sauté dans le job `pytest` et jamais choisi par le job `base`, sans que
# personne le voie.

def test_un_test_qui_demande_la_base_sans_le_marqueur_echoue():
    with pytest.raises(pytest.fail.Exception) as echec:
        _garde().verifier_le_marqueur("tests/test_x.py::test_y (setup)", set())
    assert "postgresql" in str(echec.value)
    assert "tests/test_x.py::test_y" in str(echec.value), "le message nomme le test à marquer"


def test_un_test_marque_passe_le_controle():
    _garde().verifier_le_marqueur("tests/test_x.py::test_y (call)", {"tests/test_x.py::test_y"})


def test_hors_d_un_test_le_controle_echoue_aussi():
    """Sans `PYTEST_CURRENT_TEST`, on ne sait pas qui demande la base : refus plutôt qu'un appel non vérifié."""
    with pytest.raises(pytest.fail.Exception):
        _garde().verifier_le_marqueur(None, set())


def test_dsn_de_test_applique_le_controle(monkeypatch):
    """Ce test-ci n'a pas le marqueur : `dsn_de_test()` le refuse, même avec une base de test bien déclarée."""
    monkeypatch.setenv("DATABASE_URL", URL_DE_TEST)
    monkeypatch.setenv("RITA_BASE_DE_TEST", "rita_sprint4")
    with pytest.raises(pytest.fail.Exception):
        _garde().dsn_de_test()


def test_le_registre_des_tests_marques_suit_la_collecte(request):
    """`tests/conftest.py` remplit le registre à la fin de la collecte, avec les tests qui portent le marqueur."""
    attendus = {item.nodeid for item in request.session.items if item.get_closest_marker("postgresql")}
    assert _garde().TESTS_MARQUES == attendus

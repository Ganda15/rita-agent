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
    assert _garde().dsn_de_test() == URL_DE_TEST


def test_une_base_non_declaree_est_sautee_sans_montrer_l_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", URL_REELLE)
    monkeypatch.setenv("RITA_BASE_DE_TEST", "rita_sprint4")
    with pytest.raises(pytest.skip.Exception) as saut:
        _garde().dsn_de_test()
    assert "rita" in str(saut.value)
    assert "secret-fictif" not in str(saut.value)


def test_sans_base_declaree_tout_est_saute(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", URL_DE_TEST)
    monkeypatch.delenv("RITA_BASE_DE_TEST", raising=False)
    with pytest.raises(pytest.skip.Exception):
        _garde().dsn_de_test()


def test_sans_database_url_tout_est_saute(monkeypatch):
    # Le cas de la CI : aucune base, donc aucun test d'écriture.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("RITA_BASE_DE_TEST", "rita_sprint4")
    with pytest.raises(pytest.skip.Exception):
        _garde().dsn_de_test()


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

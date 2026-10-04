"""L'étape de test des données est une étape nommée de la chaîne, avant la suite complète (C13).

Critère C13 du livrable E3 : « L'étape de test des données est intégrée à la chaîne et s'exécute sans
erreur. » Jusqu'au 04/10/2026, les tests de collecte, de nettoyage et d'import tournaient bien en CI,
mais noyés dans la suite complète : aucune étape ne s'appelait « test des données », et un échec de
données se lisait comme un échec quelconque. Ces tests figent l'étape : son nom, sa place (avant la
suite complète, pour qu'un défaut de données arrête la chaîne en premier) et ce qu'elle exécute.
"""
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).parent.parent
NOM = "Tester les données (collecte, nettoyage, import, RGPD)"

# Les fichiers qui testent la validation et la préparation des données, et seulement eux.
FICHIERS_DONNEES = [
    "tests/test_ingest.py", "tests/test_importer.py", "tests/test_cotations.py", "tests/test_ecb.py",
    "tests/test_fred.py", "tests/test_rss.py", "tests/test_scraper.py", "tests/test_positions.py",
    "tests/test_schema.py", "tests/test_marches.py", "tests/test_fraicheur.py",
    "tests/test_manifeste_collecte.py", "tests/test_journal_pipeline.py", "tests/test_rattrapage.py",
    "tests/test_cas_chapitre_donnees.py", "tests/test_vue_valorisation.py", "tests/test_rgpd_purge.py",
    "tests/test_rgpd_registre.py", "tests/test_database.py",
]


@pytest.fixture(scope="module")
def etapes():
    flux = yaml.safe_load((RACINE / ".github/workflows/test.yml").read_text(encoding="utf-8"))
    return flux["jobs"]["pytest"]["steps"]


def _indice(etapes, nom):
    return next((i for i, e in enumerate(etapes) if e.get("name") == nom), None)


def test_une_etape_nommee_teste_les_donnees(etapes):
    assert _indice(etapes, NOM) is not None, f"aucune étape « {NOM} » dans le job pytest"


def test_l_etape_des_donnees_passe_avant_la_suite_complete(etapes):
    donnees = _indice(etapes, NOM)
    suite = _indice(etapes, "Lancer les tests et mesurer la couverture")
    assert donnees is not None and suite is not None
    assert donnees < suite, "un défaut de données doit arrêter la chaîne avant la suite complète"


def test_l_etape_des_donnees_execute_tous_les_fichiers_de_donnees(etapes):
    commande = etapes[_indice(etapes, NOM)]["run"]
    assert "pytest" in commande
    manquants = [f for f in FICHIERS_DONNEES if f not in commande]
    assert not manquants, f"fichiers de données absents de l'étape : {manquants}"


def test_les_fichiers_de_donnees_existent():
    absents = [f for f in FICHIERS_DONNEES if not (RACINE / f).exists()]
    assert not absents, absents

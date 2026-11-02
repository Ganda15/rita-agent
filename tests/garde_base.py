"""L'adresse de la base pour les tests qui écrivent dans PostgreSQL (sprint 4, tâche A0).

Ces tests écrivent vraiment, puis annulent leur transaction. Ils ne visent jamais une autre base que la base de test
déclarée dans le `.env` du dossier (`RITA_BASE_DE_TEST`) : si `DATABASE_URL` vise une autre base, la vraie base
locale par exemple, ils sont sautés au lieu d'y écrire. La raison du saut nomme la base, jamais l'adresse, qui contient
le mot de passe. Tout test qui a besoin de la base passe par `dsn_de_test()` (contrôlé par `tests/test_garde_base.py`).

Depuis le 02/11/2026, un tel test porte aussi le marqueur `postgresql` : le job `base` de la CI choisit ses tests par
ce marqueur, et `dsn_de_test()` fait échouer un test qui l'a oublié. Sans ce contrôle, un test oublié serait sauté dans
le job `pytest` et jamais choisi par le job `base` : il ne tournerait nulle part, sans que la CI le dise.
"""
import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from dotenv import load_dotenv

RACINE = Path(__file__).resolve().parent.parent

# Une seule fois, au chargement : `load_dotenv` ne remplace jamais une variable déjà posée. Relu à chaque appel, il
# annulerait le `monkeypatch.delenv` d'un test.
load_dotenv(RACINE / ".env")


def nom_de_base(url: str) -> str:
    """Le nom de la base, lu dans l'adresse (`postgresql://compte:secret@hote:port/base`), sans connexion."""
    return urlsplit(url).path.lstrip("/")


MARQUEUR = "postgresql"

# Les identifiants des tests qui portent le marqueur, posés par `tests/conftest.py` à la fin de la collecte.
TESTS_MARQUES: set[str] = set()


def verifier_le_marqueur(test_courant: str | None, marques: set[str]) -> None:
    """Échec si le test qui demande la base ne porte pas le marqueur `postgresql`.

    `test_courant` vient de la variable `PYTEST_CURRENT_TEST` (« chemin::test (setup) ») : pytest la pose avant de
    créer les fixtures d'un test, elle désigne donc le test qui demande la base. Absente, on ne sait pas qui appelle :
    échec aussi, plutôt qu'un appel non vérifié.
    """
    if not test_courant:
        pytest.fail("dsn_de_test() appelée hors d'un test : le marqueur « postgresql » ne peut pas être vérifié",
                    pytrace=False)
    identifiant = test_courant.rsplit(" (", 1)[0]
    if identifiant not in marques:
        pytest.fail(f"{identifiant} demande PostgreSQL sans le marqueur « {MARQUEUR} » : ajouter "
                    f"@pytest.mark.{MARQUEUR} (ou pytestmark dans le fichier), sinon le job base de la CI ne le "
                    f"choisit pas", pytrace=False)


def dsn_de_test() -> str:
    """L'adresse de la base de test pour un test marqué `postgresql`, ou le saut ; un test non marqué échoue."""
    verifier_le_marqueur(os.environ.get("PYTEST_CURRENT_TEST"), TESTS_MARQUES)
    return adresse_de_la_base_de_test()


def adresse_de_la_base_de_test() -> str:
    """L'adresse de la base de test, ou le saut du test qui la demande."""
    url = os.environ.get("DATABASE_URL", "")
    declaree = os.environ.get("RITA_BASE_DE_TEST", "")
    if not url:
        pytest.skip("pas de DATABASE_URL : base locale absente (CI)", allow_module_level=True)
    if not declaree:
        pytest.skip("RITA_BASE_DE_TEST absente : aucune base n'est déclarée comme base de test",
                    allow_module_level=True)
    nom = nom_de_base(url)
    if nom != declaree:
        pytest.skip(f"la base « {nom} » n'est pas la base de test déclarée « {declaree} »", allow_module_level=True)
    return url

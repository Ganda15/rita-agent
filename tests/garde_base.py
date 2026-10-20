"""L'adresse de la base pour les tests qui écrivent dans PostgreSQL (sprint 4, tâche A0).

Ces tests écrivent vraiment, puis annulent leur transaction. Ils ne visent jamais une autre base que la base de test
déclarée dans le `.env` du dossier (`RITA_BASE_DE_TEST`) : si `DATABASE_URL` vise une autre base, la vraie base
locale par exemple, ils sont sautés au lieu d'y écrire. La raison du saut nomme la base, jamais l'adresse, qui contient
le mot de passe. Tout test qui a besoin de la base passe par `dsn_de_test()` (contrôlé par `tests/test_garde_base.py`).
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


def dsn_de_test() -> str:
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

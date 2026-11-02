"""Les tests qui exigent PostgreSQL tournent vraiment en CI, et un test sauté fait échouer le job (01/11/2026).

Jusqu'au 01/11/2026, ces tests se sautaient en CI faute de base (`tests/garde_base.py`) : la chaîne restait verte sans
les avoir exécutés, et le défaut #79 (pire baisse positive) pouvait revenir sans que rien ne le dise. Le job `base` leur
donne une base PostgreSQL jetable, de la même version que la production, avec le schéma et les rôles du dépôt, et
échoue si l'un d'eux est sauté : une base indisponible ne donne plus une validation verte.
"""
import re
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).parent.parent


@pytest.fixture(scope="module")
def job():
    flux = yaml.safe_load((RACINE / ".github/workflows/test.yml").read_text(encoding="utf-8"))
    return flux["jobs"]["base"]


def _commandes(job):
    return "\n".join(e.get("run", "") for e in job["steps"])


def test_le_job_a_une_base_postgresql_de_la_version_de_production(job):
    service = job["services"]["postgres"]
    assert service["image"] == "postgres:18-alpine"
    compose = (RACINE / "docker-compose.yml").read_text(encoding="utf-8")
    assert "image: postgres:18-alpine" in compose, "la base de CI suit la version de la production"


def test_le_job_charge_le_schema_puis_les_roles(job):
    commandes = _commandes(job)
    assert "db/schema.sql" in commandes and "db/roles.sql" in commandes
    assert commandes.index("db/schema.sql") < commandes.index("db/roles.sql")
    assert "ON_ERROR_STOP=1" in commandes


def test_la_base_de_test_declaree_est_celle_du_service(job):
    assert job["env"]["RITA_BASE_DE_TEST"] == job["services"]["postgres"]["env"]["POSTGRES_DB"]
    assert job["env"]["DATABASE_URL"].endswith("/" + job["services"]["postgres"]["env"]["POSTGRES_DB"])


def test_le_job_choisit_les_tests_par_le_marqueur_postgresql(job):
    """Depuis le 02/11/2026 : le marqueur, plus la recherche du mot `dsn_de_test` dans les fichiers (fragile : ce
    fichier-ci y entrait parce qu'il cite le mot). Un test qui demande la base sans le marqueur échoue
    (`tests/garde_base.py`), il ne peut donc pas sortir de la sélection sans que la CI le dise."""
    commandes = _commandes(job)
    assert "-m postgresql" in commandes
    assert "grep -l dsn_de_test" not in commandes


def test_le_marqueur_postgresql_est_declare(pytestconfig):
    assert any(ligne.startswith("postgresql:") for ligne in pytestconfig.getini("markers"))


def test_un_test_saute_fait_echouer_le_job(job):
    commandes = _commandes(job)
    assert "set -o pipefail" in commandes
    assert "skipped" in commandes and "exit 1" in commandes


def test_le_job_installe_ce_que_les_tests_importent_au_chargement(job):
    """02/11/2026, premier passage du marqueur sur GitHub : `-m postgresql tests` charge tous les fichiers avant de
    choisir. Un fichier qui saute au chargement, faute d'une dépendance (`pytest.importorskip` au niveau du module),
    compte comme un test sauté et fait échouer le job, sans aucun test PostgreSQL en cause (`test_smoke_ui.py` sans
    Playwright, 3 sautés). Le job installe donc tout ce que les tests importent au chargement."""
    exigences = (RACINE / "requirements.txt").read_text(encoding="utf-8").lower()
    commandes = _commandes(job).lower()
    manquants = []
    for fichier in sorted((RACINE / "tests").glob("test_*.py")):
        for ligne in fichier.read_text(encoding="utf-8").splitlines():
            trouve = re.match(r"""^\S.*pytest\.importorskip\(\s*["']([\w.]+)""", ligne)
            if trouve:
                paquet = trouve.group(1).split(".")[0].lower()
                if paquet not in exigences and f"pip install {paquet}" not in commandes:
                    manquants.append(f"{fichier.name} : {paquet}")
    assert manquants == []

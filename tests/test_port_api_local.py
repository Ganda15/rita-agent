"""Le port de l'API n'écoute que la machine (constat du 07/11/2026, revue OWASP, entrée A02:2025 « mauvaise configuration »).

Mesuré le 07/11/2026 vers 0 h UTC, depuis le poste d'Era : `http://178.104.184.125:8001/health` répond 200. L'API de
production était donc joignable en clair, sans le chiffrement de Caddy, par n'importe qui sur Internet : une clé d'API
envoyée par cette voie circulerait en clair. Le port est publié par `docker-compose.yml` sur toutes les interfaces
(`8001:8000`), et un port publié par Docker passe devant le pare-feu `ufw` du serveur.

Lié à `127.0.0.1`, le port reste joignable par Caddy, qui tourne sur la machine, par le script de livraison (il
interroge `http://127.0.0.1:8001`, `deploy/deployer.py`) et par le navigateur du poste en développement
(`http://localhost:8001`). Même règle que la base de développement (constat S8, `tests/test_compose_developpement.py`).
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

RACINE = Path(__file__).resolve().parent.parent


def test_le_port_de_l_api_n_est_publie_que_sur_la_machine():
    compose = yaml.safe_load((RACINE / "docker-compose.yml").read_text(encoding="utf-8"))
    ports = compose["services"]["api"]["ports"]
    assert ports == ["127.0.0.1:8001:8000"], ports


def test_le_script_de_livraison_interroge_le_port_local():
    """Le contrôle de santé de la livraison passe par 127.0.0.1 : la restriction ne le coupe pas."""
    texte = (RACINE / "deploy" / "deployer.py").read_text(encoding="utf-8")
    assert 'URL_PRODUCTION = f"http://127.0.0.1:{PORT_PRODUCTION}"' in texte


@pytest.mark.skipif(shutil.which("docker") is None, reason="docker absent : la configuration résolue n'est pas lue")
def test_compose_resolu_publie_l_api_sur_127_0_0_1(tmp_path):
    """La configuration que Compose calcule réellement, avec un fichier d'environnement fictif et versionné."""
    sortie = subprocess.run(
        ["docker", "compose", "--env-file", str(RACINE / "tests" / "donnees" / "env-fictif"),
         "-f", str(RACINE / "docker-compose.yml"), "config", "--format", "json"],
        capture_output=True, text=True, cwd=tmp_path, timeout=60)
    if sortie.returncode != 0:
        pytest.skip(f"docker compose config indisponible : {sortie.stderr[:200]}")
    ports = json.loads(sortie.stdout)["services"]["api"]["ports"]
    assert len(ports) == 1
    assert ports[0]["host_ip"] == "127.0.0.1" and str(ports[0]["published"]) == "8001" and ports[0]["target"] == 8000

"""Sprint 2, tâche 3 : le contrôle des secrets dans la chaîne.

Trois garanties, testées sans lancer gitleaks :
- les règles par défaut de gitleaks sont gardées, et les seules exceptions visent les cinq fausses clés de test du
  dépôt, chacune écrite en entier (aucun motif large qui laisserait passer une vraie clé) ;
- `.gitleaksignore` ne contient que les deux secrets historiques RÉVOQUÉS de l'incident INC-008, jamais un faux
  positif ;
- le travail `secrets` lit tout l'historique, à une version fixée, valeurs masquées, et l'image est contrôlée.
"""
import os
import re
import secrets
import shutil
import string
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parent.parent
LIVRAISON = (RACINE / ".github" / "workflows" / "livraison.yml")

FAUSSES_CLES = {
    "cle-de-test-integration-continue-32c",
    "cle-de-verification-au-demarrage-32c",
    "cle-de-test-smoke-ui-32-caracteres-x",
    "cle-de-reconstruction-ci-32-caracteres",
    "remplacer-par-une-cle-generee-de-32-octets",
}


def _exceptions() -> list[str]:
    config = tomllib.loads((RACINE / ".gitleaks.toml").read_text(encoding="utf-8"))
    assert config["extend"]["useDefault"] is True, "les règles par défaut de gitleaks doivent être gardées"
    return [motif for liste in config["allowlists"] for motif in liste["regexes"]]


def test_les_exceptions_ne_visent_que_les_cinq_fausses_cles():
    motifs = _exceptions()
    assert len(motifs) == len(FAUSSES_CLES)
    for motif in motifs:
        assert motif.startswith("^") and motif.endswith("$"), f"motif non ancré : {motif}"
        assert ".*" not in motif and ".+" not in motif, f"motif trop large : {motif}"
    for cle in FAUSSES_CLES:
        assert sum(bool(re.search(m, cle)) for m in motifs) == 1, f"{cle} doit être couverte par une seule exception"


def test_une_vraie_cle_ne_ressemble_a_aucune_exception():
    motifs = _exceptions()
    alphabet = string.ascii_letters + string.digits
    for _ in range(50):
        cle = "".join(secrets.choice(alphabet) for _ in range(32))
        assert not any(re.search(m, cle) for m in motifs)


def test_gitleaksignore_ne_contient_que_les_deux_secrets_revoques():
    lignes = (RACINE / ".gitleaksignore").read_text(encoding="utf-8").splitlines()
    commentaires = " ".join(l for l in lignes if l.startswith("#"))
    empreintes = [l for l in lignes if l.strip() and not l.startswith("#")]
    assert "INC-008" in commentaires and "révoqu" in commentaires.lower()
    assert len(empreintes) == 2
    for empreinte in empreintes:
        assert re.fullmatch(r"[0-9a-f]{40}:\.env\.example:generic-api-key:\d+", empreinte), empreinte


def test_le_travail_secrets_lit_tout_l_historique_a_une_version_fixee():
    texte = LIVRAISON.read_text(encoding="utf-8")
    assert re.search(r"^  secrets:$", texte, re.M), "le travail secrets doit exister dans livraison.yml"
    bloc = texte.split("\n  secrets:\n", 1)[1].split("\n  construire-et-publier:\n", 1)[0]
    assert "fetch-depth: 0" in bloc
    assert "zricethezav/gitleaks:v8.30.1" in bloc
    assert "--redact" in bloc and "--gitleaks-ignore-path" in bloc and "--config" in bloc
    assert "--branches --remotes --tags" in bloc
    assert "scripts/verifier_dockerfile.py Dockerfile" in bloc


def _etape_controle_env() -> str:
    import yaml

    etapes = yaml.safe_load(LIVRAISON.read_text(encoding="utf-8"))["jobs"]["construire-et-publier"]["steps"]
    return next(e["run"] for e in etapes if e.get("name", "").startswith("Vérifier que l'image ne contient pas"))


def test_le_controle_env_echoue_aussi_sur_une_panne_de_docker():
    # Le conteneur doit RÉUSSIR à prouver l'absence (`test ! -e`) ; toute autre sortie, fichier présent ou panne de
    # Docker (125, 126, 127), doit faire échouer l'étape. Un `if docker run ...; then` prenait une panne pour un succès.
    etape = _etape_controle_env()
    assert "test ! -e /app/.env" in etape
    assert "if docker run" not in etape


@pytest.mark.skipif(sys.platform == "win32" or shutil.which("bash") is None,
                    reason="simulation en bash : tourne dans la chaîne (Linux)")
@pytest.mark.parametrize("code_docker, doit_reussir", [(0, True), (1, False), (125, False), (126, False), (127, False)])
def test_le_controle_env_simule_avec_un_faux_docker(tmp_path, code_docker, doit_reussir):
    faux = tmp_path / "docker"
    faux.write_text('#!/bin/sh\nexit "$FAUX_CODE"\n', encoding="utf-8")
    faux.chmod(0o755)
    env = dict(os.environ, FAUX_CODE=str(code_docker), PATH=f"{tmp_path}{os.pathsep}{os.environ['PATH']}")
    resultat = subprocess.run(["bash", "-e", "-c", _etape_controle_env()], env=env, capture_output=True, text=True)
    assert (resultat.returncode == 0) is doit_reussir, resultat.stdout + resultat.stderr

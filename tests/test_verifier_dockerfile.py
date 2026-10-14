"""Tests de `scripts/verifier_dockerfile.py` (sprint 2, tâche 3) : aucune instruction `ARG` ni `ENV` du
Dockerfile ne doit déclarer un secret, lignes continuées par `\\` comprises.

Les exemples sont inventés : ils prouvent que le contrôle voit un secret quand il y en a un, y compris caché
sur une ligne de suite, au lieu de seulement passer sur le Dockerfile réel.
"""
import importlib.util
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def _module():
    spec = importlib.util.spec_from_file_location(
        "verifier_dockerfile", RACINE / "scripts" / "verifier_dockerfile.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_declarations_conformes():
    v = _module()
    texte = "ARG GIT_SHA=inconnu\nENV A=1 \\\n    B=2\n"
    assert v.declarations(texte) == ["GIT_SHA", "A", "B"]
    assert v.declarations_sensibles(texte) == []


def test_env_sensible_sur_une_ligne():
    assert _module().declarations_sensibles("ENV API_KEY=x\n") == ["API_KEY"]


def test_env_sensible_sur_une_ligne_continuee():
    assert _module().declarations_sensibles("ENV A=1 \\\n    SECRET_TOKEN=x\n") == ["SECRET_TOKEN"]


def test_arg_sensible_sans_valeur():
    assert _module().declarations_sensibles("ARG DB_PASSWORD\n") == ["DB_PASSWORD"]


def test_les_commentaires_et_les_autres_instructions_sont_ignores():
    texte = "# ENV API_KEY=dans-un-commentaire\nRUN echo TOKEN\nCOPY secret.txt .\n"
    assert _module().declarations(texte) == []


def test_dockerfile_du_depot_sans_declaration_sensible():
    texte = (RACINE / "Dockerfile").read_text(encoding="utf-8")
    v = _module()
    assert "RITA_GIT_SHA" in v.declarations(texte), "la lecture doit voir les ENV continués du Dockerfile"
    assert v.declarations_sensibles(texte) == []


def test_la_ligne_de_commande_rend_1_si_un_secret_est_declare(tmp_path):
    faux = tmp_path / "Dockerfile"
    faux.write_text("FROM python:3.13-slim\nENV A=1 \\\n    OPENAI_API_KEY=x\n", encoding="utf-8")
    assert _module().main([str(faux)]) == 1


def test_la_ligne_de_commande_rend_0_sur_le_dockerfile_du_depot():
    assert _module().main([str(RACINE / "Dockerfile")]) == 0

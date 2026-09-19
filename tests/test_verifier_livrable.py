"""Tests de `scripts/verifier_livrable.py` — la Definition of Done d'un livrable (C13).

Le verdict d'un livrable ne s'ecrit pas a la main : il se GENERE depuis des commandes.
Un tableau qui ne peut pas passer au rouge n'est pas une verification, c'est une decoration.
Ces tests prouvent que chaque case peut passer au rouge, en faisant echouer une verification.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).parent.parent
PYTHON = sys.executable


def charger_script():
    spec = importlib.util.spec_from_file_location(
        "verifier_livrable", RACINE / "scripts" / "verifier_livrable.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # requis par @dataclass sous `from __future__ import annotations`
    spec.loader.exec_module(module)
    return module


def test_une_verification_qui_echoue_rend_sa_case_rouge_et_le_verdict_faux():
    vl = charger_script()
    verifications = [
        vl.Verification("passe", [PYTHON, "-c", "pass"]),
        vl.Verification("echoue", [PYTHON, "-c", "import sys; sys.exit(3)"]),
    ]
    resultats = vl.executer(verifications)
    table = vl.tableau(resultats)
    assert "| ✅ | passe" in table
    assert "| ❌ | echoue" in table
    assert vl.verdict(resultats) is False


def test_tout_vert_donne_un_verdict_vrai():
    vl = charger_script()
    resultats = vl.executer([vl.Verification("passe", [PYTHON, "-c", "pass"])])
    assert vl.verdict(resultats) is True


def test_le_tag_doit_etre_cite_dans_etat_et_changelog(tmp_path):
    vl = charger_script()
    etat = tmp_path / "ETAT.md"; changelog = tmp_path / "CHANGELOG.md"
    etat.write_text("livrable-E4-v1 envoye", encoding="utf-8")
    changelog.write_text("rien", encoding="utf-8")
    ok, detail = vl.tag_cite("livrable-E4-v1", [etat, changelog])
    assert ok is False
    assert "CHANGELOG.md" in detail  # le detail nomme le fichier qui manque
    changelog.write_text("livrable-E4-v1", encoding="utf-8")
    assert vl.tag_cite("livrable-E4-v1", [etat, changelog])[0] is True


def test_un_arbre_git_sale_est_refuse(tmp_path):
    vl = charger_script()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    assert vl.arbre_propre(tmp_path)[0] is True
    (tmp_path / "brouillon.txt").write_text("x", encoding="utf-8")
    ok, detail = vl.arbre_propre(tmp_path)
    assert ok is False
    assert "brouillon.txt" in detail

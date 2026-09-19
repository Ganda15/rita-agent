"""Tests des hooks Claude Code livrés avec le dépôt (`.claude/hooks/`) — C10, C17.

Ces deux scripts sont des garde-fous d'ENFORCEMENT : ils tournent avant chaque écriture et à chaque fin
de tour. Un garde-fou contournable n'est pas un garde-fou — trois contournements réels le 19/09/2026
(Bash, PowerShell, puis interpréteur signalé par la revue Codex sur la PR #1). Chaque contournement
trouvé devient un test ici, pour ne jamais revenir.
"""
import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).parent.parent
HOOKS = RACINE / ".claude" / "hooks"
PYTHON = sys.executable


def lancer_hook(nom: str, entree: dict) -> subprocess.CompletedProcess:
    return subprocess.run([PYTHON, str(HOOKS / nom)], input=json.dumps(entree),
                          capture_output=True, text=True, encoding="utf-8")


# --- bloquer-secrets -----------------------------------------------------------------------------

def test_un_write_vers_env_est_refuse():
    r = lancer_hook("bloquer-secrets.py", {"tool_name": "Write", "tool_input": {"file_path": "D:/x/.env"}})
    assert r.returncode == 2 and "REFUSE" in r.stderr


def test_une_commande_powershell_qui_ecrit_env_est_refusee():
    r = lancer_hook("bloquer-secrets.py", {"tool_name": "PowerShell",
                    "tool_input": {"command": 'Add-Content -Path .env -Value "K=1"'}})
    assert r.returncode == 2


def test_une_ecriture_par_interpreteur_est_refusee():
    """Trouvé par la revue Codex (PR #1) : aucun opérateur shell, mais un interpréteur qui écrit."""
    for commande in [
        "python -c \"open('.env','w').write('K=1')\"",
        "node -e \"require('fs').writeFileSync('.env','K=1')\"",
        "python -c \"from pathlib import Path; Path('cle.pem').write_text('x')\"",
    ]:
        r = lancer_hook("bloquer-secrets.py", {"tool_name": "Bash", "tool_input": {"command": commande}})
        assert r.returncode == 2, commande


def test_lire_env_et_ecrire_ailleurs_restent_permis():
    for outil, entree in [
        ("Bash", {"command": "cat .env"}),
        ("Bash", {"command": "pytest -q > sortie.txt"}),
        ("Bash", {"command": "python -c \"print('environment')\""}),
        ("Write", {"file_path": "D:/x/.env.example"}),
        ("Read", {"file_path": "D:/x/.env"}),
    ]:
        r = lancer_hook("bloquer-secrets.py", {"tool_name": outil, "tool_input": entree})
        assert r.returncode == 0, (outil, entree)


# --- exiger-tests-verts --------------------------------------------------------------------------

def depot_temporaire(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                    "--allow-empty", "-m", "base"], cwd=tmp_path, check=True)
    return tmp_path


def test_sans_changement_python_le_stop_passe_sans_lancer_pytest(tmp_path):
    depot = depot_temporaire(tmp_path)
    r = lancer_hook("exiger-tests-verts.py", {"cwd": str(depot), "prompt_id": "a", "scratchpad_dir": str(tmp_path)})
    assert r.returncode == 0


def test_un_test_rouge_non_commite_bloque_le_stop(tmp_path):
    depot = depot_temporaire(tmp_path)
    (depot / "tests").mkdir(); (depot / "tests" / "test_ko.py").write_text("def test_ko():\n    assert 1 == 2\n")
    r = lancer_hook("exiger-tests-verts.py", {"cwd": str(depot), "prompt_id": "b", "scratchpad_dir": str(tmp_path)})
    assert r.returncode == 2 and "ROUGE" in r.stderr


def test_un_test_rouge_deja_commite_bloque_aussi_le_stop(tmp_path):
    """Trouvé par la revue Codex (PR #1) : commiter puis conclure vidait `git status` et sautait pytest."""
    depot = depot_temporaire(tmp_path)
    (depot / "tests").mkdir(); (depot / "tests" / "test_ko.py").write_text("def test_ko():\n    assert 1 == 2\n")
    subprocess.run(["git", "add", "."], cwd=depot, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "ko"], cwd=depot, check=True)
    r = lancer_hook("exiger-tests-verts.py", {"cwd": str(depot), "prompt_id": "c", "scratchpad_dir": str(tmp_path)})
    assert r.returncode == 2, r.stderr

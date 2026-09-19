"""Hook Stop — refuse de conclure un tour si du code Python a change et que pytest est rouge.

Regle du depot : « jamais "c'est fait" sans la sortie de pytest ». Ici la regle devient
un fait. Le hook ne tourne que si un .py a change (git), pour ne pas relancer 450 tests
a chaque phrase. Garde anti-boucle : au plus 2 blocages par prompt, puis on laisse passer
en le disant.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

PYTHON = sys.executable  # le meme interpreteur que celui qui lance le hook (Windows local, Linux en CI)
MAX_BLOCAGES = 2

donnees = json.load(sys.stdin)
projet = Path(donnees.get("cwd") or os.getcwd())
prompt_id = str(donnees.get("prompt_id", "sans-id"))
marque = Path(donnees.get("scratchpad_dir") or os.environ.get("TEMP", ".")) / "rita-stop-hook.json"

# 1. Un .py a-t-il change ? Arbre de travail (modifie, ajoute, non suivi) ET commits pas encore
#    pousses. Revue Codex sur la PR #1 (19/09) : ne regarder que l'arbre laissait conclure juste
#    apres un commit, avec des tests rouges deja commites.
def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=projet, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""

changes = git("status", "--porcelain", "--", "*.py").strip()
if not changes:
    amont = git("rev-parse", "--abbrev-ref", "@{u}").strip()
    if amont:
        changes = git("diff", "--name-only", f"{amont}...HEAD", "--", "*.py").strip()
    else:
        # Sans amont, pas de base fiable : on prend tous les commits des dernieres 24 h
        # (revue Codex PR #2 : HEAD~1 seul laissait passer un .py rouge suivi d'un commit de doc).
        changes = git("log", "--since=24.hours", "--name-only", "--pretty=format:", "--", "*.py").strip()
if not changes:
    sys.exit(0)  # pas de depot git, ou rien de Python n'a bouge : rien a verifier

# 2. Garde anti-boucle
etat = {}
try:
    etat = json.loads(marque.read_text(encoding="utf-8"))
except Exception:
    pass
blocages = int(etat.get(prompt_id, 0))
if blocages >= MAX_BLOCAGES:
    print(f"hook exiger-tests-verts : {MAX_BLOCAGES} blocages deja, on laisse conclure "
          "— MAIS les tests sont toujours rouges, a dire a Era.", file=sys.stderr)
    sys.exit(0)

# 3. Les tests
resultat = subprocess.run(
    [PYTHON, "-m", "pytest", "tests", "-q", "-x", "-p", "no:cacheprovider"],
    cwd=projet, capture_output=True, text=True, timeout=540,
)
if resultat.returncode == 0:
    sys.exit(0)

etat[prompt_id] = blocages + 1
try:
    marque.write_text(json.dumps(etat), encoding="utf-8")
except Exception:
    pass
queue = "\n".join(resultat.stdout.strip().splitlines()[-15:])
print("REFUSE par le hook exiger-tests-verts : du code Python a change et pytest est ROUGE.\n"
      "Ne pas conclure. Corriger, relancer, puis coller la sortie.\n" + queue, file=sys.stderr)
sys.exit(2)

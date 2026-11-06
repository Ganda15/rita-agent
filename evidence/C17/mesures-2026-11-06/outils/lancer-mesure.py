"""Lance la mesure Lighthouse et EcoIndex des cinq écrans, dans les conditions du 03/10 (06/11/2026).

Usage : python lancer-mesure.py <racine du dépôt> <dossier de sortie> <dossier où Lighthouse 13.5.0 est installé>

La clé d'API est jetable, tirée au hasard ici, passée par l'environnement et jamais écrite dans un fichier ; le traçage
Langfuse est coupé (leçon d'INC-006) ; l'API est servie en local sur le port 8001 puis arrêtée.
"""
import os
import secrets
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

racine, sortie, lh = (Path(a).resolve() for a in sys.argv[1:4])
cle = secrets.token_hex(16)                     # 32 caractères, jetable
env = dict(os.environ, RITA_API_KEY=cle, LANGFUSE_TRACING_ENABLED="false")
serveur = subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--port", "8001", "--log-level", "warning"],
                           cwd=racine, env=env)
try:
    for _ in range(60):
        try:
            urllib.request.urlopen("http://127.0.0.1:8001/health", timeout=2)
            break
        except OSError:
            time.sleep(1)
    else:
        sys.exit("le serveur de mesure ne répond pas")
    shutil.copy(Path(__file__).with_name("audit-rita.mjs"), lh / "audit-rita.mjs")
    for mode in ("bureau", "mobile"):
        subprocess.run(["node", str(lh / "audit-rita.mjs"), str(sortie), mode], check=True,
                       env=dict(env, LH_CLE=cle, RESULTATS=str(racine / "evidence/C7/resultats-2026-10-03.jsonl")))
finally:
    serveur.terminate()
    serveur.wait(timeout=30)

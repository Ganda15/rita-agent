"""Hook PreToolUse (Edit|Write) - refuse d'ecrire un fichier de secrets.

Un CLAUDE.md qui dit « jamais de secret dans Git » est un conseil.
Ce script est une garantie : il tourne AVANT chaque ecriture, sans exception.
Sortie 2 = ecriture refusee, le message ci-dessous est montre a l'agent.
"""
import json
import sys
from pathlib import PurePath

donnees = json.load(sys.stdin)
chemin = str(donnees.get("tool_input", {}).get("file_path", ""))
nom = PurePath(chemin).name
suffixe = PurePath(chemin).suffix.lower()

interdit = (
    (nom.startswith(".env") and nom != ".env.example")
    or suffixe in {".pem", ".key", ".p12", ".pfx"}
    or nom in {"id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
)

if interdit:
    print(
        f"REFUSE par le hook bloquer-secrets : {chemin}\n"
        "Un fichier de secrets ne s'ecrit jamais par un agent. "
        "Seul .env.example est autorise (modele sans valeur). "
        "Si c'est legitime, Era le fait a la main.",
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)

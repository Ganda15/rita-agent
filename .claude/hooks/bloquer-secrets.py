"""Hook PreToolUse (Edit|Write|Bash) - refuse d'ecrire un fichier de secrets.

Un CLAUDE.md qui dit « jamais de secret dans Git » est un conseil.
Ce script est une garantie : il tourne AVANT chaque ecriture, sans exception.
Sortie 2 = ecriture refusee, le message ci-dessous est montre a l'agent.

v2 (19/09/2026) : couvre aussi l'outil Bash. La v1 ne regardait que Write et Edit ;
une session l'a fait remarquer elle-meme : « je pourrais passer par une commande
shell et le hook ne verrait rien ». Un garde-fou contournable n'est pas un garde-fou.
"""
import json
import re
import sys
from pathlib import PurePath

NOMS_INTERDITS = {"id_rsa", "id_ed25519", "credentials.json", "secrets.json"}
SUFFIXES_INTERDITS = {".pem", ".key", ".p12", ".pfx"}


def fichier_interdit(chemin: str) -> bool:
    nom = PurePath(chemin).name
    return (
        (nom.startswith(".env") and nom != ".env.example")
        or PurePath(chemin).suffix.lower() in SUFFIXES_INTERDITS
        or nom in NOMS_INTERDITS
    )


# Une commande shell qui ECRIT : redirection, tee, cmdlets PowerShell, copie, sed -i.
OPERATEURS_ECRITURE = re.compile(
    r"(>{1,2}|\btee\b|Add-Content|Set-Content|Out-File|Copy-Item|Move-Item|"
    r"\bcp\b|\bmv\b|sed\s+-i|\bcat\s*>)", re.I)
# Un nom de fichier sensible cite dans la commande (.env, .env.local, cle.pem, id_rsa...)
FICHIERS_SENSIBLES = re.compile(
    r"(?<![\w-])(\.env(?:\.[\w-]+)?|[\w.-]+\.(?:pem|key|p12|pfx)|id_rsa|id_ed25519|"
    r"credentials\.json|secrets\.json)(?![\w-])", re.I)

donnees = json.load(sys.stdin)
outil = donnees.get("tool_name", "")
entree = donnees.get("tool_input", {})

if outil in ("Write", "Edit"):
    chemin = str(entree.get("file_path", ""))
    interdit, cible = fichier_interdit(chemin), chemin
else:  # Bash
    commande = str(entree.get("command", ""))
    cibles = [m.group(1) for m in FICHIERS_SENSIBLES.finditer(commande)
              if fichier_interdit(m.group(1))]
    interdit = bool(cibles) and bool(OPERATEURS_ECRITURE.search(commande))
    cible = ", ".join(sorted(set(cibles))) if cibles else commande[:80]

if interdit:
    print(
        f"REFUSE par le hook bloquer-secrets ({outil}) : {cible}\n"
        "Un fichier de secrets ne s'ecrit jamais par un agent, ni par Write/Edit, ni par une "
        "commande shell. Seul .env.example est autorise (modele sans valeur). "
        "Si c'est legitime, Era le fait a la main.",
        file=sys.stderr,
    )
    sys.exit(2)
sys.exit(0)

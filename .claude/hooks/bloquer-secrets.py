"""Hook PreToolUse (tous les outils) - refuse d'ecrire un fichier de secrets.

Un CLAUDE.md qui dit « jamais de secret dans Git » est un conseil.
Ce script est une garantie : il tourne AVANT chaque ecriture, sans exception.
Sortie 2 = ecriture refusee, le message ci-dessous est montre a l'agent.

v4 (19/09/2026, revue Codex sur la PR #1) : un INTERPRETEUR (python -c, node -e...) qui nomme un
fichier sensible est refuse, meme sans operateur shell. `python -c "open('.env','w')"` passait en v3.
v3 (19/09/2026, soir) : tourne sur TOUS les outils (matcher "*"). La v2 ne listait que
Edit|Write|Bash ; une session a ecrit le secret par l'outil PowerShell, absent de la liste.
Lecon : ne jamais enumerer les outils a surveiller, surveiller tout et regarder le contenu.
v2 (19/09/2026) : couvrait aussi l'outil Bash. La v1 ne regardait que Write et Edit ;
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
# Un interpreteur ou une API d'ecriture : s'il nomme un fichier sensible, on presume l'ecriture (v4).
INTERPRETEURS = re.compile(
    r"\b(python3?|py|node|deno|bun|perl|ruby|php|pwsh|powershell)\b|"
    r"open\(|write_text|write_bytes|writeFileSync|writeFile\(|Set-Content|Out-File|\[IO\.File\]", re.I)
# Un nom de fichier sensible cite dans la commande (.env, .env.local, cle.pem, id_rsa...)
FICHIERS_SENSIBLES = re.compile(
    r"(?<![\w-])(\.env(?:\.[\w-]+)?|[\w.-]+\.(?:pem|key|p12|pfx)|id_rsa|id_ed25519|"
    r"credentials\.json|secrets\.json)(?![\w-])", re.I)

donnees = json.load(sys.stdin)
outil = donnees.get("tool_name", "")
entree = donnees.get("tool_input", {})

# Champs qui peuvent porter une commande, quel que soit l'outil (Bash, PowerShell, MCP...)
CHAMPS_COMMANDE = ("command", "cmd", "script", "code", "text")

if outil in ("Write", "Edit", "NotebookEdit"):
    chemin = str(entree.get("file_path") or entree.get("notebook_path") or "")
    interdit, cible = fichier_interdit(chemin), chemin
else:  # tout autre outil : on regarde le contenu, pas le nom de l'outil
    commande = " ".join(str(entree.get(c, "")) for c in CHAMPS_COMMANDE)
    cibles = [m.group(1) for m in FICHIERS_SENSIBLES.finditer(commande)
              if fichier_interdit(m.group(1))]
    interdit = bool(cibles) and bool(OPERATEURS_ECRITURE.search(commande)
                                      or INTERPRETEURS.search(commande))
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

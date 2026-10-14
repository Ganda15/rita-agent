"""Aucun secret déclaré dans le Dockerfile (sprint 2, tâche 3, critère 5 de la grille).

Une instruction `ARG` ou `ENV` dont le nom évoque une clé (KEY, SECRET, TOKEN, PASSWORD, PASS) mettrait un secret
dans l'image ou dans son historique de construction. Le contrôle réunit d'abord les lignes continuées par `\\` :
un `ENV` sur plusieurs lignes peut cacher un nom sur sa deuxième ligne.

Limite, dite telle quelle : il lit les NOMS déclarés, pas les valeurs, et seulement les instructions `ARG` et
`ENV` ; un secret recopié par `COPY` est l'affaire de `.dockerignore` et du contrôle de l'image (`/app/.env`).

Usage : python scripts/verifier_dockerfile.py Dockerfile    (code de sortie 1 si une déclaration est sensible)
"""
from __future__ import annotations

import re
import shlex
import sys
from pathlib import Path

SENSIBLE = re.compile(r"KEY|SECRET|TOKEN|PASSWORD|PASS", re.IGNORECASE)


def _instructions(texte: str) -> list[str]:
    """Les instructions du Dockerfile, une par élément, lignes continuées réunies, commentaires retirés."""
    instructions, courante = [], ""
    for ligne in texte.splitlines():
        if not courante and ligne.lstrip().startswith("#"):
            continue
        if ligne.rstrip().endswith("\\"):
            courante += ligne.rstrip()[:-1] + " "
            continue
        courante += ligne
        if courante.strip():
            instructions.append(courante.strip())
        courante = ""
    if courante.strip():
        instructions.append(courante.strip())
    return instructions


def declarations(texte: str) -> list[str]:
    """Les noms déclarés par chaque `ARG` et chaque `ENV`, dans l'ordre du fichier."""
    noms = []
    for instruction in _instructions(texte):
        mot, _, reste = instruction.partition(" ")
        mot = mot.upper()
        if mot not in ("ARG", "ENV"):
            continue
        jetons = shlex.split(reste, posix=True)
        if mot == "ENV" and jetons and "=" not in jetons[0]:
            noms.append(jetons[0])  # ancienne forme : `ENV NOM valeur avec espaces`
            continue
        noms.extend(jeton.split("=", 1)[0] for jeton in jetons)
    return noms


def declarations_sensibles(texte: str) -> list[str]:
    """Les noms déclarés qui évoquent un secret."""
    return [nom for nom in declarations(texte) if SENSIBLE.search(nom)]


def main(argv: list[str]) -> int:
    chemin = Path(argv[0]) if argv else Path("Dockerfile")
    sensibles = declarations_sensibles(chemin.read_text(encoding="utf-8"))
    for nom in sensibles:
        print(f"::error::{chemin} déclare {nom} par ARG ou ENV : un secret n'a rien à faire dans l'image")
    if not sensibles:
        print(f"{chemin} : aucune déclaration ARG ou ENV sensible")
    return 1 if sensibles else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

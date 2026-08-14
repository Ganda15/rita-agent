#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vérifie TOUS les liens des fichiers Markdown du dépôt — externes et internes.

Pourquoi ce script existe : un livrable de certification part au formateur et au jury.
Un lien mort dans un livrable, c'est un évaluateur qui clique et qui tombe sur une erreur.
Le contrôle ne peut pas dépendre de la mémoire de quelqu'un.

Deux familles de liens, deux pannes différentes :
  - EXTERNE  (http/https) : le site peut disparaître ou déplacer sa page
  - INTERNE  (chemin relatif) : le fichier peut être renommé ou jamais commité
                                -> c'est le piège du 11/08 : `evidence/C4/` était vide

Usage :
    C:\\Python314\\python.exe scripts/verifier_liens.py            # tout le dépôt
    C:\\Python314\\python.exe scripts/verifier_liens.py docs/      # un sous-dossier
    C:\\Python314\\python.exe scripts/verifier_liens.py --internes # sans réseau

Code de sortie : 0 si tout est bon, 1 s'il existe au moins un lien cassé.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# [texte](cible) — on ignore les images ![alt](...) traitées pareil, et les ancres pures (#x)
MOTIF_LIEN = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)>\s]+)>?[^)]*\)")
IGNORES = ("mailto:", "tel:", "#", "javascript:")
DELAI_S = 20
AGENT = "Mozilla/5.0 (verificateur-de-liens RITA)"


def fichiers_markdown(depart: Path) -> list[Path]:
    exclus = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".ruff_cache"}
    return sorted(
        c for c in depart.rglob("*.md")
        if not exclus & set(c.relative_to(RACINE).parts)
    )


def liens_du_fichier(chemin: Path) -> list[tuple[int, str]]:
    """Retourne [(numéro de ligne, cible)] — le numéro sert à retrouver le lien vite."""
    trouves = []
    for n, ligne in enumerate(chemin.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        for cible in MOTIF_LIEN.findall(ligne):
            if not cible.startswith(IGNORES):
                trouves.append((n, cible))
    return trouves


def verifier_interne(source: Path, cible: str) -> str | None:
    """None si le fichier visé existe, sinon le motif de l'échec."""
    chemin = (source.parent / cible.split("#")[0]).resolve()
    if not chemin.exists():
        return "fichier introuvable"
    if not str(chemin).startswith(str(RACINE)):
        # Règle établie le 11/08 : un livrable ne pointe jamais hors du dépôt.
        return "pointe HORS du depot"
    return None


def verifier_externe(url: str) -> str | None:
    import httpx
    try:
        r = httpx.get(url, follow_redirects=True, timeout=DELAI_S,
                      headers={"User-Agent": AGENT})
    except Exception as erreur:
        return f"injoignable ({type(erreur).__name__})"
    return None if r.status_code < 400 else f"HTTP {r.status_code}"


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sans_reseau = "--internes" in sys.argv
    depart = (RACINE / args[0]).resolve() if args else RACINE

    fichiers = fichiers_markdown(depart)
    casses: list[str] = []
    n_ext = n_int = 0

    print(f"Verification des liens — {len(fichiers)} fichiers Markdown sous {depart}\n")

    for fichier in fichiers:
        relatif = fichier.relative_to(RACINE)
        for ligne, cible in liens_du_fichier(fichier):
            if cible.startswith(("http://", "https://")):
                if sans_reseau:
                    continue
                n_ext += 1
                probleme = verifier_externe(cible)
            else:
                n_int += 1
                probleme = verifier_interne(fichier, cible)

            if probleme:
                casses.append(f"{relatif}:{ligne}  {probleme}\n      -> {cible}")
                print(f"  CASSE  {relatif}:{ligne}  {probleme}")

    print(f"\n{'-' * 60}")
    print(f"Liens internes verifies : {n_int}")
    print(f"Liens externes verifies : {n_ext}" + ("  (ignores : --internes)" if sans_reseau else ""))
    print(f"Liens casses            : {len(casses)}")

    if casses:
        print("\nDETAIL :")
        for c in casses:
            print(f"  - {c}")
        return 1

    print("\nAucun lien casse.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

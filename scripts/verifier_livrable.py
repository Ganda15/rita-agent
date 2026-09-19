#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Definition of Done d'un livrable RITA — le verdict est GENERE, jamais ecrit (C13).

Pourquoi ce script existe : jusqu'au 19/09/2026, la chaine de livraison (`livraison.yml`)
ne lancait que `pytest -q` sur un tag. Ni la couverture, ni les portes d'evaluation, ni les
liens n'etaient verifies au moment precis ou l'image partait. Un tag pose sur un commit
non teste aurait publie quand meme. La checklist existait dans `docs/FILE-DE-VALIDATION.md`,
mais une checklist se saute ; un script qui renvoie 1 ne se saute pas.

Cinq verifications, une ligne chacune, ✅ ou ❌ calcule depuis le code de sortie :
  1. tests + couverture (le seuil `fail_under = 90` vit dans `.coveragerc`)
  2. portes d'evaluation des garde-fous (`tests/test_evals.py`)
  3. liens internes (`scripts/verifier_liens.py --internes`, sans reseau)
  4. le tag est cite dans `ETAT.md` et `CHANGELOG.md` (un livrable non consigne n'existe pas)
  5. arbre git propre — le tag doit designer exactement le code verifie (saute en CI : `--ci`)

Usage :
    C:/Python314/python.exe scripts/verifier_livrable.py livrable-E4-v1     # avant de poser le tag
    python scripts/verifier_livrable.py --ci                                    # dans livraison.yml

Code de sortie : 0 si tout est vert, 1 sinon.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

RACINE = Path(__file__).resolve().parent.parent
PYTHON = sys.executable
Controle = Callable[[], tuple[bool, str]]


@dataclass
class Verification:
    nom: str
    commande: list[str] | Controle   # une commande a lancer, ou une fonction (ok, detail)
    cwd: Path = field(default_factory=lambda: RACINE)


@dataclass
class Resultat:
    nom: str
    ok: bool
    detail: str


def lancer(v: Verification) -> Resultat:
    if callable(v.commande):
        ok, detail = v.commande()
        return Resultat(v.nom, ok, detail)
    p = subprocess.run(v.commande, cwd=v.cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    lignes = [l.strip() for l in (p.stdout + p.stderr).splitlines() if l.strip()] or [""]
    bilan = [l for l in lignes if re.search(r"\d+ (passed|failed|error)", l)]
    detail = bilan[-1] if bilan else (lignes[-1] if p.returncode == 0 else " / ".join(lignes[-4:]))
    return Resultat(v.nom, p.returncode == 0, detail)


def executer(verifications: list[Verification]) -> list[Resultat]:
    return [lancer(v) for v in verifications]


def verdict(resultats: list[Resultat]) -> bool:
    return all(r.ok for r in resultats)


def tableau(resultats: list[Resultat]) -> str:
    lignes = ["| | Vérification | Détail |", "|---|---|---|"]
    for r in resultats:
        lignes.append(f"| {'✅' if r.ok else '❌'} | {r.nom} | {r.detail[:160]} |")
    return "\n".join(lignes)


def tag_cite(tag: str, fichiers: list[Path]) -> tuple[bool, str]:
    manquants = [f.name for f in fichiers
                 if tag not in f.read_text(encoding="utf-8", errors="replace")]
    return (not manquants, "cité partout" if not manquants else "absent de : " + ", ".join(manquants))


def arbre_propre(depot: Path) -> tuple[bool, str]:
    p = subprocess.run(["git", "status", "--porcelain"], cwd=depot, capture_output=True, text=True)
    sale = [l for l in p.stdout.splitlines() if l.strip()]
    return (not sale, "propre" if not sale else "non commité : " + ", ".join(l[3:] for l in sale[:5]))


def verifications_du_depot(tag: str | None, ci: bool) -> list[Verification]:
    vs = [
        Verification("Tests + couverture ≥ 90 % (.coveragerc)",
                     [PYTHON, "-m", "pytest", "tests", "-q", "--cov", "-p", "no:cacheprovider"]),
        Verification("Portes d'évaluation des garde-fous (tests/test_evals.py)",
                     [PYTHON, "-m", "pytest", "tests/test_evals.py", "-q", "-p", "no:cacheprovider"]),
        Verification("Liens internes (verifier_liens.py --internes)",
                     [PYTHON, str(RACINE / "scripts" / "verifier_liens.py"), "--internes"]),
    ]
    if tag and tag.startswith("livrable-"):
        vs.append(Verification(f"Tag {tag} cité dans ETAT.md et CHANGELOG.md",
                               lambda: tag_cite(tag, [RACINE / "ETAT.md", RACINE / "CHANGELOG.md"])))
    if not ci:
        vs.append(Verification("Arbre git propre (le tag = le code vérifié)",
                               lambda: arbre_propre(RACINE)))
    return vs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("tag", nargs="?", default=os.environ.get("GITHUB_REF_NAME"),
                        help="nom du tag (livrable-E<n>-v<k>) ; en CI, lu dans GITHUB_REF_NAME")
    parser.add_argument("--ci", action="store_true", help="en CI : l'arbre est toujours propre, on saute ce contrôle")
    args = parser.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    resultats = executer(verifications_du_depot(args.tag, args.ci))
    print(f"=== DEFINITION OF DONE — {args.tag or 'sans tag (branche)'} ===")
    print(tableau(resultats))
    ok = verdict(resultats)
    print("\nVERDICT :", "✅ livrable" if ok else "❌ PAS livrable — corriger les lignes rouges")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

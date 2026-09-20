"""Importe un rapport de scan Giskard dans le banc de garde-fous — C10, C12, C17, C21.

Pourquoi : `evals/cas.py` compte 10 attaques écrites à la main. Le scan Giskard
(`evals/scan_giskard.py`, lancé en CI par `.github/workflows/scan-giskard.yml`) en génère
des centaines, adaptées à la description de RITA, classées sur l'OWASP LLM Top 10, et jugées
par un modèle. Ce module en fait un fichier de cas **séparé**, `evals/cas_giskard.py`, sans
jamais toucher à `cas.py` : le taux de blocage historique reste comparable, et la provenance
de chaque attaque est écrite.

Structure lue (giskard-checks 1.0.4, `core/result.py`, `core/interaction/`) :
SuiteResult.results[] → ScenarioResult{scenario_name, tags[], steps[].results[].status,
final_trace.interactions[]{inputs, outputs}}. Un check `failed` = l'agent n'a PAS refusé =
l'attaque est passée (`contournee`).

Usage :
    C:/Python314/python.exe -m evals.importer_giskard rapport-giskard.json --sortie evals/cas_giskard.py
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Attaque:
    texte: str
    categorie: str        # ex. "prompt-injection" (tag threat-type:…)
    owasp: str            # ex. "LLM01" (tag owasp:llm-top-10-2025:…), "" si absent
    scenario: str
    contournee: bool      # True si un check a échoué : le garde-fou n'a pas refusé


def _texte(entree: Any) -> str:
    """Ramène une entrée d'interaction à son texte : `str`, ou message structuré {content}."""
    if isinstance(entree, str):
        return entree.strip()
    if isinstance(entree, dict):
        for cle in ("content", "text", "message", "input"):
            if isinstance(entree.get(cle), str):
                return entree[cle].strip()
    if isinstance(entree, list) and entree:
        return _texte(entree[-1])
    return ""


def _tag(tags: list[str], prefixe: str) -> str:
    for t in tags or []:
        if t.startswith(prefixe):
            return t.split(":")[-1]
    return ""


def extraire_attaques(rapport: dict) -> list[Attaque]:
    """Une attaque par tour de conversation, dédoublonnée sur le texte.

    Si le même texte apparaît dans plusieurs scénarios, il est marqué `contournee` dès qu'un
    seul l'a fait passer : c'est l'information la plus utile, pas la plus flatteuse.
    """
    vues: dict[str, Attaque] = {}
    for sc in rapport.get("results") or []:
        tags = sc.get("tags") or []
        categorie = _tag(tags, "threat-type:")
        owasp = _tag(tags, "owasp:")
        statuts = [r.get("status") for etape in sc.get("steps") or [] for r in etape.get("results") or []]
        contournee = any(s == "failed" for s in statuts)
        for inter in (sc.get("final_trace") or {}).get("interactions") or []:
            texte = _texte(inter.get("inputs"))
            if not texte:
                continue
            deja = vues.get(texte)
            if deja is None or (contournee and not deja.contournee):
                vues[texte] = Attaque(texte, categorie, owasp, sc.get("scenario_name", ""), contournee)
    return list(vues.values())


def resumer(attaques: list[Attaque]) -> dict[str, dict[str, int]]:
    """Comptes par catégorie : total et passées. C'est le tableau de la preuve."""
    resume: dict[str, dict[str, int]] = {}
    for a in attaques:
        r = resume.setdefault(a.categorie or "sans-categorie", {"total": 0, "contournees": 0})
        r["total"] += 1
        r["contournees"] += int(a.contournee)
    return resume


def ecrire_cas(attaques: list[Attaque], sortie: Path, source: str) -> None:
    """Écrit un module Python importable : `ATTAQUES_GISKARD`, trié, avec sa provenance."""
    tri = sorted(attaques, key=lambda a: (a.categorie, a.texte))
    lignes = [
        '"""Attaques générées par le scan Giskard — fichier ÉCRIT PAR evals/importer_giskard.py, ne pas éditer.',
        "",
        f"Source : {source}",
        f"Attaques : {len(tri)} · passées (garde-fou contourné) : {sum(a.contournee for a in tri)}",
        "Les attaques passées sont des incidents (C21) : chacune doit finir par un test rouge, un correctif, un commit.",
        '"""',
        "",
        "ATTAQUES_GISKARD = [",
    ]
    for a in tri:
        # `repr` et non `json.dumps` : le fichier est du PYTHON (True/False, pas true/false) — le test
        # « importable » l'a attrapé avant que quiconque n'importe un fichier invalide.
        lignes.append("    " + repr({"texte": a.texte, "categorie": a.categorie, "owasp": a.owasp,
                                     "scenario": a.scenario, "contournee": a.contournee}) + ",")
    lignes += ["]", "", "INJECTIONS_GISKARD = [a['texte'] for a in ATTAQUES_GISKARD]", ""]
    sortie.write_text("\n".join(lignes), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parseur.add_argument("rapport", help="JSON produit par evals/scan_giskard.py")
    parseur.add_argument("--sortie", default="evals/cas_giskard.py")
    args = parseur.parse_args(argv)
    rapport = json.loads(Path(args.rapport).read_text(encoding="utf-8"))
    attaques = extraire_attaques(rapport)
    ecrire_cas(attaques, Path(args.sortie), source=Path(args.rapport).name)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(f"{len(attaques)} attaques → {args.sortie}")
    print("| Catégorie | Attaques | Passées |")
    print("|---|---|---|")
    for cat, c in sorted(resumer(attaques).items()):
        print(f"| {cat} | {c['total']} | {c['contournees']} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Les deux garde-fous d'ENTRÉE, mesurés séparément, sur les questions telles quelles et masquées (S9, 07/11/2026).

Demande d'Era (07/11) : mesurer séparément l'intention interdite (`guardrails/entree.py`) et le détournement
(`guardrails/detournement.py`), avec les 17 questions légitimes du jeu v3, avant et après la normalisation commune.
Les masques sont ceux des tests (`tests/test_caracteres_invisibles.py`) : largeur nulle dans et entre les mots, trait
d'union conditionnel, contrôle bidirectionnel, pleine chasse.

Usage, depuis la racine du dépôt :
    C:\\Python314\\python.exe -X utf8 evidence/C17/s9-2026-11-07/mesurer_entree_masquee.py [--racine DOSSIER]

--racine : l'arbre dont on importe le code (par défaut ce dépôt) ; un arbre de travail Git séparé pour une version
passée.
"""
import argparse
import datetime
import subprocess
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[3]


def version(racine: Path) -> str:
    git = ["git", "-c", f"safe.directory={racine.as_posix()}", "-C", str(racine)]
    tete = subprocess.run(git + ["rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    sale = subprocess.run(git + ["status", "--porcelain", "--", "guardrails"], capture_output=True, text=True)
    if tete.returncode or sale.returncode:
        return "version inconnue (git : " + (tete.stderr or sale.stderr).strip().splitlines()[0] + ")"
    return tete.stdout.strip() + (" (guardrails/ modifiés, non commités)" if sale.stdout.strip()
                                  else " (guardrails/ identique au commit)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--racine", type=Path, default=DEPOT)
    racine = parser.parse_args().racine.resolve()
    sys.path.insert(0, str(racine))
    from evals.cas import INTENTIONS_INTERDITES, INTENTIONS_LEGITIMES
    from guardrails.detournement import verifier_detournement
    from guardrails.entree import verifier_intention
    from rag.controle_questions import MOTIFS_DE_SECURITE, charger_jeu
    from tests.test_caracteres_invisibles import MASQUES

    # Mêmes listes que `evals/mesurer_entree.py` : attaques H1 à H6, et les 17 questions légitimes (L, V, et Q sauf
    # celles qui demandent un conseil).
    jeu = {q["id"]: q for q in charger_jeu()["questions"]}
    attaques = [jeu[f"H{n}"]["question"] for n in range(1, 7)]
    legitimes = [q["question"] for i, q in jeu.items()
                 if i[0] in "LV" or (i[0] == "Q" and q.get("motif_attendu") not in MOTIFS_DE_SECURITE)]

    print(f"# Garde-fous d'entrée, mesurés séparément, {datetime.datetime.now():%d/%m/%Y %H:%M}")
    print(f"Code mesuré : {version(racine)}")
    print(f"Jeux : {len(INTENTIONS_INTERDITES)} intentions interdites (evals/cas.py), {len(attaques)} attaques H1 à H6, "
          f"{len(legitimes)} questions légitimes du jeu v3, {len(INTENTIONS_LEGITIMES)} intentions légitimes")
    print()
    formes = {"telle quelle": lambda t: t, **MASQUES}
    print(f"{'forme':30} {'intention bloquée':>18} {'détournement bloqué':>20} "
          f"{'fp intention /17':>17} {'fp détournement /17':>20} {'fp intention /5':>16}")
    for nom, masque in formes.items():
        intention = sum(verifier_intention(masque(t))["bloque"] for t in INTENTIONS_INTERDITES)
        detournement = sum(verifier_detournement(masque(t))["bloque"] for t in attaques)
        fp_intention = sum(verifier_intention(masque(t))["bloque"] for t in legitimes)
        fp_detournement = sum(verifier_detournement(masque(t))["bloque"] for t in legitimes)
        fp_intention_5 = sum(verifier_intention(masque(t))["bloque"] for t in INTENTIONS_LEGITIMES)
        print(f"{nom:30} {f'{intention} sur {len(INTENTIONS_INTERDITES)}':>18} {f'{detournement} sur {len(attaques)}':>20} "
              f"{fp_intention:>17} {fp_detournement:>20} {fp_intention_5:>16}")


if __name__ == "__main__":
    main()

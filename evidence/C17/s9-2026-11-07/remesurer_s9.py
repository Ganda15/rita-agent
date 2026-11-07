"""Remesure complète du constat S9 sur le code courant (07/11/2026), chaque nombre calculé, aucun recopié.

Pourquoi : la normalisation des espaces (commit 9525bbc) est venue APRÈS les mesures « après correction » du jour.
Et dans `mesure-apres-correction-sortie-amf.txt`, la ligne des 230 briefings était une phrase écrite à la main, non
calculée par le script. Ce script recalcule tout : jeux S9, ancien jeu AMF, passages réels, briefings réels.

Usage, depuis la racine du dépôt :
    C:\\Python314\\python.exe -X utf8 evidence/C17/s9-2026-11-07/remesurer_s9.py
"""
import datetime
import glob
import json
import subprocess
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(DEPOT))

from evals.cas import SORTIES_INTERDITES, SORTIES_LEGITIMES  # noqa: E402
from evals.cas_s9_reserves_sortie import SORTIES_INTERDITES_RESERVEES, SORTIES_LEGITIMES_RESERVEES  # noqa: E402
from evals.mesurer_s9 import CONSIGNES_DES_PARCOURS, mesurer, s9_ferme  # noqa: E402
from guardrails.injection import neutraliser  # noqa: E402
from guardrails.sortie import verifier_fuite, verifier_sortie  # noqa: E402


def commit() -> str:
    tete = subprocess.run(["git", "-C", str(DEPOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    sale = subprocess.run(["git", "-C", str(DEPOT), "status", "--porcelain", "--", "guardrails", "evals"],
                          capture_output=True, text=True)
    return tete.stdout.strip() + (" (guardrails/ ou evals/ modifiés, non commités)" if sale.stdout.strip()
                                  else " (guardrails/ et evals/ identiques au commit)")


def main() -> None:
    print(f"# Remesure S9, {datetime.datetime.now(datetime.UTC):%Y-%m-%dT%H:%M:%SZ}, code {commit()}")
    print("## Injection et fuite (evals.mesurer_s9)")
    r = mesurer()
    for nom, m in r.items():
        print(f"{nom:18} blocage {m['blocage']:5.1f} % sur {m['n'][0]:2} | "
              f"faux positifs {m['faux_positifs']:5.1f} % sur {m['n'][1]:2}")
    print(f"Seuils atteints sur le jeu tenu à l'écart, injection et fuite (>= 85 % de blocage, <= 15 % de faux "
          f"positifs) : {s9_ferme(r)}. Ce n'est pas la clôture de S9, qui attend la relecture et la décision d'Era.")

    print("## Sortie AMF (verifier_sortie)")
    for nom, interdites, legitimes in (("ancien jeu", SORTIES_INTERDITES, SORTIES_LEGITIMES),
                                       ("jeu tenu à l'écart", SORTIES_INTERDITES_RESERVEES,
                                        SORTIES_LEGITIMES_RESERVEES)):
        bloquees = sum(1 for t in interdites if not verifier_sortie(t)["conforme"])
        a_tort = sum(1 for t in legitimes if not verifier_sortie(t)["conforme"])
        print(f"{nom:20} interdites bloquées {bloquees} sur {len(interdites)} ; "
              f"légitimes refusées à tort {a_tort} sur {len(legitimes)}")

    print("## Textes réels")
    # Seconde relecture du 07/11 : compter aussi les textes DISTINCTS, les deux versions du jeu portant les mêmes passages.
    n = bloques = 0
    distincts_passages: set[str] = set()
    for f in ("evidence/C7/jeu-d-essai-2026-10-03.json", "evidence/C7/jeu-d-essai-2026-10-03-v1-sans-indicateurs.json"):
        for cas in json.loads((DEPOT / f).read_text(encoding="utf-8"))["cas"]:
            for p in cas.get("passages") or []:
                n += 1
                texte = p.get("texte") or json.dumps(p, ensure_ascii=False)
                distincts_passages.add(texte)
                bloques += neutraliser(texte, "eval")["bloque"]
    print(f"passages d'articles du jeu figé du banc : {bloques} bloqués par l'injection sur {n} occurrences "
          f"({len(distincts_passages)} textes distincts)")

    fichiers = sorted(set(glob.glob(str(DEPOT / "evidence/C7/**/resultats-*.jsonl"), recursive=True)))
    lignes = textes = amf = fuite = 0
    distincts_briefings: set[str] = set()
    for f in fichiers:
        for ligne in Path(f).read_text(encoding="utf-8").splitlines():
            if not ligne.strip():
                continue
            lignes += 1
            texte = json.loads(ligne).get("texte") or ""
            if not texte.strip():
                continue
            textes += 1
            distincts_briefings.add(texte)
            amf += not verifier_sortie(texte)["conforme"]
            fuite += not verifier_fuite(texte, CONSIGNES_DES_PARCOURS)["conforme"]
    print(f"briefings des bancs ({len(fichiers)} fichiers resultats-*.jsonl, {lignes} lignes, {textes} avec un texte, "
          f"{len(distincts_briefings)} textes distincts) : "
          f"{amf} refusés par la sortie AMF, {fuite} par le contrôle de fuite (consignes des parcours comprises)")


if __name__ == "__main__":
    main()

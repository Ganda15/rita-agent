"""Mesure le garde-fou d'injection : taux de blocage ET taux de faux positifs.

« La solidité d'un garde-fou se mesure par les évals, pas par la lecture du code.
Un garde-fou non mesuré est une intention, pas une protection. » (Velmo 2.0, point 6)

Usage : python -m evals.mesurer_gardefou
"""
import time

from evals.cas import INJECTIONS, LEGITIMES
from guardrails.injection import neutraliser


def mesurer() -> dict:
    debut = time.perf_counter()

    bloquees = [t for t in INJECTIONS if neutraliser(t, "eval")["bloque"]]
    faux_positifs = [t for t in LEGITIMES if neutraliser(t, "eval")["bloque"]]

    duree_ms = (time.perf_counter() - debut) * 1000
    n_appels = len(INJECTIONS) + len(LEGITIMES)

    return {
        "taux_blocage": len(bloquees) / len(INJECTIONS) * 100,
        "taux_faux_positifs": len(faux_positifs) / len(LEGITIMES) * 100,
        "injections_ratees": [t for t in INJECTIONS if not neutraliser(t, "eval")["bloque"]],
        "faux_positifs": faux_positifs,
        "latence_moyenne_ms": duree_ms / n_appels,
    }


if __name__ == "__main__":
    r = mesurer()
    print("=== MESURE DU GARDE-FOU D'INJECTION ===")
    print(f"Taux de blocage      : {r['taux_blocage']:.1f} %  ({len(INJECTIONS)} cas malveillants)")
    print(f"Taux de faux positifs: {r['taux_faux_positifs']:.1f} %  ({len(LEGITIMES)} cas legitimes)")
    print(f"Latence moyenne      : {r['latence_moyenne_ms']:.3f} ms  (budget : 250 ms)")
    if r["injections_ratees"]:
        print("\nINJECTIONS NON DETECTEES :")
        for t in r["injections_ratees"]:
            print(f"  - {t}")
    if r["faux_positifs"]:
        print("\nFAUX POSITIFS :")
        for t in r["faux_positifs"]:
            print(f"  - {t}")

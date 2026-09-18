"""Mesure le garde-fou d'ENTREE : taux de blocage ET taux de faux positifs.

« La solidité d'un garde-fou se mesure par les évals, pas par la lecture du code.
Un garde-fou non mesuré est une intention, pas une protection. » (Velmo 2.0, point 6)

Usage : python -m evals.mesurer_entree
"""
import time

from evals.cas import INTENTIONS_INTERDITES, INTENTIONS_LEGITIMES
from guardrails.entree import verifier_intention


def mesurer() -> dict:
    debut = time.perf_counter()

    bloquees = [q for q in INTENTIONS_INTERDITES if verifier_intention(q)["bloque"]]
    faux_positifs = [q for q in INTENTIONS_LEGITIMES if verifier_intention(q)["bloque"]]

    duree_ms = (time.perf_counter() - debut) * 1000
    n_appels = len(INTENTIONS_INTERDITES) + len(INTENTIONS_LEGITIMES)

    return {
        "taux_blocage": len(bloquees) / len(INTENTIONS_INTERDITES) * 100,
        "taux_faux_positifs": len(faux_positifs) / len(INTENTIONS_LEGITIMES) * 100,
        "intentions_ratees": [q for q in INTENTIONS_INTERDITES
                               if not verifier_intention(q)["bloque"]],
        "faux_positifs": faux_positifs,
        "latence_moyenne_ms": duree_ms / n_appels,
    }


if __name__ == "__main__":
    r = mesurer()
    print("=== MESURE DU GARDE-FOU D'ENTREE (intention AMF) ===")
    print(f"Taux de blocage      : {r['taux_blocage']:.1f} %  "
          f"({len(INTENTIONS_INTERDITES)} cas a intention interdite)")
    print(f"Taux de faux positifs: {r['taux_faux_positifs']:.1f} %  "
          f"({len(INTENTIONS_LEGITIMES)} cas legitimes)")
    print(f"Latence moyenne      : {r['latence_moyenne_ms']:.3f} ms  (budget : 250 ms)")
    if r["intentions_ratees"]:
        print("\nINTENTIONS NON DETECTEES :")
        for q in r["intentions_ratees"]:
            print(f"  - {q}")
    if r["faux_positifs"]:
        print("\nFAUX POSITIFS :")
        for q in r["faux_positifs"]:
            print(f"  - {q}")

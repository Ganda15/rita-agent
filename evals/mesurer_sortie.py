"""Mesure le garde-fou de SORTIE : taux de blocage ET taux de faux positifs.

Même règle que `mesurer_gardefou.py` : les deux chiffres, toujours ensemble. Refuser tout
donnerait 100 % de blocage et un service inutilisable.

⚠️ **Ce que ce chiffre vaut, et ce qu'il ne vaut pas.** Trois des dix cas interdits ont été
écrits APRÈS les motifs et CONTRE eux. Ils passent. Le taux affiché est donc **une mesure
honnête, pas un score flatteur** : un jeu de cas construit à partir des motifs qu'il teste
rend toujours 100 %, et ce 100 % ne mesure rien (leçon de la veille S34).

Usage : python -m evals.mesurer_sortie
"""
import time

from agents.analyst import CONSIGNES_REDACTION, ROLE_REDACTEUR
from agents.question import CONSIGNES
from evals.cas import SORTIES_FUITE, SORTIES_INTERDITES, SORTIES_LEGITIMES, SORTIES_LEGITIMES_FUITE
from guardrails.sortie import verifier_fuite, verifier_sortie


def mesurer() -> dict:
    debut = time.perf_counter()

    bloquees = [t for t in SORTIES_INTERDITES if not verifier_sortie(t)["conforme"]]
    faux_positifs = [t for t in SORTIES_LEGITIMES if not verifier_sortie(t)["conforme"]]

    duree_ms = (time.perf_counter() - debut) * 1000
    n_appels = len(SORTIES_INTERDITES) + len(SORTIES_LEGITIMES)

    return {
        "taux_blocage": len(bloquees) / len(SORTIES_INTERDITES) * 100,
        "taux_faux_positifs": len(faux_positifs) / len(SORTIES_LEGITIMES) * 100,
        "sorties_ratees": [t for t in SORTIES_INTERDITES
                           if verifier_sortie(t)["conforme"]],
        "faux_positifs": faux_positifs,
        "latence_moyenne_ms": duree_ms / n_appels,
    }


def mesurer_fuite() -> dict:
    """Le contrôle de fuite (sprint 4, tâche B2) : blocage sur les sorties qui divulguent, faux positifs sur les
    sorties légitimes, y compris celles qui parlent d'une fuite ou d'une « clé » dans un sens factuel. Les consignes
    cherchées sont celles des deux parcours."""
    consignes = (CONSIGNES, ROLE_REDACTEUR, CONSIGNES_REDACTION)
    legitimes = SORTIES_LEGITIMES + SORTIES_LEGITIMES_FUITE
    debut = time.perf_counter()
    ratees = [t for t in SORTIES_FUITE if verifier_fuite(t, consignes)["conforme"]]
    faux_positifs = [t for t in legitimes if not verifier_fuite(t, consignes)["conforme"]]
    duree_ms = (time.perf_counter() - debut) * 1000
    return {
        "taux_blocage": (len(SORTIES_FUITE) - len(ratees)) / len(SORTIES_FUITE) * 100,
        "taux_faux_positifs": len(faux_positifs) / len(legitimes) * 100,
        "fuites_ratees": ratees,
        "faux_positifs": faux_positifs,
        "latence_moyenne_ms": duree_ms / (len(SORTIES_FUITE) + len(legitimes)),
    }


if __name__ == "__main__":
    r = mesurer()
    print("=== MESURE DU GARDE-FOU DE SORTIE (interdit AMF) ===")
    print(f"Taux de blocage      : {r['taux_blocage']:.1f} %  "
          f"({len(SORTIES_INTERDITES)} sorties interdites)")
    print(f"Taux de faux positifs: {r['taux_faux_positifs']:.1f} %  "
          f"({len(SORTIES_LEGITIMES)} sorties legitimes)")
    print(f"Latence moyenne      : {r['latence_moyenne_ms']:.3f} ms")
    if r["sorties_ratees"]:
        print("\nSORTIES INTERDITES NON DETECTEES :")
        for t in r["sorties_ratees"]:
            print(f"  - {t}")
    if r["faux_positifs"]:
        print("\nFAUX POSITIFS :")
        for t in r["faux_positifs"]:
            print(f"  - {t}")

    f = mesurer_fuite()
    print("\n=== MESURE DU CONTROLE DE FUITE (secrets, configuration, consignes) ===")
    print(f"Taux de blocage      : {f['taux_blocage']:.1f} %  ({len(SORTIES_FUITE)} sorties qui divulguent, "
          f"dont 2 hors echantillon)")
    print(f"Taux de faux positifs: {f['taux_faux_positifs']:.1f} %  "
          f"({len(SORTIES_LEGITIMES) + len(SORTIES_LEGITIMES_FUITE)} sorties legitimes)")
    print(f"Latence moyenne      : {f['latence_moyenne_ms']:.3f} ms")
    for titre, liste in (("FUITES NON DETECTEES", f["fuites_ratees"]), ("FAUX POSITIFS", f["faux_positifs"])):
        if liste:
            print(f"\n{titre} :")
            for t in liste:
                print(f"  - {t}")

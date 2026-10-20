"""Mesure les garde-fous d'ENTREE : taux de blocage ET taux de faux positifs.

« La solidité d'un garde-fou se mesure par les évals, pas par la lecture du code.
Un garde-fou non mesuré est une intention, pas une protection. » (Velmo 2.0, point 6)

Deux garde-fous : l'intention AMF (`mesurer`) et, depuis le sprint 4, le détournement (`mesurer_detournement`).

Usage : python -m evals.mesurer_entree
"""
import time

from evals.cas import INTENTIONS_INTERDITES, INTENTIONS_LEGITIMES, REFORMULATIONS_RESERVEES
from guardrails.detournement import verifier_detournement
from guardrails.entree import verifier_intention
from rag.controle_questions import MOTIFS_DE_SECURITE, charger_jeu

# Les attaques du jeu v3. H7 et H8 sont hors périmètre (un poème, une capitale) : c'est la recherche qui les refuse,
# pas un garde-fou ; le rejeu de la livraison les contrôle (rag/controle_questions.py).
ATTAQUES = [f"H{n}" for n in range(1, 7)]


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


def _arretee(texte: str) -> bool:
    """Arrêtée par la chaîne des garde-fous d'entrée : le détournement, puis l'intention AMF."""
    return verifier_detournement(texte)["bloque"] or verifier_intention(texte)["bloque"]


def mesurer_detournement() -> dict:
    """Le garde-fou de détournement, sur les textes du jeu v3, sans corpus ni modèle (sprint 4, tâche A5).

    Les deux chiffres sont ceux du garde-fou seul : blocage sur les attaques H1 à H6, faux positifs sur les questions
    légitimes (L, V, et Q sauf Q8, qui demande un conseil). Les deux listes, elles, regardent toute la chaîne d'entrée,
    détournement puis intention : ce sont elles que les portes de la CI exigent vides (tests/test_evals.py). Les
    reformulations réservées sont comptées pour le garde-fou seul, sans seuil.
    """
    jeu = {q["id"]: q for q in charger_jeu()["questions"]}
    attaques = [jeu[identifiant]["question"] for identifiant in ATTAQUES]
    legitimes = [q["question"] for identifiant, q in jeu.items()
                 if identifiant[0] in "LV" or (identifiant[0] == "Q" and q.get("motif_attendu") not in MOTIFS_DE_SECURITE)]
    reformulations = [r["texte"] for r in REFORMULATIONS_RESERVEES]

    debut = time.perf_counter()
    bloquees = [t for t in attaques if verifier_detournement(t)["bloque"]]
    faux_positifs_seul = [t for t in legitimes if verifier_detournement(t)["bloque"]]
    reconnues = [t for t in reformulations if verifier_detournement(t)["bloque"]]
    duree_ms = (time.perf_counter() - debut) * 1000

    return {
        "nb_attaques": len(attaques),
        "nb_legitimes": len(legitimes),
        "taux_blocage": len(bloquees) / len(attaques) * 100,
        "taux_faux_positifs": len(faux_positifs_seul) / len(legitimes) * 100,
        "attaques_ratees": [t for t in attaques if not _arretee(t)],
        "faux_positifs": [t for t in legitimes if _arretee(t)],
        "reformulations_reconnues": f"{len(reconnues)}/{len(reformulations)}",
        "latence_moyenne_ms": duree_ms / (len(attaques) + len(legitimes) + len(reformulations)),
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

    d = mesurer_detournement()
    print("\n=== MESURE DU GARDE-FOU DE DETOURNEMENT (injection, extraction) ===")
    print(f"Taux de blocage      : {d['taux_blocage']:.1f} %  ({d['nb_attaques']} attaques du jeu v3, H1 a H6)")
    print(f"Taux de faux positifs: {d['taux_faux_positifs']:.1f} %  ({d['nb_legitimes']} questions legitimes)")
    print(f"Reformulations       : {d['reformulations_reconnues']} reconnues par le garde-fou seul (mesure, sans seuil)")
    print(f"Latence moyenne      : {d['latence_moyenne_ms']:.3f} ms  (budget : 250 ms)")
    for titre, liste in (("ATTAQUES NON ARRETEES", d["attaques_ratees"]), ("FAUX POSITIFS", d["faux_positifs"])):
        if liste:
            print(f"\n{titre} :")
            for q in liste:
                print(f"  - {q}")

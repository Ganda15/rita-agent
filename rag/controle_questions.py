"""Le jeu de questions de démonstration et son rejeu (sprint 3, tâche B2 ; spec CA6.1 à CA6.5 et CA3.6).

Le jeu (`rag/questions_demo.json`) reprend le § 5 de la spec, en version 2. Le rejeu le repasse sur un index **sans
appel au modèle** : il ne contrôle que la recherche, c'est-à-dire ce qu'un nouvel index change.

Les règles :
- `refus` attendu : la recherche ne retient rien, avec le motif attendu (`OUT_OF_CORPUS`, `INTENTION_INTERDITE`).
  Sinon, écart bloquant.
- `reponse` attendue : au moins un des passages rendus est une source validée. Sinon, écart bloquant (« aucun passage
  justificatif validé »). L'ordre entre sources validées ne compte pas : un changement de classement n'est pas un écart.
- `reponse_ou_abstention` (Q3) : le même contrôle, noté sans bloquer.
Les passages rendus hors des sources validées sont listés dans le rapport, pour vérification.

`python -m rag.controle_questions --sortie <fichier>` écrit le rapport JSON dans le fichier demandé (écarts, passages
rendus par question, identité de l'index sous la clé `index`, comme `/health`) et un résumé sur la sortie standard.
Code 1 si un écart bloque, si l'index n'a pas d'identité ou si le rapport ne peut pas être écrit ; 0 sinon. Le script
du serveur (`deploy/deployer.py`, tâche B3) lance ce module avant toute mise en service d'un index, et lit `index`.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from rag.indexation import lire_identite
from rag.recherche import rechercher

JEU = Path(__file__).with_name("questions_demo.json")
ATTENDUS = {"reponse", "reponse_ou_abstention", "refus"}
K = 3   # le même nombre de passages que le parcours des questions (agents/question.py, `repondre`)


@dataclass(frozen=True)
class Ecart:
    id: str
    bloquant: bool
    message: str


def charger_jeu(chemin: Path = JEU) -> dict:
    """Lit le jeu et vérifie sa forme ; `ValueError` au premier défaut. Un jeu mal formé ne doit jamais passer pour un
    rejeu réussi."""
    jeu = json.loads(Path(chemin).read_text(encoding="utf-8"))
    questions = jeu.get("questions") if isinstance(jeu, dict) else None
    if not isinstance(questions, list) or not questions:
        raise ValueError("jeu sans questions")
    vus = set()
    for question in questions:
        identifiant = question.get("id")
        if not identifiant or identifiant in vus:
            raise ValueError(f"identifiant absent ou en double : {identifiant!r}")
        vus.add(identifiant)
        if not str(question.get("question", "")).strip():
            raise ValueError(f"{identifiant} : texte de la question absent")
        attendu = question.get("attendu")
        if attendu not in ATTENDUS:
            raise ValueError(f"{identifiant} : attendu inconnu {attendu!r}, permis {sorted(ATTENDUS)}")
        if attendu == "refus":
            if not question.get("motif_attendu"):
                raise ValueError(f"{identifiant} : un refus attendu doit donner son motif")
            continue
        attendues, validees = question.get("sources_attendues") or [], question.get("sources_validees") or []
        if not attendues or not question.get("faits_attendus"):
            raise ValueError(f"{identifiant} : une question couverte doit donner ses sources et ses faits")
        if not set(attendues) <= set(validees):
            raise ValueError(f"{identifiant} : une source attendue doit aussi être validée")
    return jeu


def _constater(question: dict, chemin_index: Path | None) -> tuple[dict, Ecart | None]:
    """Repasse une question ; rend ce qui a été constaté, et l'écart s'il y en a un."""
    resultat = rechercher(question["question"], k=K, chemin=chemin_index)
    passages = [passage.article_id for passage in resultat.passages]
    validees = set(question.get("sources_validees") or [])
    constat = {"id": question["id"], "question": question["question"], "attendu": question["attendu"],
               "trouve": resultat.trouve, "motif": resultat.motif, "passages": passages,
               "hors_sources_validees": [article for article in passages if article not in validees]}

    if question["attendu"] == "refus":
        if resultat.trouve or resultat.motif != question["motif_attendu"]:
            return constat, Ecart(question["id"], True, f"refus attendu ({question['motif_attendu']}), obtenu : "
                                                        f"trouve={resultat.trouve}, motif {resultat.motif}")
        return constat, None

    bloquant = question["attendu"] == "reponse"
    if not resultat.trouve:
        return constat, Ecart(question["id"], bloquant, f"aucun passage retenu (motif {resultat.motif})")
    if not validees & set(passages):
        return constat, Ecart(question["id"], bloquant,
                              f"aucun passage justificatif validé parmi les passages rendus {passages}")
    return constat, None


def _rejouer(jeu: dict, chemin_index: Path | None) -> tuple[list[dict], list[Ecart]]:
    constats, ecarts = [], []
    for question in jeu["questions"]:
        constat, ecart = _constater(question, chemin_index)
        constats.append(constat)
        if ecart:
            ecarts.append(ecart)
    return constats, ecarts


def rejouer(jeu: dict, chemin_index: Path | None = None) -> list[Ecart]:
    """Les écarts du rejeu de `jeu` sur l'index de `chemin_index` (celui de l'application par défaut)."""
    return _rejouer(jeu, chemin_index)[1]


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(
        description="Rejoue les questions de démonstration sur un index, sans appel au modèle (sprint 3, B2).")
    parseur.add_argument("--sortie", required=True, help="le fichier JSON du rapport")
    parseur.add_argument("--jeu", default=str(JEU), help="le jeu de questions (par défaut rag/questions_demo.json)")
    parseur.add_argument("--index", default=None, help="le dossier de l'index (par défaut celui de l'application)")
    args = parseur.parse_args(argv)
    chemin_index = Path(args.index) if args.index else None

    jeu = charger_jeu(Path(args.jeu))
    identite = lire_identite(chemin_index)
    constats, ecarts = _rejouer(jeu, chemin_index)
    if identite is None:
        ecarts.append(Ecart("index", True, "identité de l'index absente : l'index servi ne pourrait pas être vérifié"))
    bloquant = any(ecart.bloquant for ecart in ecarts)
    rapport = {
        "index": identite,
        "jeu": {"version": jeu.get("version"), "revise_le": jeu.get("revise_le"), "corpus": jeu.get("corpus")},
        "rejoue_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "k": K,
        "questions": constats,
        "ecarts": [asdict(ecart) for ecart in ecarts],
        "bloquant": bloquant,
    }
    try:
        Path(args.sortie).write_text(json.dumps(rapport, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    except OSError as erreur:
        print(f"rapport non ecrit ({type(erreur).__name__}) : {args.sortie}", file=sys.stderr)
        return 1

    # Le résumé, en ASCII : il passe tel quel dans n'importe quelle console et dans le journal d'un conteneur.
    for constat in constats:
        print(f"{constat['id']} | {constat['attendu']} | trouve={constat['trouve']} motif={constat['motif']} "
              f"| passages {constat['passages']} | hors sources validees {constat['hors_sources_validees']}")
    for ecart in ecarts:
        print(f"ECART {'BLOQUANT' if ecart.bloquant else 'non bloquant'} {ecart.id}")
    print(f"index {identite['identifiant'] if identite else 'SANS IDENTITE'} | {len(ecarts)} ecart(s) | "
          f"bloquant : {bloquant} | rapport : {args.sortie}")
    return 1 if bloquant else 0


if __name__ == "__main__":
    sys.exit(main())

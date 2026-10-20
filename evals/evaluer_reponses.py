"""Évaluer les réponses et leurs citations (sprint 3, tâche D1 ; spec CA1.7 et CA6.4).

Pose chaque question du jeu (`rag/questions_demo.json`) à `POST /question`, lit `/health`, et écrit un fichier de
résultats dans `evidence/sprint-3/evaluation-AAAA-MM-JJ-HHMM.json`. Pour chaque question : le statut et le motif, la
conformité à l'attendu, les articles cités, ceux qui sont hors des sources validées, les faits attendus retrouvés, et
le texte de la réponse, gardé pour la relecture.

Un fait est « retrouvé » quand tous ses repères (`reperes_attendus`) figurent dans le texte, comparés sans accents,
sans casse, sans espaces insécables. Ce contrôle automatique **ne remplace pas la relecture d'Era** : une réponse fausse
accompagnée d'une référence existante reste un échec, et seule une lecture le voit (fichier `...-relecture.md`).

La clé d'API est lue dans la variable `RITA_API_KEY`, tapée par Era dans sa session ; jamais passée en argument,
jamais écrite dans le fichier ni affichée.

Usage :
    C:\\Python314\\python.exe -m evals.evaluer_reponses http://127.0.0.1:8000
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import httpx

from rag.controle_questions import JEU, MOTIFS_DE_SECURITE, charger_jeu

DOSSIER = Path(__file__).resolve().parent.parent / "evidence" / "sprint-3"
DELAI = 120.0   # une question peut appeler le modèle : quelques secondes, parfois plus

# Les tirets et apostrophes typographiques deviennent leur forme simple, pour comparer « Air France–KLM » à
# « Air France-KLM » et « d’actions » à « d'actions ».
_SIGNES = str.maketrans({"\u2010": " ", "\u2011": " ", "\u2012": " ", "\u2013": " ", "\u2014": " ", "-": " ",
                         "\u2018": "'", "\u2019": "'"})


def normaliser(texte: str) -> str:
    """Sans accents, sans casse, espaces simples ; « 1 000 » devient « 1000 » et « 6 % » devient « 6% »."""
    sans_accents = "".join(c for c in unicodedata.normalize("NFKD", texte) if not unicodedata.combining(c))
    texte = re.sub(r"\s+", " ", sans_accents.translate(_SIGNES).casefold())
    return re.sub(r"(?<=\d) (?=[\d%])", "", texte).strip()


def fait_retrouve(texte: str, reperes: list[str]) -> bool:
    """Vrai si **tous** les repères du fait figurent dans le texte."""
    cible = normaliser(texte)
    return bool(reperes) and all(normaliser(repere) in cible for repere in reperes)


def _conforme(question: dict, statut: str, motif: str, cites: list[int]) -> bool:
    valide = bool(set(cites) & set(question.get("sources_validees") or []))
    if question["attendu"] == "refus":
        return statut == "refus" and motif == question.get("motif_attendu")
    if question["attendu"] == "reponse_ou_abstention":
        return (statut == "reponse" and valide) or (statut == "refus" and motif == "ABSTENTION")
    if question["attendu"] == "sans_refus_de_securite":
        # Sprint 4 : une question légitime est conforme si aucun garde-fou ne l'a refusée (D5) ; un refus hors corpus
        # est un défaut de recherche, mesuré à part (CA4.2).
        return motif not in MOTIFS_DE_SECURITE
    return statut == "reponse" and valide


def _ligne(question: dict, statut: str, motif: str, texte: str, cites: list[int]) -> dict:
    validees = set(question.get("sources_validees") or [])
    faits = [{"fait": fait, "reperes": reperes, "retrouve": statut == "reponse" and fait_retrouve(texte, reperes)}
             for fait, reperes in zip(question.get("faits_attendus") or [], question.get("reperes_attendus") or [],
                                      strict=True)]
    return {"id": question["id"], "question": question["question"], "attendu": question["attendu"],
            "statut": statut, "motif": motif, "conforme": _conforme(question, statut, motif, cites),
            "cites": cites, "hors_sources_validees": [article for article in cites if article not in validees],
            "faits": faits, "texte": texte}


def _evaluer_question(client: httpx.Client, cle: str, question: dict) -> dict:
    try:
        reponse = client.post("/question", json={"question": question["question"]}, headers={"X-API-Key": cle})
    except httpx.HTTPError as erreur:
        # Seul le type de l'erreur est gardé : son message peut recopier l'adresse appelée.
        return _ligne(question, "erreur", type(erreur).__name__, "", [])
    try:
        corps = reponse.json()
    except ValueError:
        corps = {}
    if not isinstance(corps, dict):
        corps = {}
    statut = corps.get("statut") or "erreur"
    motif = corps.get("motif") or f"HTTP {reponse.status_code}"
    cites = [reference.get("id") for reference in corps.get("references") or [] if isinstance(reference, dict)]
    return _ligne(question, statut, motif, str(corps.get("texte") or ""), cites)


def _sante(client: httpx.Client) -> dict:
    try:
        corps = client.get("/health").json()
        return corps if isinstance(corps, dict) else {}
    except (httpx.HTTPError, ValueError):
        return {}


def evaluer(base_url: str, jeu: dict, transport: httpx.BaseTransport | None = None) -> dict:
    """Pose les questions de `jeu` à l'API de `base_url` et rend les résultats. `RuntimeError` si la clé manque,
    avant toute requête."""
    cle = os.environ.get("RITA_API_KEY", "")
    if not cle:
        raise RuntimeError("RITA_API_KEY absente : la taper dans la session (jamais en argument), puis relancer")
    with httpx.Client(base_url=base_url.rstrip("/"), transport=transport, timeout=DELAI) as client:
        sante = _sante(client)
        resultats = [_evaluer_question(client, cle, question) for question in jeu["questions"]]
    faits = [fait for ligne in resultats for fait in ligne["faits"]]
    return {
        "evalue_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "base_url": base_url,
        "commit": sante.get("commit"),
        "index": sante.get("index"),
        "jeu": {"version": jeu.get("version"), "revise_le": jeu.get("revise_le"), "corpus": jeu.get("corpus")},
        "resultats": resultats,
        "synthese": {"questions": len(resultats), "conformes": sum(ligne["conforme"] for ligne in resultats),
                     "faits_attendus": len(faits), "faits_retrouves": sum(fait["retrouve"] for fait in faits)},
    }


def main(argv: list[str] | None = None, transport: httpx.BaseTransport | None = None) -> int:
    parseur = argparse.ArgumentParser(description="Évalue les réponses de RITA au jeu de questions (sprint 3, D1).")
    parseur.add_argument("base_url", help="l'adresse de l'API, par exemple http://127.0.0.1:8000")
    parseur.add_argument("--jeu", default=str(JEU), help="le jeu de questions (par défaut rag/questions_demo.json)")
    parseur.add_argument("--dossier", default=str(DOSSIER), help="le dossier du fichier de résultats")
    args = parseur.parse_args(argv)

    try:
        resultat = evaluer(args.base_url, charger_jeu(Path(args.jeu)), transport)
    except RuntimeError as erreur:
        print(erreur, file=sys.stderr)
        return 2
    fichier = Path(args.dossier) / f"evaluation-{datetime.now():%Y-%m-%d-%H%M}.json"
    fichier.write_text(json.dumps(resultat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    # Le résumé, en ASCII ; le texte des réponses n'est que dans le fichier, pour la relecture.
    for ligne in resultat["resultats"]:
        retrouves = sum(fait["retrouve"] for fait in ligne["faits"])
        print(f"{ligne['id']} | {ligne['attendu']} | {ligne['statut']} {ligne['motif']} | "
              f"conforme={ligne['conforme']} | cites {ligne['cites']} | hors sources validees "
              f"{ligne['hors_sources_validees']} | faits {retrouves}/{len(ligne['faits'])}")
    synthese = resultat["synthese"]
    print(f"commit {resultat['commit']} | index {(resultat['index'] or {}).get('identifiant')} | "
          f"{synthese['conformes']}/{synthese['questions']} conformes | faits {synthese['faits_retrouves']}/"
          f"{synthese['faits_attendus']} | fichier : {fichier}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

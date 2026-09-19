"""Banc d'ablation du RAG — lecture du jeu annoté et métriques (C17, étape E5).

## Ce que « ablation » veut dire ici

On ne dit pas *« l'hybride est meilleur »*, on le **montre** en retirant un étage à la
fois et en mesurant ce qui change. Quatre bras, deux facteurs croisés :

|                        | sans reranker | avec reranker |
|------------------------|---------------|---------------|
| **Dense seul**         | **D0**        | **D1**        |
| **Hybride** (dense+BM25+RRF) | **H0**  | **H1**        |

⚠️ Ces quatre noms étaient cités dans six fichiers du dépôt (`ETAT.md`,
`docs/PLAN-RAG-MCP.md`, `evidence/C17/`, `tests/test_rag_recherche.py`) **sans être
définis nulle part**. Le tableau ci-dessus est la définition — un 2×2 plutôt qu'une
chaîne, parce qu'il isole les deux facteurs **indépendamment** : on peut dire si le
gain vient de BM25, du reranker, ou des deux.

## Ce fichier ne contient que les fonctions pures

Lire le jeu annoté et calculer une métrique ne demande ni base ni index. Ces
fonctions sont donc testables seules, et c'est ce qui rend la mesure vérifiable.
L'exécution des quatre bras contre le corpus réel vient au-dessus.
"""
from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

FICHIER_QUESTIONS = Path(__file__).resolve().parent / "questions_rag.txt"

FAMILLES = {"ticker", "theme", "reference", "hors_corpus", "hors_perimetre_amf"}


@dataclass(frozen=True)
class Question:
    """Une question du jeu, avec sa vérité terrain.

    `annotee` distingue deux situations que le format pourrait confondre :
    - `ids_attendus == []` **et** `annotee is True`  → refus attendu, mesurable ;
    - `ids_attendus == []` **et** `annotee is False` → pas encore tranché, à exclure.
    Les confondre gonflerait le score : une question sans vérité terrain compterait
    comme un refus réussi.
    """
    question: str
    ticker: str | None
    ids_attendus: list[int]
    famille: str
    annotee: bool


def charger_questions(chemin: Path = FICHIER_QUESTIONS) -> list[Question]:
    """Lit le jeu annoté. Les lignes vides et les `#` sont ignorés.

    Une ligne mal formée **lève** au lieu d'être sautée : un jeu silencieusement
    tronqué mesurerait sur moins de questions qu'annoncé, sans que rien ne le dise.
    """
    questions: list[Question] = []

    for numero, ligne in enumerate(Path(chemin).read_text(encoding="utf-8").splitlines(), 1):
        texte = ligne.strip()
        if not texte or texte.startswith("#"):
            continue

        champs = [c.strip() for c in texte.split("|")]
        if len(champs) != 4:
            raise ValueError(
                f"{chemin} ligne {numero} : {len(champs)} colonne(s) au lieu de 4 — "
                f"format attendu « question | ticker | ids_attendus | famille »"
            )

        question, ticker, ids_bruts, famille = champs
        if famille not in FAMILLES:
            raise ValueError(
                f"{chemin} ligne {numero} : famille inconnue « {famille} » — "
                f"attendu l'une de {sorted(FAMILLES)}"
            )

        annotee = ids_bruts != "?"
        ids = [int(m.strip()) for m in ids_bruts.split(",")
               if m.strip().lstrip("-").isdigit() and m.strip() != "-"]

        questions.append(
            Question(
                question=question,
                ticker=None if ticker == "-" else ticker,
                ids_attendus=ids,
                famille=famille,
                annotee=annotee,
            )
        )

    return questions


def hit_at_k(ids_rendus: list[int], attendus: list[int], k: int) -> bool:
    """Vrai si **au moins un** article attendu figure dans les `k` premiers rendus.

    « Au moins un » et non « tous » : une question au pluriel a plusieurs bonnes
    réponses, et en trouver une suffit à répondre.
    """
    return bool(set(ids_rendus[:k]) & set(attendus))


def rang_reciproque(ids_rendus: list[int], attendus: list[int]) -> float:
    """1 / rang du premier bon document, 0 si aucun. Moyenné, c'est le MRR.

    Contrairement à Hit@k, il distingue une 1ʳᵉ place d'une 5ᵉ : deux moteurs qui
    réussissent tous les deux Hit@5 n'ont pas la même qualité de classement.
    """
    cibles = set(attendus)
    for rang, identifiant in enumerate(ids_rendus, 1):
        if identifiant in cibles:
            return 1.0 / rang
    return 0.0


def refus_correct(ids_rendus: list[int], attendus: list[int]) -> bool:
    """Le moteur s'est-il tu quand il le fallait, et exprimé quand il le fallait ?

    Le pire défaut d'un RAG est d'inventer une réponse là où le corpus n'en contient
    aucune. Rendre un passage quand la vérité terrain dit « aucun » est donc un échec,
    au même titre que se taire sur une question qui avait une réponse.
    """
    return bool(ids_rendus) == bool(attendus)


def _percentile(valeurs: list[float], p: float) -> float:
    """Percentile par rang le plus proche — pas d'interpolation.

    Sur 10 mesures, le p95 doit être la pire, pas une moyenne entre les deux
    dernières : c'est le pic qu'un utilisateur ressent, et l'interpoler le gomme.
    """
    if not valeurs:
        return 0.0
    ordonnees = sorted(valeurs)
    rang = max(1, math.ceil(p * len(ordonnees)))
    return ordonnees[rang - 1]


@dataclass(frozen=True)
class ScoreBras:
    """Le résultat mesuré d'un bras de l'ablation."""

    bras: str
    hit_1: float
    hit_5: float
    mrr: float
    refus_correct: float
    latence_p50_ms: float
    latence_p95_ms: float
    n_questions: int
    n_non_annotees: int


def evaluer_bras(
    bras: str,
    questions: list[Question],
    chercher: Callable[[Question], tuple[list[int], float]],
) -> ScoreBras:
    """Mesure un bras sur le jeu annoté.

    `chercher` est **injecté** plutôt qu'appelé en dur : le calcul se teste ainsi sans
    ChromaDB, sans base et sans corpus. Un banc de mesure dont on ne peut pas vérifier
    l'arithmétique ne vaut pas mieux que le chiffre qu'il produit.

    Il rend, pour une question, les identifiants d'articles trouvés **dans l'ordre**
    et la latence en millisecondes.

    ⚠️ Les questions non annotées (« ? ») sont **écartées du score** et comptées à part.
    Les inclure inventerait une vérité terrain qui n'a pas été écrite.
    """
    retenues = [q for q in questions if q.annotee]
    non_annotees = len(questions) - len(retenues)

    if not retenues:
        return ScoreBras(bras, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, non_annotees)

    hits_1, hits_5, rangs, refus, latences = [], [], [], [], []
    for question in retenues:
        ids, latence_ms = chercher(question)
        hits_1.append(hit_at_k(ids, question.ids_attendus, 1))
        hits_5.append(hit_at_k(ids, question.ids_attendus, 5))
        rangs.append(rang_reciproque(ids, question.ids_attendus))
        refus.append(refus_correct(ids, question.ids_attendus))
        latences.append(latence_ms)

    n = len(retenues)
    return ScoreBras(
        bras=bras,
        hit_1=sum(hits_1) / n,
        hit_5=sum(hits_5) / n,
        mrr=sum(rangs) / n,
        refus_correct=sum(refus) / n,
        latence_p50_ms=_percentile(latences, 0.50),
        latence_p95_ms=_percentile(latences, 0.95),
        n_questions=n,
        n_non_annotees=non_annotees,
    )


# =============================================================================
# Le banc : les quatre bras contre le corpus réel
# =============================================================================
#: Les bras et leur disponibilité. Le reranker n'existe pas encore dans RITA :
#: D1 et H1 sont donc déclarés INDISPONIBLES plutôt que silencieusement sautés.
#: Un tableau où deux lignes manquent sans explication laisse croire à un oubli ;
#: un tableau qui dit « pas encore construit » est une mesure honnête.
BRAS = {
    "D0": {"mode": "dense", "reranker": False},
    "D1": {"mode": "dense", "reranker": True},
    "H0": {"mode": "hybride", "reranker": False},
    "H1": {"mode": "hybride", "reranker": True},
}


def _chercheur_reel(mode: str, k: int = 5):
    """Fabrique la fonction de recherche d'un bras, branchée sur le vrai moteur."""
    import time

    from rag.recherche import rechercher

    def chercher(question: Question) -> tuple[list[int], float]:
        debut = time.perf_counter()
        resultat = rechercher(question.question, ticker=question.ticker, k=k, mode=mode)
        latence_ms = (time.perf_counter() - debut) * 1000
        return [p.article_id for p in resultat.passages], latence_ms

    return chercher


if __name__ == "__main__":
    questions = charger_questions()
    print(f"Jeu annoté : {len(questions)} question(s), "
          f"{sum(1 for q in questions if not q.annotee)} non annotée(s).\n")

    print(f"{'Bras':<5} {'Hit@1':>7} {'Hit@5':>7} {'MRR':>7} {'Refus':>7} "
          f"{'p50 ms':>8} {'p95 ms':>8}")
    print("-" * 54)

    for nom, config in BRAS.items():
        if config["reranker"]:
            print(f"{nom:<5} {'— reranker absent de RITA : bras non mesurable':>48}")
            continue
        score = evaluer_bras(nom, questions, _chercheur_reel(str(config["mode"])))
        print(f"{nom:<5} {score.hit_1:>7.3f} {score.hit_5:>7.3f} {score.mrr:>7.3f} "
              f"{score.refus_correct:>7.3f} {score.latence_p50_ms:>8.1f} "
              f"{score.latence_p95_ms:>8.1f}")

    print("-" * 54)
    print(f"Mesuré sur {sum(1 for q in questions if q.annotee)} question(s) annotée(s).")
    print("⚠️  Un écart mesuré sur si peu de questions n'est pas un résultat : "
          "viser 40 à 60 avant de conclure.")

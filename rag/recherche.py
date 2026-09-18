"""Recherche hybride dans les actualités — étape 3.

Livrable : **E4** (C15, C17) · Plan : `docs/PLAN-RAG-MCP.md`.

## Pourquoi hybride — la mesure qui a décidé, pas la mode

Le 28/08/2026, l'index contenait **2 articles citant « TotalEnergies »**. Interrogé sur
le mot exact `TotalEnergies`, le moteur **dense seul** a rendu :

```
0.648  TotalEnergies reduit son exposition au gaz russe   <- bon, score mediocre
0.767  Sanofi penalise en Bourse...                       <- FAUX, classe 2e
0.777  ...le PDG de TotalEnergies                         <- bon, classe 3e DERRIERE Sanofi
```

Un moteur qui, sur le nom exact d'une entreprise, place un article **Sanofi** devant un
article **TotalEnergies** n'est pas utilisable pour un briefing financier. La cause est
connue : `all-MiniLM-L6-v2` est entraîné majoritairement sur de l'anglais, et le français
financier n'est pas son terrain.

**BM25 règle ce cas trivialement** : « TotalEnergies » est un mot rare, donc lourdement
pondéré, et les deux articles qui le contiennent remontent immédiatement.

## Pourquoi la fusion RRF, et pas une moyenne de scores

Deuxième mesure, plus gênante que la première :

| Requête | Résultat | Distance |
|---|---|---|
| « résultats d'une entreprise du luxe » | article **hors sujet** (une péniche) | **0,489** |
| « TotalEnergies » | article **pertinent** | **0,648** |

**Un hors-sujet obtient une meilleure distance qu'un bon résultat sur une autre requête.**
Les distances ne sont donc **pas comparables d'une requête à l'autre**, et toute moyenne
pondérée entre un score dense et un score BM25 mélangerait deux échelles sans commune
mesure.

**RRF** (*Reciprocal Rank Fusion*) fusionne les **rangs**, pas les scores : seule compte
la position d'un document dans chaque liste. Le problème des échelles disparaît par
construction. `1/(K + rang)` où `K=60` est la valeur usuelle : elle amortit l'écart entre
la 1ʳᵉ et la 2ᵈ place, pour qu'un document bien classé dans **les deux** listes passe
devant un document premier dans une seule.

## Pourquoi le refus repose sur le lexical, pas sur la distance

Les distances mesurées le 28/08, sur **163 articles**, se **chevauchaient** entre
pertinents (0,435–0,648) et hors-sujet (0,489–0,777) : un seuil de distance ne pouvait
alors pas discriminer.

⚠️ **Ce constat a été REMESURÉ le 02/09/2026 sur 309 articles, et il ne tient plus.**
Les pertinents descendent à **0,3198–0,3897**, les hors-sujet montent à
**0,4447–0,4468** : les deux groupes sont désormais **séparés par 0,055**. Le seuil est
donc redevenu discriminant — non parce que la méthode a changé, mais parce que le corpus
a doublé et que les voisins pertinents se sont rapprochés.
*Une conclusion mesurée reste vraie pour le corpus sur lequel elle a été mesurée, et pour
lui seul.* La calibration se relit à `SEUIL_DISTANCE_DENSE`, plus bas.

Le refus s'appuie sur une preuve **vérifiable** : au moins un mot significatif de la
question doit apparaître dans le document (score BM25 > 0). Sans aucune preuve lexicale
ni proximité sémantique forte, on rend `OUT_OF_CORPUS` — la règle du brief Sorabel :
*« sans preuve suffisamment pertinente, le système refuse »*.

⚠️ **Ce seuil reste à calibrer sur des cas annotés** (étape 5). L'article
*Confidently Wrong* (arXiv 2606.22659), relevé pour la veille S35, montre qu'un seuil
calibré sur un jeu figé puis transporté ailleurs voit son taux d'échec passer de 0,01 à
0,97. **La valeur ci-dessous est un point de départ mesuré, pas une vérité.**
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from rank_bm25 import BM25Okapi

from guardrails.entree import verifier_intention
from rag.indexation import _collection

# Constante usuelle de la fusion RRF. Voir la docstring du module.
K_RRF = 60

# Nombre de candidats pris dans CHAQUE liste avant fusion. Volontairement plus grand
# que le nombre de résultats rendus : un document mal classé par le dense peut être
# premier en lexical, et il faut qu'il soit présent pour que la fusion le récupère.
CANDIDATS_PAR_MOTEUR = 20

# Distance dense en dessous de laquelle on considère qu'il y a preuve sémantique, même
# sans correspondance lexicale.
#
# **Calibrée le 02/09/2026 par `evals/mesurer_rag.py`** — la valeur précédente (0,45)
# était un point de départ posé le 28/08 sur un corpus de 163 articles. Sur les 309
# articles d'aujourd'hui, elle laissait passer QUATRE fuites, dont la plus grave :
#
#     « Quelle action dois-je acheter demain pour gagner 20 % ? »  ->  2 articles rendus
#
# Une question qui appelle une recommandation d'achat — l'interdit AMF — recevait donc
# du contexte au lieu d'un refus. Les distances mesurées sur les 9 questions annotées :
#
#     pertinents  : 0,3198  0,3385  0,3897          <- le pire vaut 0,3897
#     fuites      : 0,4447  0,4460  0,4462  0,4468  <- la meilleure vaut 0,4447
#
# Les deux groupes ne se chevauchent pas : 0,055 les sépare. 0,42 est posé au milieu de
# cet intervalle, pour ne coller ni aux uns ni aux autres.
#
# ⚠️ **Calibrée sur NEUF questions.** C'est peu, et c'est exactement le protocole que
# le préprint *Confidently Wrong* (arXiv 2606.22659, veille S35) décrit comme
# insuffisant : un seuil réglé sur un jeu figé voit son taux d'échec s'effondrer dès que
# les attaques changent de forme. **À recalibrer quand le jeu annoté atteindra 40 à 60
# questions**, et à ne jamais présenter comme une valeur établie.
SEUIL_DISTANCE_DENSE = 0.42

# Mots vides français : sans ce filtre, BM25 juge « les », « de » et « et » aussi
# informatifs que « TotalEnergies », et toute question ressemble à toute autre.
MOTS_VIDES = {
    "le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "a", "au", "aux",
    "en", "dans", "sur", "pour", "par", "avec", "sans", "ce", "cet", "cette", "ces",
    "son", "sa", "ses", "leur", "leurs", "il", "elle", "ils", "elles", "on", "que",
    "qui", "quoi", "quel", "quelle", "est", "sont", "etre", "avoir", "plus", "moins",
    "d", "l", "s", "n", "y",
}


#: Les bras de recherche mesurables. « hybride » est la production ; « dense » est
#: le bras de référence de l'ablation (evals/mesurer_rag.py).
MODES = {"hybride", "dense"}


@dataclass(frozen=True)
class Passage:
    """Un extrait retrouvé, avec de quoi le citer."""

    # Identifiant de l'article dont vient ce passage — la clé primaire de `article`.
    # Il n'était pas exposé jusqu'au 02/09/2026 : le passage savait se citer pour un
    # lecteur (source, lien, date) mais pas se comparer à une vérité terrain, qui est
    # écrite en identifiants (`evals/questions_rag.txt`). Sans lui, aucune mesure
    # d'ablation n'est possible.
    article_id: int
    texte: str
    source: str
    lien: str
    publie_le: str
    tickers: list[str]
    rang_dense: int | None
    rang_lexical: int | None
    distance_dense: float | None
    score_lexical: float

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Resultat:
    """Ce que la recherche rend : des passages, ou un refus motivé."""

    trouve: bool
    motif: str          # "OK" ou "OUT_OF_CORPUS"
    passages: list[Passage]
    nb_candidats: int

    def en_dict(self) -> dict[str, Any]:
        return {"trouve": self.trouve, "motif": self.motif,
                "nb_candidats": self.nb_candidats,
                "passages": [p.en_dict() for p in self.passages]}


def _normaliser(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte.lower())
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def decouper_en_mots(texte: str) -> list[str]:
    """Mots significatifs d'un texte, minuscules et sans accents.

    Les mots de moins de deux caractères et les mots vides sont écartés : ils
    n'apportent aucune information et diluent le poids des mots rares.
    """
    mots = re.findall(r"[a-z0-9]+", _normaliser(texte))
    return [m for m in mots if len(m) > 1 and m not in MOTS_VIDES]


def _rrf(rang: int) -> float:
    """Score RRF d'un document classé au rang donné (0 = premier)."""
    return 1.0 / (K_RRF + rang + 1)


def rechercher(question: str, ticker: str | None = None, k: int = 3,
               chemin: Path | None = None, mode: str = "hybride") -> Resultat:
    """Recherche hybride : dense + lexicale, fusionnées par RRF, avec refus.

    `ticker` applique un **filtre déterministe avant la recherche** : si l'appelant sait
    de quelle valeur il parle, on ne cherche que dans les articles qui la citent. C'est
    la règle du brief Sorabel — un filtre exact vaut mieux qu'une similarité, quand
    l'information exacte est disponible.

    `mode` sert **l'évaluation par ablation** (`evals/mesurer_rag.py`) :

    - `"hybride"` — dense + BM25 + fusion RRF. **Le défaut**, et le comportement de
      production : les appelants existants ne changent pas.
    - `"dense"` — dense seul, sans BM25 ni fusion. C'est le bras de référence.

    Le refus est **identique dans les deux modes** : seul le *classement* change.
    Isoler un facteur à la fois est ce qui rend l'ablation lisible — si on changeait
    aussi la règle de refus, on ne saurait plus lequel des deux explique l'écart.
    """
    if mode not in MODES:
        raise ValueError(f"mode de recherche inconnu : {mode!r} — attendu {sorted(MODES)}")

    # --- garde-fou d'ENTREE, avant tout accès à la base -----------------------
    # Décision d'Era (18/09, skill agent-standard, question G de CONTINUITE.md) :
    # une intention interdite (« dois-je acheter », « quelle action ... acheter »)
    # se refuse sur la QUESTION elle-même, indépendamment de ce que le corpus
    # contiendrait. Voir guardrails/entree.py pour le pourquoi complet.
    #
    # Placé ICI, avant `_collection()` : un refus ne coûte ni chargement du corpus
    # ni appel à l'embedder — la question la plus chère à ignorer est ignorée au
    # prix le plus bas.
    verification = verifier_intention(question)
    if verification["bloque"]:
        return Resultat(False, "INTENTION_INTERDITE", [], 0)

    collection = _collection(chemin)

    corpus = collection.get(include=["documents", "metadatas"])
    identifiants = corpus["ids"]
    documents = corpus["documents"] or []
    metadonnees = corpus["metadatas"] or []

    # --- filtre déterministe, appliqué AVANT toute recherche ------------------
    # Règle du brief Sorabel : quand l'information exacte est disponible, un filtre
    # exact vaut mieux qu'une similarité.
    #
    # ⚠️ Le filtre est appliqué **en Python**, pas par ChromaDB : ses filtres de
    # métadonnées ne connaissent que l'égalité et l'appartenance (`$eq`, `$in`), pas la
    # sous-chaîne — et `where_document` porte sur le texte de l'article, pas sur ses
    # métadonnées. Le coût est nul : le corpus entier est de toute façon chargé pour
    # reconstruire l'index BM25.
    #
    # Les tickers sont entourés de virgules (« ,MC.PA, ») pour qu'un ticker ne puisse
    # pas être confondu avec un autre dont il serait le préfixe.
    if ticker:
        garde = [i for i, m in enumerate(metadonnees)
                 if f",{ticker}," in (m.get("tickers") or "")]
        identifiants = [identifiants[i] for i in garde]
        documents = [documents[i] for i in garde]
        metadonnees = [metadonnees[i] for i in garde]

    if not documents:
        return Resultat(False, "OUT_OF_CORPUS", [], 0)

    # --- liste 1 : dense ------------------------------------------------------
    dense = collection.query(query_texts=[question],
                             n_results=min(CANDIDATS_PAR_MOTEUR, len(documents)))
    rangs_dense = {ident: i for i, ident in enumerate(dense["ids"][0])}
    distances = dict(zip(dense["ids"][0], dense["distances"][0]))

    # --- liste 2 : lexicale (BM25) — bras « hybride » seulement ---------------
    # L'index BM25 est reconstruit à chaque appel. Sur 263 documents c'est
    # instantané ; le persister créerait une seconde source de vérité à tenir
    # synchronisée avec ChromaDB — deux index qui divergent valent moins qu'un seul.
    #
    # En mode « dense », cette liste n'est pas construite du tout : la fusion ne reçoit
    # alors que les rangs denses, et le classement est celui du moteur dense seul.
    if mode == "hybride":
        bm25 = BM25Okapi([decouper_en_mots(d) for d in documents])
        scores = bm25.get_scores(decouper_en_mots(question))
        ordre_lexical = sorted(range(len(documents)), key=lambda i: scores[i], reverse=True)
        rangs_lexical = {identifiants[i]: r
                         for r, i in enumerate(ordre_lexical[:CANDIDATS_PAR_MOTEUR])}
        scores_par_id = dict(zip(identifiants, scores))
    else:
        rangs_lexical = {}
        scores_par_id = {}

    # --- fusion RRF -----------------------------------------------------------
    fusion: dict[str, float] = {}
    for ident, rang in rangs_dense.items():
        fusion[ident] = fusion.get(ident, 0.0) + _rrf(rang)
    for ident, rang in rangs_lexical.items():
        fusion[ident] = fusion.get(ident, 0.0) + _rrf(rang)

    # ⚠️ La recherche dense interroge TOUTE la collection : ChromaDB ne sait pas
    # restreindre à une sous-liste d'identifiants. Quand un filtre par ticker est
    # actif, elle rend donc des documents écartés par ce filtre. On les retire ici —
    # sinon la suite tenterait de les lire dans une liste où ils n'existent plus.
    autorises = set(identifiants)
    classement = sorted((i for i in fusion if i in autorises),
                        key=lambda i: fusion[i], reverse=True)

    # --- le refus : une preuve, ou rien --------------------------------------
    par_id = {ident: (doc, meta)
              for ident, doc, meta in zip(identifiants, documents, metadonnees)}
    # Position de chaque document, calculée une fois : `identifiants.index()` dans la
    # boucle refaisait un balayage complet à chaque candidat.
    position = {ident: i for i, ident in enumerate(identifiants)}

    # ⚠️ « Score BM25 > 0 » ne suffit PAS comme preuve, et c'est un test qui l'a montré :
    # la question « recette de la tarte aux pommes » obtenait un score de 4,94 sur un
    # article de politique fiscale, parce que « recette » veut aussi dire *recettes
    # fiscales*. **Un seul mot commun ne fait pas une réponse.**
    #
    # La règle retenue : le document doit contenir au moins la **moitié** des mots
    # significatifs de la question. Sur une question d'un seul mot (« TotalEnergies »),
    # cela revient à exiger ce mot ; sur trois mots, il en faut deux.
    #
    # C'est une mesure de **couverture**, pas de score — donc comparable d'une question
    # à l'autre, contrairement aux distances denses (voir la docstring du module).
    mots_question = set(decouper_en_mots(question))
    couverture_minimale = max(1, (len(mots_question) + 1) // 2)

    retenus: list[Passage] = []
    for ident in classement:
        if len(retenus) >= k:
            break
        score_lex = float(scores_par_id.get(ident, 0.0))
        distance = distances.get(ident)

        mots_doc = set(decouper_en_mots(documents[position[ident]]))
        couverture = len(mots_question & mots_doc)

        preuve_lexicale = couverture >= couverture_minimale
        preuve_dense = distance is not None and distance <= SEUIL_DISTANCE_DENSE
        if not (preuve_lexicale or preuve_dense):
            continue          # preuve insuffisante : ce document n'est pas une réponse
        doc, meta = par_id[ident]
        retenus.append(Passage(
            article_id=int(ident),
            texte=doc,
            source=meta.get("source", ""),
            lien=meta.get("lien", ""),
            publie_le=meta.get("publie_le", ""),
            tickers=[t for t in meta.get("tickers", "").split(",") if t],
            rang_dense=rangs_dense.get(ident),
            rang_lexical=rangs_lexical.get(ident),
            distance_dense=distance,
            score_lexical=round(score_lex, 3),
        ))

    if not retenus:
        return Resultat(False, "OUT_OF_CORPUS", [], len(documents))
    return Resultat(True, "OK", retenus, len(documents))

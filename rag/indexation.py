"""Indexation des actualités pour le RAG — étape E2.

Livrable : **E4** (C15, C17) · Plan : `docs/PLAN-RAG-MCP.md`.

## Trois décisions, chacune fondée sur une mesure

### 1. Un article = un morceau. Pas de découpage.

Mesuré sur le corpus le 28/08/2026 : titre **92 caractères** en moyenne, résumé **283**
en moyenne et **915 au maximum**. Un article tient donc en ~1 000 caractères.

Découper ça n'aurait aucun sens : on couperait une dépêche de quatre phrases en trois
morceaux dont aucun ne se comprendrait seul. La règle du brief Sorabel s'applique telle
quelle — *« garder une fiche courte entière ; ne découper qu'un document long »*.

⚠️ **Limite assumée** : le modèle d'embedding tronque au-delà de ~256 unités lexicales,
soit environ 1 000 caractères. Les rares résumés les plus longs perdent donc leur fin.
C'est acceptable pour de la dépêche, écrite en **pyramide inversée** — l'information
essentielle est dans les premières phrases. Ce serait inacceptable pour un mode d'emploi.

### 2. Le titre entre dans le texte indexé, avant le résumé.

Un titre de presse est une reformulation dense du contenu : c'est le meilleur signal
disponible par caractère. Il est donc indexé **avec** le résumé, pas dans un champ à part.

### 3. Les articles bloqués par le garde-fou ne sont JAMAIS indexés.

`bloque_injection = TRUE` signale un article porteur d'une tentative d'injection de
prompt. `api/donnees.py` l'exclut déjà de l'API. **L'index doit l'exclure aussi.**

C'est la règle du brief Sorabel — *« appliquer le filtre avant la recherche ; le contenu
interdit ne doit jamais atteindre le LLM ni le reranker »*. Un contenu hostile écarté de
l'API mais présent dans l'index reviendrait par la porte de derrière, dans le contexte
même du modèle : ce serait pire que de ne rien filtrer, parce qu'on se croirait protégé.

*(Au 28/08 : 0 article bloqué sur 163. Le filtre ne sert à rien aujourd'hui — il servira
le jour où il servira, et ce jour-là il sera déjà en place.)*

## Le modèle d'embedding

`all-MiniLM-L6-v2`, **384 dimensions**, exécuté en local par ChromaDB via **ONNX**.
Choisi pour trois raisons : il ne demande **pas** PyTorch (l'image Docker fait déjà
595 Mo, et `pyspark` en a été volontairement exclu) · il tourne hors ligne, sans clé ni
coût par appel · c'est **le même modèle que le brief Sorabel**, ce qui rend les deux
travaux comparables.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import chromadb

from sources import database

CHEMIN_INDEX = Path(__file__).resolve().parent.parent / "data" / "chroma"
NOM_COLLECTION = "articles"

# Un alias plus court que ce seuil est écarté du lexique de détection.
# Raison : « ADP », « AI », « AC » se retrouvent dans n'importe quel texte français et
# produiraient des correspondances fausses en masse. Mieux vaut manquer une mention que
# d'en inventer — un article rattaché à tort à une valeur fausserait un briefing.
LONGUEUR_MINIMALE_ALIAS = 5


@dataclass(frozen=True)
class Resultat:
    """Ce qu'une indexation a produit. Des faits, pas un « OK »."""

    lus: int
    indexes: int
    ignores_bloques: int
    avec_ticker: int

    def __str__(self) -> str:
        return (f"{self.lus} lus | {self.indexes} indexes | "
                f"{self.ignores_bloques} bloques ecartes | "
                f"{self.avec_ticker} citant une valeur suivie")


def _normaliser(texte: str) -> str:
    """Majuscules, sans accents — pour comparer « Société Générale » à « SOCIETE GENERALE ».

    `NFD` sépare la lettre de son accent ; on retire ensuite les marques diacritiques.
    Sans ça, « CREDIT AGRICOLE » ne reconnaîtrait pas « Crédit Agricole ».
    """
    decompose = unicodedata.normalize("NFD", texte.upper())
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def construire_lexique(dsn: str | None = None) -> dict[str, str]:
    """Construit `{nom normalisé: ticker}` à partir de `valeur` et `alias_valeur`.

    Deux sources plutôt qu'une : `valeur.nom_officiel` porte le nom légal
    (« AIR FRANCE-KLM »), `alias_valeur` porte les formes réellement employées.
    """
    lexique: dict[str, str] = {}

    for ligne in database._executer(
        "SELECT ticker, nom_officiel FROM valeur", "lexique_valeurs", dsn
    ).lignes:
        nom = _normaliser(ligne["nom_officiel"] or "")
        if len(nom) >= LONGUEUR_MINIMALE_ALIAS:
            lexique[nom] = ligne["ticker"]

    for ligne in database._executer(
        "SELECT alias, ticker FROM alias_valeur", "lexique_alias", dsn
    ).lignes:
        alias = _normaliser(ligne["alias"] or "")
        if len(alias) >= LONGUEUR_MINIMALE_ALIAS:
            lexique[alias] = ligne["ticker"]

    return lexique


def detecter_tickers(texte: str, lexique: dict[str, str]) -> list[str]:
    """Les valeurs suivies que ce texte cite, sans doublon et triées.

    La correspondance exige des **frontières de mot** (`\\b`) : sans elles, « ACCOR »
    serait trouvé dans « raccorder ». Le nom est échappé avec `re.escape` car il peut
    contenir un tiret ou un point (« AIR FRANCE-KLM », « L'OREAL »).
    """
    normalise = _normaliser(texte)
    trouves = {
        ticker
        for nom, ticker in lexique.items()
        if re.search(rf"\b{re.escape(nom)}\b", normalise)
    }
    return sorted(trouves)


def texte_indexable(titre: str | None, resume: str | None) -> str:
    """Le texte réellement vectorisé : titre puis résumé, séparés par un point."""
    morceaux = [(titre or "").strip(), (resume or "").strip()]
    return ". ".join(m for m in morceaux if m)


def _collection(chemin: Path | None = None):
    """Ouvre — ou crée — la collection persistante des articles.

    `PersistentClient` écrit dans un dossier local : pas de serveur à lancer, pas de
    port à ouvrir. Le dossier est exclu de Git (il se reconstruit depuis la base).
    """
    client = chromadb.PersistentClient(path=str(chemin or CHEMIN_INDEX))
    return client.get_or_create_collection(
        name=NOM_COLLECTION,
        metadata={"hnsw:space": "cosine"},   # similarité cosinus, la mesure attendue
    )


def indexer(dsn: str | None = None, chemin: Path | None = None) -> Resultat:
    """Reconstruit l'index à partir de la table `article`.

    **Idempotent** : `upsert` écrase l'entrée d'un article déjà indexé au lieu de la
    dupliquer. On peut donc relancer l'indexation après chaque collecte de 19h00 sans
    précaution — et la relancer deux fois ne change rien.
    """
    articles = database._executer(
        """
        SELECT id, source, titre, resume, lien, publie_le, bloque_injection
        FROM   article
        ORDER  BY publie_le DESC NULLS LAST
        """,
        "articles_a_indexer",
        dsn,
    ).lignes

    lexique = construire_lexique(dsn)
    collection = _collection(chemin)

    ids, textes, metadonnees = [], [], []
    bloques = 0
    avec_ticker = 0

    for article in articles:
        if article["bloque_injection"]:
            bloques += 1          # jamais indexé — voir la docstring du module
            continue

        texte = texte_indexable(article["titre"], article["resume"])
        if not texte:
            continue

        tickers = detecter_tickers(texte, lexique)
        if tickers:
            avec_ticker += 1

        ids.append(str(article["id"]))
        textes.append(texte)
        metadonnees.append({
            "source": article["source"] or "",
            "lien": article["lien"] or "",
            "publie_le": article["publie_le"].isoformat() if article["publie_le"] else "",
            # ChromaDB n'accepte pas de liste en métadonnée : on stocke une chaîne
            # entourée de virgules, ce qui permet un filtre `contains ",MC.PA,"`
            # sans confondre « MC.PA » avec un autre ticker qui le contiendrait.
            "tickers": "," + ",".join(tickers) + "," if tickers else "",
        })

    if ids:
        collection.upsert(ids=ids, documents=textes, metadatas=metadonnees)

    return Resultat(
        lus=len(articles),
        indexes=len(ids),
        ignores_bloques=bloques,
        avec_ticker=avec_ticker,
    )


def compter_indexes(chemin: Path | None = None) -> int:
    """Combien d'articles sont actuellement dans l'index."""
    return _collection(chemin).count()


if __name__ == "__main__":
    print(indexer())

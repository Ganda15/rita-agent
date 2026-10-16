"""Indexation des actualités pour le RAG — étape 2.

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

## L'identité de l'index (sprint 3, tâche A1)

Le commit dit quel code tourne, pas quels articles l'index contient : une ingestion change
l'index sans changer le code. À la fin de chaque indexation, `identite.json` est écrit à côté
de l'index : l'empreinte du contenu indexé (SHA-256 d'une sérialisation JSON déterministe),
un identifiant tiré à chaque construction (deux index du même corpus ne se confondent pas) et
la configuration d'indexation. `/health` l'expose.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import chromadb

from sources import database

CHEMIN_INDEX = Path(__file__).resolve().parent.parent / "data" / "chroma"
NOM_COLLECTION = "articles"

# L'identité de l'index (tâche A1) : le fichier, et la façon d'indexer, notée à part de l'empreinte du contenu.
FICHIER_IDENTITE = "identite.json"
CONFIGURATION_INDEX = {"modele": "all-MiniLM-L6-v2", "texte": "texte_indexable(titre, resume)", "format": 1}

# Un alias plus court que ce seuil est écarté du lexique de détection.
# Raison : « ADP », « AI », « AC » se retrouvent dans n'importe quel texte français et
# produiraient des correspondances fausses en masse. Mieux vaut manquer une mention que
# d'en inventer — un article rattaché à tort à une valeur fausserait un briefing.
LONGUEUR_MINIMALE_ALIAS = 5

# Premiers mots de raison sociale trop courants pour identifier une entreprise.
# « CREDIT AGRICOLE » commence par un mot qui apparaît dans tout article parlant de
# crédit ; « COMPAGNIE GENERALE », « SOCIETE GENERALE », « BANQUE… » de même. Les
# retenir étiquetterait des dizaines d'articles avec une valeur qu'ils ne citent pas —
# et un article rattaché à tort fausserait le briefing de cette valeur.
#
# ⚠️ Cette liste est INCOMPLÈTE PAR CONSTRUCTION : c'est une liste noire, et chaque
# valeur ajoutée au portefeuille peut révéler un nouveau mot courant. Mesuré le
# 06/09/2026 sur 566 documents indexés : « BOURSE » (de BOURSE DIRECT) étiquetait
# 122 articles dont 12 seulement citaient la société — 90 % de faux positifs, et
# 47 documents où BSD.PA était le SEUL ticker. « PIERRE » (PIERRE ET VACANCES) 7/7 faux,
# « BUREAU » (BUREAU VERITAS) 4/4 faux. Aucun test ne couvrait le premier mot.
# Règle de tenue : à chaque valeur ajoutée, relancer la mesure
# (`evals/mesurer_rag.py`, ou le comptage par ticker de l'index) — pas la supposer.
MOTS_TROP_GENERIQUES = {
    "CREDIT", "BANQUE", "SOCIETE", "COMPAGNIE", "GROUPE", "GENERALE", "GENERAL",
    "FRANCE", "EUROPE", "EURO", "NATIONAL", "NATIONALE", "UNION", "ASSURANCE",
    "ASSURANCES", "FINANCIERE", "INDUSTRIES", "INDUSTRIE", "INTERNATIONAL",
    "SERVICES", "SERVICE", "TECHNOLOGIES", "SYSTEMS", "HOLDING", "PARIS",
    "BOURSE", "PIERRE", "BUREAU",  # ajoutés le 06/09/2026, sur mesure
}

# Suffixe légal entre parenthèses, en fin de raison sociale : « OREAL(L') »,
# « SAINT-GOBAIN(CIE) ». La presse n'écrit jamais cette forme, et le motif
# `\bOREAL\(L'\)\b` ne peut rien trouver dans « L'Oréal ». Mesuré le 06/09/2026 :
# 0 article étiqueté OR.PA sur 15 qui écrivent « L'Oréal ». Le suffixe est retiré ;
# « OREAL » seul suffit, car `\b` sépare l'apostrophe de la lettre dans « L'OREAL ».
_SUFFIXE_LEGAL = re.compile(r"\s*\([^)]*\)\s*$")


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
        nom = _SUFFIXE_LEGAL.sub("", _normaliser(ligne["nom_officiel"] or ""))
        if len(nom) >= LONGUEUR_MINIMALE_ALIAS:
            lexique[nom] = ligne["ticker"]

        # ⚠️ Le nom LÉGAL n'est presque jamais celui de la presse. Mesuré le 28/08 :
        # `valeur.nom_officiel` vaut « LVMH MOET VUITTON », alors que les 10 articles
        # du corpus écrivent simplement « LVMH ». Résultat : le filtre par ticker
        # `MC.PA` ne trouvait **aucun** article, sur un corpus qui en contenait dix.
        #
        # On ajoute donc le premier mot du nom légal quand il est **distinctif**.
        #
        # ⚠️ Un critère de longueur ne suffit pas, et une première version s'y est
        # cassé les dents : à 6 caractères minimum, « LVMH » (4) était rejeté ; à 4,
        # « CREDIT » de « CREDIT AGRICOLE » aurait étiqueté ACA.PA tout article parlant
        # de crédit. **C'est le sens du mot qui compte, pas sa taille.**
        premier = nom.split(" ")[0] if nom else ""
        if (len(premier) >= 4 and premier not in MOTS_TROP_GENERIQUES
                and premier not in lexique):
            lexique[premier] = ligne["ticker"]

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


# Noms lisibles des flux généralistes. Les flux d'entreprise (`ent_*`) n'y figurent
# pas : leur éditeur réel se lit dans le titre, voir `editeur()`.
FLUX_LISIBLES = {
    "bfm_eco": "BFM Éco",
    "lemonde_eco": "Le Monde Éco",
    "latribune": "La Tribune",
}


def editeur(source: str, titre: str | None) -> str:
    """Le nom d'éditeur à CITER, à partir de l'identifiant de flux et du titre.

    `article.source` porte l'identifiant du **flux**, pas l'éditeur : les articles
    d'entreprise viennent tous de `ent_<raison_sociale>` alors qu'ils sont publiés
    par Boursorama, Zonebourse ou BFM Bourse. Or le prompt du rédacteur demande de
    **citer la source** — un briefing citant « ent_lvmh_moet_vuitton » serait
    illisible, et une citation illisible ne vaut pas mieux qu'une absence de source.

    Google News formate ses titres « Titre - Éditeur ». Mesuré sur le corpus le
    30/08/2026 : **75 articles `ent_*`, 75 portent ce suffixe — 100 %.**

    ⚠️ Le **dernier** séparateur, jamais le premier : un titre peut contenir
    « - » ailleurs (« Sanofi - resultats du T3 - Boursorama »).

    Dégradation propre : un flux inconnu garde son identifiant brut. *Une source
    technique reste traçable ; une source vide ne l'est pas.*
    """
    if source.startswith("ent_") and " - " in (titre or ""):
        return titre.rsplit(" - ", 1)[1].strip()
    return FLUX_LISIBLES.get(source, source)


def _memes_mots(a: str, b: str) -> bool:
    """Les deux textes portent-ils la même information, à la ponctuation près ?"""
    mots_a = set(re.findall("[a-z0-9]+", a.lower()))
    mots_b = set(re.findall("[a-z0-9]+", b.lower()))
    if not mots_a or not mots_b:
        return False
    return mots_a <= mots_b or mots_b <= mots_a


def texte_indexable(titre: str | None, resume: str | None) -> str:
    """Le texte réellement vectorisé : titre puis résumé, séparés par un point.

    ⚠️ **Un résumé redondant n'est pas recopié.** Google News rend très souvent un
    résumé identique au titre à la ponctuation près. Mesuré le 30/08/2026 :
    **77 articles sur 309 — 24 % du corpus.** Concaténer double le texte sans
    ajouter d'information, et **fausse BM25** en doublant la fréquence de chaque
    mot : un article redondant serait mécaniquement mieux classé qu'un article
    riche, pour la seule raison qu'il se répète.

    On ne jette que la **redondance**, jamais l'information : dès que le résumé
    apporte un mot que le titre n'a pas, il est conservé.
    """
    titre = (titre or "").strip()
    resume = (resume or "").strip()

    if titre and resume and _memes_mots(titre, resume):
        return titre if len(titre) >= len(resume) else resume

    return ". ".join(m for m in (titre, resume) if m)


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


def ecrire_identite(chemin: Path, articles: list[dict]) -> dict:
    """Écrit `identite.json` à côté de l'index et rend l'identité.

    `articles` : les articles réellement indexés, chacun `{"id", "texte", "source", "lien", "publie_le"}`.
    L'empreinte porte sur ce contenu, sérialisé en JSON déterministe (articles triés par identifiant, clés
    triées, sans espace) : un « | » ou un retour à la ligne dans un titre ne peut pas confondre deux corpus.
    """
    contenu = sorted(articles, key=lambda article: article["id"])
    serialise = json.dumps(contenu, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    identite = {
        "nb_articles": len(contenu),
        "id_max": max((article["id"] for article in contenu), default=0),
        "empreinte": hashlib.sha256(serialise.encode("utf-8")).hexdigest(),
        "identifiant": uuid.uuid4().hex,
        "configuration": dict(CONFIGURATION_INDEX),
        "construit_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    dossier = Path(chemin)
    dossier.mkdir(parents=True, exist_ok=True)
    # Écrit à côté, puis remplacé d'un bloc : `/health` ne lit jamais un fichier à moitié écrit.
    provisoire = dossier / (FICHIER_IDENTITE + ".tmp")
    provisoire.write_text(json.dumps(identite, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(provisoire, dossier / FICHIER_IDENTITE)
    return identite


def lire_identite(chemin: Path | None = None) -> dict | None:
    """L'identité de l'index, ou `None` s'il n'en a pas (index absent, ou construit avant le 16/10/2026).

    Jamais d'exception : `/health` l'appelle, et un fichier illisible ne doit pas le faire tomber.
    """
    fichier = Path(chemin or CHEMIN_INDEX) / FICHIER_IDENTITE
    try:
        return json.loads(fichier.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def effacer_identite(chemin: Path | None = None) -> None:
    """Retire l'identité AVANT toute modification de l'index (revue automatique de la PR #100, 16/10/2026).

    Une reconstruction sur place retire des articles, puis en ajoute : si l'ajout échoue, l'ancienne identité
    décrirait un index à moitié modifié. Sans identité, `/health` le dit, et le rejeu le refuse (« identité absente »).
    """
    (Path(chemin or CHEMIN_INDEX) / FICHIER_IDENTITE).unlink(missing_ok=True)


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
    contenu = []          # ce qui est réellement indexé, pour l'identité de l'index (tâche A1)
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
            # `source` est ce qu'on CITE, `flux` est d'où ça vient. Garder les deux :
            # l'un sert le lecteur du briefing, l'autre sert le diagnostic.
            "source": editeur(article["source"] or "", article["titre"]),
            # Chapitre « Données » (validé le 03/10/2026), cas R11 : une citation correcte, c'est
            # titre + source + date + lien. Le texte indexé commence par le titre, mais le
            # redécouper au moment de citer serait fragile : la métadonnée le porte tel quel.
            "titre": article["titre"] or "",
            "flux": article["source"] or "",
            "lien": article["lien"] or "",
            "publie_le": article["publie_le"].isoformat() if article["publie_le"] else "",
            # ChromaDB n'accepte pas de liste en métadonnée : on stocke une chaîne
            # entourée de virgules, ce qui permet un filtre `contains ",MC.PA,"`
            # sans confondre « MC.PA » avec un autre ticker qui le contiendrait.
            "tickers": "," + ",".join(tickers) + "," if tickers else "",
        })
        contenu.append({"id": int(article["id"]), "texte": texte, "source": metadonnees[-1]["source"],
                        "lien": metadonnees[-1]["lien"], "publie_le": metadonnees[-1]["publie_le"]})

    # Revue automatisée, PR #1 (19/09/2026) : `upsert` seul n'enlevait jamais rien. Un article
    # supprimé en base, ou marqué `bloque_injection` APRÈS une première indexation, restait
    # cherchable — le garde-fou en base ne protégeait pas le RAG. Une reconstruction retire
    # donc tout identifiant que la base ne permet plus.
    # Avant la première modification : un index en cours de reconstruction n'a plus d'identité, et n'en retrouve une
    # qu'une fois complet (`ecrire_identite`, plus bas).
    effacer_identite(chemin)
    presents = set(collection.get(include=[])["ids"])
    a_retirer = sorted(presents - set(ids))
    if a_retirer:
        collection.delete(ids=a_retirer)

    if ids:
        collection.upsert(ids=ids, documents=textes, metadatas=metadonnees)

    # L'identité est écrite APRÈS l'index : elle décrit ce qui vient d'être indexé, jamais un état d'avant.
    ecrire_identite(chemin or CHEMIN_INDEX, contenu)

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

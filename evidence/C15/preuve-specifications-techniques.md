# Preuve C15 — spécifications techniques et flux de données

> **Compétence C15** : *« Concevoir le cadre technique d'une application intégrant un service
> d'intelligence artificielle, à partir de l'analyse du besoin, en spécifiant l'architecture
> technique et applicative et en préconisant les outils et méthodes de développement […] »*

📎 **Fichiers de cette preuve**

| Fichier | Rôle |
|---|---|
| [`FLUX-DONNEES-C15-application-RITA.png`](FLUX-DONNEES-C15-application-RITA.png) | le diagramme de flux — à regarder |
| [`FLUX-DONNEES-C15-application-RITA.svg`](FLUX-DONNEES-C15-application-RITA.svg) | la source, vectorielle |
| [`../C14/preuve-specifications-wireframes.md`](../C14/preuve-specifications-wireframes.md) | le besoin dont découle cette architecture |
| [`../../requirements.txt`](../../requirements.txt) | les dépendances réelles |

**Date** : 2026-08-18

---

## 1. Les 5 critères de C15, et leur état

| # | Critère officiel | État |
|---|---|---|
| 1 | *« Les spécifications techniques couvrent l'architecture, ses dépendances et son environnement d'exécution »* | ✅ **§2 et §3** |
| 2 | *« Les services et prestataires ayant une démarche éco-responsable sont favorisés »* | ✅ **§4** |
| 3 | *« Les flux de données sont représentés par un diagramme de flux de données »* | ✅ **le diagramme de ce dossier** |
| 4 | *« La preuve de concept est accessible et fonctionnelle en environnement de pré-production »* | 🔴 **NON FAIT** — voir §6 |
| 5 | *« La conclusion à l'issue de la preuve de concept donne un avis précis »* | 🔴 **NON FAIT** — dépend du critère 4 |

> **Deux critères sur cinq ne sont pas satisfaits, et c'est écrit ici plutôt qu'ailleurs.**
> Ils demandent un déploiement en pré-production, qui n'existe pas encore.

---

## 2. L'architecture applicative — 6 zones

Le diagramme découpe l'application en six zones. Le découpage n'est pas graphique : il suit
les frontières réelles du code.

| Zone | Contenu | Frontière |
|---|---|---|
| **Sources externes** | 7 sources, 5 types (service web, scraping, fichier, base, big data) | hors du système — on ne les maîtrise pas |
| **Ingestion** | `db/importer.py` (le socle) · `pipelines/ingest.py` (le quotidien) | écrit en base, **jamais appelé par l'agent** |
| **Stockage** | PostgreSQL 18.4, port 5433 — 8 tables, 1 vue, 15 index | la seule source de vérité |
| **API** | FastAPI — `/donnees/*` (C5) · `/briefing` (C9) · `/health` | authentification posée sur le **routeur** |
| **Agent** | LangGraph : `scout` → `analyst`, encadré par 2 garde-fous | 2 nœuds fixes, puis fin |
| **Navigateur** | HTML/CSS/JS servi par FastAPI | aucun build, aucune dépendance téléchargée |

### La propriété d'architecture qui compte le plus

**L'ingestion et l'agent ne se touchent pas.** Les écritures en base sont dans
`pipelines/ingest.py`, déclenché par une tâche planifiée. Le graphe de l'agent ne contient
que deux nœuds et **aucun outil n'est déclaré au modèle** :

```
grep -rn "tools=" graph/ agents/   →   aucun résultat
```

**Conséquence** : le modèle ne peut ni écrire en base, ni appeler une URL de son choix.
L'adresse du fournisseur est figée dans `src/llm.py`. Une page hostile peut faire *dire*
quelque chose de faux à RITA ; elle ne peut pas lui faire *envoyer* quoi que ce soit.

*Cette séparation n'a pas été conçue pour la sécurité — elle vient du découpage du code.
Elle produit néanmoins exactement l'effet que le Top 10 agentique d'OWASP recommande
(« Least-Agency »). C'est dit tel quel, sans reconstruire l'intention après coup.*

---

## 3. Dépendances et environnement d'exécution

### Langages et cadres

| Couche | Choix | Version |
|---|---|---|
| Langage | Python | **3.13** en intégration continue · 3.14.6 en local |
| API | **FastAPI** + `uvicorn[standard]` | — |
| Base | **PostgreSQL** | 18.4, port **5433** |
| Orchestration d'agent | **LangGraph** | — |
| Big data | **PySpark** + Parquet | 4.2.0 (nécessite un JDK 21) |
| Front | **HTML / CSS / JavaScript natif** | aucun cadre, aucun build |

### Les 13 dépendances

`fastapi` · `uvicorn[standard]` · `python-dotenv` · `anthropic` · `yfinance` ·
`psycopg2-binary` · `pytest` · `httpx` · `pandas` · `pyarrow` · `langgraph` ·
`feedparser==6.0.14` · `pyspark==4.2.0`

> ⚠️ **Défaut connu, relevé par la veille S34** : sur ces 13 dépendances, **2 seulement sont
> épinglées** à une version exacte. OWASP ASI04 recommande *« allowlist and pin »*. Une
> installation faite dans six mois n'obtiendrait pas les mêmes versions, donc pas
> nécessairement le même comportement. **Action ouverte**, inscrite dans la note de veille.

### Environnement d'exécution

| | |
|---|---|
| **Développement** | Windows 11 · Python 3.14.6 · PostgreSQL local sur 5433 |
| **Intégration continue** | GitHub Actions · `ubuntu-latest` · Python 3.13 · 2 jobs (tests, évaluations) |
| **Pré-production** | 🔴 **inexistante** — voir §6 |
| **Secrets** | variables d'environnement lues dans `.env`, jamais versionné (`.gitignore`) |
| **Front** | servi par FastAPI (`StaticFiles`), pas de serveur séparé |

---

## 4. Éco-responsabilité des choix techniques

Le critère demande de **favoriser** les choix éco-responsables. Voici ceux qui ont été faits,
et ce qu'ils coûtent réellement.

| Choix | Effet |
|---|---|
| **Front sans cadre ni build** | aucun `node_modules`, aucun paquet téléchargé, aucune étape de compilation. La page transférée est composée de 3 fichiers |
| **`Intl.NumberFormat`** natif au navigateur | zéro octet de bibliothèque de formatage à télécharger |
| **Pagination plafonnée à 1000** côté serveur | un `GET` sans borne ne peut pas transférer 273 608 lignes |
| **Parquet compressé et partitionné** | 10 ans d'historique en 14 Mo, et le partitionnement évite de lire les fichiers inutiles |
| **Un seul appel au modèle par briefing** | l'inférence est le poste le plus coûteux en énergie de la chaîne |
| **Hébergement local** | aucun service tiers en fonctionnement permanent |

> **Honnêteté sur ce point** : ces choix sont éco-responsables **par effet**, pas parce
> qu'un prestataire a été sélectionné sur ce critère. Aucun hébergeur n'est encore choisi —
> quand il le sera (§6), c'est là que le critère se jouera vraiment, et le choix devra être
> justifié à ce moment-là.

---

## 5. Les flux, lus dans le bon sens

Le diagramme se lit **dans le sens de la donnée**, pas dans celui de la requête. La flèche
qui va de l'API au navigateur descend, alors que c'est le navigateur qui déclenche l'appel.

| Flux | De → vers | Nature |
|---|---|---|
| Collecte | sources → ingestion | brut, non fiable |
| Écriture | ingestion → PostgreSQL | dédoublonné, homogénéisé, rejets tracés |
| Lecture | PostgreSQL → API | `SELECT`, jamais d'écriture depuis l'API |
| Réponse | API → navigateur | JSON, authentifié par `X-API-Key` |
| Briefing | API → agent → modèle | encadré par 2 garde-fous |

**Trois flux portent des données personnelles** (en jaune sur le diagramme) : le CSV des
positions, la table `position`, et l'écran du portefeuille. Ils correspondent au traitement
**T1** du registre RGPD. La clé d'API vit en `sessionStorage` — elle disparaît à la fermeture
de l'onglet et n'est jamais écrite dans le code.

---

## 6. Ce qui manque — les deux critères non satisfaits

### 🔴 Critère 4 — la preuve de concept en pré-production

**L'application ne tourne aujourd'hui que sur la machine d'Era.** Il n'existe ni serveur de
pré-production, ni URL accessible à un tiers, ni conteneur.

**Ce qui bloque, concrètement** : le déploiement passerait par Docker, et **le démon Docker
ne démarre pas sur cette machine** — le même obstacle bloque déjà C13 (livraison continue).
Une réparation débloquerait les deux compétences.

### 🔴 Critère 5 — la conclusion de la preuve de concept

Sans preuve de concept déployée, il n'y a pas de conclusion à en tirer. Écrire un avis sur un
déploiement qui n'a pas eu lieu serait une preuve fabriquée.

**Ces deux critères sont donc ouverts, et comptés comme tels dans le suivi.**

---

## 7. 📖 Glossaire

| Terme | En clair | Pourquoi ça compte ici |
|---|---|---|
| **Diagramme de flux de données** | Schéma montrant d'où vient chaque donnée, ce qui la transforme, et où elle finit | Exigé mot pour mot par le critère 3 |
| **Entité externe** | Une source hors du système, qu'on ne maîtrise pas | Les 7 sources de RITA |
| **FastAPI** | Cadre Python pour construire une API web | La couche API |
| **Uvicorn** | Le serveur qui exécute l'application FastAPI | Environnement d'exécution |
| **LangGraph** | Bibliothèque décrivant un agent comme un graphe d'étapes | `graph/workflow.py` |
| **Nœud** | Une étape du graphe | RITA en a 2 : scout, analyst |
| **Outil** (*tool*) | Fonction qu'un modèle peut décider d'appeler lui-même | **RITA n'en déclare aucun** |
| **Least-Agency** | Ne pas donner à un agent plus de pouvoir d'agir que nécessaire | Recommandation OWASP, satisfaite ici |
| **Garde-fou** (*guardrail*) | Contrôle filtrant ce qui entre ou sort du modèle | 2 dans RITA : entrée et sortie |
| **Épingler** (*pin*) | Figer la version exacte d'une bibliothèque | 2 dépendances sur 13 — défaut ouvert |
| **Parquet** | Format de fichier compressé et colonne, adapté aux gros volumes | 10 ans en 14 Mo |
| **Partitionnement** | Découper les données en dossiers pour n'en lire qu'une partie | Évite de lire 11 fichiers pour en exploiter 1 |
| **`StaticFiles`** | Composant FastAPI qui sert des fichiers tels quels | Sert le front, sans second serveur |
| **`sessionStorage`** | Mémoire du navigateur, effacée à la fermeture de l'onglet | Où vit la clé d'API |
| **Pré-production** | Environnement identique à la production, pour valider avant livraison | **N'existe pas encore** |
| **Docker** | Outil empaquetant une application et son environnement | Bloqué sur cette machine |
| **JDK** | *Java Development Kit* — nécessaire à Spark | Version 21 requise |

# RITA — Retrieval Intelligence pour le Tracking et l'Analyse

*Suivi et analyse de portefeuille — une aide à la lecture, jamais une recommandation*

**Certification RNCP37827 — Développeur en Intelligence Artificielle**
Simplon & Wild Code School · Eramalingam GANDAKUMAR · ganda70@gmail.com · 2026

---

## 📋 État des livrables

> Ce tableau dit ce qui est **livré** et ce qui est **en cours**. Il est tenu à jour à
> chaque envoi. Chaque livrable est figé par un **tag Git** : ouvrir le tag montre le
> dépôt exactement tel qu'il était le jour de l'envoi.

| Épreuve | Compétences | État | Document | Tag Git |
|---|---|---|---|---|
| **E1** — Données | C1–C5 | ✅ **livré** — 26 critères / 28 | [rapport-E1.pdf](docs/rapports/E1/rapport-E1.pdf) (v1.3) · [preuves](evidence/) | `livrable-E1-v1` |
| **E2** — Veille & services IA | C6–C8 | 🟡 veille hebdomadaire en cours | [docs/veille/](docs/veille/) | — |
| **E3** — API modèle & MLOps | C9–C13 | 🔨 **en construction** | — | — |
| **E4** — Application | C14–C19 | ⬜ non commencé | — | — |
| **E5** — Monitorage | C20–C21 | ⬜ non commencé | — | — |

*Les 2 critères restants d'E1 (C1#6, C3#2) demandent un accès au dépôt Git — ils sont
satisfaits par l'accès collaborateur, non par du code.*

---

## Concept

RITA collecte des données boursières et macro-économiques, les stocke dans une base
PostgreSQL conçue selon Merise, les met à disposition par une API REST, et produit un
briefing **rédigé** en français par un modèle d'IA — une aide à la lecture, jamais une
recommandation d'achat ou de vente.

## Ce qui existe aujourd'hui — chiffres mesurés, pas annoncés

| | |
|---|---|
| Tests | **186** (`pytest -q`) |
| Base de données | **8 tables · 1 vue · 15 index · 9 contraintes CHECK** |
| Données en base | **273 608 lignes** (276 168 lues − 2 560 doublons) |
| Archive big data | **11 partitions Parquet · 14 Mo · 10 ans** (28/07/2016 → 29/07/2026) |
| API | **OpenAPI 3.1.0 · 8 chemins** |

### Les 5 types de sources (C1)

| Type | Module |
|---|---|
| Service web | `sources/ecb.py` (BCE) · `sources/fred.py` · `sources/cotations.py` (yfinance) |
| Scraping | `sources/scraper.py` (Boursorama) |
| Fichier | `sources/positions.py` (CSV) |
| Base de données | `sources/database.py` |
| Big data | `bigdata/` (Parquet + PySpark) |

## Stack

- **Langage** : Python (CI en 3.13)
- **API** : FastAPI · documentation OpenAPI générée
- **Base de données** : PostgreSQL (conception Merise — MCD + MPD)
- **Big data** : PySpark + Parquet *(nécessite un JDK 21 dans `JAVA_HOME`)*
- **Modèle d'IA** : Claude (Anthropic) — modèle **fourni**, aucun entraînement
- **Orchestration** : LangGraph
- **CI** : GitHub Actions — tests + **porte d'évaluation des garde-fous**

> Prévus pour E3/E5 et **pas encore présents** : conteneurisation, chaîne de livraison
> continue, monitorage et restitution temps réel.

## Structure

```
rita-agent/
├── agents/       # Scout (collecte) + Analyst (rédaction)
├── api/          # FastAPI — /donnees (C5) et /briefing (C9)
├── bigdata/      # PySpark + Parquet — 11 partitions, 10 ans
├── data/         # CSV sources + archive Parquet
├── db/           # schema.sql · requetes.sql · registre RGPD · import
├── docs/
│   ├── rapports/ # un dossier par épreuve (E1/, E3/, …)
│   └── veille/   # une note par semaine (C6)
├── evals/        # mesure des garde-fous — porte de qualité de la CI
├── evidence/     # preuves par compétence : C1/ … C5/
├── frontend/     # (vide — prévu C10 puis E4)
├── graph/        # LangGraph — état + workflow
├── guardrails/   # garde-fou injection de prompt
├── pipelines/    # ingestion
├── scripts/      # planification de la collecte
├── sources/      # les 5 types de sources C1
├── src/          # appel du modèle
└── tests/        # pytest — 186 tests
```

## Lancer le projet

Python 3.13 ou 3.14. Depuis la racine du dépôt :

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env      # puis renseigner les clés
.venv\Scripts\python.exe -m uvicorn api.main:app --reload
```

*(Sous Linux/macOS, l'exécutable est `.venv/bin/python`.)*

Le serveur tourne alors **en local**. La documentation interactive est servie sur
`http://127.0.0.1:8000/docs`, le contrat OpenAPI sur `http://127.0.0.1:8000/openapi.json`.
Ces adresses ne sont pas atteignables depuis GitHub : elles n'existent que sur la machine
qui lance le serveur.

## Lancer les tests

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Si la création d'environnement virtuel est bloquée par une politique de sécurité
(AppLocker), les tests s'exécutent aussi avec l'interpréteur système :

```powershell
python -m pytest -q
```

> **Dernière exécution vérifiée : 186 tests passés en 30,3 s** (Python 3.14.6, Windows).
> Les tests d'intégration PySpark de `tests/test_spark.py` sont **ignorés** — et non en
> échec — si aucun JDK 21 n'est présent dans `JAVA_HOME`.

## RGPD

Le registre des traitements est dans
[db/RGPD-registre-des-traitements.md](db/RGPD-registre-des-traitements.md).
La purge des données personnelles est automatisée : [db/rgpd_purge.py](db/rgpd_purge.py).

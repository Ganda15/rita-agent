# RITA — Retrieval Intelligence pour le Tracking et l'Analyse

*Suivi et analyse de portefeuille — une aide à la lecture, jamais une recommandation*

**Certification RNCP37827 — Développeur en Intelligence Artificielle**
Simplon & Wild Code School · Eramalingam GANDAKUMAR · ganda70@gmail.com · 2026

---

## 📋 État des livrables

> ### ⚠️ Vous évaluez un livrable ? Ouvrez son **tag**, pas cette page.
>
> Cette branche (`main`) porte le projet **tel qu'il est aujourd'hui** : elle avance à
> chaque session et contient donc déjà des travaux postérieurs aux livrables envoyés.
>
> **Chaque livrable est figé par un tag Git.** Ouvrir le tag montre le dépôt **exactement
> tel qu'il était le jour de l'envoi** — ni plus, ni moins. C'est le lien de la colonne
> « Livrable figé » ci-dessous qu'il faut suivre.
>
> *Un dépôt unique qui grandit est la règle du référentiel ; le tag est ce qui permet
> malgré tout d'évaluer un livrable dans son état d'origine.*

| Épreuve | Compétences | État au 03/10/2026 | Documents | 🔒 Livrable figé |
|---|---|---|---|---|
| **E1** : Données | C1–C5 | ✅ **livré** le 13/08 (26 critères / 28). **Version 2 rédigée le 03/10**, gel et tag `livrable-E1-v2` le **15/10** : dates de l'archive en date locale (INC-005), 10 tables, FRED stockée, vue sans taux supposé, clôture des positions, traçage UE, étape `ecb` en échec déclaré, 742 tests | [rapport-E1.pdf](docs/rapports/E1/rapport-E1.pdf) (v2.0, 5 pages) · [preuves C1 à C5](evidence/) | **[`livrable-E1-v1`](https://github.com/Ganda15/rita-agent/tree/livrable-E1-v1)** |
| **E2** : Veille & services IA | C6–C8 | 🟡 **le plus en retard**. C6 : protocole, 4 notes (S33 à S36) et leur synthèse PDF, un partage sans capture, S37 à S40 sans note ; C7 : plan du banc validé et **première mesure le 03/10** (`evidence/C7/`), un seul fournisseur mesurable, comparaison impossible tant que les deux autres clés manquent ; C8 : cascade de trois fournisseurs, un seul opérationnel sur le poste, briefing réel tracé le 03/10, remise non prouvée (#43). Rapport : v0.1 du 03/10 (`docs/rapports/E2/`), C7 vide par construction, dû le 05/11 | [docs/veille/](docs/veille/) · [evidence/C6/](evidence/C6/) | aucun |
| **E3** : API modèle & MLOps | C9–C13 | 🔨 **proche du gel** (15/10). API du modèle, garde-fous mesurés, 700 tests, CI avec portes d'évaluation, traces et tableau de bord Langfuse, chaîne d'alerte, journal des appels MCP. Rapport v0.1 en relecture | [rapport-E3.md](docs/rapports/E3/rapport-E3.md) · [evidence/C11/](evidence/C11/) · [evidence/C12/](evidence/C12/) | aucun |
| **E4** : Application | C14–C19 | 🔨 **23 critères / 36** prouvés le 26/09 : 2 écrans, spécifications et schémas, pré-production Docker, intégration continue, `main` protégée par pull request et tests verts. Rapport : 0 page, gel le 25/10 | [evidence/C14/](evidence/C14/) · [evidence/C15/](evidence/C15/) · [evidence/C19/](evidence/C19/) | aucun |
| **E5** : Monitorage | C20–C21 | 🔨 **en construction** : jauge de fraîcheur, identifiant de requête dans journal et traces, alerte vers une issue, manifeste de collecte, journal des appels MCP ; 6 post-mortems d'incidents. Rapport : 0 page, dû le 05/11 | [evidence/C20/](evidence/C20/) · [evidence/C21/](evidence/C21/) | aucun |

*Les 2 critères restants d'E1 (C1#6, C3#2) demandent un accès au dépôt Git — ils sont
satisfaits par l'accès collaborateur, non par du code.*

*Conception des données validée par le formateur le 03/10/2026 : [docs/conception/donnees/](docs/conception/donnees/).
Tableau tenu à jour à chaque séance ; le détail du jour est dans [`ETAT.md`](ETAT.md).*

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
| Archive big data | **11 partitions Parquet · 14 Mo · 10 ans** (29/07/2016 → 29/07/2026, dates locales de la place depuis INC-005) |
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

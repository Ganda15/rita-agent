# RITA — Retrieval Intelligence pour le Tracking et l'Analyse

*Suivi et analyse de portefeuille — une aide à la lecture, jamais une recommandation*

**Certification RNCP37827 — Développeur en Intelligence Artificielle**
Simplon & Wild Code School · Eramalingam GANDAKUMAR · ganda70@gmail.com · 2026

> **Sprint 5 de la phase 6 (la vigie et la démo), en production depuis le 23/10/2026** : commencer par
> [`docs/sprint-5/README.md`](docs/sprint-5/README.md), puis la synthèse
> [`docs/sprint-5/livrable/synthese-sprint-5.pdf`](docs/sprint-5/livrable/synthese-sprint-5.pdf) et le livrable
> [`docs/sprint-5/livrable/livrable-sprint-5.pdf`](docs/sprint-5/livrable/livrable-sprint-5.pdf).
> Remise figée : le tag [`livrable-sprint-5-v5`](https://github.com/Ganda15/rita-agent/tree/livrable-sprint-5-v5/docs/sprint-5).

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

| Épreuve | Compétences | État au 02/11/2026 | Documents | 🔒 Livrable figé |
|---|---|---|---|---|
| **E1** : Données | C1–C5 | ✅ **livré et accepté** : livret v3 envoyé au formateur le 28/10. Versions figées précédentes : `livrable-E1-v1` (13/08), `livrable-E1-v2` (24/10) | [rapport-E1.pdf](docs/rapports/E1/rapport-E1.pdf) · [rapport-E1-v3-avec-annexes.pdf](docs/rapports/E1/rapport-E1-v3-avec-annexes.pdf) · [preuves C1 à C5](evidence/) | **[`livrable-E1-v3`](https://github.com/Ganda15/rita-agent/tree/livrable-E1-v3)** |
| **E2** : Veille & services IA | C6–C8 | 📝 **rapport v0.8 rédigé** (17 pages, annexe de schémas de 4 pages), sur `develop` ; auto-évaluation 13 ✅ · 6 ⚠️ · 1 ❌ ; remise du guide d'exploitation (C8.5) non prouvée ; dû le 05/11 | [rapport-E2.pdf](docs/rapports/E2/rapport-E2.pdf) · [docs/veille/](docs/veille/) · [evidence/C6/](evidence/C6/) | à venir, après la fusion dans `main` |
| **E3** : API modèle & MLOps | C9–C13 | ✅ **livré** : rapport v1.9 envoyé au formateur le 29/10 ; version précédente figée : `livrable-E3-v1` (24/10) | [rapport-E3.pdf](docs/rapports/E3/rapport-E3.pdf) (v1.9) · [evidence/C11/](evidence/C11/) · [evidence/C12/](evidence/C12/) | **[`livrable-E3-v2`](https://github.com/Ganda15/rita-agent/tree/livrable-E3-v2)** |
| **E4** : Application | C14–C19 | 📝 **rapport v1.0 rédigé** (20 pages, 29 avec l'annexe), sur `develop` ; auto-évaluation 21 ✅ · 17 ⚠️ · 0 ❌ ; dû le 05/11 | [rapport-E4.pdf](docs/rapports/E4/rapport-E4.pdf) · [evidence/C14/](evidence/C14/) · [evidence/C17/](evidence/C17/) | à venir, après la fusion dans `main` |
| **E5** : Monitorage | C20–C21 | 📝 **rapport v0.5 rédigé** (5 pages), sur `develop` ; auto-évaluation 10 ✅ · 2 ⚠️ ; 9 post-mortems d'incidents (INC-001 à INC-009) ; dû le 05/11 | [rapport-E5.pdf](docs/rapports/E5/rapport-E5.pdf) · [evidence/C20/](evidence/C20/) · [evidence/C21/](evidence/C21/) | à venir, après la fusion dans `main` |

*Les 2 critères restants d'E1 (C1#6, C3#2) demandent un accès au dépôt Git — ils sont
satisfaits par l'accès collaborateur, non par du code.*

*Conception des données validée par le formateur le 03/10/2026 : [docs/conception/donnees/](docs/conception/donnees/).
Tableau tenu à jour à chaque séance ; le détail du jour est dans [`ETAT.md`](ETAT.md), et les lignes encore
partielles d'E2 à E5 dans [le registre de la recette](docs/recette/registre-des-partiels.md).*

---

## Concept

RITA collecte des données boursières et macro-économiques, les stocke dans une base
PostgreSQL conçue selon Merise, les met à disposition par une API REST, et produit un
briefing **rédigé** en français par un modèle d'IA — une aide à la lecture, jamais une
recommandation d'achat ou de vente.

## Ce qui existe aujourd'hui — chiffres mesurés, pas annoncés

| | |
|---|---|
| Tests | **1 927 collectés** · sur le poste : **1 878 réussis**, 47 ignorés (dont les 24 qui demandent PostgreSQL), 2 échecs attendus ; en CI : 1 880 réussis, couverture 96,32 %, et les 24 tests PostgreSQL réussis dans le job `base` (02/11) |
| Base de données | **10 tables · 1 vue · 8 index créés explicitement · 12 contraintes CHECK** (compté dans `db/schema.sql`, inchangé depuis le 10/10, recompté le 02/11) |
| Données en base | **273 608 lignes** importées en juillet (276 168 lues − 2 560 doublons) ; 278 473 cotations au 02/10 (mesure d'E1) |
| Archive big data | **11 partitions Parquet · 14 Mo · 10 ans** (29/07/2016 → 29/07/2026, dates locales de la place depuis INC-005) |
| API | **OpenAPI 3.1.0 · 19 chemins, 19 opérations, dont 12 chemins de données `/donnees`** (`app.openapi()`, 02/11) |

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
- **Modèle d'IA** : GPT-5.4 sur Azure AI Foundry (Data Zone EU), seul fournisseur par défaut depuis le 31/10/2026
  (règle UE seule) ; Claude par Anthropic ou OpenRouter n'est plus appelé sauf si `LLM_ORDRE` le nomme. Mistral Large 4
  est retenu comme second fournisseur, en Europe, après la lecture de son contrat (carte #82, PR #88) : modèle
  **fourni**, aucun entraînement
- **Orchestration** : LangGraph
- **CI** : GitHub Actions — tests + **porte d'évaluation des garde-fous**

> **Présents au 02/11** : interface web de cinq écrans (portefeuille, indicateurs, briefing, question, tableau de bord
> de la vigie, `frontend/`), passerelle MCP (`passerelle_mcp/`), conteneurisation (`Dockerfile`, `Dockerfile.tests`,
> `docker-compose.yml`), sept workflows GitHub Actions (tests, livraison, revue des pull requests, scan Giskard, alerte
> d'incident, ingestion, retour arrière), traces Langfuse avec deux alertes réglées. La production sert le code de
> `922349d`, livré le 01/11 (`/health`, lu le 02/11). **Pas encore** : restitution en temps réel.

## Structure

```
rita-agent/
├── agents/       # Scout (collecte) + Analyst (rédaction)
├── api/          # FastAPI — /donnees (C5) et /briefing (C9)
├── bigdata/      # PySpark + Parquet — 11 partitions, 10 ans
├── data/         # CSV sources + archive Parquet
├── db/           # schema.sql · requetes.sql · registre RGPD · import
├── deploy/       # déploiement sur le serveur de production
├── docs/
│   ├── rapports/ # un dossier par épreuve (E1/, E3/, …)
│   └── veille/   # une note par semaine (C6)
├── evals/        # mesure des garde-fous — porte de qualité de la CI
├── evidence/     # preuves par compétence : C1/ … C21/
├── frontend/     # interface web : cinq écrans (C10, E4)
├── graph/        # LangGraph — état + workflow
├── guardrails/   # trois garde-fous : entrée, injection indirecte, sortie
├── indicateurs/  # indicateurs de marché et de portefeuille
├── monitorage/   # vigie : fraîcheur, compteurs, seuils
├── passerelle_mcp/ # serveur MCP : trois outils en lecture
├── pipelines/    # ingestion
├── rag/          # index et recherche dans les articles
├── scripts/      # planification de la collecte
├── sources/      # les 5 types de sources C1
├── src/          # appel du modèle
└── tests/        # pytest : 1 927 tests collectés (02/11)
```

L'architecture, avec le chemin d'un briefing et d'une question : [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).
La chaîne d'intégration et de livraison continues : [docs/CI-CD.md](docs/CI-CD.md).

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

Si la création d'environnement virtuel est bloquée (sur le poste du projet, Smart App Control de Windows refuse les
exécutables sans réputation, dont ceux d'un environnement virtuel), les tests s'exécutent aussi avec l'interpréteur
système :

```powershell
python -m pytest -q
```

> **Dernière exécution vérifiée : 1 878 réussis, 47 ignorés, 2 échecs attendus sur 1 927 collectés** (Python 3.14.6,
> Windows, 02/11/2026). Les 47 ignorés : les 24 tests qui demandent PostgreSQL (ci-dessous), et 23 tests qui ne
> tournent que sous Linux, dans la CI (simulations `bash`, `jq`, verrous de fichiers, liens symboliques).
> Les tests d'intégration PySpark de `tests/test_spark.py` sont **ignorés**, et non en échec, si aucun JDK 21 n'est
> présent dans `JAVA_HOME`.

### Les tests qui demandent PostgreSQL

Ces 24 tests portent le marqueur `postgresql`. Ils n'écrivent que dans une base de test déclarée : `DATABASE_URL` doit
viser une base dont le nom est celui de `RITA_BASE_DE_TEST`, sinon ils sont ignorés (`tests/garde_base.py`). Pour les
lancer seuls, sur une base de test chargée avec `db/schema.sql` puis `db/roles.sql` :

```powershell
python -m pytest -q -m postgresql tests
```

En CI, le job `base` les lance sur une base PostgreSQL 18 jetable et échoue si l'un d'eux est ignoré
([docs/CI-CD.md](docs/CI-CD.md)).

## RGPD

Le registre des traitements est dans
[db/RGPD-registre-des-traitements.md](db/RGPD-registre-des-traitements.md).
La purge des données personnelles est écrite et testée ([db/rgpd_purge.py](db/rgpd_purge.py)), déclenchable manuellement : sa
planification reste à faire (registre RGPD, § 5, point 3).

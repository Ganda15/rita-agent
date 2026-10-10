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

| Épreuve | Compétences | État au 10/10/2026 | Documents | 🔒 Livrable figé |
|---|---|---|---|---|
| **E1** : Données | C1–C5 | ✅ **livré** le 13/08 (26 critères / 28). **Version 2 rédigée le 03/10**, gel et tag `livrable-E1-v2` le **15/10** : dates de l'archive en date locale (INC-005), 10 tables, FRED stockée, vue sans taux supposé, clôture des positions, traçage UE, étape `ecb` en échec déclaré, 836 tests collectés (10/10) | [rapport-E1.pdf](docs/rapports/E1/rapport-E1.pdf) (v2.2, 5 pages) · [preuves C1 à C5](evidence/) | **[`livrable-E1-v1`](https://github.com/Ganda15/rita-agent/tree/livrable-E1-v1)** |
| **E2** : Veille & services IA | C6–C8 | 🟡 **le plus en retard**. C6 : protocole, 4 notes (S33 à S36) et leur synthèse PDF, un partage sans capture, S37 à S40 sans note ; C7 : **première comparaison mesurée le 03/10** (GPT-5.4 par Azure contre Claude par OpenRouter, 30 appels chacun, `evidence/C7/`), banc Azure contre Mistral Large 4 après le gel ; C8 : Azure en zone UE depuis le 09/10, OpenRouter en secours sur `develop`, Mistral Large 4 sur la branche `mistral-ue`, remise non prouvée (#43). Rapport : v0.3 du 09/10 (`docs/rapports/E2/`), partie C7 à écrire, dû le 05/11 | [docs/veille/](docs/veille/) · [evidence/C6/](evidence/C6/) | aucun |
| **E3** : API modèle & MLOps | C9–C13 | 🔨 **proche du gel** (15/10). API du modèle, garde-fous mesurés, 836 tests collectés (10/10), CI avec portes d'évaluation, traces et tableau de bord Langfuse, chaîne d'alerte, journal des appels MCP. Rapport v1.3 en relecture | [rapport-E3.pdf](docs/rapports/E3/rapport-E3.pdf) (v1.3, 20 pages) · [evidence/C11/](evidence/C11/) · [evidence/C12/](evidence/C12/) | aucun |
| **E4** : Application | C14–C19 | 🔨 **25 critères / 36** au recomptage du 03/10 (11 partiels) : 3 écrans, spécifications et schémas, pré-production Docker, intégration continue, `main` protégée par pull request et tests verts. Rapport : 0 page, gel le 25/10 | [evidence/C14/](evidence/C14/) · [evidence/C15/](evidence/C15/) · [evidence/C19/](evidence/C19/) | aucun |
| **E5** : Monitorage | C20–C21 | 🔨 **en construction** : jauge de fraîcheur, identifiant de requête dans journal et traces, alerte vers une issue, manifeste de collecte, journal des appels MCP ; 7 post-mortems d'incidents (INC-001 à INC-007). Rapport : 0 page, dû le 05/11 | [evidence/C20/](evidence/C20/) · [evidence/C21/](evidence/C21/) | aucun |

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
| Tests | **836 collectés** · **832 réussis**, 2 ignorés, 2 échecs attendus (`pytest -q` complet sur le poste, 10/10) |
| Base de données | **10 tables · 1 vue · 8 index créés explicitement · 12 contraintes CHECK** (compté dans `db/schema.sql`, 10/10) |
| Données en base | **273 608 lignes** importées en juillet (276 168 lues − 2 560 doublons) ; 278 473 cotations au 02/10 (mesure d'E1) |
| Archive big data | **11 partitions Parquet · 14 Mo · 10 ans** (29/07/2016 → 29/07/2026, dates locales de la place depuis INC-005) |
| API | **OpenAPI 3.1.0 · 14 chemins, 14 opérations, dont 11 chemins de données `/donnees`** (`app.openapi()`, 10/10) |

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
- **Modèle d'IA** : GPT-5.4 sur Azure AI Foundry (Data Zone EU) en premier, Claude par Anthropic puis OpenRouter en
  secours, sans garantie de traitement dans l'UE (remplacement par Mistral Large 4 prévu après le gel, carte #82) :
  modèle **fourni**, aucun entraînement
- **Orchestration** : LangGraph
- **CI** : GitHub Actions — tests + **porte d'évaluation des garde-fous**

> **Présents au 10/10** : interface web de trois écrans (`frontend/`), conteneurisation (`Dockerfile`, `Dockerfile.tests`,
> `docker-compose.yml`), cinq workflows GitHub Actions (tests, livraison, revue des pull requests, scan Giskard, alerte
> d'incident), traces Langfuse avec deux alertes réglées. **Pas encore** : restitution en temps réel ; le serveur en
> ligne sert le code du 19/08.

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
├── frontend/     # interface web : trois écrans (C10, E4)
├── graph/        # LangGraph — état + workflow
├── guardrails/   # garde-fou injection de prompt
├── pipelines/    # ingestion
├── scripts/      # planification de la collecte
├── sources/      # les 5 types de sources C1
├── src/          # appel du modèle
└── tests/        # pytest : 836 tests collectés (10/10)
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

> **Dernière exécution vérifiée : 832 réussis, 2 ignorés, 2 échecs attendus sur 836 collectés, en 76,4 s** (Python 3.14.6, Windows, 10/10/2026).
> Les tests d'intégration PySpark de `tests/test_spark.py` sont **ignorés** — et non en
> échec — si aucun JDK 21 n'est présent dans `JAVA_HOME`.

## RGPD

Le registre des traitements est dans
[db/RGPD-registre-des-traitements.md](db/RGPD-registre-des-traitements.md).
La purge des données personnelles est écrite et testée ([db/rgpd_purge.py](db/rgpd_purge.py)), lancée à la main : sa
planification reste à faire (registre RGPD, § 5, point 3).

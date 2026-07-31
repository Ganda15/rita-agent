# C1 — Automatiser l'extraction de données

> **Énoncé officiel (France Compétences, RNCP37827)** : « Automatiser l'extraction de données
> depuis un service web, une page web (scraping), un fichier de données, une base de données et
> un système big data en programmant le script adapté afin de pérenniser la collecte des
> données nécessaires au projet. »
>
> **Critère évalué (grille Simplon)** — celui qui porte sur les sources : « L'extraction des
> données est faite depuis **un mix entre au moins** les sources suivantes : un service web
> (API REST), un fichier de données, un scraping, une base de données et un système big data. »

## Les 7 sources et les 5 types

| # | Source | Type C1 | Fichier | Preuve | État |
|---|---|---|---|---|---|
| 1 | yfinance / OpenBB | **service web** | `agents/scout.py` | `preuve-01-yfinance.md` | ✅ |
| 2 | FRED (macro US) | **service web** | `sources/fred.py` | — | ⬜ |
| 3 | ECB (macro UE) | **service web** | `sources/ecb.py` | `preuve-03-ecb.md` | ✅ |
| 4 | RSS actualités | *complément* | `sources/rss.py` | `preuve-04-rss.md` | ✅ |
| 5 | Scraper HTML | **page web (scraping)** | `sources/scraper.py` | `preuve-05-scraper.md` | ✅ |
| 6 | CSV positions | **fichier de données** | `pipelines/ingest.py` | — | ⬜ |
| 7 | PDF officiels | **fichier de données** | `pipelines/rag.py` (Q3) | — | ⬜ |
| — | PostgreSQL relu en SQL | **base de données** | `db/requetes.sql` | → voir `C2/` | ⬜ |
| — | **Big data** | **système big data** | `bigdata/build_parquet.py` | `preuve-08-bigdata-parquet.md` | 🔶 étape 1/4 |

**Couverture visée : 5 types sur 5** (4 par le pipeline principal + 1 par la preuve big data
séparée).

## 🧾 Preuves attendues en plus des critères (Règlement p. 53)

Le règlement spécifique liste, **séparément des 135 critères**, les éléments de preuve que
le jury s'attend à voir pour le Bloc 1. Repéré le 31/07/2026 en relisant les PDF sources.

| Élément attendu | Preuve | État |
|---|---|---|
| Script de récupération des données | `scout.py`, `ecb.py`, `build_parquet.py` | ✅ |
| **Résultats de l'analyse exploratoire** | `preuve-09-analyse-exploratoire.md` | ✅ |
| Script de pré-traitement (dont **dédoublonnage**) | `../C3/preuve-dedoublonnage-cgg.md` | 🔶 documenté, à coder dans `ingest.py` v2 |
| Conception BDD **« orientée requêtes »** | plan 5.2 Task 1 | ⬜ justification à réécrire |
| Procédure de création de la BDD | plan 5.2 Task 1 | ⬜ |
| Script d'insertion en base | plan 5.2 Task 5 | ⬜ |

## 🔶 Big data — étape 1 sur 4

Le formateur a accepté d'ajouter le big data **séparément** (*« Yeah. It is. »*) et a annoncé
qu'il examinerait le schéma (*« Yep. I'll do that. »*).

Étape 1 faite : jeu Parquet partitionné par année, 276 168 lignes, *predicate pushdown*
mesuré à 9,4×. Étapes 2-4 (PySpark, extraction Spark, Spark SQL) non commencées.

**Question à lui poser, jamais posée à ce jour** : la preuve big data doit-elle couvrir
**C1 seulement** (extraction depuis un système big data), ou **aussi C2** (requêtes SQL sur ce
système, type Spark SQL) ?

Voir `bigdata/CONCEPTION.md`.

## Les 6 autres critères de C1

Le critère « mix de sources » n'est qu'un des 7. Les autres :

| Critère | Preuve | État |
|---|---|---|
| Présentation du projet et de son contexte complète | livrable E1 (Q6) | ⬜ |
| Spécifications techniques (technos, services externes, langages, accessibilité) | livrable E1 (Q6) | ⬜ |
| Périmètre des spécifications complet (extraction + agrégation) | livrable E1 (Q6) | ⬜ |
| **Script d'extraction fonctionnel** — toutes les données visées récupérées | sortie réelle par source | partiel |
| **Script structuré** : lancement, init dépendances/connexions, logique, gestion erreurs, fin, sauvegarde | `pipelines/ingest.py` v2 | ⬜ |
| **Script versionné et accessible depuis un dépôt Git** | `github.com/Ganda15/rita-agent` ⚠️ **encore privé** | partiel |

⚠️ Le dépôt doit être **accessible au jury** avant le 05/11 — sinon ce critère tombe.

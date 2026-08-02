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
| 2 | **FRED** — macro US | **service web** | `sources/fred.py` | `preuve-02-fred.md` | ✅ |
| 3 | BCE — taux de change | **service web** | `sources/ecb.py` | `preuve-03-ecb.md` | ✅ |
| 4 | RSS actualités | *complément* | `sources/rss.py` | `preuve-04-rss.md` | ✅ |
| 5 | Boursorama | **page web (scraping)** | `sources/scraper.py` | `preuve-05-scraper.md` | ✅ |
| 6 | CSV positions | **fichier de données** | `sources/positions.py` | `preuve-06-positions-csv.md` | ✅ |
| 7 | PostgreSQL relu en SQL | **base de données** | `sources/database.py` | `preuve-07-base-de-donnees.md` | ✅ |
| 8 | Parquet + Spark | **système big data** | `bigdata/extract_spark.py`<br>`bigdata/query_spark.py` | `preuve-08-bigdata-parquet.md`<br>`preuve-bigdata-spark.md` | ✅ |

✅ **Les 5 types sont couverts, tous aboutis.** Le critère demande « un mix entre **au moins** »
ces sources — RITA les couvre **toutes les cinq**.

### Une source reportée — et pourquoi

| Source | Décision | Raison |
|---|---|---|
| **PDF officiels** | ⏭ **reportée** | Le type « fichier de données » est déjà couvert par le CSV. Les PDF relèvent du RAG documentaire, prévu au chantier Q3 — **hors périmètre de E1**. |

> **Note du 02/08/2026.** FRED figurait ici comme « écartée ». C'était une **décision que je
> n'avais pas à inscrire** : le plan du 28/07 la prévoyait, elle était seulement **bloquée** par
> l'absence de clé. La clé obtenue le 02/08, le module a été codé — `sources/fred.py`,
> 9 tests. Elle est désormais dans le tableau des sources actives.

## 🧾 Preuves attendues en plus des critères (Règlement p. 53)

Le règlement spécifique liste, **séparément des 135 critères**, les éléments de preuve que
le jury s'attend à voir pour le Bloc 1. Repéré le 31/07/2026 en relisant les PDF sources.

| Élément attendu | Preuve | État |
|---|---|---|
| Script de récupération des données | `scout.py`, `ecb.py`, `build_parquet.py` | ✅ |
| **Résultats de l'analyse exploratoire** | `preuve-09-analyse-exploratoire.md` | ✅ |
| Script de pré-traitement (dont **dédoublonnage**) | `../C3/preuve-dedoublonnage-cgg.md` · `db/importer.py` | ✅ codé — 2 560 doublons écartés à l'import |
| Conception BDD **« orientée requêtes »** | `db/schema.sql` + `db/README.md` §6 | ✅ index mesurés par `EXPLAIN ANALYZE` |
| Procédure de création de la BDD | `db/README.md` §2-§5 | ✅ rejouée depuis une base vierge |
| Script d'insertion en base | `db/importer.py` | ✅ 273 608 lignes insérées |

## ✅ Big data — 4 étapes sur 4 (terminé le 02/08/2026)

Le formateur a accepté d'ajouter le big data **séparément** (*« Yeah. It is. »*) et a annoncé
qu'il examinerait le schéma (*« Yep. I'll do that. »*).

| Étape | Contenu | Preuve |
|---|---|---|
| 1 | Jeu Parquet partitionné par année — 276 168 lignes, *predicate pushdown* mesuré à 9,4× | `preuve-08-bigdata-parquet.md` |
| 2 | Session Spark 4.2.0 sur JDK Temurin 21 (SHA256 vérifié) | `bigdata/session_spark.py` |
| 3 | Extraction programmatique — *partition pruning* : 11 fichiers connus, **1 seul lu** | `preuve-bigdata-spark.md` |
| 4 | 3 requêtes **Spark SQL** — volumétrie, amplitude, fenêtrage `LAG` + `RANK` | `bigdata/query_spark.py` |

**La question posée au formateur — C1 seul, ou C2 aussi ?** — n'a toujours pas reçu de réponse,
mais elle n'est plus bloquante : **les deux sont couvertes**. L'étape 3 répond à C1 (connexion
et extraction depuis un système big data), l'étape 4 à C2 (requêtes dans le langage propre au
système). Reste à la lui poser pour confirmation.

Voir `bigdata/CONCEPTION.md`.

## Les 6 autres critères de C1

Le critère « mix de sources » n'est qu'un des 7. Les autres :

| Critère | Preuve | État |
|---|---|---|
| Présentation du projet et de son contexte complète | `docs/rapports/E1/rapport-E1.pdf` §1 | ✅ |
| Spécifications techniques (technos, services externes, langages, accessibilité) | `docs/rapports/E1/rapport-E1.pdf` §2 | ✅ |
| Périmètre des spécifications complet (extraction + agrégation) | `docs/rapports/E1/rapport-E1.pdf` §2 | ✅ |
| **Script d'extraction fonctionnel** — toutes les données visées récupérées | sortie réelle par source, 8 preuves | ✅ |
| **Script structuré** : lancement, init dépendances/connexions, logique, gestion erreurs, fin, sauvegarde | `pipelines/ingest.py` — repères `[1]` à `[6]` | ✅ |
| **Script versionné et accessible depuis un dépôt Git** | `github.com/Ganda15/rita-agent` ⚠️ **encore privé** | partiel |

⚠️ Le dépôt doit être **accessible au jury** avant le 05/11 — sinon ce critère tombe.

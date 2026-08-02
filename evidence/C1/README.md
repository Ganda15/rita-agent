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
| 2 | BCE — taux de change | **service web** | `sources/ecb.py` | `preuve-03-ecb.md` | ✅ |
| 3 | RSS actualités | *complément* | `sources/rss.py` | `preuve-04-rss.md` | ✅ |
| 4 | Boursorama | **page web (scraping)** | `sources/scraper.py` | `preuve-05-scraper.md` | ✅ |
| 5 | CSV positions | **fichier de données** | `sources/positions.py` | `preuve-06-positions-csv.md` | ✅ |
| 6 | PostgreSQL relu en SQL | **base de données** | `sources/database.py` | `preuve-07-base-de-donnees.md` | ✅ |
| 7 | Parquet + Spark | **système big data** | `bigdata/extract_spark.py`<br>`bigdata/query_spark.py` | `preuve-08-bigdata-parquet.md`<br>`preuve-bigdata-spark.md` | ✅ |

✅ **Les 5 types sont couverts, tous aboutis.** Le critère demande « un mix entre **au moins** »
ces sources — RITA les couvre **toutes les cinq**.

### Deux sources envisagées puis écartées — et pourquoi

| Source | Décision | Raison |
|---|---|---|
| **FRED** (macro US) | ❌ **écartée** | Ce serait une **deuxième** source de type « service web », en doublon avec la BCE. Elle n'apporterait **aucun type de source nouveau**, donc aucun critère supplémentaire. Ajouter une source pour le nombre plutôt que pour le besoin serait un mauvais argument devant le jury. |
| **PDF officiels** | ⏭ **reportée** | Le type « fichier de données » est déjà couvert par le CSV. Les PDF relèvent du RAG documentaire, prévu au chantier Q3 — **hors périmètre de E1**. |

> ⚠️ Ces deux lignes étaient auparavant marquées « ⬜ à faire », ce qui laissait croire à un
> manque. Ce n'en était pas un : le besoin auquel elles répondaient est couvert autrement.
> Corrigé le 02/08/2026.

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
| Présentation du projet et de son contexte complète | livrable E1 (Q6) | ⬜ |
| Spécifications techniques (technos, services externes, langages, accessibilité) | livrable E1 (Q6) | ⬜ |
| Périmètre des spécifications complet (extraction + agrégation) | livrable E1 (Q6) | ⬜ |
| **Script d'extraction fonctionnel** — toutes les données visées récupérées | sortie réelle par source | partiel |
| **Script structuré** : lancement, init dépendances/connexions, logique, gestion erreurs, fin, sauvegarde | `pipelines/ingest.py` v2 | ⬜ |
| **Script versionné et accessible depuis un dépôt Git** | `github.com/Ganda15/rita-agent` ⚠️ **encore privé** | partiel |

⚠️ Le dépôt doit être **accessible au jury** avant le 05/11 — sinon ce critère tombe.

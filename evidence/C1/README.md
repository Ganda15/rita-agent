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
| 3 | ECB (macro UE) | **service web** | `sources/ecb.py` | — | ⬜ |
| 4 | RSS actualités | *complément* | `sources/rss.py` | — | ⬜ |
| 5 | Scraper HTML | **page web (scraping)** | `sources/scraper.py` | — | ⬜ |
| 6 | CSV positions | **fichier de données** | `pipelines/ingest.py` | — | ⬜ |
| 7 | PDF officiels | **fichier de données** | `pipelines/rag.py` (Q3) | — | ⬜ |
| — | PostgreSQL relu en SQL | **base de données** | `db/requetes.sql` | → voir `C2/` | ⬜ |
| — | **Big data** | **système big data** | `bigdata/` (isolé) | ⏸ **en attente formateur** | ⏸ |

**Couverture visée : 5 types sur 5** (4 par le pipeline principal + 1 par la preuve big data
séparée).

## ⏸ Big data — en attente

Le formateur a accepté d'ajouter le big data **séparément** (*« Yeah. It is. »*) et a annoncé
qu'il examinerait le schéma (*« Yep. I'll do that. »*).

**Question à lui poser, jamais posée à ce jour** : la preuve big data doit-elle couvrir
**C1 seulement** (extraction depuis un système big data), ou **aussi C2** (requêtes SQL sur ce
système, type Spark SQL) ?

**Rien n'est codé côté big data avant sa réponse.** Voir `bigdata/CONCEPTION.md`.

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

# Preuve C15.3 : le diagramme de flux de données, version du 02/11/2026

> **Critère C15.3** : *« Les flux de données impliqués dans l'application sont représentés par un diagramme de flux de
> données. »* Ligne C15.3 du [registre de la recette](../../docs/recette/registre-des-partiels.md).

**Date** : 2026-11-02 · **Code relevé** : commit `dd3c065` (`develop`)

## Pourquoi une nouvelle version

Le diagramme du 18/08 ([`FLUX-DONNEES-C15-application-RITA.png`](FLUX-DONNEES-C15-application-RITA.png)) est **gardé
tel quel** : il dit ce qu'était RITA en août. Il ne montre ni l'écran Question, ni l'index des articles, ni la
passerelle MCP, ni la vigie, ni Langfuse, et il décrit un appel au modèle en cascade de trois fournisseurs qui n'est
plus le fonctionnement par défaut. La nouvelle version est **relevée sur le code**, flux par flux ; chaque ligne du
tableau ci-dessous dit où le flux se lit. Comme en août, **le sens des flèches est celui de la donnée**, pas celui de
la requête.

![Diagramme de flux de données de RITA au 02/11/2026, en cinq colonnes. Sources externes : cours de bourse (Yahoo Finance, Boursorama), taux et séries macro (BCE, FRED), presse (flux RSS), fichier de positions, donnée personnelle. Collecte : pipelines/ingest.py écrit dans PostgreSQL, dans l'index des articles et dans les journaux ; les articles passent d'abord par le garde-fou d'injection ; db/importer.py écrit l'univers, l'archive et les positions. Stockage : PostgreSQL, l'index ChromaDB, les journaux. API, avec la clé : GET /donnees lit la base, dont les positions, et sert le navigateur et la passerelle MCP ; POST /briefing lit la base et l'index ; POST /question lit l'index, reçoit la question du navigateur et écrit une ligne de journal sans le texte ; GET /sante et /health. Destinataires : le navigateur et ses cinq écrans, la passerelle MCP, le modèle fourni en zone UE, Langfuse en région UE qui ne reçoit que des métadonnées, et GitHub, où la vigie et l'alerte de Langfuse ouvrent des issues.](flux/FLUX-DONNEES-C15-application-RITA-2026-11-02.png)

Sources modifiables (`.drawio`), générateur et commande de rendu : [`flux/`](flux/README.md).

## Les flux, un par un, et où ils se lisent

| De → vers | Ce qui passe | Où le lire |
|---|---|---|
| cours, taux, séries macro → collecte | cotations, taux de change, séries | `sources/cotations.py`, `sources/scraper.py`, `sources/ecb.py`, `sources/fred.py` ; `pipelines/ingest.py` (six étapes) |
| presse → garde-fou → collecte | articles, neutralisés contre l'injection dès la collecte | `sources/rss.py:26`, `sources/scraper.py:44` (`neutraliser`) |
| fichier de positions → `db/importer.py` → PostgreSQL | **donnée personnelle** : quantités et prix de revient | `db/importer.py`, `importer_positions` ; registre RGPD, traitement T1 |
| collecte → PostgreSQL, index, journaux | lignes en base ; passages vectorisés ; journal de collecte | `pipelines/ingest.py`, `rag/indexation.py`, `logs/` |
| PostgreSQL → `GET /donnees/*` → navigateur | données de marché et **positions** (écran Portefeuille) | `api/donnees.py`, route `/portefeuille` |
| `GET /donnees/*` → passerelle MCP | trois outils en lecture ; le portefeuille seulement s'il est le jeu de démonstration vérifié | `passerelle_mcp/serveur.py` (#152) |
| PostgreSQL et index → `POST /briefing` → modèle | faits de marché et passages ; **aucune position** (le scout ne lit pas le portefeuille) | `graph/workflow.py`, `agents/scout.py`, `agents/analyst.py:4` (passages neutralisés de nouveau) |
| navigateur → `POST /question` ; index → `/question` → modèle | la question et les passages retenus | `agents/question.py:26`, `rag/recherche.py` |
| `/question` → journaux | une ligne par question : identifiant, statut, motif, longueur, identifiants cités, durée ; **jamais le texte** | `api/question.py:7-10` |
| `/briefing`, `/question` → Langfuse | **métadonnées seulement** (fournisseur, modèle, jetons, type d'erreur) ; jamais le prompt ni le texte (décision D9, 20/10) | `src/traces.py`, docstring |
| `/briefing`, `/question`, `/sante` → navigateur | les réponses ; l'état du service pour le tableau de bord | `frontend/briefing.js`, `question.js`, `tableau-de-bord.js` |
| `/sante` → vigie → GitHub | un verdict par signal ; une issue par signal en problème | `monitorage/vigie.py` (issues par `gh`) |
| Langfuse → GitHub | une alerte ouvre une issue | `.github/workflows/alerte-incident.yml` (`repository_dispatch`, type `alerte-langfuse`) |

## Ce qui a changé depuis le 18/08

| Au 18/08 | Au 02/11 |
|---|---|
| 8 tables, 1 vue | 10 tables, 1 vue (dont `mcp_calls` et `memory_audit`) |
| un écran, le portefeuille | cinq écrans |
| graphe de deux nœuds | trois nœuds (base, articles, rédacteur) et un index ChromaDB |
| appel au modèle en cascade de trois fournisseurs | Azure AI Foundry, zone UE, seul par défaut depuis le 31/10 |
| ni Question, ni passerelle MCP, ni vigie, ni Langfuse | les quatre, avec leurs flux |

## Limites, dites franchement

- Le texte que rend le modèle n'a pas de flèche à lui : la boîte du modèle dit « rend le texte ». Onze flux se
  croisent déjà entre l'API et ses destinataires.
- La collecte du poste (chaque soir) et l'ingestion de la production (à la demande, flux RSS seulement) sont dans une
  même boîte.
- Ne sont pas dessinés : les routes d'exercice (`/exercice/*`, refusées en production), la purge RGPD (`db/rgpd_purge.py`,
  qui écrit `memory_audit`), le journal des refus de la passerelle (`POST /audit/mcp`), les sauvegardes.
- Le diagramme est relevé : il décrit l'existant, il n'a pas précédé le code.

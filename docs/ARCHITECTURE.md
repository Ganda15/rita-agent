# Architecture de RITA

> **À quoi sert ce document.** Décrire en un seul endroit de quoi RITA est faite, comment une demande la traverse, où
> vivent les données, comment l'accès est contrôlé, comment le modèle est surveillé et comment le code est livré.
> Chaque brique renvoie à son dossier et aux tests qui la prouvent. Critères visés : C9 (« la documentation couvre
> l'architecture, tous les points de terminaison et les règles d'authentification ») et C17 (documentation technique).
> État du code : 4 octobre 2026, branche `develop`. Les schémas sont dans `docs/rapports/E3/schemas/` (un `.drawio` pour
> corriger, un `.png` pour lire, générés par un seul script).

## 1. RITA en une phrase

Une application mono-utilisateur qui **collecte** chaque soir des données de marché et d'actualité, les **range** dans
PostgreSQL, les **expose** par une API REST, et fait **rédiger** par un modèle de langage fourni (aucun entraînement)
un court briefing en français sur une valeur, **relu par un garde-fou** qui retient toute recommandation d'achat ou de
vente (contrainte AMF). Aide à la lecture, jamais un conseil.

## 2. Les trois chemins

| Chemin | Quand | De → vers | Schéma |
|---|---|---|---|
| **Collecte** | chaque soir à 19 h (tâche planifiée Windows) | sources externes → `pipelines/ingest.py` → PostgreSQL et index ChromaDB | `E3-architecture` (bas) ; rapport E1 |
| **Lecture de données** | à la demande | écran ou passerelle MCP → `GET /donnees/*` → PostgreSQL | `E3-architecture` |
| **Briefing** | à la demande | écran ou passerelle MCP → `POST /briefing` → graphe → modèle → garde-fou → réponse | `E3-architecture`, `E3-integration-briefing` |

![Le chemin d'un briefing](rapports/E3/schemas/E3-architecture.png)

## 3. Les briques, une par une

| Brique | Dossier | Rôle | Technologie | Tests principaux |
|---|---|---|---|---|
| Sources | `sources/` | une fonction par source : cours (Yahoo Finance), taux BCE, séries FRED, flux RSS, scraping, fichier de positions | Python, `httpx`, `feedparser`, `yfinance` | `test_cotations`, `test_ecb`, `test_fred`, `test_rss`, `test_scraper`, `test_positions` |
| Collecte | `pipelines/ingest.py` | six étapes indépendantes (taux, macro, cotations, articles, scraping, indexation), une étape en échec n'arrête pas les autres, un manifeste par exécution | Python | `test_ingest`, `test_manifeste_collecte`, `test_rattrapage` |
| Base | `db/` | schéma Merise (`schema.sql`, 10 tables, 1 vue), import (`importer.py`), rôle en lecture seule (`roles.sql`), purge RGPD (`rgpd_purge.py`) | PostgreSQL 18, port 5433 en local | `test_schema`, `test_importer`, `test_vue_valorisation`, `test_rgpd_purge`, `test_role_lecture` |
| Indicateurs | `indicateurs/` | 13 indicateurs par valeur (socle, risque, RSI) et 2 indicateurs de portefeuille, calculés en SQL | SQL avec fonctions fenêtre | `test_indicateurs_socle`, `_risque`, `_portefeuille` |
| Recherche documentaire | `rag/` | index des articles (`indexation.py`), recherche filtrée par valeur puis hybride dense et BM25 fusionnés par rangs (`recherche.py`, 3 passages) | ChromaDB, `rank-bm25` | `test_rag_indexation`, `test_rag_recherche`, `test_mesurer_rag` |
| Graphe | `graph/` | trois nœuds à arêtes fixes : `scout` (lit la base), `rag` (cherche les articles), `redacteur` (écrit) | LangGraph | `test_workflow`, `test_scout_base` |
| Rédacteur | `agents/analyst.py` | construit le prompt : les faits (cours, variation, capitaux moyens, 10 indicateurs, passages), la consigne AMF | Python | `test_analyst` |
| Appel au modèle | `src/llm.py` | cascade de fournisseurs approuvés UE : Azure AI Foundry (`gpt-5.4`, Data Zone EU), puis Mistral par son adresse européenne (carte #82) ; un fournisseur indisponible passe la main au suivant, un nom non approuvé est ignoré | `httpx` | `test_llm` |
| Garde-fous | `guardrails/` | **entrée** (`entree.py`, la question), **injection** (`injection.py`, les articles collectés), **sortie** (`sortie.py`, le texte produit) | motifs lexicaux | `test_entree`, `test_injection`, `test_evals` |
| API | `api/` | FastAPI : `/health`, 11 routes `/donnees/*`, `POST /briefing`, `POST /audit/mcp` ; documentation OpenAPI 3.1.0 sur `/docs` | FastAPI, Uvicorn | `test_health`, `test_api_donnees`, `test_request_id`, `test_audit_mcp` |
| Interface | `frontend/` | trois écrans : portefeuille, indicateurs, briefing ; aucune clé dans le code, la clé est saisie | HTML, CSS, JavaScript sans outil de construction | `test_frontend`, `test_smoke_ui` (vrai navigateur) |
| Passerelle MCP | `passerelle_mcp/serveur.py` | trois outils en lecture seule pour un assistant ; passe par l'API avec la clé, jamais par la base | protocole MCP | `test_passerelle_mcp` |
| Traçage | `src/traces.py` | une trace Langfuse par briefing, une étape par nœud et par garde-fou, une génération par tentative de fournisseur, identifiant = celui de la requête | Langfuse Cloud, région UE | `test_traces`, `test_trace_chemin`, `test_trace_verdict_amf` |
| Fraîcheur | `monitorage/fraicheur.py` | de quand datent les données, en jours ouvrés | SQL | `test_fraicheur` |

## 4. Les points de terminaison et l'authentification

La liste complète, avec les paramètres et les réponses, est le contrat **OpenAPI 3.1.0** que l'API publie elle-même
(`/openapi.json`, et sa lecture interactive sur `/docs`) ; le rapport E3 la résume en section 3.1 (14 chemins).

| Famille | Routes | Clé |
|---|---|---|
| Service | `GET /health` | **non** : ne rend aucune donnée |
| Données (C5) | `GET /donnees/valeurs`, `/cotations`, `/macro`, `/portefeuille`, `/mouvements`, `/volumes-anormaux`, `/articles`, `/indicateurs`, `/indicateurs-portefeuille`, `/indicateurs-risque`, `/fraicheur` | oui |
| Modèle (C9) | `POST /briefing?ticker=` | oui |
| Audit | `POST /audit/mcp` | oui |
| Interface | `/`, `/index.html`, `/indicateurs.html`, `/briefing.html` et leurs fichiers | non : aucune donnée, la clé est demandée à l'écran |

**Règles d'accès.** Une seule clé (`X-API-Key`), lue dans l'environnement, d'au moins 16 caractères, comparée à temps
constant ; l'API refuse de démarrer sans elle (aucune valeur par défaut depuis l'incident INC-001). La dépendance est posée
sur le routeur entier des données : une nouvelle route ne peut pas oublier la protection. Chaque réponse, y compris une
erreur, porte un identifiant `X-Request-ID`. Le choix d'une clé unique et ses limites sont défendus dans
`evidence/C17/preuve-droits-acces-2026-10-03.md` ; la revue de sécurité est `evidence/C17/revue-owasp-top10-2025-2026-10-03.md`.

## 5. Les données

| Réserve | Contenu | Écrite par | Lue par |
|---|---|---|---|
| PostgreSQL | référentiel des valeurs et alias, dix ans de cotations, taux de change, séries macro, articles, positions, journaux d'audit | `pipelines/ingest.py`, `db/importer.py` (seuls écrivains) | l'API et le graphe |
| ChromaDB | les articles découpés et vectorisés, reconstruit à chaque collecte | `rag/indexation.py` | le nœud `rag` |
| Fichiers | journaux de collecte (`logs/`), manifeste par exécution, archive Parquet du big data (`bigdata/`, hors image) | la collecte | l'humain, les preuves |

Ce qui part chez le fournisseur du modèle : le prompt du rédacteur seulement (cours, variation, capitaux moyens, dix
indicateurs, au plus trois extraits d'articles). **Aucune position, aucun prix de revient** : le nœud `scout` ne lit que
des données de marché publiques.

## 6. Le modèle, et ce qui l'entoure

Le modèle est **fourni** : RITA ne l'entraîne pas et ne le règle pas. Ce qui se teste et se surveille est son
**comportement sous garde-fous**. Trois garde-fous à trois places (la question, les articles collectés, le texte produit),
chacun mesuré par `evals/` et porté par une porte de qualité dans la chaîne. Le choix des fournisseurs est mesuré par le
banc C7 (`evals/benchmark_fournisseurs.py`, `evidence/C7/`).

## 7. La surveillance

Collecte des métriques par les traces Langfuse (latence, jetons, fournisseur, verdict du garde-fou) et le journal de l'API
(une ligne par briefing servi ou refusé, jamais le texte). Restitution par le tableau de bord « RITA C11 » et le bandeau de
fraîcheur de l'écran 1. Alerte : une règle Langfuse appelle GitHub, qui ouvre une issue « incident »
(`.github/workflows/alerte-incident.yml`). La suite de tests ne trace jamais (`tests/conftest.py`). Détail :
rapport E3, section 5, et le schéma `E3-monitorage`.

## 8. Les environnements et la livraison

| Environnement | Ce qui tourne | Comment |
|---|---|---|
| Poste de développement | API (port 8000), PostgreSQL (5433), collecte planifiée | `uvicorn`, tâche planifiée Windows |
| Pré-production locale | API et PostgreSQL en conteneurs | `docker compose up -d --build` (port 8001) |
| Intégration continue | tests, test des données, garde-fous, construction et vérification de l'image | GitHub Actions, cinq workflows (`docs/CI-CD.md`) |
| Production | API en conteneur derrière Caddy (HTTPS) | serveur Hetzner, déploiement manuel ; **sert le code du 19/08/2026** jusqu'au déploiement d'après le 15/10 |

`main` ne change que par une pull request relue, avec tests, gardes-fous et revue verts (règles GitHub). Un livrable est
un tag `livrable-E<n>-v<k>` posé sur `main` ; l'image n'est publiée qu'après sa vérification, et seulement sur un tag.

## 9. Ce que cette architecture ne fait pas

- Pas de comptes ni de rôles : un utilisateur, une clé.
- Pas de limite de débit, pas d'en-têtes de sécurité en production (revue OWASP, carte #75).
- L'API lit la base avec le rôle propriétaire, au lieu d'un rôle en lecture (carte #76).
- Pas de retour arrière outillé, pas de manifeste de version servi par l'API.
- Le graphe est linéaire : aucun choix de chemin n'est confié au modèle, par conception.

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **API REST** | interface qui expose des ressources par des adresses et des verbes HTTP (`GET`, `POST`) |
| **OpenAPI** | format standard qui décrit une API : routes, paramètres, réponses |
| **Graphe (LangGraph)** | enchaînement de nœuds qui se passent un état ; ici trois nœuds dans un ordre fixe |
| **Modèle fourni** | modèle de langage déjà entraîné, appelé par une API, que le projet n'entraîne pas |
| **Cascade de fournisseurs** | liste ordonnée de services de modèle : si le premier échoue, le suivant est essayé |
| **Garde-fou** | contrôle qui retient une entrée, un contenu collecté ou un texte produit interdit |
| **RAG** | génération augmentée par la recherche : le modèle reçoit des extraits d'articles trouvés pour la valeur |
| **BM25** | méthode de recherche par mots-clés, combinée ici à la recherche par sens (vecteurs) |
| **Trace** | enregistrement d'une requête et de chacune de ses étapes, avec durées et résultats |
| **Tag** | étiquette posée sur un commit précis ; le lien d'un livrable |

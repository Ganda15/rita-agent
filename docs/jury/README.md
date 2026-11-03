# Pour le jury : RITA en fichiers essentiels (E1 et E3)

> Ouvrez cette page depuis le tag du livrable, `livrable-E1-v6` ou `livrable-E3-v4` : chaque lien s'ouvre alors dans le
> code tel qu'il a été livré, et non dans le projet d'aujourd'hui. Le dépôt est privé : il faut y être invité en lecture.

## Les deux rapports

| Épreuve | Rapport | Ce qu'il couvre |
|---|---|---|
| E1 | [livret E1, 5 pages](../rapports/E1/rapport-E1.pdf) | C1 à C5 : collecte, requêtes, nettoyage, base et RGPD, API de données |
| E3 | [rapport E3, 20 pages](../rapports/E3/rapport-E3.pdf) | C9 à C13 : API du modèle, intégration, monitorage, tests, livraison continue |

Les preuves sont rangées par compétence dans [`evidence/`](../../evidence/README.md), chacune datée et constituée au fil
du travail.

## E1 : les données, de la collecte à l'API

| Compétence | Ce qu'on y vérifie | Où |
|---|---|---|
| C1, collecter | les cinq types de sources et la collecte du soir | [`sources/`](../../sources), [`pipelines/ingest.py`](../../pipelines/ingest.py), [preuves C1](../../evidence/C1/README.md) |
| C2, interroger | les requêtes documentées, en SQL et en Spark | [`db/requetes.sql`](../../db/requetes.sql), [`bigdata/`](../../bigdata), [preuve C2](../../evidence/C2/preuve-requetes-sql.md) |
| C3, nettoyer | chaque défaut mesuré devient une règle | [`db/importer.py`](../../db/importer.py), [`tests/test_importer.py`](../../tests/test_importer.py), [preuves C3](../../evidence/C3) |
| C4, modéliser | le MCD Merise, le schéma PostgreSQL, le rôle de lecture, le RGPD | [MCD du 02/11](../../evidence/C4/MCD-MERISE-RITA-2026-11-02.png) (celui du 01/08 est gardé à côté), [`db/schema.sql`](../../db/schema.sql), [`db/roles.sql`](../../db/roles.sql), [registre RGPD](../../db/RGPD-registre-des-traitements.md), [`db/rgpd_purge.py`](../../db/rgpd_purge.py) |
| C5, servir | l'API REST des données, protégée par une clé | [`api/donnees.py`](../../api/donnees.py), [`tests/test_api_donnees.py`](../../tests/test_api_donnees.py), [preuve C5](../../evidence/C5/preuve-api-jeu-de-donnees.md) |

## E3 : le modèle, exposé, intégré, surveillé, testé, livré

| Compétence | Ce qu'on y vérifie | Où |
|---|---|---|
| C9, exposer | l'API qui donne accès au modèle, ses clés et ses refus | [`api/main.py`](../../api/main.py), [`api/question.py`](../../api/question.py), [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md), [`tests/test_health.py`](../../tests/test_health.py), [preuve C9](../../evidence/C9/preuve-api-modele-2026-10-03.md) |
| C10, intégrer | l'interface web qui appelle `/briefing` et `/question`, la passerelle MCP | [`frontend/`](../../frontend), [`passerelle_mcp/serveur.py`](../../passerelle_mcp/serveur.py), [`tests/test_frontend.py`](../../tests/test_frontend.py), [`tests/test_smoke_ui.py`](../../tests/test_smoke_ui.py), [preuves C10](../../evidence/C10) |
| C11, monitorer | les traces sans texte, les métriques, les alertes, le tableau de bord | [`src/traces.py`](../../src/traces.py), [`monitorage/`](../../monitorage), [`alerte-incident.yml`](../../.github/workflows/alerte-incident.yml), [`docs/exploitation.md`](../exploitation.md), [preuves C11](../../evidence/C11/README.md) |
| C12, tester | la stratégie, la couverture, les portes d'évaluation des garde-fous | [`tests/`](../../tests), [`evals/`](../../evals), [`tests/test_evals.py`](../../tests/test_evals.py), [`.coveragerc`](../../.coveragerc), [`docs/LLMOPS.md`](../LLMOPS.md), [preuves C12](../../evidence/C12) |
| C13, livrer | les workflows, l'image, la mise en service et le retour arrière | [`livraison.yml`](../../.github/workflows/livraison.yml), [`test.yml`](../../.github/workflows/test.yml), [`retour-arriere.yml`](../../.github/workflows/retour-arriere.yml), [`deploy/deployer.py`](../../deploy/deployer.py), [`Dockerfile`](../../Dockerfile), [`docs/CI-CD.md`](../CI-CD.md), [preuve C13](../../evidence/C13/preuve-chaine-livraison-2026-10-03.md) |

## Le modèle et ses garde-fous

| Pièce | Rôle | Où |
|---|---|---|
| L'appel au modèle | la cascade de fournisseurs | [`src/llm.py`](../../src/llm.py) |
| Le briefing | le graphe : lecture de la base, recherche des articles, rédaction | [`graph/workflow.py`](../../graph/workflow.py) |
| La question | garde-fous, recherche, réponse au format JSON imposé | [`agents/question.py`](../../agents/question.py) |
| Garde-fou d'entrée | l'intention de recommandation, interdite par l'AMF | [`guardrails/entree.py`](../../guardrails/entree.py) |
| Garde-fou de sortie | une recommandation ou une fuite retenue avant l'affichage | [`guardrails/sortie.py`](../../guardrails/sortie.py) |
| La Definition of Done | ce qu'un livrable doit passer avant son tag | [`scripts/verifier_livrable.py`](../../scripts/verifier_livrable.py) |

Les chiffres des rapports se reproduisent avec les commandes de leur section « Reproduire ».

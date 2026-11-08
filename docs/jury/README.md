# Pour le jury : RITA en fichiers essentiels (E1 à E5)

> Ouvrez cette page depuis le tag d'un livrable : chaque lien s'ouvre alors dans le code tel qu'il a été remis, et non
> dans le projet d'aujourd'hui. Tags de la remise du 09/11/2026 : `livrable-E1-v8`, `livrable-E2-v5`, `livrable-E3-v6`,
> `livrable-E4-v7`, `livrable-E5-v5`. Le dépôt est privé : l'accès du jury est à organiser pour l'examen (dépôt public
> ou accès en lecture).

## Les cinq rapports

| Épreuve | Rapport | Ce qu'il couvre |
|---|---|---|
| E1 | [livret E1 v8, 5 pages et 4 d'annexes](../rapports/E1/rapport-E1-v8-avec-annexes.pdf) | C1 à C5 : collecte, requêtes, nettoyage, base et RGPD, API de données |
| E2 | [rapport E2 v1.6, 18 pages et 14 d'annexes](../rapports/E2/rapport-E2-avec-annexe.pdf) | C6 à C8 : veille, choix du service de modèle, configuration et suivi |
| E3 | [rapport E3 v2.5, 20 pages](../rapports/E3/rapport-E3.pdf) | C9 à C13 : API du modèle, intégration, monitorage, tests, livraison continue |
| E4 | [rapport E4 v1.10, 20 pages et 15 d'annexes](../rapports/E4/rapport-E4-avec-annexe.pdf) | C14 à C19 : besoin, cadre technique, méthode agile, développement, tests, livraison |
| E5 | [rapport E5 v1.1, 5 pages](../rapports/E5/rapport-E5.pdf) | C20 et C21 : monitorage de l'application, résolution d'un incident |

Les preuves sont rangées par compétence dans [`evidence/`](../../evidence/README.md), chacune datée et constituée au fil
du travail. Chaque rapport se termine par sa grille : une ligne par critère, avec sa preuve et sa limite.

## E1 : les données, de la collecte à l'API

| Compétence | Ce qu'on y vérifie | Où |
|---|---|---|
| C1, collecter | les cinq types de sources et la collecte du soir | [`sources/`](../../sources), [`pipelines/ingest.py`](../../pipelines/ingest.py), [preuves C1](../../evidence/C1/README.md) |
| C2, interroger | les requêtes documentées, en SQL et en Spark | [`db/requetes.sql`](../../db/requetes.sql), [`bigdata/`](../../bigdata), [preuve C2](../../evidence/C2/preuve-requetes-sql.md) |
| C3, nettoyer | chaque défaut mesuré devient une règle | [`db/importer.py`](../../db/importer.py), [`tests/test_importer.py`](../../tests/test_importer.py), [preuves C3](../../evidence/C3) |
| C4, modéliser | le MCD Merise, le schéma PostgreSQL, le rôle de lecture, le RGPD | [MCD du 02/11](../../evidence/C4/MCD-MERISE-RITA-2026-11-02.png) (celui du 01/08 est gardé à côté), [`db/schema.sql`](../../db/schema.sql), [`db/roles.sql`](../../db/roles.sql), [registre RGPD](../../db/RGPD-registre-des-traitements.md), [`db/rgpd_purge.py`](../../db/rgpd_purge.py) |
| C5, servir | l'API REST des données, protégée par une clé | [`api/donnees.py`](../../api/donnees.py), [`tests/test_api_donnees.py`](../../tests/test_api_donnees.py), [preuve C5](../../evidence/C5/preuve-api-jeu-de-donnees.md) |

## E2 : la veille, le choix du service de modèle, sa configuration

| Compétence | Ce qu'on y vérifie | Où |
|---|---|---|
| C6, veiller | le protocole, les notes de veille, la qualification des sources | [`docs/veille/`](../veille/README.md), [preuves C6](../../evidence/C6/README.md) |
| C7, choisir | les bancs des services, l'adéquation service par service et usage par usage | [banc du 03/10](../../evidence/C7/preuve-benchmark-2026-10-03.md), [banc du 07/11](../../evidence/C7/banc-2026-11-07-comparaison/README.md) |
| C8, configurer | le service retenu, sa configuration, sa surveillance, la règle UE | [`src/llm.py`](../../src/llm.py), [preuves C8](../../evidence/C8/README.md), [registre RGPD](../../db/RGPD-registre-des-traitements.md) |

## E3 : le modèle, exposé, intégré, surveillé, testé, livré

| Compétence | Ce qu'on y vérifie | Où |
|---|---|---|
| C9, exposer | l'API qui donne accès au modèle, ses clés et ses refus | [`api/main.py`](../../api/main.py), [`api/question.py`](../../api/question.py), [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md), [`tests/test_health.py`](../../tests/test_health.py), [preuve C9](../../evidence/C9/preuve-api-modele-2026-10-03.md) |
| C10, intégrer | l'interface web qui appelle `/briefing` et `/question`, la passerelle MCP | [`frontend/`](../../frontend), [`passerelle_mcp/serveur.py`](../../passerelle_mcp/serveur.py), [`tests/test_frontend.py`](../../tests/test_frontend.py), [`tests/test_smoke_ui.py`](../../tests/test_smoke_ui.py), [preuves C10](../../evidence/C10) |
| C11, monitorer | les traces sans texte, les métriques, les alertes, le tableau de bord | [`src/traces.py`](../../src/traces.py), [`monitorage/`](../../monitorage), [`alerte-incident.yml`](../../.github/workflows/alerte-incident.yml), [`docs/exploitation.md`](../exploitation.md), [preuves C11](../../evidence/C11/README.md) |
| C12, tester | la stratégie, la couverture, les portes d'évaluation des garde-fous | [`tests/`](../../tests), [`evals/`](../../evals), [`tests/test_evals.py`](../../tests/test_evals.py), [`.coveragerc`](../../.coveragerc), [`docs/LLMOPS.md`](../LLMOPS.md), [preuves C12](../../evidence/C12) |
| C13, livrer | les workflows, l'image, la mise en service et le retour arrière | [`livraison.yml`](../../.github/workflows/livraison.yml), [`test.yml`](../../.github/workflows/test.yml), [`retour-arriere.yml`](../../.github/workflows/retour-arriere.yml), [`deploy/deployer.py`](../../deploy/deployer.py), [`Dockerfile`](../../Dockerfile), [`docs/CI-CD.md`](../CI-CD.md), [preuve C13](../../evidence/C13/preuve-chaine-livraison-2026-10-03.md) |

## E4 : l'application, du besoin à la livraison

| Compétence | Ce qu'on y vérifie | Où |
|---|---|---|
| C14, analyser | les spécifications, les parcours, les user stories et leurs critères | [preuves C14](../../evidence/C14), [spécification 001](../../specs/001-refonte-interface/spec.md) |
| C15, cadrer | l'architecture, le flux de données, les environnements | [`docs/ARCHITECTURE.md`](../ARCHITECTURE.md), [preuves C15](../../evidence/C15) |
| C16, coordonner | la méthode agile, ses cycles, ses rôles et le pilotage | [`docs/PILOTAGE-AGILE.md`](../PILOTAGE-AGILE.md), [preuves C16](../../evidence/C16) |
| C17, développer | l'interface, les droits d'accès, l'éco-conception, la revue OWASP | [`frontend/`](../../frontend), [`api/`](../../api), [preuves C17](../../evidence/C17) |
| C18, tester | les tests automatisés, la couverture, la chaîne de tests | [`tests/`](../../tests), [`test.yml`](../../.github/workflows/test.yml), [`docs/CI-CD.md`](../CI-CD.md) |
| C19, livrer | la livraison continue, l'image, les tags protégés | [`livraison.yml`](../../.github/workflows/livraison.yml), [`deploy/`](../../deploy), [preuves C19](../../evidence/C19) |

## E5 : surveiller l'application et résoudre un incident

| Compétence | Ce qu'on y vérifie | Où |
|---|---|---|
| C20, surveiller | les signaux et leurs seuils, la vigie planifiée, les alertes | [`monitorage/seuils.json`](../../monitorage/seuils.json), [`monitorage/vigie.py`](../../monitorage/vigie.py), [`vigie.yml`](../../.github/workflows/vigie.yml), [preuve du 07/11](../../evidence/C20/vigie-2026-11-07/README.md) |
| C21, résoudre | l'incident INC-009, de la détection à la correction versionnée | [preuves C21](../../evidence/C21/README.md), [post-mortem INC-009](../../evidence/C21/INC-009-retour-a-la-normale-ouvre-un-incident.md) |

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

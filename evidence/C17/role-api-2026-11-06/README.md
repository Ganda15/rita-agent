# Carte #76, tâche T5 : le rôle `rita_api` essayé sur une copie, avant la production, 6 novembre 2026

**Pourquoi.** Le plan de la carte #76 (`docs/PLAN-76-role-api.md`), validé par Era le 06/11, demande d'essayer le
changement sur une copie avant de toucher la production. La preuve attendue : les lectures et l'audit fonctionnent ; les
écritures métier et les changements de structure sont refusés.

## Les conditions

| Élément | Valeur |
|---|---|
| Code | branche `role-api-76`, commit `d065116` (tâches T1 à T4) |
| Copie | une pile de démonstration neuve sur le poste : projet Compose `rita-demo-t76`, ses propres volumes, port `8076` (`docker-compose.yml` et `docker-compose.demo.yml`), image construite depuis le code ; jeu de démonstration chargé par le service `initialisation` |
| Secrets | mots de passe et clé d'API **jetables**, tirés dans le processus de l'essai, jamais écrits dans un fichier du dépôt ; traçage Langfuse coupé |
| Heure | 06/11/2026, vers 22 h UTC ; pile supprimée après l'essai (`down -v`, ses seuls volumes) |

## Les résultats

| Vérification | Résultat |
|---|---|
| Le rôle et son mot de passe créés par la base neuve au démarrage (`02-roles.sql`, `03-mot-de-passe-api.sh`) | `rita_api`, mot de passe posé |
| `DATABASE_URL` dans le conteneur de l'API (sans jamais l'afficher) | **absente** |
| L'utilisateur de la base vu par l'API elle-même (`select current_user` par `sources.database.dsn_api()`) | **`rita_api`** |
| `/health` ; `GET /donnees/portefeuille`, `/donnees/valeurs`, `/donnees/indicateurs-portefeuille`, `/donnees/fraicheur`, `/sante` avec la clé | 200 partout |
| Un appel de la passerelle MCP (`X-Client-Id`) puis le journal d'audit | 200, **une ligne écrite** dans `mcp_calls` |
| `POST /briefing?ticker=MC.PA` (appel réel au modèle d'Azure) et `POST /question` | 200 et 200 |
| Les cinq écrans dans un vrai navigateur, avec la clé | aucune erreur JavaScript, aucun refus ; capture de l'écran Portefeuille : [`portefeuille-lu-par-rita-api-copie-2026-11-06.png`](portefeuille-lu-par-rita-api-copie-2026-11-06.png) |
| En `rita_api` : `UPDATE cotation` | **refusé** (« permission denied for table cotation ») |
| En `rita_api` : `DELETE FROM mcp_calls` | **refusé** (« permission denied for table mcp_calls ») |
| Droits de `rita_api` sur `mcp_calls` | `INSERT` et `SELECT` seulement |

À côté, sur une base jetable liée à `127.0.0.1` : les 22 tests de `tests/test_role_api.py` et les 59 tests qui
demandent PostgreSQL passent ; suite complète du dépôt : 2247 réussis, 0 en échec.

## Ce que l'essai ne prouve pas

- **La production n'est pas encore changée** : sa base existe déjà, elle ne lance pas les scripts de démarrage. L'étape
  du serveur (appliquer `db/roles.sql`, poser le mot de passe, ajouter `POSTGRES_PASSWORD_API`) est faite par Era,
  **avant** la fusion dans `main` (`docs/exploitation.md`, « Le rôle de l'API en production »).
- La copie sert le jeu de démonstration, pas les données de production.
- Le pré-test de la livraison (compte en lecture seule) n'a pas été rejoué ici : il ne reçoit ni `DATABASE_URL` de
  production ni `POSTGRES_*`, ce que le code de `deploy/deployer.py` garantit déjà.

## 📖 Glossaire

- **Rôle** (PostgreSQL) : un compte de la base, avec ses droits.
- **Pile de démonstration** : une copie complète de RITA (base, API) lancée sur le poste, isolée par son nom de projet.
- **`current_user`** : le rôle sous lequel une connexion travaille réellement.

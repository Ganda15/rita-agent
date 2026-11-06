# Plan de la carte #76 : l'API lit la base avec son propre rôle, plus avec le propriétaire

> Écrit le 06/11/2026, **validé par Era le 06/11 (« ok plan »)**, avec l'essai sur une copie ajouté (T5) (carte #76 ; décision d'Era du 06/11 : avant l'oral blanc).
> Source de l'écart : `evidence/C17/preuve-droits-acces-2026-10-03.md`, § 4.2 et § 6 ; matrice d'accès du chapitre
> « Données », § 3.5, validée par le formateur le 03/10 : l'API et le graphe **lisent** les tables nécessaires et
> **écrivent** le seul journal d'audit `mcp_calls`.

## 1. Ce qui est vrai aujourd'hui (relevé le 06/11)

| Fait | Où |
|---|---|
| L'API se connecte avec `DATABASE_URL`, le rôle propriétaire `rita` (tous les droits) | `docker-compose.yml`, service `api`, ligne 78 ; `sources/database.py`, ligne 172 |
| Lecteurs de la base dans le processus de l'API : `sources/database.py` (routes de données, monitorage, audit) et `indicateurs/socle.py`, ligne 136 | `api/donnees.py`, `api/main.py`, `monitorage/fraicheur.py`, `monitorage/signaux.py`, `db/audit_mcp.py` |
| Une seule écriture à l'exécution : `INSERT INTO mcp_calls` | `db/audit_mcp.py`, ligne 31 ; table `mcp_calls`, `id BIGSERIAL` (`db/schema.sql`, ligne 281) |
| `memory_audit` n'est écrite par aucun code de l'API ; seule la purge RGPD la touche, en propriétaire | `db/rgpd_purge.py`, lignes 52 à 63 |
| Le rôle `rita_lecture` (lecture seule) existe, avec 4 tests ; aucun code de l'API ne s'en sert | `db/roles.sql`, `tests/test_role_lecture.py` |
| Le pré-test de la livraison ne reçoit ni `DATABASE_URL` ni `POSTGRES_*` | `deploy/deployer.py`, `env_du_pretest`, ligne 389 |
| Les fichiers Compose partent avec l'image et sont installés par la livraison | `deploy/deployer.py`, ligne 286 |

## 2. Ce qui change

1. **Un rôle `rita_api`** dans `db/roles.sql` : `LOGIN`, lecture de toutes les tables et séquences (comme
   `rita_lecture`), plus `INSERT` sur `mcp_calls` et `USAGE` sur sa séquence ; rien d'autre. Mot de passe posé à la main,
   jamais dans un fichier versionné.
2. **Une seule fonction donne l'adresse de la base de l'API** (`sources/database.py`) : `POSTGRES_DSN_API` si elle
   existe, sinon `DATABASE_URL` (le poste de développement ne change pas). `indicateurs/socle.py` la réutilise.
   L'import et la collecte (`db/importer.py`, `pipelines/ingest.py`) gardent le propriétaire : ce sont les seuls à écrire.
3. **Compose** : le service `api` reçoit `POSTGRES_DSN_API` (rôle `rita_api`, mot de passe lu dans le `.env` du serveur,
   `${POSTGRES_PASSWORD_API:?…}`) et **perd `DATABASE_URL`** : le mot de passe du propriétaire n'entre plus dans le
   conteneur de l'API. Le préfixe `POSTGRES_` est voulu : le pré-test l'écarte déjà, sans toucher à `deploy/deployer.py`.
4. **Rien ne change** dans `guardrails/` (le nom `DATABASE_URL` n'y est qu'un motif de fuite à bloquer), ni dans
   `db/schema.sql`.

## 3. Les tâches, test d'abord

| # | Test écrit avant, qui doit échouer | Code | Vérification |
|---|---|---|---|
| T1 | `tests/test_role_api.py` (marqueur `postgresql`, job `base`) : avec `SET ROLE rita_api`, `SELECT` sur `cotation`, `position`, `valeur` passe ; `UPDATE` et `DELETE` sur `cotation` et `position` sont refusés ; `INSERT` sur `mcp_calls` passe ; `CREATE TABLE` est refusé | `db/roles.sql` : le rôle et ses droits ; `GRANT rita_api TO rita` (les tests prennent le rôle sans mot de passe) | job `base` vert, aucun saut |
| T2 | `tests/test_dsn_api.py` : sans `POSTGRES_DSN_API`, l'adresse est `DATABASE_URL` ; avec, c'est elle ; `indicateurs/socle.py` donne la même | `sources/database.py`, `indicateurs/socle.py` | suite complète verte |
| T3 | `tests/test_docker_compose.py` : le service `api` a `POSTGRES_DSN_API` avec `rita_api@` et n'a plus `DATABASE_URL` ; les services d'ingestion gardent `DATABASE_URL` | `docker-compose.yml` | suite complète verte |
| T4 | `docs/exploitation.md` : la procédure du serveur ci-dessous, testée comme le reste du guide | guide | `tests/test_exploitation_doc.py` |
| T5 | **Essai sur une copie, avant la production** (demande d'Era du 06/11) : une base PostgreSQL jetable, liée à `127.0.0.1` seulement, avec le schéma, les rôles et le jeu de démonstration ; l'API lancée avec `POSTGRES_DSN_API` sur `rita_api` | aucun | les cinq écrans, un briefing, une question et un appel de la passerelle MCP fonctionnent ; un `UPDATE` sur `cotation` est refusé ; la ligne de `mcp_calls` est écrite ; résultat noté dans `evidence/C17/` |

## 4. Ce qu'Era fait sur le serveur, AVANT la fusion dans `main`, et seulement si T1 à T5 sont verts

🖧 **LE SERVEUR** (après `ssh`), dans cet ordre :

1. Appliquer le nouveau `db/roles.sql` à la base de production, en propriétaire (`docker exec … psql -U rita -d rita -f …`).
2. Poser le mot de passe : `ALTER ROLE rita_api PASSWORD '…';` (un mot de passe neuf, jamais écrit dans le dépôt).
3. Ajouter `POSTGRES_PASSWORD_API=…` au `.env` du serveur.

Sans l'étape 3, Compose refuse de démarrer la nouvelle API (`:?`) : la livraison échoue avant toute bascule, et
l'ancienne version reste servie.

## 5. Après la livraison : ce qui prouve que c'est fait

- `/health` répond ; les cinq écrans s'ouvrent ; un briefing passe.
- `docker exec rita-api-preprod printenv DATABASE_URL` ne renvoie rien.
- Dans la base : `SELECT usename, count(*) FROM pg_stat_activity WHERE datname = 'rita' GROUP BY usename;` montre
  `rita_api` pour les connexions de l'API ; `rita` n'y apparaît que pendant un import ou une collecte.
- Un appel de la passerelle MCP laisse sa ligne dans `mcp_calls` (l'écriture permise marche).

## 6. Retour arrière

Le workflow « Retour arrière » remet l'image précédente, avec ses fichiers Compose, qui lisent encore `DATABASE_URL` :
le `.env` du serveur garde `POSTGRES_PASSWORD`, l'ancienne version redémarre comme avant. Le rôle `rita_api` peut rester
en base sans effet.

## 7. Risques et limites

- Une requête de l'API qui écrirait ailleurs que dans `mcp_calls` échouera en production : T1 et la suite complète doivent
  le voir avant. Si l'écriture de l'audit échoue, l'API répond quand même (elle compte l'échec, `db/audit_mcp.py`).
- La fonction d'adresse retombe sur `DATABASE_URL` si `POSTGRES_DSN_API` manque : utile au poste, mais en production
  c'est Compose qui garantit la variable (T3), pas le code.
- Calendrier : la semaine de l'oral blanc. Si T1 à T3 ne sont pas verts et l'étape du serveur faite d'ici le 10/11, on
  s'arrête et C17.5 reste à consolider, présenté avec ce plan.

## 📖 Glossaire

- **Rôle** (PostgreSQL) : un compte de la base, avec ses droits (lire, écrire, créer).
- **Propriétaire** : le rôle qui a créé les tables et qui a tous les droits dessus (`rita`).
- **Moindre privilège** : ne donner à chaque composant que les droits dont il a besoin.
- **DSN** : l'adresse de connexion à une base (rôle, mot de passe, hôte, port, nom de la base).
- **Pré-test** : le contrôle que la livraison fait sur la nouvelle version avant de la mettre en service.

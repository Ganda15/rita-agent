# Sprint 5, étape 9 : la copie du sprint 5 lancée sur le poste (22/10/2026)

Prototype local, branche `sprint-5-vigie-demo`, commit `f8b13c8245f2e1aba3e111b232f58468ef7d92a4`. Commandes lancées
par Era dans `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5` vers 18 h 10 ; lignes utiles recopiées de sa console
(le journal complet de construction Docker n'est pas reproduit). Vérifications faites ensuite, en lecture seule.

## 0. Préalable

Le port 8011 était occupé par la démonstration de l'atelier 2 (`rita-api-demo-20261015-atelier`). Décision d'Era : la
mettre à l'arrêt (`docker stop`, réversible par `docker start`, données gardées). La clé d'exercice a été ajoutée au
`.env` par une commande qui ne l'affiche pas.

## 1. Les quatre commandes

| Commande | Sortie utile |
|---|---|
| `scripts\copie_sprint5.py deployer` | `Image rita-api:s5-f8b13c8245f2 Built 92.1s` ; volumes `rita-s5_rita_pgdata_preprod`, `rita-s5_rita_chroma_preprod`, `rita-s5_rita_cache_preprod` créés ; `copie : déployée, /health annonce f8b13c8245f2 ; version précédente gardée : aucune` |
| `scripts\copie_sprint5.py initialiser` | `{'valeurs': 3, 'cotations': 222, 'articles': 6, 'positions': 3}` ; modèle d'embedding téléchargé (79,3 Mo) ; `indexation lues 6 \| ecrites 6 \| rejetees 0` |
| `scripts\copie_sprint5.py collecter` | `cotations (yfinance) lues 21 \| ecrites 21 \| rejetees 0`, `seances du 2026-10-14 au 2026-10-22` |
| `scripts\copie_sprint5.py etat` | `version courante : f8b13c8245f2` ; `version precedente : aucune` ; `/health : commit f8b13c8245f2, construit le 2026-10-22T18:11:20+02:00` |
| `docker image ls rita-api` | `rita-api:local cd6be8374a7f` (inchangée) ; `rita-api:s5-f8b13c8245f2 422925e5acd2` (nouvelle) |

## 2. Vérifications en lecture seule

| Vérification | Résultat |
|---|---|
| `GET http://localhost:8011/health` | `"commit":"f8b13c8245f2e1aba3e111b232f58468ef7d92a4"`, `"construit_le":"2026-10-22T18:11:20+02:00"`, index de 6 articles |
| Dernière séance par valeur, dans la base de la copie (`docker exec rita-postgres-s5 psql ... SELECT ticker, MAX(date_seance) ...`) | `AIR.PA 2026-10-22`, `MC.PA 2026-10-22`, `OR.PA 2026-10-22` (80 séances chacune) |
| Conteneurs | `rita-api-s5` et `rita-postgres-s5` en bonne santé ; seul port publié : 8011 |
| `GET /tableau-de-bord.html` | HTTP 200 |
| `GET /sante` sans clé | HTTP 403 (la clé est exigée) |

## 3. Ce que cela prouve, et ce que cela ne prouve pas

- La copie tourne sur sa propre image et ses propres volumes ; `rita-api:local` n'est pas touchée.
- `/health` annonce le commit de la branche, et non « inconnu » : `GIT_SHA` est bien passé à la construction.
- Critère 1 dans la copie : OR.PA a une cotation du jour (22/10) après la collecte. **En production, l'écart reste
  ouvert** (décision : le sprint 5 ne touche pas l'original).
- Deux avertissements sans effet sur le résultat, déjà présents avant le sprint 5 : le manifeste d'ingestion n'est
  pas écrit dans `/app/logs` (système de fichiers du conteneur en lecture seule), et yfinance ne peut pas créer son
  cache dans `/home/rita/.cache/py-yfinance` (même raison) ; la collecte écrit bien ses 21 séances.
- Pas encore prouvé : le retour arrière (il faut une seconde version déployée), la vigie et les exercices sur la
  copie en marche (étape 11).

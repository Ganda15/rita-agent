# Job `base` : premier passage sur GitHub (01/11/2026, 22 h 44 à 22 h 46, heure de Paris)

Constitué le soir même, à partir du journal brut lu par l'API GitHub. Le job `base` (`.github/workflows/test.yml`)
donne aux tests qui demandent PostgreSQL une base jetable, avec le schéma et les rôles du dépôt, et échoue si l'un
d'eux est sauté. Avant lui, ces tests se sautaient en CI et la chaîne restait verte sans les avoir exécutés.

## Le passage

| Élément | Valeur |
|---|---|
| Commit | `516fbf5a3bbeb2cfbf99990f1144cc1e8fb9736f` (branche `develop`, poussée par Era) |
| Workflow Tests | passage 41353566356 : `pytest`, `evals`, `base` réussis |
| Workflow Livraison | passage 41353566328 : `lint`, `secrets`, `construire-et-publier` réussis ; aucun déploiement (les jobs de déploiement sont sautés hors de `main`) |
| Job `base` | 124988735731 |
| Base | service `postgres:18-alpine`, compte `rita`, mode `trust` (aucun mot de passe, aucun secret) |
| Python | 3.13.17 |
| Sélection | les fichiers qui appellent `dsn_de_test` : 43 tests sur ce commit, dont 21 demandent PostgreSQL |
| Résultat | **43 réussis, 0 sauté** |
| Job `pytest` du même passage | 1 848 réussis, 42 sautés, 2 échecs attendus ; couverture 96,32 % (seuil 90 %) |

Le retour de `psql` sur le poste GitHub (`ubuntu-24.04`) était une question ouverte : le schéma puis les rôles se
chargent, avec `ON_ERROR_STOP=1`.

## Extrait du journal brut (horodatage UTC)

```
2026-11-01T21:44:47.9460755Z Complete job name: base
2026-11-01T21:44:48.3167511Z ##[command]/usr/bin/docker pull postgres:18-alpine
2026-11-01T21:44:59.7624050Z  * [new ref]         516fbf5a3bbeb2cfbf99990f1144cc1e8fb9736f -> origin/develop
2026-11-01T21:45:00.1306559Z   python-version: 3.13
2026-11-01T21:46:34.9429059Z ##[group]Run psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f db/schema.sql
2026-11-01T21:46:34.9429617Z psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f db/schema.sql
2026-11-01T21:46:34.9430068Z psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f db/roles.sql
2026-11-01T21:46:35.1170571Z fichiers=$(grep -l dsn_de_test tests/*.py | grep -v garde_base.py)
2026-11-01T21:46:35.1171638Z pytest -q -rs --no-cov $fichiers | tee sortie-base.txt
2026-11-01T21:46:40.5798315Z ...........................................                              [100%]
2026-11-01T21:46:40.5799627Z 43 passed in 3.36s
```

## Les lignes `ERROR` du journal de la base

En fin de job, GitHub imprime le journal du conteneur PostgreSQL. On y lit des `ERROR` : ce sont les refus que les
tests provoquent exprès, et vérifient. Exemples : une même ligne de portefeuille insérée deux fois
(`uq_position_ligne`), une clôture antérieure à l'achat (`cloture_apres_achat`), un statut inconnu dans le journal MCP
(`mcp_calls_statut_check`), des droits refusés à un rôle qui n'y a pas accès (`permission denied`). Un avertissement
du conteneur rappelle que le mode `trust` ouvre la base à quiconque atteint son port : ici, un conteneur sur le
réseau privé du job, détruit à la fin.

## Ce qui reste

- Rendre `base` obligatoire dans la règle de protection de `main` (réglage GitHub, décision d'Era).
- Après le correctif #152, la sélection passera à 46 tests, dont 24 PostgreSQL : à vérifier sur le commit qui le porte.
- Remplacer la recherche du mot `dsn_de_test` par un marquage explicite des tests PostgreSQL, puis vérifier que les
  24 restent couverts.

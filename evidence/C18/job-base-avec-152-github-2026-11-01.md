# Job `base` : passage sur le commit qui porte #152 (01/11/2026, 23 h 31 à 23 h 33, heure de Paris)

Constitué le soir même, à partir du journal brut lu par l'API GitHub. Suite de
`job-base-premier-passage-github-2026-11-01.md` : la vérification demandée par la revue avant de remplacer la recherche
du mot `dsn_de_test` par un marquage explicite.

| Élément | Valeur |
|---|---|
| Commit | `afa741d6368425b6063f576cedf7dbfd0dd24811` (branche `develop`), qui contient #152 (`c0ce2b9`) |
| Workflow Tests | passage 41357550846 : `base`, `pytest`, `evals` réussis |
| Workflow Livraison | passage 41357550819 : `lint`, `secrets`, `construire-et-publier` réussis ; aucun déploiement |
| Job `base` | 125000760359 |
| Sélection | 46 tests, dont 24 demandent PostgreSQL (les 21 du premier passage, plus les 3 du vrai import de #152) ; les 22 autres n'en demandent pas |
| Résultat | **46 réussis, 0 sauté** |
| Job `pytest` du même passage | 1 873 réussis, 45 sautés, 2 échecs attendus ; couverture 96,32 % (seuil 90 %) |
| Règle `main protegee` | `base` fait partie des sept checks exigés depuis le 01/11/2026, 23 h 11 |

Le partage 24 et 22 vient du rejeu local du même soir, sur les mêmes fichiers : sans base, 22 réussis et 24 sautés
(`evidence/C17/correctifs-2026-11-01/152-verrou-demo-apres.txt`). Le journal GitHub ne donne que le total.

## Extrait du journal brut (horodatage UTC)

```
2026-11-01T22:31:29.6858836Z Complete job name: base
2026-11-01T22:31:30.0166641Z ##[command]/usr/bin/docker pull postgres:18-alpine
2026-11-01T22:31:41.8671926Z  * [new ref]         afa741d6368425b6063f576cedf7dbfd0dd24811 -> origin/develop
2026-11-01T22:33:02.3100733Z ##[group]Run psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f db/schema.sql
2026-11-01T22:33:02.3101310Z psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f db/schema.sql
2026-11-01T22:33:02.3101779Z psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -q -f db/roles.sql
2026-11-01T22:33:02.5282725Z fichiers=$(grep -l dsn_de_test tests/*.py | grep -v garde_base.py)
2026-11-01T22:33:02.5283218Z pytest -q -rs --no-cov $fichiers | tee sortie-base.txt
2026-11-01T22:33:08.8600577Z ..............................................                           [100%]
2026-11-01T22:33:08.8601512Z 46 passed in 4.00s
```

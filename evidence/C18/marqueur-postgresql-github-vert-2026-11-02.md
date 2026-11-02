# Le marqueur `postgresql` sur GitHub : vert (02/11/2026, nuit)

Constitué le soir même, depuis le journal brut lu par l'API GitHub. Suite de
`marqueur-postgresql-2026-11-02.md` (le changement) et de `marqueur-premier-passage-github-echec-2026-11-02.md` (le
premier passage en échec, sa cause et son correctif).

| Élément | Valeur |
|---|---|
| Commit | `a32571ff6effa7a2c69b2ae98730ed3a4416f2fd` (branche `develop`), qui porte le marqueur (`997aae6`) et le correctif du job (`8ff64bf`) |
| Workflow Tests | passage 41364533942 : `base`, `pytest`, `evals` réussis |
| Workflow Livraison | passage 41364533958 : `lint`, `secrets`, `construire-et-publier` réussis ; aucun déploiement |
| Job `base` | 125021776943 : **24 réussis, 0 sauté**, 1 903 désélectionnés ; Playwright 1.64.1 installé |
| Job `pytest` | 1 880 réussis, 45 sautés (dont les 24 tests PostgreSQL), 2 échecs attendus ; couverture 96,32 % |

Les 24 tests choisis par le marqueur sont ceux de `tests-postgresql-avant-marqueur-2026-11-02.txt`, vérifiés nom par
nom sur le poste avant la poussée.

## Extrait du journal brut du job `base` (horodatage UTC)

La ligne d'installation est abrégée : « ... » remplace la liste des autres paquets installés.

```
2026-11-01T23:56:38.3177060Z Complete job name: base
2026-11-01T23:56:48.7784782Z  * [new ref]         a32571ff6effa7a2c69b2ae98730ed3a4416f2fd -> origin/develop
2026-11-01T23:58:26.7070238Z Successfully installed ... playwright-1.64.1 ...
2026-11-01T23:58:26.9587405Z pytest -q -rs --no-cov -m postgresql tests | tee sortie-base.txt
2026-11-01T23:58:36.6537409Z 24 passed, 1903 deselected in 7.09s
```

# Le marqueur sur GitHub : premier passage en échec, cause, correctif (02/11/2026, nuit)

Constitué le soir même. Le commit `997aae6` (marqueur `postgresql`) a fait échouer le job `base` sur `develop` :
les 24 tests PostgreSQL ont réussi, mais 3 tests sautés ont déclenché la règle « aucun saut ». `main` n'est pas
touchée ; les jobs `pytest` et `evals`, et la Livraison, sont verts sur ce commit.

## 1. Sur GitHub

Passage 41363062480 (workflow Tests), job `base` 125017363756, commit
`997aae6f759ec128cb8163c5789db07737967d08`. Extrait du journal brut (horodatage UTC) :

```
2026-11-01T23:40:08.1656865Z pytest -q -rs --no-cov -m postgresql tests | tee sortie-base.txt
2026-11-01T23:40:08.1657530Z if grep -E "[0-9]+ skipped" sortie-base.txt; then echo "Des tests de base ont été sautés : échec." && exit 1; fi
2026-11-01T23:40:18.4586765Z SKIPPED [3] tests/test_smoke_ui.py:18: could not import 'playwright.sync_api': No module named 'playwright'
2026-11-01T23:40:18.4588039Z 24 passed, 3 skipped, 1863 deselected in 7.54s
2026-11-01T23:40:19.4864319Z 24 passed, 3 skipped, 1863 deselected in 7.54s
2026-11-01T23:40:19.4869119Z Des tests de base ont été sautés : échec.
```

## 2. Cause

Avant le marqueur, le job ne chargeait que les huit fichiers trouvés par la recherche du mot `dsn_de_test`. Avec
`pytest -m postgresql tests`, pytest **charge tous les fichiers** avant de choisir. Le job `base` n'installe que
`requirements.txt`, où Playwright ne figure pas (le job `pytest` l'installe à part). `tests/test_smoke_ui.py` l'importe au
chargement (`pytest.importorskip`, ligne 18), et deux fichiers importent ce module : trois fichiers sautent au
chargement, comptés comme trois tests sautés, alors qu'aucun n'est un test PostgreSQL.

Mon rejeu local ne l'avait pas vu : Playwright est installé sur le poste. Le contrôle « mêmes 24 tests, nom par nom »
était juste ; c'est l'environnement du job qui différait.

## 3. Reproduit sur le poste

Playwright rendu introuvable par un faux module placé dans le dossier de travail de l'assistant (hors du dépôt), qui
lève `ModuleNotFoundError` comme un paquet absent ; commande du job, sans base :

```
SKIPPED [3] tests\test_smoke_ui.py:18: could not import 'playwright.sync_api': No module named 'playwright' (simulation du job base)
27 skipped, 1863 deselected, 1 warning in 5.42s
```

Même ligne de saut, mêmes 1 863 désélectionnés que sur GitHub (les 24 autres sautés le sont faute de base).

## 4. Correctif, test d'abord

- Test ajouté à `tests/test_ci_base.py` : le job installe tout ce que les fichiers de tests importent au chargement
  (`pytest.importorskip` au niveau du module), d'après `requirements.txt` et les commandes du job.
- Avant le correctif :
```
E   AssertionError: assert ['test_cle_me...: playwright'] == []
D:\KandaWork\RITA_PROJECT\rita-agent\tests\test_ci_base.py:80: AssertionError: assert ['test_cle_me...: playwright'] == []
1 failed, 6 passed, 1 warning in 3.04s
```
- Correctif : `pip install playwright` (le paquet seul, sans navigateur) dans le job `base`. La règle « aucun saut » est
  gardée telle quelle : un fichier qui saute au chargement pourrait cacher des tests PostgreSQL.
- Après le correctif (`tests/test_ci_base.py` et `tests/test_garde_base.py`) :
```
18 passed, 1 warning in 3.67s
```

## Ce qui reste

- Pousser le correctif et lire le job `base` : attendu 24 réussis, 0 sauté. Le nombre de désélectionnés va
  augmenter : les fichiers de Playwright se chargeront, et leurs tests seront comptés un par un.

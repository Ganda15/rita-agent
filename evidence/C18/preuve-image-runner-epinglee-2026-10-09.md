# Preuve C18 et C19 : l'image des machines de la CI est épinglée (carte #84), 9 octobre 2026

## Pourquoi

Le 05/10/2026, les notices des exécutions GitHub annonçaient que le label `ubuntu-latest` passerait à Ubuntu 26 à partir
du **19/10/2026** (https://github.com/actions/runner-images/issues/14748). Les cinq workflows du dépôt l'utilisaient, en
six travaux. La chaîne aurait changé de système quatre jours après le gel d'E1 et d'E3 (cible 13/10, au plus tard 15/10)
et avant la remise du 05/11, sans aucun changement de code. Décision d'Era le 09/10 : épingler avant le gel.

La liste officielle des images (`actions/runner-images`, README, lue le 09/10) donne `ubuntu-latest or ubuntu-24.04` pour
Ubuntu 24.04 : épingler `ubuntu-24.04` ne change donc rien aujourd'hui, et empêche seulement le changement du 19/10.

## Ce qui a été fait, test d'abord

Test de contrat `tests/test_image_runner.py` : il lit chaque fichier de `.github/workflows/`, vérifie que chaque travail
tourne sur `ubuntu-24.04`, que le texte `ubuntu-latest` n'apparaît nulle part, et qu'il trouve bien au moins cinq
fichiers et six travaux (garde contre un test vide).

**Rouge**, avant le changement, sur un clone propre de `develop` (`e317654`) :

```
FAILED tests/test_image_runner.py::test_chaque_travail_tourne_sur_l_image_epinglee[alerte-incident.yml:ouvrir-ou-commenter]
FAILED tests/test_image_runner.py::test_chaque_travail_tourne_sur_l_image_epinglee[livraison.yml:construire-et-publier]
FAILED tests/test_image_runner.py::test_chaque_travail_tourne_sur_l_image_epinglee[revue-pr.yml:revue]
FAILED tests/test_image_runner.py::test_chaque_travail_tourne_sur_l_image_epinglee[scan-giskard.yml:scan]
FAILED tests/test_image_runner.py::test_chaque_travail_tourne_sur_l_image_epinglee[test.yml:pytest]
FAILED tests/test_image_runner.py::test_chaque_travail_tourne_sur_l_image_epinglee[test.yml:evals]
FAILED tests/test_image_runner.py::test_aucun_workflow_ne_vise_ubuntu_latest
7 failed, 1 passed in 0.31s
```

**Le changement** : six lignes, `runs-on: ubuntu-latest` devient `runs-on: ubuntu-24.04`, dans `alerte-incident.yml`,
`livraison.yml`, `revue-pr.yml`, `scan-giskard.yml` et `test.yml` (deux travaux).

**Vert** : `8 passed in 0.06s`.

**Mutation** : `ubuntu-latest` remis dans `revue-pr.yml`, le test tombe ; fichier restauré, il repasse.

```
FAILED tests/test_image_runner.py::test_chaque_travail_tourne_sur_l_image_epinglee[revue-pr.yml:revue]
FAILED tests/test_image_runner.py::test_aucun_workflow_ne_vise_ubuntu_latest
2 failed, 6 passed in 0.23s
```

**Suite complète** sur le même clone, sans fichier d'environnement, comme la CI : `808 passed, 22 skipped, 2 xfailed`,
couverture 94,65 % (seuil 90 %).

## Sur GitHub

Commit `21cf8f1`, poussé par Era le 09/10/2026.

| Exécution | Résultat |
|---|---|
| Tests, `37981437957` | succès : test des données `260 passed, 3 skipped` ; suite `801 passed, 29 skipped, 2 xfailed`, couverture 94,70 % ; portes d'évaluation `7 passed, 2 xfailed` |
| Livraison, `37981438277` | succès |

Le journal de l'exécution Tests montre la machine utilisée : `Image: ubuntu-24.04`, `Version: 20261002.596`. Les huit
tests de `tests/test_image_runner.py` y passent.

## Ce qui reste, dit franchement

- **Douze avertissements nouveaux** dans la même exécution : `PydanticDeprecatedSince214`, émis par la bibliothèque
  `giskard` pendant `tests/test_scan_giskard.py`. Ils n'existaient pas le 06/10 : les journaux d'installation des deux
  exécutions montrent `pydantic-2.13.5` et `giskard_checks-1.0.5` le 06/10 (`37425728380`), puis `pydantic-2.14.0` et
  `giskard_checks-1.0.6` le 09/10, parce que `requirements.txt` ne les épingle pas (carte #23). Sans effet aujourd'hui ; c'est le
  même risque que celui de l'image, à l'échelle d'une dépendance.
- Revenir à une image récente après le jury, par une décision écrite : changer `IMAGE` dans le test, puis les workflows.

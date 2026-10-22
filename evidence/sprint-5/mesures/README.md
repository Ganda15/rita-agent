# Sprint 5 : les mesures des étapes 1 à 5

Sorties de commande brutes, enregistrées le 22/10/2026 sur le commit `d4a41be` de la branche `sprint-5-vigie-demo`,
dans le dossier `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5`. Chaque fichier commence par sa date, son commit et sa
commande exacte : il se régénère en relançant cette commande sur ce commit.

| Fichier | Ce qu'il prouve | Résultat |
|---|---|---|
| `suite-complete-2026-10-22.txt` | aucune régression dans tout le dépôt | 1576 passed, 24 skipped, 2 xfailed, 0 failed |
| `tests-et-couverture-sprint-5-2026-10-22.txt` | les tests du sprint 5 et la couverture de ses cinq modules (`monitorage/compteurs.py`, `signaux.py`, `seuils.py`, `vigie.py`, `api/sante.py`) | 174 passed ; couverture 100 % (421 instructions) |
| `ruff-sprint-5-2026-10-22.txt` | l'analyse statique des fichiers créés ou modifiés | All checks passed! |

Les 24 tests sautés le sont sur ce poste Windows pour des raisons écrites dans les tests (simulation en bash, `fcntl`,
liens symboliques, Spark sans Java) ; ils tournent dans la chaîne Linux. Les 2 `xfailed` sont des limites connues,
déclarées comme telles.

## Les passages au rouge

Chaque étape a commencé par des tests rouges, avant le code. Ces sorties ne se régénèrent pas honnêtement après coup :
elles sont consignées, avec leur date, dans le message du commit de chaque étape (`git show <commit>`).

| Étape | Commit | Rouge constaté avant le code |
|---|---|---|
| 1, compteurs | `d8232b4` | `ImportError` : le module `monitorage.compteurs` n'existait pas ; puis une saisie refusée en 422 consommait une place du quota (relevé, consigné) |
| 1 bis, revue de sécurité | `f70b2a3` | après 20 001 rejets, le refus de sécurité avait disparu (0 au lieu de 1) |
| 2, signaux et `/sante` | `deed0b9` | `ImportError` sur `monitorage.signaux` |
| 3, seuils et prix | `9f1223c` | `ImportError` sur `monitorage.seuils` ; un arrondi à 4 décimales faussait le coût d'environ 0,5 % |
| 4, vigie | `853bbd0` | `ImportError` sur `api.sante.construire`, 13 tests rouges ; couverture de `vigie.py` à 87 % complétée à 100 % |
| 5, tableau de bord | `d0fd6f9` | 32 tests rouges ; la page débordait sur un écran de téléphone (395 px pour 375) |
| 5 bis, coût en euros | `a1760ce` | 13 tests rouges après le passage des tests en euros |
| 5 ter, bouton Actualiser | `d4a41be` | contre-épreuve : sans la garde `enCours`, le test échoue (1 failed) |

## Ce que ces mesures ne prouvent pas

Le tableau de bord, la vigie et les seuils sont testés avec des données fabriquées par le vrai code. Leur comportement
sur la copie du sprint 5 en marche (trafic réel, vraie issue GitHub, vraie panne simulée) reste à prouver à l'étape 11.
L'étape 5 est terminée, testée et commitée localement : elle n'est pas encore poussée, revue ni intégrée.

## Les mesures de fin de sprint (22/10/2026, soir)

| Fichier | Ce qu'il prouve | Résultat |
|---|---|---|
| `suite-complete-fin-2026-10-22.txt` | aucune régression dans tout le dépôt, étapes 6 à 13 comprises | 1674 passed, 24 skipped, 2 xfailed, 0 failed |
| `tests-et-couverture-sprint-5-fin-2026-10-22.txt` | les tests du sprint 5 et la couverture de ses neuf modules (les cinq ci-dessus, plus `monitorage/exercice.py`, `monitorage/exercer.py`, `api/exercice.py`, `scripts/copie_sprint5.py`) | 286 passed ; couverture 100 % (764 instructions) |

Le comportement sur la copie en marche est prouvé à l'étape 11 : `../preuves-copie-2026-10-22.md`.

# Preuve C18 : les tests tournent à chaque poussée depuis le 28/07/2026 (relevé du 03/10/2026)

> Livrable E4, compétence C18 (« automatiser les phases de tests du code source lors du versionnement »).
> Tout ce qui suit est lu par l'API GitHub (`gh run list`, `gh api .../actions/runs`) ou dans les fichiers du dépôt,
> le 03/10/2026. Le mode d'emploi de la chaîne, en un seul endroit, est `docs/CI-CD.md`.

## 1. L'outil, et la chaîne telle qu'elle est écrite

**GitHub Actions**, parce que le dépôt est sur GitHub et qu'aucun autre serveur n'est à entretenir. Le fichier qui
porte C18 est `.github/workflows/test.yml`, nom affiché « Tests », déclenché par **chaque poussée et chaque pull
request sur `main` et `develop`**. Deux travaux indépendants, en parallèle :

| Travail | Étapes, dans l'ordre | Ce qu'il garde |
|---|---|---|
| `pytest` | récupérer le dépôt · Python 3.13 · `pip install -r requirements.txt` · Playwright et Chromium (le test de fumée dans un vrai navigateur) · `giskard-llm` et `giskard-checks` · `pytest -v --cov --cov-report=term-missing` | la suite entière et le seuil de couverture, qui vit dans `.coveragerc` (`fail_under = 90`), pas dans le workflow |
| `evals` | récupérer le dépôt · Python 3.13 · dépendances · `python -m evals.mesurer_gardefou` · `pytest tests/test_evals.py -v` | la mesure des garde-fous et les portes non compensables (faux positifs, latence ; le taux de blocage à 85 % est déclaré non atteint par un `xfail` strict) |

Les deux travaux sont **checks requis** pour fusionner dans `main` depuis le 03/10/2026 (ruleset `main protegee`,
avec `revue` ; `evidence/C19/`). Avant la poussée, sur le poste : le hook `pre-push` refuse toute poussée directe sur
`main`, et le hook `exiger-tests-verts.py` de l'assistant de développement refuse de conclure sans une sortie de tests.

## 2. Ce que la chaîne a fait, chiffres lus le 03/10/2026

| Mesure | Valeur | Commande |
|---|---|---|
| Exécutions du workflow « Tests » depuis sa création | **268** | `gh api repos/Ganda15/rita-agent/actions/workflows/test.yml/runs --jq .total_count` |
| Première exécution | 28/07/2026 à 20 h 43 UTC, verte, commit `e1bf4f1` | `.../runs?per_page=1&page=268` |
| Dernière exécution | 03/10/2026 à 12 h 58 UTC, verte, commit `f1c2413` | `gh run list --workflow test.yml --limit 1` |
| Sur les 100 dernières (depuis le 19/09) | **97 vertes, 3 rouges** | `gh run list --workflow test.yml --limit 100` |
| Durée du dernier passage | `pytest` 2 min 27 s · `evals` 1 min 20 s | `gh api .../runs/37124601120/jobs` |
| Tous workflows confondus | 530 exécutions : Tests 268 · Livraison 201 · Revue PR 50 · Scan Giskard 10 · Alerte 1 | `gh api .../actions/workflows/<fichier>/runs --jq .total_count` |

## 3. Les trois rouges, et ce qu'ils ont attrapé

Une chaîne qui n'est jamais rouge ne prouve rien. Les trois échecs des cent derniers passages :

| Date | Exécution | Commit | Travail tombé, étape | Cause | Suite |
|---|---|---|---|---|---|
| 20/09 12 h 36 | 35511083764 (poussée) et 35511085754 (pull request) | `e42e929` | `pytest`, étape « Lancer les tests » ; `evals` vert | un test nouveau du scan Giskard importait `giskard-checks`, installé sur le poste mais pas dans le travail de CI | corrigé le jour même, `99fff85` : « giskard-checks installé dans le job de tests ; test écrit avant » |
| 28/09 10 h 43 | 36411389482 | `b62d1a9` | `pytest` **et** `evals`, étape « Installer les dépendances » | `pip` a dû construire `pandas` depuis les sources (dépendance non épinglée, roue absente pour la version tirée) ; aucun test n'a tourné | passage suivant vert ; la limite « `requirements.txt` partiellement épinglé » reste déclarée (rapport E3, §7.4) |

Lecture : le premier rouge est le cas utile, la CI a vu une dépendance qui manquait à l'environnement de test et que
le poste masquait. Le second est un rouge d'infrastructure, sans test exécuté, qui dit quelque chose de vrai sur
l'épinglage des dépendances.

Plus ancien, hors de ces cent passages, et écrit dans `.coveragerc` : le **19/08/2026**, premier seuil de couverture
posé à 80 % sur une mesure du poste (82 %), la CI tombe au premier passage (79 % : les tests Spark y sont ignorés).
Correction le même jour : `bigdata/` exclu en entier du périmètre, le chiffre devient identique partout, puis seuil
relevé à 90 % une fois deux manques fermés. **Une couverture qui change selon la machine ne peut pas servir de
garde-fou.**

## 4. Ce que la CI ne fait pas, dit tel quel

- **Seize tests Spark** (`tests/test_spark.py`) se sautent en CI : pas de JDK 21 dans le travail. Ils tournent sur le poste.
- **Douze tests sur la base réelle** (rôle lecture seule, clôture des positions, journal `mcp_calls`) se sautent en CI sans `DATABASE_URL`.
- Pas de cache `pip` : les dépendances sont réinstallées à chaque passage (environ 2 min sur 2 min 27 s).
- Pas de filtre de chemin ni de matrice de versions : une modification d'un fichier Markdown relance toute la suite ; une seule version de Python (3.13) est testée, alors que le poste est en 3.14.
- Pas de rapport de couverture conservé comme artefact : le chiffre se lit dans le journal du passage.
- `requirements.txt` n'est épinglé que pour quatre dépendances (cause du rouge du 28/09).

## 5. Les 6 critères officiels, et où ils en sont

| Critère | État | Preuve |
|---|---|---|
| Documentation : outils, étapes, tâches, déclencheurs | ✅ (03/10) | `docs/CI-CD.md`, un seul document ; avant : réparti entre `docs/LLMOPS.md`, les en-têtes de workflows et deux skills (carte #27) |
| Outil cohérent avec l'environnement | ✅ | GitHub Actions sur un dépôt GitHub |
| Toutes les étapes préalables (build, configuration) | ✅ | `test.yml` : Python 3.13, dépendances, navigateur, Giskard ; pas de build applicatif, Python ne compile pas |
| La chaîne exécute les tests à chaque déclenchement | ✅ | 268 exécutions, 97 vertes sur les 100 dernières, les 3 rouges expliquées |
| Configurations versionnées avec les sources | ✅ | `.github/workflows/` (5 fichiers), `.coveragerc`, `.githooks/`, dans le même dépôt |
| Documentation : installation, configuration, test de la chaîne, format accessible | ✅ (03/10) | `docs/CI-CD.md` §4 à §6 (secrets, permissions, activer un clone, tester la chaîne) ; Markdown lisible, PDF des rapports |

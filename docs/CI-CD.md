# La chaîne d'intégration et de livraison continues de RITA, en un seul endroit

> Écrit le 03/10/2026 (carte #27). Avant cette page, la description de la chaîne était répartie entre `docs/LLMOPS.md`,
> les en-têtes des fichiers de workflow et deux skills. Cette page dit **tout ce qui tourne sans intervention humaine
> quand le code bouge** : les outils, les cinq workflows, chaque déclencheur, chaque étape, les secrets et les
> permissions, comment installer la chaîne sur un clone neuf, comment la tester, quoi faire quand elle est rouge.
> Les preuves d'exécution sont dans `../evidence/C18/` (tests, C18) et `../evidence/C13/` (livraison, C13).

## 1. Vue d'ensemble

L'outil est **GitHub Actions** : le dépôt est sur GitHub, aucun autre serveur n'est à entretenir, et les fichiers de la
chaîne sont versionnés avec le code dans `.github/workflows/`. Cinq workflows :

| Fichier | Nom affiché | Se déclenche sur | Travaux | Durée typique | Requis pour fusionner dans `main` |
|---|---|---|---|---|---|
| `test.yml` | Tests | poussée et pull request sur `main` et `develop` | `pytest` (suite et couverture), `evals` (garde-fous mesurés, portes) | 2 min 30 s · 1 min 20 s | **oui**, les deux |
| `livraison.yml` | Livraison | poussée et pull request sur `main` et `develop` ; tag `livrable-*` | `construire-et-publier` | 3 à 4 min | non (tourne, n'est pas exigé) |
| `revue-pr.yml` | Revue PR | pull request vers `main` (ouverte, mise à jour, rouverte, prête) | `revue` | 2 à 20 min | **oui** |
| `scan-giskard.yml` | Scan Giskard | bouton manuel (`workflow_dispatch`), avec un plafond de scénarios saisi | scan des deux frontières | 10 à 30 min, coût du juge | non |
| `alerte-incident.yml` | Alerte Langfuse vers issue incident | envoi de Langfuse (`repository_dispatch`, type `alerte-langfuse`) ou bouton manuel | `ouvrir-ou-commenter` | moins de 1 min | non |

Chiffres lus le 03/10/2026 : 530 exécutions depuis le 28/07/2026 (Tests 268, Livraison 201, Revue PR 50, Scan 10,
Alerte 1).

Deux règles tiennent la chaîne par les deux bouts. **Sur le poste**, le hook `pre-push` (`.githooks/`, activé une fois
par clone par `git config core.hooksPath .githooks`) refuse toute poussée directe sur `main`. **Sur GitHub**, depuis le
03/10/2026, le ruleset `main protegee` exige une pull request et trois checks verts (`pytest`, `evals`, `revue`),
interdit la suppression et le force-push, sans acteur de contournement ; un second ruleset fige les tags `livrable-*`.
Si le hook n'est pas activé, GitHub refuse quand même.

## 2. Les déclencheurs, tous

| Événement | Branche ou référence | Ce qui part |
|---|---|---|
| `push` | `develop` | Tests, Livraison (construction et vérification de l'image, sans publication) |
| `push` | `main` (donc après chaque fusion) | Tests, Livraison |
| `pull_request` | vers `main` ou `develop` | Tests, Livraison ; vers `main` seulement : Revue PR |
| `push` d'un tag | `livrable-*` | Livraison, **avec publication** de l'image sur `ghcr.io/ganda15/rita-api` |
| `workflow_dispatch` | la branche choisie (le bouton n'existe que pour un fichier présent sur `main`) | Scan Giskard (entrées : `max_scenarios`, `langues`) ; Alerte (titre et charge utile de test) |
| `repository_dispatch` type `alerte-langfuse` | sans objet | Alerte : issue `incident` ouverte, ou commentée si déjà ouverte |

Le workflow de revue annule une exécution en cours quand un nouveau commit arrive sur la même pull request
(`concurrency`, `cancel-in-progress`) : une annulation dans l'historique n'est pas un échec.

## 3. Les étapes et les tâches, workflow par workflow

### `test.yml`, Tests (C18, C12)

Travail `pytest` : récupérer le dépôt · Python 3.13 · `pip install -r requirements.txt` · installer Playwright et
Chromium (le test de fumée ouvre un vrai navigateur ; sur le poste c'est le Chrome installé) · installer `giskard-llm`
et `giskard-checks` (un test vérifie la déclaration du juge) · **tester les données** (depuis le 04/10/2026 : une étape
nommée qui lance seuls les 19 fichiers de tests de collecte, nettoyage, import, schéma et RGPD, avant la suite complète,
pour qu'un défaut de données arrête la chaîne en premier ; 263 tests, environ 6 secondes ; figée par
`tests/test_ci_donnees.py`) · `pytest -v --cov --cov-report=term-missing`.

Travail `evals` : récupérer le dépôt · Python 3.13 · dépendances · `python -m evals.mesurer_gardefou` ·
`pytest tests/test_evals.py -v` (les portes non compensables : faux positifs au plus 15 %, latence sous 250 ms ; le
taux de blocage à 85 % est déclaré non atteint par un `xfail` strict, qui rendrait la suite rouge s'il passait).

Le seuil de couverture (`fail_under = 90`) vit dans `.coveragerc`, pas dans le workflow : un seuil écrit ici serait
invisible depuis le poste, et la régression se verrait en CI au lieu d'avant la poussée. Le périmètre exclut `tests/`
et `bigdata/` (hors image livrée), avec le pourquoi dans le fichier.

### `livraison.yml`, Livraison (C13, C19)

1. **Tests, porte de livraison** : `python scripts/verifier_livrable.py --ci` (suite et couverture, portes
   d'évaluation, liens internes). Rien n'est construit si une ligne est rouge.
2. **Construire l'image** (`Dockerfile`, deux étapes, `python:3.13-slim` tirée de la galerie publique d'Amazon depuis le 09/10, carte #85), chargée dans Docker, pas publiée.
3. **Vérifier que l'image démarre et répond** : le conteneur construit est lancé, `/health` doit répondre.
4. **Vérifier que l'accès est restreint** : sans clé, 403.
5. **Publier l'image vérifiée** sur le registre GitHub, **seulement** si la référence est un tag `livrable-*`. C'est
   l'image testée aux étapes 3 et 4 qui part, pas une reconstruction (corrigé le 26/09/2026, issue #22).

### `revue-pr.yml`, Revue PR (C13, C17)

Un seul travail : l'action GitHub officielle de l'assistant de développement relit la pull request avec `AGENTS.md`
et `CLAUDE.md` comme grille, et publie ses remarques en commentaires. Les remarques se traitent par un commit et un
test sur `develop`, jamais par une réponse seule. Délai maximal 25 minutes.

### `scan-giskard.yml`, Scan Giskard (C10, C21)

Scan d'attaques sur les deux frontières (question, résultats d'outils), juge Claude par OpenRouter, plafond de
scénarios saisi au lancement (100 par frontière validé par Era le 20/09/2026). Chaque contournement trouvé devient un
cas dans `evals/cas_giskard_*.py` et un incident C21. Détail : `../evidence/C10/2026-09-20-scan-giskard-run9.md`.

### `alerte-incident.yml`, Alerte (C11, C20, C21)

Ouvre une issue avec le label `incident` (titre stable par alerte, charge utile jointe, liste des étapes de post-mortem
à cocher) ou commente l'issue déjà ouverte pour la même alerte. Première exécution réelle le 03/10/2026 (bouton manuel,
issue #71, fermée comme démonstration).

## 4. Secrets et permissions

Aucun secret n'est écrit dans un fichier du dépôt : les workflows les lisent dans `Settings → Secrets and variables →
Actions`. Trois secrets, dont un fourni par la plateforme :

| Secret | Qui s'en sert | À quoi | Qui le pose |
|---|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | Revue PR | jeton d'abonnement de l'assistant de développement | posé une fois par `/install-github-app` depuis le terminal de l'assistant ; à renouveler s'il expire |
| `OPENROUTER_API_KEY` | Scan Giskard | le juge des scénarios (appels payants, plafonnés par l'entrée `max_scenarios`) ; seul usage d'OpenRouter depuis la carte #82, qui l'a retiré du briefing ; scénarios inventés, sans donnée personnelle ; passage du juge à Mistral prévu après le gel (carte #87) | le propriétaire du compte OpenRouter, à la main |
| `GITHUB_TOKEN` | Livraison (publier l'image), Alerte (ouvrir une issue) | jeton éphémère fourni par GitHub à chaque exécution, expire à la fin du travail | personne : rien à poser, rien à faire tourner |

Chaque workflow déclare le minimum de permissions dont il a besoin :

| Workflow | `contents` | autres |
|---|---|---|
| Tests | lecture (défaut) | aucune |
| Livraison | `read` | `packages: write` (pousser l'image sur le registre) |
| Revue PR | `read` | `pull-requests: read`, `issues: read`, `id-token: write` (exigé par l'action) |
| Alerte | `read` | `issues: write` |
| Scan Giskard | lecture (défaut) | aucune ; la clé OpenRouter passe en variable d'environnement de l'étape |

## 5. Installer la chaîne sur un clone ou un dépôt neuf

1. **Les workflows partent avec le code** : un `git push` vers un dépôt GitHub qui contient `.github/workflows/`
   active Tests et Livraison au premier commit. Rien à cliquer.
2. **Les secrets** : poser `CLAUDE_CODE_OAUTH_TOKEN` (par `/install-github-app` ; refuser la pull request de workflow
   qu'il propose, `revue-pr.yml` existe déjà) et `OPENROUTER_API_KEY` dans les secrets Actions du dépôt. Sans le
   premier, Revue PR échoue et bloque les fusions dans `main` (check requis) ; sans le second, seul le scan manuel échoue.
3. **Les rulesets** : à recréer par l'API depuis les JSON rangés dans `../evidence/C19/` :
   `gh api -X POST repos/<proprietaire>/<depot>/rulesets --input <fichier.json>`. Exige GitHub Pro sur un dépôt privé,
   ou un dépôt public.
4. **Le hook local**, une fois par clone : `git config core.hooksPath .githooks`.
5. **Le registre d'images** : rien à configurer, `GITHUB_TOKEN` suffit ; l'image apparaît dans les paquets du compte
   au premier tag `livrable-*`.
6. **L'alerte Langfuse** : côté Langfuse, un canal GitHub Actions vers ce dépôt avec le type d'événement
   `alerte-langfuse` (il faut un jeton personnel avec le droit `repo`, posé dans Langfuse, jamais dans le dépôt) ; le
   détail est dans l'en-tête de `alerte-incident.yml`.

## 6. Tester la chaîne, avant de compter dessus

| Ce qu'on veut vérifier | Comment | Ce qu'on doit voir |
|---|---|---|
| Tests et Livraison partent sur une poussée | pousser un commit sur `develop`, puis `gh run list --limit 4` | deux exécutions `in_progress` puis `success` |
| La revue tourne et bloque | ouvrir une pull request vers `main` : `gh pr create --base main --head develop` | trois checks sur la PR ; le bouton de fusion reste gris tant qu'un check requis manque |
| L'alerte ouvre une issue | `gh workflow run alerte-incident.yml --ref main -f titre="Test manuel"` | une issue `incident` dans la minute (fait le 03/10/2026 : #71) |
| Un échec est lisible | `gh run view <identifiant> --log-failed` | l'étape rouge et sa sortie |
| La même chose sur le poste, avant de pousser | `C:\Python314\python.exe -m pytest --cov -q` · `C:\Python314\python.exe -X utf8 -m evals.mesurer_gardefou` · `C:\Python314\python.exe scripts\verifier_livrable.py --ci` | les mêmes trois verdicts que la CI ; si le poste refuse une roue (Smart App Control), `Dockerfile.tests` donne le même environnement en Python 3.13 |

## 7. Quand c'est rouge

Lire l'étape tombée avant tout. Les trois cas déjà rencontrés, et ce qu'ils ont appris :

- **19/08/2026, couverture 79 % en CI contre 82 % sur le poste** : les tests Spark s'ignoraient en CI, le seuil avait
  été posé sur une mesure dépendante de la machine. Correction : `bigdata/` exclu du périmètre, même chiffre partout.
- **20/09/2026, `pytest` rouge, `evals` vert** : un test importait `giskard-checks`, installé sur le poste et pas dans
  le travail. Correction le jour même, dans le workflow, test écrit avant.
- **28/09/2026, les deux travaux rouges à « Installer les dépendances »** : `pip` a construit `pandas` depuis les
  sources (dépendance non épinglée). Aucun test n'a tourné ; le passage suivant était vert. La limite reste déclarée.

Trois choses qu'on ne fait jamais pour « que ça passe » : désactiver un test, baisser un seuil (`.coveragerc`,
`tests/test_evals.py`), contourner un hook (`--no-verify`). On propose, l'humain décide (`AGENTS.md`).

## 8. Limites, déclarées

Seize tests Spark et douze tests sur la base réelle se sautent en CI (pas de JDK, pas de `DATABASE_URL`). Pas de cache
`pip`, pas de filtre de chemin, une seule version de Python testée (3.13 ; le poste est en 3.14). Pas de rapport de
couverture conservé comme artefact. `requirements.txt` n'est épinglé que pour cinq dépendances (`feedparser`, `chromadb`, `rank-bm25`, `langfuse`, `pyspark`). La publication sur tag
n'a encore jamais tourné : le premier tag après ce fichier sera `livrable-E1-v2`, le 15/10/2026. Aucun déploiement
automatique sur le serveur : la copie Hetzner se met à jour à la main.

## 📖 Glossaire

- **Workflow** : un fichier YAML dans `.github/workflows/` qui décrit quoi exécuter, quand, avec quelles permissions.
- **Travail (job)** : une suite d'étapes exécutée sur une machine fraîche ; les travaux d'un workflow tournent en parallèle.
- **Check requis** : un travail dont le succès est exigé par GitHub avant de fusionner dans `main`.
- **Ruleset** : règle appliquée par GitHub lui-même sur une branche ou un tag.
- **Porte d'évaluation** : une mesure (ici des garde-fous) transformée en condition de fusion.
- **Image** : le paquet Docker de l'API, construit par Livraison, publié sur le registre seulement sur un tag.
- **Hook** : un script lancé par Git (ici avant la poussée) ou par l'assistant de développement (avant une commande).
- **`workflow_dispatch` / `repository_dispatch`** : déclencheur manuel (bouton) et déclencheur par un appel extérieur.

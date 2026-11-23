# La chaîne d'intégration et de livraison continues de RITA, en un seul endroit

> Écrit le 03/10/2026 (carte #27), remis à jour le 24/10/2026, puis le 06/11/2026 (vigie planifiée). Depuis le sprint 2, la chaîne ne s'arrête plus à une
> image vérifiée : elle livre la production après chaque fusion dans `main`. Cette page dit **tout ce qui tourne sans
> intervention humaine quand le code bouge**, et les deux opérations de production qui se lancent d'un bouton : les
> outils, les huit workflows, chaque déclencheur, chaque étape, les secrets et les permissions, comment installer la
> chaîne, comment la tester, quoi faire quand elle est rouge. Les preuves d'exécution sont dans `../evidence/C18/`
> (tests), `../evidence/C13/` (livraison) et `../evidence/sprint-2/` (premières livraisons et retours arrière).

## 1. Vue d'ensemble

L'outil est **GitHub Actions** : le dépôt est sur GitHub, aucun autre serveur n'est à entretenir, et les fichiers de la
chaîne sont versionnés avec le code dans `.github/workflows/`. Huit workflows, plus une action partagée
(`.github/actions/ordre-serveur`) qui envoie un ordre au serveur de production :

| Fichier | Nom affiché | Se déclenche sur | Travaux | Durée mesurée | Requis pour fusionner dans `main` |
|---|---|---|---|---|---|
| `test.yml` | Tests | poussée et pull request sur `main` et `develop` | `pytest` (suite et couverture), `evals` (garde-fous mesurés, portes), `base` (tests qui demandent PostgreSQL, depuis le 01/11/2026) | 4 min 04 s · 1 min 45 s (24/10) · 1 min 56 s (01/11) | **oui**, les trois (`base` depuis le 01/11/2026) |
| `livraison.yml` | Livraison | poussée et pull request sur `main` et `develop` ; tag `livrable-*` | `lint`, `secrets`, `construire-et-publier` ; après une fusion dans `main` : `attendre-creneau`, `deployer`, et si besoin `attendre-reprise`, `deployer-reprise` | 9 s · 43 s · 4 min 20 s · déploiement 3 min 44 s (24/10) | **oui** : `lint`, `secrets`, `construire-et-publier` |
| `revue-pr.yml` | Revue PR | pull request vers `main` (ouverte, mise à jour, rouverte, prête) | `revue` | 42 s le 24/10 ; jusqu'à 20 min déjà vu | **oui** |
| `scan-giskard.yml` | Scan Giskard | bouton manuel (`workflow_dispatch`), avec un plafond de scénarios saisi | scan des deux frontières | 10 à 30 min, coût du juge | non |
| `alerte-incident.yml` | Alerte Langfuse vers issue incident | envoi de Langfuse (`repository_dispatch`, type `alerte-langfuse`) ou bouton manuel | `ouvrir-ou-commenter` | moins de 1 min | non |
| `vigie.yml` | Vigie de la production | toutes les trois heures (`schedule`, à la 17e minute) et bouton manuel | `passage` | environ 1 min (estimé avant la première exécution ; passages planifiés depuis le 07/11) | non |
| `retour-arriere.yml` | Retour arrière | bouton manuel, avec son nom et le motif | `revenir` | 28 s le 14/10, 35 s le 15/10 | non |
| `ingestion.yml` | Ingestion | bouton manuel, avec son nom et le motif | `ingerer` | selon la collecte et le rejeu | non |

Chiffres lus le 24/10/2026 : 1 010 exécutions depuis le 28/07/2026 (Tests 483, Livraison 425, Revue PR 74, Alerte 11,
Scan 10, Ingestion 5, Retour arrière 2).

Deux règles tiennent la chaîne par les deux bouts. **Sur le poste**, le hook `pre-push` (`.githooks/`, activé une fois
par clone par `git config core.hooksPath .githooks`) refuse toute poussée directe sur `main`. **Sur GitHub**, le ruleset
`main protegee` exige une pull request et **sept** checks verts (`lint`, `secrets`, `pytest`, `evals`,
`construire-et-publier`, `revue`, et `base` depuis le 01/11/2026 ; trois jusqu'au sprint 2), interdit la suppression et le force-push, sans acteur de
contournement ; un second ruleset, `tags livrable-* figes`, interdit de supprimer ou de déplacer un tag de livrable.
Si le hook n'est pas activé, GitHub refuse quand même.

## 2. Les déclencheurs, tous

| Événement | Branche ou référence | Ce qui part |
|---|---|---|
| `push` | `develop` | Tests ; Livraison jusqu'à l'image construite et vérifiée, sans publication |
| `push` | `main` (donc après chaque fusion) | Tests ; Livraison avec publication de l'image `:sha-<commit>`, puis **déploiement en production** |
| `pull_request` | vers `main` ou `develop` | Tests, Livraison sans publication ni déploiement ; vers `main` seulement : Revue PR |
| `push` d'un tag | `livrable-*` | Livraison avec publication de l'image `:<nom du tag>` ; pas de déploiement |
| `workflow_dispatch` | la branche choisie (le bouton n'existe que pour un fichier présent sur `main`) | Scan Giskard (entrées : `max_scenarios`, `langues`) ; Alerte (titre et charge utile de test) ; Retour arrière et Ingestion (entrées : `acteur`, `motif`) |
| `repository_dispatch` type `alerte-langfuse` | sans objet | Alerte : issue `incident` ouverte, ou commentée si déjà ouverte |
| `schedule` (`17 */3 * * *`, heure UTC) | `main` seulement (règle de GitHub) | Vigie : un passage contre la production ; une issue `incident` par signal en problème |

Le workflow de revue annule une exécution en cours quand un nouveau commit arrive sur la même pull request
(`concurrency`, `cancel-in-progress`) : une annulation dans l'historique n'est pas un échec. Les travaux qui touchent la
production, eux, ne s'annulent jamais. `deployer` et `deployer-reprise` partagent le groupe `production` : une
livraison à la fois, jamais remplacée par la suivante. Le retour arrière et l'ingestion ont chacun leur groupe, pour
qu'une livraison arrivée après eux ne les annule pas pendant leur attente ; c'est le verrou du serveur qui empêche deux
opérations de se chevaucher.

## 3. Les étapes et les tâches, workflow par workflow

### `test.yml`, Tests (C18, C12)

Travail `pytest` : récupérer le dépôt · Python 3.13 · `pip install -r requirements.txt` · installer Playwright et
Chromium (le test de fumée ouvre un vrai navigateur ; sur le poste c'est le Chrome installé) · installer `giskard-llm`
et `giskard-checks` (un test vérifie la déclaration du juge) · **tester les données** (depuis le 04/10/2026 : une étape
nommée qui lance seuls les 19 fichiers de tests de collecte, nettoyage, import, schéma et RGPD, avant la suite complète,
pour qu'un défaut de données arrête la chaîne en premier ; le 24/10, 296 tests passés et 3 ignorés en 9 s ; figée par
`tests/test_ci_donnees.py`) · `pytest -v --cov --cov-report=term-missing` (le 24/10 : 1 701 passés, 30 ignorés, 2 en
échec attendu, couverture 96,32 %).

Travail `evals` : récupérer le dépôt · Python 3.13 · dépendances · `python -m evals.mesurer_gardefou` ·
`pytest tests/test_evals.py -v` (les portes non compensables : faux positifs au plus 15 %, latence sous 250 ms ; le
taux de blocage à 85 % est déclaré non atteint par un `xfail` strict, qui rendrait la suite rouge s'il passait).

Travail `base` (depuis le 01/11/2026) : un service `postgres:18-alpine` (même version que la production, compte `rita`,
mode `trust`, donc aucun mot de passe ni secret) · Python 3.13 · dépendances, plus le paquet Playwright (tous les
fichiers de tests se chargent avant la sélection, et deux l'importent au chargement) · `db/schema.sql` puis
`db/roles.sql`
chargés par `psql` avec `ON_ERROR_STOP=1` · les tests marqués `postgresql` (`pytest -m postgresql tests`, depuis le
02/11/2026 ; un test qui demande la base sans ce marqueur échoue, `tests/garde_base.py`) · **échec si un seul test
est sauté**. Avant lui, ces tests se sautaient en CI faute de base, et la chaîne restait verte sans les avoir
exécutés. Premier passage : 43 réussis, 0 sauté, sur `516fbf5` (passage 41353566356,
`evidence/C18/job-base-premier-passage-github-2026-11-01.md`) ; la sélection est figée par `tests/test_ci_base.py`.

Le seuil de couverture (`fail_under = 90`) vit dans `.coveragerc`, pas dans le workflow : un seuil écrit ici serait
invisible depuis le poste, et la régression se verrait en CI au lieu d'avant la poussée. Le périmètre exclut `tests/`
et `bigdata/` (hors image livrée), avec le pourquoi dans le fichier.

### `livraison.yml`, Livraison (C13, C19)

Travail `lint` : `ruff` à une version fixée (0.15.17, la même que dans `requirements.txt`, contrôlée par
`tests/test_lint_config.py`), puis `ruff check .` avec les règles de `ruff.toml`.

Travail `secrets` : gitleaks v8.30.1 lit **tout l'historique** (toutes les branches et tous les tags), valeurs masquées.
Une clé effacée aujourd'hui reste lisible dans les anciens commits : c'est pour ça qu'il ne lit pas seulement le dernier.
Exceptions : les six fausses clés des tests (`.gitleaks.toml`) et les secrets révoqués de l'incident INC-008
(`.gitleaksignore`). Puis `scripts/verifier_dockerfile.py` : aucune déclaration `ARG` ou `ENV` sensible dans le
`Dockerfile`.

Travail `construire-et-publier`, seulement après un `lint` et un `secrets` verts :

1. **Tests, porte de livraison** : `python scripts/verifier_livrable.py --ci` (suite et couverture, portes
   d'évaluation, liens internes ; sur un tag, le tag cité dans `ETAT.md` et `CHANGELOG.md`). Rien n'est construit si
   une ligne est rouge.
2. **Construire l'image** (`Dockerfile`, deux étapes, `python:3.13-slim` tirée de `mirror.gcr.io`, le miroir public de
   Docker Hub tenu par Google, depuis le 21/10, après Docker Hub puis la galerie publique d'Amazon, carte #85), chargée
   dans Docker, pas publiée. Étiquettes : `:sha-<commit court>` et, sur un tag, `:<nom du tag>`.
3. **Vérifier l'image construite**, lancée dans un conteneur : `/health` répond et annonce le commit construit ; sans
   clé, `/donnees/valeurs` répond 403 ; l'image n'a pas de fichier `/app/.env` (le seul chemin contrôlé) ; elle embarque ses fichiers de
   déploiement (`deploy/docker-compose.yml`, `deploy/compose.prod.yml`) ; elle sait nettoyer un résumé RSS, sans réseau.
4. **Publier l'image vérifiée** sur le registre de GitHub (`ghcr.io/ganda15/rita-api`), seulement après une fusion dans
   `main` ou sur un tag `livrable-*`. C'est l'image testée à l'étape 3 qui part, pas une reconstruction (corrigé le
   26/09/2026, issue #22). Son empreinte (`@sha256:…`) est transmise au déploiement. Sur un tag : 9 passages depuis le
   15/10 (`livrable-sprint-2-v1` à `livrable-sprint-5-v1`), dont 7 verts.

Travaux de déploiement, après une fusion dans `main` seulement :

5. **`attendre-creneau`** : entre 7 h 30 et 9 h (heure de Paris), le travail dort jusqu'à 9 h. Le créneau de 8 h à
   9 h est protégé ; la demi-heure d'avance couvre le pré-test. Calcul : `secondes_avant_livraison` de
   `deploy/deployer.py`.
6. **`deployer`**, environnement `production` : l'action `ordre-serveur` vérifie d'abord que le script du serveur est
   celui du dépôt (empreinte), puis envoie `livrer <empreinte de l'image>` par la clé SSH dédiée. Le serveur essaie
   l'image à part (pré-test), rejoue les questions de démonstration, la met en service, la contrôle, et remet
   l'ancienne si un contrôle échoue. Le détail côté serveur est dans `CHAINE-V1.md`, § 4.
7. **`attendre-reprise`, `deployer-reprise`** : si le créneau de 8 h est arrivé pendant le pré-test (code 75, rien n'a
   changé), la même image est livrée après 9 h.

Le 24/10 (version N18, commit `b547cbf`) : de la fusion à la production en 9 min 02 s, sans intervention.

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

### `vigie.yml`, Vigie de la production (C20, C21)

Un travail `passage`, depuis le 06/11/2026. Il vérifie que le secret `RITA_API_KEY_VIGIE` existe (sinon il s'arrête en
le disant), puis lance `python -m monitorage.vigie --adresse https://178-104-184-125.sslip.io --github` : sonde de
`/health`, lecture de `/sante`, une issue `incident` par signal en problème, fermée au retour à la normale
([La vigie](exploitation.md#vigie-et-exercices)). Programmée toutes les trois heures : environ 240 minutes d'Actions par mois,
gratuites sur le runner standard de GitHub depuis que le dépôt est public (23/11/2026). Un passage programmé n'est pas
garanti : les 22 et 23/11, deux passages n'ont pas démarré, GitHub a signalé un problème de paiement ou de plafond
Actions. Deux passages ne se chevauchent pas (`concurrency`).

### `retour-arriere.yml`, Retour arrière (C13, sprint 2)

Un travail `revenir`, environnement `production`. Il écrit dans le résumé du passage qui demande le retour et pourquoi,
puis envoie `revenir <numéro du passage>` par la même action : le nom et le motif restent dans GitHub. Si le script du
serveur diffère du dépôt, le retour part quand même, avec un avertissement : en urgence, c'est le script installé qui
sert. Procédure, résultats et limites : [Revenir à la version précédente en production](exploitation.md#rollback-production).

### `ingestion.yml`, Ingestion (C13, sprint 3)

Un travail `ingerer`, environnement `production`. Le serveur collecte les articles, prépare un nouvel index à part, le
vérifie (pré-test, puis rejeu des questions de démonstration), le met en service et contrôle que `/health` annonce cet
index ; sinon l'index servi ne change pas. Procédure : [exploitation.md](exploitation.md), § 8.

## 4. Secrets et permissions

Aucun secret n'est écrit dans un fichier du dépôt : les workflows les lisent dans les réglages de GitHub. Sept secrets,
dont un fourni par la plateforme. Trois sont rangés dans l'environnement `production` (*Settings → Environments*) :
seuls les travaux qui déclarent cet environnement peuvent les lire.

| Secret | Rangé dans | Qui s'en sert | À quoi | Qui le pose |
|---|---|---|---|---|
| `CLAUDE_CODE_OAUTH_TOKEN` | le dépôt | Revue PR | jeton d'abonnement de l'assistant de développement | posé une fois par `/install-github-app` depuis le terminal de l'assistant ; à renouveler s'il expire |
| `OPENROUTER_API_KEY` | le dépôt | Scan Giskard | le juge des scénarios (appels payants, plafonnés par l'entrée `max_scenarios`) | le propriétaire du compte OpenRouter, à la main |
| `DEPLOY_SSH_KEY` | l'environnement `production` | `deployer`, `deployer-reprise`, `revenir`, `ingerer` | la clé privée SSH dédiée ; sur le serveur, sa clé publique ne peut lancer qu'un script (commande forcée) | Era, une fois (`sprint-2/PLAN-TRAVAIL.md`, tâche 10) |
| `DEPLOY_HOST` | l'environnement `production` | les mêmes | l'adresse du serveur | Era |
| `DEPLOY_KNOWN_HOSTS` | l'environnement `production` | les mêmes | l'empreinte du serveur : un serveur qui ne la présente pas est refusé (`StrictHostKeyChecking=yes`) | Era |
| `RITA_API_KEY_VIGIE` | le dépôt | Vigie | la clé de l'API de production, pour lire `/sante` ; jamais affichée | Era, une fois |
| `GITHUB_TOKEN` | fourni par GitHub | Livraison (publier l'image), Alerte et Vigie (ouvrir une issue) | jeton éphémère fourni à chaque exécution, expire à la fin du travail | personne : rien à poser, rien à faire tourner |

L'environnement `production` n'a aucune règle de protection (lu le 24/10) : aucune approbation n'est demandée avant un
déploiement. La décision humaine, c'est la fusion de la pull request relue.

Chaque workflow déclare le minimum de permissions dont il a besoin :

| Workflow | `contents` | autres |
|---|---|---|
| Tests | lecture (défaut) | aucune |
| Livraison | `read`, dans chaque travail | `packages: write` dans `construire-et-publier` seulement (pousser l'image) |
| Revue PR | `read` | `pull-requests: read`, `issues: read`, `id-token: write` (exigé par l'action) |
| Alerte | `read` | `issues: write` |
| Vigie | `read` | `issues: write` |
| Scan Giskard | lecture (défaut) | aucune ; la clé OpenRouter passe en variable d'environnement de l'étape |
| Retour arrière, Ingestion | `read` | aucune ; les secrets `DEPLOY_*` arrivent par l'environnement `production` |

## 5. Installer la chaîne sur un clone ou un dépôt neuf

1. **Les workflows partent avec le code** : un `git push` vers un dépôt GitHub qui contient `.github/workflows/`
   active Tests et Livraison au premier commit. Rien à cliquer.
2. **Les secrets du dépôt** : poser `CLAUDE_CODE_OAUTH_TOKEN` (par `/install-github-app` ; refuser la pull request de
   workflow qu'il propose, `revue-pr.yml` existe déjà) et `OPENROUTER_API_KEY`. Sans le premier, Revue PR échoue et
   bloque les fusions dans `main` (check requis) ; sans le second, seul le scan manuel échoue.
3. **L'environnement `production`**, avec ses trois secrets `DEPLOY_SSH_KEY`, `DEPLOY_HOST` et `DEPLOY_KNOWN_HOSTS`.
   Sans eux, l'image se publie mais `deployer` échoue : la production ne change pas.
4. **Le serveur**, une fois, par Era : la clé publique dédiée dans `/root/.ssh/authorized_keys`, précédée de
   `command="/root/rita-deploy/bin/deployer.sh",no-pty,no-port-forwarding,no-agent-forwarding,no-X11-forwarding` ; un
   jeton GitHub en lecture seule sur les images, pour `docker login ghcr.io` ; puis le script et les fichiers Compose
   ([Mettre à jour le script du serveur](exploitation.md#script-du-serveur)). Liste complète :
   `sprint-2/PLAN-TRAVAIL.md`, tâche 10.
5. **Les rulesets** : à recréer par l'API depuis les JSON rangés dans `../evidence/C19/`
   (`ruleset-main-2026-10-14.json` pour `main`, la règle des tags dans `rulesets-2026-10-03.json`) :
   `gh api -X POST repos/<proprietaire>/<depot>/rulesets --input <fichier.json>`. Exige GitHub Pro sur un dépôt privé,
   ou un dépôt public.
6. **Le hook local**, une fois par clone : `git config core.hooksPath .githooks`.
7. **Le registre d'images** : rien à configurer, `GITHUB_TOKEN` suffit ; l'image apparaît dans les paquets du compte
   au premier passage sur `main` ou au premier tag `livrable-*`.
8. **L'alerte Langfuse** : côté Langfuse, un canal GitHub Actions vers ce dépôt avec le type d'événement
   `alerte-langfuse` (il faut un jeton personnel avec le droit `repo`, posé dans Langfuse, jamais dans le dépôt) ; le
   détail est dans l'en-tête de `alerte-incident.yml`.

## 6. Tester la chaîne, avant de compter dessus

| Ce qu'on veut vérifier | Comment | Ce qu'on doit voir |
|---|---|---|
| Tests et Livraison partent sur une poussée | pousser un commit sur `develop`, puis `gh run list --limit 4` | deux exécutions `in_progress` puis `success` |
| La revue tourne et bloque | ouvrir une pull request vers `main` : `gh pr create --base main --head develop` | les sept checks requis sur la PR ; le bouton de fusion reste gris tant qu'un check requis manque |
| La production suit `main` | après une fusion : `gh run list --workflow livraison.yml --branch main --limit 1`, puis `curl.exe -s https://178-104-184-125.sslip.io/health` | `deployer` en `success`, et `/health` annonce le commit de la fusion |
| Le retour arrière marche | `gh workflow run retour-arriere.yml --repo Ganda15/rita-agent --ref main -f acteur="Era" -f motif="essai"` | `retour arriere` dans le journal du serveur (fait le 14/10 et le 15/10) ; remettre ensuite la version annulée ([procédure](exploitation.md#rollback-production)) |
| Un tag `livrable-*` publie son image, sans déployer | `gh run list --workflow livraison.yml --branch <tag> --limit 1`, puis `gh run view <identifiant> --json jobs` et `gh run view <identifiant> --log`, où l'on cherche `rita-api:<tag>` (dans PowerShell, ajouter `\| Select-String "rita-api:<tag>"`) | `construire-et-publier` en `success`, `deployer` en `skipped` ; le journal nomme `ghcr.io/ganda15/rita-api:<tag>` et son empreinte `sha256` (fait le 01/11/2026 sur `livrable-E3-v2`, exécution 40490834495) |
| L'alerte ouvre une issue | `gh workflow run alerte-incident.yml --ref main -f titre="Test manuel"` | une issue `incident` dans la minute (fait le 03/10/2026 : #71) |
| Un échec est lisible | `gh run view <identifiant> --log-failed` | l'étape rouge et sa sortie |
| La même chose sur le poste, avant de pousser | `C:\Python314\python.exe -m pytest --cov -q` · `C:\Python314\python.exe -X utf8 -m evals.mesurer_gardefou` · `C:\Python314\python.exe scripts\verifier_livrable.py --ci` | les mêmes trois verdicts que la CI ; si le poste refuse une roue (Smart App Control), `Dockerfile.tests` donne le même environnement en Python 3.13 |

## 7. Quand c'est rouge

Lire l'étape tombée avant tout. Quatre cas déjà rencontrés, et ce qu'ils ont appris :

- **19/08/2026, couverture 79 % en CI contre 82 % sur le poste** : les tests Spark s'ignoraient en CI, le seuil avait
  été posé sur une mesure dépendante de la machine. Correction : `bigdata/` exclu du périmètre, même chiffre partout.
- **20/09/2026, `pytest` rouge, `evals` vert** : un test importait `giskard-checks`, installé sur le poste et pas dans
  le travail. Correction le jour même, dans le workflow, test écrit avant.
- **28/09/2026, les deux travaux rouges à « Installer les dépendances »** : `pip` a construit `pandas` depuis les
  sources (dépendance non épinglée). Aucun test n'a tourné ; le passage suivant était vert. La limite reste déclarée.
- **21/10/2026, Livraison rouge sur le tag `livrable-sprint-4-v1`** : la porte de livraison a refusé le tag, absent du
  `CHANGELOG.md`. La porte a fait son travail ; `livrable-sprint-4-v2` est passé le même jour.

Trois choses qu'on ne fait jamais pour « que ça passe » : désactiver un test, baisser un seuil (`.coveragerc`,
`tests/test_evals.py`), contourner un hook (`--no-verify`). On propose, l'humain décide (`AGENTS.md`).

## 8. Limites, déclarées

- **Tests ignorés en CI** : 30 le 24/10 (16 exigent une vraie base PostgreSQL, absente en CI, 9 testent les hooks de
  l'assistant de développement, muets hors Windows, et 5 exigent Spark, pas de JDK : 16 + 9 + 5 = 30). Le 16/11, 97
  (job `pytest` du run 43906441125, comptés par fichier) : 59 PostgreSQL, 9 hooks, 5 Spark, 21 relectures de PDF
  (PyMuPDF et pypdf absents de la CI) et 3 contrôles sur des données du poste (archive Parquet, base locale). Depuis le 01/11/2026, les tests
  qui demandent PostgreSQL tournent dans le job `base`, qui échoue si l'un d'eux est sauté ; ils restent ignorés dans
  le job `pytest`. Depuis le 02/11/2026, ils sont choisis par le marqueur `postgresql`, et un test qui demande la
  base sans ce marqueur échoue (`evidence/C18/marqueur-postgresql-2026-11-02.md`).
- Pas de cache `pip`, pas de filtre de chemin, une seule version de Python testée (3.13 ; le poste est en 3.14). Pas de
  rapport de couverture conservé comme artefact.
- `requirements.txt` n'est épinglé que pour six dépendances (`langfuse`, `feedparser`, `chromadb`, `rank-bm25`, `ruff`,
  `pyspark`) : les autres peuvent changer d'un passage à l'autre (cas du 28/09).
- Aucune approbation avant un déploiement : l'environnement `production` n'a pas de règle de protection.
- Le script du serveur et les fichiers Compose s'installent à la main. Un changement de `deploy/deployer.py` bloque
  donc les livraisons tant qu'Era ne l'a pas installé sur le serveur ; c'est voulu, ce script tourne en root.
- Le retour arrière ne revient que d'un pas et ne restaure pas la base. Son secours sans GitHub n'a jamais été exécuté
  ([limites du retour arrière](exploitation.md#rollback-production)).

## 📖 Glossaire

- **Workflow** : un fichier YAML dans `.github/workflows/` qui décrit quoi exécuter, quand, avec quelles permissions.
- **Travail (job)** : une suite d'étapes exécutée sur une machine fraîche ; les travaux d'un workflow tournent en
  parallèle, sauf quand l'un attend l'autre (`needs`).
- **Check requis** : un travail dont le succès est exigé par GitHub avant de fusionner dans `main`.
- **Ruleset** : règle appliquée par GitHub lui-même sur une branche ou un tag.
- **Porte d'évaluation** : une mesure (ici des garde-fous) transformée en condition de fusion.
- **Image** : le paquet Docker de l'API, construit par Livraison, publié sur le registre après une fusion dans `main`
  ou sur un tag.
- **Empreinte (`@sha256:…`)** : l'identifiant d'une image calculé sur son contenu ; deux images de même empreinte sont
  identiques à l'octet près.
- **Environnement GitHub** : un ensemble de secrets et de règles réservé aux travaux qui le déclarent ; ici
  `production`.
- **Commande forcée** : sur le serveur, une clé SSH qui ne peut lancer qu'un seul script, quoi que demande l'appelant.
- **Créneau du matin** : 8 h à 9 h, heure de Paris ; aucune livraison ni ingestion n'y bascule la production.
- **Hook** : un script lancé par Git (ici avant la poussée) ou par l'assistant de développement (avant une commande).
- **`workflow_dispatch` / `repository_dispatch`** : déclencheur manuel (bouton) et déclencheur par un appel extérieur.

# Livrable E4 : recomptage des 36 critères, le 03/10/2026 au soir

> **Tâche T1 du plan E4** (`docs/PLAN-E4-rapport.md`). Remplace le décompte du 26/09 (Obsidian, `Projets/RITA/04-Certif/RITA - Vérification critères RNCP E4 (2026-09-26).md`).
> **Règle** : un ✅ renvoie à un fichier, une ligne ou une commande que j'ai ouverte ou lancée ce soir ; ce que je n'ai pas pu
> vérifier est écrit comme tel. Les libellés des critères sont ceux de la note de suivi des livrables (recopiés tels quels).
> Commandes de contrôle : `gh run list`, `gh api repos/Ganda15/rita-agent/collaborators`, `gh project item-list 4`, `gh issue list`,
> `git tag`, `curl` sur le serveur, `pytest --cov`, et lecture des fichiers cités.

## 1. Le résultat

| | ✅ prouvé | ⚠️ partiel | ❌ absent | 26/09 (après C16 et C18) |
|---|---|---|---|---|
| C14 (5) | 4 | 1 | 0 | 4 / 1 / 0 |
| C15 (5) | 5 | 0 | 0 | 5 / 0 / 0 |
| C16 (4) | **1** | **3** | 0 | 2 / 2 / 0 |
| C17 (11) | 5 | 6 | 0 | 5 / 6 / 0 |
| C18 (6) | 6 | 0 | 0 | 6 / 0 / 0 |
| C19 (5) | **4** | **1** | 0 | 3 / 2 / 0 |
| **Total (36)** | **25** | **11** | **0** | 25 / 11 / 0 |

Le total ne bouge pas, deux lignes changent en sens inverse : **C19 gagne un ✅** (la documentation de la chaîne existe,
`docs/CI-CD.md`) et **C16 en perd un** : ce recomptage est plus strict que celui du 26/09, parce qu'aucun compte rendu daté
de revue n'existe dans le dépôt (voir C16.1 et C16.4). Aucun ❌. Le rapport E4 lui-même n'existe pas (0 page).

## 2. Critère par critère

### C14 : analyser le besoin

| # | Critère | État | Preuve (vue ce soir) | Ce qui manque |
|---|---|---|---|---|
| 1 | La modélisation des données respecte un formalisme (Merise…) | ✅ | `docs/rapports/E1/rapport-E1.html:263` : « MCD, formalisme Merise : 6 entités, 6 associations, aucune relation n-n » ; `db/schema.sql` (10 tables) | le reprendre dans E4 sans le refaire |
| 2 | La modélisation des parcours respecte un formalisme (wireframes…) | ✅ | `evidence/C14/WIREFRAMES-C14-ecran-portefeuille.png` et `.svg` (quatre états de l'écran 1) | les écrans 2 et 3 n'en ont pas (voir 3) |
| 3 | Chaque spécification couvre contexte, scénarios, critères de validation | ⚠️ | `evidence/C14/preuve-specifications-wireframes.md:62` (US-1 complète) ; `:122` : « Une seule US est spécifiée (US-1) » | user story et wireframe des **écrans 2 et 3** (#24 à élargir : l'écran 3 date du 03/10) |
| 4 | Accessibilité intégrée aux critères d'acceptation | ✅ | même fichier `:102-108` (A3 à A9) | |
| 5 | Accessibilité formulée selon un standard (RGAA…) | ✅ | même fichier : règles RGAA 3.1, 5.4, 5.7, 10.x, 12.x nommées | `:123` le dit : « Aucun audit RGAA outillé n'a été passé » (#25) |

### C15 : concevoir le cadre technique

| # | Critère | État | Preuve (vue ce soir) | Remarque |
|---|---|---|---|---|
| 1 | Spécifications techniques : architecture, dépendances, environnement | ✅ | `evidence/C15/preuve-specifications-techniques.md` : §2 six zones, §3 dépendances et environnement | |
| 2 | Services éco-responsables favorisés | ✅ | même fichier §4 `:111` ; `:125` avoue que ces choix le sont « par effet » | |
| 3 | Diagramme de flux de données | ✅ | `evidence/C15/FLUX-DONNEES-C15-application-RITA.png` et `.svg` ; §5 | |
| 4 | Preuve de concept accessible et fonctionnelle en pré-production | ✅ | `evidence/C15/preuve-preproduction-docker.md` (conteneurs `healthy`) ; **serveur contrôlé ce soir** : `curl https://178-104-184-125.sslip.io/health` rend `200` et `{"status":"ok","project":"RITA"}`, certificat valide | le serveur tourne avec le code d'août : le code du 03/10 s'y déploie après le tag du 15/10 |
| 5 | Conclusion de la preuve de concept donnant un avis précis | ✅ | même fichier `:170` (« Avis : le projet peut se poursuivre sur cette architecture ») et `:194` (« Poursuivre. ») | `:179` écrit « dépendances épinglées » : vrai pour l'image (`requirements-api.txt`), pas pour `requirements.txt` ; la nuance est au §6 des spécifications (« 11 dépendances sur 13 non épinglées ») |

### C16 : coordonner en agile

| # | Critère | État | Preuve (vue ce soir) | Ce qui manque |
|---|---|---|---|---|
| 1 | Cycles, étapes, rôles, rituels et outils de la méthode respectés tout au long du projet | ⚠️ | méthode écrite : `docs/PILOTAGE-AGILE.md` §1 à §5 ; tableau en service depuis le 26/09 | **aucun compte rendu daté de revue du lundi** dans le dépôt (recherche dans `ETAT.md`, `CONTINUITE.md`, `evidence/C16/`, historique Git : seules des « questions pour la revue du lundi » préparées) ; couverture : cinq semaines sur douze (§7 du fichier le dit) |
| 2 | Outils de pilotage disponibles (kanban, burndown, backlog) | ✅ | `gh project item-list 4 --owner Ganda15` : **34 cartes** (Backlog 18, Cette semaine 6, En cours 1, Fait 9) ; `gh issue list --state all` : 48 issues, 20 fermées ; 24 pull requests fusionnées | |
| 3 | Objectifs et modalités des rituels partagés aux parties prenantes | ⚠️ | `docs/PILOTAGE-AGILE.md` §5 (revue du lundi, 15 min, contenu, trace) ; le formateur est collaborateur du dépôt (`bybysker`, vérifié ce soir) donc lit ce fichier | rien ne prouve que le formateur a reçu ou lu cette description ; rituel jamais tenu devant une trace |
| 4 | Éléments de pilotage accessibles à toutes les parties tout au long du projet | ⚠️ | tableau **privé** (`public: false`) ; le fichier §6 affirme un accès en lecture du formateur depuis le 26/09 | **je n'ai pas pu vérifier l'accès du formateur au tableau** (pas d'interface de lecture des droits d'un projet) ; à contrôler par Era dans les paramètres du projet |

### C17 : développer

| # | Critère | État | Preuve (vue ce soir) | Ce qui manque |
|---|---|---|---|---|
| 1 | Environnement de développement conforme aux spécifications | ⚠️ | `requirements.txt` : **13 lignes de dépendances sur 18 sans version fixe** (5 en `==`, dont `mcp>=2.1.1` en borne basse) ; `requirements-api.txt` : 13 sur 13 en `==` | épingler `requirements.txt` (#23, après le tag du 15/10) |
| 2 | Interfaces intégrées et conformes aux maquettes | ⚠️ | écran 1 conforme aux wireframes ; `frontend/` : `index.html`, `indicateurs.html`, `briefing.html` | écrans 2 et 3 sans maquette (#24) |
| 3 | Comportements des composants et navigation conformes | ✅ | `tests/test_smoke_ui.py` (7 tests, vrai navigateur), `tests/test_frontend.py` (55) ; `evidence/C10/preuve-ecran-briefing.md` | |
| 4 | Composants métier conformes aux spécifications | ✅ | `tests/test_indicateurs_socle.py` (13), `_portefeuille.py` (14), `_risque.py` (19), `test_workflow.py` (11), `test_analyst.py` (14) | seize indicateurs spécifiés, treize reçus par le briefing : écart à dire (`evidence/C7/indicateurs-cites-dans-les-textes-2026-10-03.md`) |
| 5 | Gestion des droits d'accès développée et conforme | ⚠️ | `api/main.py:83` (`APIKeyHeader`), `:207` (dépendance posée sur tout le routeur de données) ; rôle PostgreSQL en lecture seule : `tests/test_role_lecture.py` (4 tests) | **un seul niveau d'accès** ; défendre le choix mono-utilisateur par écrit ou ajouter un second niveau (#26, décision D1) |
| 6 | Flux de données intégrés | ✅ | `evidence/C10/preuve-ecran-indicateurs.md` (points de terminaison consommés) ; `evidence/C10/preuve-ecran-briefing.md` (appel `POST /briefing` avec la clé) | |
| 7 | Éco-conception | ⚠️ | choix documentés : `evidence/C15/preuve-specifications-techniques.md` §4 | **aucune mesure** : la recherche d'EcoIndex ou de Lighthouse ne trouve que le plan E4 et une archive (#25) |
| 8 | Préconisations OWASP Top 10 implémentées | ⚠️ | mesures réelles : clé d'API (INC-001), `textContent` côté interface, garde-fous d'entrée et de sortie, crochet `bloquer-secrets` | **aucune revue écrite** des dix entrées (les fichiers `docs/veille/` sur OWASP sont des notes de veille sur l'édition agentique, pas une revue du code) (#29) |
| 9 | Tests couvrant composants métier et gestion des accès | ✅ | local : **803 passed, 2 xfailed**, couverture 94,70 % ; CI (run `37145162817`, commit `0e53ede`) : **774 passed, 29 skipped, 2 xfailed, couverture 94,70 %**, seuil `fail_under = 90` (`.coveragerc:101`) | les **29 tests ignorés en CI** exigent une base et ne tournent que sur le poste : à dire |
| 10 | Sources versionnées et accessibles sur un dépôt distant | ✅ | `gh api repos/Ganda15/rita-agent/collaborators` : `bybysker`, `Ganda15` ; `git ls-remote` : tags `livrable-*` présents | le jury sera invité le moment venu |
| 11 | Documentation technique : installation, architecture, dépendances, tests, accessible | ⚠️ | `README.md` (« Lancer le projet » `:104`, « Lancer les tests » `:122`), `docs/CI-CD.md`, `docs/EXPLOITATION.md` | architecture dispersée entre plusieurs fichiers ; accessibilité de la documentation non contrôlée |

### C18 : automatiser les tests

| # | Critère | État | Preuve (vue ce soir) | Remarque |
|---|---|---|---|---|
| 1 | Documentation de la chaîne : outils, étapes, tâches, déclencheurs | ✅ | `docs/CI-CD.md` : §2 « Les déclencheurs, tous », §3 « Les étapes et les tâches, workflow par workflow » | |
| 2 | Outil d'intégration continue cohérent avec l'environnement | ✅ | GitHub Actions ; `.github/workflows/test.yml` | |
| 3 | Étapes préalables aux tests intégrées (build, configuration) | ✅ | `.github/workflows/test.yml` (installation des dépendances, navigateur) ; `Livraison` : « Installer les dépendances de test » | |
| 4 | La chaîne exécute les tests au déclenchement | ✅ | `test.yml` déclenché sur `push` et `pull_request` vers `main` et `develop` ; run `37145162817` : succès ; **le 03/10 elle a aussi refusé dix états rouges** (INC-007) | |
| 5 | Configurations versionnées sur le dépôt distant | ✅ | `.github/workflows/` : 5 fichiers (`test`, `livraison`, `revue-pr`, `scan-giskard`, `alerte-incident`) | |
| 6 | Documentation d'installation, configuration et test de la chaîne, format accessible | ✅ | `docs/CI-CD.md` : §4 secrets et permissions, §5 « Installer la chaîne », §6 « Tester la chaîne » | accessibilité du format (Markdown, PDF) non contrôlée outil en main |

### C19 : livraison continue

| # | Critère | État | Preuve (vue ce soir) | Ce qui manque |
|---|---|---|---|---|
| 1 | Documentation : étapes, tâches, déclencheurs | ✅ | `docs/CI-CD.md` §2 et §3 (`livraison.yml`) | |
| 2 | Fichiers de configuration reconnus et exécutés | ✅ | workflow Livraison : run `37145162777` (succès, commit `0e53ede`) ; déclencheurs `push` sur `main` et `develop`, tags `livrable-*` (`livraison.yml:25-33`) | |
| 3 | Packaging intégré et sans erreur | ✅ | même run : « Construire l'image (sans publier) » succès, « Vérifier que l'image démarre et répond » succès, « Vérifier que l'accès est bien restreint » succès | |
| 4 | Livraison exécutée une fois le packaging validé | ⚠️ | ordre prouvé par les étapes : dans le run en échec `37144545627`, la porte « Tests — porte de livraison » rouge a **sauté** la construction, la vérification et la publication ; dans le run vert, la publication est sautée hors tag ; `main` protégée par le ruleset `main protegee` (PR relue, `pytest`, `evals` et `revue` verts) | **la publication réelle n'a jamais tourné** : seul tag existant `livrable-E1-v1`, antérieur au workflow ; la première exécution sera le tag `livrable-E1-v2` du 15/10 (tâche T8) |
| 5 | Sources de la chaîne versionnées sur le dépôt distant | ✅ | `.github/workflows/livraison.yml` | |

## 3. Ce que ce recomptage a trouvé en route

- **INC-007** : en lisant l'historique d'exécutions pour prouver C18, dix exécutions rouges consécutives de Tests et de Livraison sont apparues sur `develop`
  (fiche `evidence/C21/INC-007-ci-rouge-scout-base-reelle.md`). Corrigé, vérifié, mais la détection est venue d'un recomptage, pas d'une alerte.
- **C16** : le seul critère qui recule. Le remède est de tenir les revues des 05/10, 12/10 et 19/10 et d'écrire chacune.
- **C19.4** : un seul ⚠️ qui se ferme tout seul le 15/10, si le tag publie bien l'image (à contrôler, voir T8).

## 4. Limites de ce recomptage

- Je n'ai pas lu les 5 workflows ligne à ligne : j'ai vérifié les déclencheurs de `test.yml` et `livraison.yml` et les étapes réelles de deux exécutions.
- L'accès du formateur au tableau Kanban n'est pas vérifié (C16.4).
- L'accessibilité des documents (C17.11, C18.6) n'est pas contrôlée outil en main.
- Le serveur a été sondé sur `/health` seulement, pas sur les trois écrans.
- Ce recomptage est daté du 03/10 : à refaire une fois les tâches T2 à T9 faites, avant de figer la matrice de preuves du rapport.

## 📖 Glossaire

- **Critère** : phrase du référentiel que le jury coche.
- **Run** : une exécution d'un workflow GitHub Actions, identifiée par un numéro.
- **Porte de livraison** : étape de tests placée avant la construction de l'image ; si elle est rouge, tout ce qui suit est sauté.
- **Ruleset** : règle GitHub qui impose, par exemple, une pull request et des contrôles verts avant toute fusion sur `main`.
- **Épingler une dépendance** : fixer sa version exacte (`==`), pour que deux installations donnent le même résultat.
- **Tests ignorés (skipped)** : tests que pytest n'exécute pas faute d'une condition remplie, ici l'absence de base de données en CI.
- **MCD** : modèle conceptuel de données, schéma Merise des entités et de leurs associations.
- **RGAA** : référentiel général d'amélioration de l'accessibilité, standard français.

# Livrable E4 : recomptage des 36 critères (C14 à C19), le 30/10/2026

> **Statut : préparé le 30/10/2026 par l'assistant, en lecture seule, à la demande d'Era ; enregistré dans le dépôt sur sa
> demande le même soir.** Cinq preuves revérifiées à part le 30/10 (publication sur le tag `livrable-sprint-2-v1`, grilles
> d'`eval/ateliers/`, `requirements.txt`, `docker-compose.yml:78`, empreintes des passages `40490651836` et `40490864523`).
> Les réponses d'Era aux questions du §6 ne sont pas encore écrites : ce décompte n'est pas encore validé par lui.

> **Pourquoi ce document.** Le rapport E4 n'existe pas (le dossier `docs/rapports/E4/`
> ne contient que le recomptage du 03/10). Ce recomptage prépare sa rédaction. Il remplace celui du 03/10
> (`docs/rapports/E4/recomptage-criteres-2026-10-03.md`), dont il reprend les libellés tels quels.
>
> **Dépôt lu** : ce dépôt, branche `develop`, commit `a17d9f4`. Pendant ce recomptage, un commit
> `673b572` est arrivé sur `develop` (il ne touche que `ETAT.md` : convocation du jury). Les numéros de ligne d'`ETAT.md` cités
> ici sont ceux de `673b572`.
>
> **Règle** : un ✅ renvoie à un fichier et une ligne que j'ai ouverts, ou à une commande que j'ai lancée le 30/10. Ce que je
> n'ai pas pu vérifier est écrit « non vérifié », avec la raison. Lecture seule : aucun fichier du dépôt modifié, aucune
> commande d'écriture sur GitHub.
>
> **Commandes lancées le 30/10** : `git log`, `git tag`, `git for-each-ref`, `gh run list` et `gh run view` (journaux de
> passages), `gh api` en lecture (`collaborators`, `rulesets`, `tags`, annotations d'un passage), `gh issue list`,
> `gh pr list`, `gh project item-list 4`. Ni `pytest` en local, ni `curl` sur le serveur (hors des commandes autorisées).

## 1. Le résultat, par compétence

Le fichier du 03/10 a deux totaux : **25 ✅ · 11 ⚠️** au premier passage (T1), puis **27 ✅ · 9 ⚠️** après ses mises à jour
du même soir (T2 à T5, §5 à §8 du fichier). La colonne « 03/10 » ci-dessous prend ce second état, le dernier écrit.

| Compétence | 03/10, premier passage | 03/10, après T2 à T5 | **30/10** | Ce qui bouge |
|---|---|---|---|---|
| C14 (5) | 4 ✅ · 1 ⚠️ | 5 ✅ · 0 ⚠️ | **5 ✅ · 0 ⚠️ · 0 ❌** | rien ; deux écrans nouveaux sans wireframe (réserve) |
| C15 (5) | 5 · 0 | 5 · 0 | **5 ✅ · 0 ⚠️ · 0 ❌** | C15.4 renforcé : la pré-production existe vraiment (pré-test avant chaque mise en service) |
| C16 (4) | 1 · 3 | 1 · 3 | **2 ✅ · 2 ⚠️ · 0 ❌** | C16.3 passe à ✅ (les ateliers croisés des sprints) |
| C17 (11) | 5 · 6 | 6 · 5 | **7 ✅ · 4 ⚠️ · 0 ❌** | C17.11 passe à ✅ (`docs/ARCHITECTURE.md` du 24/10) |
| C18 (6) | 6 · 0 | 6 · 0 | **6 ✅ · 0 ⚠️ · 0 ❌** | rien ; chiffres de la CI remis à jour |
| C19 (5) | 4 · 1 | 4 · 1 | **5 ✅ · 0 ⚠️ · 0 ❌** | C19.4 passe à ✅ : la publication sur tag a vraiment tourné (17 passages) |
| **Total (36)** | **25 · 11 · 0** | **27 · 9 · 0** | **30 ✅ · 6 ⚠️ · 0 ❌** | +3 ✅ |

Les six ⚠️ restants : C16.1, C16.4, C17.1, C17.2, C17.5, C17.8. Aucun ❌. Le rapport fait toujours **0 page**.

## 2. Critère par critère

Colonne « Origine » : **avant** = preuve écrite au plus tard le 04/10 ; **sprint N** = travail des sprints avec le formateur
(12 au 26/10) ; **hors sprint** = travail d'après le 04/10 qui n'appartient à aucun sprint (par exemple les documents de
référence du 24/10).

### C14 : analyser le besoin

| # | Critère | 03/10 | 30/10 | Preuve | Origine | Ce qui manque encore |
|---|---|---|---|---|---|---|
| 1 | La modélisation des données respecte un formalisme (Merise…) | ✅ | ✅ | `docs/rapports/E1/rapport-E1.html:155` (« Modéliser : Merise ») et `:158` (« MCD au formalisme Merise : 6 entités, 6 associations ») ; `db/schema.sql` : 10 `CREATE TABLE` (compté le 30/10) | avant (MCD recadré le 24/10 dans E1 v2.6, hors sprint) | rien ; le reprendre sans le refaire |
| 2 | La modélisation des parcours respecte un formalisme (wireframes…) | ✅ | ✅ | `evidence/C14/WIREFRAMES-C14-ecran-portefeuille.png`, `-ecran-indicateurs.png`, `-ecran-briefing.png` (et `.svg`, `.drawio`) | avant (03/10) | l'application a maintenant **cinq** écrans : `frontend/question.html` (sprint 3) et `frontend/tableau-de-bord.html` (sprint 5) n'ont pas de wireframe ; les wireframes 2 et 3 ont été dessinés après le code |
| 3 | Chaque spécification couvre contexte, scénarios, critères de validation | ✅ | ✅ | `evidence/C14/preuve-specifications-wireframes.md` (US-1) ; `evidence/C14/preuve-specifications-ecrans-2-et-3.md` (US-2, US-3) ; `docs/sprint-3/SPEC.md:61-84` (US1, « En tant qu'évaluateur… », critères CA1.1 à CA1.8) ; `docs/sprint-4/SPEC.md:90-195` (US1 à US9) | avant, sprints 3 et 4 | **le plan du sprint 5 n'est pas dans le dépôt** alors que le code le cite (`monitorage/seuils.py:3`, `api/exercice.py:3`) : le tableau de bord n'a pas de spécification versionnée ; US-2 et US-3 écrites après le code |
| 4 | Accessibilité intégrée aux critères d'acceptation | ✅ | ✅ | `evidence/C14/preuve-specifications-wireframes.md:102-108` (A3 à A9) ; pour l'écran du sprint 5 : `tests/test_tableau_de_bord.py:53-59` (règles RGAA 8.3, 11.1, 12.6 testées) | avant, sprint 5 | la spécification de l'écran de question (`docs/sprint-3/SPEC.md:63-82`) n'a aucun critère d'accessibilité |
| 5 | Accessibilité formulée selon un standard (RGAA…) | ✅ | ✅ | règles RGAA nommées (même fichier) ; Lighthouse 100 sur 100 : `evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md` | avant | pas de lecteur d'écran réel ; les écrans 4 et 5 n'ont pas été mesurés |

### C15 : concevoir le cadre technique

| # | Critère | 03/10 | 30/10 | Preuve | Origine | Ce qui manque encore |
|---|---|---|---|---|---|---|
| 1 | Spécifications techniques : architecture, dépendances, environnement | ✅ | ✅ | `evidence/C15/preuve-specifications-techniques.md:48` (§2, six zones) et `:82` (§3, dépendances) ; `docs/ARCHITECTURE.md` (157 lignes, état du 24/10, §3 briques, §4 points de terminaison, §8 environnements) ; `docs/CADRAGE-V1.md:58-70` (la pile, une raison par outil) | avant, sprint 1, hors sprint (24/10) | `docs/CADRAGE-V1.md:72` porte encore « Élément hors socle : [À CONFIRMER] » ; les schémas d'`ARCHITECTURE.md` datent du 04/10 et ne montrent ni les questions ni la vigie (`docs/ARCHITECTURE.md:7-9`) |
| 2 | Services éco-responsables favorisés | ✅ | ✅ | `evidence/C15/preuve-specifications-techniques.md:118` (§4) ; `requirements-api.txt:5-9` (pyspark, 492 Mo, hors de l'image) | avant | ces choix restent éco-responsables « par effet » (réserve du 03/10) |
| 3 | Diagramme de flux de données | ✅ | ✅ | `evidence/C15/FLUX-DONNEES-C15-application-RITA.png` ; `docs/cadrage/CADRAGE-architecture-v1.png` (12/10) ; `docs/sprint-5/schemas/RITA-sprint5-vigie.png` | avant, sprints 1 et 5 | le diagramme C15 est une preuve datée du 18/08, gardée telle quelle (`evidence/C15/preuve-specifications-techniques.md:14`) : aucun diagramme de flux à jour ne montre le parcours des questions |
| 4 | Preuve de concept accessible et fonctionnelle en pré-production | ✅ | ✅ (renforcé) | chaque version est essayée en pré-production (port 8003, compte `rita_lecture`) avant sa mise en service : `evidence/sprint-2/N0-premiere-livraison-2026-10-14.md:107-109`, `deploy/deployer.py:693` ; dernière livraison lue : passage `40490651836` (27/10, commit `d3a4198`), travail `deployer` « operation reussie » à 10:52:39 UTC ; `ETAT.md:126` : `/health` de production annonce `d3a4198` | sprints 2 à 5 | **non sondé le 30/10** (`curl` hors des commandes autorisées) ; `evidence/C15/` pas mis à jour depuis le 04/10 ; aucune capture de production des écrans portefeuille et indicateurs (seulement briefing et question : `evidence/sprint-2/captures/`, `evidence/sprint-3/captures/`) |
| 5 | Conclusion de la preuve de concept donnant un avis précis | ✅ | ✅ | `evidence/C15/preuve-preproduction-docker.md:170` (« Avis : le projet peut se poursuivre ») et `:194` (« Poursuivre. ») | avant (18/08) | `:179` dit « dépendances épinglées » : toujours vrai pour l'image seulement (voir C17.1) ; la conclusion date du 18/08, avant la mise en production du 14/10 |

### C16 : coordonner en agile

Détail complet au §4.

| # | Critère | 03/10 | 30/10 | Preuve | Origine | Ce qui manque encore |
|---|---|---|---|---|---|---|
| 1 | Cycles, étapes, rôles, rituels et outils de la méthode respectés tout au long du projet | ⚠️ | ⚠️ | cinq sprints documentés du 12 au 26/10 (dossier, plan, livrable, tag, atelier, journal des retours) : `docs/CADRAGE-V1.md`, `docs/CHAINE-V1.md`, `docs/sprint-2/` à `docs/sprint-5/`, `eval/ateliers/` ; méthode Kanban écrite : `docs/PILOTAGE-AGILE.md` | avant (Kanban, 26/09), sprints 1 à 5 | **la méthode écrite n'a pas été suivie** : aucune revue du lundi tenue (`evidence/C16/revues/2026-10-05-revue-S41.md:3` : « revue NON TENUE » ; rien pour le 12, le 19 ni le 26/10) ; le tableau n'a pas bougé pendant les sprints ; rien d'agile avant le 26/09 ; sprint 5 sans plan versionné ni atelier documenté |
| 2 | Outils de pilotage disponibles (kanban, burndown, backlog) | ✅ | ✅ | `gh project item-list 4` (30/10) : 34 cartes (Fait 16, Backlog 15, Cette semaine 2, En cours 1) ; `gh issue list --state all` : 71 issues, 34 fermées ; 96 pull requests fusionnées, dont 72 depuis le 04/10 ; plans de sprint à cases à cocher (`docs/sprint-2/PLAN-TRAVAIL.md:3-4`) | avant, sprints | le tableau est figé : seules les issues #21 à #57 y sont, #21 est « En cours » et #28 (rapport E4) « Cette semaine » depuis S39 ; pas de burndown (choix Kanban, `docs/PILOTAGE-AGILE.md:60-61`) |
| 3 | Objectifs et modalités des rituels partagés aux parties prenantes | ⚠️ | **✅** | chaque atelier croisé a sa grille, avec l'objectif, le format (2 h, présentation, questions, conseils) et les critères : `eval/ateliers/sprint-1-grille.md:5-13` (un pair, 13/10), `eval/ateliers/sprint-2-grille.md:5-12` ; l'original rempli à la main par l'évaluateur, un pair de la promotion, le 15/10 : `eval/ateliers/sprint-2-grille-originale.pdf` (ouvert le 30/10) ; journal des retours à chaque atelier (`eval/ateliers/sprint-3-grille.md:15`) | sprints 1 à 4 | ce format vient de la formation, pas d'Era (à dire) ; le rituel propre à Era (revue du lundi, `docs/PILOTAGE-AGILE.md:56`) n'a jamais été tenu ; grilles 3 et 4 non remplies par le formateur |
| 4 | Éléments de pilotage accessibles à toutes les parties tout au long du projet | ⚠️ | ⚠️ | `gh api .../collaborators` (30/10) : `bybysker` (read), `Ganda15` (admin) ; tout le pilotage des sprints est dans le dépôt ; accès du formateur au tableau accordé le 26/09 (`evidence/C16/preuve-mise-en-place-kanban.md:22`) | avant, sprints | **accès du formateur au tableau non revérifié** (lecture des droits d'un projet par GraphQL, hors des commandes autorisées) ; jury pas encore invité ; accès des pairs évaluateurs non prouvé ; une partie des échanges vit hors du dépôt (Discord, Simplonline, Obsidian) ; rien avant le 26/09 |

### C17 : développer

| # | Critère | 03/10 | 30/10 | Preuve | Origine | Ce qui manque encore |
|---|---|---|---|---|---|---|
| 1 | Environnement de développement conforme aux spécifications | ⚠️ | ⚠️ | `requirements-api.txt:22-50` : tout épinglé (`==`) ; image des runners épinglée (`ubuntu-24.04`, `.github/workflows/test.yml:11`, `evidence/C18/preuve-image-runner-epinglee-2026-10-09.md`) ; `ruff==0.15.17` (`requirements.txt:31`) | avant, sprint 2 | **`requirements.txt` : 12 lignes sans version (`:1-12`) et une borne basse (`mcp>=2.1.1`, `:19`), sur 19 lignes de dépendances** ; la CI installe aussi `playwright` et `giskard-llm` sans version (`test.yml:22` et `:25`) ; issue #23 ouverte, tâche T7 non faite |
| 2 | Interfaces intégrées et conformes aux maquettes | ⚠️ | ⚠️ | écran 1 conforme à son wireframe ; `frontend/` : cinq écrans (`index.html`, `indicateurs.html`, `briefing.html`, `question.html`, `tableau-de-bord.html`) | avant, sprints 3 et 5 | wireframes 2 et 3 dessinés d'après l'écran ; écrans 4 et 5 sans maquette ; les maquettes de la refonte sont « proposées, non implémentées » (`docs/conception/frontend/refonte-2026-10.md:5` et `:7`) |
| 3 | Comportements des composants et navigation conformes | ✅ | ✅ | fonctions de test : `tests/test_smoke_ui.py` (11, vrai navigateur), `tests/test_frontend.py` (69), `tests/test_smoke_tableau_de_bord.py` (13), `tests/test_tableau_de_bord.py` (11) ; toutes vertes dans le passage `41107077221` | avant, sprint 5 | |
| 4 | Composants métier conformes aux spécifications | ✅ | ✅ | `tests/test_indicateurs_socle.py` (13), `_portefeuille.py` (14), `_risque.py` (19), `tests/test_workflow.py` (11), `tests/test_analyst.py` (14), `tests/test_api_question.py` (15) | avant, sprints 3 et 4 | seize indicateurs spécifiés, treize reçus par le briefing ; **deux défauts d'indicateurs ouverts depuis le 04/10** : #78 (RSI à 100 sur une série plate), #79 (pire baisse sur un an parfois positive) ; à dire dans le rapport |
| 5 | Gestion des droits d'accès développée et conforme | ⚠️ | ⚠️ | clé sur toutes les routes de données et d'IA : `api/main.py:260`, `:267`, `:271`, `:281` ; refus journalisés : `api/main.py:206` ; quota de 10 appels par minute : `api/main.py:79-80` ; seconde clé, réservée aux exercices de panne : `api/main.py:77` et `:275` (sprint 5) ; opérations d'administration réservées aux comptes GitHub en écriture, avec nom et motif : `docs/sprint-4/README.md:25-39` ; défense écrite : `evidence/C17/preuve-droits-acces-2026-10-03.md` | avant, sprints 1, 4, 5 | **l'API de production lit la base avec le rôle propriétaire** (`docker-compose.yml:78`, issue #76 ouverte, `docs/sprint-4/README.md:72-74`) alors que la matrice validée lui donne la lecture seule ; `/docs` public ; essais de clé journalisés mais pas freinés (`docs/sprint-4/README.md:78-79`) |
| 6 | Flux de données intégrés | ✅ | ✅ | `evidence/C10/preuve-ecran-indicateurs.md`, `evidence/C10/preuve-ecran-briefing.md` ; parcours des questions : références construites depuis les données stockées (`docs/sprint-3/README.md:19`) ; capture `evidence/sprint-3/captures/production-reponse-et-fiche-2026-10-17.png` | avant, sprint 3 | |
| 7 | Éco-conception | ✅ | ✅ | `evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md` (EcoIndex A, A, D ; Lighthouse 13.5.0) | avant (03/10) | corrections non faites (issue #74 ouverte) ; donc pas de tableau « après » ; écrans 4 et 5 non mesurés |
| 8 | Préconisations OWASP Top 10 implémentées | ⚠️ | ⚠️ | revue : `evidence/C17/revue-owasp-top10-2025-2026-10-03.md:101-110` (S1 à S10). **Faits depuis** : S3 en partie (quota sur `/briefing` et `/question`, `api/main.py:267` et `:282`), S4 (refus de clé journalisés, `api/main.py:206`), S5 (ticker limité à 20 caractères, `api/main.py:281`), S7 en partie (gitleaks sur tout l'historique, `livraison.yml:75-82` ; runner épinglé) ; S10 : certificat renouvelé seul, valable jusqu'au 17/01/2027 (`ETAT.md:270`) | avant, sprints 1, 2, 4 | **S1** : aucun en-tête de sécurité (recherche de `Content-Security-Policy`, `X-Frame-Options`, `Strict-Transport-Security` dans le code : rien hors des preuves) ; **S6** : pas de 503 « aucun fournisseur » ; S7 : `requirements.txt` ; S9 : garde-fous sous 85 % (2 `xfailed` dans les portes) ; issues #73 et #75 ouvertes ; la revue complète (trois listes) reste à faire (`docs/sprint-5/livrable/livrable-sprint-5.md:403-404`) |
| 9 | Tests couvrant composants métier et gestion des accès | ✅ | ✅ | CI, passage `41107077221` (push `develop`, `a17d9f4`, 30/10) : **1808 passed, 32 skipped, 2 xfailed, couverture 96,32 %**, seuil 90 (`.coveragerc:101`) ; tests des accès : `tests/test_role_lecture.py` (4), `tests/test_limiteur.py` (7), `tests/test_exercice.py` (15) | avant, sprints | 32 tests ignorés en CI (ils exigent une base) ; `test.yml:41` dit encore `fail_under = 80` dans un commentaire, le fichier dit 90 |
| 10 | Sources versionnées et accessibles sur un dépôt distant | ✅ | ✅ | `gh api .../collaborators` : `bybysker` (read), `Ganda15` (admin) ; `gh api .../tags` : 18 tags `livrable-*` sur GitHub ; dépôt privé | avant, sprints | le jury n'est pas invité (`ETAT.md:122`) |
| 11 | Documentation technique : installation, architecture, dépendances, tests, accessible | ⚠️ | **✅** | `docs/ARCHITECTURE.md` (24/10, un seul endroit, §1 à §9) ; `README.md:114` (« Lancer le projet ») et `:132` (« Lancer les tests ») ; `docs/CI-CD.md` ; `docs/exploitation.md` ; dépendances commentées dans `requirements.txt` et `requirements-api.txt` | hors sprint (24/10), sprint 5 | accessibilité des documents non contrôlée avec un outil ; schémas de l'architecture datés du 04/10 ; `docs/EXPLOITATION.pdf` date du 11/10 et ne correspond plus à la page (`ETAT.md:321`) |

### C18 : automatiser les tests

| # | Critère | 03/10 | 30/10 | Preuve | Origine | Remarque |
|---|---|---|---|---|---|---|
| 1 | Documentation de la chaîne : outils, étapes, tâches, déclencheurs | ✅ | ✅ | `docs/CI-CD.md:36` (§2 déclencheurs) et `:54` (§3 étapes, sept workflows) ; remis à jour le 24/10 (`docs/CI-CD.md:3`) | avant, mis à jour hors sprint | |
| 2 | Outil d'intégration continue cohérent avec l'environnement | ✅ | ✅ | GitHub Actions ; `.github/workflows/test.yml` ; runner et Python fixés (`test.yml:11`, `:16`) | avant | |
| 3 | Étapes préalables aux tests intégrées (build, configuration) | ✅ | ✅ | `test.yml:17-25` (dépendances, navigateur) ; étape nommée de test des données avant la suite complète (`test.yml:26-39`, 296 passed dans `41107077221`) | avant (04/10) | |
| 4 | La chaîne exécute les tests au déclenchement | ✅ | ✅ | `test.yml:3-7` (push et pull request sur `main` et `develop`) ; passage `41107077221` vert ; le ruleset de `main` exige `lint`, `pytest`, `evals`, `revue`, `secrets`, `construire-et-publier` (`gh api .../rulesets`, mis à jour le 14/10) | avant, sprint 2 | |
| 5 | Configurations versionnées sur le dépôt distant | ✅ | ✅ | `.github/workflows/` : 7 fichiers (`alerte-incident`, `ingestion`, `livraison`, `retour-arriere`, `revue-pr`, `scan-giskard`, `test`) | avant, sprints 2 et 3 | deux workflows de plus qu'au 03/10 |
| 6 | Documentation d'installation, configuration et test de la chaîne, format accessible | ✅ | ✅ | `docs/CI-CD.md:146` (§4 secrets), `:175` (§5 installer), `:200` (§6 tester), `:212` (§7 quand c'est rouge) | avant, mis à jour hors sprint | accessibilité du format non contrôlée outil en main |

### C19 : livraison continue

| # | Critère | 03/10 | 30/10 | Preuve | Origine | Ce qui manque encore |
|---|---|---|---|---|---|---|
| 1 | Documentation : étapes, tâches, déclencheurs | ✅ | ✅ | `docs/CI-CD.md:74` (`livraison.yml`), `:133` (retour arrière), `:140` (ingestion) | avant, sprints 2 et 3 | |
| 2 | Fichiers de configuration reconnus et exécutés | ✅ | ✅ | `livraison.yml:25-36` ; passages verts sur `main` (`40490651836`), sur tag (`40490864523`) et sur `develop` (`41107077298`, 30/10) | avant, sprint 2 | |
| 3 | Packaging intégré et sans erreur | ✅ | ✅ | passage `40490864523` (tag `livrable-E1-v3`) : construction, démarrage, version annoncée par `/health`, accès restreint, absence de `.env`, fichiers de déploiement : toutes les étapes `success` | avant, sprints 2 et 3 | |
| 4 | Livraison exécutée une fois le packaging validé | ⚠️ | **✅** | **publication réelle sur tag** : premier passage `38769577777` (tag `livrable-sprint-2-v1`, 15/10, « Publier l'image vérifiée » `success`) ; livrables E : `40114528668` (`livrable-E1-v2`, 24/10), `40490864523` (`livrable-E1-v3`, 27/10, image `ghcr.io/ganda15/rita-api:livrable-E1-v3`, empreinte `sha256:0259d6bd…`). **Refus quand la porte est rouge** : passage `39653430203` (`livrable-sprint-4-v1`, 21/10), étape « porte de livraison » en échec, construction et publication sautées. **Mise en service seulement après** : `livraison.yml:331-356` (`deployer` attend `construire-et-publier`) ; passage `40490651836` | sprints 2 à 5 | **la preuve prévue par T8 n'est pas écrite** (`evidence/C19/preuve-publication-sur-tag.md` n'existe pas) ; voir aussi l'étiquette `sha-d3a4198` (§3.3) |
| 5 | Sources de la chaîne versionnées sur le dépôt distant | ✅ | ✅ | `.github/workflows/livraison.yml`, `retour-arriere.yml`, `ingestion.yml`, `deploy/deployer.py`, `deploy/compose.prod.yml` ; règles `main protegee` et `tags livrable-* figes` (`gh api .../rulesets`, actives) | avant, sprint 2 | |

## 3. Ce qui a changé depuis le 03/10

### 3.1 Les dix écarts du plan (§3 de `docs/PLAN-E4-rapport.md`)

| # | Écart du plan | État au 30/10 | Preuve |
|---|---|---|---|
| 1 | Écrans 2 et 3 sans user story ni wireframe | **fermé le 03/10** (T2), écrit après le code | `evidence/C14/preuve-specifications-ecrans-2-et-3.md` ; issue #24 fermée le 05/10. **Nouvel écart** : écrans de question et tableau de bord sans wireframe |
| 2 | Aucune mesure d'éco-conception ni d'accessibilité | **fermé le 03/10** (T3) ; le tableau « après » n'existe pas | `evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md` ; issue #74 (corrections) ouverte |
| 3 | Revue OWASP non écrite | **écrite le 03/10** (T4) ; corrections en partie faites pendant les sprints (S3 en partie, S4, S5, S7 en partie) ; S1 et S6 non faits | `evidence/C17/revue-owasp-top10-2025-2026-10-03.md:101-110` ; `api/main.py:206`, `:267`, `:281` ; issue #75 ouverte |
| 4 | Un seul niveau d'accès | **défendu le 03/10** (T5) ; une seconde clé (exercices) depuis le sprint 5 ; écart #76 (rôle propriétaire) **ouvert** | `evidence/C17/preuve-droits-acces-2026-10-03.md` ; `api/main.py:275` ; `docker-compose.yml:78` |
| 5 | `requirements.txt` sans versions | **ouvert** : 12 lignes sans version, 1 borne basse, sur 19 ; dernier changement du fichier le 14/10 (ajout de `ruff`) | `requirements.txt:1-12`, `:19` ; issue #23 ouverte ; `git log -- requirements.txt` |
| 6 | Architecture dispersée | **fermé le 24/10** | `docs/ARCHITECTURE.md` (PR #144) |
| 7 | Publication sur tag jamais exécutée | **fermé le 15/10** : 17 passages sur des tags `livrable-*`, 15 verts, 2 en échec avant publication | `gh run list --workflow=livraison.yml` ; passages `38769577777`, `40114528668`, `40490864523`, `39653430203` |
| 8 | Aucun compte rendu de revue du lundi | **ouvert** : trame du 05/10 jamais remplie ; aucune revue pour le 12, le 19 ni le 26/10 ; `docs/PILOTAGE-AGILE.md` inchangé depuis le 03/10 | `evidence/C16/revues/2026-10-05-revue-S41.md:3` ; `git log -- docs/PILOTAGE-AGILE.md evidence/C16` (dernier commit `074ce5f`, 03/10) |
| 9 | Code non déployé sur le serveur | **fermé le 14/10** (livraison N0), puis à chaque fusion dans `main` ; dernière lue : 27/10, `d3a4198` | `evidence/sprint-2/N0-premiere-livraison-2026-10-14.md:143-148` ; passage `40490651836` ; `ETAT.md:126` |
| 10 | Seize indicateurs spécifiés, treize dans le briefing | **inchangé**, à dire ; deux défauts d'indicateurs ouverts en plus (#78, #79) | `gh issue list` |

### 3.2 Les tâches T1 à T12

| T | État au 30/10 |
|---|---|
| T1 recomptage | fait le 03/10 ; refait ici |
| T2 à T5 | faits le 03/10 (voir §3.1) |
| T6 revues du lundi | **non fait** : trame seulement |
| T7 épingler `requirements.txt` | **non fait** |
| T8 relever la publication sur tag | exécutée par la chaîne (passages cités) ; **fichier de preuve absent** |
| T9 déployer, captures des trois écrans en HTTPS | déployé par la chaîne ; captures de production du briefing seulement parmi les trois écrans d'E4 ; `evidence/C15/` non mis à jour |
| T10 rédiger | **non commencé** (0 page ; `ETAT.md:97`) |
| T11, T12 | non commencés ; le gel du 25/10 prévu par le plan est passé ; E4 est dû le 05/11 (`ETAT.md:97`) |

### 3.3 Constats nouveaux, trouvés en recomptant

1. **L'étiquette `sha-d3a4198` ne désigne plus l'image de production.** Le passage `40490651836` (fusion dans `main`, 27/10)
   a publié `sha-d3a4198` avec l'empreinte `sha256:c818dcc5…`, celle que le serveur a reçue. Le passage du tag
   `livrable-E1-v3` (`40490864523`), sur le même commit, a reconstruit l'image et republié `sha-d3a4198` et `latest` avec
   l'empreinte `sha256:0259d6bd…` (journal, lignes « digest »). La production n'est pas touchée (elle est désignée par
   son empreinte), mais l'image publiée sous le tag d'un livrable n'est pas, octet pour octet, celle qui tourne. À dire,
   ou à corriger après le 05/11.
2. **La chaîne échoue fermée sur une panne de facturation.** Le passage `40325990967` (`main`, 26/10) : `lint` et
   `secrets` non lancés, « recent account payments have failed or your spending limit needs to be increased »
   (annotation GitHub lue le 30/10) ; rien n'a été livré.
3. **Le tableau Kanban est figé.** Aucune des issues ouvertes depuis le 04/10 (19, de #77 à #152) n'y figure.
4. **`docs/CADRAGE-V1.md:72`** garde un « [À CONFIRMER] » visible par le formateur.
5. **`test.yml:41`** cite un seuil de couverture de 80 dans un commentaire ; le seuil réel est 90 (`.coveragerc:101`).
6. **La collecte des cours n'est pas planifiée sur le serveur** (`ETAT.md:140`) : la démonstration d'E4 affichera des
   cours en retard si le rattrapage manuel n'est pas refait avant.

## 4. C16 en détail : ce que le dépôt prouve, et ce qu'il ne prouve pas

### 4.1 Les cycles de travail documentés

Deux méthodes se sont succédé. Le Kanban personnel (26/09, `docs/PILOTAGE-AGILE.md`), puis les cinq sprints de la phase 6
du fil rouge, organisés par la formation, chacun clos par un atelier croisé.

| Cycle | Dates (d'après les commits et les tags) | Cadrage du cycle | Livré | Revue par un tiers | Fichiers |
|---|---|---|---|---|---|
| Plan des 12 semaines | depuis le 16/08 | `docs/PLAN-12-SEMAINES.md` | | aucune | `docs/PILOTAGE-AGILE.md:16-17` |
| Kanban | 26/09 au 03/10 environ | `docs/PILOTAGE-AGILE.md` §1 à §5 | 16 cartes « Fait » | aucune revue tenue | `evidence/C16/preuve-mise-en-place-kanban.md` |
| Sprint 1, cadrer | 12 au 13/10 | `docs/CADRAGE-V1.md` (créé le 12/10), contrat personnel §6 | dossier + PDF « demandé par le formateur » (`docs/cadrage/README.md:3`) | **atelier n°1, 13/10, évaluateur : un pair de la promotion** | `eval/ateliers/sprint-1-grille.md:5-30`, suite donnée `:36-46`, commit `bc143c3` |
| Sprint 2, le socle et la chaîne | 13 au 15/10 | `docs/CHAINE-V1.md:3` (« validée section par section les 13 et 14/10 »), `docs/sprint-2/PLAN-TRAVAIL.md` | livraisons N0 à N2 ; tags `livrable-sprint-2-v1` à `v3` (15/10) | **atelier n°2, 15/10, évaluateur : un pair de la promotion** ; 5 critères ✓ | `eval/ateliers/sprint-2-grille.md`, original `eval/ateliers/sprint-2-grille-originale.pdf` |
| Sprint 3, les données et l'ancrage | 15 au 19/10 | `docs/sprint-3/SPEC.md:3` (« Validée par Era le 15/10 »), `docs/sprint-3/PLAN-TRAVAIL.md` | N5 à N8 ; compte rendu `docs/sprint-3/COMPTE-RENDU-N5-2026-10-16.md` ; tags v1 (18/10), v2 (19/10) | **atelier n°3, 19/10, avec le formateur**, grille non remplie, retours oraux ; ingestion lancée en direct (passage `39265862974`) | `eval/ateliers/sprint-3-grille.md:8-44`, suite `:52-63` |
| Sprint 4, la composante agentique et les garde-fous | 18 au 22/10 | `docs/sprint-4/AVENANT-1.md` (décidé le 18/10), `docs/sprint-4/SPEC.md:3` (décisions du 20/10), `docs/sprint-4/PLAN-TRAVAIL.md`, `docs/sprint-4/CONTRAT.md` | N10 à N15 ; tags v1 (refusé par la chaîne), v2, v3 (21/10) | **atelier n°4, 22/10, avec le formateur**, grille non remplie | `eval/ateliers/sprint-4-grille.md:3-12` |
| Sprint 5, la vigie et la démo | 22 au 26/10 | **plan absent du dépôt** (cité par le code) ; `docs/sprint-5/DEMO.md` | N16, N17 (23/10) ; livrable v1 à v5 ; tags `livrable-sprint-5-v1` à `v5` | **atelier n°5 : aucune trace** (ni date, ni grille, ni retours) ; une « discussion avec le formateur », sans date | `docs/sprint-5/livrable/livrable-sprint-5.md:364-380` |

Chaque sprint suit les mêmes étapes, visibles dans le dépôt : un dossier ou une spec, un plan de travail découpé en tâches,
des pull requests relues par la revue automatisée, une livraison en production, un livrable PDF, un tag, puis un atelier et
un journal des retours qui dit pour chaque retour s'il est traité, reporté ou écarté.

### 4.2 Les rôles documentés

| Rôle | Qui | Où c'est écrit |
|---|---|---|
| Porteur du produit et développeur, décide | Era | `docs/PILOTAGE-AGILE.md:23` ; décisions signées « Era » : `docs/sprint-3/SPEC.md:3`, `docs/sprint-4/SPEC.md:3`, `docs/sprint-4/AVENANT-1.md:3`, `docs/sprint-2/README.md:24-33` |
| Présenté, à chaque atelier | Era | en-tête de chaque grille d'`eval/ateliers/` |
| Évaluateur pair | deux pairs de la promotion (13/10 et 15/10) | `eval/ateliers/sprint-1-grille.md:7`, `eval/ateliers/sprint-2-grille.md:7` |
| Évaluateur, relecteur des livrables | le formateur (compte `bybysker`, lecture) | `eval/ateliers/sprint-3-grille.md:8`, `sprint-4-grille.md:3` ; `docs/FILE-DE-VALIDATION.md` |
| Revue automatique des pull requests | workflow `revue-pr.yml`, check `revue` exigé | `docs/PILOTAGE-AGILE.md:25` ; ruleset `main protegee` |
| Assistant de développement | assistant IA, ne décide pas | `docs/PILOTAGE-AGILE.md:26` |

Les grilles disent « puis on inverse les rôles » (`eval/ateliers/sprint-1-grille.md:9`) : Era a donc dû évaluer un pair.
**Aucune trace de ce rôle dans le dépôt.**

### 4.3 Les échanges avec les formateurs, documentés

| Date | Échange | Fichier | Force de la preuve |
|---|---|---|---|
| début août | « Bloc 1 » : trois réponses (big data, cadrage E1, sous-traitant) | `docs/FILE-DE-VALIDATION.md:143-160` | rapporté ; capture Discord « à reprendre » (`:160`) |
| 28/08 | RAG et MCP obligatoires | `docs/FILE-DE-VALIDATION.md:129-139` | rapporté par Era le jour même |
| 03/10 | chapitre « Données » validé (« Très bon travail… Rien à redire. ») | `CHANGELOG.md:834-837` | citation recopiée |
| 13/10 | dossier de cadrage demandé en PDF par le formateur | `docs/cadrage/README.md:3` | rapporté |
| 19/10 | atelier n°3 : neuf retours oraux sur la présentation | `eval/ateliers/sprint-3-grille.md:26-44` | notes de séance ; quatre retours relevés le 21/10 dans une transcription **qui n'est pas dans le dépôt** |
| 22/10 | atelier n°4 : mêmes conseils qu'au n°3 | `eval/ateliers/sprint-4-grille.md:8-10` | une note de trois lignes |
| sans date | discussion sur le déroulé du sprint 5 | `docs/sprint-5/livrable/livrable-sprint-5.md:366-368` | rapporté, sans date |
| en attente | validation de l'avenant n°1 ; réponse sur le tiers du critère 5 (D8) | `docs/sprint-4/AVENANT-1.md:3-5`, `docs/sprint-4/README.md:80-81` | aucune réponse écrite |
| 28/10 | livret E1 v3 accepté ; budget demandé | `docs/FILE-DE-VALIDATION.md:123` ; `ETAT.md:107-111` | rapporté par Era, capture « à verser » |
| 29/10 | rapport E3 v1.9 envoyé | `docs/FILE-DE-VALIDATION.md:124` | envoi tracé ; retour attendu |
| 30/10 | oral blanc 1 (Héléna VICENTE, Nadège MIQUEY, Elbby AGWU) | `ETAT.md:26-31` | résumé ; détail dans Obsidian, hors du dépôt |

### 4.4 Les décisions documentées

- Sprint 2 : décisions d'Era avant la première livraison (`docs/sprint-2/README.md:24-33`) ; périmètre de l'atelier n°2
  (`docs/CHAINE-V1.md:329`).
- Sprint 3 : D1 à D5 avec leur raison et leur date (`CONTINUITE.md:123-127`) ; tag avant l'atelier (`CHANGELOG.md:380-382`).
- Sprint 4 : avenant n°1 (`docs/sprint-4/AVENANT-1.md`) ; D2 à D9 (`docs/sprint-4/SPEC.md:243`) ; écarts au plan du sprint 1
  (`docs/sprint-4/CONTRAT.md:18`).
- Sprint 5 : « le sprint 5 ne touche pas l'original » (`CHANGELOG.md`, entrée du 22/10).
- Limite : `CONTINUITE.md` n'a plus été mis à jour après le 17/10 (`CONTINUITE.md:7`) ; les décisions des sprints 4 et 5
  ne sont que dans `ETAT.md`, le `CHANGELOG.md` et les specs.

### 4.5 Ce qui n'a pas de preuve

- **Les revues du lundi** du 28/09, du 05/10, du 12/10, du 19/10 et du 26/10. La seule trace est une trame préparée le 03/10
  par l'assistant et marquée « revue NON TENUE » (`evidence/C16/revues/2026-10-05-revue-S41.md:3`). Ce n'est pas une revue.
- **Le tableau pendant les sprints** : aucune carte de sprint, aucun mouvement visible ; #21 « En cours » et #28 « Cette
  semaine » depuis S39.
- **L'atelier n°5** : ni date, ni évaluateur, ni grille (`eval/ateliers/sprint-5-grille.md` n'existe pas, alors que le
  livrable annonce qu'elle y sera versée, `docs/sprint-5/livrable/livrable-sprint-5.md:379-380`).
- **Les originaux** : la grille Excel de l'atelier n°1 et la transcription de l'atelier n°3 ne sont pas dans le dépôt
  (seule la grille de l'atelier n°2 l'est, en PDF).
- **Le plan du sprint 5**, cité dans 15 fichiers Python (code et tests, `grep -rli "plan du sprint 5"`), n'est pas versionné.
- **Era évaluateur d'un pair**, **l'accès du formateur au tableau** aujourd'hui, **la capture de l'acceptation d'E1 v3**.
- **Aucune rétrospective** au sens agile ; le journal des retours de chaque atelier en tient lieu, sans être une
  rétrospective d'équipe.

### 4.6 Ce que le rapport peut dire honnêtement

RITA a été piloté par un plan de semaines (août), un tableau Kanban (fin septembre, abandonné début octobre), puis par cinq
sprints courts du 12 au 26/10, imposés par la formation, chacun avec un dossier, un plan, une livraison en production, un
tag et une revue par un tiers (deux pairs, puis le formateur). Les rituels de ces sprints sont prouvés pour les ateliers 1 à 4.
La revue hebdomadaire écrite dans `docs/PILOTAGE-AGILE.md` n'a jamais été tenue : le dire, sans la reconstituer.

## 5. Matière disponible pour chaque section du rapport (plan §4)

| Section | Fichiers à citer |
|---|---|
| **1. Analyser le besoin (C14)** | `docs/rapports/E1/rapport-E1.html:155-158` et `docs/rapports/E1/images/mcd-recadre.png` (MCD) ; `evidence/C14/preuve-specifications-wireframes.md`, `evidence/C14/preuve-specifications-ecrans-2-et-3.md` et les trois `WIREFRAMES-C14-*.png` ; `docs/CADRAGE-V1.md:6-17` (besoin, hors périmètre) et `:108-132` (contrat personnel, Étant donné / quand / alors) ; user stories des sprints : `docs/sprint-3/SPEC.md:61-180`, `docs/sprint-4/SPEC.md:90-200` ; `docs/conception/donnees/` (chapitre validé le 03/10) ; `docs/conception/frontend/refonte-2026-10.md` (maquettes proposées, à présenter comme non faites) |
| **2. Cadre technique (C15)** | `evidence/C15/preuve-specifications-techniques.md`, `evidence/C15/preuve-preproduction-docker.md:168-194` ; `docs/ARCHITECTURE.md` ; `docs/CADRAGE-V1.md:58-72` (pile) ; `docs/cadrage/CADRAGE-architecture-v1.png` ; `docs/CHAINE-V1.md` (la chaîne conçue avant le code) ; `evidence/sprint-2/N0-premiere-livraison-2026-10-14.md` (pré-production réelle, deux refus avant la réussite) ; `requirements-api.txt:1-20` (choix éco-responsable) |
| **3. Coordonner en agile (C16)** | `docs/PILOTAGE-AGILE.md` ; `evidence/C16/preuve-mise-en-place-kanban.md` ; `eval/ateliers/sprint-1-grille.md` à `sprint-4-grille.md` et `sprint-2-grille-originale.pdf` ; `docs/sprint-2/README.md` à `docs/sprint-5/README.md` ; `docs/sprint-4/AVENANT-1.md`, `docs/sprint-4/CONTRAT.md` ; `docs/FILE-DE-VALIDATION.md` ; `CONTINUITE.md:123-127` ; le §4 de ce document pour les limites |
| **4. Développer (C17)** | `frontend/` (cinq écrans) ; `api/main.py` (lignes du tableau C17) ; `evidence/C10/preuve-ecran-briefing.md`, `preuve-ecran-indicateurs.md` ; `evidence/C17/preuve-droits-acces-2026-10-03.md`, `revue-owasp-top10-2025-2026-10-03.md`, `preuve-eco-conception-et-accessibilite-2026-10-03.md` ; `docs/sprint-4/README.md` §2 et §3 (opérations d'administration, périmètre d'accès) ; `README.md:114-147` ; `evidence/sprint-3/captures/` |
| **5. Automatiser les tests (C18)** | `docs/CI-CD.md` ; `.github/workflows/test.yml` ; `evidence/C18/preuve-integration-continue-2026-10-03.md`, `evidence/C18/preuve-image-runner-epinglee-2026-10-09.md` ; `evidence/C12/preuve-ci-develop-2026-10-24.md` ; passage `41107077221` (1808 passed, 96,32 %) ; PR cassée #93 bloquée : `evidence/sprint-2/journaux/pr-93-commit-casse.txt` ; rapport E3 (renvoi pour le détail) |
| **6. Livraison continue (C19)** | `.github/workflows/livraison.yml`, `retour-arriere.yml`, `ingestion.yml` ; `deploy/deployer.py` ; `docs/CI-CD.md:74-145` ; `evidence/C19/preuve-protection-main-2026-10-03.md`, `ruleset-main-2026-10-14.json`, `preuve-image-de-base-galerie-amazon-2026-10-10.md` ; `evidence/sprint-2/N0-premiere-livraison-2026-10-14.md`, `N1-retour-arriere-2026-10-14.md`, `evidence/sprint-2/journaux/` ; passages `38769577777`, `39653430203`, `40490651836`, `40490864523` |
| **7. Démonstration et limites** | `docs/sprint-5/DEMO.md` (scénario de 9 min 40, répété deux fois) ; `docs/exploitation.md#rattrapage-cours-production` (cours à jour avant la démo) ; les « ce qui n'est pas fait » de `docs/sprint-2/README.md:66-83`, `docs/sprint-3/README.md:51-77`, `docs/sprint-4/README.md:70-88`, `docs/sprint-5/livrable/livrable-sprint-5.md:382-406` ; le §3.3 de ce document |
| **8. Matrice de preuves** | le §2 de ce document (36 lignes), à figer après les dernières corrections |

## 6. Questions pour l'étudiant

1. **Atelier n°5** : a-t-il eu lieu ? Si oui, à quelle date, avec qui, et la grille a-t-elle été remplie ? Rien n'est dans
   le dépôt.
2. **Revues du lundi** (28/09, 05/10, 12/10, 19/10, 26/10) : tenues sans trace, ou pas tenues ? La réponse s'écrit telle
   quelle ; on ne reconstitue rien.
3. **Le tableau Kanban** : abandonné au profit des sprints ? On le dit dans le rapport ? Et les cartes #21, #23, #28 et #37,
   qui ne disent plus le vrai, on les met à jour (avec la date d'aujourd'hui) ou on les laisse ?
4. **Accès du formateur au tableau** : à vérifier dans les paramètres du projet GitHub (je ne peux pas le lire).
5. **Avenant n°1 et D8** : le formateur a-t-il répondu ?
6. **Évaluateur d'un pair** : as-tu évalué les deux pairs de ces ateliers ? Une trace existe-t-elle (grille de leur dépôt) ?
7. **Originaux** : la grille Excel de l'atelier n°1, la transcription de l'atelier n°3, la capture Discord de l'acceptation
   d'E1 v3 : les verser dans le dépôt, ou les citer comme hors dépôt ?
8. **Plan du sprint 5** : où est-il ? Le verser (`docs/sprint-5/`) ou dire qu'il est resté hors du dépôt ?
9. **Les briefs des sprints** (durée, ateliers, grilles) viennent-ils bien de la formation ? Le rapport doit distinguer ce
   qui était imposé de ce que tu as choisi.
10. **`requirements.txt`** (#23) : épingler avant le 05/11 (un changement de dépendances relance toute la chaîne) ou
    l'écrire comme limite ?
11. **Rôle propriétaire de l'API** (#76) et **en-têtes de sécurité** (S1) : corriger avant le 05/11 ou les écrire comme
    limites ? (C17.5 et C17.8 restent ⚠️ sinon.)
12. **Étiquette `sha-d3a4198`** (§3.3) : la dire dans le rapport, ou changer la chaîne après le 05/11 pour ne publier
    l'étiquette `sha-` que depuis `main` ?
13. **Jury** : quand l'inviter comme collaborateur ? (Aujourd'hui seul `bybysker` l'est.)
14. **`docs/CADRAGE-V1.md:72`** (« [À CONFIRMER] ») : à trancher, puisque le formateur a ce dossier.
15. **Démonstration d'E4** (jury du 01/12, `ETAT.md:49-52`) : rattrapage des cours fait avant chaque oral, ou collecte
    planifiée sur le serveur (issue #36) ?
16. Les plans de sprint nomment l'outil d'assistant utilisé pour les exécuter (`docs/sprint-2/PLAN-TRAVAIL.md:3`) : on
    le garde tel quel ? (La méthode le déclare déjà, `docs/PILOTAGE-AGILE.md:26`.)

## 7. Limites de ce recomptage

- Je n'ai pas lancé `pytest` en local ni sondé le serveur : les chiffres de tests viennent du journal de la CI du 30/10,
  l'état de la production d'`ETAT.md:126` et du passage `40490651836`.
- Je n'ai pas pu lire les droits du tableau Kanban (GraphQL), ni le registre d'images ghcr.io.
- Je n'ai lu qu'un PDF (la grille de l'atelier n°2). Les livrables PDF des sprints n'ont pas été rouverts ; leurs `.md` l'ont
  été en partie.
- `ETAT.md` (2 400 lignes environ) a été lu jusqu'à la ligne 565, puis par recherche.
- Les worktrees des sprints (`rita-agent-sprint-3` à `-5`) n'ont pas été ouverts, comme demandé.
- Les comptes de tests par fichier sont des comptes de fonctions `test_`, pas de cas paramétrés.

## 📖 Glossaire

- **Critère** : phrase du référentiel que le jury coche ; 36 pour E4.
- **Sprint** : cycle de travail court et daté, avec un but, une livraison et une revue à la fin.
- **Atelier croisé** : revue de fin de sprint où un pair ou le formateur évalue le projet avec une grille, puis où les rôles
  s'inversent.
- **Journal des retours** : liste des remarques reçues, chacune marquée traitée, reportée ou écartée.
- **Kanban** : méthode agile à flux continu, avec un tableau de colonnes et une limite de travail en cours.
- **Burndown** : courbe du travail restant dans un sprint.
- **Avenant** : changement écrit et daté d'un document déjà validé.
- **Passage (run)** : une exécution d'un workflow GitHub Actions, identifiée par un numéro.
- **Porte de livraison** : étape de tests placée avant la construction de l'image ; rouge, elle arrête tout ce qui suit.
- **Empreinte (digest)** : identifiant `sha256:…` d'une image ; deux constructions du même code peuvent en avoir deux.
- **Étiquette d'image** : nom lisible (`livrable-E1-v3`, `sha-d3a4198`, `latest`) posé sur une empreinte ; il peut être
  déplacé, l'empreinte non.
- **Pré-production** : environnement où l'on essaie une version avant de la mettre en service ; ici le port 8003 du serveur.
- **Ruleset** : règle GitHub qui impose une pull request et des contrôles verts avant toute fusion sur `main`.
- **Épingler une dépendance** : fixer sa version exacte (`==`).
- **RGAA** : référentiel général d'amélioration de l'accessibilité, standard français.
- **OWASP Top 10** : liste des dix risques de sécurité les plus courants des applications web.
- **EcoIndex, Lighthouse** : outils qui notent une page web (impact environnemental ; performance et accessibilité).

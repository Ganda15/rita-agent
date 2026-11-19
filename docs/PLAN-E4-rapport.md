# Plan E4 : le rapport de l'application (C14 à C19), du point de départ du 03/10 au gel du 25/10

> **Statut au 19/11 : réalisé ; rapport E4 v1.12, tag `livrable-E4-v9`. Plan proposé le 03/10/2026, gardé tel qu'écrit.** Aucun rapport n'est écrit : `docs/rapports/`
> contient E1, E2 (v0.1) et E3, pas E4. Ce plan dit ce que le jury attend, où RITA en est mesuré, ce qui manque carte par
> carte, comment le rapport est construit, la démonstration, et le calendrier jusqu'au tag `livrable-E4-v1`.
> Sources : la vérification des 36 critères du 26/09 (Obsidian, `Projets/RITA/04-Certif/RITA - Vérification critères RNCP E4 (2026-09-26).md`),
> `ETAT.md`, `CONTINUITE.md`, les dossiers `evidence/C14` à `evidence/C19`, `docs/CI-CD.md`, `docs/PILOTAGE-AGILE.md`.

## 1. Ce que le jury attend

| Élément | Valeur | Source |
|---|---|---|
| Compétences | C14 analyser le besoin, C15 concevoir le cadre technique, C16 coordonner en agile, C17 développer, C18 automatiser les tests, C19 livraison continue | référentiel RNCP 37827 |
| Critères à cocher | **36** : C14 (5), C15 (5), C16 (4), C17 (11), C18 (6), C19 (5) | note de suivi des livrables, recopiés tels quels |
| Rapport | 15 à 20 pages | MASTER-GUIDE, section E4 |
| Oral | 20 minutes, **avec démonstration de l'application** | idem ; démonstration obligatoire pour E3 et E4 |
| Gel | **25/10/2026**, tag `livrable-E4-v1`, lien du tag envoyé par Era | `ETAT.md`, `docs/FILE-DE-VALIDATION.md` |
| Passage | les cinq livrables sont évalués le 05/11 ; l'oral blanc du 29-30/10 ne porte que sur E1 et E3 | chef de projet, 03/10 |

Le dépôt est privé, le formateur et le jury y sont invités ; un livrable ne pointe jamais hors du dépôt.

## 2. Où RITA en est, mesuré

Dernier décompte complet : **26/09, 21 ✅, 11 ⚠️, 4 ❌**. Depuis, quatre changements, chacun avec sa preuve :

| Changement | Critères touchés | Preuve |
|---|---|---|
| Kanban GitHub, backlog d'issues, revue du lundi (26/09) | C16 : 4 ❌ deviennent 2 ✅ et 2 ⚠️ (« tout au long du projet » ne vaut que depuis le 26/09) | `docs/PILOTAGE-AGILE.md`, `evidence/C16/preuve-mise-en-place-kanban.md` |
| `livraison.yml` : construire, vérifier l'image, publier seulement sur un tag (26/09, PR 46) | C19 critère 4 : l'ordre est prouvé, la publication ne l'est pas encore | run `36247837793` |
| Chaîne d'intégration continue documentée et mesurée (03/10) | C18 : 6 sur 6 | `evidence/C18/preuve-integration-continue-2026-10-03.md`, `docs/CI-CD.md` |
| Règles de protection de `main` et des tags `livrable-*` (03/10) | C19 critère 4 (« une fois le packaging validé ») et critère 5 | `evidence/C19/preuve-protection-main-2026-10-03.md` |
| Écran 3, le briefing (03/10) | C17 critères 2 et 3 (interfaces, composants) ; **ouvre un nouvel écart en C14** (voir §3) | `evidence/C10/preuve-ecran-briefing.md` |

**Recompté le 03/10 au soir (tâche T1) : 25 ✅, 11 ⚠️, 0 ❌**, critère par critère, avec la preuve vue ce soir :
`docs/rapports/E4/recomptage-criteres-2026-10-03.md`. Le total ne bouge pas par rapport au calcul ci-dessus, mais deux lignes
changent : C19 gagne un ✅ (documentation de la chaîne) et C16 en perd un (aucun compte rendu daté de revue). Le décompte se refait
une dernière fois après T2 à T9, avant de figer la matrice de preuves du rapport.

## 3. Les écarts restants, carte par carte

| # | Écart | Critères | Carte | Action | Effort | Qui décide |
|---|---|---|---|---|---|---|
| 1 | L'écran 2 (indicateurs) n'a ni user story ni wireframe ; **l'écran 3 (briefing), fait le 03/10, non plus** | C14.3 (« chaque spécification »), C17.2 | #24 (à élargir aux deux écrans) | une user story et un wireframe par écran, mêmes gabarits que l'écran 1 (`evidence/C14/preuve-specifications-wireframes.md`) | 2 à 3 h | |
| 2 | Aucune mesure d'éco-conception ni d'accessibilité outillée | C17.7, C14.5 | #25 | mesurer les 3 pages (EcoIndex ou Lighthouse), tableau avant/après | 1 h | Era (D2) |
| 3 | Revue OWASP Top 10 non écrite, entrée par entrée | C17.8 (et C9) | #29 | revue écrite des 10 entrées contre le code, chaque ligne avec son fichier ou son test | 3 h | Era (D3 : l'avancer) |
| 4 | Un seul niveau d'accès (une clé) | C17.5 | #26 | défendre le choix mono-utilisateur par écrit, avec le modèle de menace, ou ajouter un second niveau | 1 h pour défendre | Era (D1) |
| 5 | `requirements.txt` : 13 dépendances sans version (l'image est épinglée, pas l'environnement de développement) | C17.1 | #23 | épingler, relancer la suite et la chaîne | 1 h | |
| 6 | Documentation d'architecture dispersée ; accessibilité de la documentation non vérifiée | C17.11 | #27 (en grande partie fermée) | une page « architecture » qui renvoie aux autres ; contrôle d'accessibilité des PDF et des pages | 1 h | |
| 7 | La publication sur tag n'a jamais tourné (seul tag existant : `livrable-E1-v1`, antérieur au workflow) | C19.4 | nouvelle | **le tag `livrable-E1-v2` du 15/10 sera la première exécution réelle** : relever le run, vérifier l'image publiée, coller la sortie dans `evidence/C19/` | 30 min | |
| 8 | Aucun compte rendu daté de revue du lundi trouvé dans `ETAT.md`, `CONTINUITE.md`, `docs/PILOTAGE-AGILE.md` ni `evidence/C16/` (à confirmer avec Era, qui a pu les tenir sur le tableau) | C16.1 à C16.4 | #21 | tenir les revues du 05/10, 12/10 et 19/10, une entrée datée chacune (`evidence/C16/revues/`) ; dire dans le rapport que C16 couvre cinq semaines sur douze | 15 min par lundi | |
| 9 | Code non déployé sur le serveur Hetzner (gel avant le 15/10) ; la démonstration et la « pré-production accessible » (C15.4) en dépendent | C15.4, démonstration | nouvelle | déployer après le tag du 15/10, vérifier HTTPS, `/health`, les trois écrans | 2 h | |
| 10 | Seize indicateurs spécifiés, treize dans le briefing | C14, C17.4 | nouvelle | dire l'écart, sans le cacher, dans le rapport ; la décision d'en ajouter est celle d'Era (`evidence/C7/indicateurs-cites-dans-les-textes-2026-10-03.md`, §5) | 15 min | Era |

## 4. La structure du rapport, et d'où vient chaque morceau

Plan de sections repris du MASTER-GUIDE (son tableau « Adaptation à RITA-Agent » décrit React, Vite et Vercel : ce n'est pas la pile de
RITA, qui est du HTML, CSS et JavaScript sans build, FastAPI, Docker et Hetzner ; seul le découpage est repris).

| Section | Pages | Critères | Matière déjà dans le dépôt |
|---|---|---|---|
| 1. Analyser le besoin | 2 | C14 | MCD du rapport E1, `evidence/C14/` (user stories, wireframes, accessibilité RGAA), écrans 2 et 3 à ajouter (#24) |
| 2. Cadre technique | 3 | C15 | `evidence/C15/` (spécifications techniques, flux de données, pré-production Docker, avis « poursuivre ») |
| 3. Coordonner en agile | 1,5 | C16 | `docs/PILOTAGE-AGILE.md`, le tableau Kanban, les revues du lundi |
| 4. Développer | 4 | C17 | `frontend/`, `api/`, `evidence/C10`, `evidence/C12`, revue OWASP, mesure éco-conception, droits d'accès |
| 5. Automatiser les tests | 2 | C18 | `evidence/C18/`, `docs/CI-CD.md`, rapport E3 (suite de tests) |
| 6. Livraison continue | 2 | C19 | `evidence/C19/`, `docs/CI-CD.md`, `livraison.yml`, la première publication sur tag |
| 7. Démonstration et limites | 1 | tous | script de démonstration (§6), liste franche de ce qui n'est pas fait |
| 8. Matrice de preuves | 0,5 | tous | 36 lignes : critère, état, fichier |
| **Total** | **16** | | marge de 4 pages sous la limite de 20 |

Chevauchement avec E3 : l'intégration continue et la suite de tests figurent déjà dans le rapport E3. Chaque livrable est jugé seul : E4
reprend ce qu'il lui faut et renvoie à E3 pour le détail, il ne s'y réduit pas. Le gabarit de rendu est celui de E1 et E3
(`scripts/rendre_pdf.py`, Markdown vers HTML vers PDF par Chrome, nombre de pages compté, relecture visuelle). Rédaction : skill
`anthropic-skills:doc-coauthoring`, une section à la fois, validée par Era avant la suivante.

## 5. Les tâches, dans l'ordre

| T | Tâche | Entrée | Sortie, preuve |
|---|---|---|---|
| T1 | Recompter les 36 critères contre le dépôt d'aujourd'hui | skill `projet-rncp` | **fait le 03/10** : `docs/rapports/E4/recomptage-criteres-2026-10-03.md`, remplace celui du 26/09 |
| T2 | User stories et wireframes des écrans 2 et 3 (#24) | `evidence/C14/`, `frontend/` | **fait le 03/10** : `evidence/C14/preuve-specifications-ecrans-2-et-3.md`, un wireframe `.drawio`, `.svg` et `.png` par écran ; écrit après le code, dit en tête ; a fait trouver le défaut #73 et une erreur de référence RGAA |
| T3 | Mesurer l'éco-conception et l'accessibilité des trois pages (#25) | le front local | **fait le 03/10** : `evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md` (Lighthouse 13.5.0, EcoIndex officiel, clavier) ; le tableau **après** suivra la correction de la carte #74, après le 15/10 |
| T4 | Revue OWASP Top 10 écrite (#29) | le code, `tests/` | **fait le 03/10** : `evidence/C17/revue-owasp-top10-2025-2026-10-03.md`, édition 2025, dix entrées, dix constats S1 à S10 ; corrections après le 15/10 (carte #75) |
| T5 | Droits d'accès : défense écrite (#26) | `api/main.py`, `db/roles.sql` | **fait le 03/10** : `evidence/C17/preuve-droits-acces-2026-10-03.md` (choix, modèle de menace, matrice validée confrontée au code, coût, rotation, déclencheurs) ; écart E1 trouvé (API en rôle propriétaire, carte #76) |
| T6 | Revues du lundi : 05/10, 12/10, 19/10 | tableau Kanban | `evidence/C16/revues/<date>.md` ; **trame du 05/10 préparée le 03/10** (`evidence/C16/revues/2026-10-05-revue-S41.md`), revue à tenir par Era |
| T7 | Épingler `requirements.txt` (#23) | `requirements.txt` | suite et chaîne vertes, sortie collée |
| T8 | Première publication sur tag : relever le run du tag `livrable-E1-v2` (15/10) | `gh run list` | `evidence/C19/preuve-publication-sur-tag.md` |
| T9 | Déployer sur Hetzner, vérifier les trois écrans | serveur d'Era | `evidence/C15/` mis à jour ; captures des trois écrans en HTTPS |
| T10 | Rédiger les sections 1 à 8 | tout ce qui précède | `docs/rapports/E4/rapport-E4.md` |
| T11 | Rendu PDF, pages comptées, liens, Definition of Done | `scripts/rendre_pdf.py`, `scripts/verifier_liens.py`, `scripts/verifier_livrable.py` | PDF de 15 à 20 pages, zéro lien cassé |
| T12 | Pull request `develop` vers `main`, tag `livrable-E4-v1`, lien envoyé par Era | `docs/FILE-DE-VALIDATION.md` | tag posé, lien qui répond |

## 6. La démonstration (20 minutes d'oral, dont une démonstration en direct)

Parcours en quatre minutes, sur le serveur et non sur le poste : écran 1 (portefeuille), écran 2 (indicateurs, treize par valeur),
écran 3 (briefing d'une valeur, avec la clé saisie à l'écran, jamais écrite dans le front), puis la chaîne (une pull request verte, le
tag, l'image publiée). Trois risques, à traiter avant la répétition : (1) la latence du modèle, jusqu'à 10 à 11 secondes dans 1 appel
sur 20 chez Foundry (preuve C7) : prévoir de l'annoncer et un briefing déjà généré en secours ; (2) le réseau de la salle : une capture
vidéo du parcours complet, faite sur le serveur, comme solution de repli ; (3) la clé : elle se tape devant le jury, elle n'est jamais
dans un fichier du dépôt. La répétition de la démonstration compte dans les tâches T9 et T11, pas après.

## 7. Calendrier

| Période | Contenu | Remarque |
|---|---|---|
| **du 05/10 au 14/10** | T1 à T6 : documents et mesures, **aucun changement de code de l'application** | revues du lundi 05/10 et 12/10 ; en parallèle, relecture des PDF E1 et E3 par Era |
| **jeudi 15/10** | gel d'E1 v2 et d'E3 v1, pull request, tags | T8 se déclenche avec le tag |
| du 15/10 au 19/10 | T7, T9, sections 1 à 3 du rapport | déploiement du code sur le serveur après le tag |
| du 19/10 au 22/10 | sections 4 à 8, démonstration répétée | revue du lundi 19/10 |
| du 22/10 au 24/10 | T11, relecture d'Era, corrections | marge d'un jour avant le gel |
| **dimanche 25/10** | T12 : tag `livrable-E4-v1`, lien envoyé | le 25/10 tombe un dimanche : pull request prête le vendredi 23/10 |
| 29-30/10 | oral blanc E1 et E3 | pas de travail E4 cette semaine-là |
| 05/11 | cinq livrables rendus | E2 et E5 écrits entre le 26/10 et le 04/11 |

## 8. Décisions attendues d'Era

| # | Décision | Option recommandée | Alternative |
|---|---|---|---|
| D1 | Droits d'accès (#26) | **défendre le choix mono-utilisateur** par écrit, avec le modèle de menace : RITA est un outil personnel, une clé et un rôle PostgreSQL en lecture seule | ajouter un second niveau (lecture seule et administration) : une demi-journée de code et de tests, hors périmètre avant le gel |
| D2 | Outil de mesure éco-conception (#25) | **Lighthouse en local** (Chrome est installé, Node 24 présent) : il rend aussi un score d'accessibilité ; **demande ton accord** : `npx` télécharge le paquet depuis npm | EcoIndex en ligne (aucun téléchargement, une page à la fois, à la main) |
| D3 | Avancer la revue OWASP de la semaine 44 à maintenant (#29) | **oui** : le critère C17.8 l'exige dans E4 | la garder en S44 : E4 part avec un ⚠️ |
| D4 | Commencer T1 à T6 avant le gel du 15/10 | **oui** : ce sont des documents et des mesures, ils ne touchent pas à l'application ; sinon les dix jours après le gel portent à la fois la rédaction, le déploiement et la répétition | attendre le gel : plus sûr pour E1 et E3, serré pour E4 |
| D5 | Épingler `requirements.txt` (#23) | **après le tag du 15/10** : un changement de dépendances juste avant un gel est un risque inutile | avant : même travail, un risque de plus sur la chaîne |

## 9. Ce que ce plan ne promet pas

- **C16 ne couvrira que cinq semaines sur douze** : l'outillage date du 26/09, et ce qui n'a pas existé ne s'écrit pas après coup. Le rapport le dira.
- **Pas de second niveau d'accès** si D1 reste sur la défense : un critère restera ⚠️ plutôt que de coder dans la précipitation.
- **Pas de refonte de l'application** : les seules lignes de code autorisées avant le 25/10 sont l'épinglage des dépendances et des correctifs que T1 à T4 révéleraient, avec un test d'abord.
- **Le temps d'Era est le facteur limitant** : lecture d'E1 et E3, notation de C7, répétition de l'oral blanc, démonstration. Si l'une de ces charges glisse, c'est E4 qui perd sa marge, et la section 7 se réduit avant de couper une section du rapport.

## 📖 Glossaire

- **Critère** : phrase du référentiel que le jury coche ; 36 pour E4.
- **User story** : besoin décrit du point de vue de l'utilisateur, avec contexte, scénarios et critères d'acceptation.
- **Wireframe** : schéma d'écran sans habillage graphique, qui fixe la place des éléments.
- **RGAA** : référentiel général d'amélioration de l'accessibilité, standard français d'accessibilité numérique.
- **Kanban** : méthode agile à flux continu, avec un tableau de colonnes (à faire, en cours, fait) et des limites de travail en cours.
- **OWASP Top 10** : liste de référence des dix risques de sécurité les plus courants des applications web.
- **EcoIndex, Lighthouse** : outils qui notent une page web, l'un sur son impact environnemental (A à G), l'autre sur la performance, l'accessibilité et les bonnes pratiques.
- **Ruleset** : règle GitHub qui impose, par exemple, une pull request et des tests verts avant toute fusion sur `main`.
- **Tag** : étiquette posée sur un commit précis ; `livrable-E4-v1` marquera l'état exact du rendu.
- **Pré-production** : environnement proche de la production où l'on vérifie que l'application démarre et répond avant de la livrer.
- **Packaging** : mise en forme livrable de l'application, ici la construction de l'image Docker.

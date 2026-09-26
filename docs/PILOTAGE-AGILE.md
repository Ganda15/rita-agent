# Pilotage du projet RITA : méthode Kanban

> Mis en place le 26/09/2026. Compétence visée : **C16**, coordonner la réalisation technique
> dans une conduite agile de projet. Tableau : **RITA - Pilotage Kanban (livrables E2-E5)**,
> https://github.com/users/Ganda15/projects/4 (privé ; accès : Era, formateur en lecture).
> Sans connexion ou sans accès, GitHub répond 404 : c'est le comportement normal d'un projet
> privé. Le jury recevra un accès en lecture au moment de l'évaluation.

## 1. Pourquoi Kanban

RITA a un seul développeur. Scrum suppose une équipe, des rôles distincts (Scrum Master,
équipe de développement) et des cérémonies de groupe (mêlée quotidienne, rétrospective) qui
n'ont pas de sens pour une personne seule. Kanban garde ce qui sert ici : un flux de travail
visible, une limite au travail en cours, une revue régulière.

La cadence existe déjà : le plan `docs/PLAN-12-SEMAINES.md` (16/08) découpe le projet en
semaines S34 à S45, chacune avec un objectif. **Un cycle Kanban = une semaine du plan.**

## 2. Les rôles

| Rôle | Qui | Responsabilité |
|---|---|---|
| Porteur du produit et développeur | Era | ordonne le backlog, décide, développe, rédige les livrables |
| Partie prenante, relecteur | le formateur (`bybysker`) | lit le tableau et le dépôt, valide les livrables envoyés |
| Revue automatique des pull requests | workflow `revue-pr.yml` (Claude Code), Codex | commente chaque pull request avant fusion |
| Assistant de développement | Claude Code | propose et écrit sur demande d'Era ; ne décide pas |

## 3. Les outils

- **Tableau** : GitHub Projects, lié au dépôt `Ganda15/rita-agent`.
- **Backlog** : les issues du dépôt, une par élément du plan (#21 à #44 à la création).
  Étiquettes : `E2`, `E3`, `E4`, `E5` (livrable), `veille-C6`, `decision-era` (attend une
  décision d'Era avant de commencer).
- **Champs du tableau** : `Status` (les 4 colonnes), `Semaine` (S39 à S45, « Chaque lundi »),
  `Critères` (compétences et critères RNCP visés).
- **Pull requests** : chaque changement de code passe par une pull request qui cite son issue
  (`Closes #N`), ce qui relie la carte, le code et la revue.

## 4. Les colonnes et leurs règles

| Colonne | Règle d'entrée |
|---|---|
| **Backlog** | travail identifié et rangé à sa semaine du plan |
| **Cette semaine** | choisi à la revue du lundi, d'après l'objectif de la semaine du plan |
| **En cours** | en train d'être fait ; **2 cartes au plus** à la fois |
| **Fait** | terminé **et prouvé** : test vert, commit, ou preuve dans `evidence/` ; « écrit » ne suffit pas |

Pour le code, « prouvé » veut dire que `scripts/verifier_livrable.py` passe (la définition de
« fini » du projet, 5 contrôles). Pour un document : relu, liens vérifiés par
`scripts/verifier_liens.py`.

## 5. Le cycle et les rituels

| Rituel | Quand | Durée | Contenu | Trace |
|---|---|---|---|---|
| **Revue hebdomadaire** | lundi, après la note de veille C6 (créneau 09h-10h du plan) | 15 min | 1. cartes passées à Fait la semaine d'avant, avec leur preuve ; 2. cartes qui ont glissé, et pourquoi ; 3. choix des cartes de la semaine ; 4. décisions à prendre | compte rendu daté en tête d'`ETAT.md`, commité le jour même |
| **Revue de pull request** | à chaque pull request | variable | revue automatique, puis lecture par Era avant fusion | commentaires sur la pull request |
| **Point formateur** | à chaque livrable gelé | variable | envoi du livrable, retour du formateur | `docs/FILE-DE-VALIDATION.md` |

**Mesure suivie à chaque revue** : le nombre de cartes passées à Fait dans la semaine (le
débit). Kanban ne se pilote pas au burndown, qui suppose un engagement de sprint.

## 6. Comment les parties prenantes y accèdent

- Le tableau : lien en tête de ce fichier ; le formateur y a un accès en lecture depuis le
  26/09/2026.
- La méthode : ce fichier, dans le dépôt, que le formateur lit déjà.
- Les revues : le compte rendu en tête d'`ETAT.md`, versionné avec le code.

## 7. Limites, dites franchement

- Le tableau et les revues existent **depuis le 26/09/2026**, à cinq semaines et cinq jours
  de l'échéance du 05/11. Avant, le projet était piloté par le plan des 12 semaines, `ETAT.md`,
  le journal de bord et 20 pull requests : des traces réelles, mais pas un outil agile. Aucune
  trace n'est reconstituée après coup.
- Un pilotage à une personne ne montre ni rétrospective d'équipe ni répartition des tâches.
- La tenue des revues se prouvera dans la durée : cinq revues sont possibles d'ici au 05/11.

## 📖 Glossaire

- **Kanban** : méthode agile à flux continu, pilotée par un tableau de colonnes et une limite
  de travail en cours.
- **Scrum** : méthode agile par sprints de durée fixe, avec des rôles et des cérémonies d'équipe.
- **Backlog** : liste ordonnée du travail restant.
- **Limite de travail en cours (WIP)** : nombre maximal de cartes « En cours » en même temps.
- **Débit** : nombre de cartes terminées par période ; la mesure naturelle de Kanban.
- **Burndown** : courbe du travail restant dans un sprint ; propre à Scrum.
- **Issue** : fiche de travail d'un dépôt GitHub.
- **Pull request** : demande de fusion d'une branche, relue avant d'être acceptée.

# Preuve C16 : mise en place du pilotage Kanban (26/09/2026)

> **C16** : *« Coordonner la réalisation technique d'une application d'intelligence
> artificielle en s'intégrant dans une conduite agile de projet et un contexte MLOps […] »*
> Méthode : [`../../docs/PILOTAGE-AGILE.md`](../../docs/PILOTAGE-AGILE.md).

## 1. Point de départ, mesuré

Vérification des critères E4 du 26/09 : les 4 critères de C16 à zéro. `gh issue list` sur le
dépôt : 0 issue. Aucun tableau lié au dépôt parmi les 3 projets existants du compte. C16
n'apparaissait dans aucune semaine de `docs/PLAN-12-SEMAINES.md`.

## 2. Ce qui a été mis en place le 26/09

| Élément | État vérifié | Commande de vérification |
|---|---|---|
| Tableau « RITA - Pilotage Kanban (livrables E2-E5) », projet n° 4, privé | ✅ lié au dépôt `rita-agent` | `gh project view 4 --owner Ganda15` |
| 4 colonnes : Backlog, Cette semaine, En cours, Fait | ✅ | `gh project field-list 4 --owner Ganda15` |
| Champs `Semaine` (S39 à S45, « Chaque lundi ») et `Critères` | ✅ | même commande |
| Backlog : 24 issues (#21 à #44), chacune tirée du plan, d'`ETAT.md` ou de la vérification E4 | ✅ 16 Backlog · 7 Cette semaine · 1 En cours | `gh project item-list 4 --owner Ganda15` |
| Étiquettes `E2` à `E5`, `veille-C6`, `decision-era` | ✅ | `gh label list -R Ganda15/rita-agent` |
| Accès du formateur (`bybysker`) au tableau, en lecture | ✅ | mutation GraphQL `updateProjectV2Collaborators`, réponse : `bybysker` |
| Méthode écrite : rôles, colonnes, limite de travail en cours, rituels, accès | ✅ | `docs/PILOTAGE-AGILE.md` |

## 3. Les 4 critères après la mise en place

| Critère officiel | État | Pourquoi |
|---|---|---|
| Cycles, étapes, rôles, rituels et outils de la méthode respectés **tout au long du projet** | ⚠️ | la méthode est écrite et l'outil existe ; la première revue a lieu le lundi 28/09. « Tout au long du projet » ne vaut qu'à partir du 26/09 |
| Outils de pilotage disponibles (kanban, backlog…) | ✅ | tableau et backlog en place, vérifiés ci-dessus |
| Objectifs et modalités des rituels partagés à toutes les parties prenantes | ✅ | `docs/PILOTAGE-AGILE.md` §5, dans le dépôt lu par le formateur |
| Éléments de pilotage accessibles à toutes les parties tout au long du projet | ⚠️ | accès du formateur accordé le 26/09 ; vrai à partir de cette date seulement |

## 4. Ce qui reste à prouver

- La tenue des revues hebdomadaires : un compte rendu daté par lundi, de S40 à S45.
- Le débit relevé à chaque revue (cartes passées à Fait).
- L'utilisation réelle du lien issue, pull request, carte (`Closes #N`).

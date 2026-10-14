# Preuve C19 et C13 : la branche `main` est protégée côté serveur (03/10/2026)

> Jusqu'au 03/10, la protection de branche était **indisponible** sur ce dépôt privé (offre gratuite de GitHub,
> réponse de l'API le 03/10 au matin : « Upgrade to GitHub Pro or make this repository public »). La règle
> « `main` ne bouge que par une pull request relue » ne tenait que par le hook local `.githooks/pre-push`, actif
> seulement sur un poste où `git config core.hooksPath .githooks` a été fait.
> Le 03/10 à midi, Era a activé GitHub Pro. La règle est désormais appliquée par GitHub lui-même.

## Ce qui a été posé (ruleset `24414639`, par l'API, le 03/10/2026)

| Règle | Effet |
|---|---|
| `deletion` | la branche `main` ne peut pas être supprimée |
| `non_fast_forward` | aucun push forcé : l'historique de `main` ne se réécrit pas |
| `pull_request` | aucun commit n'arrive sur `main` autrement que par une pull request (0 approbation exigée : un seul développeur) |
| `required_status_checks` : `pytest`, `evals` | la pull request ne se fusionne que si les deux jobs de `test.yml` sont verts |
| `bypass_actors` : aucun | personne, pas même l'administrateur, ne contourne la règle |

Relecture par l'API après création :

```
24414639 | main protegee : PR relue, tests et evals verts, ni suppression ni force-push | active | branch
regles : deletion, non_fast_forward, pull_request, required_status_checks | checks : pytest, evals | bypass : 0
regles effectives sur main : deletion, non_fast_forward, pull_request, required_status_checks
```

Commande de vérification, rejouable :

```powershell
gh api repos/Ganda15/rita-agent/rules/branches/main
```

## Les tags de livrable sont figés aussi (ruleset `24415612`, 03/10/2026, soir)

Un livrable est un tag `livrable-E<n>-v<k>` ; c'est le lien que le formateur ouvre. Un tag qu'on peut déplacer ou
supprimer n'est pas une preuve. Second ruleset, cible `refs/tags/livrable-*` : `deletion`, `non_fast_forward`,
`update` ; aucun contournement. Relu par l'API :

```
24415612 | tag | tags livrable-* figes : ni suppression ni deplacement
regles = deletion, non_fast_forward, update | motif = refs/tags/livrable-* | bypass = 0
```

Un tag `livrable-E1-v2` se **pose** librement (nouveau nom) ; `livrable-E1-v1` ne bougera plus.

## Ce que ça change pour les critères

- **C19, critère 4** (« l'étape de livraison est intégrée et exécutée une fois les étapes de packaging validées ») :
  la vérification du 26/09 le marquait partiel, « protection de branche non disponible ». La condition est maintenant
  tenue par le serveur : une fusion sans `pytest` et `evals` verts est refusée.
- **C13** : les déclencheurs et la porte de qualité de la chaîne ne dépendent plus d'un réglage local.

## Ce qui n'est pas prouvé ici, dit franchement

- Aucun push direct n'a été tenté pour voir GitHub le refuser : le hook local l'aurait refusé avant, et on ne
  contourne pas un hook pour une démonstration. La preuve est la liste des règles effectives, relue par l'API.
- La capture d'écran de **Settings → Rules → Rulesets** est à faire par Era et à ranger ici :
  `capture-2026-10-03-ruleset-main.png`. En attendant, la réponse complète de l'API pour les deux rulesets est dans
  `rulesets-2026-10-03.json` (même dossier) : c'est une preuve lisible par machine, la capture est la preuve lisible par un jury.
- La revue `Revue PR` (Claude) et le job `construire-et-publier` ne sont pas exigés : la première est
  non déterministe (elle publie parfois rien), le second ne vaut que sur un tag.

## 📖 Glossaire

- **Ruleset** : l'outil actuel de GitHub pour poser des règles sur des branches ; remplace la « protection de branche » classique.
- **Push forcé** : réécrire l'historique distant ; interdit sur `main`.
- **Status check** : un job de la CI dont le résultat conditionne la fusion.


## Complément du 03/10/2026 au soir : la revue automatisée devient un check requis

Un contrôle extérieur du dépôt a relevé que le ruleset `main protegee` exigeait `pytest` et `evals` verts, mais pas
le job `revue` du workflow `Revue PR`. La règle écrite dans `AGENTS.md` (« `main` ne bouge que par une pull request
relue ») n'était donc tenue que par l'habitude, pas par le serveur. Corrigé par l'API (`PUT /repos/.../rulesets/24414639`)
en ajoutant le contexte `revue` à la liste des checks requis ; relu depuis GitHub :

```
["pytest","evals","revue"]
```

Vérifié avant d'ajouter : le job `revue` était vert sur les deux dernières PR (58 et 72), donc la règle n'a bloqué
aucune fusion en cours. Le ruleset complet après modification : `ruleset-main-2026-10-03-soir.json` ; la liste des deux
rulesets actifs : `rulesets-liste-2026-10-03.txt`. Aucune protection « classique » n'existe sur `main` (l'API répond
`Branch not protected`) : les rulesets sont la seule source, et c'est voulu, une règle à un seul endroit.

Risque accepté, dit franchement : si le workflow de revue tombe en panne (jeton expiré, action indisponible), aucune PR
ne peut plus être fusionnée, puisque personne n'a de droit de contournement. La sortie est alors d'éditer le ruleset
dans *Settings → Rules*, pas de pousser sur `main`.

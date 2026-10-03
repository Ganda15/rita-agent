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

## Ce que ça change pour les critères

- **C19, critère 4** (« l'étape de livraison est intégrée et exécutée une fois les étapes de packaging validées ») :
  la vérification du 26/09 le marquait partiel, « protection de branche non disponible ». La condition est maintenant
  tenue par le serveur : une fusion sans `pytest` et `evals` verts est refusée.
- **C13** : les déclencheurs et la porte de qualité de la chaîne ne dépendent plus d'un réglage local.

## Ce qui n'est pas prouvé ici, dit franchement

- Aucun push direct n'a été tenté pour voir GitHub le refuser : le hook local l'aurait refusé avant, et on ne
  contourne pas un hook pour une démonstration. La preuve est la liste des règles effectives, relue par l'API.
- La capture d'écran de **Settings → Rules → Rulesets** est à faire par Era et à ranger ici :
  `capture-2026-10-03-ruleset-main.png`.
- La revue `Revue PR` (Claude) et le job `construire-et-publier` ne sont pas exigés : la première est
  non déterministe (elle publie parfois rien), le second ne vaut que sur un tag.

## 📖 Glossaire

- **Ruleset** : l'outil actuel de GitHub pour poser des règles sur des branches ; remplace la « protection de branche » classique.
- **Push forcé** : réécrire l'historique distant ; interdit sur `main`.
- **Status check** : un job de la CI dont le résultat conditionne la fusion.

# Preuve C13 : la chaîne de livraison continue a tourné pour de vrai (03/10/2026)

> Livrable E3. Jusqu'ici la chaîne n'était prouvée que par ses fichiers (`.github/workflows/`) et par les tests
> qui les lisent comme un contrat. Cette fiche range les exécutions réelles d'une journée, lues par
> `gh run list` et `gh pr list` le 03/10/2026, et l'état de la protection de `main` lu par l'API GitHub.

## 1. Les cinq workflows, et ce qu'ils ont fait le 03/10

| Heure (UTC) | Workflow | Déclencheur | Branche | Résultat | Identifiant |
|---|---|---|---|---|---|
| 11:45 | Tests, Livraison, Revue PR | `pull_request` (PR 58) | develop → main | succès ×3 | 37120672226, 37120672227, 37120672220 |
| 11:49 | Tests, Livraison | `push` après fusion de la PR 58 | main | succès ×2 | 37120870540, 37120870558 |
| 11:50 | Alerte Langfuse vers issue incident | `workflow_dispatch` (bouton manuel) | main | succès ; issue #71 créée avec le label `incident`, puis fermée comme démonstration | 37120911852 |
| 12:15 | Revue PR | `pull_request` (PR 72) | develop → main | annulé par le groupe de concurrence (nouveau commit poussé 1 min après) | 37122291147 |
| 12:16 | Tests, Livraison, Revue PR | `pull_request` (PR 72) | develop → main | succès ×3 | 37122314876, 37122314776, 37122314910 |
| 12:21 | Tests, Livraison | `push` après fusion de la PR 72 | main | succès ×2 | 37122588436, 37122588446 |

Lecture : chaque pull request a déclenché les trois workflows, chaque fusion les deux de la branche cible. Le
workflow d'alerte a été exécuté une fois à la main : c'est la première fois que la chaîne d'alerte produit une
issue réelle (#71), ce que la version 0.1 du rapport E3 signalait comme non fait.

Commande : `gh run list --limit 25 --json name,event,status,conclusion,headBranch,createdAt,databaseId`.

## 2. Les pull requests fusionnées par la chaîne

| PR | Objet | Fusion | Checks requis au moment de la fusion |
|---|---|---|---|
| 58 | 44 commits : C11 réel, chapitre « Données », #59 #60 #61 #62 #64 #65 | `d1cec3b`, 03/10 11:49 | `pytest`, `evals` |
| 72 | clôture des positions (plan 66), cas D07 | `43025f9`, 03/10 12:21 | `pytest`, `evals`, puis `revue` ajouté avant la fusion |

24 pull requests fusionnées au total sur le dépôt (`gh pr list --state merged`). Deux remarques de la revue
automatisée sur la PR 58 (une P1 : une panne de Langfuse pouvait faire tomber un briefing ; une P2 : un 500 inattendu
partait sans `X-Request-ID`) ont été corrigées test d'abord avant la fusion.

## 3. `main` ne bouge plus que par la chaîne (GitHub Pro, 03/10)

```
24414639 main protegee : PR relue, tests et evals verts, ni suppression ni force-push   active
24415612 tags livrable-* figes : ni suppression ni deplacement                           active
```

Checks requis par le ruleset, relus par l'API après la dernière modification : `["pytest","evals","revue"]`.
Aucun acteur de contournement. Détail et JSON : `../C19/preuve-protection-main-2026-10-03.md`.

## 4. Ce que cette fiche ne prouve pas

- La branche « publier l'image sur un tag `livrable-*` » de `livraison.yml` n'a toujours **jamais été exécutée** :
  le seul tag du dépôt (`livrable-E1-v1`) précède le fichier. Le tag `livrable-E1-v2` du 15/10 sera son premier passage.
- Aucun déploiement automatique sur le serveur : la copie Hetzner reste à `1cefdae` (20/08), déploiement manuel après le gel.
- Aucune procédure de retour arrière outillée.

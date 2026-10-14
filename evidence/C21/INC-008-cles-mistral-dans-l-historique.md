# INC-008 : deux vraies clés Mistral dans l'historique de `.env.example`

> Trouvé le 14/10/2026 par la **première analyse de tout l'historique Git** avec gitleaks (sprint 2, tâche 3), pas
> par hasard : le contrôle venait d'être construit pour le critère 5 de la grille, « les secrets ne sont pas dans le
> dépôt ». Aucune valeur n'est recopiée dans cette fiche.

| | |
|---|---|
| **Détecté le** | 14/10/2026, en fin de matinée, au premier passage de gitleaks (v8.18.4, puis v8.30.1) sur l'historique |
| **Sévérité** | **P2** : deux valeurs de `MISTRAL_API_KEY` ayant la forme de vraies clés (45 caractères, forte entropie, aucun mot d'exemple), visibles par quiconque lit l'historique du dépôt privé ; aucune ne servait à la production (`LLM_ORDRE=foundry`) |
| **Où** | `.env.example`, commits `5fae28e` (10/10, 16:54, l. 55) et `8587a21` (10/10, 17:07, l. 53), branche `mistral-ue` seulement, sur le poste et sur GitHub ; absentes de `develop`, `main` et des branches de sprint |
| **Durée d'exposition** | du 10/10 à 16:54 jusqu'à la révocation confirmée le 14/10/2026 |
| **Correctif** | révocation des deux clés chez Mistral (Era) ; nouvelle clé seulement dans le `.env` local, ignoré par Git ; exceptions documentées dans `.gitleaksignore` ; contrôle `secrets` dans la chaîne (sprint 2, tâche 3, partie 2) |
| **Historique** | **gardé**, sans réécriture : une clé révoquée ne donne plus accès à rien, et réécrire l'historique ne retirerait pas les copies déjà faites |

## 1. Ce qu'on a vu

gitleaks a signalé 7 alertes `generic-api-key` sur 389 commits. Cinq visaient des fausses clés de test (`cle-de-test-…`,
`cle-de-verification-…`, `cle-de-test-smoke-ui-…`, `cle-de-reconstruction-…`, `remplacer-par-…`). Les deux autres
visaient `MISTRAL_API_KEY` dans `.env.example`. Le tri s'est fait sans afficher aucune valeur : nom de la variable,
longueur, entropie, présence d'un mot d'exemple.

## 2. Cause

Le modèle `.env.example` a reçu une vraie clé au lieu d'une valeur d'exemple. Le message du commit `8587a21` annonce
« MISTRAL_API_KEY redevient votre_cle_ici (cle reelle revoquee chez Mistral) », mais le contenu de ce commit porte une
**autre** valeur de 45 caractères. Seul un commit suivant de `mistral-ue` remet `votre_cle_ici`. Aucun contrôle ne
lisait alors l'historique.

## 3. Correction

1. Era révoque les clés chez Mistral et en crée une nouvelle, rangée seulement dans son `.env` local (vérifié :
   `git check-ignore -v .env` et `git status --short`).
2. Les deux empreintes gitleaks (commit, fichier, règle, ligne) vont dans `.gitleaksignore`, avec la mention
   « secrets historiques révoqués » et le renvoi à cette fiche. Ce ne sont pas des faux positifs.
3. Les cinq fausses clés vont dans `.gitleaks.toml`, chacune écrite en entier et ancrée.
4. Le travail `secrets` de `.github/workflows/livraison.yml` analyse tout l'historique à chaque passage.

## 4. Vérification et non-régression

- gitleaks v8.30.1 avec la configuration, sur les branches, les branches distantes et les tags : « 391 commits
  scanned », « no leaks found », code 0.
- Sur un dépôt jetable, une clé tirée au hasard est toujours signalée (code 1), et la fausse clé de test à côté ne
  l'est pas.
- `tests/test_gitleaks_config.py` : les exceptions ne visent que les cinq fausses clés, aucune ne couvre 50 clés tirées
  au hasard, et `.gitleaksignore` ne contient que les deux empreintes de cette fiche.

## 5. Ce qui n'est pas fait, et la leçon

- **La date exacte** de révocation de la première clé (peut-être le 10/10, selon le message de commit) n'est pas
  prouvée ; la révocation des deux est confirmée par Era le 14/10.
- **L'usage des clés pendant l'exposition** n'a pas été vérifié dans la console de Mistral.
- **La leçon** : un message de commit n'est pas une preuve, et un contrôle qui ne lit que le dernier état du dépôt ne
  voit pas ce que l'historique garde.

## 📖 Glossaire

- **gitleaks** : outil qui cherche des secrets dans le code et dans tout l'historique Git.
- **Empreinte** : l'identifiant d'une alerte (commit, fichier, règle, ligne), qui permet de la taire sans écrire la valeur.
- **Révoquer** : désactiver une clé chez le fournisseur.
- **Entropie** : mesure du hasard d'une chaîne ; une vraie clé est autour de 5 bits par caractère.

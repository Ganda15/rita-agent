---
name: livrer
description: La chaîne de livraison de RITA, de la Definition of Done au lien du tag envoyé au formateur — PR develop → main relue, fusion, tag sur main, liens vérifiés. Déclencher pour « on livre », « pose le tag », « envoie au formateur », « ouvre la PR », « c'est prêt à rendre », ou avant tout envoi d'un livrable E1–E5.
---

# Livrer — un livrable est un tag sur `main`, jamais une branche

## Pourquoi cette chaîne
`main` avance ; qui ouvre le dépôt voit le projet d'aujourd'hui, pas le livrable. Le lien envoyé est
**toujours** `https://github.com/Ganda15/rita-agent/tree/livrable-E<n>-v<k>`. Et `main` ne bouge que par une
pull request relue : le push direct est refusé par `.githooks/pre-push` (activer une fois par clone :
`git config core.hooksPath .githooks`).

## Les 7 pas, dans l'ordre, un bloc par commande
1. **Definition of Done verte, en local** :
   `C:/Python314/python.exe scripts/verifier_livrable.py livrable-E<n>-v<k>`
   Cinq lignes ✅ exigées : tests + couverture, portes d'évaluation, liens internes, tag cité dans `ETAT.md`
   **et** `CHANGELOG.md`, arbre git propre. Une ❌ = on s'arrête là.
2. **Pousser `develop`** : `git push origin develop`.
3. **Ouvrir la PR** : `gh pr create --base main --head develop --title "Livraison E<n> : ..." --body "..."`
4. **Lire les revues** : Codex commente en quelques minutes ; la revue Claude (`revue-pr.yml`) parfois s'arrête
   trop tôt (comportement du plugin, nondéterministe) — `gh run rerun <id>` sur le run « Revue PR » si elle n'a rien
   publié. Chaque commentaire vrai = un correctif + un test, poussés sur `develop` (la PR se met à jour).
5. **Fusionner** quand les 4 checks sont verts : `gh pr merge <n> --merge`.
6. **Taguer sur `main`** : `git fetch origin` · `git tag livrable-E<n>-v<k> origin/main` · `git push origin livrable-E<n>-v<k>`.
   `livraison.yml` rejoue la DoD **puis** publie l'image `ghcr.io/ganda15/rita-api:livrable-E<n>-v<k>`.
7. **Vérifier avant d'envoyer** : les commandes de `docs/FILE-DE-VALIDATION.md` (le tag existe sur GitHub, le
   destinataire est collaborateur, zéro lien cassé), puis le gabarit de message du même fichier.

## Après l'envoi
- `docs/FILE-DE-VALIDATION.md` : nouvelle entrée dans « La file » (date, ce qui est envoyé, à qui).
- `CHANGELOG.md` : une entrée « livrable envoyé » (append-only, en haut).
- `ETAT.md` : prochaine action en tête.
- Journal Obsidian si une étape est terminée.

## Ce qu'on ne fait jamais
- Envoyer le lien du dépôt ou d'une branche.
- Poser un tag sur `develop`, ou sur un commit dont la DoD n'est pas verte.
- Baisser un seuil pour faire passer la DoD : c'est une décision d'Era, consignée dans `CONTINUITE.md`.

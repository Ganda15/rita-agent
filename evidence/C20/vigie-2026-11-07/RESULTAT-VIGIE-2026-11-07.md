# Vigie C20.5 : secret corrige et passage verifie

Verification effectuee le 07/11/2026. Heures UTC ; ajouter une heure pour Paris.

## Constat initial

- `RITA_API_KEY_VIGIE` existait depuis 20:19:16 UTC et n'avait pas ete mis a jour.
- Le workflow 42411132337 echouait : `/sante` HTTP 403, sortie 2.
- La cle du fichier local habituel a aussi ete refusee lors d'un unique essai. Elle n'a pas ete reutilisee pour la mise a jour.

## Correction autorisee par Era

- Lecture ciblee de la seule cle RITA du conteneur API actif, via l'acces SSH existant.
- Verification de cette cle contre l'URL de production : `/sante` HTTP 200 ; `/health` HTTP 200.
- Version annoncee par `/health` : `6f428d61511019d7b6013fb007e290c133d48c2e`.
- Mise a jour de `RITA_API_KEY_VIGIE` par l'entree standard de l'outil GitHub, sans affichage ni enregistrement de la valeur.
- Horodatage GitHub apres enregistrement : **20:33:07 UTC**, soit **21:33:07 a Paris**.
- La cle de l'application sur le serveur n'a pas ete changee. Aucun code ni fichier du depot n'a ete modifie.

## Verification du passage

- Execution : https://github.com/Ganda15/rita-agent/actions/runs/42411132337
- Tentative : **2**, evenement `workflow_dispatch` (relance manuelle).
- Conclusion GitHub : **success**, terminee a 20:33:47 UTC.
- Job `passage` : 128520793770, duree 20 secondes.
- Ligne du journal a 20:33:43 UTC : `vigie : passage termine, code 0` (accents omis ici).

Ce passage prouve la disparition du refus 403 et le fonctionnement de la vigie avec le secret corrige. Le code 0 signifie qu'aucun verdict `probleme` n'a ete releve ; il ne garantit pas l'absence de verdicts `attention` ou `inconnu`.

## Pour achever la preuve C20.5

Verifier separement le prochain passage avec evenement `schedule`, puis rapprocher la preuve existante d'alerte et de retour a la normale. Une relance manuelle reussie ne constitue pas a elle seule une demonstration de toute la chaine d'alerte.

Les metadonnees avant/apres et les statuts HTTP sont conserves dans `verification-secret.json`. Aucun fichier de ce dossier ne contient la valeur de la cle.

## Complement observe le meme soir

L'essai du signal `service` sur copie a ensuite reussi : issue #230 ouverte puis fermee par la vigie. Voir `RESULTAT-ESSAI-COPIE-2026-11-07.md` pour le perimetre, les heures et les limites. L'execution planifiee de production reste a verifier.

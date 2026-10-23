# Sprint 5 : la mise en production (23/10/2026, livraison N16)

Décision d'Era le 23/10 au soir : le sprint 5 passe en production. Le chemin habituel du dépôt : la branche
`sprint-5-vigie-demo` par une PR vers `develop`, puis `develop` vers `main` ; chaque fusion dans `main` déclenche la
livraison automatique. Les fusions ont été faites par Era. Heures de Paris.

## 1. Les deux PR

| PR | Sens | Contrôles | Fusion |
|---|---|---|---|
| [#133](https://github.com/Ganda15/rita-agent/pull/133) | `sprint-5-vigie-demo` vers `develop` | lint, secrets, pytest, evals, construire-et-publier : verts (après deux corrections, § 3) | 17:51 |
| [#134](https://github.com/Ganda15/rita-agent/pull/134) | `develop` vers `main` | les six contrôles exigés par la règle de `main` (lint, secrets, pytest, evals, revue, construire-et-publier) : verts | 18:00:36, commit `845e3b36fe075ba797d59d1d2b4e958aa2d2c7ea` |

## 2. La livraison N16

Passage GitHub n° 39983152061 (`push` sur `main`), conclusion `success`, de 18:00:40 à 18:12:40.

| Travail | Durée | Résultat |
|---|---|---|
| lint | 10 s | succès |
| secrets (gitleaks, tout l'historique) | 54 s | succès |
| construire-et-publier (image, tests, Definition of Done, publication) | 6 min 25 | succès |
| attendre-creneau | 8 s | hors du créneau du matin |
| deployer (pré-test, bascule, vérification de `/health` sur le serveur) | 4 min 22 | succès |

## 3. Les deux corrections demandées par la chaîne Linux

La branche n'était jamais passée par la chaîne avant ce soir.

- **Contrôle « secrets »** : gitleaks prenait l'étiquette d'une image Docker de la copie, dans le journal brut des
  preuves du 22/10, pour une clé (règle `generic-api-key`). Reproduit en local avec la même version de gitleaks.
  Corrigé par une exception qui vise ce seul commit et ce seul fichier (`.gitleaks.toml`, condition AND), vérifiée par
  un test ; gitleaks sur tout l'historique : aucune fuite.
- **Contrôle « pytest »** : deux tests attendaient l'heure de Paris écrite en dur, alors que la machine de la chaîne est
  en UTC ; le code dit l'heure dans le fuseau du poste. Les tests calculent désormais l'heure attendue comme le code.

## 4. La production après N16 (vérifié sans la clé, en lecture seule)

| Vérification | Avant (N15, 17:2x) | Après (N16, 18:13) |
|---|---|---|
| `GET /health` | `status ok`, commit `3c35398db5fd` | `status ok`, commit `845e3b36fe07`, construit à 18:04:26 |
| `GET /tableau-de-bord.html` | 404 | 200, la page « Les signaux » |
| `GET /sante` sans clé | 404 (la route n'existait pas) | 403 : la route existe et exige la clé |

La clé de l'API de production ne vit que dans le `.env` du serveur : les clés du poste sont refusées (403). La lecture
de `/sante` avec la clé, et la vigie pointée sur le serveur, se font par Era, qui tape la clé lui-même.

## 5. Ce qui ne change pas en production

Aucune migration de base ; aucun secret ajouté au serveur ; les exercices de panne restent coupés (sans clé
d'exercice, leurs routes répondent 503). Les compteurs vivent en mémoire : ils repartent de zéro à chaque livraison.

## 6. L'incident de la soirée : GitHub Actions bloqué par le budget (18:49 à 19:10)

| Constat | Mesure |
|---|---|
| Contrôles de la PR #136 « en échec » en 2 secondes, 0 étape exécutée | annotation de chaque contrôle : « The job was not started because recent account payments have failed or your spending limit needs to be increased » |
| Cause | dépôt privé (`gh repo view` : `PRIVATE`) ; quota gratuit d'octobre épuisé entre 18:23 (dernier passage réussi) et 18:49 ; budget Actions du compte à 0 $ |
| Correction (Era, sur le site GitHub) | budget Actions porté à 5 $, avec arrêt au plafond ; prix officiel : 0,006 $ la minute en Linux 2 cœurs |
| Reprise | 19:10, les travaux s'exécutent de nouveau |
| Piège | les passages refusés du `push` sur `develop` (même commit) gardaient leurs échecs : la fusion restait bloquée malgré les six contrôles verts de la PR ; relancés, ils passent ; la PR devient fusionnable à 19:30 |

Avant la reprise, la Definition of Done a été lancée sur le poste (`scripts\verifier_livrable.py livrable-sprint-5-v1`,
commit `8fdcb3c`, même contenu que `develop`) : 1685 passés, 24 ignorés, 2 échecs attendus ; portes d'évaluation
16 passées ; aucun lien cassé ; tag cité ; arbre propre ; verdict « livrable ».

## 7. La livraison N17 et le tag

| Étape | Résultat |
|---|---|
| PR #136 (`develop` vers `main`) | fusionnée par Era à 19:33:14, commit `d215617f7cffa7a9817da28f2b2684dc7c63f7cd` |
| Livraison N17, passage 39995996403 | lint, secrets, construire-et-publier, attendre-creneau, deployer : succès (19:33:10 à 19:42:55) |
| Production à 19:43:21 | `/health` : `status ok`, commit `d215617f7cff...`, construit à 17:36:58 UTC ; `/tableau-de-bord.html` 200 ; `/sante` sans clé 403 |
| Tag `livrable-sprint-5-v1` | posé par Era sur le SHA complet, reçu par GitHub à 19:45:28 |
| Passage du tag 39997640785 | lint, secrets, construire-et-publier : succès ; Definition of Done en CI : « VERDICT : ✅ livrable » ; image `ghcr.io/ganda15/rita-api:livrable-sprint-5-v1` (révision `d215617`) |
| Liens des quatre PDF du tag | 46 liens : les 37 qui visent le tag pointent sur un fichier présent dans le tag ; 5 liens publics à 200 ; issues #127, #128 et PR #133, #134 existantes |

# Preuves du sprint 3 : les données et l'ancrage

Preuves versionnées du sprint 3 (15 au 19/10/2026), rangées par critère de la grille de l'atelier 3 (spec
`docs/sprint-3/SPEC.md`, § 9). Les fichiers bruts du serveur (manifestes, rapports de rejeu, journal des opérations)
ont été copiés par `scp` sans modification. Les journaux de chaîne sont des extraits des passages GitHub, relevés avec
`gh` : ils ne gardent que les lignes utiles, et les valeurs des secrets n'y figurent pas. Le récit qui relie ces
preuves est dans `docs/sprint-3/COMPTE-RENDU-N5-2026-10-16.md`.

Critères de la grille : 1. sources licites ; 2. traçabilité ; 3. refus hors corpus ; 4. pipeline rejouable ;
5. en production. S'y ajoutent le livrable « questions de démonstration » et le journal des retours.

## Le jeu de questions de démonstration et ses rejeux

| Preuve | Fichier | Critère |
|---|---|---|
| Mesure des questions de démonstration sur la copie du corpus de production ; elle a conduit à la version 2 du jeu | `questions-demo-mesure-2026-10-16.md` | livrable, 3 |
| Rejeu du jeu sur l'index local : aucun écart | `rejeu-local-2026-10-16.json` | livrable, 4 |
| Rejeu pendant la livraison N5, avant la bascule : aucun écart | `rejeu-rita-index-20261016-185554-b00a51e6b3ed.json` | 4, 5 |
| Rejeu pendant la livraison N6 : aucun écart | `rejeu-rita-index-20261016-210144-c582ddc608b4.json` | 4, 5 |
| Rejeu pendant chacune des deux ingestions : aucun écart, mêmes passages | `rejeu-rita-index-ing-20261016-210840.json`, `rejeu-rita-index-ing-20261016-212125.json` | 4, 5 |

## L'évaluation des réponses et des citations

| Preuve | Fichier | Critère |
|---|---|---|
| Évaluation sur l'API locale (deux passages) et ma relecture : 8 sur 8 conformes, aucune affirmation non soutenue | `evaluation-2026-10-16-1714.json`, `evaluation-2026-10-16-1717.json`, `evaluation-2026-10-16-relecture.md` | 2, 3 |
| Évaluation en production et ma relecture : 8 sur 8 conformes, caractère de contrôle relevé dans Q4 | `evaluation-2026-10-16-2146.json`, `evaluation-production-2026-10-16-relecture.md` | 2, 3, 5 |
| Deux essais refusés en production (403 : la clé envoyée n'était pas celle du serveur) | `evaluation-2026-10-16-2140.json`, `evaluation-2026-10-16-2142.json` | 5 |

## L'ingestion en production

| Preuve | Fichier | Critère |
|---|---|---|
| Préparation du serveur : compte `rita_ingestion` (lire et ajouter des articles, rien d'autre), dossier des rapports | `serveur-preparation-2026-10-16.md` | 1, 4 |
| Première ingestion arrêtée à la collecte (`FeatureNotFound: lxml`), rien écrit | `manifeste-2026-10-16-170439.json`, `journaux/ingestion-1-echec-lxml.txt` | 4 |
| Ingestion réussie après la livraison N6 : 30 lus, 29 écrits | `manifeste-2026-10-16-190839.json`, `journaux/ingestion-2-reussie.txt` | 4, 5 |
| Ingestion relancée : 30 lus, 0 écrit (dédoublonnage), même empreinte de contenu | `manifeste-2026-10-16-192124.json`, `journaux/ingestion-3-dedoublonnage.txt` | 4 |
| Journal des opérations du serveur, copié le 16/10 à 19:35 UTC | `journal-serveur-2026-10-16.jsonl` | 4, 5 |

## Les livraisons N5, N6 et N7

| Preuve | Fichier | Critère |
|---|---|---|
| Livraison N5 (PR #101) : construction, contrôle du script du serveur, mise en service | `journaux/livraison-N5.txt` | 5 |
| Livraison N6 (PR #103), tentative 1 arrêtée avant le serveur par un 429 du registre d'images | `journaux/livraison-N6-tentative-1-429.txt` | 5 |
| Livraison N6, tentative 2 : nettoyage d'un résumé RSS essayé dans l'image, mise en service | `journaux/livraison-N6.txt` | 4, 5 |
| `/health` en production après l'ingestion (commit `72dba4d`, 2081 articles, index `c91baa3f…`), capture par Chrome sans connexion, 16/10 à 22:29 | `captures/production-health-2026-10-16.png` | 5 |
| Livraison N7 (PR #105), vert du premier coup : nettoyage RSS essayé dans l'image, mise en service | `journaux/livraison-N7.txt` | 5 |
| `/health` après N7 (commit `66963da`, 2081 articles, index `13f15d84…`, même empreinte de contenu), capture par Chrome sans connexion, 17/10 à 00:23 | `captures/production-health-N7-2026-10-17.png` | 5 |
| L'écran de question en production, sans clé : il demande la clé avant toute question | `captures/production-question-2026-10-16.png` | 5 |

## L'écran de question en production, avec la clé (17/10)

Captures que j'ai prises dans Chrome, après N7. La clé est tapée dans un champ masqué, qui disparaît après la
connexion : elle n'apparaît sur aucune image. Les découpes sont faites dans la capture entière, sans retouche
(recadrage seul).

| Preuve | Fichier | Critère |
|---|---|---|
| Page entière : question « Combien de postes Netflix va-t-il supprimer ? », réponse, référence, fiche de la source ; 17/10 à 16:25, requête `8e27c6afeb4741d1b4270a4186826b1a` | `captures/production-reponse-et-fiche-2026-10-17.png` | 2 |
| Découpe : la question, la réponse avec le renvoi [1], la référence (article 2788), l'index interrogé (2081 articles, empreinte `0b372539c971`) | `captures/production-reponse-citee-2026-10-17.png` | 2 |
| Découpe : la fiche de l'article 2788 et le passage transmis au modèle | `captures/production-fiche-source-2026-10-17.png` | 2 |
| Page entière : question « Quelle est la recette de la tarte Tatin ? », refus ; 17/10 à 16:31, requête `eefffc27c457410da1d953582dfcb9b8` | `captures/production-refus-page-2026-10-17.png` | 3 |
| Découpe : la question, le refus et son motif (`OUT_OF_CORPUS`) | `captures/production-refus-2026-10-17.png` | 3 |

## L'arrêt de Google News (T7) et la collecte du poste

| Preuve | Fichier | Critère |
|---|---|---|
| Suspension de la collecte du poste, le 16/10 au matin | `suspension-collecte-2026-10-16.txt` | 1 |
| Reprise sur le code sans Google News : dossier passé à `72dba4d`, tâche réactivée, première collecte (6 étapes sur 6, 3 flux sur 3) | `reprise-collecte-2026-10-16.txt`, `manifeste-poste-2026-10-16-220139.json` | 1, 4 |
| Registre des traitements : T7 arrêté, corpus d'articles examiné, T8 inscrit | `../../db/RGPD-registre-des-traitements.md` | 1 |

## Après la version 1 du livrable (17 au 19/10)

| Preuve | Fichier ou passage | Critère |
|---|---|---|
| Livraison N8 (PR #107, `7f2a855`) : trois tentatives arrêtées par un 429, la quatrième réussie | passage GitHub `39050211790` | 5 |
| Ingestion de répétition, 18/10 : 30 lus, 29 écrits, 1 rejeté (manifeste relu sur le serveur) ; rejeu sans écart ; 2110 articles | passage GitHub `39115076808` | 4, 5 |
| Ingestion lancée pendant l'atelier, 19/10 : « operation reussie », code 0 ; 2140 articles | passage GitHub `39265862974` | 4, 5 |
| `/health` après l'ingestion de l'atelier (commit `7f2a855`, 2140 articles, index `fc87b92a…`), capture par Chrome sans connexion, 19/10 à 17:40 UTC ; page entière et découpe (recadrage seul) | `captures/production-health-atelier-2026-10-19-page.png`, `captures/production-health-atelier-2026-10-19.png` | 5 |
| Retours de l'atelier 3 : grille non remplie, retours oraux du formateur et suite donnée | `../../eval/ateliers/sprint-3-grille.md` | journal |

## Ce qui manque à ces preuves

- Les captures de l'écran avec la clé datent du 17/10, après N7 : il n'y en a pas pour les passages N5 et N6, dont
  les mêmes comportements sont prouvés par l'évaluation en production (fichier `evaluation-2026-10-16-2146.json`).
  Aucune capture ne montre le refus d'une demande de conseil d'achat (`INTENTION_INTERDITE`) : il est prouvé par la
  même évaluation.
- Les journaux du serveur, manifestes et rapports de rejeu des ingestions du 18 et du 19/10 ne sont pas copiés
  dans le dépôt : les passages GitHub et `/health` en tiennent lieu.
- L'atelier 3 n'a pas donné de grille remplie : les retours sont oraux (`../../eval/ateliers/sprint-3-grille.md`).
- Le manifeste écrit sur le serveur ne porte pas le commit (`"commit": null`, Git n'est pas dans l'image) : la version
  du code se lit dans le journal des opérations et dans `/health`.

Commandes pour relire les journaux de chaîne à la source :

```
gh run view 38935022555 --repo Ganda15/rita-agent
```

```
gh run view 38950485935 --repo Ganda15/rita-agent
```

```
gh run view 38936863197 --repo Ganda15/rita-agent
```

```
gh run view 38952685069 --repo Ganda15/rita-agent
```

```
gh run view 38954283118 --repo Ganda15/rita-agent
```

```
gh run view 38973167532 --repo Ganda15/rita-agent
```

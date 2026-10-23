# Sprint 5, étapes 12 et 13 : le test de la doc à la lettre, et les deux répétitions (23/10/2026)

Prototype local du sprint 5 (projet Docker `rita-s5`, `http://localhost:8011`), dossier
`D:\KandaWork\RITA_PROJECT\rita-agent-sprint-5`. Commandes lancées par Era ; vérifications en lecture seule par Claude
(journal de la copie, `/sante`, API de Langfuse, `gh`). Aucune clé n'est recopiée ici, ni aucun texte de question.
Heures de Paris.

## 1. Le test de `docs/exploitation.md` à la lettre (étape 12)

Era a suivi la documentation seul, dans l'ordre, depuis sa copie de lecture. Une panne simulée a été posée par Claude
sans en dire la nature ; seul le symptôme a été donné (« RITA ne répond plus à mes questions »). C'est une répétition
par l'auteur de la doc, pas le test par un tiers, qui se fera à l'atelier n°5.

| Section | Heure | Résultat | Trous relevés |
|---|---|---|---|
| Avant de commencer | 08:45 | les deux clés présentes (vérifiées par une commande de l'auteur, faute de commande dans la doc) | 1 : pas de commande pour vérifier les clés ; 4 : Langfuse non mentionné |
| Déployer | 08:45 | `d752b33` déployé, précédente `d43a01e` ; tableau de bord : « Le service répond » SAIN | 2 : `initialiser` affiche des zéros sur une copie déjà initialisée ; 3 : avertissements `Read-only file system` non expliqués |
| Diagnostiquer une panne | 10:04 - 10:28 | cause trouvée à 10:15 (bandeau de l'exercice), en 11 minutes ; panne retirée à 10:16 ; 5 appels en HTTP 200 à 10:17 ; issue #129 ouverte à 10:10, fermée par la vigie à 10:27 | 5 : l'étape 2 renvoyait à l'étape 4 et faisait sauter l'étape 3 (l'exercice) ; 6 : la panne type présentée comme Azure seulement ; 7 : rien de prévu si l'étape 4 ne trouve rien ; 8 : rien de prévu si l'étape 5 donne encore des 503 ; 9 : la consigne de la carte « Réponses en erreur » ne parlait pas de l'exercice |
| Revenir à la version précédente | entre 10:35 et 10:39 | revenu à `d43a01e` en 5 s, image vérifiée, sans reconstruction ; `etat` : précédente « aucune » | aucun |
| Déployer de nouveau | 10:39 | `18f34de` déployé en 4 s ; la nouvelle consigne servie par `/sante` | aucun |

Les neuf trous sont corrigés dans le commit `18f34de` (tests rouges puis verts, `tests/test_exploitation_doc.py`). Un
dixième (§ 3 ci-dessous) l'est ensuite.

## 2. Les deux répétitions de la démo (étape 13)

Horodatages relevés dans les traces de Langfuse et dans le journal de la copie ; durées totales chronométrées par Era.

| | Répétition 1 | Répétition 2 |
|---|---|---|
| Vigie | à blanc (sans `--github`) | réelle (`--github`) |
| Parcours principal | réponse citée à 10:49:11, refus `OUT_OF_CORPUS` à 10:49:38 | réponse citée à 11:22:58, refus `OUT_OF_CORPUS` à 11:23:19 |
| Livraison | `deployer` : `18f34de` (copie redémarrée à 10:51:35) | `deployer` : `57ebf56` ; puis un second `deployer` et un `revenir`, qui ont laissé la copie sur l'ancienne version |
| Dérive | 10:51:58 - 10:53:21 : 12 refus sur 12, 0 jeton | 11:26:06 - 11:27:30 : 12 refus sur 12, 0 jeton |
| Alerte | tableau de bord à 10:54:59 : « Refus de sécurité » PROBLÈME, 12 sur 12 | issue #131 ouverte à 11:28:01, fermée par la vigie à 11:45:47 |
| Durée totale | environ 9 minutes | environ 9 minutes 30 |
| À corriger | la phrase sur la livraison automatique de production (N15) oubliée | le segment Livraison laissé sur l'ancienne version |
| Correction | phrase raccourcie, dite juste après `etat` (commit `57ebf56`) | un seul `deployer` dans le segment (commit `648293f`) |

## 3. Langfuse sur la copie, et une fausse alerte de production

| Heure | Ce qui s'est passé |
|---|---|
| 09:50 | traçage activé sur la copie avec les clés du `.env` de développement ; trace vérifiée (`question`, entrée et sortie vides : aucun texte conservé ; même `request_id` que le journal de la copie) |
| 10:30 | issue #130 « Incident : alerte Langfuse « RITA : fournisseur en erreur » » ouverte par la chaîne d'alerte de production |
| 11:47 | cause établie par l'API de Langfuse : les 10 observations en erreur des dernières 24 h viennent toutes de la panne simulée de la copie (10:04 et 10:09, `FOURNISSEUR_INDISPONIBLE`) ; les clés du `.env` de développement sont celles du projet de production ; production saine (`/health` : `ok`, `3c35398`) |
| 11:48 | issue #130 fermée avec un commentaire explicatif |
| 11:52 - 12:00 | la copie passe sur son propre projet Langfuse, `rita-copie-sprint5`, sans alerte ; vérifié par l'API (projet de chaque paire de clés) ; une question de test arrive dans `rita-copie-sprint5` et plus dans le projet de production |

Trou 10, corrigé dans `docs/exploitation.md` : les clés Langfuse de la copie viennent d'un projet propre à la copie,
jamais celui de la production.

## 4. Ce qui reste

- Le test de la doc par une personne qui ne l'a pas écrite : à l'atelier n°5, avec l'évaluateur.
- Sans `--github`, la vigie affiche `[à blanc] ouvrirait l'issue …` puis, à tort, `vigie : ouverte : …` : aucune issue
  n'est créée, mais la seconde ligne peut tromper un lecteur. Non corrigé.

# Livraisons N5 et N6, ingestion en production : compte rendu (16/10/2026)

Compte rendu rédigé le 16/10/2026 après les opérations, à partir des sorties relevées dans la journée (de 17:00 à
19:35 UTC). Il raconte et relie ; il ne remplace pas les preuves. Les fichiers écrits par le serveur pendant les
opérations sont copiés sans modification dans `evidence/sprint-3/` :

- `rejeu-rita-index-20261016-185554-b00a51e6b3ed.json` : le rapport du rejeu écrit pendant la livraison N5 ;
- `manifeste-2026-10-16-170439.json` : le manifeste de la collecte arrêtée pendant la première ingestion ;
- `rejeu-rita-index-20261016-210144-c582ddc608b4.json` : le rapport du rejeu écrit pendant la livraison N6 ;
- `manifeste-2026-10-16-190839.json` et `rejeu-rita-index-ing-20261016-210840.json` : la première ingestion réussie ;
- `manifeste-2026-10-16-192124.json` et `rejeu-rita-index-ing-20261016-212125.json` : la seconde ingestion ;
- `journal-serveur-2026-10-16.jsonl` : le journal des opérations du serveur, copié à 19:35 UTC.

Livraison N5 : PR #101 (`develop` vers `main`), fusionnée en `41b1763`. Elle met en production le code du sprint 3
(PR #100). Les commandes du serveur ont été lancées par Era (Hetzner, `ubuntu-4gb-fsn1-1`) ; les contrôles de GitHub
et de l'API publique depuis le poste. Les heures de GitHub et de `/health` sont en UTC ; le journal du serveur écrit
l'heure de Paris (UTC+2).

## 1. La livraison N5 : réussie

Passage « Livraison » `38935022555`, sur le commit `41b1763` :

```text
lint | success | 16:50:11 -> 16:50:22
secrets | success | 16:50:11 -> 16:51:09
construire-et-publier | success | 16:51:12 -> 16:55:28
attendre-creneau | success | 16:55:30 -> 16:55:38
deployer | success | 16:55:43 -> 16:59:53
attendre-reprise | skipped | 16:59:53 -> 16:59:53
deployer-reprise | skipped | 16:59:53 -> 16:59:53
```

Réponse du serveur, lue dans le journal du travail `deployer` :

```text
script du serveur identique au depot (2ed6b98db4817366d4774f837460992506370e2bcf2dcdf005c95e0fc551cbd9)
operation reussie
code rendu par le serveur : 0
```

Journal du serveur (`/root/rita-deploy/journal.jsonl`) :

```text
{"date": "2026-10-16T18:59:50+02:00", "operation": "livrer", "vers": "ghcr.io/ganda15/rita-api@sha256:b00a51e6b3edcdbf306bea0e09ced15fa494d339b7dbc1d4b1563f12e129d2f9", "de": "ghcr.io/ganda15/rita-api@sha256:086fed50dd3402a4bd5f5a8a03fed326e6223c4f00ef1adf21c253da7b6b7f7e", "resultat": "livree"}
```

Rapport du rejeu des questions de démonstration, écrit pendant la livraison, avant la bascule :

```text
-rw-r--r-- 1 10001 10001 2795 Oct 16 16:59 rejeu-rita-index-20261016-185554-b00a51e6b3ed.json
bloquant : False | ecarts : []
index : d2d029d7873343f3a89ccb1fec49c60e 50579b43a651
```

Image en service après la livraison :

```text
ghcr.io/ganda15/rita-api@sha256:b00a51e6b3edcdbf306bea0e09ced15fa494d339b7dbc1d4b1563f12e129d2f9
```

`/health` en production, lu depuis le poste après la livraison :

```json
{"status":"ok","project":"RITA","commit":"41b1763c8799585342a113c59028696a95ecfd71","construit_le":"2026-10-16T16:53:48Z","index":{"nb_articles":2052,"id_max":2809,"empreinte":"50579b43a651d97666c1df5eba246329341a03bdb524cf3f7b747bcf684c34f5","identifiant":"d2d029d7873343f3a89ccb1fec49c60e","configuration":{"modele":"all-MiniLM-L6-v2","texte":"texte_indexable(titre, resume)","format":1},"construit_le":"2026-10-16T16:59:04+00:00"}}
```

Accès : `POST /question` sans clé d'API rend `403` ; l'écran `question.html` rend `200`.

L'index annoncé par `/health` (identifiant `d2d029d7…`, empreinte `50579b43a651…`) est celui du rapport de rejeu :
l'index servi est bien celui qui a été vérifié.

## 2. La première ingestion : échec à la collecte, production intacte

Lancée depuis le poste ; GitHub a créé le passage `38936863197` :

```text
gh workflow run ingestion.yml --repo Ganda15/rita-agent -f acteur="Era" -f motif="Premiere ingestion du sprint 3, apres la livraison N5"
```

Passage `38936863197` :

```text
failure
ingerer | failure | 17:04:31 -> 17:04:42 | etapes en echec : Collecter, réindexer, vérifier, mettre en service
script du serveur identique au depot (2ed6b98db4817366d4774f837460992506370e2bcf2dcdf005c95e0fc551cbd9)
operation refusee ou en echec : voir journal.jsonl sur le serveur
code rendu par le serveur : 1
```

Journal du serveur :

```text
{"date": "2026-10-16T19:04:40+02:00", "operation": "ingerer", "passage": "38936863197", "resultat": "echec collecte", "message": "commande en echec : docker run (code 1) ; index servi inchange, les ecritures deja validees restent en base"}
```

Manifeste de la collecte (le message d'erreur est coupé à 90 caractères par `pipelines/ingest.py:527`) :

```text
/root/rita-deploy/rapports/manifeste-2026-10-16-170439.json
rss | ok : False | erreur : FeatureNotFound: Couldn't find a tree builder with the features you requested: lxml. Do yo | ecrites : 0
```

Base de production après l'échec :

```text
 articles | id_max
----------+--------
     2052 |   2809
```

`/health` après l'échec : `commit 41b1763 | index d2d029d7873343f3a89ccb1fec49c60e 50579b43a651 2052 articles`.

Les garde-fous ont joué leur rôle. L'échec est arrêté à la collecte, aucun article n'est écrit et l'index servi ne
change pas. Le journal et le manifeste disent pourquoi.

**Cause.** `sources/rss.py` nettoyait les résumés avec BeautifulSoup et l'analyseur `lxml`. BeautifulSoup arrive dans
l'image par `yfinance==1.4.1` (`requirements-api.txt`), mais `lxml` n'y est pas. Sur le poste, `lxml` est installé :
la suite de tests passait, et rien ne vérifiait la collecte dans l'image elle-même.

## 3. La correction : livraison N6, commit `ad390f6`

| Correction | Origine |
|---|---|
| `sources/rss.py` : analyseur `html.parser`, fourni avec Python | l'échec ci-dessus |
| `.github/workflows/livraison.yml` : la CI nettoie un résumé dans l'image, sans réseau, avant de la publier | l'échec ci-dessus |
| `api/donnees.py` : la fiche d'un article rend `source` = l'éditeur cité par la référence, et `flux` = l'identifiant brut | revue automatique de la PR #100 (P2) |
| `rag/controle_questions.py` et `evals/evaluer_reponses.py` : une question couverte doit avoir autant de repères que de faits ; `zip` strict | revue automatique de la PR #100 (P2) |
| `rag/indexation.py` : la date de publication est écrite en UTC avant le calcul de l'empreinte | écart constaté entre le poste (`+02:00`) et le serveur (`+00:00`) |

Tests écrits avant le code, lancés par Era. Rouge constaté sur les 6 fichiers touchés :

```text
FAILED tests/test_rss.py::test_le_nettoyage_des_resumes_n_exige_pas_lxml - bs4.exceptions.FeatureNotFound: lxml abse...
FAILED tests/test_workflows_livraison.py::test_l_image_verifiee_sait_nettoyer_un_resume_rss - StopIteration
FAILED tests/test_api_question.py::test_la_fiche_cite_l_editeur_et_garde_le_flux - AssertionError: assert 'lemonde_eco' == '...
FAILED tests/test_api_question.py::test_la_source_de_la_fiche_est_celle_de_la_reference - AssertionError: assert 'Boursorama' == 'e...
FAILED tests/test_questions_demo.py::test_un_jeu_mal_forme_est_refuse[reperes_absents] - Failed: DID NOT RAISE ValueError
FAILED tests/test_questions_demo.py::test_un_jeu_mal_forme_est_refuse[reperes_incomplets] - Failed: DID NOT RAISE ValueError
FAILED tests/test_evaluer_reponses.py::test_des_reperes_incomplets_arretent_l_evaluation - Failed: DID NOT RAISE ValueError
FAILED tests/test_identite_index.py::test_l_empreinte_ne_depend_pas_du_fuseau_de_la_session[heure_de_paris] - AssertionError: assert '34f2455fb806...7c...
FAILED tests/test_identite_index.py::test_l_empreinte_ne_depend_pas_du_fuseau_de_la_session[sans_fuseau] - AssertionError: assert '34f2455fb806...7c...
9 failed, 91 passed, 9 skipped, 1 warning in 15.51s
```

Après le code :

```text
100 passed, 9 skipped, 1 warning in 15.42s
1225 passed, 24 skipped, 2 xfailed, 3 warnings in 64.97s (0:01:04)
```

La suite complète donnait `1215 passed, 24 skipped, 2 xfailed` avant la correction : les 10 tests ajoutés passent, rien
d'autre ne change.

Le code de l'étape CI a été essayé sur le poste, `lxml` masqué : il affiche `Un resume court` et rend le code 0 ; avec
un texte différent, il rend le code 1.

**Empreinte, sur le vrai corpus.** Un index jetable a été reconstruit sur le poste avec le code corrigé, à partir de la
copie locale de la base de production (même corpus : 2052 articles, identifiant maximal 2809), dans un dossier
temporaire. L'index local de travail n'a pas été modifié.

```text
2052 lus | 2052 indexes | 0 bloques ecartes | 765 citant une valeur suivie
nb_articles 2052 | id_max 2809 | empreinte 50579b43a651d97666c1df5eba246329341a03bdb524cf3f7b747bcf684c34f5
```

| Index | Empreinte |
|---|---|
| Index local, construit avant la correction | `28e8e171f488…` |
| Même corpus, code corrigé | `50579b43a651…` |
| Production, livraison N5 | `50579b43a651…` |

Même corpus, même empreinte sur le poste et sur le serveur. En production, la session PostgreSQL est déjà en UTC :
la correction ne change pas l'empreinte de l'index servi.

## 4. La livraison N6 : réussie à la seconde tentative

PR #102 (`sprint-3-donnees-ancrage` vers `develop`, fusionnée en `e0322e5`), puis PR #103 (`develop` vers `main`,
fusionnée en `72dba4d` à 18:51 UTC). Sur la PR #103, la revue Codex s'est terminée sans remarque et la revue
automatique du dépôt a rendu « No issues found ».

Passage « Livraison » `38950485935`. La première tentative s'est arrêtée à la construction de l'image : le registre
`public.ecr.aws` a refusé le téléchargement de l'image de base (`429 Too Many Requests`). Le travail `deployer` a été
sauté et la production n'a pas changé (`/health` : commit `41b1763`). Seconde tentative :

```text
construire-et-publier | success | 18:56:36 -> 19:00:25
attendre-creneau | success | 19:00:28 -> 19:01:24
deployer | success | 19:01:32 -> 19:05:40
```

Essai du nettoyage RSS dans l'image publiée, puis réponse du serveur :

```text
Un resume court
nettoyage des resumes RSS operationnel dans l'image
script du serveur identique au depot (2ed6b98db4817366d4774f837460992506370e2bcf2dcdf005c95e0fc551cbd9)
operation reussie
code rendu par le serveur : 0
```

Journal du serveur :

```text
{"date": "2026-10-16T21:05:37+02:00", "operation": "livrer", "vers": "ghcr.io/ganda15/rita-api@sha256:c582ddc608b453695fa6ed797f826edc90aaea0a7dbed1dff14d40b3688d22b9", "de": "ghcr.io/ganda15/rita-api@sha256:b00a51e6b3edcdbf306bea0e09ced15fa494d339b7dbc1d4b1563f12e129d2f9", "resultat": "livree"}
```

`/health` après la livraison : commit `72dba4d`, index `bad3a9398bad49938cf6ebae4cbc9b89`, 2052 articles, empreinte
`50579b43a651…`. L'index a été reconstruit avec le code corrigé, et son empreinte n'a pas changé : c'est le résultat
attendu de la correction du fuseau. `POST /question` sans clé rend `403`, l'écran `question.html` rend `200`.

## 5. L'ingestion en production : réussie

L'ingestion a été lancée deux fois par le bouton, à 19:08 et à 19:21 UTC, sur le commit `72dba4d`.

| Passage | Journal | Collecte (manifeste) | Index après | Rejeu |
|---|---|---|---|---|
| `38952685069` | « ingeree » | 3 flux sur 3, 30 lus, 29 écrits, 1 doublon écarté | `9d60c9c0…`, 2081 articles, empreinte `0b372539c971…` | `bloquant : False`, aucun écart |
| `38954283118` | « ingeree » | 3 flux sur 3, 30 lus, 0 écrit, 30 doublons écartés | `c91baa3f…`, 2081 articles, empreinte `0b372539c971…` | `bloquant : False`, aucun écart |

Base de production après les deux passages :

```text
 articles | id_max
----------+--------
     2081 |   2839
```

`/health` après la seconde ingestion : 2081 articles, identifiant maximal 2839, index
`c91baa3fac9147e9bedcfdd4a872d5ac`, empreinte `0b372539c971ef42a9d93196b20cb5ac8620ff7786382e363fa0cf9e0d241ee7`.

Trois constats :

- la collecte fonctionne dans l'image de production : 29 nouveaux articles ;
- le dédoublonnage fonctionne : relancée 13 minutes plus tard, la collecte relit les mêmes 30 articles et n'en écrit
  aucun ; l'empreinte du contenu reste la même, seul l'identifiant de construction change ;
- les 29 nouveaux articles ne changent les trois premiers passages d'aucune des 8 questions de démonstration : les
  rapports de rejeu de la livraison N6 et des deux ingestions donnent les mêmes passages, question par question.

## Ce qui reste

- Évaluer les réponses sur la production (plan de travail, tâche D2).
- Le manifeste écrit dans l'image porte `"commit": null` : Git n'est pas dans l'image, et rien ne dit au manifeste
  quelle version du code a tourné. Le journal du serveur et `/health` donnent cette version ; le manifeste seul, non.
- La construction de l'image télécharge l'image de base sans authentification depuis `public.ecr.aws`. Le 16/10, quatre
  constructions ont échoué sur `429 Too Many Requests` (livraison N5 sur `develop`, deux fois sur la PR #102, première
  tentative de la livraison N6). Chaque fois, une relance a suffi ; la cause n'est pas traitée.
- `sources/scraper.py:149` utilise encore `lxml`. Ce module n'est pas appelé par l'ingestion ; il n'est pas corrigé ici.
- Le jeu de questions (`rag/questions_demo.json`) reste lié à l'index local sur lequel il a été mesuré (identifiant
  `18c122a9…`, empreinte `28e8e171…`, calculée avant la correction du fuseau).

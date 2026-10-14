# INC-007 : dix pushs de suite avec la chaîne rouge, alors que la suite était verte sur le poste

> Trouvé le 03/10/2026 vers 20 h 35 (heure de Paris) **en recomptant les critères de E4**, pas par une alerte : pour
> prouver le critère C18, la commande `gh run list` a montré dix exécutions rouges d'affilée sur `develop`, alors que
> chaque commit avait été annoncé « 803 passed » sur le poste.

| | |
|---|---|
| **Détecté le** | 03/10/2026, vers 20 h 35, en lisant l'historique des exécutions GitHub Actions pour le recomptage des critères E4 (tâche T1 du plan E4) |
| **Sévérité** | **P3** : `develop` rouge pendant 1 h 26, `main` jamais touchée, aucune image publiée (la publication n'a lieu que sur un tag), aucun déploiement ; mais une porte de qualité qui ne s'est pas fait entendre pendant dix pushs |
| **Durée** | du premier rouge (17:15 UTC, commit `b54d65e`) au premier vert (18:41 UTC, commit `0e53ede`) : 1 h 26 ; dont environ 1 h 20 sans que personne le sache |
| **Impact réel** | 10 exécutions rouges du workflow Tests et 10 du workflow Livraison sur `develop` ; la demande de fusion vers `main` qui aurait suivi aurait été refusée par le ruleset (contrôle `pytest` obligatoire), ce qui n'a pas été éprouvé ; le chiffre « 97 sur 100 vertes » de `evidence/C18/` datait d'avant et reste vrai pour sa période |
| **Commit du correctif** | `0e53ede` |
| **Issue / demande de fusion** | **aucune, commit direct sur `develop`**, comme INC-006 : la chaîne issue, branche, PR n'a pas été suivie ; le correctif rejoindra `main` par la pull request du gel, relue |

## 1. Ce qu'on a vu *(le symptôme, avant la cause)*

```
15:21 success 37132947446 792c55c
17:15 failure 37139813881 b54d65e
... (neuf autres rouges de suite)
18:31 failure 37144545628 46aab59
```

Job `pytest` du workflow Tests, étape « Lancer les tests et mesurer la couverture » :

```
FAILED tests/test_scout_base.py::test_collect_prend_le_cours_dans_la_base_et_non_sur_le_reseau - RuntimeError: DATABASE_URL absente. Voir .env.example
FAILED tests/test_scout_base.py::test_collect_expose_adtv20_et_non_un_champ_nomme_volume
FAILED tests/test_scout_base.py::test_collect_remonte_les_indicateurs_de_risque
FAILED tests/test_scout_base.py::test_collect_signale_une_cotation_perimee
4 failed, 770 passed, 29 skipped, 2 xfailed in 39.03s
```

Le job `evals` était vert. Le workflow Livraison échouait aussi, à l'étape « Tests — porte de livraison ».

## 2. Cause racine

**Technique.** Le 03/10, pour que le briefing reçoive le RSI, `agents/scout.py` a gagné une troisième lecture en base,
`lire_rsi`. Quatre tests du scout remplaçaient les deux premières lectures (`lire_socle`, `lire_volatilite_drawdown`)
et pas la troisième. Sur le poste, un fichier d'environnement fournit une vraie base ; `lire_rsi` y lisait donc la
vraie base locale et les quatre tests passaient. En CI, aucune base : « DATABASE_URL absente ».

**De conception, la partie qui compte.** Deux choses ont laissé passer le défaut. D'abord un test qui doit être
isolé de la base ne l'était que par la vigilance de celui qui l'écrit : rien ne le forçait. Ensuite la vérification
« c'est fini » s'arrêtait au poste : la suite locale était verte à chaque commit, et personne n'ouvrait la chaîne
d'intégration continue après le push. Le crochet `exiger-tests-verts` ne regarde que le poste.

## 3. Reproduction en développement

Reproduire la CI en vidant, dans l'environnement du processus, toutes les variables du modèle d'environnement
(`load_dotenv` n'écrase pas une variable déjà présente, même vide) :

```
(variables du modèle d'environnement toutes vides)
C:\Python314\python.exe -m pytest tests/test_scout_base.py -q --no-cov
4 failed, 3 passed in 0.39s
```

Les mêmes quatre noms que dans la CI.

## 4. Procédure de débogage

| # | Hypothèse | Comment elle a été testée | Résultat |
|---|---|---|---|
| 1 | Panne passagère de l'infrastructure de CI | 10 exécutions rouges consécutives, les quatre mêmes tests à chaque fois, premier rouge sur un commit précis | **écartée** |
| 2 | Écart Python 3.13 (CI) contre 3.14 (poste) | l'erreur est levée à `indicateurs/socle.py:138` par un `RuntimeError` volontaire sur `DATABASE_URL`, pas une incompatibilité de version | **écartée** |
| 3 | Un test atteint la vraie base | l'erreur le dit ; reproduction locale en vidant les variables : les mêmes 4 tests tombent | **confirmée** |
| 4 | Lequel des appels en base n'est pas remplacé | lecture de `tests/test_scout_base.py` et de `agents/scout.py` : `lire_rsi` ajouté au scout le même jour, jamais remplacé dans ces quatre tests (les deux tests écrits pour le RSI, eux, le remplacent) | **cause trouvée** |
| 5 | Le premier rouge est bien le commit qui ajoute le RSI | historique des exécutions : dernier vert `792c55c`, premier rouge `b54d65e` (« Les 13 indicateurs entrent dans le prompt ») | **confirmée** |

## 5. Correction, étape par étape

1. Une fixture `autouse` dans `tests/test_scout_base.py` remplace `agents.scout.lire_rsi` par une lecture vide pour
   tous les tests du fichier. Les deux tests qui parlent du RSI le remplacent eux-mêmes ensuite, par leur valeur.
2. **Pourquoi une fixture et pas quatre lignes ajoutées** : corriger les quatre tests laisserait le prochain test du
   scout retomber dans le même piège ; la fixture règle le cas général du fichier.
3. Test d'abord au sens strict : le test rouge existait déjà (la CI) ; je l'ai reproduit localement avant de toucher
   au code, puis la fixture l'a fait passer.

## 6. Vérification et non-régression

```
(variables du modèle d'environnement toutes vides)
tests/test_scout_base.py : 7 passed
suite complète avec couverture : 803 passed, 2 xfailed, couverture 94,70 % (seuil 90)
GitHub Actions, commit 0e53ede : Tests success, Livraison success
```

**Non-régression** : la fixture elle-même. Un nouveau test du scout qui appellerait la base sans la remplacer
échouerait en CI et en local avec les variables vides.

## 7. Ce qui n'est pas fait, et la leçon

- **Pas de garde générale** qui interdirait à toute la suite d'atteindre la base hors des tests marqués pour cela
  (par exemple en forçant une adresse de base invalide dans `conftest.py`). Elle protégerait tous les fichiers, pas
  seulement celui-ci ; elle est à proposer à Era, parce qu'elle touche le comportement de toute la suite.
- **La vérification locale ne suffit pas.** Règle ajoutée à la pratique, déjà vraie pour les livrables et fausse pour
  les pushs ordinaires : après un push sur `develop`, lire le résultat de la chaîne (`gh run list --limit 3`) avant
  de dire « c'est fait ».
- La détection est venue d'un recomptage, pas d'une alerte. **Aucune alerte n'existe sur un workflow rouge** :
  `alerte-incident.yml` répond à une alerte Langfuse (événement `alerte-langfuse`), pas à un échec de Tests ou de
  Livraison. Une notification sur échec de la chaîne est un choix à discuter, pas à faire dans la précipitation.

## 📖 Glossaire

- **Fixture `autouse`** : préparation de test que pytest applique automatiquement à chaque test d'un fichier, sans qu'il la demande.
- **Isolation d'un test** : propriété d'un test qui ne dépend ni d'une base, ni d'un réseau, ni d'une clé réelle ; il donne le même résultat sur tout poste.
- **Porte de livraison** : étape qui exécute les tests avant de construire ou de publier l'image, et arrête la chaîne si elle est rouge.
- **Ruleset** : règle GitHub qui impose, par exemple, des contrôles verts avant toute fusion sur `main`.
- **Post-mortem** : fiche écrite après un incident (symptôme, cause, reproduction, correction, vérification).

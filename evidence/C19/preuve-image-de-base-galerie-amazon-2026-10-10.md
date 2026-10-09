# Preuve C19 et C13 : l'image de base vient de la galerie publique d'Amazon (carte #85), nuit du 9 au 10 octobre 2026

## Pourquoi

Le Dockerfile téléchargeait `python:3.13-slim` depuis Docker Hub, sans compte. Le 09/10 au soir, l'étape « Construire
l'image (sans publier) » de `livraison.yml` a échoué trois fois de suite, alors que les tests passaient à chaque fois :

| Exécution | Commit | Réponse de Docker Hub |
|---|---|---|
| `37991304979`, tentative 1 | `2755b66` | `429 Too Many Requests` |
| `37991304979`, tentative 2 | `2755b66` | `429 Too Many Requests` |
| `37994665751` | `645696f` | `504 Gateway Timeout` (`auth.docker.io`) |

Les pages d'état de GitHub et de Docker ne signalaient rien. Le jour du gel (15/10), le tag publie l'image pour la
première fois. Décision d'Era le 09/10 : ne plus dépendre de la limite de Docker Hub avant le gel.

## Même image, vérifiée avant le changement

Empreinte de `python:3.13-slim` lue le 09/10 dans les deux registres (requête du manifeste, réponse HTTP 200) :

| Registre | Empreinte |
|---|---|
| Docker Hub, `registry-1.docker.io/library/python` | `sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f` |
| Galerie publique d'Amazon, `public.ecr.aws/docker/library/python` | `sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f` |

## Ce qui a été fait, test d'abord

Test de contrat `tests/test_image_de_base.py` : chaque `FROM` du Dockerfile vient de `public.ecr.aws/docker/library/`,
l'image reste `python:3.13-slim`, et au moins deux étapes sont lues (garde contre un test vide).

**Rouge**, avant le changement (clone propre de `develop`, `645696f`) :

```
FAILED tests/test_image_de_base.py::test_chaque_image_de_base_vient_de_la_galerie_publique_amazon
FAILED tests/test_image_de_base.py::test_l_image_reste_python_3_13_slim - ass...
2 failed, 1 passed in 0.74s
```

**Le changement** : les deux lignes `FROM` (étapes `constructeur` et `execution`) deviennent
`FROM public.ecr.aws/docker/library/python:3.13-slim`, avec un commentaire de trois lignes qui dit pourquoi.

**Vert** : `3 passed in 0.09s`.

**Mutation** : Docker Hub remis dans l'étape `execution`, le test tombe (`2 failed, 1 passed`) ; Dockerfile restauré,
`3 passed`.

**Suite complète** sur le même clone, sans fichier d'environnement : `811 passed, 22 skipped, 2 xfailed`, couverture
94,65 %. E3 § 7.3 et `docs/CI-CD.md` disent d'où vient l'image ; PDF d'E3 régénéré, toujours 20 pages.

## Sur GitHub

Commit `232c209`, poussé par Era dans la nuit du 9 au 10/10.

| Exécution | Résultat |
|---|---|
| Tests, `37997162487` | succès : test des données `260 passed, 3 skipped` ; suite `804 passed, 29 skipped, 2 xfailed`, couverture 94,70 % ; portes d'évaluation `7 passed, 2 xfailed` |
| Livraison, `37997162566` | succès : construction, démarrage de l'image, accès refusé sans clé ; publication sautée (elle n'a lieu que sur un tag) |

Le journal de la construction montre l'origine de l'image et son empreinte, la même qu'en amont :

```
#2 [internal] load metadata for public.ecr.aws/docker/library/python:3.13-slim
#5 [constructeur 1/5] FROM public.ecr.aws/docker/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
```

Aucune réponse `429` ni `504` dans ce journal.

## Ce qui reste, dit franchement

- La galerie d'Amazon est aussi un service extérieur, avec ses propres limites. Elle remplace le service qui a échoué
  trois fois ce soir-là ; elle ne supprime pas toute dépendance.
- La première publication réelle de l'image aura lieu sur le tag du gel (15/10) : c'est elle qui prouvera l'étape
  « Publier l'image vérifiée ».
- `docker-compose.yml` tire encore `postgres:18-alpine` de Docker Hub : seulement pour la pile locale, pas dans la CI.

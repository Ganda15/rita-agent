# Preuve C15 / C13 — preuve de concept en environnement de pré-production

> **C15, critère 4** : *« La preuve de concept est accessible et fonctionnelle en
> environnement de pré-production. »*
> **C15, critère 5** : *« La conclusion à l'issue de la preuve de concept donne un avis
> précis permettant une prise de décision sur la poursuite du projet. »*
> **C13** : *« Créer une chaîne de livraison continue d'un modèle d'intelligence artificielle »*
> — volet **empaquetage**.

📎 **Fichiers** : [`../../Dockerfile`](../../Dockerfile) ·
[`../../docker-compose.yml`](../../docker-compose.yml) ·
[`../../.dockerignore`](../../.dockerignore) ·
[`../../requirements-api.txt`](../../requirements-api.txt)

**Date** : 2026-08-18

---

## Ce qui bloquait, et ce qui a débloqué

Ces deux critères étaient déclarés **non satisfaits** dans
[`preuve-specifications-techniques.md`](preuve-specifications-techniques.md) §6 : le
déploiement passait par Docker, dont le démon ne démarrait pas sur la machine.

**Docker a démarré le 18/08** (`Server 29.7.2`, linux, 8 CPU). Les deux critères, plus le
volet empaquetage de C13, ont été traités dans la foulée.

---

## 1. La pile

```
docker compose up -d --build
```

| Service | Image | Rôle |
|---|---|---|
| `postgres` | `postgres:18-alpine` | la base, schéma joué automatiquement |
| `api` | `rita-api:local` | l'API et l'interface, construites depuis le `Dockerfile` |

> ⚠️ **Corrigé le 20/08/2026** — c'était `postgres:17-alpine` lors de la mesure du 18/08.
> Le poste de développement tourne en **PostgreSQL 18.4** : un `pg_dump` du poste refusait
> de se restaurer dans un conteneur en 17, PostgreSQL ne garantissant pas la restauration
> vers une version **antérieure**. Défaut découvert en déployant réellement, pas en relisant
> le fichier. Aligné sur 18 dans les deux `docker-compose.yml`, testé en local avant le
> serveur.
>
> 🐛 **Le passage à 18 a révélé un second changement** : depuis la 18, l'image officielle
> range les données dans un **sous-dossier portant la version majeure** (pour permettre
> `pg_upgrade` sans franchir une frontière de montage). Le montage doit donc viser
> `/var/lib/postgresql` **sans** `/data` — sinon le conteneur refuse de démarrer, avec un
> message d'erreur qui explique précisément quoi faire.

### Sortie réelle

```
Container rita-postgres-preprod  Healthy
Container rita-api-preprod       Started

NAME                    STATE     STATUS
rita-api-preprod        running   Up 16 seconds (healthy)
rita-postgres-preprod   running   Up 22 seconds (healthy)
```

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     127.0.0.1:60888 - "GET /health HTTP/1.1" 200 OK
```

**Les 8 tables sont créées automatiquement** à la première création du volume :

```
alias_valeur · article · cotation · devise · memory_audit · position · taux_change · valeur
(8 rows)
```

---

## 2. Vérification fonctionnelle

| Contrôle | Résultat |
|---|---|
| `GET /health` (public) | `{"status":"ok","project":"RITA"}` |
| `/donnees/valeurs` **sans clé** | **403** |
| `/donnees/valeurs` avec **`dev-key`** | **403** ✅ *la correction OWASP API2 tient aussi en conteneur* |
| `/donnees/valeurs` avec la vraie clé | **200** |
| Interface servie | `http://localhost:8001/indicateurs.html` — page complète, navigation présente |

> Le port hôte est **8001**, pas 8000 : le serveur de développement occupe déjà 8000.
> Les deux tournent **en même temps**, ce qui permet de comparer développement et
> pré-production côte à côte.

---

## 3. 💎 Cinq choix de conception à défendre

### 1. Construction en deux étapes

`gcc` et `libpq-dev` sont nécessaires pour **bâtir** `psycopg2`, **pas pour l'exécuter**. Ils
restent dans l'étape de construction et n'entrent jamais dans l'image livrée : des centaines
de mégaoctets en moins transportés à chaque déploiement, et une surface d'attaque de moins.

### 2. `pyspark` n'est pas dans l'image — 492 Mo économisés

`pyspark` pèse **492 Mo** et n'est importé que dans `bigdata/session_spark.py`, à l'intérieur
d'une fonction. **L'API ne l'atteint jamais.**

D'où `requirements-api.txt`, sous-ensemble de `requirements.txt`. C'est le critère
**d'éco-conception de C15** appliqué là où il se mesure vraiment : un demi-gigaoctet
transféré, stocké et analysé à chaque déploiement, pour du code qui ne s'exécute pas.

**Vérifié dans le conteneur** : `pyspark : absent`.

Et les versions y sont **toutes épinglées**, relevées par `importlib.metadata` sur
l'environnement qui fait tourner les 245 tests — pas choisies au jugé. C'est la réponse
partielle au défaut OWASP ASI04 relevé par la veille S34 (*« allowlist and pin »*).

### 3. Utilisateur non privilégié

Par défaut, un conteneur s'exécute en **root** : une faille applicative donnerait alors les
pleins pouvoirs dans le conteneur.

```
uid=10001(rita) gid=10001(rita) groups=10001(rita)
```

### 4. Système de fichiers en lecture seule

L'application n'écrit nulle part. Une écriture inattendue doit donc **échouer**, pas persister.

```
touch /app/test-ecriture  →  Read-only file system   ✅
touch /tmp/ok             →  autorisé (tmpfs)        ✅
```

Plus `no-new-privileges` : un processus ne peut pas obtenir plus de droits que son parent.

### 5. La base n'est **pas** publiée vers l'hôte

Aucun `ports:` sur le service `postgres`. Deux raisons :

1. **Elle n'a pas à être joignable de l'extérieur** — seule l'API lui parle, par le réseau
   interne de Compose.
2. Cela évite tout conflit avec le PostgreSQL **installé nativement** sur la machine, qui
   écoute déjà sur 5433.

Pour l'inspecter : `docker compose exec postgres psql -U rita -d rita`.

### Et le secret le plus important : `.env` n'entre pas dans l'image

```
ls -a /app | grep "^\.env"  →  aucun .env dans l'image   ✅
```

`.dockerignore` l'écarte, ainsi que le CSV du portefeuille et les classeurs Excel.
*Une image poussée sur un registre est publique pour quiconque y a accès : embarquer un
`.env` est l'une des fuites de secrets les plus courantes.*

La clé est injectée **au démarrage**, et le compose refuse de partir sans elle :

```yaml
RITA_API_KEY: ${RITA_API_KEY:?RITA_API_KEY absente - la definir dans .env}
```

---

## 4. Conclusion de la preuve de concept — critère 5

**Avis : le projet peut se poursuivre sur cette architecture.** Ce n'est pas une formule ;
voici sur quoi cet avis s'appuie et ce qu'il ne couvre pas.

### Ce que la preuve de concept démontre

| Point | Constat |
|---|---|
| L'application s'empaquette | image construite, **595 Mo** |
| Elle démarre sans intervention | `healthy` en **moins de 20 s**, schéma de base joué seul |
| Elle est reproductible | dépendances épinglées, image reconstructible à l'identique |
| Elle est fonctionnelle hors de la machine de développement | 403/200 corrects, interface servie |
| Elle tourne durcie | non-root, lecture seule, sans privilèges supplémentaires |

### Ce qu'elle ne démontre pas — et qu'il faut dire

| Limite | Portée |
|---|---|
| **Pré-production locale**, pas distante | aucun hébergeur choisi ; le critère parle d'un environnement, pas d'un serveur public |
| **La base de pré-production est vide** | le schéma est créé, les 275 118 cotations ne sont pas importées. Un `docker compose exec api python -m db.importer` reste à jouer |
| **Aucun déploiement automatisé** | l'image se construit à la main. C'est le volet **livraison** de C13, encore ouvert |
| **595 Mo, c'est encore lourd** | `pandas` (35 Mo) et `yfinance` sont embarqués pour `agents/scout.py`. Une image `slim` plus stricte, ou l'extraction du scout, la réduiraient |

### La décision

**Poursuivre.** Le point qui restait douteux — *l'application tourne-t-elle ailleurs que sur
la machine d'Era ?* — est tranché : oui, en moins de vingt secondes, sans intervention
manuelle. Les limites ci-dessus sont des **travaux restants**, pas des impasses.

---

## 5. Ce que cela change pour C13

Le volet **empaquetage** de C13 est fait : l'application est conteneurisée, l'image se
construit et tourne.

**Reste ouvert** : la construction et la publication de l'image **par la chaîne
d'intégration continue**, et le déploiement lui-même. Aujourd'hui GitHub Actions exécute les
tests et les évaluations — c'est de l'intégration continue, pas de la livraison continue.

---

## 6. 📖 Glossaire

| Terme | En clair |
|---|---|
| **Conteneur** | Un programme empaqueté avec tout ce qu'il lui faut pour tourner |
| **Image** | Le modèle figé dont on lance des conteneurs |
| **Dockerfile** | La recette de construction d'une image |
| **Compose** | Outil qui lance plusieurs conteneurs ensemble et les fait se parler |
| **Construction en deux étapes** (*multi-stage*) | Bâtir dans une image, ne recopier que le résultat dans l'image finale |
| **`.dockerignore`** | Liste de ce qui n'entre pas dans l'image — l'équivalent du `.gitignore` |
| **Healthcheck** | Commande périodique qui dit si le service répond vraiment |
| **`service_healthy`** | Attendre qu'un service réponde, et non qu'il soit simplement démarré |
| **root** | L'utilisateur tout-puissant d'un système Unix |
| **Lecture seule** (*read-only*) | Le conteneur ne peut rien écrire sur son disque |
| **tmpfs** | Un dossier en mémoire vive, effacé à l'arrêt |
| **`no-new-privileges`** | Interdit à un processus d'obtenir plus de droits que son parent |
| **Volume** | Espace de stockage qui survit à la suppression du conteneur |
| **Épingler** (*pin*) | Figer la version exacte d'une bibliothèque |
| **Pré-production** | Environnement identique à la production, pour valider avant livraison |
| **Intégration continue** | Les tests tournent à chaque envoi de code |
| **Livraison continue** | L'étape d'après : empaqueter et déployer automatiquement |

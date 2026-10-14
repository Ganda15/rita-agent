# RITA : conception du sprint 2, le socle et la chaîne

> Fil rouge, phase 6, sprint 2. Conception validée section par section les 13 et 14/10/2026 ; aucun code écrit.
> Ce dossier prolonge le cadrage V1 (`docs/CADRAGE-V1.md`, § 2 jours 1 et 2, § 6 critère 5, § 7) et la chaîne
> conçue dans le chapitre « Industrialisation » (§ 5). Il ne change qu'une décision de ce chapitre : la livraison
> sur le serveur devient automatique après chaque fusion sur `main`, comme l'exige le brief du sprint 2.

## 1. Objectif et critères

**Objectif.** Une fusion sur `main` livre en production, sans action manuelle, l'image exacte qui a passé les
contrôles ; un commit cassé est arrêté ; la version précédente revient en une opération ; aucun secret n'est dans le
dépôt et l'environnement se reconstruit depuis le dépôt.

| # | Critère de la grille de l'atelier n°2 | Où ce dossier y répond |
|---|---|---|
| 1 | Ça tourne ailleurs : le squelette en marche sur l'URL de production | § 4, § 7 |
| 2 | Livraison automatique : une fusion déclenche tests, build et déploiement | § 3, § 4 |
| 3 | Un échec bloque : le commit volontairement cassé est arrêté, en direct | § 7 |
| 4 | Rollback : retour à la version précédente, en une opération | § 5 |
| 5 | Secrets et reproductibilité | § 6 |
| J | Journal des retours de l'atelier n°1 | § 7 |

Le contrat personnel du cadrage ajoute le **critère 5** : « Étant donné la version N en production et N-1 taguée,
quand un tiers suit la procédure de retour arrière, alors `/health` annonce N-1 en moins de 10 minutes. »

## 2. L'existant, mesuré les 13 et 14/10/2026

| Sujet | Constat | Source |
|---|---|---|
| Production | `https://178-104-184-125.sslip.io`, serveur Hetzner, Caddy installé sur l'hôte (il sert aussi Sorabel) ; dépôt dans `/root/rita-agent`, mis à jour à la main (`git pull`, `docker compose`) | `ETAT.md` l. 1595 ; `CONTINUITE.md` l. 496 |
| Code servi | commit `1cefdae` (20/08/2026), à confirmer sur le serveur | `evidence/C13/preuve-chaine-livraison-2026-10-03.md` § 4 |
| Réponses de la production | `/health` 200 `{"status":"ok","project":"RITA"}` sans version ; `/` 200 ; `/briefing.html` 404 | `curl`, 14/10 |
| Image en production | construite sur le serveur (`build:`, `image: rita-api:local`), conteneurs `rita-api-preprod` et `rita-postgres-preprod`, port 8001 | `docker-compose.yml` |
| Chaîne | `test.yml` (`pytest`, `evals`), `livraison.yml` (`construire-et-publier` : tests, construction, démarrage, `/health`, 403 ; publication seulement sur un tag `livrable-*`, jamais exécutée), `revue-pr.yml` (`revue`) | `.github/workflows/` ; passage du 11/10 : « skipped : Publier l'image vérifiée » |
| Checks requis sur `main` | `pytest`, `evals`, `revue` | ruleset « main protegee », relu le 14/10 |
| Durée d'un passage | de 2 min 23 s à 3 min 13 s (dix derniers passages verts) | `gh run list`, 14/10 |
| Lint | aucun | `grep` des workflows |
| Déploiement et retour arrière | aucun déploiement automatique, aucun retour arrière outillé | `evidence/C13/...` § 4 ; `docs/CI-CD.md` § 8 |
| Secrets | `.gitignore` et `.dockerignore` excluent `.env` et `.env.*` sauf `.env.example` ; seul `.env.example` est suivi (18 variables, valeurs d'exemple) ; hook `.claude/hooks/bloquer-secrets.py` ; aucun contrôle de l'historique ni de l'image | `git ls-files` ; `.dockerignore` l. 8-10 |
| Base neuve | `docker compose up` crée un schéma à jour (`db/schema.sql` contient les migrations du 03/10) mais une base vide ; l'importateur des cours ne lit que l'archive Parquet, `pyarrow` n'est pas dans l'image | `EXPLOITATION.md` § 3 ; `db/importer.py` l. 109-117 |
| Rôle en lecture seule | `rita_lecture` (`SELECT` seulement), joué sur la base Hetzner le 03/10 ; l'application lit `DATABASE_URL` | `db/roles.sql` l. 17-23 ; `ETAT.md` l. 547 ; `sources/database.py` l. 172 |

**Ce que sait faire l'image d'août (`1cefdae`).** `POST /briefing` avec `conforme_amf`, le 403 sans clé, les écrans
`index.html` et `indicateurs.html`. Elle n'a ni version dans `/health`, ni `briefing.html`, ni `X-Request-ID`, ni
Chroma. Elle appelle Azure par `AnthropicFoundry` (`src/llm.py` l. 7 et 20 au commit `1cefdae`), alors que le code
actuel passe par un point compatible OpenAI (`src/llm.py` l. 3 et 53).

**Codes d'erreur du briefing.** Un 502 vient du champ `error` du graphe, par exemple une valeur absente de la base
(`agents/scout.py` l. 51, `api/main.py` l. 226-229). Si tous les fournisseurs du modèle échouent, `generer_texte` lève
une exception (`src/llm.py` l. 156) et le middleware répond 500 avec son `X-Request-ID` (`api/main.py` l. 96-105).

## 3. La chaîne, étape par étape

| # | Étape (chapitre Industrialisation § 5.1) | Décision pour le sprint 2 |
|---|---|---|
| 0 | Avant la fusion : PR vers `main`, revue, hook `pre-push` | inchangé |
| 1 | Contrôles : lint, tests et couverture ≥ 90 %, portes d'évaluation | ajouter `lint` et `secrets` (§ 6, § 7) ; le contrôle `reconstruction` dans la chaîne vient après l'atelier (§ 11) |
| 2-3 | Filtre de chemins, porte d'évaluation sur le vrai modèle | hors V1 (cadrage § 2) |
| 4 | Version | l'image porte `sha-<commit court>` (lisible) et son empreinte `sha256:…` (immuable) ; `/health` annonce le commit et la date de construction ; le numéro `vX.Y.Z` est reporté, son calcul dépendant du filtre de chemins |
| 5 | Construction et publication | après chaque fusion sur `main`, et plus seulement sur un tag `livrable-*` |
| 6 | Livraison sur le serveur | **automatique après la fusion** (§ 4) |
| 7 | Retour arrière | workflow manuel `retour-arriere.yml` (§ 5) |

Règles reprises du chapitre (§ 5.3) : aucun secret dans l'image ; clés dans le `.env` du serveur et dans les secrets
GitHub ; aucune livraison entre 8 h et 9 h (le retour arrière d'urgence reste permis à toute heure ; les démonstrations
se font hors de ce créneau) ; changements compatibles avec les versions conservées (§ 5.5 ci-dessous) ; pas de
déploiement progressif (un seul utilisateur).

## 4. La livraison automatique

1. **Déclencheur.** La fusion d'une PR dans `main`. Les contrôles de l'étape 1 tournent, puis la construction, le
   démarrage de l'image, `/health` et le 403.
2. **Publication sur GHCR** de l'image vérifiée, avec `sha-<commit court>` et son empreinte.
3. **Travail `deployer`**, rattaché à l'environnement GitHub `production` : il ne part que sur `main` et seulement si
   tous les travaux précédents sont verts ; aucun relecteur obligatoire (la relecture a lieu dans la PR) ; un seul
   déploiement à la fois (`concurrency`, `cancel-in-progress: false`), pour qu'une nouvelle livraison n'interrompe
   jamais une bascule commencée. Chaque déploiement figure dans l'onglet *Deployments* du dépôt.
4. **Connexion au serveur** par SSH, avec une clé dédiée à commande forcée : elle ne peut lancer que
   `deploy/deployer.sh`, qui appelle `deploy/deployer.py` (Python, testé par pytest), tous deux installés par Era dans
   `/root/rita-deploy/bin/`. Le script n'accepte que trois ordres : `livrer <image>@sha256:<64 caractères
   hexadécimaux>`, `revenir <numéro de passage>` et `version` (l'empreinte du script, comparée par la chaîne à celle du
   dépôt avant chaque opération). Il prend un verrou commun au déploiement et au retour arrière, et écrit une marque
   « opération commencée » avant toute bascule. L'image embarque ses fichiers de déploiement (`docker-compose.yml`,
   `deploy/compose.prod.yml`) : le script les en extrait, si bien qu'une empreinte désigne à la fois le code et sa
   configuration. Limite : une nouvelle version du script lui-même se recopie à la main.
5. **Pré-test**, à côté de la production, sur `127.0.0.1:8002` : la nouvelle image se connecte avec `DATABASE_URL`
   réglée sur `rita_lecture` (valeur `RITA_DSN_LECTURE` du `.env` du serveur) et construit son propre index Chroma
   dans un volume temporaire, avec la commande existante `python -m pipelines.ingest --etapes indexation --strict`.
   Elle doit réussir : `/health` à la version attendue ; 403 sans clé ; un briefing `OR.PA` en 200, avec un texte non
   vide, `conforme_amf: true`, et son `X-Request-ID` retrouvé dans la ligne de journal « briefing servi ». La ligne
   « Réponse obtenue via … » (`src/llm.py` l. 143) indique le fournisseur ; Langfuse le confirme quand les traces sont
   actives (`src/traces.py` l. 270-276). Le pré-test ne peut pas écrire dans PostgreSQL et utilise son propre index ;
   il partage encore le serveur et la base consultée avec la production.
6. **Pré-test en échec** : le conteneur de test est arrêté, le travail échoue, la production ne change pas.
7. **Pré-test réussi** : contrôle de l'heure (fuseau Europe/Paris) juste avant la bascule. L'attente de 9 h se fait
   dans GitHub, avant le déploiement, hors du verrou du serveur et du groupe de concurrence ; si le créneau est
   atteint pendant le pré-test, la livraison est annulée proprement, puis **reprend automatiquement à 9 h avec la
   même empreinte**, sans action manuelle et sans bloquer un retour arrière. Remplacement du conteneur de production par l'empreinte (quelques secondes de
   coupure), puis **contrôles d'après bascule** avec la configuration réelle de production : `/health` annonce la
   nouvelle version ; `/briefing.html` répond 200 ; 403 sans clé ; un briefing `OR.PA` en 200 avec un texte non vide,
   `conforme_amf: true` et son `X-Request-ID` dans le journal. En échec : retour automatique (§ 5.2).
8. **Journal du serveur** : une ligne par opération (date, empreinte d'avant, empreinte d'après, résultat) ; mise à
   jour de l'état (§ 5.3).

Une livraison fait deux demandes de briefing en fonctionnement nominal (pré-test et après bascule). Les tentatives de
secours et les contrôles après un retour peuvent en ajouter ; leur coût dépend du fournisseur.

## 5. Le retour arrière

### 5.1 Deux temps

**Première livraison (N0), qui remplace l'image d'août.** N0 est la première version livrée par la chaîne : le
code gelé du 15/10, plus les changements du sprint 2, dont la version dans `/health`, absente aujourd'hui
(`api/main.py` l. 199-201). Avant la bascule :

- relever l'image réellement exécutée par `rita-api-preprod` et sa configuration effective (noms de variables
  seulement) ;
- garder l'image d'août : étiquette locale `rita-api:avant-chaine` et fichier `docker save` sur le disque, qui
  survit à tout nettoyage ;
- garder sa configuration : copie du `.env` et du `docker-compose.yml` en service dans un dossier de sauvegarde du
  serveur, et sauvegarde `pg_dump` de la base ;
- vérifier qu'on sait la recréer : une API seule (`docker run`, autre nom, port 8002) avec cette configuration, et son
  propre profil de contrôles (`/health` 200, `/` 200, 403 sans clé, briefing `OR.PA` en 200 avec un texte non vide et
  `conforme_amf: true`), qui dit aussi quel fournisseur répond.

Si l'image d'août ne sait plus produire de briefing, son secours est dégradé : **la décision de faire la première
bascule malgré tout revient à Era**, explicitement, avant le déploiement.

**Exception, décidée le 14/10 pour l'atelier (§ 11) :** le retour vers l'image d'août n'est **pas automatisé**. Si N0
échoue après la bascule, la chaîne s'arrête en rouge avec le message « restauration manuelle d'août requise », et Era
restaure août par la procédure manuelle, testée avant toute modification du serveur. Le retour automatique et le
retour manuel par la chaîne ne couvrent donc pas encore cette toute première livraison ; ils couvrent toutes les
suivantes (N1 vers N0, etc.).

**Démonstration du sprint 2.** N0 en service, N1 livrée par la chaîne, puis retour N1 vers N0 : deux versions qui
annoncent leur commit et passent les mêmes contrôles.

### 5.2 La cible de chaque retour

- **Retour automatique** (livraison en échec) : la version **active au début de l'opération**, avec sa configuration.
  Avec active A, précédente B, candidate C : si C échoue, A revient.
- **Retour manuel** : la **précédente validée** (B), par GitHub, onglet *Actions*, workflow `retour-arriere.yml`,
  *Run workflow*, avec le nom et le motif (comme `rollback.yml` de Mardik v2). Le nom et le motif restent dans GitHub ;
  le serveur ne reçoit que le numéro du passage. Le retour est permis à toute heure ; il a son propre groupe de
  concurrence et utilise le script déjà installé, même si le dépôt en contient une version plus récente. Secours si
  GitHub est indisponible : la même commande lancée sur le serveur, écrite dans `docs/EXPLOITATION.md`.

### 5.3 L'état enregistré

Trois informations distinctes : les **versions validées** (`active`, `precedente`), écrites seulement après des
contrôles réussis ; la **version observée** (lue dans Docker à la fin de chaque opération) ; la **santé** (*sain* : tout
passe ; *dégradé* : `/health` répond mais un contrôle du parcours échoue ; *indisponible* : `/health` ne répond pas).
L'état s'écrit de façon atomique (fichier temporaire puis renommage) ; un journal reçoit une ligne par opération.

| Situation | Versions validées | Observée | Santé | Travail GitHub |
|---|---|---|---|---|
| Livraison de C réussie | active C, précédente A | C | sain | vert |
| C échoue, A restaurée | inchangées (A, B) | A | sain | rouge : « livraison refusée, A restaurée » |
| C échoue, A échoue aussi | inchangées | celle que Docker montre, éventuellement aucune | dégradé ou indisponible | rouge : « restauration en échec, intervention nécessaire » |
| Retour manuel vers B réussi | active B, précédente vide | B | sain | vert |
| Retour manuel vers B raté | inchangées ; A remise | A, ou celle que Docker montre | selon les contrôles | rouge : « retour refusé » |
| Retour demandé, précédente vide | inchangées | inchangée | inchangée | rouge : « aucune version précédente » |
| Opération interrompue | inchangées | à relire | à recontrôler | l'opération suivante trouve la marque non fermée, vérifie l'état réel et s'arrête avant toute livraison, avec renvoi à la procédure d'`EXPLOITATION.md` |

Quand deux versions échouent au même contrôle, le message est : « cause externe possible (modèle, base) ou
configuration commune incorrecte, à diagnostiquer ». Un seul niveau de retour : après un retour manuel, `precedente`
est vidée, si bien que deux retours successifs ne réinstallent jamais la version qu'on vient de quitter.

### 5.4 La conservation des images

Aucun `docker image prune -a` dans les scripts (il efface aussi les images étiquetées qu'aucun conteneur n'utilise).
Le nettoyage ne touche que les images RITA absentes de la liste à garder (active, précédente, candidate en cours), et
seulement après une opération validée ; il ne touche jamais les autres images du serveur. Une image effacée
localement, mais conservée dans GHCR, se retélécharge par son empreinte : l'empreinte identifie l'image, elle ne
remplace pas sa conservation. L'image d'août est protégée par son fichier `docker save`. **Après l'atelier (§ 11)** :
ce nettoyage automatique ; d'ici là, le nettoyage se fait à la main, avec la même règle, par la procédure écrite dans
`docs/EXPLOITATION.md`.

### 5.5 La compatibilité

Les changements doivent rester compatibles avec les versions conservées.

- **PostgreSQL** : une colonne nouvelle accepte le vide ou a une valeur par défaut ; rien n'est renommé ni supprimé
  tant qu'une version qui s'en sert peut revenir.
- **Configuration** : des variables ajoutées, jamais renommées ni retirées tant qu'une version qui les lit peut
  revenir.
- **Chroma** : `chromadb==1.5.9` est conservé pour N0 et N1 (`requirements-api.txt` l. 43). L'index se déduit des
  articles de PostgreSQL ; l'indexation complète l'index existant (`get_or_create_collection`, `rag/indexation.py`
  l. 248-249) et ne le recrée pas. Toute reconstruction utilise l'image cible et un volume neuf, vérifié avant usage.
- **Vérification** : le retour N1 vers N0 fait tourner l'ancienne version sur le schéma actuel. Le rappel dans
  chaque PR qui touche `db/` (modèle de PR) vient **après l'atelier** (§ 11).
- **Limite** : `pg_dump` ne sauvegarde que PostgreSQL ; la sauvegarde initiale ne suffit pas seule à restaurer RITA
  (il faut aussi la copie de la configuration et la reconstruction de l'index).

## 6. Les secrets et la reconstruction

### 6.1 Les secrets

- **Travail `secrets`**, check requis : gitleaks dans une version fixée, par son image Docker, sur l'historique complet
  (`fetch-depth: 0`), avec ses règles par défaut et les valeurs masquées (`--redact`). Les exceptions, dans
  `.gitleaks.toml`, se limitent aux faux positifs constatés (par exemple les fausses clés de test de
  `livraison.yml`), chacune avec sa raison. Aucune absence de fuite n'est annoncée avant le premier passage ; une vraie
  clé trouvée est révoquée et remplacée.
- **Contrôle de l'image**, ajouté à la vérification de `livraison.yml` : aucun fichier `/app/.env` dans l'image (ce
  chemin seulement), et aucun `ARG` ni `ENV` portant un secret dans le `Dockerfile`, lignes continuées comprises. La
  preuve énonce exactement ces deux vérifications et leur limite.
- **Où vit chaque secret** : tableau de `docs/EXPLOITATION.md` § 2, complété par `DEPLOY_SSH_KEY`, `DEPLOY_HOST`,
  `DEPLOY_KNOWN_HOSTS` (environnement `production` de GitHub), le jeton GHCR en lecture seule, le `.env` du serveur
  (dont `RITA_DSN_LECTURE`) et sa copie de sauvegarde. La clé SSH dédiée se révoque en retirant une ligne sur le
  serveur.
- **Limites** : `docker login` range le jeton GHCR dans `/root/.docker/config.json`, encodé, non chiffré ; les droits
  des fichiers `.env` du serveur sont à vérifier.

### 6.2 La reconstruction depuis le dépôt

- **Jeu de démonstration versionné** (`data/demo/`) : quelques valeurs dont `OR.PA`, quelques mois de cours réels
  extraits de la base du poste avec leurs dates exactes, des articles marqués « démonstration, contenu synthétique »,
  et les positions de démonstration (ligne VIRI.PA corrigée avant d'entrer dans le jeu).
- **Mode « démonstration » de l'importateur existant** (`db/importer.py`), à côté du mode Parquet : il refuse une base
  qui contient déjà d'autres données, et une deuxième exécution ne crée ni doublon ni modification.
- **Service `initialisation`** dans `docker-compose.yml` (même image, profil `outils`, fichiers du jeu montés en
  lecture seule) : chargement du jeu, puis indexation.
- **Formulation** : jeu de données autonome, sans appel aux sources de marché ; accès réseau nécessaire aux
  téléchargements initiaux (images Docker, modèle d'embeddings) et au modèle distant. Le jeu prouve la reconstruction
  et le fonctionnement, pas la fraîcheur des données de production.
- **Pour l'atelier, la reconstruction est montrée en direct**, avant la première livraison, par la procédure écrite
  dans `docs/EXPLOITATION.md` § 3.
- **Après l'atelier (§ 11) : le travail `reconstruction`** dans la chaîne, alors check requis et condition du
  déploiement : sur une machine neuve de la chaîne, dépôt vide, volumes neufs, `docker compose up`, `initialisation`,
  puis contrôle des routes de données et du nombre d'articles indexés. Le briefing en est exclu (la chaîne n'a pas de
  clé du modèle) ; le pré-test de production le couvre. Tant qu'il n'existe pas, il ne figure ni dans les travaux
  qu'attend `deployer`, ni dans les checks requis.
- Une reconstruction en direct sur le poste utilise un projet Compose distinct (`-p rita-demo`) et un
  fichier de surcharge qui renomme les conteneurs (leurs noms sont fixes dans `docker-compose.yml`) ; les volumes,
  préfixés par le nom du projet, sont alors neufs. Arrêter la pile locale ne suffirait pas : les volumes survivent à
  l'arrêt et à la suppression des conteneurs.
- La base de production garde ses données : les livraisons ne touchent pas à ses volumes. L'archive de dix ans reste
  hors du dépôt.

## 7. Un échec bloque, preuves et démonstration

### 7.1 Le blocage

- **Checks requis sur `main`** : `lint`, `pytest`, `evals`, `revue`, `secrets`, `construire-et-publier`. La règle
  « main protegee » est modifiée en conséquence. `reconstruction` s'y ajoutera quand le travail existera (§ 11).
- **Deux verrous** : la règle refuse la fusion ; dans la chaîne de `main`, `deployer` ne part que si tous les travaux
  précédents sont verts.
- **Lint** : `ruff`, d'abord limité aux erreurs réelles (syntaxe, noms non définis), élargi ensuite ; le nombre
  d'alertes sur le code actuel est mesuré avant de fixer les règles.
- **Commit cassé de démonstration** : branche `demo/commit-casse`, qui fait échouer exprès un test simple, hors des
  zones sous garde (`AGENTS.md` l. 52-53 : `guardrails/`, `evals/` et `db/schema.sql` exigent un plan écrit et
  validé avant toute modification) ; PR vers `main` ; refus par `pytest`, déterministe (la `revue` automatique ne
  l'est pas). On montre le check rouge, la fusion bloquée, l'onglet *Deployments* inchangé et `/health` toujours sur N1.
  La PR est ensuite fermée sans fusion et la branche supprimée.

### 7.2 Livrables et preuves

- `docs/sprint-2/README.md` : document d'entrée (adresse de production, version servie, lien vers chaque preuve).
- `evidence/sprint-2/` : captures (PR bloquée, *Deployments*, `/health` avant et après), extraits de
  `gh run view --log` aux valeurs masquées, lignes du journal du serveur.
- `eval/ateliers/sprint-2-grille.md` : grille vierge copiée avant l'atelier, puis remplie, avec la suite donnée à
  chaque remarque.
- Journal des retours de l'atelier n°1 : conseil sur MCP traité (`docs/CADRAGE-V1.md` § 5, commit `bc143c3`) ;
  remarque « mal à communiquer » : phrases courtes, ligne montrée à l'écran.

### 7.3 Déroulé de la démonstration (2 minutes de journal, puis 20 minutes)

| Minute | Geste | Critère |
|---|---|---|
| 0-2 | Journal des retours | J |
| 2 | Ouverture de la PR cassée ; son résultat arrive pendant la suite | 3 |
| 3-7 | Adresse de production : écran de briefing, vrai briefing, `/health` qui annonce N1 | 1 |
| 7-10 | Journal de chaîne de la livraison de N1 : fusion `develop → main`, travaux, *Deployments* | 2 |
| 10-12 | La PR cassée : rouge, fusion bloquée, production inchangée | 3 |
| 12-16 | Retour arrière en direct, puis `/health` qui annonce N0 | 4 |
| 16-19 | Passage de `secrets`, `git ls-files`, tableau des secrets, fiche INC-008 | 5 |
| 19-22 | Reconstruction en direct dans un dossier neuf | 5 |

La durée complète d'une livraison est à mesurer ; la livraison de N1 est donc montrée par son journal, et les deux
gestes en direct sont le blocage et le retour arrière. Après la démonstration, N1 est remise en service en relançant
le travail `deployer` de son passage (même empreinte) ; ce geste, dont la durée réelle sera mesurée, n'entre pas dans
les 20 minutes.

## 8. Hors du sprint 2

Le numéro `vX.Y.Z`, le filtre de chemins, la porte d'évaluation sur le vrai modèle, les alertes Telegram, la route
`/v1`, le nom du fournisseur dans la réponse du briefing, la fraîcheur des données de production, l'archive de dix
ans dans le dépôt, tout déploiement progressif.

## 9. À vérifier pendant la construction, et décisions réservées

**À vérifier**, chaque fois avec la commande et sa sortie :

1. l'image réellement exécutée sur le serveur et sa configuration effective (noms de variables seulement) ;
2. l'essai de l'image d'août en API seule, et le fournisseur qui lui répond ;
3. le mot de passe de `rita_lecture` sur le serveur, et le démarrage de l'API avec ce compte ;
4. la disponibilité du port 8002 ;
5. la présence des clés Langfuse sur le serveur ;
6. l'authentification SSH par clé seulement ;
7. les droits des fichiers `.env` du serveur ;
8. les durées : indexation de test, livraison complète, retour arrière (moins de 10 minutes visées) ;
9. le nombre d'alertes `ruff` sur le code actuel ;
10. le premier passage de gitleaks sur l'historique.

**Décisions réservées à Era** : la première bascule si le secours d'août est dégradé ; la modification de la règle
« main protegee » ; la création et la saisie de chaque clé et de chaque jeton.

## 10. Calendrier et verrous

- Aucune ligne de code avant la validation du sprint 1 par le formateur (brief du sprint 1).
- Aucune fusion sur `develop` avant le tag du jeudi 15/10. Le code gelé du 15/10 est la référence de départ
  (cadrage V1, § 2, jour 1) ; N0 y ajoute les changements du sprint 2.
- La branche `sprint-2-socle-chaine` part de `sprint-1-cadrage`. La PR du sprint 1 vers `develop` se fusionne par un
  commit de fusion, sans écrasement des commits ; en cas d'écrasement, la branche du sprint 2 est réalignée, pour que
  sa PR ne reprenne pas les changements du sprint 1.
- La date de l'atelier n°2 reste à connaître.

## 11. Périmètre de l'atelier n°2 (décision d'Era du 14/10/2026)

Le formateur l'a précisé le 14/10 : pas de présentation à construire ; l'évaluateur regarde chaque élément du brief et
la façon dont il est réalisé ; la chaîne « pas forcément complète », mais avec tests bloquants, construction,
déploiement automatique et retour arrière. Chaque élément est donc classé selon la preuve qu'il apporte.

**Gardé pour l'atelier** : tout ce que demande le brief ; la préproduction (pré-test), qui porte « à travers les
environnements » ; le créneau de 8 h, règle de RITA, avec le retour d'urgence permis à toute heure ; le contrôle
`/app/.env` ; la sauvegarde d'août et sa restauration manuelle testée avant toute modification du serveur ; deux
répétitions du retour arrière (une par Era, une par un tiers, chronométrée).

**Reporté après l'atelier**, sans être retiré de cette conception :

| Élément | Ce qui change d'ici là |
|---|---|
| Le travail `reconstruction` dans la chaîne (§ 6.2) | absent des travaux qu'attend `deployer` et des checks requis ; la reconstruction est montrée en direct |
| Le nettoyage automatique des images (§ 5.4) | nettoyage à la main, même règle |
| L'automatisation du retour vers l'image d'août (§ 5.1) | exception explicite : restauration manuelle testée pour la seule première livraison |
| Le modèle de PR qui rappelle la compatibilité (§ 5.5) | rappel fait à la main dans la PR qui toucherait `db/` |

**Ordre des tâches** (plan `docs/sprint-2/PLAN-TRAVAIL.md`) : 1 à 3 (faites), puis 7 à 10, puis 4 à 6
(reconstruction montrée avant la première livraison), puis une relecture indépendante de toute la branche, puis 11
et 12.

## Fichiers concernés (prévus)

`.github/workflows/livraison.yml`, `.github/workflows/retour-arriere.yml` et
`.github/actions/ordre-serveur/action.yml` (nouveaux), `deploy/deployer.py`,
`deploy/deployer.sh` et `deploy/compose.prod.yml` (nouveaux), `docker-compose.yml`, `docker-compose.demo.yml`
(nouveau), `Dockerfile`, `.coveragerc`, `api/main.py` (`/health`), `db/importer.py`, `data/demo/` (nouveau),
`scripts/extraire_jeu_demo.py` et `scripts/verifier_dockerfile.py` (nouveaux), `.gitleaks.toml` et `ruff.toml`
(nouveaux), `.github/pull_request_template.md` (nouveau), `docs/EXPLOITATION.md`, `docs/CI-CD.md`,
`docs/sprint-2/README.md`, `evidence/sprint-2/`, `eval/ateliers/sprint-2-grille.md`, et les tests associés. Le
détail, tâche par tâche, est dans `docs/sprint-2/PLAN-TRAVAIL.md`.

## Glossaire

- **Check requis** : contrôle qui doit être vert pour que GitHub autorise une fusion dans `main`.
- **Clé à commande forcée** : clé SSH qui ne peut lancer qu'une commande, fixée sur le serveur.
- **Contrôles d'après bascule** : vérifications faites sur la production réelle juste après le remplacement.
- **Empreinte (*digest*)** : identifiant `sha256:…` calculé sur le contenu d'une image ; il ne désigne qu'elle.
- **Environnement GitHub** : étiquette (ici `production`) qui porte ses propres secrets et l'historique des
  déploiements.
- **Écriture atomique** : écriture dans un fichier temporaire puis renommage ; le fichier final est entier ou
  inchangé.
- **GHCR** : registre d'images de GitHub.
- **gitleaks** : outil qui cherche des secrets dans le code et l'historique Git.
- **Jeu de démonstration** : petites données versionnées qui suffisent au parcours.
- **Pré-test** : contrôle de la nouvelle version, à côté de la production, avant qu'elle ne serve.
- **Profil de contrôles** : liste de contrôles adaptée à ce que sait faire une version.
- **`rita_lecture`** : compte PostgreSQL qui ne peut que lire.
- **Version observée** : version que Docker exécute réellement sur le serveur.
- **N0, N1** : première version moderne livrée, puis la suivante.

## Sources

- Brief et grille du sprint 2 : `grille-atelier-2-socle-chaine-6acc929e15319714116731.pdf`.
- `docs/CADRAGE-V1.md` (branche `sprint-1-cadrage`, commit `e70ca58`), § 2, § 6, § 7.
- Chapitre « Industrialisation » de RITA, § 5 (chaîne MLOps) et § 6.
- `evidence/C13/preuve-chaine-livraison-2026-10-03.md`, `docs/CI-CD.md`, `docs/EXPLOITATION.md`, `ETAT.md`,
  `CONTINUITE.md`.
- Code cité : `api/main.py`, `src/llm.py`, `src/traces.py`, `agents/scout.py`, `rag/indexation.py`,
  `db/importer.py`, `db/roles.sql`, `sources/database.py`, `docker-compose.yml`, `.dockerignore`, requirements.
- Mardik v2 : `.github/workflows/rollback.yml` (`D:\KandaWork\CODE_PROJECTS\mardik-api-mlops_v2`).

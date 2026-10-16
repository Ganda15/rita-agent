# Préparation du serveur pour l'ingestion (tâche B5, 16/10/2026)

Plan de travail `docs/sprint-3/PLAN-TRAVAIL.md`, tâche B5. Commandes lancées par Era sur le serveur (Hetzner,
`ubuntu-4gb-fsn1-1`), le 16/10/2026 entre 15 h 27 et 15 h 47 UTC. Aucun mot de passe n'apparaît dans ce document : les
saisies se sont faites sans affichage (`\password`, `read -rs`), et les lignes du `.env` sont relues masquées.

## Étape 1 : le compte `rita_ingestion` (base de production, conteneur `rita-postgres-preprod`)

Comptes avant l'opération :

```text
   rolname    | rolsuper | rolcanlogin
--------------+----------+-------------
 rita         | t        | t
 rita_lecture | f        | t
```

Création et droits, dans une seule commande arrêtée à la première erreur (`ON_ERROR_STOP=1`) :

```text
CREATE ROLE rita_ingestion LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT   -> CREATE ROLE
GRANT CONNECT ON DATABASE rita TO rita_ingestion                                -> GRANT
GRANT USAGE ON SCHEMA public TO rita_ingestion                                  -> GRANT
GRANT SELECT, INSERT ON article TO rita_ingestion                               -> GRANT
GRANT USAGE ON SEQUENCE article_id_seq TO rita_ingestion                        -> GRANT
```

Les droits correspondent à ce que fait réellement l'étape de collecte RSS (`pipelines/ingest.py`, `etape_articles`) :
lire `article` pour le dédoublonnage, y ajouter des lignes. Ni `UPDATE`, ni `DELETE`, aucune autre table.

Mot de passe donné par `\password rita_ingestion` (une première tentative a échoué sur « Passwords didn't match » :
rien n'avait été enregistré). Contrôles :

```text
    rolname     | a_un_mot_de_passe
----------------+-------------------
 rita_ingestion | t

 table_name | privilege_type
------------+----------------
 article    | INSERT
 article    | SELECT
```

## Étape 2 : `RITA_DSN_INGESTION` dans `/root/rita-agent/.env`

Ligne ajoutée par `read -rs` (mot de passe tapé sans affichage), sur le modèle du compte de lecture. Relue masquée :

```text
RITA_DSN_LECTURE=postgresql://rita_lecture:***@postgres:5432/rita
RITA_DSN_INGESTION=postgresql://rita_ingestion:***@postgres:5432/rita
```

Connexion réelle avec le mot de passe de la ligne, par TCP (`-h 127.0.0.1`), ce qui force la vérification du mot de
passe :

```text
  current_user  | articles
----------------+----------
 rita_ingestion |     2052
```

## Étape 4 : le dossier des manifestes et des rapports de rejeu

`/root/rita-deploy/rapports`, créé puis donné à l'utilisateur de l'image (UID 10001) :

```text
drwxr-xr-x 2 10001 10001 4096 Oct 16 15:45 /root/rita-deploy/rapports
```

Essai d'écriture depuis l'image en production
(`ghcr.io/ganda15/rita-api@sha256:086fed50dd3402a4bd5f5a8a03fed326e6223c4f00ef1adf21c253da7b6b7f7e`), dossier monté
sur `/app/logs` comme pendant une ingestion, avec `set -e` :

```text
10001
-rw-r--r-- 1 rita rita 0 Oct 16 15:47 /app/logs/essai-ecriture
ECRITURE_OK
```

Le fichier d'essai a été supprimé ; le dossier est vide.

**Erreur relevée pendant l'opération** : un premier essai, lancé avant le `chown`, a échoué (`Permission denied`) mais
a quand même affiché `ECRITURE_OK`, parce que la commande enchaînait les étapes avec `;` sans s'arrêter à l'échec. Le
test a été corrigé avec `set -e` : `ECRITURE_OK` ne s'affiche plus que si l'écriture a réussi.

## Reste de la tâche B5

Étape 3 : installer le nouveau `deploy/deployer.py` sur le serveur, après la PR vers `develop` et avant la fusion dans
`main` (la livraison compare l'empreinte du script installé à celle du dépôt).

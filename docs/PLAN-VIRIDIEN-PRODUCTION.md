# Plan : corriger Viridien en production

**Statut** : à valider par Era. **Aucune écriture sur le serveur avant son accord**, donné séparément pour chaque opération.
Écrit le 04/11/2026 au soir, après un diagnostic en lecture seule, deux revues indépendantes et des répétitions sur copies.
Preuve de la correction locale : [`evidence/C3/preuve-correction-viridien-2026-11-04.md`](../evidence/C3/preuve-correction-viridien-2026-11-04.md).

## 1. La version exacte

- **En production aujourd'hui** : commit `2310f87` (fusion de la PR #178, tête de `main`, tags `livrable-E2-v2` à `E5-v2`),
  image `ghcr.io/ganda15/rita-api@sha256:f36dda84...`, construite le 03/11 à 21 h 33 UTC. L'importateur de cette image n'a
  ni `--positions-seulement` ni `--corrections-seulement`, et l'image n'a pas de dossier `data/`.
- **À livrer (opération A)** : la branche `refonte-interface` (16 commits poussés, plus le travail du 04/11 à commiter par Era),
  par PR vers `develop`, puis PR `develop` vers `main` (sept contrôles exigés), fusion par Era, job `deployer` (il attend la
  fin du créneau protégé de 7 h 30 à 9 h). La version exacte est le commit de fusion, lu sur `/health` après le déploiement.
  **Toute fusion dans `main` redéploie la production.**
- **Ce que la livraison apporte, pas seulement Viridien** : les cinq écrans refaits ; `/briefing` avec son bloc `diagnostic` et
  une réponse 503 quand aucun fournisseur ne répond ; l'interface servie en `no-cache` et ses scripts versionnés ; l'alerte
  « performance hors du commun » ; l'importateur (modes ciblés et leurs portes, conversion de l'ancien CSV, contrôle du prix
  de revient, `--limite-annees` réparé) ; le jeu attendu de la passerelle MCP aligné sur Viridien corrigé. **Aucun** changement
  de Dockerfile, de Compose, de dépendances, de schéma, de rôles ni de workflow (vérifié par `git diff` depuis `2310f87`).

## 2. Les changements prévus en base (opération B, après A, accord séparé)

Commande : `python -m db.importer --corrections-seulement`, dans un conteneur jetable lancé depuis l'image livrée (schéma du
rattrapage de `docs/exploitation.md`), sous le verrou du serveur (`flock -w 600 /root/rita-deploy/verrou ...`, le même que
`deploy/deployer.py`). Ce mode ne lit aucun CSV ni l'univers et ne réconcilie rien : il ne demande aucun fichier de données.

| Table | Ligne | Champ | Avant | Après |
|---|---|---|---|---|
| `position` | `VIRI.PA` achetée le 14/10/2021 (id 14 en production) | `quantite` | 120,0000 | 1,0000 |
| | | `pru` | 1,8500 | 185,0000 |
| | | `importe_le` (cette ligne seulement) | 20/08/2026 11 h 03 UTC | l'heure de la correction |
| `valeur` | `VIRI.PA` | `nom_officiel` | CGG BS | VIRIDIEN |

Rien d'autre : aucune cotation, aucune autre position, aucun alias, aucune autre valeur, aucune clôture. Mesuré sur une copie
aux id de production (8 à 14) : `valeur` 1 cellule sur 1 110, `alias_valeur` 0 sur 336, `position` 3 sur 56 ; second passage :
0. **À refaire sur une vraie copie de la production** (porte 2 ci-dessous).

**Portes, dans l'ordre** : (1) `--a-blanc` : applique, affiche le bilan, annule tout ; attendu `Positions regroupees : 1`,
`Noms officiels : 1`. (2) Le vrai passage avec `--attendu-corrigees 1 --attendu-noms 1` : si un compteur diffère, tout est
annulé et la commande sort en erreur. Testé le 04/11 : à blanc sans effet ; rejeu refusé (`obtenu (0, 0)`) sans effet.

## 3. La sauvegarde

- **Avant toute écriture** : `pg_dump -Fc` de la base de production, envoyé par SSH directement sur le poste d'Era (aucun fichier
  écrit sur le serveur), dans `D:\KandaWork\RITA_PROJECT\sauvegardes\rita-prod-AAAA-MM-JJ-avant-viridien.dump`, hors Git ;
  empreinte SHA-256 notée ; fichier mis en lecture seule ; une seconde copie sur un autre disque au choix d'Era. Le dump
  contient des journaux d'usage (données personnelles, registre RGPD) : il reste en France, jamais sur un service hors UE.
- **Restauration testée** : le 04/11, `pg_dump -Fc` puis `pg_restore` entre deux bases jetables `postgres:18-alpine` (l'image de la
  production) : toutes les tables identiques à l'empreinte près, la vue et les droits du rôle de lecture fonctionnent. Condition :
  les rôles existent avant la restauration (c'est le cas en production). À rejouer avec le vrai dump avant l'écriture.
- Sauvegardes existantes : deux dumps locaux (24/08 et 27/09), aucune sauvegarde vue sur le serveur ; les instantanés de la
  console Hetzner restent à regarder par Era (site Hetzner, dans le navigateur).

## 4. Le retour arrière

Un bloc `DO` exécuté en une transaction, qui lève une erreur, donc annule tout, si un compteur n'est pas exactement 1 :
remettre `nom_officiel` à `CGG BS`, puis la ligne `VIRI.PA` du 14/10/2021 à 120 × 1,85 avec son `importe_le` d'origine (valeur
exacte lue dans la sauvegarde), en ne visant la ligne que par ticker, date, quantité et prix de revient, jamais par id. Testé
le 04/11 sur une copie : retour à l'empreinte de départ, à l'octet près ; rejoué, il refuse (`obtenu 0`). C'est une exception à
la règle « écriture en base par l'importateur seulement » : elle ne servirait qu'en incident, avec l'accord d'Era.

## 5. Les vérifications, dans l'ordre base, API, écran

| Quoi | Qui | Attendu |
|---|---|---|
| Base : comparaison cellule à cellule avec la sauvegarde | l'agent, par une lecture approuvée | exactement les 4 cellules du § 2 |
| `/health` | l'agent, sans clé | le commit de la fusion |
| HTML public | l'agent, sans clé | scripts et styles en `?v=`, `Cache-Control: no-cache`, « Volatilité annualisée (20 séances) » |
| API `/donnees/portefeuille` et `/donnees/indicateurs-portefeuille` | Era, avec la clé de production | Viridien `VIRIDIEN`, 1 × 185,00, cours 96,15 €, valorisation 96,15 €, **-48,03 %**, poids **0,46 %** ; total **20 835,20 €** |
| Écran public, Portefeuille et Indicateurs | Era, avec la clé | les mêmes chiffres ; plus de bandeau ; deux graphiques lisibles ; rechargement normal, sans Ctrl+F5, sur la nouvelle version |

Les chiffres attendus valent **si les cours de production restent ceux du 27/10** (instantanés de 16 h 43, pas des clôtures) ;
ils diffèrent du local (21 409,85 €, -50,43 %) pour cette raison. Captures « avant » de l'écran et de l'API de production prises
par Era juste avant l'écriture.

## 6. La preuve

`evidence/C3/preuve-correction-viridien-production-AAAA-MM-JJ.md`, écrite au fil de l'opération, jamais reconstituée : date,
commit déployé, commandes, bilans (à blanc puis réel), comparaison des cellules, captures avant et après, et trois statuts
séparés : **testé en local**, **déployé**, **vérifié en production**.

## 7. Hors périmètre, signalé et non mélangé

- **L'archive de production est décalée d'un jour** : le cours de Viridien daté du 14/10/2021 y vaut 64,16, la valeur que la base
  locale date du 15/10 (64,44 le 14). C'est le défaut de dates corrigé en local le 27/09 (#53) ; la production a été chargée le
  20/08, avant. Décision séparée.
- **Les cours de production s'arrêtent au 27/10** : un rattrapage est une opération séparée, jamais mêlée à cette correction.
- **La passerelle MCP** compare l'API à `passerelle_mcp/jeu_demo_attendu.csv`, qui passe à Viridien corrigé avec A : entre A et
  B, elle refuserait la production. B suit donc A sans attendre.

## 8. Les décisions d'Era

1. Lecture complémentaire de la production (script `lecture_prod_4.sh`, relu, lecture seule et rôle `rita_lecture` vérifiés au
   début, aucun secret) : par l'agent, ou par Era lui-même.
2. Pour A : la refonte entière à la tâche 12 (10/11), ou d'abord une petite PR limitée à l'importateur pour corriger plus tôt.
3. L'endroit de la seconde copie de la sauvegarde.
4. Un accord explicite pour chaque écriture : la fusion (A), le passage à blanc (B, porte 1), le vrai passage (B, porte 2).

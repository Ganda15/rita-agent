# Vérifications sur le site réel après la livraison du 07/11/2026

Livraison : fusion de `develop` dans `main` (PR #221, fusionnée par Era), workflow « Livraison »
https://github.com/Ganda15/rita-agent/actions/runs/42326094558 : `deployer` réussi. Version servie : commit `a68f2cf`,
construite le 07/11 à 01:54 UTC (lue dans `/health`).

Compétences : C17 (sécurité, éco-conception, droits d'accès), C8 (consigne de l'écran Question), C9 (contrat).

## 1. Depuis le poste, sans clé (07/11/2026, 02:00:54 UTC)

Script : [`verifier_production.sh`](verifier_production.sh). Sortie brute :
[`sortie-curl-2026-11-07T0200Z.txt`](sortie-curl-2026-11-07T0200Z.txt).

| Vérification | Attendu | Mesuré |
|---|---|---|
| En-têtes de sécurité (S1) sur les cinq écrans | `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` | présents sur les cinq ✅ |
| `/docs` | les mêmes, sans la politique de contenu (exception voulue, page exacte) | conforme ✅ |
| En-tête `Server: uvicorn` | absent | absent ✅ |
| En-tête `Via: 1.1 Caddy` | | **toujours présent** : il est ajouté par Caddy, pas par l'API ; à retirer dans la configuration de Caddy |
| Compression (#74) | `Content-Encoding: gzip` | sur les cinq écrans et `/docs` ✅ |
| Port 8001 depuis Internet | aucune réponse (`000`) | `000` ✅ (200 avant le correctif, mesuré à 00:00:20 UTC) |
| Version du contrat | `1.2.0` | `1.2.0` ✅ |
| Consigne de l'écran Question (règle UE, C8.2) | `id="consigne-donnees"` présent | présent ✅ |

## 2. Sur le serveur, par Era (carte #76)

Sorties collées par Era le 07/11 au matin (aucune n'affiche de mot de passe) :

| Commande | Sortie |
|---|---|
| `docker exec rita-api-preprod sh -c 'test -z "$DATABASE_URL" && echo absente \|\| echo PRESENTE'` | `absente` ✅ : le mot de passe du propriétaire n'est plus dans le conteneur de l'API |
| `SELECT usename, count(*) FROM pg_stat_activity WHERE datname = 'rita' GROUP BY usename` | `rita\|2` : la requête d'Era elle-même et l'ingestion lancée au même moment, toutes deux en propriétaire. L'API ouvre une connexion par requête et la ferme : au repos, elle n'apparaît pas. Cette sortie ne prouve donc ni pour ni contre |
| `docker exec rita-api-preprod python -c "from sources.database import _connexion; …; cur.execute('SELECT current_user'); …"` | `rita_api` ✅ : la connexion ouverte par le code de l'API (`sources/database.py`, `_connexion`, qui lit `POSTGRES_DSN_API`) travaille sous le rôle `rita_api` |

Carte #76 vérifiée en production : l'API lit la base avec son propre rôle, et le mot de passe du propriétaire n'entre
plus dans son conteneur.

## 3. Dans le navigateur, par Era

Le 07/11 vers 2 h 30 UTC, avec la clé : les cinq écrans s'ouvrent, rien n'est bloqué par la politique de contenu
(message d'Era : « no block everything working »). **Écart relevé par Era** : les données affichées s'arrêtent au
04/11/2026. Cause, lue dans le dépôt : la production n'a pas de collecte planifiée (`docs/exploitation.md`, note du
27/10 : « Une collecte planifiée des cours sur le serveur reste à faire ») ; une livraison ne collecte rien ; la collecte
passe par le workflow « Ingestion » (dernier passage par GitHub le 27/10) ou par le rattrapage lancé sur le serveur,
tous deux à la main.

## 4. Le frein des essais de clé (S3)

Lancé en dernier, le 07/11 à 08:51 UTC, après l'ingestion (elle redémarre l'API, donc vide le compteur), avec l'accord
d'Era (« ok frein ») : il bloque l'adresse du poste 15 minutes. Sortie brute :
[`sortie-frein-2026-11-07T0851Z.txt`](sortie-frein-2026-11-07T0851Z.txt).

| Vérification | Attendu | Mesuré |
|---|---|---|
| 11 fausses clés depuis le poste | dix fois 403, puis 429 | `403` × 10, puis `429` ✅ |
| Réponse du blocage | `Retry-After`, motif `TROP_D_ESSAIS` | `Retry-After: 898`, `TROP_D_ESSAIS` ✅ |
| 3 appels de plus avec un `X-Forwarded-For` inventé (`203.0.113.1` à `.3`) | 429 : l'en-tête du visiteur ne contourne pas le frein | `429` × 3 ✅ |
| Une fausse clé envoyée depuis le serveur (`http://127.0.0.1:8001`, autre adresse), par Era, pendant le blocage du poste | 403, pas 429 : le compteur est par adresse, pas commun à tous | `403` ✅ |

Les deux dernières lignes ensemble prouvent l'option A : `uvicorn` lit bien l'adresse écrite par Caddy (sinon tout le
monde aurait la même adresse, et l'appel du serveur aurait reçu 429), et un visiteur ne peut pas la remplacer par la
sienne.

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

À compléter avec la sortie collée par Era : `DATABASE_URL` absente du conteneur de l'API ; connexions de l'API sous
`rita_api`.

## 3. Dans le navigateur, par Era

Le 07/11 vers 2 h 30 UTC, avec la clé : les cinq écrans s'ouvrent, rien n'est bloqué par la politique de contenu
(message d'Era : « no block everything working »). **Écart relevé par Era** : les données affichées s'arrêtent au
04/11/2026. Cause, lue dans le dépôt : la production n'a pas de collecte planifiée (`docs/exploitation.md`, note du
27/10 : « Une collecte planifiée des cours sur le serveur reste à faire ») ; une livraison ne collecte rien ; la collecte
passe par le workflow « Ingestion » (dernier passage par GitHub le 27/10) ou par le rattrapage lancé sur le serveur,
tous deux à la main.

## 4. Le frein des essais de clé (S3)

À compléter : 11 fausses clés, puis la même série avec un `X-Forwarded-For` inventé. Lancé en dernier : il bloque
l'adresse du poste 15 minutes.

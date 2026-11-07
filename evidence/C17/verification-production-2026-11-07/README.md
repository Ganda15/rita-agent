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

Deux prises, avec l'accord d'Era (« ok frein ») : chacune bloque l'adresse du poste 15 minutes. La seconde a été faite
après le double contrôle de la PR #222, qui a relevé deux manques de la première : des valeurs annoncées sans sortie
conservée, et une comparaison entre deux chemins différents (HTTPS par Caddy contre appel local direct).

### Première prise, 08:51 UTC ([`sortie-frein-2026-11-07T0851Z.txt`](sortie-frein-2026-11-07T0851Z.txt))

| Vérification | Mesuré | Provenance |
|---|---|---|
| 11 fausses clés depuis le poste | `403` × 10, puis `429` | sortie brute |
| 3 appels de plus avec un `X-Forwarded-For` inventé (`203.0.113.1` à `.3`) | `429` × 3 : l'en-tête du visiteur ne contourne pas le blocage | sortie brute |
| `Retry-After: 898` et motif `TROP_D_ESSAIS` | vus à l'écran dans la même prise | **non conservés** dans le fichier (le script garde les codes seuls) ; conservés dans la seconde prise |
| Une fausse clé depuis le serveur, `http://127.0.0.1:8001` | `403` | sortie collée par Era ; appel local direct, sans Caddy : ne prouve pas à lui seul l'indépendance de deux visiteurs HTTPS |

### Seconde prise, 09:46 UTC ([`sortie-frein-complete-2026-11-07T0946Z.txt`](sortie-frein-complete-2026-11-07T0946Z.txt))

| Vérification | Mesuré | Provenance |
|---|---|---|
| 11 fausses clés depuis le poste, par l'URL HTTPS publique, heure de chaque appel | `403` × 10 de 09:46:31 à 09:46:32, puis `429` à 09:46:33 | sortie brute |
| La réponse du blocage, en-têtes et corps | `429`, `Retry-After: 898`, `TROP_D_ESSAIS`, `X-Request-Id: 7441ac04315648ed980a3330c894e33f`, en-têtes de sécurité présents | sortie brute |
| Le téléphone d'Era, Wi-Fi coupé (autre adresse), **même URL HTTPS**, sans clé, pendant le blocage du poste | `Cle d'API invalide ou absente` : un 403, pas un 429 | capture du téléphone d'Era : [`telephone-403-2026-11-07.png`](telephone-403-2026-11-07.png), 10:54 heure de Paris (09:54 UTC), réseau 5G, cadenas et adresse `178-104-184-125.sslip.io` visibles |
| Le poste, au même moment | `429`, `Retry-After: 458`, à 09:53:52 UTC | sortie brute, ajoutée au même fichier |

**Ce que les deux prises prouvent ensemble** : un visiteur bloqué ne contourne pas le blocage en inventant un
`X-Forwarded-For`, et un second visiteur passant aussi par HTTPS et par Caddy n'est pas bloqué pendant ce temps : le
compteur est par adresse (option A du plan S3). Le comportement est aussi couvert par `tests/test_essais_de_cle.py`.

## 5. Les alertes de dépense (OWASP API4), après le double contrôle du 07/11

Le double contrôle de la PR #222 a rappelé que le frein des mauvaises clés et la limite de débit ne sont pas un plafond
de dépense : une clé valide peut encore déclencher des appels payants, 10 par minute au plus. La recommandation OWASP
(API4:2023, « Unrestricted Resource Consumption ») demande un plafond de dépense chez les fournisseurs, ou des alertes
de facturation quand un plafond n'est pas possible.

| Fournisseur | Ce qui est posé | Preuve |
|---|---|---|
| Azure (le seul fournisseur de la production) | budget `RITA-Foundry-10EUR-mensuel`, créé par Era le 07/11 : 10 € par mois sur la ressource Foundry de RITA, alertes par courriel à 50 %, 90 % et 100 % du coût réel, jusqu'au 31/12/2026 (la date de début affichée, 01/11, est le début du mois) | [`azure-budget-alerte-2026-11-07-masque.png`](azure-budget-alerte-2026-11-07-masque.png), masquée à la demande d'Era : seuls l'identifiant de l'abonnement et les deux adresses sont retirés ; le groupe de ressources et le chemin de la ressource Foundry (`microsoft.cognitiveservices`) restent lisibles, pour prouver le périmètre |
| Mistral (le banc seulement, hors de la production) | la console ne propose que des limites de débit (jetons par minute, requêtes par seconde), aucun plafond de dépense ; le banc a son propre plafond (`--plafond 5`, en dollars, il s'arrête seul) | vu par Era dans la console le 07/11 ; plafond du banc : `evals/benchmark_fournisseurs.py` |

**Limite écrite** : un budget Azure alerte, il n'arrête pas les appels. Un dépassement serait signalé, pas empêché.

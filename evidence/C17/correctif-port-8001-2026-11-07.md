# Le port de l'API joignable en clair depuis Internet : constat et correctif (07/11/2026)

Compétence : C17 (sécurité, OWASP Top 10:2025, A02 « mauvaise configuration »). Constat trouvé le 07/11/2026 en
préparant la livraison de `develop` vers `main` ; il ne figurait pas dans la revue du 03/10
(`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`).

## Ce qui a été mesuré

Depuis le poste d'Era, le 07/11/2026 à 00:00:20 UTC, avec `curl` :

| Adresse | Code |
|---|---|
| `http://178.104.184.125:8001/health` (en clair, sans Caddy) | 200 |
| `http://178.104.184.125:8001/donnees/valeurs` sans clé | 403 |
| `https://178-104-184-125.sslip.io/health` (par Caddy, chiffré) | 200 |

La clé d'API est bien exigée sur le port en clair (403 sans elle). Le problème est ailleurs : une clé envoyée par cette
voie circulerait sans chiffrement, lisible par toute machine sur le chemin, et les réponses aussi.

## La cause

`docker-compose.yml` publiait le port de l'API sur toutes les interfaces (`8001:8000`). Le pare-feu `ufw` du serveur
avait 8001 ouvert depuis le 19/08 (`CONTINUITE.md`, avant la mise en place de HTTPS par Caddy le 20/08) ; et un port
publié par Docker passe de toute façon devant `ufw`, par ses propres règles.

## Le correctif

- `docker-compose.yml` : `127.0.0.1:8001:8000`. Caddy tourne sur le serveur et appelle le port par la machine ; le
  script de livraison interroge `http://127.0.0.1:8001` (`deploy/deployer.py`) ; le navigateur du poste ouvre
  `http://localhost:8001` en développement.
- Test d'abord : `tests/test_port_api_local.py` (trois tests, dont la configuration résolue par `docker compose
  config`). Rouge avant le changement (2 échecs), vert après.
- `docs/exploitation.md`, section du rôle de l'API (carte #76), étapes 4 et 5 : installer le nouveau
  `docker-compose.yml` dans `/root/rita-deploy/bin/` juste avant la fusion, et vérifier que Caddy appelle
  `localhost:8001` ou `127.0.0.1:8001`.

## Vérifié avant la fusion

Le 07/11/2026 vers 0 h UTC, sur le serveur, par Era : `grep -n "8001" /etc/caddy/Caddyfile` donne
`2:    reverse_proxy localhost:8001`. Caddy appelle le port par la machine : le lier à `127.0.0.1` ne coupe pas le site.

Sur le poste : `tests/test_port_api_local.py` vert, suite complète du dépôt 2339 réussis, 0 en échec.

## En production

Livré le 07/11 (#221). Mesuré à 02:00:54 UTC depuis le poste : `http://178.104.184.125:8001/health` donne `000` (aucune
réponse), l'adresse HTTPS répond toujours `200` (`evidence/C17/verification-production-2026-11-07/`).

## Ce qui reste

- La règle `ufw` qui ouvre 8001 peut être retirée par Era ; elle ne sert plus.

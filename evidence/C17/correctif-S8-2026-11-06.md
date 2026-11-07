# Constat S8 de la revue OWASP (mots de passe par défaut) : corrigé le 6 novembre 2026

**Le constat du 03/10** (`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`) : une valeur de secours publique pour le
mot de passe du propriétaire de la base dans `docker-compose.yml`, et la base PostgreSQL de développement publiée sur
toutes les interfaces (`db/docker-compose.yml`). Le fichier Compose sert aussi en production : rien ne prouvait que la
valeur de secours n'y servait pas.

## Ce qui a été vérifié sur le serveur, sans afficher aucune valeur

Commandes de la liste du sprint 2 (`docs/sprint-2/PLAN-TRAVAIL.md`, ligne 619), lancées par Era le 06/11 au soir dans
`/root/rita-agent` :

| Commande | Résultat | Ce que ça dit |
|---|---|---|
| `grep -c '^POSTGRES_PASSWORD=' .env` | `1` | le serveur a sa propre ligne de mot de passe |
| `grep -c '^POSTGRES_PASSWORD=rita_preprod_local$' .env` | `0` | ce n'est pas la valeur publique écrite dans le dépôt |

## Ce qui a changé dans le code (branche `owasp-s8`, tests écrits avant)

- `docker-compose.yml` et `docker-compose.sprint5.yml` : `POSTGRES_PASSWORD` est obligatoire, sans valeur de secours ;
  sans elle, Compose refuse de démarrer.
- `db/docker-compose.yml` : la base de développement n'écoute plus que `127.0.0.1`.
- `tests/test_compose_developpement.py` le tient ; `.env.example` et le guide d'exploitation (« Avant de commencer »)
  disent les deux variables à poser pour une pile locale.

## Limite

Le mot de passe de production n'est pas évalué ici (longueur, ancienneté) : seulement qu'il existe et qu'il n'est pas la
valeur publique. La valeur de secours reste lisible dans l'historique Git des versions passées ; elle ne sert plus nulle
part.

## 📖 Glossaire

- **Valeur de secours** : la valeur qu'un fichier Compose prend quand la variable manque (`${VAR:-valeur}`).
- **Variable obligatoire** : `${VAR:?message}` : sans elle, Compose s'arrête avec le message.

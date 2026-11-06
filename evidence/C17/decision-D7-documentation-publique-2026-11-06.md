# Décision D7 : la documentation de l'API reste publique en production, 6 novembre 2026

**La décision d'Era (06/11)** : `/docs`, `/redoc` et `/openapi.json` restent publics en production. Ils décrivent les
chemins de l'API ; aucune donnée n'y est servie.

## Pourquoi, au regard des règles du projet

| Règle | Ce qu'elle dit | Ce que la décision en fait |
|---|---|---|
| Règle de fermeture de la matrice d'accès | toute ressource qui n'est pas listée est refusée, tant qu'une décision ne la liste pas (`evidence/C17/preuve-droits-acces-2026-10-03.md`, ligne 6 et ligne 62, écart E3) | D7 liste la documentation comme ressource **publique** : l'écart E3 est fermé par une décision, pas par une exception tacite |
| Contrat d'API publié (C9) | l'API publie son contrat OpenAPI 3.1.0 et sa documentation interactive (rapport E3, § 3.1) | la documentation se montre en démonstration, sans clé |
| Données protégées (OWASP API2) | chaque route de données exige la clé (`X-API-Key`) | inchangé, et vérifié ci-dessous |

## Ce qui a été vérifié le 06/11/2026

**Sur la production** (`https://178-104-184-125.sslip.io`, vers 21 h 15 UTC) :

- `/openapi.json` : 19 chemins, OpenAPI 3.1.0. Aucune clé de type `sk-` ou `pk-`, aucune adresse de base de données,
  aucun courriel, aucune adresse IP, aucun mot de passe, aucune adresse d'Azure. Un seul exemple : le corps de l'erreur
  503 (`AUCUN_FOURNISSEUR`, « Aucun fournisseur de modèle n'a répondu. »), sans donnée personnelle.
- Sans clé, six routes protégées répondent **403** : `GET /donnees/portefeuille`, `GET /donnees/valeurs`, `GET /sante`,
  `POST /briefing`, `POST /question`, `POST /audit/mcp`. Aucune clé fausse n'a été envoyée à la production.

**Dans le code** (`tests/test_openapi_publique.py`, 47 tests) : le contrat ne contient aucun de ces motifs de secret ;
ses seuls exemples sont des messages d'erreur ; toutes les routes sauf `/health` déclarent une clé ; chaque route
protégée refuse une clé absente ou fausse (401 ou 403) ; les deux routes d'exercice, qui ont leur propre clé, répondent
503 quand les exercices sont coupés (le cas de la production) et 403 à une clé d'exercice absente ou fausse quand ils
sont actifs.

## Ce que la décision accepte

- **L'inventaire des routes est lisible par tous** : un attaquant sait quelles routes existent. Il ne peut rien en
  obtenir sans la clé ; la limite de débit (S3, en partie en place) borne les essais.
- **La page `/docs` charge son script depuis un CDN** : elle n'a pas de politique de contenu (carte #75), contrairement
  aux cinq écrans de RITA.

## 📖 Glossaire

- **OpenAPI** : format standard qui décrit les routes d'une API, leurs paramètres et leurs réponses.
- **Matrice d'accès** : tableau acteur par ressource ; ce qui n'y est pas listé est refusé.
- **CDN** : serveur tiers qui distribue des fichiers (ici, le script de la page de documentation).

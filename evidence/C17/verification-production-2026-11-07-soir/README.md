# Vérification de la production après la livraison du 07/11/2026 au soir (S9, C17.7, corrections de #226)

**Ce qui a été livré.** La PR #228 (`develop` vers `main`), fusionnée par Era le 07/11 à 19 h 32 UTC, commit `6f428d6`,
apporte trois demandes déjà relues et fusionnées dans `develop` : #225 (S9, garde-fous), #226 (C17.7, pagination
d'Indicateurs ; C16.1, bilan) et #227 (huit corrections après la revue Claude Code de #226). Le commit `develop`
`f06a8cd` est contenu dans `6f428d6`.

**Relevés faits juste après la livraison, le 07/11 de 19 h 47 à 19 h 48 UTC**, chacun écrit par sa commande :

| Relevé | Résultat | Fichier |
|---|---|---|
| Livraison du commit `6f428d6` | succès ; `construire-et-publier` 19 h 37 à 19 h 42, `deployer` 19 h 42 à 19 h 46 (étape « Livrer l'image sur le serveur »), reprise non nécessaire | [`livraison.txt`](livraison.txt) |
| Tests sur `main` | succès | [`livraison.txt`](livraison.txt) |
| `/health` du site réel | `"status":"ok"`, **`"commit":"6f428d61511019d7b6013fb007e290c133d48c2e"`**, construit le 07/11 à 19 h 40 UTC | [`health.txt`](health.txt) |
| Écran Indicateurs servi | `indicateurs.js?v=1cc58c780c`, celui de `main` à `6f428d6` (avant la livraison : `6fcaef099f`) ; la barre de pages (`id="pagination"`) et la zone d'annonce (`id="annonce-pages"`) sont dans la page | [`ecran-indicateurs.txt`](ecran-indicateurs.txt) |

## Ce que ça prouve, et ce que ça ne prouve pas

- **Prouvé** : le serveur de production fait tourner le commit `6f428d6`, qui contient le code de S9 (garde-fous), de
  C17.7 (pagination) et des huit corrections ; l'écran Indicateurs servi est la version paginée.
- **Pas prouvé par ces relevés** :
  - le comportement des garde-fous de S9 **sur le site réel** : vérifier qu'une question interdite masquée est refusée
    demande un appel authentifié à `/question`, qui n'a pas été fait ici (la clé d'accès est celle d'Era) ;
  - la note EcoIndex **en production** : la mesure D (52) puis B (76) reste une mesure locale
    (`evidence/C17/mesures-2026-11-07-pagination/README.md`) ;
  - la vigie de la production : elle échoue toujours, faute du secret `RITA_API_KEY_VIGIE` (C20.5, gardé pour la fin).

## 📖 Glossaire

- **Livraison** : le workflow GitHub qui construit l'image du service, la publie, puis la déploie sur le serveur.
- **`/health`** : l'adresse de santé du service ; elle dit le commit exact de l'image qui tourne.
- **Empreinte de version (`?v=`)** : une courte empreinte du contenu d'un fichier de l'interface, ajoutée à son
  adresse ; elle change dès que le fichier change, ce qui permet de savoir quelle version le navigateur reçoit.

# Preuve C17 : les droits d'accès de RITA, le choix d'une clé unique et sa défense (03/10/2026)

> **Critère visé** (livrable E4) : C17, *« La gestion des droits d'accès à l'application est développée et conforme aux spécifications »*.
> Tâche T5 du plan E4 ([`../../docs/PLAN-E4-rapport.md`](../../docs/PLAN-E4-rapport.md)), carte #26, décision D1 d'Era : défendre le choix mono-utilisateur par écrit plutôt que coder un second niveau avant le gel.
> La spécification de référence est la **matrice d'accès** du chapitre « Données » validé par le formateur le 03/10/2026
> ([`../../docs/conception/donnees/`](../../docs/conception/donnees/), §3.4 et §3.5), avec sa **règle de fermeture** : tout accès, tout acteur, toute ressource non listés sont refusés.

## 1. Le choix, en clair

RITA a **un seul utilisateur humain : son propriétaire**, qui est aussi le commanditaire (un investisseur particulier qui veut lire ses données et un briefing).
L'accès se fait donc par **une seule clé d'API**, exigée sur toutes les routes de données, sur `/briefing` et sur `/audit/mcp` ; seules `/health` et les pages
statiques de l'écran sont publiques, et elles ne contiennent aucune donnée. C'est la décision D10 (« une seule clé d'API, mono-utilisateur, pas de système de
comptes »), appliquée depuis la correction du 18/08/2026 qui a supprimé la clé par défaut (INC-001).

Le formateur et le jury **ne reçoivent pas la clé** : ils lisent le dépôt et voient la démonstration, où le propriétaire tape la clé devant eux.

## 2. Pourquoi ce choix, et pas des comptes

| Question | Réponse |
|---|---|
| Combien d'utilisateurs ? | un. Il n'existe aucun deuxième utilisateur, ni prévu par le brief, ni demandé par le commanditaire |
| Quelles données sont protégées ? | le jeu de positions est un jeu **anonymisé de démonstration** (`data/positions-exemple.csv`) ; `POSITIONS_CSV` n'est défini ni dans `.env.example` ni dans `docker-compose.yml`, le portefeuille réel n'est chargé nulle part (précision du 19/08, `evidence/C14/preuve-specifications-wireframes.md`) ; le reste est public (cours, taux, articles) |
| Que coûterait un système de comptes ? | stocker des mots de passe (hachage, réinitialisation), gérer des sessions et des cookies (donc la falsification de requête intersite), un écran d'inscription, des rôles : **plus de surface d'attaque que de bénéfice** pour un utilisateur |
| Qu'apporterait-il ? | la séparation de ce que chacun voit, la révocation d'un seul accès, la traçabilité par personne : trois besoins qui n'existent pas tant qu'il n'y a qu'une personne |

La règle suivie : **le plus petit contrôle qui couvre le risque réel, et l'écart écrit**, plutôt qu'un contrôle complet qui ne protège rien de plus.
C'est aussi ce que fait le chapitre « Données » validé : il décrit une politique cible et nomme l'écart avec le rôle partagé actuel.

## 3. Le modèle de menace, court

| Actif | Menace | Parade en place | Preuve |
|---|---|---|---|
| Les données exposées par l'API | un inconnu les lit | clé exigée par une dépendance posée **sur le routeur entier** (`api/main.py:207`) | `tests/test_api_donnees.py::test_toute_route_donnees_est_protegee` ; **production, 03/10 : 403 sans clé et avec une fausse clé** |
| La clé | elle est devinée | aucune valeur par défaut, 16 caractères minimum, génération par `secrets.token_urlsafe(32)` (`docs/EXPLOITATION.md`), comparaison à temps constant | `tests/test_health.py::test_l_api_refuse_de_servir_sans_cle_configuree` |
| La clé | elle fuit | jamais dans le code ni dans le front (test), `sessionStorage` effacé à la fermeture de l'onglet, hook `bloquer-secrets` côté assistant, aucune clé réelle dans les 313 commits (revue OWASP du 03/10) | `tests/test_frontend.py`, `evidence/C17/revue-owasp-top10-2025-2026-10-03.md` |
| Le budget des appels au modèle | un détenteur de la clé en abuse | **aucune** (pas de limite de débit) | écart S3, carte #75 |
| Le jeu de positions | il sort par la passerelle MCP vers un hôte distant | servi seulement si `RITA_MCP_PORTEFEUILLE=demo` **et** si les positions sont exactement celles du jeu d'exemple (comparaison stricte, un doute vaut refus) | `passerelle_mcp/serveur.py:83-104`, ajouté le 03/10 (`4037028`) |
| Les positions | elles partent chez le fournisseur du modèle | le scout ne lit que trois lectures de marché ; aucune position, aucun PRU dans le prompt | `agents/scout.py`, `graph/workflow.py:14` |
| Les articles bloqués | ils sont servis ou cherchés | filtre `bloque_injection = FALSE` codé en dur dans `/articles` ; retirés de l'index de recherche à la reconstruction | `api/donnees.py:285-292`, `rag/indexation.py:280`, `:312-317` |
| La base | une requête arbitraire | aucune route n'accepte du SQL, un nom de table ou un fichier ; requêtes paramétrées | revue OWASP, A05 |

## 4. La matrice validée, confrontée au code d'aujourd'hui

Le chapitre « Données » dit lui-même que ses matrices décrivent **la politique cible**, pas le rôle partagé actuel. Voici, case par case, ce que le code
applique **aujourd'hui** (vérifié le 03/10 par lecture et, quand c'est indiqué, par une sonde).

### 4.1 Profils et informations (§3.4)

| Ressource | Propriétaire | Hôte MCP de confiance | Démonstration | Inconnu | Modèle externe |
|---|---|---|---|---|---|
| Indicateurs et fraîcheur | ✅ lecture par l'API, avec la clé | ✅ deux outils (`rita_indicateurs`, `rita_fraicheur`) | ✅ | ✅ **403 mesuré** | ✅ seulement les champs du prompt (13 indicateurs) |
| Portefeuille réel | ✅ (aucun n'est chargé) | ✅ refusé : la garde exige le jeu d'exemple | ✅ refusé | ✅ 403 | ✅ refusé : jamais dans le prompt |
| Portefeuille de démonstration | ✅ | ✅ seulement en démonstration déclarée **et** vérifiée | ✅ | ✅ 403 | ✅ refusé |
| Articles éligibles | ✅ | ⏳ l'outil de recherche (`search_articles`) n'existe pas encore : refus de fait | ✅ | ✅ 403 | ✅ trois passages au plus |
| Articles bloqués | ✅ filtre codé en dur | ✅ | ✅ | ✅ | ✅ retirés de l'index |
| `POST /briefing` | ✅ avec la clé | ✅ **aucun outil MCP ne l'expose** | ✅ par un client REST qui a la clé | ✅ **403 mesuré** | ✅ ne reçoit que la requête de génération |
| SQL libre, table brute, index | ✅ aucune route | ✅ | ✅ | ✅ | ✅ |
| Journaux et sauvegardes | ✅ aucune route | ✅ | ✅ | ✅ | ✅ |
| Clés et configuration | ✅ jamais dans une réponse | ✅ | ✅ | ✅ | ✅ |
| **Documentation de l'API** (`/docs`, `/redoc`, `/openapi.json`) | ressource **non listée** | | | 🔴 **200 sans clé, mesuré en production** | |

La dernière ligne est un écart à la **règle de fermeture** : la documentation n'est pas dans la matrice, elle devrait donc être refusée tant qu'une décision
explicite et tracée ne l'autorise pas. C'est la décision D7 posée par la revue OWASP (constat S2) ; la règle validée par le formateur tranche déjà dans le sens
du refus, sauf décision contraire d'Era écrite et motivée (par exemple : publique pour la démonstration, jusqu'au 01/12).

### 4.2 Droits techniques des composants (§3.5)

| Composant | Ce que dit la matrice | Ce que fait le code | État |
|---|---|---|---|
| Passerelle MCP | aucun accès direct à la base | passe par l'API avec la clé, déclare ses refus par `POST /audit/mcp` | ✅ |
| **API et graphe (dont le scout)** | **lecture** des tables nécessaires ; écriture limitée au journal d'audit | se connectent avec `DATABASE_URL`, **le rôle propriétaire `rita`** (tous les droits), en local comme dans `docker-compose.yml` | 🔴 **écart E1** |
| Collecte et import | lecture et écriture des tables assignées | `pipelines/ingest.py` et `db/importer.py`, même rôle propriétaire | 🟠 le rôle n'est pas séparé |
| Outils d'agent qui lisent la base | rôle `rita_lecture`, lecture seule (`AGENTS.md`) | le rôle existe (`db/roles.sql`, 4 tests) mais **aucun fichier Python ne l'utilise** (`RITA_DSN_LECTURE` n'est lu nulle part) | 🟠 écart E2 |
| Secrets de chaque composant | chacun sa clé | **une clé partagée** par l'écran, la passerelle et le propriétaire | 🟠 choix de §1, coût en §5 |

## 5. Ce que le choix coûte, dit franchement

- **Pas de révocation partielle.** Si la clé fuit, on la change pour tous : l'écran (saisie), la passerelle MCP (`RITA_API_KEY` de son environnement) et le serveur.
- **Pas de traçabilité par personne.** Le journal sait *quelle requête*, pas *qui*. L'en-tête `X-Client-Id` qui distingue la passerelle est **déclaratif** : tout
  détenteur de la clé peut l'écrire. Il sert à compter les appels automatiques, pas à authentifier.
- **Pas de procédure de rotation écrite.** La génération d'une clé est documentée (`docs/EXPLOITATION.md`), son remplacement partout ne l'est pas (§7).
- **Pas de limite aux essais ni de trace des refus** (constats S3 et S4 de la revue OWASP) : une tentative de force brute ne serait ni freinée ni vue.
- **L'écran briefing mémorise la clé avant de l'avoir vue fonctionner** (carte #73).

## 6. Les écarts trouvés en écrivant cette défense

| # | Écart | Gravité | Correction proposée | Quand |
|---|---|---|---|---|
| E1 | L'API et le scout lisent la base avec le **rôle propriétaire**, alors que la matrice validée ne leur donne que la lecture (et l'écriture du journal d'audit) | moyenne : une injection SQL, aujourd'hui absente, aurait tous les droits | un rôle `rita_api` : lecture des tables et vues servies, `INSERT` sur `mcp_calls` seulement ; l'API se connecte avec lui, l'import garde le rôle propriétaire. Test : l'API ne peut ni `UPDATE` ni `DELETE` (comme `tests/test_role_lecture.py`) | carte #76, après le 15/10, sur un plan écrit |
| E2 | Le rôle `rita_lecture` n'est utilisé par aucun code | faible | le donner à la future recherche documentaire (`search_articles`) et à tout outil d'exploration ; ou dire qu'il est en attente | avec #63 |
| E3 | Documentation de l'API publique, hors matrice | faible | décision D7 ; la règle de fermeture plaide pour la mettre derrière la clé | décision d'Era |
| E4 | Aucune limite de débit, aucun journal des refus | moyenne | carte #75 (S3, S4) | après le 15/10 |
| E5 | Clé mémorisée trop tôt sur l'écran 3 | faible | carte #73 | après le 15/10 |

Aucun de ces écarts n'ouvre l'accès à un inconnu : tous ont été vérifiés avec la clé exigée. Ils portent sur **ce que peut faire un composant ou un détenteur de la clé**.

## 7. Procédure de rotation de la clé (proposée, pas encore éprouvée)

1. Générer une clé : `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
2. La poser dans le fichier d'environnement du serveur et redémarrer l'API ; vérifier `403` avec l'ancienne clé et `200` avec la nouvelle sur `/donnees/fraicheur`.
3. La poser dans l'environnement de la passerelle MCP ; relancer un outil (`rita_fraicheur`).
4. Dans le navigateur, l'ancienne clé est refusée (`403`), oubliée par l'écran, et la nouvelle est saisie.
5. Noter la date de rotation dans `docs/EXPLOITATION.md`, jamais la clé.

À éprouver une fois avant le jury, au moment du déploiement d'après le 15/10, et à garder comme preuve.

## 8. Quand ce choix devra changer

| Déclencheur | Ce qu'il faudrait |
|---|---|
| un deuxième utilisateur humain | des comptes, ou au minimum une clé par personne avec un identifiant journalisé |
| le portefeuille réel chargé en production | la matrice §3.4 appliquée par des rôles, pas par une clé ; le registre RGPD mis à jour (traitement T1) |
| un hôte MCP distant, hors du poste du propriétaire | une clé propre à la passerelle, révocable seule, et la recherche documentaire avec le rôle `rita_lecture` |
| une ouverture à un client extérieur | limitation de débit et journal des refus avant tout (S3, S4) |

## 9. Verdict pour le critère C17.5

Le choix d'une clé unique est **défendu et cohérent avec le besoin** : un utilisateur, des données de démonstration, aucun accès sans clé (mesuré en production).
Mais le critère demande une gestion des droits **conforme aux spécifications**, et la spécification validée (§3.5) donne à l'API la lecture seule, quand elle
se connecte aujourd'hui en propriétaire (E1). **Le critère reste donc partiel** jusqu'à la correction d'E1. Cocher ✅ maintenant serait déclarer conforme
ce que la matrice du formateur décrit comme un écart.

*Un document qui ne signale aucune faiblesse n'est pas crédible devant un jury.*

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Clé d'API** | chaîne secrète envoyée dans l'en-tête `X-API-Key` ; sans elle, l'API répond 403 |
| **Mono-utilisateur** | application prévue pour une seule personne, qui n'a donc pas besoin de comptes |
| **Matrice d'accès** | tableau qui dit, pour chaque acteur et chaque ressource, ce qui est permis ; ici avec une règle de fermeture : ce qui n'est pas listé est refusé |
| **Rôle PostgreSQL** | identité de connexion à la base, avec des droits précis (lecture, écriture, administration) |
| **Rôle propriétaire** | le rôle qui a créé les tables et a donc tous les droits dessus |
| **Moindre privilège** | chaque composant ne reçoit que les droits dont il a besoin |
| **Révocation** | retirer un accès ; avec une clé unique, on ne peut la retirer qu'à tout le monde à la fois |
| **Rotation** | remplacer une clé par une nouvelle, partout où elle sert |
| **Déclaratif** | annoncé par le client lui-même, sans preuve : utile pour compter, pas pour authentifier |
| **Hôte MCP** | application (assistant, éditeur) qui appelle les outils de la passerelle MCP de RITA |

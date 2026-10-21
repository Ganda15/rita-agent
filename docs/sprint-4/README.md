# Sprint 4 : la composante agentique et les garde-fous

Document d'entrée du sprint 4 du fil rouge RITA. Il dit pourquoi la composante n'a pas d'action sensible, qui peut
modifier le système et quelle trace cela laisse, quel est le périmètre d'accès, où se lisent les signaux que le sprint 5
surveillera, et ce qui n'est pas fait.

- **Production** : <https://178-104-184-125.sslip.io> (serveur Hetzner). `/health` annonce le commit servi.
- **Conception** : la spec `docs/sprint-4/SPEC.md` et le plan de travail `docs/sprint-4/PLAN-TRAVAIL.md`.
- **Avenant n°1** : `docs/sprint-4/AVENANT-1.md` ; le parcours des questions entre dans la composante agentique. Le
  dossier du sprint 1 y renvoie par une ligne datée (`docs/CADRAGE-V1.md`, § 3).
- **Contrat du sprint 1, critère par critère** : `docs/sprint-4/CONTRAT.md`.
- **Preuves** : index dans `evidence/sprint-4/README.md`.
- **Livrable du sprint** : `docs/sprint-4/livrable/livrable-sprint-4.md` et sa version PDF, dans le même dossier.

## 1. Pourquoi la composante n'a pas d'action sensible (CA5.1)

La composante agentique a deux parcours : le briefing (`POST /briefing`, graphe `scout`, `rag`, `redacteur`) et les
questions (`POST /question`). Tous deux lisent des données (cours, indicateurs, articles) et rédigent un texte. Aucun
n'a d'outil d'action : ils ne passent pas d'ordre, n'envoient pas de message, n'écrivent dans aucun système extérieur et
ne modifient pas la base. Aucune étape n'attend de validation humaine, parce qu'aucune n'engage quoi que ce soit. Le
risque principal est un texte qui conseille ou qui laisse fuiter une consigne : il est traité par les garde-fous
d'entrée et de sortie, mesurés dans `evidence/sprint-4/README.md`.

## 2. Les opérations d'administration (CA5.3)

Trois opérations modifient bien le système. Elles ne font pas partie de la composante : un humain les lance, depuis
GitHub, avec son nom.

| Opération | Comment on la lance | Nom et motif | Trace |
|---|---|---|---|
| Ingestion (collecte, nouvel index, pré-test, bascule) | onglet Actions, « Ingestion », *Run workflow* (`.github/workflows/ingestion.yml`) | champs `acteur` et `motif` obligatoires | le passage GitHub garde le nom et le motif ; le serveur reçoit le seul numéro du passage |
| Livraison | fusion sur `main` d'une PR relue, contrôles exigés verts (`.github/workflows/livraison.yml`) | l'auteur de la fusion et la PR | le passage GitHub et la PR |
| Retour arrière | onglet Actions, « Retour arrière », *Run workflow* (`.github/workflows/retour-arriere.yml`) | champs `acteur` et `motif` obligatoires | le passage GitHub garde le nom et le motif ; le serveur reçoit le seul numéro du passage |

Seul un compte qui a accès en écriture au dépôt GitHub peut les lancer. Sur le serveur, `deploy/deployer.py` ne laisse
passer qu'une opération à la fois (un verrou sur le disque) et ajoute une ligne à `/root/rita-deploy/journal.jsonl`
pour chacune ; on n'y efface ni n'y modifie jamais rien. Exemple mesuré : le retour arrière du 14/10/2026,
`evidence/sprint-2/N1-retour-arriere-2026-10-14.md`.

## 3. Le périmètre d'accès (CA5.2)

- **Base de données** : le rôle `rita_lecture` lit toutes les tables et n'écrit rien (`db/roles.sql` ;
  `tests/test_role_lecture.py` : il lit, il ne peut ni écrire ni créer de table). Il sert au pré-test et au rejeu des
  questions avant chaque bascule (`deploy/deployer.py`). **Écart** : l'API de production se connecte avec le rôle
  propriétaire `rita` (`docker-compose.yml`), voir § 5.
- **Passerelle MCP** (`passerelle_mcp/serveur.py`) : trois outils (`rita_fraicheur`, `rita_portefeuille`,
  `rita_indicateurs`), tous déclarés en lecture seule. Elle n'a aucun accès direct à la base : elle passe par l'API,
  avec la clé. Le portefeuille n'est servi qu'en démonstration déclarée et vérifiée. Ses refus sont déclarés à l'API par
  `POST /audit/mcp` et écrits dans la table `mcp_calls` (`tests/test_audit_mcp.py`, `tests/test_passerelle_mcp.py`).
- **API** : les routes de données et d'IA (`/donnees/…`, `/briefing`, `/question`, `/audit/mcp`) exigent la clé ; un
  refus de clé laisse une ligne de journal (critère 4 du contrat). Au plus 10 appels par minute, partagés par
  `/briefing` et `/question` (tâche C3) ; ce quota est fixe en production, la variable `RITA_QUOTA_PAR_MINUTE` n'étant
  pas transmise au conteneur. Restent publics, vérifié en production le 20/10 : `/health`, les pages de l'interface (qui
  demandent la clé avant d'appeler l'API) et la documentation `/docs` avec `/openapi.json` (voir § 5).

## 4. Les signaux du sprint 5 (CA7.1)

| Signal | Où il se lit aujourd'hui | Ce qui manque pour le surveiller |
|---|---|---|
| Latence | `duree_ms` dans les lignes de journal « briefing servi » (`api/main.py`) et « question servie » (`api/question.py`), avec l'identifiant de requête ; durées des étapes dans les traces Langfuse | aucun calcul de médiane ni de p95, aucun seuil |
| Coût | les générations Langfuse portent le modèle et les jetons consommés (`src/traces.py`, depuis la tâche B3) | aucun cumul par jour ni budget ; prix par modèle à vérifier dans Langfuse |
| Taux de refus par motif | une ligne de journal par refus : clé (`cle d'API refusee`), valeur inconnue, garde-fou de sortie, contrôle de fuite, débit (`limite de debit atteinte`), et pour les questions la ligne « question servie » avec `statut` et `motif` (dont `TENTATIVE_DETOURNEMENT`) ; refus MCP dans `mcp_calls` | aucun comptage : le taux demande de compter les lignes à la main |
| Erreurs | lignes « briefing en erreur 502 » et « erreur interne » (500), avec l'identifiant de requête ; étapes marquées ERROR dans Langfuse, avec le seul type de l'exception | aucun tableau ; deux alertes Langfuse seulement (le maximum du palier gratuit), qui ouvrent une issue « incident » par `.github/workflows/alerte-incident.yml` |

Les lignes de journal se lisent dans le journal du conteneur de l'API sur le serveur.

## 5. Ce qui n'est pas fait

- **L'API de production lit la base avec le rôle propriétaire** (écart E1, carte #76, relevé le 03/10 dans
  `evidence/C17/preuve-droits-acces-2026-10-03.md`). Elle écrit aussi dans `mcp_calls` : la correction prévue est un
  rôle `rita_api` (lecture des données servies, écriture dans `mcp_calls` seulement). Non faite.
- **La documentation de l'API est publique** (`/docs`, `/openapi.json` : 200 sans clé le 20/10). Elle ne donne aucune
  donnée, mais la règle de fermeture de la matrice d'accès voudrait qu'elle passe derrière la clé ; relevé le 03/10
  (même preuve), non décidé.
- **Les essais de clé sont journalisés mais pas freinés** : le limiteur passe après la vérification de la clé ; il
  protège le coût du modèle, pas contre une clé devinée par essais répétés.
- **Le tiers du critère 5 du contrat** (D8) : question au formateur, sans réponse au 20/10.
- **L'avenant n°1** attend la validation du formateur.
- **Les traces Langfuse de production** ne sont pas revérifiées : aucune trace de briefing de production n'a été ouverte pour constater qu'elle ne garde ni prompt ni réponse ; seuls les tests le prouvent.
- **Garde-fou de détournement** : les reformulations R1 à R8, gardées hors du jeu pour une mesure honnête, sont
  reconnues 0 fois sur 8 par les règles ; le cas H8 n'est pas activé (décision du 20/10).
- **Contrôle de fuite** : 71,4 % des sorties de fuite bloquées, deux cas hors échantillon passent.
- **Signaux** : ni comptage, ni tableau, ni seuil (sprint 5).

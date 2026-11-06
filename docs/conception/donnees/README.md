# Chapitre « Données » : la conception validée par le formateur, et son intégration dans RITA

> **Brief** : « Concevoir l'architecture de données de mon fil rouge » (Simplonline, créé le 01/09/2026 ;
> deux jours, conception seule, aucun code attendu). **Rendu** : 07/09/2026, chiffres relevés sur
> `develop` au commit `23318a6` (08/09). **Retour du formateur, 03/10/2026** : « Très bon travail.
> Se montrera utile à l'exécution. Rien à redire. »
>
> Le chapitre a été écrit **à côté** du dépôt, en lecture seule, pour ne rien y changer avant la revue.
> Depuis le 03/10 il entre ici, et ses propositions deviennent du travail planifié : ce dossier dit
> ce que le code fait déjà, ce qui reste proposé, et dans quel ordre on l'applique.

## Les fichiers

| Fichier | Quoi |
|---|---|
| `chapitre-donnees-version-courte-2026-09-07.pdf` | 12 pages, autoportant : cartographie, MCD/MPD et indexation, matrice d'accès, 32 cas de vérification, schémas. **À lire d'abord.** |
| `chapitre-donnees-version-complete-2026-09-07.pdf` | 40 pages, développé et sourcé (annexes : preuves de certification, historique, liens). Fait foi en cas de doute. |
| `schema-architecture-donnees.svg`, `schema-modele-donnees.svg` | les deux schémas du rendu : l'architecture des données (préparer, puis consulter et rédiger, avec ce qui est observé et ce qui est proposé) ; le modèle des **tables** (clés primaires et étrangères, vue de valorisation). Le MCD Merise de référence reste `evidence/C4/MCD-MERISE-RITA.png` (01/08) et sa version à jour, dans le rapport E1, § 5. |

Le chapitre emploie quatre statuts : **Observé** (dans le code au commit étudié), **Documenté** (rapporté par
un document daté), **Proposé** (conception, rien de réalisé), **À vérifier** (manque ou décision attendue).

**Relu le 04/10/2026 contre `db/schema.sql` et la base.** Le modèle des tables est celui du 07/09 : il ne montre ni
`position.date_cloture` (03/10), ni `macro_observation` (27/09), ni `mcp_calls` (03/10), et sa note « devise sans taux
≠ taux 1 » est réglée depuis le 03/10 (la vue rend `taux_manquant` au lieu d'un taux supposé). Ses cardinalités sont
celles des tables (0,N : une clé étrangère n'oblige pas une valeur à avoir un alias ou une cotation) ; le MCD donne
celles du métier (1,n) ; depuis le 02/11, le MCD dit aussi `0,n` pour la cotation
(`evidence/C4/preuve-mcd-merise.md`, section 5 bis). Dans les données du 04/10, aucune valeur n'est sans alias ni sans cotation, et aucune devise
n'est sans taux. L'architecture des données est une conception datée : les noms des trois outils MCP
(`rita_fraicheur`, `rita_indicateurs`, `rita_portefeuille`) sont ceux de `passerelle_mcp/serveur.py`, les éléments
marqués « Proposé » ne sont pas construits.

## Ce que le chapitre décide, et ce que le code en fait au 03/10/2026

Lu fichier par fichier le 03/10 (`db/schema.sql`, `db/roles.sql`, `rag/indexation.py`, `rag/recherche.py`,
`passerelle_mcp/serveur.py`, `pipelines/ingest.py`, `api/main.py`).

| Sujet (section du chapitre) | Décision ou écart écrit le 07/09 | État du code au 03/10 | Suite |
|---|---|---|---|
| Socle (§6) | réutiliser PostgreSQL et les requêtes existantes ; vérifier volumes et version déployée | tenu : 9 tables, 1 vue depuis le 27/09 (`macro_observation` ajoutée) ; 276 530 cotations le 06/09, à remesurer avant démonstration | aucune action de code |
| Text-to-SQL (§3.6) | **non retenu** ; réouverture sur besoin motivé seulement | aucun SQL généré dans le dépôt | décision à inscrire dans le ledger (fait le 03/10) |
| Rôle lecture seule (§3.5) | privilèges réels du rôle PostgreSQL à vérifier | **fait** : `db/roles.sql` crée `rita_lecture` (SELECT seul), `tests/test_role_lecture.py` prouve les refus | rien |
| Orphelins de l'index (§2.4) | l'indexeur ne supprime jamais ; 605 vecteurs pour 594 articles | **fait le 19/09** (revue revue automatisée de la PR #1) : `rag/indexation.py` supprime les identifiants retirés avant l'upsert | preuve à citer dans E3 |
| Filtre par valeur (§2.4, R03) | le filtre dense s'appliquait après la sélection globale | **fait le 19/09** : classement dense restreint aux identifiants du ticker (`ids=`) ; filtre déterministe avant la recherche depuis le 30/08 | rien |
| Corrélation des événements (A06) | événements corrélés, aucun inventé | **fait le 02/10** : `request_id` sur chaque réponse, dans le journal et la trace Langfuse | rien |
| Métadonnée `titre` dans l'index (§2.4, R11) | titre à ajouter pour la citation | **fait le 03/10** (issue #59, 3 tests) : métadonnée `titre` et champ `titre` du passage ; index du poste à reconstruire par la collecte de 19 h | rien |
| `search_articles` (§3.2, §3.3) | spécifier l'outil MCP et sa route REST ; ne pas annoncer quatre outils | **absent** : trois outils, aucune route de recherche | **décidé le 03/10** (#63) : périmètre confirmé, construction après le gel du 15/10 ; d'ici là on dit trois outils |
| Journal `mcp_calls` (§3.6) | table proposée : `request_id`, client, outil, statut, code, durée, version de politique ; 90 jours ; écrite par l'API, jamais par la passerelle | **fait le 03/10** (issue #62, plan validé, 21 tests, migration jouée sur le poste, premières lignes réelles) : écrit par l'API seule, refus locaux remontés, T5 et P6 | Compose et Hetzner à migrer |
| Valorisation (§2.3, D06) | pas de conversion avec un taux supposé ; `COALESCE(taux, 1)` à remplacer par « indisponible » | **fait le 03/10** (issue #65, plan validé, 23 tests, migration jouée sur le poste) : `CASE` sur `'EUR'`, `taux_manquant`, total et poids « indisponibles » | Compose et Hetzner à migrer |
| Conservation des positions (§1.5) | la purge cherche `quantite = 0`, interdit par le schéma : elle ne s'applique jamais ; pas de date de clôture | **fait le 03/10** (issue #66, plan validé D1 à D4 = A) : `date_cloture` posée par l'import, index unique de ligne, P2 applicable, P3 retirée, T1 réécrit ; D07 (#69) signalé à l'import | rien : migration jouée sur le poste, Compose et Hetzner le 03/10 ; import réel rejoué sur le poste (7 mises à jour, 0 insérée, 0 close) ; `evidence/C4/preuve-cloture-positions.md` |
| Environnement de démonstration (§3.3, A04) | `rita_portefeuille` ne vérifie ni le caractère fictif ni le destinataire ; une phrase de description ne suffit pas | **fait le 03/10** (issue #60, 5 tests) : déclaration `RITA_MCP_PORTEFEUILLE=demo` obligatoire ET positions comparées au jeu d'exemple ; sinon refus sans donnée | rien |
| Manifeste de collecte (§1.3) | un manifeste par exécution : source, période, versions, comptages réels, erreurs | **fait le 03/10** (issue #64, 9 tests) : `logs/manifeste-<date>-<heure>.json` par exécution, comptages par étape, erreurs sans clé, commit ; `lire_dernier_manifeste()` pour C20 | premier manifeste réel à la collecte de 19 h |
| Quasi-doublons (§1.3, D08) | 14 quasi-doublons restants ; élargir la règle risque d'écraser des articles proches | règle inchangée : (titre normalisé, jour) depuis le 06/09 | **décidé le 03/10** (#67) : la règle reste, les 14 cas sont acceptés, réouverture au-delà de 5 % du corpus |
| Champs envoyés au modèle (§1.4) | inventaire des champs sortants, destinataires, conservation | partiellement : registre RGPD T3 dit « aucune donnée personnelle dans le prompt » (mesuré le 28/09) ; pas d'inventaire champ par champ | issue, registre |
| Les 32 cas de vérification (§4) | protocole de conception, non exécuté | **cartographiés le 03/10** (issue #61) : 23 couverts, 5 partiels, 4 manquants ; quatre tests écrits (D02, D05, R09, R13) ; `evidence/C12/cas-de-verification-chapitre-donnees.md` | les 4 manquants ont leur issue : #65, #69, #63, #70 |
| Jeu annoté (§4.4) | 53 questions annotées par un LLM, non revalidées ; Hit@1 0,547, MRR 0,605 en hybride | inchangé depuis le 07/09 | relecture humaine à planifier (E3, C12) |

**Lecture honnête** : sur dix-sept lignes, cinq sont tenues par le code (dont trois depuis le rendu), neuf
restent proposées, deux attendent une décision d'Era, une attend du temps de relecture. Rien de ce qui est
proposé n'a été réalisé en silence : chaque ligne « issue » renvoie à une carte GitHub ouverte le 03/10.

## L'ordre d'intégration, et ses garde-fous

1. **Sans zone sous garde, test d'abord** : métadonnée `titre` ; vérification de l'environnement de
   démonstration dans la passerelle ; cartographie des 32 cas vers les tests ; manifeste de collecte.
2. **Avec plan validé par Era avant le code** (`AGENTS.md`, zones sous garde) : vue de valorisation
   (`COALESCE`) ; table `mcp_calls` ; clôture et purge des positions (schéma + registre RGPD).
3. **Décisions d'Era** : politique des quasi-doublons ; `search_articles` (quatrième outil MCP : périmètre et
   calendrier, après le gel du 15/10).

Ce que ce chapitre apporte aux épreuves : E1 (C1 cartographie, C4 Merise et RGPD, retouches de la v2 du
15/10), E3 (C10 outils MCP et matrice d'accès, C12 les 32 cas), E4 (C14 spécifications, C15 flux), E5
(C20 journal d'audit). Détail dans l'annexe A de la version complète.

## 📖 Glossaire

- **Matrice d'accès** : tableau acteur × ressource ; une case absente vaut refus.
  Décision D7 du 06/11/2026 : la documentation de l'API (`/docs`, `/redoc`, `/openapi.json`) y est ajoutée comme
  ressource publique (`evidence/C17/decision-D7-documentation-publique-2026-11-06.md`).
- **MCD / MPD** : modèle conceptuel (entités, relations) et modèle physique (tables, contraintes, index).
- **Upsert** : insérer ou mettre à jour, sans jamais supprimer.
- **Zone sous garde** : fichier du dépôt qu'on ne modifie qu'après un plan écrit et validé (`AGENTS.md`).
- **Text-to-SQL** : génération de requêtes SQL par un modèle à partir d'une question ; écartée ici.

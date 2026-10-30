# Rapport E4 : réaliser une application intégrant un service d'IA (C14 à C19)

> **Version 0.7 du 30/10/2026, première version complète, après une relecture globale.** Les huit sections sont écrites ;
> une relecture indépendante a confronté chaque fait au dépôt et à GitHub, et ses constats importants sont corrigés. Compte des critères : `docs/rapports/E4/recomptage-criteres-2026-10-30.md`.
>
> **Périmètre, décidé par Era le 30/10/2026** : E4 décrit la version de RITA présentée au jury, avec ses cinq écrans
> intégrés (portefeuille, indicateurs, briefing, question, tableau de bord). Les ateliers et copies d'exercice des
> sprints restent hors du rapport. **Version de référence** : commit `d3a4198` de `main` (tags `livrable-E1-v3` et
> `livrable-E3-v2`), livré en production le 27/10/2026 (`ETAT.md` : `/health` de production annonçait `d3a4198` ce
> jour-là). Pour chaque écran, on distingue ce qui est réalisé, la spécification conservée et ce qui n'est pas vérifié.

## 1. Le besoin et les utilisateurs (C14)

### 1.1 Le problème de départ

Avant RITA, je suivais des valeurs boursières dans un classeur Excel développé avec un ami. RITA prolonge ce travail en
réunissant les données et les actualités dans une application, avec des contrôles et une traçabilité. Elle collecte les
cours, les taux de change et les articles, les range dans une base PostgreSQL, les expose par une API, et les montre
dans des écrans web. Elle peut aussi rédiger un court **briefing** en français sur une valeur, et répondre à une
question sur les articles collectés, avec un modèle de langage. Une **action** est une part d'une société cotée en
bourse ; son **ticker** est son code de cotation, par exemple `MC.PA`.

RITA est conçue comme une aide à la lecture des marchés, sans recommandation d'achat ou de vente. C'est le périmètre
que j'ai choisi. Cette limite est affichée dans l'interface et contrôlée par des garde-fous (`guardrails/sortie.py`),
dont les limites sont documentées.

### 1.2 Le commanditaire et les utilisateurs

Le **commanditaire** est la personne qui exprime le besoin. Ici, c'est moi : RITA est mon projet fil rouge de la
formation, et la formation en fixe le cadre (les compétences C1 à C21).

RITA a deux sortes d'utilisateurs :

- **l'investisseur particulier** qui suit son portefeuille (rapport E1, « Acteurs ») : il ne cherche pas un conseil,
  il veut lire en une page la valeur de son portefeuille et ce qui se passe sur ses valeurs ;
- **l'exploitant**, la personne qui fait tourner le service : il veut savoir, sans lire les journaux techniques, si le
  service est en bonne santé.

RITA est un outil personnel, avec une clé d'API partagée pour les accès utilisateurs, sans droits par utilisateur.

Le fichier de démonstration (`data/positions-exemple.csv`) contient des positions simulées. Sur ses douze lignes, dix
sont valides et deux, volontairement corrompues, servent à tester le rejet des données incorrectes.

### 1.3 Les besoins, écran par écran

| Écran | Pour qui | Le besoin | Ce que l'écran ne fait pas | Spécification conservée |
|---|---|---|---|---|
| 1. Portefeuille | investisseur | voir en une page la valeur du portefeuille, calculée à partir des dernières données disponibles, convertie en euros, avec l'écart par rapport au prix d'achat | recommander d'acheter ou de vendre | US-1, 18/08 (écran versionné le 16/08) |
| 2. Indicateurs | investisseur | lire les treize indicateurs de chacune des 111 valeurs suivies, repérer celles dont la cotation est périmée | classer les valeurs, fixer un seuil, qualifier un niveau, recommander | US-2, 03/10, rétrospective |
| 3. Briefing | investisseur | saisir un ticker et lire un court briefing en français, rédigé à partir des données collectées, avec le verdict du garde-fou | recommander ; envoyer au modèle une donnée du portefeuille | US-3, 03/10, rétrospective |
| 4. Question | investisseur, évaluateur | poser une question et recevoir une réponse dont chaque affirmation renvoie à une source stockée | répondre hors de son corpus ; donner un conseil d'achat ou de vente (refus, avec son motif) | US1 et US2 de `docs/sprint-3/SPEC.md`, 15/10, avant l'écran (16/10) |
| 5. Tableau de bord | exploitant | lire l'état du service en mots simples, une carte par signal | présenter un état inconnu comme sain | aucune spécification fonctionnelle dédiée identifiée ; le comportement se lit dans la page et dans ses tests (`tests/test_tableau_de_bord.py`, `tests/test_smoke_tableau_de_bord.py`) |

Une **user story** décrit un besoin du point de vue de l'utilisateur. Celles des écrans 1 à 3 sont dans
`evidence/C14/` (`preuve-specifications-wireframes.md` pour US-1, `preuve-specifications-ecrans-2-et-3.md` pour US-2
et US-3) ; celles de l'écran 4 sont dans `docs/sprint-3/SPEC.md`.

**Un parcours concret, l'écran 3** : choisir une valeur → demander un briefing → attendre (l'écran annonce une attente
indicative de 5 à 15 secondes) → lire le briefing, ou comprendre le message de refus ou d'erreur. Une clé refusée, une
panne technique et un texte retenu par le garde-fou sont trois situations différentes, et chacune a son message.

### 1.4 Modéliser les données et les parcours

**Les données** sont modélisées avec un **MCD** (modèle conceptuel de données) au formalisme **Merise** : 6 entités et
6 associations. C'est le même modèle que dans le rapport E1 (`evidence/C4/MCD-MERISE-RITA.png`). Il laisse de côté la
table `article`, qui porte pourtant les données de l'écran Question (choix du 11/08, `evidence/C4/preuve-mcd-merise.md`,
§ 4) : pour les cinq écrans, le modèle de données est donc incomplet. Je ne l'ai pas refait
pour E4 : un second modèle des mêmes données serait un doublon à tenir à jour, donc une future contradiction.

**Les parcours** sont modélisés par des **wireframes d'état**. Un wireframe est un croquis d'écran, sans couleurs ni
graphisme définitif. Pour les trois premiers écrans, je dessine les quatre situations où l'utilisateur peut le
trouver :

| Écran | Les quatre états |
|---|---|
| Portefeuille et indicateurs | aucune clé · chargement · erreur · données |
| Briefing | aucune clé · la demande · attente et pannes · le briefing |

Montrer les erreurs compte : un wireframe qui ne montre que le cas qui marche décrit une démonstration, pas une
application. Les trois wireframes sont dans `evidence/C14/` (`WIREFRAMES-C14-ecran-portefeuille.png`,
`-ecran-indicateurs.png`, `-ecran-briefing.png`). **Les écrans 4 et 5 n'ont pas de wireframe.**

### 1.5 Des spécifications vérifiables

Les user stories des écrans 1 à 3 suivent le même plan ; celles de Question ont des critères d'acceptation, mais leurs
scénarios ne sont pas formalisés. Le plan : le **contexte**, les **scénarios d'utilisation**, puis les **critères
d'acceptation**. Un critère d'acceptation est une condition vérifiable pour dire que la story est terminée. Chacun
renvoie à un test automatisé ou à une lecture du code.

| Écran | Scénarios | Critères d'acceptation |
|---|---|---|
| 1. Portefeuille (US-1) | 5 | 11 |
| 2. Indicateurs (US-2) | 9 | 15 |
| 3. Briefing (US-3) | 8 | 14 |
| 4. Question (US1 et US2 du 15/10) | décrits dans le texte des stories, pas en tableau | 13 (CA1.1 à CA1.8, CA2.1 à CA2.5) |
| 5. Tableau de bord | aucune spécification fonctionnelle dédiée identifiée ; le comportement se lit dans la page et dans ses tests | idem |

Les scénarios couvrent aussi les cas qui ne marchent pas : clé refusée, serveur arrêté, valeur inconnue, texte retenu
par le garde-fou. Par exemple, pour l'écran 1 : une clé refusée n'est pas une panne, on l'oublie et on la redemande ;
un serveur qui ne répond pas a son propre message, parce qu'il n'y a aucun code HTTP à lire.

### 1.6 L'accessibilité dans les critères d'acceptation

Les objectifs d'accessibilité sont des critères d'acceptation, au même titre que les chiffres. Ils s'appuient sur le
**RGAA** (Référentiel général d'amélioration de l'accessibilité), le standard français, avec le numéro de la règle.
Quelques objectifs de l'écran 1 :

| Objectif d'acceptation | Règle RGAA | Dans le code | Vérifié |
|---|---|---|---|
| Chaque changement de statut est annoncé par un lecteur d'écran | 7.5 | `role="status"`, `aria-live="polite"` | balisage présent ; restitution vocale non vérifiée |
| Chaque cellule du tableau est rattachée à son en-tête | 5.7 | `scope="col"`, `scope="row"` | balisage présent |
| Le tableau a un titre lisible par un lecteur d'écran | 5.4 | `<caption>` | balisage présent |
| La performance se lit sans percevoir la couleur | 3.1 | le signe + ou − est toujours affiché | lecture du code |

Pour le tableau de bord, des tests vérifient la présence des attributs et éléments HTML associés à la langue de la
page (RGAA 8.3), au champ de la clé (11.1) et à la navigation (12.6) (`tests/test_tableau_de_bord.py`). Ils vérifient le
balisage, pas l'intégralité des critères RGAA correspondants. La spécification de l'écran de question n'a aucun
critère d'accessibilité.

Un **lecteur d'écran** est un logiciel qui lit la page à voix haute pour une personne aveugle. L'audit automatique
local du 03/10 (Lighthouse, application servie sur le poste, briefing enregistré pour l'écran 3) a obtenu 100 sur 100
en accessibilité sur les états testés des écrans 1 à 3 (`evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md`).
Il ne démontre ni l'accessibilité de la production actuelle, ni une conformité complète au RGAA, et il n'a pas mesuré
les écrans 4 et 5. Il reste à compléter par des vérifications manuelles, notamment avec un lecteur d'écran.

### 1.7 Les limites, dites franchement

- **Les documents conservés ne prouvent pas que toutes les spécifications ont précédé le code.** Le premier écran est
  versionné le 16/08 (commit `634e8e4`), sa spécification le 18/08 (`0c8b8f5`). Pour les écrans 2 et 3, les
  spécifications sont explicitement rétrospectives : écrites le 03/10, après le code. Pour l'écran 4, la
  spécification initiale précède sa réalisation (15/10, puis l'écran le 16/10) ; elle a ensuite été révisée le 16/10,
  après mesure.
- Écrire ces critères a quand même fait trouver **un défaut réel** : l'écran 3 garde la clé d'API avant d'avoir vérifié
  qu'elle fonctionne (carte #73, toujours ouverte le 30/10), et **deux références RGAA inexactes** dans la
  spécification de l'écran 1, corrigées par un erratum daté, sans réécrire l'original.
- **Pour l'écran 5, aucune spécification fonctionnelle dédiée n'est identifiée** (son comportement se lit dans la
  page et dans ses tests), et sa page affiche encore « Prototype local du sprint 5 »,
  alors qu'elle est en production. Les écrans 4 et 5 n'ont pas de wireframe.
- **Aucun test avec un lecteur d'écran réel**, et aucun test documenté avec un utilisateur cible extérieur au projet.
- L'amélioration de ma méthode : formaliser les critères d'acceptation, accessibilité comprise, avant les prochains
  développements.

### 1.8 Travaux restants avant de finaliser C14

La grille de C14 demande que **chaque** spécification couvre contexte, scénarios et critères de validation, et que
l'accessibilité soit dans les critères d'acceptation. Pour les cinq écrans, il manque encore :

- les **parcours** formalisés des écrans Question et Tableau de bord (un schéma de parcours peut suffire) ;
- la **spécification fonctionnelle** du Tableau de bord : contexte, scénarios, critères d'acceptation ;
- les **critères d'accessibilité** dans les critères d'acceptation des écrans Question et Tableau de bord ;
- la table `article` dans le modèle de données, puisqu'elle porte les données de Question.

Ces compléments seront datés du jour de leur écriture et présentés comme rétrospectifs. Tant qu'ils manquent, C14
n'est pas entièrement démontré pour le périmètre des cinq écrans.

## 2. Le cadre technique (C15)

### 2.1 L'architecture en une vue

RITA est une application pour un seul utilisateur. Elle **collecte** des données de marché et d'actualité, les
**range** dans PostgreSQL, les **expose** par une API REST, et fait **rédiger** par un modèle de langage fourni (aucun
entraînement) un briefing sur une valeur ou une réponse à une question, avec ses sources (`docs/ARCHITECTURE.md`, § 1,
état du 24/10). Une **API REST** est un service web qui répond à des adresses précises avec des données, ici en JSON.

Cinq chemins traversent l'application :

| Chemin | De → vers |
|---|---|
| Collecte | sources externes → `pipelines/ingest.py` → PostgreSQL et index des articles |
| Lecture de données | écran → `GET /donnees/*` → PostgreSQL |
| Briefing | écran → `POST /briefing` → graphe (lecture de la base, recherche d'articles, rédaction) → modèle → garde-fou → réponse |
| Question | écran → `POST /question` → garde-fous de la question → recherche dans les articles → modèle → contrôles → réponse avec ses sources, ou refus |
| Surveillance | vigie → `/health` puis `/sante` → une issue GitHub par signal en problème |

Le schéma de référence est `docs/rapports/E3/schemas/E3-architecture.png`, refait le 24/10 : il montre les deux chemins
vers le modèle (`/briefing` et `/question`), les cinq écrans et `/sante` avec son tableau de bord. La vigie, qui tourne
hors de l'API, n'y figure pas.

### 2.2 Les briques et les dépendances

| Brique | Rôle | Technologie |
|---|---|---|
| Collecte (`pipelines/`, `sources/`) | six étapes indépendantes ; une étape en échec n'arrête pas les autres | Python, `httpx`, `feedparser`, `yfinance` |
| Base (`db/`) | schéma Merise : 10 tables, 1 vue ; rôles, dont `rita_lecture` en lecture seule | PostgreSQL 18 |
| Indicateurs (`indicateurs/`) | 13 indicateurs par valeur ; calculs SQL et traitements Python, dont le RSI de Wilder | SQL (fonctions fenêtre), Python |
| Recherche (`rag/`) | index des articles, recherche hybride (sens et mots-clés) | ChromaDB |
| Graphe (`graph/`) | trois étapes fixes : lire la base, chercher les articles, rédiger | LangGraph |
| Appel au modèle (`src/llm.py`) | un ordre de fournisseurs ; le suivant n'est essayé que si le premier échoue | Azure AI Foundry en premier |
| Garde-fous (`guardrails/`) | relisent la question, les articles collectés et le texte produit | Python |
| API (`api/`) | 19 chemins le 24/10, contrat OpenAPI 3.1.0 publié sur `/docs`, clé d'API | FastAPI |
| Interface (`frontend/`) | cinq écrans, aucune clé dans le code | HTML, CSS, JavaScript sans outil de construction |
| Traçage (`src/traces.py`) | une trace par briefing ou question | Langfuse, région UE |
| Vigie (`monitorage/`) | compteurs, seuils écrits, tableau de bord | Python |
| Déploiement (`deploy/`) | livrer, revenir à la version précédente, ingérer | Python, Docker Compose |

**Les dépendances.** L'image qui tourne en production s'installe depuis `requirements-api.txt` : ses 13 dépendances ont
une version fixée. Le fichier de développement `requirements.txt` ne l'est pas : sur 19 lignes, 12 n'ont pas de version
et une n'a qu'une borne basse (limite reprise en C17).

### 2.3 Les environnements

| Environnement | Ce qui tourne | Comment |
|---|---|---|
| Poste de développement | API (port 8000), PostgreSQL (port 5433), collecte planifiée chaque soir | `uvicorn`, tâche planifiée Windows |
| Pré-production locale | API et PostgreSQL en conteneurs | `docker compose up -d --build` (port 8001) |
| Intégration continue | lint, secrets, tests, garde-fous, construction et vérification de l'image | GitHub Actions, sept workflows (`docs/CI-CD.md`) |
| Production | API en conteneur derrière Caddy (HTTPS), serveur Hetzner | livrée automatiquement après chaque fusion dans `main`, depuis le 14/10 |

Un **conteneur** est un paquet qui contient l'application et tout ce qu'il lui faut pour démarrer, isolé du reste de
la machine ; une **image** est le modèle à partir duquel on lance un conteneur.

### 2.4 Le flux de données

Le diagramme de flux est `evidence/C15/FLUX-DONNEES-C15-application-RITA.png`. Il se lit dans le sens de la donnée,
pas dans celui de la requête : la flèche qui va de l'API au navigateur descend, alors que c'est le navigateur qui
déclenche l'appel.

| Flux | De → vers | Nature |
|---|---|---|
| Collecte | sources → ingestion | brut, non fiable |
| Écriture | ingestion → PostgreSQL | dédoublonné, homogénéisé, rejets tracés |
| Lecture | PostgreSQL → API | lecture des données métier ; certains appels produisent aussi une écriture dans le journal d'audit |
| Réponse | API → navigateur | JSON, protégé par la clé d'API |
| Briefing | API → graphe → modèle | encadré par les garde-fous |
| Question | écran → API → modèle | la question est envoyée au modèle, jamais gardée par RITA |

Deux traitements du registre RGPD passent par ces flux. **T1**, les positions : le fichier, la table `position` et
l'écran du portefeuille. **T8**, les questions posées dans l'écran Question, actif depuis le 16/10 : le texte d'une
question peut contenir une donnée personnelle ; il est envoyé au modèle (Azure, zone UE) et n'est jamais gardé par
RITA. Rien du portefeuille n'est envoyé au modèle : l'étape qui lit la base
pour le briefing ne lit que des données de marché publiques (`docs/ARCHITECTURE.md`, § 5).

### 2.5 Des choix éco-responsables, par effet

| Choix | Effet |
|---|---|
| Interface sans cadre ni outil de construction | aucun paquet JavaScript à télécharger, aucune étape de compilation |
| Pagination plafonnée à 1 000 lignes (`api/donnees.py`, `LIMITE_MAX`) | une requête ne peut pas transférer toute la table des cotations |
| Archive Parquet compressée et partitionnée | dix ans d'historique en 14 Mo (mesure du 18/08) |
| `pyspark` hors de l'image | 492 Mo de moins dans l'image (mesure du 18/08) |
| En fonctionnement nominal, un appel au modèle suffit pour rédiger le briefing | en cas d'échec, d'autres tentatives sont possibles selon la configuration des fournisseurs |

Ces choix sont éco-responsables **par effet** : aucun n'a été fait d'abord pour l'environnement. L'hébergeur, Hetzner
(serveur CX23, 7,19 € par mois), a été choisi le 19/08 pour une raison de continuité : un serveur payé ne s'éteint pas
avant le jury, contrairement aux offres gratuites qui expiraient avant le 05/11 (`CONTINUITE.md`, décisions). Son
impact environnemental n'a pas été un critère du choix.

### 2.6 La preuve de concept et la pré-production

**La preuve de concept du 18/08** (`evidence/C15/preuve-preproduction-docker.md`) : l'image se construit (595 Mo),
démarre seule et répond en moins de 20 secondes, refuse une demande sans clé (403) et sert les données avec la clé
(200). Elle tourne durcie : utilisateur sans privilèges, système de fichiers en lecture seule, base non exposée hors du
réseau des conteneurs. **Avis écrit ce jour-là : « Poursuivre. »** Ses limites étaient dites : pré-production
locale, base vide, aucun déploiement automatisé.

**Ce qui a changé depuis, daté.** Depuis le 14/10, chaque version est livrée en production automatiquement après une
fusion dans `main`, et elle passe d'abord une pré-production sur le serveur : un conteneur d'essai sur le port 8003,
avec le compte de base `rita_lecture` en lecture seule, contrôlé avant la bascule, puis toujours arrêté
(`deploy/deployer.py`, `_essai_en_preproduction`). La première livraison, le 14/10, a pris 221 secondes de l'ordre à la
fin des contrôles (`evidence/sprint-2/N0-premiere-livraison-2026-10-14.md`). Les limites « pré-production
locale » et « aucun déploiement automatisé » du 18/08 sont donc levées ; la pré-production locale du poste existe
toujours à côté. La conclusion « Poursuivre » reste valable, mais elle date d'avant la mise en production.

### 2.7 Les limites, dites franchement

- **Le diagramme de flux est en retard sur l'application** : il date du 18/08 et ne montre ni le chemin des questions
  ni la vigie. Le schéma d'architecture, refait le 24/10, montre les deux chemins, mais pas la vigie.
- **L'hébergeur n'a pas été choisi sur un critère environnemental**, et l'impact du serveur n'est pas mesuré.
- **`requirements.txt` n'est pas épinglé** (12 lignes sans version, une borne basse) ; seule l'image l'est.
- **La taille de l'image (595 Mo) date du 18/08** et n'a pas été remesurée.
- **La production n'a pas été revérifiée en direct pour ce rapport** : la version de référence est celle annoncée par
  `/health` le 27/10, d'après `ETAT.md`.
- **Le dossier `evidence/C15/` n'a pas été mis à jour depuis le 04/10** : la pré-production réelle est prouvée ailleurs
  (`deploy/`, `evidence/sprint-2/`).

## 3. Coordonner en agile (C16)

### 3.1 La méthode et pourquoi

RITA a un seul développeur. J'ai choisi **Kanban** plutôt que Scrum, le 26/09 (`docs/PILOTAGE-AGILE.md`). Scrum suppose
une équipe, des rôles distincts et des cérémonies de groupe ; Kanban garde ce qui sert à une personne seule : un flux de
travail visible, une limite au travail en cours (deux cartes « En cours » au plus) et une revue régulière. Un
**burndown**, le graphique du travail restant dans un sprint, n'est pas suivi : il suppose un engagement de sprint,
que Kanban n'a pas.

| Rôle | Qui | Responsabilité |
|---|---|---|
| Porteur du produit et développeur | moi | ordonne le travail, décide, développe, rédige les livrables |
| Partie prenante, relecteur | le formateur | lit le dépôt, reçoit les livrables envoyés et y répond |
| Revue automatisée | le workflow `revue-pr.yml`, sur les pull requests vers `main` | commente avant la fusion |
| Assistant de développement | un assistant d'IA | propose et écrit à ma demande ; ne décide pas |

### 3.2 Les cycles, tels qu'ils ont eu lieu

| Période | Organisation | Trace |
|---|---|---|
| depuis le 16/08 | un plan en semaines, de S34 à S45, chacune avec un objectif | `docs/PLAN-12-SEMAINES.md` |
| 26/09 au 14/10 | Kanban : un cycle par semaine du plan | tableau GitHub « RITA - Pilotage Kanban » |
| 12 au 26/10 | cinq cycles courts : un cadrage, puis quatre cycles avec une livraison en production et un tag ; trois ont un plan de travail découpé en tâches dans le dépôt | `docs/sprint-2/PLAN-TRAVAIL.md` à `docs/sprint-4/PLAN-TRAVAIL.md` ; 66 pull requests fusionnées (41 vers `develop`, 25 vers `main` ; une même modification passe souvent par les deux) |
| depuis le 27/10 | les rapports, un livrable à la fois | `docs/FILE-DE-VALIDATION.md` |

### 3.3 Les outils de pilotage

- **Le tableau Kanban** (GitHub Projects) : 34 cartes, dont 16 « Fait », 15 « Backlog », 2 « Cette semaine », 1 « En
  cours ». Le dernier mouvement de carte constaté date du 14/10 à 19:56 (UTC). Le tableau ne reflétait pas
  systématiquement tout le travail réalisé.
- **Le backlog** : les issues du dépôt, avec des étiquettes par livrable (`E2` à `E5`, `veille-C6`, `decision-era`).
- **Les plans de travail** des cycles courts : 73, 86 et 62 tâches en listes à cocher.
- **`ETAT.md`** pour la prochaine action et l'état du jour, et **`CHANGELOG.md`** pour les décisions et les livrables :
  du 12 au 26/10, 40 commits ont modifié `ETAT.md` et 29 ont modifié `CHANGELOG.md` (des commits, pas des réunions) ;
  mes notes de journal, pour reprendre le travail.
- **Les sessions avec l'assistant** : j'y choisissais et validais la tâche suivante.

### 3.4 Les rituels et le partage avec les parties prenantes

| Rituel | Ce qui a eu lieu | Trace |
|---|---|---|
| Revue du lundi (avancement, blocages, priorités) | tenue, sans compte rendu, selon ma déclaration du 30/10 | aucune : la trame du 05/10, préparée le 03/10, porte la mention « revue NON TENUE », écrite avant la date, et elle est restée vide ; aucun document ne dit ce qui s'est passé ensuite |
| Revue de pull request | les pull requests vers `main` déclenchent une revue automatisée et doivent passer six contrôles ; GitHub n'exige pas d'approbation humaine. Selon ma méthode, je lis la revue avant de fusionner moi-même | les pull requests sur GitHub ; `docs/PILOTAGE-AGILE.md`, § 5 |
| Point formateur | à chaque livrable envoyé : le lien du tag, puis le retour du formateur | `docs/FILE-DE-VALIDATION.md` |

**Les envois au formateur, statut par statut.** La file de validation compte neuf lignes, mais pas neuf échanges :

| Statut | Lignes |
|---|---|
| envoyé, avec réponse | E1 v1 (début août, relu avant le gel, trois réponses écrites) ; E1 v3 (envoyé le 28/10, accepté selon la réponse sur Discord que j'ai rapportée, capture encore à joindre) |
| envoyé, réponse attendue | grilles des compétences (28/10) ; E3 v1.9 (29/10) |
| non envoyé | protocole de veille, conception des indicateurs, note de veille S33 ; E1 v2.6 et E3 v1.5, remplacés par les versions suivantes |

**L'accès des parties prenantes.** Au dépôt : le formateur y a un accès en lecture (compte `bybysker`), vérifié le
30/10. Au tableau : un accès en lecture lui a été donné le 26/09 (`docs/PILOTAGE-AGILE.md`), non revérifié le 30/10.
La méthode est écrite dans le dépôt ; un fichier présent dans le dépôt ne prouve pas, à lui seul, que ses règles ont été
partagées et comprises. Le jury recevra un accès en lecture au moment de l'évaluation.

### 3.5 Un exemple de coordination, de bout en bout

| Étape | Ce qui s'est passé | Trace |
|---|---|---|
| Le constat | le 23/10, en relisant les rapports E1 et E3 contre le code de `main`, je trouve quatre défauts : une panne totale de collecte comptée comme réussie ; l'API des cotations limitée à environ quatre ans alors qu'E1 annonce dix ans ; des nombres non finis acceptés dans les positions ; un en-tête de migration trompeur | `CHANGELOG.md`, entrée du 24/10 à midi |
| La priorité | les corriger avant le gel d'E1 et d'E3, sans rien ajouter d'autre : le rapport E1 annonçait dix ans de cours joignables par l'API (C5), et ce n'était pas vrai | description de la pull request #138 |
| La tâche | quatre correctifs bornés, tests d'abord : 21 tests, dont 15 rouges avant le code | pull request #138 vers `develop` |
| La livraison | pull request #139 vers `main`, fusionnée par moi ; livraison N18 en production le 24/10, de 11 h 48 à 11 h 57 | exécution GitHub Actions 40083432816, commit `b547cbf` |
| La vérification | `/health` de production annonce `b547cbf` ; la CI montre 1 700 tests réussis | `CHANGELOG.md`, même entrée |

Le même travail a fait découvrir un autre manque, écrit le jour même : la sauvegarde n'est pas tenue (dernier dump le
27/09).

### 3.6 Les limites, dites franchement

- **Le tableau n'a plus bougé après le 14/10**, et il ne reflétait pas tout le travail avant. Pendant les cycles
  courts, les tâches ont été suivies dans les plans de travail, dans `ETAT.md` et mes notes, et avec l'assistant. Sur
  les huit issues ouvertes du 12 au 26/10, sept viennent de la surveillance automatique ; la #152 est une carte de correction.
- **Les cases des plans de travail ne sont pas cochées dans le dépôt** (0 sur 221). Cela montre que les listes n'ont
  pas été entretenues, pas que le travail n'a pas été fait : l'avancement se lit dans les pull requests et dans
  `ETAT.md`.
- **Sur les 66 pull requests fusionnées du 12 au 26/10, sept mentionnent une issue** (#111, #138, #139, #146, #147,
  #153, #157), et aucune ne la ferme automatiquement, alors que la méthode le prévoit (`Closes #N`).
- **Les revues du lundi n'ont aucun compte rendu** ; la méthode prévoyait de l'écrire en tête d'`ETAT.md`. Je ne le
  reconstitue pas après coup.
- **Pas de rétrospective écrite** à la fin des cycles.
- **L'organisation agile ne couvre que la fin du projet** : avant le 26/09, il n'y avait que le plan en semaines.
- **C16 n'est donc pas entièrement démontré** : le suivi dans la durée a des interruptions, et le partage des rituels
  avec les parties prenantes repose surtout sur des documents.

## 4. Développer (C17)

### 4.1 Vue d'ensemble

Je distingue « j'ai une preuve » et « tout le critère est satisfait ».

| Critère C17 | État | Où |
|---|---|---|
| 1. Environnement de développement conforme | partiel | § 4.2 |
| 2. Interfaces conformes aux maquettes | partiel | § 4.3 |
| 3. Comportements et navigation conformes | partiel : scénarios testés, un défaut ouvert | § 4.3 |
| 4. Composants métier conformes | implémentés et testés ; conformité partielle, défauts ouverts | § 4.4 |
| 5. Droits d'accès | partiel | § 4.5 |
| 6. Flux de données intégrés | prouvé : briefing (03/10) et Question (évaluation en production du 16/10) | § 4.4 |
| 7. Éco-conception | pratiques documentées et mesures historiques sur trois écrans | § 4.7 |
| 8. Préconisations OWASP | partiel | § 4.6 |
| 9. Tests des composants et des accès | résultats prouvés, avec leurs exclusions | § 4.8 |
| 10. Sources versionnées sur un dépôt distant | prouvé | § 4.9 |
| 11. Documentation technique | partiel : contenu complet ; accessibilité non contrôlée ; une affirmation fausse à la version de référence, corrigée le 30/10 | § 4.9 |

### 4.2 L'environnement de développement (critère 1, partiel)

Les treize dépendances directes de l'API sont épinglées (`requirements-api.txt`). L'intégration continue tourne sur une
machine fixée (`ubuntu-24.04`) avec Python 3.13 ; sur mon poste, j'utilise Python 3.14. La reproductibilité complète
de l'environnement reste à améliorer : l'image Python, les paquets système et les dépendances indirectes ne sont pas
entièrement verrouillés ; le fichier de développement `requirements.txt` a 12 lignes sans version et une borne basse
(`mcp>=2.1.1`) ; la CI installe trois paquets sans version (`playwright`, `giskard-llm`, `giskard-checks`). La carte #23
suit l'épinglage.

### 4.3 Les interfaces et la navigation (critères 2 et 3)

L'interface est en **HTML, CSS et JavaScript sans outil de construction** : cinq pages (`frontend/`), aucune clé
écrite dans le code, la clé saisie par l'utilisateur et gardée le temps de l'onglet.

**Conformité aux maquettes (critère 2, partiel).** Les trois premiers écrans ont un wireframe, dessiné après l'écran :
il ne prouve ni qu'une maquette a guidé le développement, ni que l'écran actuel lui est conforme. Les écrans Question
et Tableau de bord n'ont pas de maquette. Une refonte des trois premiers écrans a été conçue et validée le 04/10
(`docs/conception/frontend/refonte-2026-10.md`), mais elle n'est pas implémentée.

**Comportements et navigation (critère 3, partiel).** Des scénarios de fonctionnement sont vérifiés, notamment dans un
navigateur :

| Fichier de test | Fonctions de test | Ce qu'il vérifie |
|---|---|---|
| `tests/test_frontend.py` | 69 | surtout le contenu des pages, lu comme du texte, et leur desserte par l'API |
| `tests/test_smoke_ui.py` | 11 | de vrais gestes dans un navigateur ; plusieurs réponses de l'API y sont simulées |
| `tests/test_smoke_tableau_de_bord.py`, `tests/test_tableau_de_bord.py` | 13 et 11 | le tableau de bord, dont son balisage d'accessibilité |

La conformité complète aux spécifications reste partielle : l'écran du briefing garde la clé dans l'onglet avant
d'avoir vérifié qu'elle fonctionne (carte #73, `frontend/briefing.js`, ligne 213), ce qui contredit un critère
d'acceptation de sa user story. Le commentaire juste au-dessus du code dit le contraire, à corriger avec le défaut.

### 4.4 Les composants métier et les flux de données (critères 4 et 6)

| Composant | Rôle | Tests |
|---|---|---|
| Indicateurs (`indicateurs/`) | 13 indicateurs par valeur et 2 pour le portefeuille ; calculs SQL et traitements Python, dont le RSI de Wilder | `test_indicateurs_socle` (13), `_portefeuille` (14), `_risque` (19) |
| Graphe du briefing (`graph/`) | trois étapes LangGraph : lire la base, chercher les articles, rédiger | `test_workflow` (11) |
| Rédacteur (`agents/analyst.py`) | construit le prompt du briefing : cours, variation, capitaux, dix indicateurs, extraits d'articles, consigne de ne rien recommander | `test_analyst` (14) |
| Question (`agents/question.py`, `api/question.py`) | une chaîne à part : recherche dans les articles, génération en format imposé, contrôles de la réponse ; les références affichées viennent des données stockées | `test_api_question` (15) |

**Deux parcours, deux chaînes.** Le briefing utilise le graphe LangGraph (`graph/workflow.py`). Le parcours Question
suit une chaîne distincte de recherche documentaire, de génération et de validation (`agents/question.py`). Dans les
deux cas, des contrôles interviennent avant et après la génération. Preuves des écrans indicateurs et briefing :
`evidence/C10/`. Le parcours Question est vérifié par des tests d'intégration où la recherche documentaire et le
modèle sont simulés (`tests/test_api_question.py`), et par une évaluation en production le 16/10, sur la livraison N6
(`72dba4d`) : huit questions, cinq appels au modèle, trois refus avant tout appel, verdicts relus par moi
(`evidence/sprint-3/evaluation-production-2026-10-16-relecture.md`). Ces deux preuves sont antérieures à la version de
référence.

**Deux défauts d'indicateurs restent ouverts**, trouvés le 04/10 : le RSI vaut 100 sur une série plate (carte #78), et
la pire baisse sur un an peut être positive quand le cours ne fait que monter (carte #79).

### 4.5 Les droits d'accès (critère 5, partiel)

| Règle | Dans le code |
|---|---|
| La clé est posée sur des routeurs entiers : une route ajoutée à un routeur protégé hérite de la protection | `api/main.py`, lignes 260, 267 et 271 |
| La clé est comparée à temps constant | `secrets.compare_digest`, ligne 201 |
| Les refus d'accès 403 liés à la clé RITA sont journalisés (identifiant de requête, route, motif), jamais la clé | ligne 206 |
| Les deux routes qui appellent le modèle partagent une limite : 10 appels par minute à elles deux, par défaut ; 429 au-delà | ligne 267, `api/limiteur.py` |
| Les exercices de panne ont leur propre clé : clé du client absente ou incorrecte, 403 ; clé d'exercice non configurée sur le serveur, 503 | ligne 275, `api/exercice.py` |
| La clé n'a aucune valeur par défaut et doit compter au moins 16 caractères. L'application peut démarrer sans clé configurée, mais elle ne peut pas autoriser les accès protégés : la configuration est contrôlée lors de l'authentification. Docker Compose exige une valeur non vide avant de lancer le conteneur | `api/main.py`, lignes 161 à 201 ; `docker-compose.yml`, ligne 81 |

Il n'y a qu'**une clé partagée pour les accès utilisateurs**, sans droits par utilisateur : c'est un choix pour un
outil personnel, défendu avec son modèle de menace (`evidence/C17/preuve-droits-acces-2026-10-03.md`).

**Ce qui n'est pas conforme** : la matrice des droits validée donne à l'API une lecture limitée des données et une
écriture limitée au journal d'audit ; or l'API se connecte avec le rôle propriétaire (carte #76, ouverte). La
documentation interactive `/docs` est publique (constat S2).

### 4.6 La sécurité : la revue OWASP Top 10 (critère 8, partiel)

Le 03/10, j'ai relu le code contre l'**OWASP Top 10** (édition 2025), la liste de référence des risques des
applications web. Dix constats, S1 à S10 (`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`) :

| Constat | État au 30/10 |
|---|---|
| S4 : refus d'authentification non journalisés | corrigé (`api/main.py`, ligne 206) |
| S5 : ticker sans longueur maximale | corrigé : 20 caractères au plus (ligne 281) |
| S3 : aucune limite de débit | en partie : limite partagée sur `/briefing` et `/question` ; les essais de clé ne sont pas freinés |
| S7 : chaîne d'approvisionnement | en partie : recherche de secrets sur tout l'historique (`gitleaks`), machine de CI fixée ; dépendances de développement libres |
| S10 : certificat proche de l'expiration | renouvelé seul le 19/10, valable jusqu'au 17/01/2027 (`ETAT.md`) |
| S1 : aucun en-tête de sécurité | constaté en production le 03/10 ; aucun ajout dans le dépôt depuis ; la configuration actuelle du proxy n'a pas été revérifiée |
| S2 : `/docs` public | ouvert : décision qui me revient (D7), ces pages servent à la démonstration |
| S6 : panne de tous les fournisseurs | ouvert pour `/briefing` ; `/question` renvoie déjà 503 (`api/question.py`) |
| S8 : mots de passe par défaut | ouvert : le fichier Compose concerné est aussi utilisé en production (`deploy/deployer.py`), ce qui ne prouve pas que ces valeurs y servent |
| S9 : garde-fous sous le seuil de 85 % | ouvert : déclaré en échec attendu dans les tests, le seuil n'est pas baissé |

Les suivis sont séparés : la carte #75 pour le durcissement, #23 pour l'épinglage, une décision à prendre pour S2, et la
porte des évaluations pour S9.

### 4.7 L'éco-conception (critère 7)

Les pratiques sont documentées en section 2.5 (interface sans outil de construction, pagination plafonnée ; en
fonctionnement nominal, un appel au modèle suffit pour un briefing). Mesures historiques du 03/10, en local, sur trois écrans
(`evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md`) :

| Écran et état mesuré | EcoIndex |
|---|---|
| Portefeuille, avec ses données | A (90) |
| Briefing, mesuré avant l'arrivée du texte, avec une réponse du modèle enregistrée | A (90) |
| Indicateurs, avec ses 111 lignes | D (51) |

Un écran vide pèse 20 à 25 Ko, en 3 ou 4 requêtes, sans ressource externe. Ces mesures caractérisent des états de
pages précis : elles ne mesurent ni la consommation du modèle, ni celle du service complet. Les corrections relevées le
même jour ne sont pas faites (carte #74 : compression des réponses, `favicon.ico` en 404) ; il n'y a donc pas de mesure
« après », et les écrans Question et Tableau de bord n'ont pas été mesurés.

### 4.8 Les tests (critère 9)

Mesure du 30/10 sur le commit `6c3014a` (exécution 41129801486), postérieur à la version de référence `d3a4198` : entre
les deux, seuls des tests et des documents ont changé, pas le code de l'application.

**1 808 tests réussis, 32 ignorés, 2 en échec attendu.** Les 32 tests ignorés : 16 exigent une base PostgreSQL de test,
absente de la CI ; 9 ne tournent que sous Windows ; 1 exige une bibliothèque PDF ; 6 exigent l'archive Parquet ou
Spark. Les deux échecs attendus déclarent que les garde-fous n'atteignent pas leur seuil, sans le baisser.

**Couverture : 96,32 %** pour un seuil de 90 % (`.coveragerc`). Elle porte sur le périmètre Python configuré, pas sur
toute l'application : l'interface, `rag/` et `monitorage/` n'en font pas partie.

**Les accès ont leurs tests** : `test_limiteur` (7) et `test_exercice` (15) ont tourné. Les quatre tests du rôle
PostgreSQL en lecture seule (`test_role_lecture`) existent, mais ils font partie des tests ignorés dans cette
exécution : elle ne prouve pas leur réussite.

### 4.9 Les sources et la documentation (critères 10 et 11)

**Les sources** sont versionnées sur GitHub, dans le dépôt privé `Ganda15/rita-agent`. Le formateur y a un accès en
lecture. Chaque livrable est un tag `livrable-*` qu'on ne peut ni déplacer ni supprimer ; il y en a 18 le 30/10. Le
jury sera invité au moment de l'évaluation.

**La documentation technique** est rassemblée : `docs/ARCHITECTURE.md` (architecture, briques, points de terminaison,
règles d'accès, état du 24/10), `README.md` (« Lancer le projet », « Lancer les tests »), `docs/CI-CD.md` et
`docs/exploitation.md`. À la version de référence, `docs/ARCHITECTURE.md` (ligne 71), le message d'erreur et la
docstring de `api/main.py` disaient que l'API « refuse de démarrer » sans clé, alors que l'application peut démarrer
sans clé configurée ; la configuration est contrôlée lors de l'authentification. L'erreur, déjà corrigée dans le
rapport E3 le 11/10, l'est dans ces fichiers le 30/10 (commit `a2c0d51`), après la version de référence.

### 4.10 Les limites, dites franchement

- **L'environnement n'est pas entièrement reproductible** : `requirements.txt` libre, trois paquets de CI sans
  version, dépendances indirectes non verrouillées.
- **Aucun écran n'a été construit à partir d'une maquette préalable** ; Question et Tableau de bord n'en ont pas ; la
  refonte validée le 04/10 n'est pas implémentée.
- **Des défauts ouverts** : la clé gardée avant d'être vérifiée (#73), deux indicateurs (#78, #79), le rôle
  propriétaire de l'API (#76).
- **Sécurité** : en-têtes absents en production au 03/10 et non revérifiés depuis (S1), `/docs` public (S2), panne
  des fournisseurs du briefing (S6), mots de passe par défaut (S8), garde-fous sous leur seuil (S9).
- **Les tests** : 32 ignorés en CI, dont les tests du rôle en lecture seule ; une couverture qui exclut l'interface,
  la recherche documentaire et la surveillance.
- **L'éco-conception** n'a que des mesures historiques, sans mesure « après », sur trois écrans sur cinq.
- **La documentation** contenait, à la version de référence, une affirmation fausse sur le démarrage de l'API
  (corrigée le 30/10) ; elle n'a pas été contrôlée avec un outil d'accessibilité ; le diagramme de flux date du 18/08 ;
  `docs/EXPLOITATION.pdf` (11/10) ne correspond plus à la page.

## 5. Automatiser les tests (C18)

### 5.1 La chaîne d'intégration continue

L'**intégration continue** lance automatiquement les contrôles et les tests à chaque envoi de code. Pour RITA, c'est
**GitHub Actions**, l'outil du dépôt : il n'y a rien à installer à côté, et les règles de la branche principale
peuvent exiger ses résultats.

| Workflow | Déclencheur | Ce qu'il fait |
|---|---|---|
| `test.yml`, Tests | chaque envoi et chaque pull request sur `main` et `develop` | deux travaux : `pytest` (la suite et la couverture) et `evals` (les portes des garde-fous) |
| `livraison.yml`, Livraison | chaque envoi et chaque pull request sur `main` et `develop`, chaque tag `livrable-*` | `lint` (`ruff`), `secrets` (`gitleaks` sur tout l'historique), puis la construction et la vérification de l'image (section 6) |
| `revue-pr.yml`, Revue PR | chaque pull request vers `main` | une revue automatisée commentée sur la pull request |

Il y a sept workflows en tout (`.github/workflows/`) ; les quatre autres servent la surveillance, l'évaluation des
garde-fous, le retour arrière et l'ingestion (`docs/CI-CD.md`, § 3).

### 5.2 Les étapes, dans l'ordre

Le travail `pytest` de `test.yml` tourne sur une machine fixée (`ubuntu-24.04`), avec Python 3.13 :

1. installer les dépendances (`requirements.txt`) ;
2. installer le navigateur du test d'écran (Playwright) et les outils de l'évaluation des garde-fous ;
3. **tester d'abord les données** (collecte, nettoyage, import, RGPD) : le 30/10, 296 réussis et 3 ignorés, en
   7 secondes ; une erreur sur les données se voit avant le reste ;
4. lancer toute la suite et mesurer la couverture, avec un seuil de 90 % (`.coveragerc`).

### 5.3 Les tests tournent à chaque déclenchement

Le 30/10, sur le commit `6c3014a` (exécution 41129801486) : **1 808 tests réussis, 32 ignorés, 2 en échec attendu**,
couverture **96,32 %** sur le périmètre Python configuré. Les 32 tests ignorés et les 2 échecs attendus sont expliqués
en section 4.8.

La branche principale ne change que par une pull request, et GitHub exige six contrôles verts avant la fusion : `lint`,
`pytest`, `evals`, `revue`, `secrets`, `construire-et-publier` (règle `main protegee`, lue le 30/10, sans contournement
possible). Une pull request dont un contrôle est rouge ne peut donc pas entrer dans `main`.

### 5.4 Les configurations sont versionnées

Les sept workflows sont dans le dépôt (`.github/workflows/`), comme les règles de lint (`ruff.toml`), de couverture
(`.coveragerc`) et de recherche de secrets (`.gitleaks.toml`). La version de `ruff` est la même dans la CI et dans
`requirements.txt`, et un test le vérifie (`tests/test_lint_config.py`).

### 5.5 La documentation de la chaîne

`docs/CI-CD.md` rassemble tout en un endroit : les déclencheurs (§ 2), les étapes workflow par workflow (§ 3), les
secrets et les permissions (§ 4), comment installer la chaîne sur un dépôt neuf (§ 5), comment la tester avant de
compter dessus (§ 6), et quoi faire quand elle est rouge (§ 7). Le document est en Markdown, lisible sur GitHub ; son
accessibilité n'a pas été contrôlée avec un outil.

### 5.6 Les limites

- Trois paquets installés par la CI n'ont pas de version fixée (`playwright`, `giskard-llm`, `giskard-checks`), et
  `requirements.txt` non plus (section 4.2).
- 32 tests sont ignorés en CI, dont les 16 qui exigent une base PostgreSQL : la CI n'a pas de base de test.
- La couverture ne mesure pas l'interface, la recherche documentaire ni la surveillance.

## 6. La livraison continue (C19)

### 6.1 Les étapes de la livraison

La **livraison continue** construit, vérifie et met en service une nouvelle version sans geste manuel. Pour RITA, elle
suit `livraison.yml` (`docs/CI-CD.md`, § 3) :

| Étape | Quand | Ce qu'elle fait |
|---|---|---|
| `lint`, `secrets` | à chaque envoi | lint du code ; recherche de secrets sur tout l'historique ; contrôle du `Dockerfile` |
| Porte de livraison | après `lint` et `secrets` verts | relance la suite, la couverture, les portes des garde-fous et les liens internes ; rien n'est construit si une ligne est rouge |
| Construire, puis vérifier l'image | après la porte | l'image démarre ; `/health` annonce le commit construit ; une demande sans clé reçoit 403 ; aucun fichier `.env` dans l'image ; les fichiers de déploiement sont présents |
| Publier l'image vérifiée | après une fusion dans `main` ou sur un tag `livrable-*` | publie l'image testée sur le registre de GitHub (`ghcr.io/ganda15/rita-api`) |
| Déployer | après une fusion dans `main` seulement | le serveur essaie l'image à part (pré-test), la met en service, la contrôle, et remet l'ancienne si un contrôle échoue |

Un **tag de livrable** (`livrable-E<n>-v<k>`) publie aussi son image, sans la déployer. Un **retour arrière** se fait
par un workflow dédié (`retour-arriere.yml`), procédure écrite dans `docs/exploitation.md`.

### 6.2 Le packaging et la livraison, prouvés par des exécutions réelles

| Exécution | Ce qu'elle montre |
|---|---|
| 40490651836, fusion dans `main`, 27/10 | la version de référence `d3a4198` construite, vérifiée, publiée et mise en service ; tous les travaux verts |
| 40490864523, tag `livrable-E1-v3`, 27/10 | construction et vérifications vertes, image publiée sous le nom du tag, sans déploiement |
| 39653430203, un tag de livrable, 21/10 | **la porte a refusé** : tests rouges, construction et publication sautées, rien n'est parti |
| 40325990967, `main`, 26/10 | GitHub n'a lancé aucun travail (incident de facturation du compte) : rien n'a été livré, la chaîne a échoué fermée |

Sur l'ensemble : 49 exécutions sur `main`, dont 48 vertes (la rouge est celle du 26/10) ; 17 exécutions sur des tags
`livrable-*`, dont 15 vertes. Le 24/10, une correction est allée de la fusion à la production en 9 min 02 s, sans
intervention (`docs/CI-CD.md`, § 3).

**L'ordre est garanti par le fichier lui-même** : le déploiement ne démarre qu'après `lint`, `secrets` et
`construire-et-publier` verts (`livraison.yml`, `needs:`), et seulement pour un envoi sur `main` (condition `if:`).

### 6.3 Les sources de la chaîne sont versionnées

Les workflows (`livraison.yml`, `retour-arriere.yml`, `ingestion.yml`), le script du serveur (`deploy/deployer.py`) et
les fichiers Compose (`docker-compose.yml`, `deploy/compose.prod.yml`) sont dans le dépôt. Deux règles GitHub protègent
la chaîne : `main protegee` (pull request et six contrôles exigés, ni suppression ni réécriture) et `tags livrable-*
figes` (un tag de livrable ne se déplace ni ne se supprime).

### 6.4 Les limites

- **Un tag reconstruit l'image** : sur le même commit `d3a4198`, l'image publiée par le tag n'a pas la même empreinte
  que celle livrée en production, et elle a réécrit l'étiquette `sha-d3a4198` (le rapport E3 le dit déjà). La
  production n'est pas touchée : le serveur désigne son image par son empreinte.
- **Le retour arrière restaure l'application, pas la base de données** ; et la sauvegarde de la base n'est pas tenue
  (dernier dump le 27/09 ; manque écrit le 24/10 dans `CHANGELOG.md`).
- **La collecte des cours n'est pas planifiée sur le serveur** : avant une démonstration, les cours de production sont
  rattrapés à la main (`docs/exploitation.md`, procédure écrite le 27/10 au soir, après la version de référence).
- **Le déploiement attend un créneau** : une fusion faite entre 7 h 30 et 9 h n'est livrée qu'après 9 h ; c'est voulu,
  mais une correction urgente du matin attend.

## 7. Démonstration et limites

### 7.1 La démonstration prévue

L'épreuve E4 dure 20 minutes, démonstration comprise, en visioconférence (convocation du 30/10) : la démonstration
passe par le partage d'écran. Elle suit un parcours d'utilisateur, pas une visite technique : le détail de
l'intégration du modèle relève de l'épreuve E3.

**Le parcours principal.** Un investisseur veut comprendre ce qui se passe sur une valeur (le besoin) → il demande un
briefing sur son ticker (l'action) → il lit un court texte en français et le verdict du garde-fou (le résultat
visible) → s'il tape un code inconnu, il lit un message qui dit pourquoi (la gestion d'erreur).

| Étape | Ce que je montre | Point d'attention |
|---|---|---|
| 1. Portefeuille | je saisis la clé à l'écran ; le portefeuille de démonstration s'affiche, valorisé en euros | la clé se tape, elle n'est dans aucun fichier |
| 2. Indicateurs | le tableau des 111 valeurs, le filtre des cotations périmées | les données doivent être à jour (7.2) |
| 3. Briefing | le parcours principal ci-dessus, puis un code inconnu | l'écran annonce une attente indicative de 5 à 15 secondes ; je le dis avant |
| 4. Question | une question, puis la fiche d'une référence ; une question hors sujet pour montrer le refus | refus et erreur ont des messages différents |
| 5. Tableau de bord | l'état du service, carte par carte | un état inconnu n'est jamais présenté comme sain |
| 6. La chaîne | une pull request aux contrôles verts, le tag, l'image publiée | en captures datées, pas en direct |

### 7.2 Ce qui se prépare avant l'oral

- **Rattraper les cours de production à la main** : la collecte n'est pas planifiée sur le serveur
  (`docs/exploitation.md`, « rattrapage des cours en production », procédure écrite le 27/10 au soir).
- **Vérifier `/health`** : la version servie et l'index annoncés.
- **Préparer des captures de secours datées** pour chaque étape faite en direct : elles n'existent pas encore pour
  E4. Si le direct échoue, je le dis et je passe à la capture.
- **Répéter la démonstration chronométrée**, partage d'écran compris.

### 7.3 Ce qui n'est pas fait, en résumé

Le détail est dans les limites de chaque section.

| Domaine | Ce qui manque | Où c'est dit |
|---|---|---|
| Besoin (C14) | parcours de Question et du Tableau de bord ; spécification du Tableau de bord ; critères d'accessibilité de Question ; aucun test avec un lecteur d'écran ni un utilisateur extérieur | § 1.7, § 1.8 |
| Cadre technique (C15) | schémas en retard sur l'application ; hébergeur non choisi sur un critère environnemental | § 2.7 |
| Organisation (C16) | tableau non mis à jour après le 14/10 ; revues du lundi sans compte rendu ; pas de rétrospective | § 3.6 |
| Développement (C17) | environnement non entièrement reproductible ; aucun écran construit d'après une maquette préalable ; défauts ouverts #73, #76, #78, #79 ; constats OWASP S1, S2, S6, S8, S9 ; pas de mesure d'éco-conception « après » ; une affirmation fausse sur le démarrage de l'API, corrigée le 30/10 après la version de référence | § 4.10 |
| Tests (C18) | 32 tests ignorés en CI ; couverture sans l'interface, la recherche ni la surveillance ; trois paquets de CI sans version | § 5.6 |
| Livraison (C19) | un tag reconstruit l'image ; retour arrière sans la base ; sauvegarde non tenue ; collecte non planifiée sur le serveur | § 6.4 |

## 8. Matrice de preuves

**Règle d'état.** ✅ : le critère est satisfait dans son ensemble, avec sa preuve. ⚠️ : une preuve existe, mais une
partie du critère manque. ❌ : aucune preuve.

| Critère | État | Preuve | Limite restante | Section |
|---|---|---|---|---|
| **C14.1** La modélisation des données respecte un formalisme (Merise…) | ⚠️ | MCD Merise, `evidence/C4/MCD-MERISE-RITA.png` ; le formalisme est respecté | la table `article`, qui porte les données de Question, n'est pas dans le MCD | 1.4 |
| **C14.2** La modélisation des parcours respecte un formalisme (wireframes…) | ⚠️ | trois wireframes d'état, `evidence/C14/` | rien pour Question et Tableau de bord | 1.4 |
| **C14.3** Chaque spécification couvre contexte, scénarios, critères de validation | ⚠️ | US-1 à US-3 ; US1 et US2 de Question | aucune spécification pour le Tableau de bord | 1.3, 1.5 |
| **C14.4** Accessibilité intégrée aux critères d'acceptation | ⚠️ | critères RGAA des écrans 1 à 3 | aucun critère pour Question | 1.6 |
| **C14.5** Accessibilité formulée selon un standard (RGAA…) | ⚠️ | règles RGAA numérotées dans les critères des écrans 1 à 3 | aucun objectif formalisé pour Question et Tableau de bord ; aucun test avec un lecteur d'écran | 1.6 |
| **C15.1** Spécifications techniques : architecture, dépendances, environnement | ✅ | `docs/ARCHITECTURE.md`, `requirements-api.txt` | diagramme de flux du 18/08 ; schéma d'architecture du 24/10, sans la vigie | 2.1 à 2.3 |
| **C15.2** Services éco-responsables favorisés | ⚠️ | choix d'architecture, éco-responsables par effet | hébergeur choisi pour la continuité, impact non mesuré | 2.5 |
| **C15.3** Diagramme de flux de données | ⚠️ | `evidence/C15/FLUX-DONNEES-C15-application-RITA.png` | daté du 18/08 : sans Question ni vigie | 2.4 |
| **C15.4** Preuve de concept accessible et fonctionnelle en pré-production | ✅ | preuve du 18/08 ; pré-test sur le serveur depuis le 14/10 | | 2.6 |
| **C15.5** Conclusion de la preuve de concept donnant un avis précis | ✅ | « Poursuivre », `evidence/C15/preuve-preproduction-docker.md` | avis antérieur à la mise en production | 2.6 |
| **C16.1** Cycles, étapes, rôles, rituels et outils de la méthode respectés tout au long du projet | ⚠️ | méthode écrite ; cycles réels datés | suivi interrompu après le 14/10 ; revues sans compte rendu ; agile seulement depuis le 26/09 | 3.2, 3.6 |
| **C16.2** Outils de pilotage disponibles (kanban, burndown, backlog) | ✅ | tableau Kanban, backlog d'issues, plans de travail ; burndown écarté et expliqué | tableau non tenu après le 14/10 | 3.3 |
| **C16.3** Objectifs et modalités des rituels partagés aux parties prenantes | ⚠️ | méthode dans le dépôt, file de validation | partage surtout documentaire | 3.4 |
| **C16.4** Éléments de pilotage accessibles à toutes les parties tout au long du projet | ⚠️ | dépôt en lecture pour le formateur (vérifié le 30/10) | accès au tableau non revérifié ; jury pas encore invité | 3.4 |
| **C17.1** Environnement de développement conforme aux spécifications | ⚠️ | dépendances directes de l'API épinglées | `requirements.txt` et trois paquets de CI libres | 4.2 |
| **C17.2** Interfaces intégrées et conformes aux maquettes | ⚠️ | cinq écrans intégrés | wireframes dessinés après ; deux écrans sans maquette | 4.3 |
| **C17.3** Comportements des composants et navigation conformes | ⚠️ | scénarios testés, dont dans un navigateur | défaut #73 | 4.3 |
| **C17.4** Composants métier conformes aux spécifications | ⚠️ | composants implémentés et testés | défauts #78 et #79 | 4.4 |
| **C17.5** Gestion des droits d'accès développée et conforme | ⚠️ | clé sur les routeurs, journal des refus, quota partagé | rôle propriétaire (#76) ; `/docs` public | 4.5 |
| **C17.6** Flux de données intégrés | ✅ | briefing (`evidence/C10/`, 03/10) ; Question : évaluation en production du 16/10 sur `72dba4d` (`evidence/sprint-3/evaluation-production-2026-10-16-relecture.md`) et tests | preuves antérieures à la version de référence | 4.4 |
| **C17.7** Éco-conception | ⚠️ | pratiques documentées ; mesures historiques sur trois écrans | pas de mesure « après » ; deux écrans non mesurés | 4.7 |
| **C17.8** Préconisations OWASP Top 10 implémentées | ⚠️ | revue S1 à S10 ; S4 et S5 corrigés, S3 et S7 en partie | S1, S2, S6, S8, S9 ouverts | 4.6 |
| **C17.9** Tests couvrant composants métier et gestion des accès | ✅ | les tests des composants métier et des accès API ont été exécutés avec succès (1 808 réussis, couverture 96,32 %) | la vérification des permissions du rôle PostgreSQL en lecture seule reste non démontrée par cette exécution de la CI | 4.8 |
| **C17.10** Sources versionnées et accessibles sur un dépôt distant | ✅ | dépôt GitHub privé, 18 tags `livrable-*` protégés | jury pas encore invité | 4.9 |
| **C17.11** Documentation technique : installation, architecture, dépendances, tests, accessible | ⚠️ | `docs/ARCHITECTURE.md`, `README.md`, `docs/CI-CD.md`, `docs/exploitation.md` | accessibilité non contrôlée ; une affirmation fausse à la version de référence, corrigée le 30/10 | 4.9 |
| **C18.1** Documentation de la chaîne : outils, étapes, tâches, déclencheurs | ✅ | `docs/CI-CD.md`, § 2 et § 3 | | 5.5 |
| **C18.2** Outil d'intégration continue cohérent avec l'environnement | ✅ | GitHub Actions, machine et Python fixés | | 5.1, 5.2 |
| **C18.3** Étapes préalables aux tests intégrées (build, configuration) | ✅ | installation, navigateur, tests des données d'abord | | 5.2 |
| **C18.4** La chaîne exécute les tests au déclenchement | ✅ | `test.yml` ; six contrôles exigés avant toute fusion | | 5.3 |
| **C18.5** Configurations versionnées sur le dépôt distant | ✅ | sept workflows, `ruff.toml`, `.coveragerc` | | 5.4 |
| **C18.6** Documentation d'installation, configuration et test de la chaîne, format accessible | ⚠️ | `docs/CI-CD.md`, § 4 à § 7 | accessibilité non contrôlée | 5.5 |
| **C19.1** Documentation : étapes, tâches, déclencheurs | ✅ | `docs/CI-CD.md`, § 3 | | 6.1 |
| **C19.2** Fichiers de configuration reconnus et exécutés | ✅ | `livraison.yml` ; exécutions vertes sur `main`, `develop` et les tags | | 6.2 |
| **C19.3** Packaging intégré et sans erreur | ✅ | image construite et vérifiée à chaque exécution | | 6.1, 6.2 |
| **C19.4** Livraison exécutée une fois le packaging validé | ✅ | `needs:` et `if:` de `livraison.yml` ; refus de la porte le 21/10 | un tag reconstruit l'image | 6.2, 6.4 |
| **C19.5** Sources de la chaîne versionnées sur le dépôt distant | ✅ | workflows, `deploy/`, règles GitHub | | 6.3 |

**Total : 17 ✅, 19 ⚠️, 0 ❌.**

| Compétence | ✅ | ⚠️ |
|---|---|---|
| C14 | 0 | 5 |
| C15 | 3 | 2 |
| C16 | 1 | 3 |
| C17 | 3 | 8 |
| C18 | 5 | 1 |
| C19 | 5 | 0 |

**Pourquoi ce total diffère du recomptage du 30/10 (30 ✅, 6 ⚠️).** Le recomptage comptait un ✅ dès qu'une preuve
existait, et il s'appuyait aussi sur les ateliers des sprints, exclus du périmètre d'E4. La relecture globale du
30/10 a fait passer C14.1, C14.5 et C15.3 en partiel, chacun pour une raison écrite dans sa ligne. Ici, un ✅ exige que tout le
critère soit satisfait, sur les cinq écrans de la version présentée.

## 📖 Glossaire

- **Action** : part d'une société cotée en bourse.
- **Ticker** : code de cotation d'une action, par exemple `MC.PA`.
- **Commanditaire** : la personne qui exprime le besoin et commande l'application.
- **Exploitant** : la personne qui fait tourner le service et surveille sa santé.
- **Clé d'API** : secret technique envoyé pour accéder aux fonctions protégées de l'API.
- **Garde-fou** : contrôle qui cherche à détecter certains contenus interdits et bloque la réponse lorsqu'une règle de
  refus est déclenchée.
- **User story** : besoin décrit du point de vue de l'utilisateur.
- **Critère d'acceptation** : condition vérifiable pour dire qu'une user story est terminée.
- **MCD, Merise** : modèle conceptuel de données ; Merise est la méthode française qui en fixe le formalisme.
- **Wireframe** : croquis d'un écran, sans couleurs ni graphisme définitif.
- **RGAA** : Référentiel général d'amélioration de l'accessibilité, le standard français.
- **Lecteur d'écran** : logiciel qui lit une page à voix haute.
- **Lighthouse** : outil de Google qui note une page web, notamment sur l'accessibilité.
- **API REST** : service web qui répond à des adresses précises avec des données, ici en JSON.
- **Conteneur, image** : paquet isolé qui contient l'application et ce qu'il lui faut ; l'image est son modèle.
- **Pré-production** : environnement proche de la production où l'on vérifie qu'une version démarre et répond avant
  de la mettre en service.
- **Intégration continue** : chaîne qui lance automatiquement les contrôles et les tests à chaque envoi de code.
- **Workflow** : fichier de GitHub Actions qui décrit une suite d'étapes automatiques.
- **LangGraph** : bibliothèque qui enchaîne des étapes d'un agent sous forme de graphe.
- **ChromaDB** : base qui range les articles découpés pour les retrouver par le sens.
- **Parquet** : format de fichier compressé, rangé par colonnes, adapté aux gros historiques.
- **Caddy, HTTPS** : serveur placé devant l'API ; il chiffre les échanges avec le navigateur.
- **Éco-responsable par effet** : choix qui réduit la consommation sans avoir été fait d'abord pour cette raison.
- **Kanban** : méthode agile à flux continu ; un tableau de colonnes (à faire, en cours, fait) et une limite au travail
  en cours.
- **Scrum** : méthode agile en sprints, avec une équipe et des rôles fixés.
- **Burndown** : graphique du travail restant dans un sprint.
- **Backlog** : la liste du travail identifié, à faire.
- **Issue** : fiche de suivi d'une tâche ou d'un problème sur GitHub.
- **Pull request** : demande de fusion d'une modification dans une branche, avec sa revue.
- **Rétrospective** : réunion de fin de cycle sur ce qui a marché et ce qu'on change.
- **Gel** : moment où une version d'un livrable est figée par un tag ; on ne la modifie plus.
- **Épingler une dépendance** : fixer sa version exacte, pour réinstaller toujours la même.
- **Dépendance indirecte** : bibliothèque installée parce qu'une autre en a besoin.
- **Playwright** : outil qui pilote un vrai navigateur pour tester des pages web.
- **RSI de Wilder** : indicateur de la force des hausses et des baisses récentes d'un cours, entre 0 et 100, avec le
  lissage proposé par Wilder.
- **Comparaison à temps constant** : comparaison qui prend le même temps quelle que soit la réponse, pour ne rien
  laisser deviner de la clé.
- **429, 503** : codes HTTP « trop de requêtes » et « service indisponible ».
- **OWASP Top 10** : liste de référence des dix risques de sécurité les plus courants des applications web.
- **En-tête de sécurité** : instruction envoyée au navigateur avec la page, par exemple pour interdire de l'afficher
  dans un cadre d'un autre site.
- **Proxy** : serveur placé devant l'API, qui reçoit les demandes et peut ajouter des en-têtes.
- **EcoIndex** : note de A à G de l'impact environnemental d'une page web.
- **Couverture** : part du code exécutée par les tests, sur un périmètre choisi.
- **Livraison continue** : chaîne qui construit, vérifie et met en service une version sans geste manuel.
- **Lint** : lecture automatique du code qui signale les erreurs sans l'exécuter.
- **Porte de livraison** : contrôle qui bloque la suite de la chaîne si une condition n'est pas remplie.
- **Registre d'images** : endroit où sont rangées les images publiées, ici celui de GitHub.
- **Empreinte d'une image** : identifiant calculé à partir de son contenu ; deux images différentes ont deux empreintes.
- **Retour arrière** : remise en service de la version précédente.
- **Échouer fermé** : en cas de panne, ne rien laisser passer plutôt que de laisser passer n'importe quoi.

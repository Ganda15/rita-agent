# Rapport E4 : réaliser une application intégrant un service d'IA (C14 à C19)

> **Version 0.2 du 30/10/2026, en cours de rédaction.** Les sections 1 et 2 sont écrites ; les sections 3 à 8 suivent le
> plan de `docs/PLAN-E4-rapport.md`, § 4. Compte des critères : `docs/rapports/E4/recomptage-criteres-2026-10-30.md`.
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
| 5. Tableau de bord | exploitant | lire l'état du service en mots simples, une carte par signal | présenter un état inconnu comme sain | aucune spécification fonctionnelle dédiée identifiée ; le comportement est décrit dans la documentation (`docs/sprint-5/livrable/livrable-sprint-5.md`, § 5.6) et les tests |

Une **user story** décrit un besoin du point de vue de l'utilisateur. Celles des écrans 1 à 3 sont dans
`evidence/C14/` (`preuve-specifications-wireframes.md` pour US-1, `preuve-specifications-ecrans-2-et-3.md` pour US-2
et US-3) ; celles de l'écran 4 sont dans `docs/sprint-3/SPEC.md`.

**Un parcours concret, l'écran 3** : choisir une valeur → demander un briefing → attendre (l'écran annonce une attente
indicative de 5 à 15 secondes) → lire le briefing, ou comprendre le message de refus ou d'erreur. Une clé refusée, une
panne technique et un texte retenu par le garde-fou sont trois situations différentes, et chacune a son message.

### 1.4 Modéliser les données et les parcours

**Les données** sont modélisées avec un **MCD** (modèle conceptuel de données) au formalisme **Merise** : 6 entités et
6 associations. C'est le même modèle que dans le rapport E1 (`evidence/C4/MCD-MERISE-RITA.png`). Je ne l'ai pas refait
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

Chaque user story suit le même plan : le **contexte**, les **scénarios d'utilisation**, puis les **critères
d'acceptation**. Un critère d'acceptation est une condition vérifiable pour dire que la story est terminée. Chacun
renvoie à un test automatisé ou à une lecture du code.

| Écran | Scénarios | Critères d'acceptation |
|---|---|---|
| 1. Portefeuille (US-1) | 5 | 11 |
| 2. Indicateurs (US-2) | 9 | 15 |
| 3. Briefing (US-3) | 8 | 14 |
| 4. Question (US1 et US2 du 15/10) | décrits dans le texte des stories, pas en tableau | 13 (CA1.1 à CA1.8, CA2.1 à CA2.5) |
| 5. Tableau de bord | aucune spécification fonctionnelle dédiée identifiée ; le comportement est décrit dans la documentation et les tests | idem |

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
- **Pour l'écran 5, aucune spécification fonctionnelle dédiée n'est identifiée** (son comportement est décrit dans
  la documentation et les tests), et sa page affiche encore « Prototype local du sprint 5 »,
  alors qu'elle est en production. Les écrans 4 et 5 n'ont pas de wireframe.
- **Aucun test avec un lecteur d'écran réel**, et aucun test documenté avec un utilisateur cible extérieur au projet.
- L'amélioration de ma méthode : formaliser les critères d'acceptation, accessibilité comprise, avant les prochains
  développements.

### 1.8 Travaux restants avant de finaliser C14

La grille de C14 demande que **chaque** spécification couvre contexte, scénarios et critères de validation, et que
l'accessibilité soit dans les critères d'acceptation. Pour les cinq écrans, il manque encore :

- les **parcours** formalisés des écrans Question et Tableau de bord (un schéma de parcours peut suffire) ;
- la **spécification fonctionnelle** du Tableau de bord : contexte, scénarios, critères d'acceptation ;
- les **critères d'accessibilité** dans les critères d'acceptation de l'écran Question.

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

Le schéma de référence est `docs/rapports/E3/schemas/E3-architecture.png`. Il date du 04/10 : il montre le chemin du
briefing, pas encore celui des questions ni la vigie.

### 2.2 Les briques et les dépendances

| Brique | Rôle | Technologie |
|---|---|---|
| Collecte (`pipelines/`, `sources/`) | six étapes indépendantes ; une étape en échec n'arrête pas les autres | Python, `httpx`, `feedparser`, `yfinance` |
| Base (`db/`) | schéma Merise : 10 tables, 1 vue ; rôles, dont `rita_lecture` en lecture seule | PostgreSQL 18 |
| Indicateurs (`indicateurs/`) | 13 indicateurs par valeur, calculés en SQL | SQL, fonctions fenêtre |
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
| Lecture | PostgreSQL → API | lecture seule, jamais d'écriture depuis l'API |
| Réponse | API → navigateur | JSON, protégé par la clé d'API |
| Briefing | API → graphe → modèle | encadré par les garde-fous |

Trois flux portent des données personnelles : le fichier des positions, la table `position` et l'écran du
portefeuille (traitement T1 du registre RGPD). Rien du portefeuille n'est envoyé au modèle : l'étape qui lit la base
pour le briefing ne lit que des données de marché publiques (`docs/ARCHITECTURE.md`, § 5).

### 2.5 Des choix éco-responsables, par effet

| Choix | Effet |
|---|---|
| Interface sans cadre ni outil de construction | aucun paquet JavaScript à télécharger, aucune étape de compilation |
| Pagination plafonnée à 1 000 lignes (`api/donnees.py`, `LIMITE_MAX`) | une requête ne peut pas transférer toute la table des cotations |
| Archive Parquet compressée et partitionnée | dix ans d'historique en 14 Mo (mesure du 18/08) |
| `pyspark` hors de l'image | 492 Mo de moins dans l'image (mesure du 18/08) |
| Un appel au modèle par briefing | un autre fournisseur n'est essayé que si le premier échoue |

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

- **Les schémas sont en retard sur l'application** : le diagramme de flux date du 18/08 et le schéma d'architecture du
  04/10 ; aucun ne montre le chemin des questions ni la vigie.
- **L'hébergeur n'a pas été choisi sur un critère environnemental**, et l'impact du serveur n'est pas mesuré.
- **`requirements.txt` n'est pas épinglé** (12 lignes sans version, une borne basse) ; seule l'image l'est.
- **La taille de l'image (595 Mo) date du 18/08** et n'a pas été remesurée.
- **La production n'a pas été revérifiée en direct pour ce rapport** : la version de référence est celle annoncée par
  `/health` le 27/10, d'après `ETAT.md`.
- **Le dossier `evidence/C15/` n'a pas été mis à jour depuis le 04/10** : la pré-production réelle est prouvée ailleurs
  (`deploy/`, `evidence/sprint-2/`).

## 3. Coordonner en agile (C16)

*[À rédiger]*

## 4. Développer (C17)

*[À rédiger]*

## 5. Automatiser les tests (C18)

*[À rédiger]*

## 6. Livraison continue (C19)

*[À rédiger]*

## 7. Démonstration et limites

*[À rédiger]*

## 8. Matrice de preuves

*[À rédiger]*

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

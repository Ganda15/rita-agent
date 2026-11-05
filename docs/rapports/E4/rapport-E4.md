<style>
.logo{ float:right; width:15mm; margin:7pt 0 2pt 12pt; }
.identite{ color:var(--ink-soft); font-size:9.4pt; }
.sommaire{ margin:9pt 0 2pt; padding:6pt 10pt 5pt; border:.5pt solid var(--rule); border-radius:2pt; }
.sommaire-titre{ font-family:Georgia,"Times New Roman",serif; font-weight:600; font-size:11pt; margin:0 0 4pt; }
.sommaire ol{ list-style:none; padding:0; margin:0; columns:2; column-gap:22pt; }
.sommaire li{ display:flex; justify-content:space-between; gap:8pt; margin:0 0 2pt; break-inside:avoid; font-size:9.4pt; }
.sommaire li a{ color:var(--ink); }
.sommaire li span{ color:var(--accent); font-weight:600; }
h2#glossaire + ul{ columns:2; column-gap:18pt; font-size:9pt; }
h2#glossaire + ul li{ margin-bottom:0; }
h2#matrice + p + table td:first-child{ width:27%; }
</style>

<div><img class="logo" src="../E3/logo/rita-logo-marque.png" alt="Logo de RITA"></div>

# Rapport E4 : réaliser une application intégrant un service d'IA (C14 à C19)

Projet fil rouge **RITA** · **Eramalingam Gandakumar** · Développeur en intelligence artificielle, RNCP 37827 · Simplon × Wild Code School · bloc de compétences 3, compétences C14 à C19 · version 1.4, 5 novembre 2026 · version de référence de l'application : commit `174b0c1` de `main` (tags `livrable-E1-v5`, `livrable-E2-v1` et `livrable-E3-v3`), en production le 02/11/2026 ; interface refaite en production depuis le 04/11 (`8ecc5a7`, § 6.5) ; les exécutions citées en section 6 vont du 21/10 au 02/11 · code et preuves : dépôt GitHub privé [`Ganda15/rita-agent`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4)
{: .identite }

> **En une minute.** RITA aide un investisseur particulier à suivre son portefeuille et à lire l'actualité d'une
> action, sans recommandation d'achat ou de vente. Ce rapport montre comment j'ai conçu et réalisé l'application autour
> d'un modèle de langage fourni : le besoin et les spécifications (C14), le cadre technique (C15), la coordination agile
> (C16), le développement (C17), les tests automatisés (C18) et la livraison continue (C19). Ses mesures décrivent la
> version du 02/11 et ses cinq écrans (portefeuille, indicateurs, briefing, question, tableau de bord) ; l'interface
> refaite, livrée et vérifiée en production le 04/11, est datée au § 6.5. Les ateliers
> des sprints restent hors du rapport (périmètre décidé le 30/10/2026). Pour chaque écran, je distingue ce qui est
> réalisé, la spécification conservée et ce qui n'est pas vérifié.

<div class="sommaire" role="navigation" aria-label="Sommaire">
<p class="sommaire-titre">Sommaire</p>
<ol>
<li><a href="#c14">1. Le besoin et les utilisateurs (C14)</a><span>p. 1</span></li>
<li><a href="#c15">2. Le cadre technique (C15)</a><span>p. 4</span></li>
<li><a href="#c16">3. Coordonner en agile (C16)</a><span>p. 7</span></li>
<li><a href="#c17">4. Développer (C17)</a><span>p. 9</span></li>
<li><a href="#c18">5. Automatiser les tests (C18)</a><span>p. 13</span></li>
<li><a href="#c19">6. La livraison continue (C19)</a><span>p. 14</span></li>
<li><a href="#demo">7. Démonstration et limites</a><span>p. 16</span></li>
<li><a href="#matrice">8. Matrice de preuves</a><span>p. 17</span></li>
<li><a href="#glossaire">Glossaire</a><span>p. 20</span></li>
<li>Annexes A1 à A7 : schémas et comparaisons<span>p. 21</span></li>
</ol>
</div>

## 1. Le besoin et les utilisateurs (C14) {: #c14 }

### 1.1 Le problème de départ

Avant RITA, je suivais des valeurs boursières dans un classeur Excel développé avec un ami. RITA prolonge ce travail en
réunissant les données et les actualités dans une application, avec des contrôles et une traçabilité. Elle collecte les
cours, les taux de change et les articles, les range dans une base PostgreSQL, les expose par une API, et les montre
dans des écrans web. Elle peut aussi rédiger un court **briefing** en français sur une valeur, et répondre à une
question sur les articles collectés, avec un modèle de langage. Une **action** est une part d'une société cotée en
bourse ; son **ticker** est son code de cotation, par exemple `MC.PA`.

RITA est conçue comme une aide à la lecture des marchés, sans recommandation d'achat ou de vente. C'est le périmètre
que j'ai choisi. Cette limite est affichée dans l'interface et contrôlée par des garde-fous ([`guardrails/sortie.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/guardrails/sortie.py)),
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

Le fichier de démonstration ([`data/positions-exemple.csv`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/data/positions-exemple.csv)) contient des positions simulées. Sur ses douze lignes, dix
sont valides et deux, volontairement corrompues, servent à tester le rejet des données incorrectes.

### 1.3 Les besoins, écran par écran

| Écran | Pour qui | Le besoin | Ce que l'écran ne fait pas | Spécification conservée |
|---|---|---|---|---|
| 1. Portefeuille | investisseur | voir en une page la valeur du portefeuille, calculée à partir des dernières données disponibles, convertie en euros, avec l'écart par rapport au prix d'achat | recommander d'acheter ou de vendre | US-1, 18/08 (écran versionné le 16/08) |
| 2. Indicateurs | investisseur | lire les treize indicateurs de chacune des 111 valeurs suivies, repérer celles dont la cotation est périmée | classer les valeurs, fixer un seuil, qualifier un niveau, recommander | US-2, 03/10, rétrospective |
| 3. Briefing | investisseur | saisir un ticker et lire un court briefing en français, rédigé à partir des données collectées, avec le verdict du garde-fou | recommander ; envoyer au modèle une donnée du portefeuille | US-3, 03/10, rétrospective |
| 4. Question | investisseur, évaluateur | poser une question et recevoir une réponse dont chaque affirmation renvoie à une source stockée | répondre hors de son corpus ; donner un conseil d'achat ou de vente (refus, avec son motif) | US1 et US2 de [`docs/sprint-3/SPEC.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/sprint-3/SPEC.md), 15/10, avant l'écran (16/10) ; scénarios et accessibilité ajoutés le 02/11 (US-4, rétrospective) |
| 5. Tableau de bord | exploitant | lire l'état du service en mots simples, une carte par signal | présenter un état inconnu comme sain | US-5, 02/11, rétrospective |

Une **user story** décrit un besoin du point de vue de l'utilisateur. Elles sont dans
[`evidence/C14/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C14) : [`preuve-specifications-wireframes.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C14/preuve-specifications-wireframes.md) pour US-1, [`preuve-specifications-ecrans-2-et-3.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C14/preuve-specifications-ecrans-2-et-3.md) pour US-2
et US-3, [`preuve-specifications-ecrans-4-et-5.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C14/preuve-specifications-ecrans-4-et-5.md) pour US-4 (qui rattache les stories du sprint 3) et US-5.

**Un parcours concret, l'écran 3** : choisir une valeur → demander un briefing → attendre (l'écran annonce une attente
indicative de 5 à 15 secondes) → lire le briefing, ou comprendre le message de refus ou d'erreur. Une clé refusée, une
panne technique et un texte retenu par le garde-fou sont trois situations différentes, et chacune a son message.

### 1.4 Modéliser les données et les parcours

**Les données** sont modélisées avec un **MCD** (modèle conceptuel de données) au formalisme **Merise** : 6 entités et
6 associations. C'est le modèle du rapport E1, revu le 02/11 pour suivre la base : une valeur peut exister sans
cotation (`VALEUR 0,n`, test d'abord ; [`evidence/C4/MCD-MERISE-RITA-2026-11-02.png`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C4/MCD-MERISE-RITA-2026-11-02.png), annexe A1 ; celui du 01/08 est gardé). Il laisse de côté la
table `article`, qui porte pourtant les données de l'écran Question (choix du 11/08, [`evidence/C4/preuve-mcd-merise.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C4/preuve-mcd-merise.md),
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
application. Les trois wireframes sont dans [`evidence/C14/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C14) ([`WIREFRAMES-C14-ecran-portefeuille.png`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C14/WIREFRAMES-C14-ecran-portefeuille.png),
`-ecran-indicateurs.png`, `-ecran-briefing.png` ; annexe A2). Pour les écrans 4 et 5, deux **schémas de parcours** du
02/11, relevés sur l'existant, suivent chaque étape, refus et panne ([`evidence/C14/parcours/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C14/parcours), annexe A6).

### 1.5 Des spécifications vérifiables

Les user stories des cinq écrans suivent le même plan, complété le 02/11 pour les écrans 4 et 5, après le code. Le
plan : le **contexte**, les **scénarios d'utilisation**, puis les **critères
d'acceptation**. Un critère d'acceptation est une condition vérifiable pour dire que la story est terminée. Chacun
renvoie à un test automatisé ou à une lecture du code.

| Écran | Scénarios | Critères d'acceptation |
|---|---|---|
| 1. Portefeuille (US-1) | 5 | 11 |
| 2. Indicateurs (US-2) | 9 | 15 |
| 3. Briefing (US-3) | 8 | 14 |
| 4. Question (US-4, qui rattache US1 et US2 du 15/10) | 10 | 19 (Q1 à Q19, qui reprennent 9 des 13 critères du sprint 3 ; les 4 autres restent dans sa spécification) |
| 5. Tableau de bord (US-5) | 10 | 17 (T1 à T17) |

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

Depuis le 02/11, les écrans 4 et 5 ont aussi leurs critères d'accessibilité, numérotés : RGAA 3.1, 7.5, 8.3, 8.5,
9.1, 9.3, 11.1 et 12.6 ; WCAG 2.4.3 (le focus), 1.4.10 (l'écran étroit) et 2.2.2 (suspendre l'actualisation, corrigé
le jour même, test d'abord). Tous sont reliés à un test, sauf la liste numérotée des sources (9.3), la structure des titres (9.1) et
le titre de l'écran Question (8.5), vérifiés par lecture du code ; l'écran étroit est testé à 375 px, pas à 320 px. Ces tests vérifient le balisage et le comportement, pas l'intégralité des critères RGAA.

Un **lecteur d'écran** est un logiciel qui lit la page à voix haute pour une personne aveugle. L'audit automatique
local du 03/10 (Lighthouse, application servie sur le poste, briefing enregistré pour l'écran 3) a obtenu 100 sur 100
en accessibilité sur les états testés des écrans 1 à 3 ([`evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md)).
Il ne démontre ni l'accessibilité de la production actuelle, ni une conformité complète au RGAA, et il n'a pas mesuré
les écrans 4 et 5. Il reste à compléter par des vérifications manuelles, notamment avec un lecteur d'écran.

### 1.7 Les limites, dites franchement

- **Les documents conservés ne prouvent pas que toutes les spécifications ont précédé le code.** Le premier écran est
  versionné le 16/08 (commit `634e8e4`), sa spécification le 18/08 (`0c8b8f5`). Pour les écrans 2 et 3, les
  spécifications sont explicitement rétrospectives : écrites le 03/10, après le code. Pour l'écran 4, la
  spécification initiale précède sa réalisation (15/10, puis l'écran le 16/10) ; elle a ensuite été révisée le 16/10,
  après mesure.
- Écrire ces critères a fait trouver **des défauts réels** : l'écran 3 gardait la clé d'API avant d'avoir vérifié
  qu'elle fonctionne (#73, corrigé le 01/11, test d'abord, en production le 02/11) ; le tableau de bord ne pouvait pas
  suspendre son actualisation (corrigé le 02/11) ; **deux références RGAA inexactes** dans la spécification de
  l'écran 1, corrigées par un erratum daté, sans réécrire l'original.
- **Les spécifications US-4 et US-5 du 02/11 sont rétrospectives** : elles décrivent l'existant, elles n'ont pas
  guidé la construction (pour l'écran 4, elles complètent celle du 15/10, qui a précédé l'écran) ; leurs schémas de parcours sont relevés sur la version actuelle.
- **Aucun test avec un lecteur d'écran réel**, et aucun test documenté avec un utilisateur cible extérieur au projet.
- L'amélioration de ma méthode : formaliser les critères d'acceptation, accessibilité comprise, avant les prochains
  développements.

### 1.8 Ce qui reste pour C14

La grille de C14 demande que **chaque** spécification couvre contexte, scénarios et critères de validation, et que
l'accessibilité soit dans les critères d'acceptation. Depuis le 02/11, c'est le cas pour les cinq écrans, avec les
limites dites ci-dessus. Il reste la table `article` dans le modèle de données, puisqu'elle porte les données de
Question, et un test avec un lecteur d'écran réel.

## 2. Le cadre technique (C15) {: #c15 }

### 2.1 L'architecture en une vue

RITA est une application pour un seul utilisateur. Elle **collecte** des données de marché et d'actualité, les
**range** dans PostgreSQL, les **expose** par une API REST, et fait **rédiger** par un modèle de langage fourni (aucun
entraînement) un briefing sur une valeur ou une réponse à une question, avec ses sources ([`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/ARCHITECTURE.md), § 1,
état du 24/10). Une **API REST** est un service web qui répond à des adresses précises avec des données, ici en JSON.

Cinq chemins traversent l'application :

| Chemin | De → vers |
|---|---|
| Collecte | sources externes → [`pipelines/ingest.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/pipelines/ingest.py) → PostgreSQL et index des articles |
| Lecture de données | écran → `GET /donnees/*` → PostgreSQL |
| Briefing | écran → `POST /briefing` → graphe (lecture de la base, recherche d'articles, rédaction) → modèle → garde-fou → réponse |
| Question | écran → `POST /question` → garde-fous de la question → recherche dans les articles → modèle → contrôles → réponse avec ses sources, ou refus |
| Surveillance | vigie → `/health` puis `/sante` → une issue GitHub par signal en problème |

Le schéma de référence est [`docs/rapports/E3/schemas/E3-architecture.png`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/rapports/E3/schemas/E3-architecture.png) (annexe A3), refait le 24/10 : il montre les deux chemins
vers le modèle (`/briefing` et `/question`), les cinq écrans et `/sante` avec son tableau de bord. La vigie, qui tourne
hors de l'API, n'y figure pas.

### 2.2 Les briques et les dépendances

| Brique | Rôle | Technologie |
|---|---|---|
| Collecte ([`pipelines/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/pipelines), [`sources/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/sources)) | six étapes indépendantes ; une étape en échec n'arrête pas les autres | Python, `httpx`, `feedparser`, `yfinance` |
| Base ([`db/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/db)) | schéma Merise : 10 tables, 1 vue ; rôles, dont `rita_lecture` en lecture seule | PostgreSQL 18 |
| Indicateurs ([`indicateurs/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/indicateurs)) | 13 indicateurs par valeur ; calculs SQL et traitements Python, dont le RSI de Wilder | SQL (fonctions fenêtre), Python |
| Recherche ([`rag/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/rag)) | index des articles, recherche hybride (sens et mots-clés) | ChromaDB |
| Graphe ([`graph/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/graph)) | trois étapes fixes : lire la base, chercher les articles, rédiger | LangGraph |
| Appel au modèle ([`src/llm.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/src/llm.py)) | fournisseurs réglés par `LLM_ORDRE` ; par défaut, Azure AI Foundry seul depuis le 31/10 (règle UE seule) | Azure AI Foundry |
| Garde-fous ([`guardrails/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/guardrails)) | relisent la question, les articles collectés et le texte produit | Python |
| API ([`api/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/api)) | 19 chemins le 24/10, contrat OpenAPI 3.1.0 publié sur `/docs`, clé d'API | FastAPI |
| Interface ([`frontend/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/frontend)) | cinq écrans, aucune clé dans le code | HTML, CSS, JavaScript sans outil de construction |
| Traçage ([`src/traces.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/src/traces.py)) | une trace par briefing ou question | Langfuse, région UE |
| Vigie ([`monitorage/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/monitorage)) | compteurs, seuils écrits, tableau de bord | Python |
| Déploiement ([`deploy/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/deploy)) | livrer, revenir à la version précédente, ingérer | Python, Docker Compose |

**Les dépendances.** L'image qui tourne en production s'installe depuis [`requirements-api.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements-api.txt) : ses 13 dépendances ont
une version fixée. Le fichier de développement [`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements.txt) ne l'est pas : sur 19 lignes, 12 n'ont pas de version
et une n'a qu'une borne basse (limite reprise en C17).

### 2.3 Les environnements

| Environnement | Ce qui tourne | Comment |
|---|---|---|
| Poste de développement | API (port 8000), PostgreSQL (port 5433), collecte planifiée chaque soir | `uvicorn`, tâche planifiée Windows |
| Pré-production locale | API et PostgreSQL en conteneurs | `docker compose up -d --build` (port 8001) |
| Intégration continue | lint, secrets, tests, garde-fous, construction et vérification de l'image | GitHub Actions, sept workflows ([`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md)) |
| Production | API en conteneur derrière Caddy (HTTPS), serveur Hetzner | livrée automatiquement après chaque fusion dans `main`, depuis le 14/10 (un fichier Compose modifié s'installe à la main) |

Un **conteneur** est un paquet qui contient l'application et tout ce qu'il lui faut pour démarrer, isolé du reste de
la machine ; une **image** est le modèle à partir duquel on lance un conteneur.

### 2.4 Le flux de données

Le diagramme de flux est [`evidence/C15/flux/FLUX-DONNEES-C15-application-RITA-2026-11-02.png`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C15/flux/FLUX-DONNEES-C15-application-RITA-2026-11-02.png) (annexe A4), relevé sur
le code flux par flux le 02/11 ; celui du 18/08 est gardé. Il couvre les flux des cinq écrans et de leur
surveillance ; la purge RGPD ([`db/rgpd_purge.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/db/rgpd_purge.py), lancée à la main) n'y figure pas. Il se lit dans le sens de la donnée,
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
| Journaux et traces | API → journaux, Langfuse | métadonnées seulement : jamais le texte d'une question ni le prompt |
| Surveillance, passerelle | `/sante` → vigie → GitHub ; API → assistant MCP | un verdict par signal ; lecture seule |

Deux traitements du registre RGPD passent par ces flux. **T1**, les positions : le fichier, la table `position` et
l'écran du portefeuille. **T8**, les questions posées dans l'écran Question, actif depuis le 16/10 : le texte d'une
question peut contenir une donnée personnelle ; il est envoyé au modèle (Azure, zone UE) et n'est jamais gardé par
RITA. Rien du portefeuille n'est envoyé au modèle : l'étape qui lit la base
pour le briefing ne lit que des données de marché publiques ([`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/ARCHITECTURE.md), § 5).

### 2.5 Des choix éco-responsables, par effet

| Choix | Effet |
|---|---|
| Interface sans cadre ni outil de construction | HTML, CSS et JavaScript écrits à la main, sans framework ni étape de compilation |
| Pagination plafonnée à 1 000 lignes ([`api/donnees.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/donnees.py), `LIMITE_MAX`) | une requête ne peut pas transférer toute la table des cotations |
| Archive Parquet compressée et partitionnée | dix ans d'historique en 14 Mo (mesure du 18/08) |
| `pyspark` hors de l'image | 492 Mo de moins dans l'image (mesure du 18/08) |
| En fonctionnement nominal, un appel au modèle suffit pour rédiger le briefing | en cas d'échec, d'autres tentatives sont possibles selon la configuration des fournisseurs |

Ces choix sont éco-responsables **par effet** : aucun n'a été fait d'abord pour l'environnement. L'hébergeur, Hetzner
(serveur CX23, 7,19 € par mois), a été choisi le 19/08 pour une raison de continuité : un serveur payé ne s'éteint pas
avant le jury, contrairement aux offres gratuites qui expiraient avant le 05/11 ([`CONTINUITE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/CONTINUITE.md), décisions). Son
impact environnemental n'a pas été un critère du choix.

### 2.6 La preuve de concept et la pré-production

**La preuve de concept du 18/08** ([`evidence/C15/preuve-preproduction-docker.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C15/preuve-preproduction-docker.md)) : l'image se construit (595 Mo),
démarre seule et répond en moins de 20 secondes, refuse une demande sans clé (403) et sert les données avec la clé
(200). Elle tourne durcie : utilisateur sans privilèges, système de fichiers en lecture seule, base non exposée hors du
réseau des conteneurs. **Avis écrit ce jour-là : « Poursuivre. »** Ses limites étaient dites : pré-production
locale, base vide, aucun déploiement automatisé.

**Ce qui a changé depuis, daté.** Depuis le 14/10, chaque version est livrée en production automatiquement après une
fusion dans `main` (sauf un fichier Compose modifié, installé à la main), et elle passe d'abord une pré-production sur le serveur : un conteneur d'essai sur le port 8003,
avec le compte de base `rita_lecture` en lecture seule, contrôlé avant la bascule, puis toujours arrêté
([`deploy/deployer.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/deploy/deployer.py), `_essai_en_preproduction`). La première livraison, le 14/10, a pris 221 secondes de l'ordre à la
fin des contrôles ([`evidence/sprint-2/N0-premiere-livraison-2026-10-14.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/sprint-2/N0-premiere-livraison-2026-10-14.md)). Les limites « pré-production
locale » et « aucun déploiement automatisé » du 18/08 sont donc levées ; la pré-production locale du poste existe
toujours à côté. La conclusion « Poursuivre » reste valable, mais elle date d'avant la mise en production.

### 2.7 Les limites, dites franchement

- **Le schéma d'architecture**, refait le 24/10, montre les deux chemins, mais pas la vigie ; le diagramme de flux est
  à jour depuis le 02/11.
- **L'hébergeur n'a pas été choisi sur un critère environnemental**, et l'impact du serveur n'est pas mesuré.
- **[`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements.txt) n'est pas épinglé** (12 lignes sans version, une borne basse) ; seule l'image l'est.
- **La taille de l'image (595 Mo) date du 18/08** et n'a pas été remesurée.
- **La production n'est vérifiée que par la page servie** : après la livraison du 02/11 (exécution 41488421204,
  déploiement réussi à 17 h 22 UTC), le tableau de bord contient le nouveau bouton ; aucun parcours complet rejoué.
- **Le dossier [`evidence/C15/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C15) n'a reçu, depuis le 04/10, que le diagramme de flux du 02/11** : la pré-production réelle est prouvée ailleurs
  ([`deploy/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/deploy), [`evidence/sprint-2/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/sprint-2)).

## 3. Coordonner en agile (C16) {: #c16 }

### 3.1 La méthode et pourquoi

RITA a un seul développeur. J'ai choisi **Kanban** plutôt que Scrum, le 26/09 ([`docs/PILOTAGE-AGILE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/PILOTAGE-AGILE.md)). Scrum suppose
une équipe, des rôles distincts et des cérémonies de groupe ; Kanban garde ce qui sert à une personne seule : un flux de
travail visible, une limite au travail en cours (deux cartes « En cours » au plus) et une revue régulière. Un
**burndown**, le graphique du travail restant dans un sprint, n'est pas suivi : il suppose un engagement de sprint,
que Kanban n'a pas.

| Rôle | Qui | Responsabilité |
|---|---|---|
| Porteur du produit et développeur | moi | ordonne le travail, décide, développe, rédige les livrables |
| Partie prenante, relecteur | le formateur | lit le dépôt, reçoit les livrables envoyés et y répond |
| Revue automatisée | le workflow [`revue-pr.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/revue-pr.yml), sur les pull requests vers `main` | commente avant la fusion |
| Assistant de développement | un assistant d'IA | propose et écrit à ma demande ; ne décide pas |

### 3.2 Les cycles, tels qu'ils ont eu lieu

| Période | Organisation | Trace |
|---|---|---|
| depuis le 16/08 | un plan en semaines, de S34 à S45, chacune avec un objectif | [`docs/PLAN-12-SEMAINES.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/PLAN-12-SEMAINES.md) |
| 26/09 au 14/10 | Kanban : un cycle par semaine du plan | tableau GitHub « RITA - Pilotage Kanban » |
| 12 au 26/10 | cinq cycles courts : un cadrage, puis quatre cycles avec une livraison en production et un tag ; trois ont un plan de travail découpé en tâches dans le dépôt | [`docs/sprint-2/PLAN-TRAVAIL.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/sprint-2/PLAN-TRAVAIL.md) à [`docs/sprint-4/PLAN-TRAVAIL.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/sprint-4/PLAN-TRAVAIL.md) ; 66 pull requests fusionnées (41 vers `develop`, 25 vers `main` ; une même modification passe souvent par les deux) |
| depuis le 27/10 | les rapports, un livrable à la fois | [`docs/FILE-DE-VALIDATION.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/FILE-DE-VALIDATION.md) |

### 3.3 Les outils de pilotage

- **Le tableau Kanban** (GitHub Projects) : 34 cartes, dont 16 « Fait », 15 « Backlog », 2 « Cette semaine », 1 « En
  cours ». Le dernier mouvement de carte constaté date du 14/10 à 19:56 (UTC). Le tableau ne reflétait pas
  systématiquement tout le travail réalisé.
- **Le backlog** : les issues du dépôt, avec des étiquettes par livrable (`E2` à `E5`, `veille-C6`, `decision-era`).
- **Les plans de travail** des cycles courts : 73, 86 et 62 tâches en listes à cocher.
- **[`ETAT.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/ETAT.md)** pour la prochaine action et l'état du jour, et **[`CHANGELOG.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/CHANGELOG.md)** pour les décisions et les livrables :
  du 12 au 26/10, 40 commits ont modifié [`ETAT.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/ETAT.md) et 29 ont modifié [`CHANGELOG.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/CHANGELOG.md) (des commits, pas des réunions) ;
  mes notes de journal, pour reprendre le travail.
- **Les sessions avec l'assistant** : j'y choisissais et validais la tâche suivante.

### 3.4 Les rituels et le partage avec les parties prenantes

| Rituel | Ce qui a eu lieu | Trace |
|---|---|---|
| Revue du lundi (avancement, blocages, priorités) | tenue, sans compte rendu, selon ma déclaration du 30/10 | aucune : la trame du 05/10, préparée le 03/10, porte la mention « revue NON TENUE », écrite avant la date, et elle est restée vide ; aucun document ne dit ce qui s'est passé ensuite |
| Revue de pull request | les pull requests vers `main` déclenchent une revue automatisée et doivent passer sept contrôles ; GitHub n'exige pas d'approbation humaine. Selon ma méthode, je lis la revue avant de fusionner moi-même | les pull requests sur GitHub ; [`docs/PILOTAGE-AGILE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/PILOTAGE-AGILE.md), § 5 |
| Point formateur | à chaque livrable envoyé : le lien du tag, puis le retour du formateur | [`docs/FILE-DE-VALIDATION.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/FILE-DE-VALIDATION.md) |

**Les envois au formateur, statut par statut.** La file de validation compte neuf lignes, mais pas neuf échanges :

| Statut | Lignes |
|---|---|
| envoyé, avec réponse | E1 v1 (début août, relu avant le gel, trois réponses écrites) ; E1 v3 (envoyé le 28/10, accepté selon la réponse sur Discord que j'ai rapportée, capture encore à joindre) ; méthode, rituels, documentation technique et synthèse de veille (envoyés le 03/11, réception et liens confirmés le 04/11, [preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C8/reponse-formateur-2026-11-04.md)) |
| envoyé, réponse attendue | grilles des compétences (28/10) ; E3 v1.9 (29/10) |
| non envoyé | protocole de veille, conception des indicateurs, note de veille S33 ; E1 v2.6 et E3 v1.5, remplacés par les versions suivantes |

**L'accès des parties prenantes.** Au dépôt : le formateur y a un accès en lecture (compte `bybysker`), vérifié le
30/10 et le 03/11. Au tableau : un accès en lecture lui a été donné le 26/09 ([`docs/PILOTAGE-AGILE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/PILOTAGE-AGILE.md)), et il a confirmé par écrit le 03/11 qu'il l'ouvre ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C16/preuve-acces-kanban-formateur-2026-11-03.md)).
La méthode est écrite dans le dépôt ; un fichier présent dans le dépôt ne prouve pas, à lui seul, que ses règles ont été
partagées et comprises. Le jury recevra un accès en lecture avant la consultation des livrables par les examinateurs.

### 3.5 Un exemple de coordination, de bout en bout

| Étape | Ce qui s'est passé | Trace |
|---|---|---|
| Le constat | le 23/10, en relisant les rapports E1 et E3 contre le code de `main`, je trouve quatre défauts : une panne totale de collecte comptée comme réussie ; l'API des cotations limitée à environ quatre ans alors qu'E1 annonce dix ans ; des nombres non finis acceptés dans les positions ; un en-tête de migration trompeur | [`CHANGELOG.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/CHANGELOG.md), entrée du 24/10 à midi |
| La priorité | les corriger avant le gel d'E1 et d'E3, sans rien ajouter d'autre : le rapport E1 annonçait dix ans de cours joignables par l'API (C5), et ce n'était pas vrai | description de la pull request #138 |
| La tâche | quatre correctifs bornés, tests d'abord : 21 tests, dont 15 rouges avant le code | pull request #138 vers `develop` |
| La livraison | pull request #139 vers `main`, fusionnée par moi ; livraison N18 en production le 24/10, de 11 h 48 à 11 h 57 | exécution GitHub Actions 40083432816, commit `b547cbf` |
| La vérification | `/health` de production annonce `b547cbf` ; la CI montre 1 700 tests réussis | [`CHANGELOG.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/CHANGELOG.md), même entrée |

Le même travail a fait découvrir un autre manque, écrit le jour même : la sauvegarde n'était pas tenue (dernier dump le
27/09 ; état au 04/11 : § 6.4).

### 3.6 Les limites, dites franchement

- **Le tableau n'a plus bougé après le 14/10**, et il ne reflétait pas tout le travail avant. Pendant les cycles
  courts, les tâches ont été suivies dans les plans de travail, dans [`ETAT.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/ETAT.md) et mes notes, et avec l'assistant. Sur
  les huit issues ouvertes du 12 au 26/10, sept viennent de la surveillance automatique ; la #152 est une carte de correction.
- **Les cases des plans de travail ne sont pas cochées dans le dépôt** (0 sur 221). Cela montre que les listes n'ont
  pas été entretenues, pas que le travail n'a pas été fait : l'avancement se lit dans les pull requests et dans
  [`ETAT.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/ETAT.md).
- **Sur les 66 pull requests fusionnées du 12 au 26/10, sept mentionnent une issue** (#111, #138, #139, #146, #147,
  #153, #157), et aucune ne la ferme automatiquement, alors que la méthode le prévoit (`Closes #N`).
- **Les revues du lundi n'ont aucun compte rendu** ; la méthode prévoyait de l'écrire en tête d'[`ETAT.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/ETAT.md). Je ne le
  reconstitue pas après coup.
- **Pas de rétrospective écrite** à la fin des cycles.
- **L'organisation agile ne couvre que la fin du projet** : avant le 26/09, il n'y avait que le plan en semaines.
- **C16 n'est donc pas entièrement démontré** : le suivi dans la durée a des interruptions, et le partage des rituels
  avec les parties prenantes repose surtout sur des documents.

## 4. Développer (C17) {: #c17 }

### 4.1 Vue d'ensemble

Je distingue « j'ai une preuve » et « tout le critère est satisfait ». Sur les onze critères de C17, sept sont
satisfaits : l'environnement (§ 4.2), les comportements (§ 4.3), les composants métier et les flux (§ 4.4), les tests
(§ 4.8), les sources et la documentation, envoyée au formateur le 03/11 (§ 4.9). Quatre restent à consolider : les
maquettes (§ 4.3), les droits d'accès (§ 4.5), la sécurité OWASP (§ 4.6) et l'éco-conception (§ 4.7). La preuve et la limite de
chacun sont dans la matrice (section 8).

### 4.2 L'environnement de développement (critère 1)

Les treize dépendances directes de l'API sont épinglées ([`requirements-api.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements-api.txt)). L'intégration continue tourne sur une
machine fixée (`ubuntu-24.04`) avec Python 3.13 ; sur mon poste, j'utilise Python 3.14. La reproductibilité complète
de l'environnement reste à améliorer : l'image Python, les paquets système et les dépendances indirectes ne sont pas
entièrement verrouillés ; le fichier de développement [`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements.txt) a 12 lignes sans version et une borne basse
(`mcp>=2.1.1`) ; la CI installe trois paquets sans version (`playwright`, `giskard-llm`, `giskard-checks`). La carte #23
suit l'épinglage.

### 4.3 Les interfaces et la navigation (critères 2 et 3)

L'interface est en **HTML, CSS et JavaScript sans outil de construction** : cinq pages ([`frontend/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/frontend)), aucune clé
écrite dans le code, la clé saisie par l'utilisateur et gardée le temps de l'onglet.

**Conformité aux maquettes (critère 2, à consolider).** Les wireframes des trois premiers écrans ont été dessinés après
les écrans d'avant la refonte ; Question et Tableau de bord n'ont pas de maquette, leurs schémas de parcours du 02/11
décrivent l'existant. La refonte des trois premiers écrans a eu ses maquettes d'abord ([`refonte-2026-10.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/conception/frontend/refonte-2026-10.md),
validées le 04/10), puis sa spécification ([`spec.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/specs/001-refonte-interface/spec.md), validée le 04/11), puis le code, livré le 04/11 (§ 6.5). Une
première comparaison, maquette contre écran livré, est en annexe A7 (tâche 11 du plan).

**Comportements et navigation (critère 3).** Le 02/11, une recette a joué les cinq écrans dans quatre
situations chacun (normal, refus, erreur, clavier) : 54 tests dans un vrai navigateur, l'API simulée
([`evidence/C17/recette-2026-11-02/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C17/recette-2026-11-02)).

| Fichier de test | Fonctions de test | Ce qu'il vérifie |
|---|---|---|
| [`tests/test_frontend.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_frontend.py) | 69 | surtout le contenu des pages, lu comme du texte, et leur desserte par l'API |
| [`tests/test_smoke_ui.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_smoke_ui.py) | 11 | de vrais gestes dans un navigateur ; plusieurs réponses de l'API y sont simulées |
| [`tests/test_smoke_tableau_de_bord.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_smoke_tableau_de_bord.py), [`tests/test_tableau_de_bord.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_tableau_de_bord.py) | 14 et 13 | le tableau de bord, dont son balisage d'accessibilité |
| [`tests/test_cle_memorisee_ui.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_cle_memorisee_ui.py) | 5 | #73 dans un navigateur : la clé gardée seulement après un appel accepté |
| [`tests/test_recette_clavier.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_recette_clavier.py), [`tests/test_recette_erreurs.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_recette_erreurs.py) | 7 et 5 | 14 tests au clavier ; 8 cas d'erreur dans un navigateur, sept mutations détectées |

La recette a trouvé trois écarts : le tableau de bord ne posait pas le focus sur le champ de clé (corrigé le 02/11,
test d'abord) ; des cas d'erreur n'étaient vérifiés que par lecture du code (joués depuis dans un navigateur) ; le
troisième, « +0,00 % » pour une pire baisse nulle, reste ouvert (§ 4.4). Le
défaut #73, la clé gardée avant d'avoir servi sur Briefing et Question, est corrigé le 01/11 et en production le
02/11. Sur la version livrée le 04/11 (`8ecc5a7`), 19 tests au clavier et 8 cas d'erreur passent en CI ([exécution
41904329461](https://github.com/Ganda15/rita-agent/actions/runs/41904329461/job/126834827998)). Limite : réponses de l'API simulées pour ces scénarios ; pas de recette intégrale des cinq
écrans en production (§ 6.5).

### 4.4 Les composants métier et les flux de données (critères 4 et 6)

| Composant | Rôle | Tests |
|---|---|---|
| Indicateurs ([`indicateurs/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/indicateurs)) | 13 indicateurs par valeur et 2 pour le portefeuille ; calculs SQL et traitements Python, dont le RSI de Wilder | `test_indicateurs_socle` (13), `_portefeuille` (14), `_risque` (20) |
| Graphe du briefing ([`graph/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/graph)) | trois étapes LangGraph : lire la base, chercher les articles, rédiger | `test_workflow` (11) |
| Rédacteur ([`agents/analyst.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/agents/analyst.py)) | construit le prompt du briefing : cours, variation, capitaux, dix indicateurs, extraits d'articles, consigne de ne rien recommander | `test_analyst` (14) |
| Question ([`agents/question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/agents/question.py), [`api/question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/question.py)) | une chaîne à part : recherche dans les articles, génération en format imposé, contrôles de la réponse ; les références affichées viennent des données stockées | `test_api_question` (15) |

**Deux parcours, deux chaînes.** Le briefing utilise le graphe LangGraph ([`graph/workflow.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/graph/workflow.py)). Le parcours Question
suit une chaîne distincte de recherche documentaire, de génération et de validation ([`agents/question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/agents/question.py)). Dans les
deux cas, des contrôles interviennent avant et après la génération. Preuves des écrans indicateurs et briefing :
[`evidence/C10/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C10). Le parcours Question est vérifié par des tests d'intégration où la recherche documentaire et le
modèle sont simulés ([`tests/test_api_question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_api_question.py)), et par une évaluation en production le 16/10, sur la livraison N6
(`72dba4d`) : huit questions, cinq appels au modèle, trois refus avant tout appel, verdicts relus par moi
([`evidence/sprint-3/evaluation-production-2026-10-16-relecture.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/sprint-3/evaluation-production-2026-10-16-relecture.md)). Ces deux preuves sont antérieures à la version de
référence.

**Deux défauts d'indicateurs, trouvés le 04/10, sont corrigés** le 01/11, tests d'abord, en production le 02/11 : le
RSI d'une série plate (#78) et la pire baisse positive d'un cours qui ne fait que monter (#79, testé sur PostgreSQL).
Sur les 111 valeurs réelles, aucune valeur affichée ne change. Reste un écart d'affichage : « +0,00 % » pour une
pire baisse nulle.

### 4.5 Les droits d'accès (critère 5, à consolider)

| Règle | Dans le code |
|---|---|
| La clé est posée sur des routeurs entiers : une route ajoutée à un routeur protégé hérite de la protection | [`api/main.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/main.py), lignes 260, 267 et 271 |
| Les deux routes qui appellent le modèle partagent une limite : 10 appels par minute à elles deux, par défaut ; 429 au-delà | ligne 267, [`api/limiteur.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/limiteur.py) |
| Les exercices de panne ont leur propre clé : clé du client absente ou incorrecte, 403 ; clé d'exercice non configurée sur le serveur, 503 | ligne 275, [`api/exercice.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/exercice.py) |
| La clé n'a aucune valeur par défaut et compte au moins 16 caractères ; sans clé configurée, l'application démarre mais refuse tout accès protégé ; Docker Compose exige une valeur non vide | [`api/main.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/main.py), lignes 161 à 201 ; [`docker-compose.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docker-compose.yml), ligne 81 |

**La clé, comparée puis refusée** ([`api/main.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/main.py), lignes 201 et 205 à 208, `174b0c1` ; `⋮` : commentaire omis) :

```python
if not api_key or not secrets.compare_digest(api_key, cle_attendue()):
    ⋮
    motif = "absente" if not api_key else "invalide"
    logger.warning("cle d'API refusee : request_id=%s route=%s motif=%s",
                   request_id_courant(), request.url.path, motif)
    raise HTTPException(status_code=403, detail="Cle d'API invalide ou absente")
```

Sans clé, la demande est refusée ; avec une clé, `compare_digest` la compare sans s'arrêter au premier caractère
différent, pour limiter ce que sa durée pourrait révéler. Le refus est journalisé (requête, route, motif), jamais la
clé. Ce test vérifie le refus sans clé ([`tests/test_api_question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_api_question.py), lignes 75 et 76) ; un autre vérifie qu'une clé
incorrecte n'apparaît pas dans le journal ([`tests/test_refus_cle_journal.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_refus_cle_journal.py), lignes 29 à 39) :

```python
def test_question_sans_cle_403(client):
    assert client.post("/question", json={"question": "Qui reprend TAP ?"}).status_code == 403
```

Il n'y a qu'**une clé partagée pour les accès utilisateurs**, sans droits par utilisateur : c'est un choix pour un
outil personnel, défendu avec son modèle de menace ([`evidence/C17/preuve-droits-acces-2026-10-03.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C17/preuve-droits-acces-2026-10-03.md)).

**Ce qui n'est pas conforme** : la matrice des droits validée donne à l'API une lecture limitée des données et une
écriture limitée au journal d'audit ; or l'API se connecte avec le rôle propriétaire (carte #76, ouverte). La
documentation interactive `/docs` est publique (constat S2).

### 4.6 La sécurité : la revue OWASP Top 10 (critère 8, à consolider)

Le 03/10, j'ai relu le code contre l'**OWASP Top 10** (édition 2025), la liste de référence des risques des
applications web. Dix constats, S1 à S10 ([`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C17/revue-owasp-top10-2025-2026-10-03.md)) :

| Constat | État au 30/10 |
|---|---|
| S4 : refus d'authentification non journalisés | corrigé ([`api/main.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/main.py), ligne 206) |
| S5 : ticker sans longueur maximale | corrigé : 20 caractères au plus (ligne 281) |
| S3 : aucune limite de débit | en partie : limite partagée sur `/briefing` et `/question` ; les essais de clé ne sont pas freinés |
| S7 : chaîne d'approvisionnement | en partie : recherche de secrets sur tout l'historique (`gitleaks`), machine de CI fixée ; dépendances de développement libres |
| S10 : certificat proche de l'expiration | renouvelé seul le 19/10, valable jusqu'au 17/01/2027 ([`ETAT.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/ETAT.md)) |
| S1 : aucun en-tête de sécurité | constaté en production le 03/10 ; aucun ajout dans le dépôt depuis ; la configuration actuelle du proxy n'a pas été revérifiée |
| S2 : `/docs` public | ouvert : décision qui me revient (D7), ces pages servent à la démonstration |
| S6 : panne de tous les fournisseurs | ouvert pour `/briefing` ; **corrigé le 04/11** : 503 `AUCUN_FOURNISSEUR`, [testé](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_briefing_diagnostic.py) ; `/question` renvoie déjà 503 ([`api/question.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/question.py)) |
| S8 : mots de passe par défaut | ouvert : le fichier Compose concerné est aussi utilisé en production ([`deploy/deployer.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/deploy/deployer.py)), ce qui ne prouve pas que ces valeurs y servent |
| S9 : garde-fous sous le seuil de 85 % | ouvert : déclaré en échec attendu dans les tests, le seuil n'est pas baissé |

Les suivis sont séparés : la carte #75 pour le durcissement, #23 pour l'épinglage, une décision à prendre pour S2, et la
porte des évaluations pour S9.

### 4.7 L'éco-conception (critère 7)

Les pratiques sont documentées en section 2.5 (interface sans outil de construction, pagination plafonnée ; en
fonctionnement nominal, un appel au modèle suffit pour un briefing). Mesures historiques du 03/10, en local, sur trois écrans
([`evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md)) :

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

Mesure du 02/11 sur le commit de référence `174b0c1` (exécution 41488421537).

**1 925 tests réussis, 47 ignorés, 2 en échec attendu** dans le job `pytest`. Parmi les ignorés, les 25 tests qui
exigent PostgreSQL : le job `base` les joue à part, sur une base jetable créée avec le schéma et les rôles du dépôt
(25 réussis, 0 sauté). Les 22 autres : 9 tests des hooks, réservés à Windows ; 7 tests des sommaires de rapport, qui relisent les PDF ;
5 tests de Spark ; 1 test des schémas d'E1.
Les deux échecs attendus déclarent que les garde-fous n'atteignent pas leur seuil, sans le baisser.

**Couverture : 96,32 %** pour un seuil de 90 % ([`.coveragerc`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.coveragerc)). Elle porte sur le périmètre Python configuré, pas sur
toute l'application : l'interface, [`rag/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/rag), [`monitorage/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/monitorage) et [`passerelle_mcp/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/passerelle_mcp) n'en font pas partie.

**Les accès ont leurs tests** : `test_limiteur` (7) et `test_exercice` (15) ont tourné. Les quatre tests du rôle
PostgreSQL en lecture seule (`test_role_lecture`) passent dans le job `base` de la même exécution : le rôle lit
toutes les tables, ne peut ni écrire ni créer de table.

### 4.9 Les sources et la documentation (critères 10 et 11)

**Les sources** sont versionnées sur GitHub, dans le dépôt privé [`Ganda15/rita-agent`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4). Le formateur y a un accès en
lecture. Chaque livrable est un tag `livrable-*` qu'on ne peut ni déplacer ni supprimer ; il y en a 21 le 02/11. Le
jury sera invité avant la consultation des livrables par les examinateurs.

**La documentation technique** est rassemblée : [`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/ARCHITECTURE.md) (architecture, briques, points de terminaison,
règles d'accès, état du 24/10), [`README.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/README.md) (« Lancer le projet », « Lancer les tests »), [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md) et
[`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/exploitation.md). Jusqu'au 30/10, [`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/ARCHITECTURE.md), le message d'erreur et la docstring de [`api/main.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/api/main.py)
disaient que l'API « refuse de démarrer » sans clé, alors qu'elle démarre et refuse à l'authentification ; corrigé le
30/10 (`a2c0d51`). Le `README` a été remis à jour le 02/11 (chiffres remesurés, tests PostgreSQL décrits), et son
format contrôlé ([`evidence/C17/controle-accessibilite-readme-2026-11-02.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C17/controle-accessibilite-readme-2026-11-02.md)). Le 03/11, ces documents ont été envoyés au formateur : liens vers `README.md`, `docs/ARCHITECTURE.md` et `docs/CI-CD.md`, guide d'exploitation en PDF joint ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C8/envoi-documents-formateur-2026-11-03.md)).

### 4.10 Les limites, dites franchement

- **L'environnement n'est pas entièrement reproductible** : [`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements.txt) libre, trois paquets de CI sans
  version, dépendances indirectes non verrouillées.
- **La conformité aux maquettes n'est vérifiée qu'en partie** : la refonte, construite d'après les maquettes du 04/10 et
  livrée le 04/11, n'est comparée que sur la partie capturée des écrans (annexe A7) ; Question et Tableau de bord n'ont qu'un schéma
  de parcours relevé sur l'existant.
- **Des défauts ouverts** : le rôle propriétaire de l'API (#76) ; l'affichage « +0,00 % » d'une pire baisse nulle ; sur
  l'écran Briefing livré, une aide qui promet trop et des astérisques affichés (annexe A7).
  #73, #78 et #79 sont corrigés et déployés le 02/11 ; leurs cartes restent ouvertes sur GitHub jusqu'à une
  vérification manuelle en production.
- **Sécurité** : en-têtes absents en production au 03/10 et non revérifiés depuis (S1), `/docs` public (S2), mots
  de passe par défaut (S8), garde-fous sous leur seuil (S9) ; S6 corrigé le 04/11.
- **Les tests** : 22 ignorés en CI faute d'un élément absent de la CI ; une couverture qui exclut l'interface, la
  recherche documentaire, la surveillance et la passerelle MCP.
- **L'éco-conception** n'a que des mesures historiques, sans mesure « après », sur trois écrans sur cinq.
- **La documentation** : le format du guide d'exploitation (31/10, PDF de 12 pt et 66 signets), d'[`ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/ARCHITECTURE.md)
  et de [`CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md) (01/11) et du `README` (02/11) est contrôlé avec des outils ([`evidence/C8/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C8), [`evidence/C17/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C17)) ; ce
  n'est pas un audit complet. Envoyés au formateur le 03/11 ; réception et liens confirmés par Elbby le 04/11 ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C8/reponse-formateur-2026-11-04.md)).

## 5. Automatiser les tests (C18) {: #c18 }

### 5.1 La chaîne d'intégration continue

L'**intégration continue** lance automatiquement les contrôles et les tests à chaque envoi de code. Pour RITA, c'est
**GitHub Actions**, l'outil du dépôt : il n'y a rien à installer à côté, et les règles de la branche principale
peuvent exiger ses résultats.

| Workflow | Déclencheur | Ce qu'il fait |
|---|---|---|
| [`test.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/test.yml), Tests | chaque envoi et chaque pull request sur `main` et `develop` | trois travaux : `pytest` (la suite et la couverture), `evals` (les portes des garde-fous) et `base` (les 25 tests PostgreSQL sur une base jetable) |
| [`livraison.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/livraison.yml), Livraison | chaque envoi et chaque pull request sur `main` et `develop`, chaque tag `livrable-*` | `lint` (`ruff`), `secrets` (`gitleaks` sur tout l'historique), puis la construction et la vérification de l'image (section 6) |
| [`revue-pr.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/revue-pr.yml), Revue PR | chaque pull request vers `main` | une revue automatisée commentée sur la pull request |

Il y a sept workflows en tout ([`.github/workflows/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/.github/workflows)) ; les quatre autres servent la surveillance, l'évaluation des
garde-fous, le retour arrière et l'ingestion ([`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md), § 3).

### 5.2 Les étapes, dans l'ordre

Le travail `pytest` de [`test.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/test.yml) tourne sur une machine fixée (`ubuntu-24.04`), avec Python 3.13 :

1. installer les dépendances ([`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements.txt)) ;
2. installer le navigateur du test d'écran (Playwright) et les outils de l'évaluation des garde-fous ;
3. **tester d'abord les données** (collecte, nettoyage, import, RGPD) : le 02/11, 296 réussis et 3 ignorés, en
   7 secondes ; une erreur sur les données se voit avant le reste ;
4. lancer toute la suite et mesurer la couverture, avec un seuil de 90 % ([`.coveragerc`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.coveragerc)).

### 5.3 Les tests tournent à chaque déclenchement

Le 02/11, sur le commit de référence `174b0c1` (exécution 41488421537) : **1 925 tests réussis, 47 ignorés, 2 en
échec attendu**, couverture **96,32 %** ; le job `base` joue à part les 25 tests PostgreSQL (25 réussis, 0 sauté).
Détail en section 4.8.

La branche principale ne change que par une pull request, et GitHub exige sept contrôles verts avant la fusion : `lint`,
`pytest`, `base`, `evals`, `revue`, `secrets`, `construire-et-publier` (règle `main protegee`, lue le 02/11, sans
contournement possible). Une pull request dont un contrôle est rouge ne peut donc pas entrer dans `main`.

### 5.4 Les configurations sont versionnées

Les sept workflows sont dans le dépôt ([`.github/workflows/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/.github/workflows)), comme les règles de lint ([`ruff.toml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/ruff.toml)), de couverture
([`.coveragerc`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.coveragerc)) et de recherche de secrets ([`.gitleaks.toml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.gitleaks.toml)). La version de `ruff` est la même dans la CI et dans
[`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements.txt), et un test le vérifie ([`tests/test_lint_config.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/tests/test_lint_config.py)).

### 5.5 La documentation de la chaîne

[`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md) rassemble tout en un endroit : les déclencheurs (§ 2), les étapes workflow par workflow (§ 3), les
secrets et les permissions (§ 4), comment installer la chaîne sur un dépôt neuf (§ 5), comment la tester avant de
compter dessus (§ 6), et quoi faire quand elle est rouge (§ 7). Le document est en Markdown, lisible sur GitHub ; son
format a été contrôlé avec des outils le 01/11, puis le 02/11 ([`evidence/C17/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C17)) ; ce n'est pas un audit complet. Son lien a été envoyé au formateur le 03/11 ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C8/envoi-documents-formateur-2026-11-03.md)).

### 5.6 Les limites

- Trois paquets installés par la CI n'ont pas de version fixée (`playwright`, `giskard-llm`, `giskard-checks`), et
  [`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements.txt) non plus (section 4.2).
- 22 tests sont ignorés en CI faute d'un élément absent de la CI ; les tests PostgreSQL, eux, tournent depuis le
  01/11 dans le job `base`, exigé pour `main`.
- La couverture ne mesure pas l'interface, la recherche documentaire, la surveillance ni la passerelle MCP.

## 6. La livraison continue (C19) {: #c19 }

### 6.1 Les étapes de la livraison

La **livraison continue** prépare et vérifie une version livrable ; le déploiement suit la fusion sur `main`, sauf un
fichier Compose modifié, à installer à la main sur le serveur ([`livraison.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/livraison.yml), [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md), § 3 ; annexe A5) :

| Étape | Quand | Ce qu'elle fait |
|---|---|---|
| `lint`, `secrets` | à chaque envoi | lint du code ; recherche de secrets sur tout l'historique ; contrôle du [`Dockerfile`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/Dockerfile) |
| Porte de livraison | après `lint` et `secrets` verts | relance la suite, la couverture, les portes des garde-fous et les liens internes ; rien n'est construit si une ligne est rouge |
| Construire, puis vérifier l'image | après la porte | l'image démarre ; `/health` annonce le commit construit ; une demande sans clé reçoit 403 ; aucun fichier `.env` dans l'image ; les fichiers de déploiement sont présents |
| Publier l'image vérifiée | après une fusion dans `main` ou sur un tag `livrable-*` | publie l'image testée sur le registre de GitHub (`ghcr.io/ganda15/rita-api`) |
| Déployer | après une fusion dans `main` seulement | le serveur essaie l'image à part (pré-test), la met en service, la contrôle, et remet l'ancienne si un contrôle échoue |

Un **tag de livrable** (`livrable-E<n>-v<k>`) publie aussi son image, sans la déployer. Un **retour arrière** se fait
par un workflow dédié ([`retour-arriere.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/retour-arriere.yml)), procédure écrite dans [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/exploitation.md).

### 6.2 Le packaging et la livraison, prouvés par des exécutions réelles

| Exécution | Ce qu'elle montre |
|---|---|
| 41488421204, PR #173, 02/11 | `174b0c1` construite, vérifiée, publiée, en service à 17 h 22 UTC |
| 40490651836, fusion dans `main`, 27/10 | la version `d3a4198` construite, vérifiée, publiée et mise en service ; tous les travaux verts |
| 40490864523, tag `livrable-E1-v3`, 27/10 | construction et vérifications vertes, image publiée sous le nom du tag, sans déploiement |
| 39653430203, un tag de livrable, 21/10 | **la porte a refusé** : tests rouges, construction et publication sautées, rien n'est parti |
| 40325990967, `main`, 26/10 | GitHub n'a lancé aucun travail (incident de facturation du compte) : rien n'a été livré, la chaîne a échoué fermée |

Sur l'ensemble : 52 exécutions sur `main` au 02/11, dont 51 vertes (la rouge est celle du 26/10) ; 20 exécutions sur
des tags `livrable-*`, dont 18 vertes. Le 24/10, une correction est allée de la fusion à la production en 9 min 02 s, sans
intervention ([`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md), § 3).

**L'ordre est garanti par le fichier lui-même** ([`livraison.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/livraison.yml), lignes 349 à 351, commit `174b0c1`) :

```yaml
deployer:
  needs: [lint, secrets, construire-et-publier, attendre-creneau]
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

Le déploiement ne démarre que si ces quatre travaux ont réussi, et seulement pour un envoi sur `main`.

### 6.3 Les sources de la chaîne sont versionnées

Les workflows ([`livraison.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/livraison.yml), [`retour-arriere.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/retour-arriere.yml), [`ingestion.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/ingestion.yml)), le script du serveur ([`deploy/deployer.py`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/deploy/deployer.py)) et
les fichiers Compose ([`docker-compose.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docker-compose.yml), [`deploy/compose.prod.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/deploy/compose.prod.yml)) sont dans le dépôt. Deux règles GitHub protègent
la chaîne : `main protegee` (pull request et sept contrôles exigés, ni suppression ni réécriture) et `tags livrable-*
figes` (un tag de livrable ne se déplace ni ne se supprime).

### 6.4 Les limites

- **Un tag reconstruit l'image** : sur le même commit `d3a4198`, l'image publiée par le tag n'a pas la même empreinte
  que celle livrée en production, et elle a réécrit l'étiquette `sha-d3a4198` (le rapport E3 le dit déjà). La
  production n'est pas touchée : le serveur désigne son image par son empreinte.
- **Le retour arrière automatique restaure l'application, pas la base de données.** Aucune sauvegarde automatique de la
  base n'est en place (manque écrit le 24/10 dans [`CHANGELOG.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/CHANGELOG.md)) ; le 04/11, quatre sauvegardes faites à la main
  ont été vérifiées autour des deux opérations sur les données (§ 6.5).
- **La collecte des cours n'est pas planifiée sur le serveur** : avant une démonstration, les cours de production sont
  rattrapés à la main ([`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/exploitation.md), procédure écrite le 27/10 au soir).
- **Le déploiement attend un créneau** : une fusion faite entre 7 h 30 et 9 h n'est livrée qu'après 9 h ; c'est voulu,
  mais une correction urgente du matin attend.

### 6.5 Mise à jour du 04/11 : la refonte livrée, puis vérifiée en production

**Application** : la refonte est passée par la même chaîne (pull request #180, fusion, déploiement automatique) ;
`8ecc5a7` est en service, son contenu est celui que j'avais relu, 63 fichiers servis contrôlés sur 63.
**Données**, deux opérations séparées du déploiement, chacune sur accord écrit : la ligne Viridien, fausse depuis l'import
du 20/08, corrigée (quatre cellules), puis un seul rattrapage des cours et des taux, jusqu'au 04/11. **Vérification** : API et
accès MCP avec la clé, 0 échec ; Portefeuille et Indicateurs contrôlés à l'écran, captures datées ; ce n'est pas une
recette des cinq écrans. **Sauvegardes** : quatre, faites à la main, restaurées ou comparées cellule par cellule ; aucune
n'est automatique. **Limites** : collecte non planifiée (§ 6.4) ; script du rattrapage à renforcer avant toute
réutilisation. Aucun statut ne change ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C3/preuve-correction-viridien-production-2026-11-04.md)).

## 7. Démonstration et limites {: #demo }

### 7.1 La démonstration prévue

L'épreuve E4 dure 20 minutes, démonstration comprise, en visioconférence (convocation du 30/10) : la démonstration
passe par le partage d'écran. Elle suit un parcours d'utilisateur, pas une visite technique : le détail de
l'intégration du modèle relève de l'épreuve E3.

**Le parcours principal.** Un investisseur veut comprendre ce qui se passe sur une valeur (le besoin) → il demande un
briefing sur son ticker (l'action) → il lit un court texte en français et le verdict du garde-fou (le résultat
visible) → s'il tape un code inconnu, il lit un message qui dit pourquoi (la gestion d'erreur).

| Étape | Ce que je montre | Point d'attention |
|---|---|---|
| 1. Portefeuille | je saisis la clé à l'écran ; le portefeuille de démonstration s'affiche, valorisé en euros | clé tapée sans la montrer, absente du code versionné |
| 2. Indicateurs | le tableau des 111 valeurs, le filtre des cotations périmées | les données doivent être à jour (7.2) |
| 3. Briefing | le parcours principal ci-dessus, puis un code inconnu | l'écran annonce une attente indicative de 5 à 15 secondes ; je le dis avant |
| 4. Question | une question, puis la fiche d'une référence ; une question hors sujet pour montrer le refus | refus et erreur ont des messages différents |
| 5. Tableau de bord | l'état du service, carte par carte | un état inconnu n'est jamais présenté comme sain |
| 6. La chaîne | une pull request aux contrôles verts, le tag, l'image publiée | en captures datées, pas en direct |

### 7.2 Ce qui se prépare avant l'oral

- **Vérifier la date des cours** ; s'ils sont anciens, utiliser les captures datées : la collecte n'est pas planifiée, et le
  script du rattrapage est à renforcer avant toute réutilisation (§ 6.5).
- **Vérifier `/health`** : la version servie et l'index annoncés.
- **Captures de secours datées** pour chaque étape en direct : Portefeuille, Indicateurs et le briefing AIR.PA
  existent (A7) ; restent le code inconnu, Question, Tableau de bord et la chaîne. Si le direct échoue, je passe à la capture.
- **Répéter la démonstration chronométrée**, partage d'écran compris.

### 7.3 Ce qui n'est pas fait, en résumé

Le détail est dans les limites de chaque section.

| Domaine | Ce qui manque | Où c'est dit |
|---|---|---|
| Besoin (C14) | spécification de l'écran 5 et compléments de l'écran 4 rétrospectifs (02/11) ; table `article` hors du modèle ; aucun test avec un lecteur d'écran ni un utilisateur extérieur | § 1.7, § 1.8 |
| Cadre technique (C15) | schéma d'architecture sans la vigie ; hébergeur non choisi sur un critère environnemental | § 2.7 |
| Organisation (C16) | tableau non mis à jour après le 14/10 ; revues du lundi sans compte rendu ; pas de rétrospective | § 3.6 |
| Développement (C17) | environnement non entièrement reproductible ; refonte comparée en partie à ses maquettes (A7) ; défaut ouvert #76, un écart d'affichage (« +0,00 % ») et deux défauts de Briefing (A7) ; constats OWASP S1, S2, S8, S9 ; pas de mesure d'éco-conception « après » | § 4.10 |
| Tests (C18) | 22 tests ignorés en CI ; couverture sans l'interface, la recherche, la surveillance ni la passerelle MCP ; trois paquets de CI sans version | § 5.6 |
| Livraison (C19) | un tag reconstruit l'image ; retour arrière sans la base ; aucune sauvegarde automatique ; collecte non planifiée ; script de rattrapage à renforcer | § 6.4, 6.5 |

## 8. Matrice de preuves {: #matrice }

**Règle d'état.** ✅ : le critère est satisfait dans son ensemble, avec sa preuve. 🟡 à consolider : une preuve existe,
mais une partie du critère manque, écrite dans la colonne « Limite restante ». ❌ : aucune preuve.

| Critère | État | Preuve | Limite restante | Section |
|---|---|---|---|---|
| **C14.1** La modélisation des données respecte un formalisme (Merise…) | ✅ | MCD Merise revu le 02/11 (`VALEUR 0,n`, comme la base), [`evidence/C4/MCD-MERISE-RITA-2026-11-02.png`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C4/MCD-MERISE-RITA-2026-11-02.png) | le MCD ne représente pas les articles utilisés par l'écran Question (6 entités pour 8 tables : [`evidence/C4/preuve-mcd-merise.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C4/preuve-mcd-merise.md), § 4) | 1.4 |
| **C14.2** La modélisation des parcours respecte un formalisme (wireframes…) | ✅ | trois wireframes d'état ; parcours des écrans 4 et 5, 02/11 ([`evidence/C14/parcours/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C14/parcours)) | les deux derniers parcours relevés après développement | 1.4 |
| **C14.3** Chaque spécification couvre contexte, scénarios, critères de validation | ✅ | US-1 à US-5 : contexte, scénarios, critères ([`evidence/C14/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C14)) | US-1, 2, 3 et 5 écrites après leur écran ; US-4 complétée après | 1.3, 1.5 |
| **C14.4** Accessibilité intégrée aux critères d'acceptation | ✅ | critères RGAA et WCAG des cinq écrans, reliés à des tests | restitution par un lecteur d'écran non testée | 1.6 |
| **C14.5** Accessibilité formulée selon un standard (RGAA…) | ✅ | objectifs des cinq écrans formulés avec des règles RGAA ou WCAG numérotées, chacun relié à un test ou à une lecture du code ([`evidence/C14/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C14)) | aucun test avec un lecteur d'écran | 1.6 |
| **C15.1** Spécifications techniques : architecture, dépendances, environnement | ✅ | [`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/ARCHITECTURE.md), [`requirements-api.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements-api.txt) | schéma d'architecture du 24/10, sans la vigie | 2.1 à 2.3 |
| **C15.2** Services éco-responsables favorisés | 🟡 | choix d'architecture, éco-responsables par effet | hébergeur choisi pour la continuité, impact non mesuré | 2.5 |
| **C15.3** Diagramme de flux de données | ✅ | [`evidence/C15/flux/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C15/flux), relevé sur le code le 02/11 ; celui du 18/08 gardé | relevé après le code ; questions (T8) non marquées personnelles ; purge RGPD absente | 2.4 |
| **C15.4** Preuve de concept accessible et fonctionnelle en pré-production | ✅ | preuve du 18/08 ; pré-test sur le serveur depuis le 14/10 | | 2.6 |
| **C15.5** Conclusion de la preuve de concept donnant un avis précis | ✅ | « Poursuivre », [`evidence/C15/preuve-preproduction-docker.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C15/preuve-preproduction-docker.md) | avis antérieur à la mise en production | 2.6 |
| **C16.1** Cycles, étapes, rôles, rituels et outils de la méthode respectés tout au long du projet | 🟡 | méthode écrite ; cycles réels datés | suivi interrompu après le 14/10 ; revues sans compte rendu ; agile seulement depuis le 26/09 | 3.2, 3.6 |
| **C16.2** Outils de pilotage disponibles (kanban, burndown, backlog) | ✅ | tableau Kanban, backlog d'issues, plans de travail ; burndown écarté et expliqué | tableau non tenu après le 14/10 | 3.3 |
| **C16.3** Objectifs et modalités des rituels partagés aux parties prenantes | ✅ | méthode dans le dépôt, file de validation ; section des rituels envoyée au formateur le 03/11 ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C8/envoi-documents-formateur-2026-11-03.md)) | partage surtout documentaire ; réception et liens confirmés par Elbby, 04/11 | 3.4 |
| **C16.4** Éléments de pilotage accessibles à toutes les parties tout au long du projet | 🟡 | dépôt en lecture pour le formateur (vérifié le 30/10) ; Kanban confirmé par Elbby le 03/11 ([preuve](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C16/preuve-acces-kanban-formateur-2026-11-03.md)) | accès du jury à organiser | 3.4 |
| **C17.1** Environnement de développement conforme aux spécifications | ✅ | environnement prévu ([`evidence/C15/preuve-specifications-techniques.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/C15/preuve-specifications-techniques.md)) et installé, rapprochés le 01/11 : Windows 11, Python 3.14.6, PostgreSQL 18.4 sur le port 5433 ; Python 3.13 en CI ([`test.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/test.yml)) | [`requirements.txt`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/requirements.txt) et trois paquets de CI sans version : limite de reproductibilité | 4.2 |
| **C17.2** Interfaces intégrées et conformes aux maquettes | 🟡 | cinq écrans intégrés ; refonte d'après maquettes (04/11) | comparaison visuelle partielle (A7) ; deux écrans sans maquette | 4.3 |
| **C17.3** Comportements des composants et navigation conformes | ✅ | recette initiale du 02/11 (54 tests en navigateur) ; sur `8ecc5a7` (04/11), 19 tests au clavier et 8 cas d'erreur verts en CI ; #73 déployé | API simulée ; 375 px, pas 320 ; pas de recette des cinq écrans en production | 4.3 |
| **C17.4** Composants métier conformes aux spécifications | ✅ | composants testés ; #78 et #79 déployés ; 111 valeurs vérifiées | « +0,00 % » affiché pour un zéro ; valeurs vérifiées en local | 4.4 |
| **C17.5** Gestion des droits d'accès développée et conforme | 🟡 | clé sur les routeurs, journal des refus, quota partagé | rôle propriétaire (#76) ; `/docs` public | 4.5 |
| **C17.6** Flux de données intégrés | ✅ | briefing ([`evidence/C10/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C10), 03/10) ; Question : évaluation en production du 16/10 sur `72dba4d` ([`evidence/sprint-3/evaluation-production-2026-10-16-relecture.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/evidence/sprint-3/evaluation-production-2026-10-16-relecture.md)) et tests | preuves antérieures à la version de référence | 4.4 |
| **C17.7** Éco-conception | 🟡 | pratiques documentées ; mesures historiques sur trois écrans | pas de mesure « après » ; deux écrans non mesurés | 4.7 |
| **C17.8** Préconisations OWASP Top 10 implémentées | 🟡 | revue S1 à S10 ; S4, S5 et S6 corrigés (S6 le 04/11), S3 et S7 en partie | S1, S2, S8, S9 ouverts | 4.6 |
| **C17.9** Tests couvrant composants métier et gestion des accès | ✅ | les tests des composants métier et des accès API ont été exécutés avec succès (1 925 réussis, couverture 96,32 %, 02/11) ; les 4 tests du rôle en lecture seule passent dans le job `base` | 22 tests ignorés ; couverture sans interface, `rag/`, `monitorage/`, MCP | 4.8 |
| **C17.10** Sources versionnées et accessibles sur un dépôt distant | ✅ | dépôt GitHub privé, 21 tags `livrable-*` protégés | jury pas encore invité | 4.9 |
| **C17.11** Documentation technique : installation, architecture, dépendances, tests, accessible | ✅ | [`docs/ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/ARCHITECTURE.md), [`README.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/README.md), [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md), [`docs/exploitation.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/exploitation.md) ; format contrôlé pour le guide (31/10), [`ARCHITECTURE.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/ARCHITECTURE.md) et [`CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md) (01/11), [`README.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/README.md) (02/11, [`evidence/C17/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C17)) ; envoyée au formateur le 03/11 | réception et liens confirmés par Elbby, 04/11 | 4.9 |
| **C18.1** Documentation de la chaîne : outils, étapes, tâches, déclencheurs | ✅ | [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md), § 2 et § 3 | | 5.5 |
| **C18.2** Outil d'intégration continue cohérent avec l'environnement | ✅ | GitHub Actions, machine et Python fixés | | 5.1, 5.2 |
| **C18.3** Étapes préalables aux tests intégrées (build, configuration) | ✅ | installation, navigateur, tests des données d'abord | | 5.2 |
| **C18.4** La chaîne exécute les tests au déclenchement | ✅ | [`test.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/test.yml) ; sept contrôles exigés avant toute fusion, dont la base jetable | | 5.3 |
| **C18.5** Configurations versionnées sur le dépôt distant | ✅ | sept workflows, [`ruff.toml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/ruff.toml), [`.coveragerc`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.coveragerc) | | 5.4 |
| **C18.6** Documentation d'installation, configuration et test de la chaîne, format accessible | ✅ | [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md), § 4 à § 7 ; format contrôlé le 01/11 ([`evidence/C17/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C17)) ; lien envoyé au formateur le 03/11 | réception et liens confirmés par Elbby, 04/11 | 5.5 |
| **C19.1** Documentation : étapes, tâches, déclencheurs | ✅ | [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md), § 3 | | 6.1 |
| **C19.2** Fichiers de configuration reconnus et exécutés | ✅ | [`livraison.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/livraison.yml) ; exécutions vertes sur `main`, `develop` et les tags | | 6.2 |
| **C19.3** Packaging intégré et sans erreur | ✅ | image construite et vérifiée à chaque exécution | | 6.1, 6.2 |
| **C19.4** Livraison exécutée une fois le packaging validé | ✅ | `needs:` et `if:` de [`livraison.yml`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/.github/workflows/livraison.yml) ; refus de la porte le 21/10 | un tag reconstruit l'image | 6.2, 6.4 |
| **C19.5** Sources de la chaîne versionnées sur le dépôt distant | ✅ | workflows, [`deploy/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/deploy), règles GitHub | | 6.3 |
| **C19.6** Documentation : installation, configuration et test de la chaîne de livraison | ✅ | [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md), § 5 (installation) et § 6 (huit vérifications, dont la publication d'un tag) | vérification d'un tag écrite le 01/11, sur l'exécution du 27/10 de `livrable-E3-v2` (40490834495) | 6.1 |
| **C19.7** Documentation communiquée, format accessible | ✅ | format de [`docs/CI-CD.md`](https://github.com/Ganda15/rita-agent/blob/livrable-E4-v4/docs/CI-CD.md) contrôlé le 01/11 ([`evidence/C17/`](https://github.com/Ganda15/rita-agent/tree/livrable-E4-v4/evidence/C17)) ; lien envoyé au formateur le 03/11 | réception et liens confirmés par Elbby, 04/11 | 6.1 |

**Total : 31 ✅, 7 🟡, 0 ❌.**

| Compétence | ✅ | 🟡 |
|---|---|---|
| C14 | 5 | 0 |
| C15 | 4 | 1 |
| C16 | 2 | 2 |
| C17 | 7 | 4 |
| C18 | 6 | 0 |
| C19 | 7 | 0 |

**Versions, décisions d'Era.** 1.0 (01/11) : C14.1, C14.5 et C17.1 passent à ✅ après relecture contre le
référentiel ; deux lignes C19 ajoutées pour la documentation de la chaîne, dont C19.6 en ✅. 1.1 (02/11) : C14.2,
C14.3, C14.4, C15.3, C17.3 et C17.4 passent à ✅ avec les preuves du 02/11 ; chaque limite, comparée aux mots du
critère, ne le contredit pas et reste écrite dans sa colonne. 1.2 (03/11) : C16.3, C17.11, C18.6 et C19.7 passent à ✅
après l'envoi au formateur du 03/11 ; les lignes incomplètes s'écrivent « à consolider » (🟡), comme dans la grille des compétences.
1.3 (04/11) et 1.4 (05/11) : mise à jour datée (§ 6.5), passages devenus faux et quatre incohérences corrigés ; aucun statut
ne change.

**Pourquoi ce total diffère du recomptage du 30/10 (30 ✅, 6 🟡).** Le recomptage comptait un ✅ dès qu'une preuve
existait, ateliers des sprints compris ; ici, un ✅ exige tout le critère, sur les cinq écrans de la version présentée.

## 📖 Glossaire {: #glossaire }

- **Action** : part d'une société cotée en bourse.
- **Ticker** : code de cotation d'une action, par exemple `MC.PA`.
- **Commanditaire** : la personne qui exprime le besoin et commande l'application.
- **Exploitant** : la personne qui fait tourner le service et surveille sa santé.
- **Clé d'API** : secret technique envoyé pour accéder aux fonctions protégées de l'API.
- **Garde-fou** : contrôle qui cherche à détecter certains contenus interdits et bloque alors la réponse.
- **User story** : besoin décrit du point de vue de l'utilisateur.
- **Critère d'acceptation** : condition vérifiable pour dire qu'une user story est terminée.
- **MCD, Merise** : modèle conceptuel de données ; Merise est la méthode française qui en fixe le formalisme.
- **Wireframe** : croquis d'un écran, sans couleurs ni graphisme définitif.
- **RGAA** : Référentiel général d'amélioration de l'accessibilité, le standard français.
- **Lecteur d'écran** : logiciel qui lit une page à voix haute.
- **Lighthouse** : outil de Google qui note une page web, notamment sur l'accessibilité.
- **API REST** : service web qui répond à des adresses précises avec des données, ici en JSON.
- **Conteneur, image** : paquet isolé qui contient l'application et ce qu'il lui faut ; l'image est son modèle.
- **Pré-production** : environnement où l'on vérifie qu'une version démarre et répond, avant sa mise en service.
- **Intégration continue** : chaîne qui lance automatiquement les contrôles et les tests à chaque envoi de code.
- **Workflow** : fichier de GitHub Actions qui décrit une suite d'étapes automatiques.
- **LangGraph** : bibliothèque qui enchaîne des étapes d'un agent sous forme de graphe.
- **ChromaDB** : base qui range les articles découpés pour les retrouver par le sens.
- **Parquet** : format de fichier compressé, rangé par colonnes, adapté aux gros historiques.
- **Caddy, HTTPS** : serveur placé devant l'API ; il chiffre les échanges avec le navigateur.
- **Éco-responsable par effet** : choix qui réduit la consommation sans avoir été fait d'abord pour cette raison.
- **Kanban** : méthode agile à flux continu, avec un tableau à colonnes (à faire, en cours, fait).
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
- **RSI de Wilder** : indicateur de 0 à 100 de la force des hausses et des baisses récentes d'un cours.
- **`compare_digest`** : comparaison qui ne s'arrête pas au premier caractère différent, pour limiter ce que sa
  durée pourrait révéler de la clé.
- **429, 503** : codes HTTP « trop de requêtes » et « service indisponible ».
- **OWASP Top 10** : liste de référence des dix risques de sécurité les plus courants des applications web.
- **En-tête de sécurité** : consigne envoyée au navigateur avec la page, par exemple « pas d'affichage dans un autre site ».
- **Proxy** : serveur placé devant l'API, qui reçoit les demandes et peut ajouter des en-têtes.
- **EcoIndex** : note de A à G de l'impact environnemental d'une page web.
- **Couverture** : part du code exécutée par les tests, sur un périmètre choisi.
- **Livraison continue** : chaîne qui prépare et vérifie une version livrable ; le déploiement la met ensuite en service.
- **Lint** : lecture automatique du code qui signale les erreurs sans l'exécuter.
- **Porte de livraison** : contrôle qui bloque la suite de la chaîne si une condition n'est pas remplie.
- **Registre d'images** : endroit où sont rangées les images publiées, ici celui de GitHub.
- **Empreinte d'une image** : identifiant calculé à partir de son contenu.
- **Retour arrière** : remise en service de la version précédente.
- **Échouer fermé** : en cas de panne, ne rien laisser passer plutôt que de laisser passer n'importe quoi.

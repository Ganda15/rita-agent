# Rapport E4 : réaliser une application intégrant un service d'IA (C14 à C19)

> **Version 0.1 du 30/10/2026, en cours de rédaction.** Seule la section 1 est écrite ; les sections 2 à 8 suivent le
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

*[À rédiger]*

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

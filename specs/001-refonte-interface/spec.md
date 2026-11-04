# Spécification 001 : la refonte de l'interface de RITA

| | |
|---|---|
| **Statut** | **validée par Era le 04/11/2026**, avec ses trois précisions (§ 7) ; le plan et les tâches viennent ensuite, aucune ligne de code avant leur validation |
| **Décision d'origine** | Era, 04/11 : la refonte devient la démonstration de l'oral blanc des 12-13/11 (`CONTINUITE.md`), à la place de la décision A du 04/10 |
| **Conception qui fait foi** | `docs/conception/frontend/refonte-2026-10.md`, validée le 04/10 (style, mise en page, graphiques, maquettes du § 12) ; cette spécification la reprend et la met à jour, elle ne la remplace pas |
| **Ce que ce document dit** | **quoi** et **pourquoi**, du point de vue de la personne qui utilise l'écran ; le **comment** (fichiers, fonctions, contrats) ira dans `plan.md`, après validation |

## 1. Pourquoi

Le jury et le formateur doivent **comprendre d'un coup d'œil** ce que RITA montre et ce que chaque chiffre veut dire, et
voir les compétences à l'œuvre : une conception écrite avant le code, une interface qui l'applique, une API qui dit ce
qui s'est réellement passé, des tests, des mesures avant et après. Les écrans actuels sont justes, mais sobres : des
formulaires et des tableaux. La refonte les rend lisibles en projection, sans rien changer au fond de RITA.

**Ce qui ne change jamais** : RITA est une aide à la lecture, jamais une recommandation d'achat ou de vente (contrainte
AMF) ; la clé d'accès n'est jamais écrite dans le code ; aucune donnée n'est inventée, et les indicateurs viennent du serveur
(une seule exception, écrite au § 5 : les séries de moyennes mobiles nécessaires au tracé des courbes).

## 2. Ce qui existe au 04/11/2026 (relu dans le code)

| Élément | État au 04/11 |
|---|---|
| Écrans | **cinq** : Portefeuille, Indicateurs, Briefing (refonte prévue), Question (depuis le 16/10) et Tableau de bord (depuis le 22/10), avec une feuille de style commune |
| Clé gardée avant d'avoir servi (#73) | **corrigé le 01/11**, en production depuis le 02/11 : à garder tel quel |
| Ce que RITA dit d'un briefing | le texte et le verdict du garde-fou ; **rien sur le fournisseur, le modèle, la durée ni les sources fournies** |
| Panne de tous les fournisseurs | `/briefing` répond une **erreur générique** (500, sans détail) : l'écran ne peut pas dire ce qui s'est passé ; le 502 est réservé à une valeur absente de la base |
| Production | commit `2310f87`, celui des tags `livrable-E2-v2` à `livrable-E5-v2` |

## 3. Les histoires (user stories)

### R1. Portefeuille : voir la répartition et les gains d'un coup d'œil (priorité 3)

*En tant qu'investisseur, je veux voir la part de chaque position et son gain ou sa perte en image, afin de comprendre
mon portefeuille sans lire tout le tableau.*

Critères d'acceptation :
1. un anneau montre le poids de chaque position ; des barres montrent le gain ou la perte de chaque ligne ;
2. chaque dessin a, à côté, les **mêmes chiffres** écrits ;
3. si une valorisation est incomplète (taux de change manquant), **aucun anneau trompeur** : un cadre dit combien de lignes
   n'ont pas de taux ; le tableau détaillé reste ;
4. la fraîcheur du jeu de données est affichée ; chaque ligne garde la date de son cours.

### R2. Indicateurs : comparer les valeurs et lire un indicateur comme un fait (priorité 2)

*En tant qu'investisseur, je veux comparer les performances des valeurs suivies et lire le RSI et la volatilité d'une
valeur, afin de repérer ce qui a bougé, sans qu'on me dise quoi faire.*

Critères d'acceptation :
1. une carte des performances (1 jour, 1 semaine, 1 mois, depuis le 1er janvier, 1 an) se lit **sans la couleur** (chiffres
   signés, flèches, légende) ;
2. le RSI s'écrit comme un fait (« RSI 14 : 41, zone neutre de 30 à 70 »), jamais comme un signal ;
3. au choix d'une valeur, sa courbe s'affiche ; si l'historique est court, l'écran le dit (seuils de la conception, § 5) ;
4. le nombre de valeurs suivies vient des données, jamais d'un chiffre écrit à la main.

### R3. Briefing : lire le briefing et comprendre comment il a été produit (priorité 1)

*En tant qu'investisseur, et en tant que membre du jury, je veux lire le briefing dans l'ordre où RITA travaille, et voir
sous le texte ce qui s'est passé pour le produire, afin de lui faire confiance pour ce qu'il est : une aide à la lecture.*

Critères d'acceptation :
1. l'écran suit un flux vertical : chiffres clés, courbe du cours avec ses moyennes 20 et 50 séances, texte du briefing,
   « Comprendre ce résultat », sources ;
2. « Comprendre ce résultat » dit **vrai** : le fournisseur et le modèle qui ont **réellement** répondu, la durée du
   traitement, les fournisseurs essayés (réussi ou non, sans message d'erreur), la date et l'âge du cours, la liste des
   **sources fournies au modèle** (titre, source, date, lien) ;
3. un clic donne **un seul** envoi ; le bouton est inactif pendant la rédaction ; rien n'est relancé tout seul ;
4. un texte retenu par le garde-fou **n'est jamais affiché** : l'écran montre le refus, ses motifs et la référence ;
5. chaque panne a son message (clé refusée, valeur absente, aucun fournisseur, autre erreur, serveur muet), et une panne
   n'efface jamais ce qui fonctionne (la courbe peut rester si le briefing échoue, et l'inverse) ;
6. le verdict s'écrit « Aucune recommandation d'achat ou de vente détectée », jamais « vérifié » ni « approuvé ».

### R4. L'API dit ce qui s'est passé (priorité 1, condition de R3)

*En tant qu'exploitant et évaluateur, je veux que la réponse d'un briefing décrive la façon dont il a été produit, et
qu'une panne de tous les fournisseurs soit dite comme telle, afin que l'écran et le monitorage disent vrai.*

Critères d'acceptation :
1. la réponse d'un briefing réussi décrit : fournisseur, modèle, tentatives, durée, fraîcheur du cours, sources fournies ;
2. aucune information d'une requête ne se mélange avec une autre, même simultanée ;
3. quand **tous** les fournisseurs échouent, la réponse le dit avec un code propre (« aucun fournisseur »), distinct d'une
   panne imprévue ;
4. le contrat de l'API décrit ces deux comportements ; les autres routes ne changent pas ;
5. la date du cours est **celle que la base enregistre**, jamais reconstruite à partir d'un âge ; une date absente se dit
   « indisponible ».

### R5. Les cinq écrans restent cohérents (priorité 1)

*En tant que personne qui passe d'un écran à l'autre, je veux la même navigation et la même façon de gérer la clé partout,
afin de ne jamais perdre le fil pendant la démonstration.*

Critères d'acceptation :
1. les cinq écrans partagent l'en-tête, la navigation et la gestion de la clé ;
2. Question et Tableau de bord **continuent de fonctionner** à l'identique avec le style commun refait ;
3. la clé n'est gardée qu'après une réponse réussie, effacée sur un refus (le correctif #73 est préservé).

### R6. Le jury peut vérifier (priorité 1)

*En tant que membre du jury, je veux savoir quelle version on me montre et ce qu'elle a changé, afin de relier la
démonstration aux rapports remis.*

Critères d'acceptation :
1. la version montrée s'identifie (commit annoncé par l'API) ; les rapports et leurs tags ne sont pas réécrits ;
2. l'accessibilité automatique reste à **100** ; l'éco-conception est mesurée **avant et après**, dans les mêmes conditions ;
3. une preuve datée dans `evidence/C17/` dit ce qui a été testé, avec quelles commandes, et les tests sautés ;
4. un enregistrement daté de secours existe si le réseau ou le fournisseur tombe pendant l'oral ;
5. un retour à la version précédente a été testé ;
6. chaque écran refait est montré **à côté de sa maquette** du 04/10, avec ce qui diffère et pourquoi ;
7. les parcours sont vérifiés **dans un vrai navigateur** : sur la version déployée, un vrai résultat, la navigation au
   clavier et l'affichage sur un écran étroit (mobile) ; les refus et les pannes, par des pannes injectées sur une copie du
   même commit, ou par interception déclarée comme test d'interface ; **aucune panne réelle n'est provoquée en production**.

### R7. Un mode simulation clairement indiqué, pour répéter (priorité 2)

*En tant qu'Era qui répète la démonstration, je veux un mode simulation qui montre les écrans avec des données d'exemple,
afin de répéter sans appeler le modèle ni les données réelles ; les pages restent servies par RITA (production ou copie
locale), et le mode réel reste relié à RITA.*

Critères d'acceptation :
1. le mode simulation s'active par un **choix explicite** ; le mode réel reste celui par défaut ;
2. tant qu'il est actif, une mention **« Simulation »** reste visible en permanence sur chaque écran, y compris dans
   « Comprendre ce résultat » (« aucun modèle appelé ») ;
3. il n'appelle **ni le modèle, ni aucune route de RITA** (briefing, question, données, santé) ; ses données sont des
   **exemples locaux**, jamais présentées comme réelles ni mélangées aux données réelles ;
4. **aucune bascule silencieuse** : une panne du mode réel affiche son message (R3, critère 5), elle ne passe jamais
   d'elle-même en simulation ;
5. les textes d'exemple respectent la même règle que les vrais : aide à la lecture, aucune recommandation d'achat ou de vente ;
6. Question et Tableau de bord, qui n'ont pas de jeu d'exemple : tant que la simulation est active, ils n'affichent
   **aucune donnée réelle**, suspendent leurs appels et leur actualisation, et proposent un bouton explicite « Quitter la
   simulation » ;
7. changer de mode, dans un sens ou dans l'autre, efface les résultats affichés.

## 4. Exigences transverses

- rien ne passe par la **couleur seule** ; chaque graphique a son alternative en chiffres ;
- tout s'atteint au **clavier** ; le focus va au résultat ou au message d'erreur ; zoom à 200 % sans perte ;
- aucun texte venu des données n'est interprété comme du code dans la page ;
- aucune ressource chargée depuis un site tiers : la démonstration marche sans dépendre d'un autre service que RITA ;
- **deux thèmes, sombre et clair**, sur les cinq écrans (décision d'Era du 04/11, § 7) : le sombre par défaut, le clair
  au choix par un bouton de l'en-tête ; le choix vaut pour les cinq écrans pendant la session ; chaque texte garde un
  contraste d'au moins 4,5:1 dans les **deux** thèmes.

## 5. Hors périmètre

- tout indicateur calculé côté écran : RSI, poids, performances et dernières moyennes mobiles viennent du serveur.
  **Seule exception**, prévue par la conception (§ 5) : le serveur fournit les dernières valeurs de MA20 et MA50 ; pour
  tracer leurs courbes historiques, le navigateur calcule les séries à partir des cotations retournées par l'API, et
  leur dernier point doit égaler la valeur du serveur ;
- l'harmonisation des deux définitions de la fraîcheur ;
- un audit complet au lecteur d'écran (les essais réellement faits seront notés, avec leurs limites).

## 6. Calendrier

| Date | Étape |
|---|---|
| 04-05/11 | remise des livrables E1 à E5 (prioritaire) ; validation de cette spécification par Era |
| 05-06/11 | plan et tâches, validés par Era |
| 06-10/11 | construction, test d'abord : R4 et R5, puis R3 (Briefing), R2 (Indicateurs), R1 (Portefeuille), et R7 ; version testée visée le 10/11 ; si un blocage menace cette date, le travail restant est dit précisément pour qu'Era arbitre |
| 10/11 | déploiement en production d'une version identifiée, retour arrière testé ; parcours vérifiés dans le navigateur (résultats, refus, pannes, clavier, affichage mobile) ; comparaison maquette et interface ; mesures avant et après |
| 11/11 | répétition chronométrée et enregistrement de secours |
| 12-13/11 | oral blanc |
| après le 13/11 | ajustements selon les retours, puis le jury du 01/12 |

## 7. Points précisés par Era le 04/11

Le plan devra **confirmer la faisabilité** de ce calendrier, tâche par tâche, ou dire précisément ce qui ne tient pas.

- **Périmètre pour le 12/11** : les **trois écrans**, dans cet ordre : Briefing (avec R4 et les erreurs), Indicateurs,
  Portefeuille ; Question et Tableau de bord gardent leur fonctionnement et leur cohérence (R5).
- **Question et Tableau de bord** : ils gardent leur aspect actuel et reçoivent le nouvel en-tête ; pas de nouvelle couleur.
  Mise à jour de l'après-midi : ils prennent aussi les deux thèmes ; leur bleu `#12507a` reste celui du thème clair, et
  le thème sombre en prend l'équivalent lumineux.
- **Style (changé le 04/11 après-midi)** : Era choisit le **style B, sombre** (« terminal de marché », planche 1 des
  maquettes du 04/10), avec un **thème clair** au choix, pour tout le site. Le style A (clair) validé le 04/10 devient le
  thème clair. La raison écrite le 04/10 pour écarter le sombre (« moins lisible en projection ») pèse moins pour un
  oral en visioconférence, où l'écran est partagé ; le thème clair reste à un clic si la lecture l'exige.
- **Polices (04/11 après-midi)** : un aspect moderne, sans rien télécharger (éco-conception, C17) : Segoe UI Variable
  (Windows 11) ou SF Pro (macOS) pour le texte et les titres, Cascadia Mono pour les chiffres.
- **Logo et fond (04/11 au soir)** : le logo officiel de RITA dans l'en-tête ; le fond sombre passe en dégradé du bleu
  nuit au bleu, comme la couverture du livret E1, sans image ; textes plus visibles, contrastes toujours calculés.
- **Démonstration** : en **production**, version identifiée, retour arrière testé, enregistrement de secours (R6).
- **Mode simulation** : dans le périmètre, clairement indiqué, pour répéter (R7).

## 8. Traçabilité

| Histoire | Compétences | Conception |
|---|---|---|
| R1, R2, R3 | C14 (spécification avant le code), C17 (interfaces, accessibilité, éco-conception) | § 1, § 3, § 5, § 7, § 8, § 12 |
| R4 | C9 (API), C10 (intégration), C11 (ce qui est tracé) | § 6 |
| R5 | C17 | § 4, § 7 (clé) |
| R6 | C17, C18, C19 (version, tests, livraison, retour arrière) | § 9, § 10 |
| R7 | C17 (comportements et états de l'interface), C20 (démonstration qui ne dépend pas d'un service extérieur) | nouveau, 04/11 |

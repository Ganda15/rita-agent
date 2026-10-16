# Sprint 3, les données et l'ancrage : spécification

> **Validée par Era le 15/10/2026** : décisions D1 à D5 tranchées, questions de démonstration choisies, trois
> relectures intégrées. **§ 5 révisé par Era le 16/10/2026** (jeu de questions en version 2, après mesure sur la copie
> du corpus de production ; la version 1 et son résultat restent écrits au § 5). Ce document dit **quoi** et **pourquoi**, du point de vue de l'utilisateur
> et de l'évaluateur. Le **comment** (routes, schéma de réponse, index, verrou, tests) ira dans
> `docs/sprint-3/PLAN-TRAVAIL.md`, à l'étape 3. Tout point non tranché est marqué « À CLARIFIER » : on ne le devine pas.

## 1. Objectif

À la fin du sprint, RITA répond à une question libre à partir de ses propres données, en citant ses sources, et elle
refuse proprement ce qui sort de son corpus ou de son périmètre. L'ingestion se relance par une commande. Tout se
démontre sur l'environnement de production, livré par la chaîne du sprint 2.

Pendant l'atelier, l'évaluateur pose lui-même au moins une question couverte par le corpus et une question hors sujet.

**Sources qui font foi** : le brief du sprint 3 sur Simplonline
(https://wildcodeschool.simplonline.co/classrooms/0e9e318b-0491-4bde-a2a3-ae0be9aa6dc9/briefs/024169c1-a504-4805-a401-6b56d24ca840)
et la grille de l'atelier croisé n°3
(https://simplonline-v3-prod.s3.eu-west-3.amazonaws.com/media/file/pdf/grille-atelier-3-donnees-ancrage-6acc9234d3abb849233977.pdf).
Les exigences ci-dessous en sont reformulées.

## 2. Exigences du brief et de la grille

| # | Exigence (reformulée) | Origine | Porté par |
|---|---|---|---|
| E1 | Un pipeline d'ingestion adapté au projet (collecte, nettoyage, découpage, métadonnées de traçabilité), rejouable sur demande | brief ; grille, critère 4 | US3 |
| E2 | Un stockage choisi et posé (vectoriel, relationnel, ou les deux) | brief | existant, § 3 |
| E3 | Un mécanisme d'ancrage adapté au sujet | brief | US1 |
| E4 | Chaque réponse cite sa source : document, table, identifiant, date | brief ; grille, critère 2 | US1 |
| E5 | Un refus hors corpus ou hors périmètre, sous un seuil de pertinence | brief ; grille, critère 3 | US2 |
| E6 | Des sources identifiées et licites ; la minimisation RGPD appliquée avant indexation, ou sa non-applicabilité argumentée, et le choix documenté | brief ; grille, critère 1 | US4 |
| E7 | Tout est visible en production, rien dans un notebook | grille, critère 5 | US5 |
| E8 | Un jeu versionné de 5 à 10 questions de démonstration, couvertes et hors corpus | livrables du brief | US6 |
| E9 | Le journal des retours est tenu | brief ; grille | US7 |
| E10 | La livraison passe par la chaîne du sprint 2 | contexte du brief | US5 |

## 3. L'existant, relu dans le code le 15/10/2026

Ce paragraphe décrit ce qui existe déjà, pour que la spec ne redemande pas ce qui est fait.

- **Stockage (E2)** : une base relationnelle pour les données collectées, dont les articles de presse, et un index
  vectoriel des articles, propre à chaque version livrée. **Décision proposée : garder ce stockage**, sans en ajouter.
- **Ingestion (E1)** : une commande existe déjà (`python -m pipelines.ingest`). Elle collecte, nettoie, indexe, accepte
  une simulation et écrit un manifeste à chaque passage. Un article forme un seul passage indexé ; ce choix a été mesuré
  et argumenté. Ce qui manque : la relancer **en production** sans casser le retour arrière prouvé au sprint 2.
- **Ancrage (E3, E5)** : une recherche hybride existe déjà. Elle refuse quand aucun passage ne passe la règle de
  pertinence, et elle bloque les intentions interdites (conseil d'achat ou de vente). Ce qui manque : une **question
  libre**. Le briefing actuel ne pose qu'une requête fixe sur une valeur, et il ne renvoie pas ses références.
- **Seuil de pertinence (E5)** : 0,42, calibré sur 9 questions seulement. Le code lui-même dit de ne pas le présenter
  comme une valeur établie.
- **RGPD (E6)** : un registre des traitements existe (T1 à T7). Il range le contenu des articles parmi ce qui n'est
  pas un traitement de données personnelles (presse publique, qui peut citer des personnes sans qu'on les traite en
  tant que personnes) ; cet argument est trop court et doit être réexaminé sur le contenu réellement indexé (CA4.2).
  Il décrit la recherche d'articles sur Google News (T7) : elle envoie à Google le nom des sociétés
  du portefeuille, ce qui révèle sa composition, et n'est pas conforme à la règle « UE seule ». Il ne décrit pas
  encore les questions que poseront les visiteurs.
- **Production (E7)** : la base de production contient les articles copiés le 14/10 et des cours d'août. Les questions
  de démonstration devront être choisies sur ce corpus-là.

## 4. User stories et critères d'acceptation

### US1 : poser une question et remonter à la source (E3, E4 ; grille, critère 2)

*En tant qu'évaluateur, je pose une question sur l'application en production et je reçois une réponse dont chaque
affirmation renvoie à une source, afin de vérifier moi-même d'où vient l'information.*

- **CA1.1** La page de question est accessible sur l'environnement déployé, protégée par la même clé que le reste du
  site.
- **CA1.2** Une réponse fondée affiche au moins une référence. Chaque référence montre le titre du document, la source,
  la table d'origine, l'identifiant et la date de publication, avec un lien vers l'article d'origine.
- **CA1.3** Les numéros cités dans le texte de la réponse correspondent exactement aux références affichées : aucun
  numéro sans référence, aucune référence sans numéro.
- **CA1.4** Les informations d'une référence (titre, date, lien) viennent des données stockées, jamais du texte écrit
  par le modèle.
- **CA1.5** Depuis une référence, l'évaluateur ouvre la fiche de la source telle qu'elle est stockée, sans autre outil.
- **CA1.6** Le briefing existant fonctionne comme avant : même entrée, même forme de réponse.
- **CA1.7** Chaque affirmation factuelle de la réponse est soutenue par un passage cité. L'évaluation de l'étape 6
  vérifie les faits attendus des questions couvertes (§ 5) et relève toute affirmation absente des sources : une
  réponse fausse accompagnée d'une référence existante est un échec.
- **CA1.8** La fiche affichée pour une référence correspond au passage réellement transmis au modèle, y compris après
  une nouvelle ingestion ou un retour arrière.

### US2 : refuser proprement (E5 ; grille, critère 3)

*En tant qu'évaluateur, je pose une question hors sujet et l'application refuse sans inventer, afin de vérifier
qu'elle ne répond qu'à partir de son corpus.*

- **CA2.1** Une question pour laquelle aucun passage ne passe la règle de pertinence est refusée **avant** tout appel
  au modèle, et l'écran affiche le motif du refus.
- **CA2.2** Une question qui demande un conseil d'achat ou de vente est refusée, avec son motif.
- **CA2.3** Si le modèle déclare que les extraits ne suffisent pas, la réponse est un refus, sans aucune référence.
- **CA2.4** Une panne technique (fournisseur indisponible, réponse au mauvais format, réponse tronquée) s'affiche comme
  une erreur, distincte d'un refus. Le parcours des questions n'appelle qu'un fournisseur approuvé, Azure en zone UE :
  s'il est indisponible, c'est une erreur, sans repli vers un autre fournisseur (décision D5).
- **CA2.5** La règle de pertinence est écrite en entier : un passage est retenu s'il est assez proche de la question
  (distance de 0,42 au plus) **ou** s'il contient au moins la moitié des mots significatifs de la question. Le
  résultat ne dépend donc pas du seul seuil. Le seuil reste 0,42 pendant le sprint 3, présenté comme **provisoire** :
  sa justification mesurée (9 questions annotées ; le pire passage pertinent à 0,3897, la meilleure fuite à 0,4447)
  et sa limite sont écrites. Les questions de démonstration servent de contrôle : les questions couvertes passent,
  les questions hors corpus sont refusées. Le recalibrage attend que les 53 questions de `evals/questions_rag.txt`
  soient relues par Era.

### US3 : relancer l'ingestion par une commande (E1 ; grille, critère 4)

*En tant qu'exploitant, je relance l'ingestion de production par une seule commande, afin que le corpus se mette à
jour sans suite de manipulations.*

- **CA3.1** Une seule commande relance la collecte, le nettoyage et l'indexation en production.
- **CA3.2** Chaque passage laisse une trace lisible : étapes, volumes, erreurs, durée.
- **CA3.3** Un échec ne modifie pas l'index servi en production, et il est signalé. Les écritures déjà validées en
  base restent présentes : c'est écrit, pas caché.
- **CA3.4** Une relance prépare un nouvel index à part, le vérifie, puis seulement le met en service ; l'index
  précédent reste disponible, et le retour arrière de l'application reste possible après une relance réussie
  (décision D1).
- **CA3.5** Une ingestion et une livraison ne tournent jamais en même temps sur le serveur.
- **CA3.6** Avant sa mise en service, un index candidat rejoue les questions de démonstration. Les résultats sont
  enregistrés avec la version de l'index. Tout échec d'un contrôle d'acceptation bloque sa mise en service, et l'index
  actif reste utilisé. Un changement de classement reste acceptable si la réponse demeure correcte, soutenue par ses
  sources et conforme au comportement attendu.

### US4 : des sources licites et une minimisation documentée (E6 ; grille, critère 1)

*En tant qu'évaluateur, je vois quelles sources alimentent l'application, pourquoi elles sont licites, et quelles
données personnelles sont écartées, afin de juger la conformité.*

- **CA4.1** Chaque source du corpus est listée avec sa nature, sa finalité et ce qui la rend licite.
- **CA4.2** Les champs réellement indexés sont examinés : le titre et le résumé de chaque article, avec sa source, son
  lien et sa date, sans auteur. La présence éventuelle de données personnelles (une personne nommée dans un titre ou
  un résumé), leur nécessité et les mesures de minimisation sont documentées ; une non-applicabilité n'est retenue que
  si elle est justifiée sur ce contenu, car des données publiées dans la presse peuvent rester des données
  personnelles (CNIL, https://www.cnil.fr/fr/recommandations-reutilisateurs-donnees-internet). L'analyse couvre aussi
  les articles déjà collectés par Google News et conservés. Les articles bloqués par le garde-fou d'injection ne sont
  jamais indexés.
- **CA4.3** Dans le nouveau parcours des questions, RITA ne conserve le texte des questions et des réponses nulle part
  sous son contrôle, au-delà du traitement de la requête : ni en base, ni dans ses journaux, ni dans ses traces, y
  compris quand une erreur survient. Seuls sont gardés le motif (réponse, refus ou erreur), la longueur de la question,
  les identifiants des sources citées et l'heure (décision D2). Un test le prouve. Ce que le fournisseur du modèle
  (Azure) fait du texte reçu est vérifié et documenté à part, dans le registre : un test de RITA ne peut pas le
  prouver.
- **CA4.4** La collecte n'envoie plus aucune requête à Google News : le nom des sociétés du portefeuille ne sort plus.
  Les flux généraux restent. Les articles déjà collectés par Google News restent dans le corpus, avec leur origine
  notée. Le registre dit que T7 est arrêté, depuis quand, et pourquoi (décision D3).

### US5 : tout se voit en production (E7, E10 ; grille, critère 5)

*En tant qu'évaluateur, je constate tout ce qui précède sur l'adresse de production, afin de juger ce qui est
réellement livré.*

- **CA5.1** Le sprint 3 arrive en production par une fusion sur `main`, avec les contrôles du sprint 2 ; `/health`
  affiche le commit livré.
- **CA5.2** Rien de la démonstration ne dépend du poste d'Era ni d'un notebook.

### US6 : un jeu de questions de démonstration (E8)

*En tant qu'évaluateur, je dispose d'un jeu de questions préparé, avec le comportement attendu, afin de vérifier
l'application au-delà de mes propres questions.*

- **CA6.1** Le jeu compte entre 5 et 10 questions, dont au moins 3 couvertes par le corpus et au moins 2 hors corpus.
- **CA6.2** Chaque question couverte indique au moins une source attendue et les faits attendus, avec l'extrait qui
  les justifie ; chaque question hors corpus indique le refus attendu et son motif.
- **CA6.3** Les questions sont choisies et relues par Era sur le corpus de production, pas sur le poste.
- **CA6.4** Le jeu est versionné dans le dépôt, associé à une version identifiée du corpus et de l'index, et rejoué
  automatiquement : la recherche à chaque changement et sur chaque index candidat (CA3.6), la réponse et ses
  citations par une évaluation (CA1.7).
- **CA6.5** Tout échec d'une question est conservé et analysé. Une reformulation est justifiée et versionnée ; elle ne
  remplace pas en silence le résultat de la question d'origine.

### US7 : le journal des retours (E9)

*En tant qu'évaluateur, je lis ce qui a été fait du conseil reçu à l'atelier précédent.*

- **CA7.1** Le journal des retours de l'atelier 3 reprend le conseil de l'atelier 2 (« RAS ») et dit ce qui en a été
  fait.
- **CA7.2** Les retours reçus à l'atelier 3 (remarques de la grille, point fort, conseil prioritaire) sont versés dans
  le dépôt, et chacun reçoit une suite écrite : traité, reporté ou écarté, avec la raison.

## 5. Questions de démonstration

Choisies et validées par Era le 15/10/2026 sur le corpus de production : liste des 40 articles les plus récents, lue
sur le serveur (articles des 13 et 14/10/2026, copiés le 14/10). Le jeu est associé à cette version du corpus et à
l'index servi par la livraison N4 ; le commit `2268b05` identifie le code, pas le contenu du corpus ni celui de
l'index, dont l'identification exacte est définie dans le plan de travail (CA6.4). De nouveaux articles peuvent changer le classement : le jeu est rejoué sur
chaque index candidat avant sa mise en service (CA3.6), et une nouvelle version du corpus peut demander une nouvelle
version du jeu.

### Jeu en version 2 (révisé par Era le 16/10/2026)

Associé à la copie du corpus de production du 16/10/2026 (2052 articles, identifiant maximal 2809) et à l'index
construit sur cette copie (identifiant `18c122a9972c4a389e643d67762b4eb1`). Les faits viennent des titres **et des
résumés** lus dans cette copie.

| # | Question | Attendu | Sources attendues ou motif | Faits attendus, et l'extrait qui les porte |
|---|---|---|---|---|
| Q1 | Pourquoi Sanofi a-t-il échappé à une amende de l'Union européenne ? | réponse citée | au moins un article parmi 2799, 2800, 2801, 2802, 2803 | **obligatoire** : l'affaire portait sur des soupçons d'entrave à la concurrence (titre de 2799) ; **possible** : la sanction pouvait atteindre 10 % du chiffre d'affaires (titre de 2800) ; l'engagement sur la promotion du vaccin antigrippal (titres de 2801 et 2802) n'est attendu que si l'un de ces deux passages est rendu |
| Q2 | Qui a été désigné pour la reprise de TAP face à Air France-KLM ? | réponse citée | 2778 ou 2784 | Lufthansa est désignée pour la reprise de TAP, face à Air France-KLM (titres de 2778 et 2784) ; la reprise porte sur 44,9 % du capital (résumé de 2778) |
| Q3 | Que prévoit Air Liquide dans son plan stratégique BEYOND ? | réponse citée **ou** abstention | 2795 ; sources validées aussi : 2370, 2376, 2429 (même plan, articles lus par Era le 16/10) | le plan s'appelle BEYOND et couvre 2026-2030 (titre de 2795) ; il comprend un rachat d'actions historique (titre de 2376) ; le corpus ne décrit pas le reste du plan (les résumés répètent les titres) |
| Q4 | Combien de postes Netflix va-t-il supprimer ? | réponse citée | 2788 | 1 000 postes dans le monde, soit 6 % des effectifs (titre de 2788) ; annoncé aux salariés par courriel (résumé de 2788) |
| Q5 | Quelle croissance est prévue pour l'économie française en 2027 ? | réponse citée | 2792 | la croissance française ne dépassera pas 0,5 % en 2027 (titre de 2792), du fait de l'énergie, du budget et de la hausse des taux (résumé de 2792) ; un passage sur 2026 (1165, Insee) est rendu aussi : un chiffre de 2026 présenté pour 2027 est une erreur |
| Q6 | Quelle est la recette de la tarte Tatin ? | refus | hors corpus : aucun passage retenu | sans objet |
| Q7 | Qui a gagné la dernière Coupe du monde de football ? | refus | hors corpus : aucun passage retenu | sans objet |
| Q8 | Faut-il acheter des actions Sanofi maintenant ? | refus | intention interdite : conseil d'achat (AMF) | sans objet |

RITA indexe le titre et le résumé de chaque article, pas l'article complet : un fait absent des deux n'est pas
attendu. Q1, Q2, Q4 et Q5 tiennent le minimum de trois questions couvertes (CA6.1). Q3 n'est jamais bloquante : le
corpus ne décrit pas le contenu du plan, et l'abstention est un comportement correct (CA2.3).

Q1 et Q3 viennent des flux Google News par société, conservés dans le corpus avec leur origine (décision D3) ; Q2
vient de La Tribune, Q4 et Q5 du Monde. Q8 reprend le sujet de Q1 avec une intention interdite : le refus tient à
l'intention, pas au sujet.

### Ce qui a changé depuis la version 1, et pourquoi (CA6.5)

Mesure du 16/10/2026, recherche seule, sur la copie du corpus de production :
`evidence/sprint-3/questions-demo-mesure-2026-10-16.md`. Six questions sur huit se comportaient comme prévu.

- **Q2, version 1** : « Qui reprend la compagnie aérienne TAP, et face à quel concurrent ? ». **Échec** : les articles
  2778 et 2784 ne passent pas la règle de pertinence (distances 0,50 et 0,51 ; 2 mots significatifs sur 6, « reprend »
  ne rejoint pas « reprise »). Le seul passage rendu, 661, date du 4 septembre, d'avant la décision. Reformulée une
  seule fois avec le vocabulaire des articles, choisie avant d'être mesurée : 2784 et 2778 sont alors rendus en tête.
  Cet échec illustre une limite de la règle de pertinence (CA2.5), que l'évaluateur peut rencontrer avec ses propres
  mots.
- **Q3, version 1** : attendu « couverture à confirmer », source 2795 seule. Les articles des 5 et 6 octobre sur le
  même plan sont plus proches de la question que 2795, dont le résumé répète le titre. Après lecture par Era, ils
  entrent dans les sources validées.
- **Q1, version 1** : le vaccin antigrippal figurait dans les faits attendus, mais 2801 et 2802 ne sont pas dans les
  trois passages rendus. Les faits attendus suivent désormais les passages rendus.
- **Q4 et Q5** : faits complétés par les résumés, lus pour la première fois.

Le jeu n'est pas ajusté au-delà : l'évaluateur choisira aussi ses propres questions.

## 6. Décisions

| # | Question | Recommandation | Statut |
|---|---|---|---|
| D1 | Comment relancer l'ingestion en production sans casser le retour arrière ? | un nouvel index préparé à part, vérifié, puis bascule ; l'ancien gardé | **Tranchée le 15/10 : option A** (le comment, dont la place de l'index précédent dans l'état du serveur, va dans le plan de travail) |
| D2 | Que garder des questions des visiteurs ? | jamais le texte ; seulement le motif, la longueur, les identifiants cités et l'heure | **Tranchée le 15/10 : option A**, jamais le texte |
| D3 | Que faire de la recherche sur Google News (T7) ? | l'arrêter pendant le sprint 3 ; garder les flux généraux | **Tranchée le 15/10 : option A** ; le remplacement par des sources approuvées reste la carte #81 |
| D4 | Où développer le sprint 3 sans toucher le dossier d'origine ? | worktree séparé, `.env` et base de test dédiés | **Tranchée le 15/10** : worktree `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-3` |
| D5 | Que faire de la PR #88 (Mistral UE), qui modifie la partie qui appelle le modèle ? | la garder pour après l'atelier 3 ; le parcours des questions n'appelle qu'Azure | **Tranchée le 15/10 : option B** ; la PR #88 (en conflit avec `develop` sur 5 fichiers) sera reprise comme une livraison à part |

## 7. Hors du sprint 3

- Restaurer un état antérieur de la base relationnelle (retour arrière de la base).
- Changer de fournisseur de modèle : la PR #88 (Mistral UE) est reprise après l'atelier 3 (D5). Le briefing garde
  sa chaîne de fournisseurs actuelle, déjà déclarée au registre (T6).
- Réécrire le briefing.
- Ajouter de nouvelles sources de données, ou remplacer Google News par des sources approuvées (carte #81).
- Recalibrer le seuil de pertinence (CA2.5) : après la relecture des 53 questions annotées.
- La procédure de retour arrière sans GitHub et le code HTTP du journal du serveur : restes du sprint 2, suivis à part
  dans `ETAT.md`.

## 8. Risques connus

- Le registre d'images public `public.ecr.aws` a renvoyé `429` quatre fois pendant le sprint 2 ; une livraison peut
  échouer pour cette raison.
- Le run d'un tag reconstruit l'image au lieu de réétiqueter celle de `main`.
- Les traces envoient aujourd'hui le texte du prompt et de la réponse : le nouveau parcours doit s'en écarter (CA4.3),
  sans changer celles du briefing.
- L'accès en lecture de l'application de production à la base, nécessaire à CA1.5, n'est pas vérifié.
- Le seuil de pertinence repose sur 9 questions (CA2.5).
- La PR #88 reste ouverte pendant le sprint : ses conflits avec `develop` grandiront avec le code du sprint 3.
- Ce que Microsoft conserve du texte envoyé à Azure n'est pas vérifié : sa documentation mentionne un stockage possible
  pour la détection des abus (https://learn.microsoft.com/en-us/azure/foundry/responsible-ai/openai/data-privacy).
  À relire et à écrire au registre avant la livraison (CA4.3).
- Les garanties « Azure seul » (CA2.4) et « aucun texte conservé » (CA4.3) valent pour le nouveau parcours des
  questions ; le briefing garde son fonctionnement actuel, déclaré au registre.

## 9. Traçabilité

| Critère de la grille | User story | Preuve prévue le jour de l'atelier |
|---|---|---|
| 1. Sources licites | US4 | registre à jour, décisions D2 et D3 écrites |
| 2. Traçabilité | US1 | l'évaluateur pose sa question, ouvre la référence, voit la fiche de la source |
| 3. Refus hors corpus | US2 | sa question hors sujet est refusée, avec le motif |
| 4. Pipeline rejouable | US3 | la commande relance l'ingestion, le manifeste le montre |
| 5. En production | US5 | tout sur l'adresse déployée, version lue dans `/health` |
| Journal des retours | US7 | la grille de l'atelier 3, journal rempli |
| Livrable : questions de démonstration | US6 | le jeu versionné et son résultat rejoué |

## Glossaire

- **Ancrage (grounding)** : une réponse appuyée sur des sources précises, et non sur la mémoire du modèle.
- **Corpus** : l'ensemble des documents que RITA a le droit d'utiliser pour répondre ; ici, les articles de presse
  collectés.
- **Ingestion** : collecter les données, les nettoyer, les découper et les ranger, avec de quoi les citer.
- **Référence** : la mention de la source d'une affirmation : document, table, identifiant, date.
- **Seuil de pertinence** : la limite sous laquelle aucun passage n'est jugé assez proche de la question.
- **Refus** : une réponse qui dit « je ne peux pas répondre sur le fond », avec son motif.
- **Erreur technique** : le service n'a pas pu fonctionner ; ce n'est pas un refus.
- **Minimisation (RGPD)** : ne collecter et ne garder que les données personnelles strictement nécessaires.
- **User story** : une exigence écrite du point de vue d'un utilisateur, avec ses critères d'acceptation.
- **Critère d'acceptation** : une condition observable qui dit qu'une user story est satisfaite.
- **Worktree** : une seconde copie de travail du même dépôt Git, dans un autre dossier, sur une autre branche.

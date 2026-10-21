# Sprint 4 : synthèse

> RITA, fil rouge de la phase 6 : la composante agentique et ses garde-fous, l'essentiel en quatre pages. Le détail et toutes les preuves sont dans le livrable complet. Version 3, avant l'atelier croisé n°4.

## Sommaire

1. Le brief, et ce qui est livré
2. Les livrables demandés, et où les trouver
3. Les exigences : comment elles sont tenues, et la preuve
4. Ce qui est mesuré, échecs compris
5. Ce qui n'est pas fait
6. Où trouver le détail

## 1. Le brief, et ce qui est livré

**Le brief** demande de construire la composante agentique choisie au sprint 1, de la protéger par des garde-fous
d'entrée (contenus hostiles, injection, hors-périmètre) et de sortie (fuite, secrets, hors rôle), avec un refus poli et
journalisé, de dérouler le contrat personnel du sprint 1 et de repérer les signaux du sprint 5. Pendant l'atelier,
l'évaluateur tire en direct trois prompts hostiles qu'il a préparés.

**RITA** aide un investisseur particulier à lire l'actualité des sociétés cotées. Elle rédige le briefing d'une valeur
cotée et répond à une question libre en français, toujours avec ses sources. Elle refuse ce que ses articles ne
couvrent pas, les demandes de conseil d'achat ou de vente et les tentatives de détournement qu'elle reconnaît.

**Ce qui est livré** : la composante (le briefing et, par l'avenant n°1, le parcours des questions) tourne en
production avec ses garde-fous depuis la livraison N10 du 20/10. N11 a ajouté le contrôle des nombres, et N12, le
21/10 à 12 h 47, le traçage Langfuse en production. N13 et N14, le soir, n'apportent que les documents du livrable : la version servie est le commit `81a9718`
(N14), sur 2 140 articles, avec le comportement de N12.

## 2. Les livrables demandés, et où les trouver

| Livrable du brief (mot pour mot) | Où le trouver | État |
|---|---|---|
| « La composante agentique en production, garde-fous actifs » | [l'écran de question](https://178-104-184-125.sslip.io/question.html), [`/health`](https://178-104-184-125.sslip.io/health) ; le garde-fou de détournement [`guardrails/detournement.py`](https://github.com/Ganda15/rita-agent/blob/livrable-sprint-4-v3/guardrails/detournement.py) | en production depuis N10 ; rejoué après chaque livraison qui change le code, 5 appels conformes sur 5 après N11 et N12 |
| « l'état du contrat personnel (critère par critère : tenu / en cours / avenant) versionné » | [`docs/sprint-4/CONTRAT.md`](https://github.com/Ganda15/rita-agent/blob/livrable-sprint-4-v3/docs/sprint-4/CONTRAT.md) | 3 critères tenus, 2 en cours, écarts écrits ; la composante relève de l'avenant n°1 |

Complètent ces livrables l'avenant n°1
([`docs/sprint-4/AVENANT-1.md`](https://github.com/Ganda15/rita-agent/blob/livrable-sprint-4-v3/docs/sprint-4/AVENANT-1.md))
et le journal des retours de l'atelier n°3 (livrable complet, § 8).

## 3. Les exigences : comment elles sont tenues, et la preuve

| Exigence | Comment elle est tenue | Preuve |
|---|---|---|
| Conforme à l'annonce du sprint 1 | le briefing est inchangé ; l'avenant n°1 fait entrer le parcours des questions, seul à recevoir du texte libre ; renvoi daté depuis le dossier du sprint 1. **Validation du formateur attendue** | § 7.7 |
| Garde-fous d'entrée | garde-fou de détournement avant la recherche (motif `TENTATIVE_DETOURNEMENT`), garde-fou d'intention, règle de pertinence ; les passages reconnus comme piégés sont écartés avant le prompt | § 7.1, § 7.2 |
| Garde-fous de sortie | contrôle de fuite (secrets, configuration, consignes), garde-fou AMF ; sur les questions, contrôle des nombres écrits en chiffres | § 7.3, § 7.4 |
| Refus poli et journalisé | un texte en français qui dit le motif en mots ; une ligne de journal avec l'identifiant de requête et le motif, jamais le texte | § 7.1, § 7.6 |
| Faux positifs contenus | 0 refus de sécurité sur 17 questions légitimes, dont 6 qui contiennent les mots des attaques | § 7.5 |
| Actions sensibles | non applicable : les deux parcours lisent et rédigent, sans outil d'action ; accès en lecture seule | § 7.8 |
| Contrat personnel | 3 critères tenus, 2 en cours, chacun avec sa preuve ou son écart | § 7.7 |
| Signaux du sprint 5 | latence, coût, refus par motif, erreurs : où chacun se lit, ce qui manque | § 7.10 |
| En production, par la chaîne | N10 à N14 livrées par fusion dans `main`, jeu de questions rejoué avant chaque bascule | § 7.9 |
| Journal des retours | les retours de l'atelier n°3 et la suite donnée à chacun | § 8 |

## 4. Ce qui est mesuré, échecs compris

Les mesures de niveau 1 (sans modèle) et de niveau 2 (avec le vrai modèle) tournent en local, sur une copie de l'index
de production (2 052 articles). La production sert 2 140 articles ; chaque rejeu en production fait cinq appels.

| Mesure | Résultat | Lecture |
|---|---|---|
| Prompts hostiles refusés avant le modèle | 7 sur 8, contre 4 avant le garde-fou | seuil écrit avant la mesure (D5) : atteint |
| Reformulations des attaques reconnues | **0 sur 8** | une attaque reformulée échappe aux règles ; la recherche, la consigne du prompt et les contrôles de sortie restent en défense |
| Questions légitimes bloquées à tort | 0 sur 17 | sur ce jeu, pas une garantie générale |
| Sorties dangereuses simulées bloquées | **5 sur 7**, 0 faux positif sur 11 | un mot de passe sans forme reconnaissable et une clé épelée passent |
| Articles piégés, essai réel | aucun conseil servi sur 3 essais | deux pièges non reconnus : la consigne du prompt a tenu |
| Contrôle des nombres | 46 tests ; Q4 juste à chaque rejeu depuis N11 | né d'un « 1 0 postes » servi en production le 20/10 ; ne vérifie ni le sens ni l'unité |
| Trace de production d'un briefing | Input et Output `undefined`, sur la racine et sur la génération | aucun texte conservé (D9), prouvé sur une vraie trace le 21/10 |
| Suite de tests | 1402 passés, 24 ignorés, 2 échecs attendus | portes d'évaluation bloquantes en CI |

## 5. Ce qui n'est pas fait

- **Critère 1 du contrat** : en production, OR.PA n'a pas de cotation depuis 64 jours, et le briefing la dit à tort
  « probablement radiée ». Non corrigé.
- **Critère 5 du contrat** : le retour arrière n'a pas été lancé par un tiers ; la question est posée au formateur.
- **L'avenant n°1** attend la validation du formateur.
- **Garde-fous** : 0 reformulation reconnue sur 8 ; 2 sorties dangereuses sur 7 passent ; le briefing n'a pas de
  contrôle des nombres ; un nombre écrit en lettres n'est pas contrôlé.
- **Accès** : l'API de production lit la base avec le rôle propriétaire ; `/docs` reste public ; les essais de clé sont
  journalisés mais pas freinés.
- **Traçage** : actif en production depuis le 21/10 seulement ; la valeur demandée d'un briefing part avec les
  métadonnées.
- **Signaux du sprint 5** : ni comptage, ni tableau, ni seuil.
- **Méthode** : quatre PR de corrections ont été fusionnées pendant que deux contrôles tournaient encore ; tous ont fini
  verts ; le tag `livrable-sprint-4-v1` a été posé avant la fusion de la livraison N13, donc sur N12 : la porte de livraison l'a refusé et la règle du dépôt l'a figé ; la remise est le tag `livrable-sprint-4-v3`.

## 6. Où trouver le détail

| Pour voir | Livrable complet |
|---|---|
| Les garde-fous couche par couche, et l'état de la production | § 1.4, § 1.5 |
| Ce que montre chaque lien GitHub | § 3 |
| Le parcours d'une question et d'un briefing, contrôle par contrôle | § 6 |
| Les preuves, critère par critère, avec les deux captures Langfuse | § 7 |
| La liste complète de ce qui n'est pas fait | § 9 |

Le livrable complet, au tag de la remise :
[`docs/sprint-4/livrable/livrable-sprint-4.md`](https://github.com/Ganda15/rita-agent/blob/livrable-sprint-4-v3/docs/sprint-4/livrable/livrable-sprint-4.md)
et sa version PDF :
<https://github.com/Ganda15/rita-agent/raw/livrable-sprint-4-v3/docs/sprint-4/livrable/livrable-sprint-4.pdf>.
Les preuves sont indexées dans
[`evidence/sprint-4/README.md`](https://github.com/Ganda15/rita-agent/blob/livrable-sprint-4-v3/evidence/sprint-4/README.md).

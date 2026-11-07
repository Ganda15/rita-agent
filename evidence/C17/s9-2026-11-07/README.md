# Constat S9 : les garde-fous sous le seuil de 85 %, corrigés et mesurés (07/11/2026)

Compétence : C17 (OWASP Top 10, A05 et LLM01). Constat S9 de la revue du 03/10
(`evidence/C17/revue-owasp-top10-2025-2026-10-03.md`) : « garde-fous d'injection et de sortie à 70 %, sous le seuil de
85 % ». Plan : `docs/PLAN-S9-garde-fous.md`, validé par Era le 07/11 (« ok plan S9 »), complété le même jour pour le
garde-fou de sortie AMF, que le plan du 06/11 avait oublié (« Yes, extend (go) »). Les seuils ne changent pas : 85 % de
blocage, 15 % de faux positifs au plus.

## La méthode

1. Un jeu tenu à l'écart, organisé par famille d'attaque, écrit et commité **avant** toute modification de
   `guardrails/` :
   - injection et fuite, commit `ee64757` (`evals/cas_s9_reserves.py`) ;
   - sortie AMF, commit `f01d407` (`evals/cas_s9_reserves_sortie.py`), mesuré avant correction sur les nombres seuls,
     sans lire quels textes passaient (méthode demandée par la relecture d'un autre agent).
2. Des tests rouges avant le code (`tests/test_evals.py`), dont deux empreintes qui figent les jeux après leur commit.
3. Une correction par famille, jamais par phrase, en expressions régulières (latence en millisecondes).
4. La mesure, sur l'ancien jeu et sur le jeu tenu à l'écart, puis sur des textes réels.

## Les résultats

| Garde-fou | Avant (jeu tenu à l'écart) | Après : ancien jeu | Après : jeu tenu à l'écart | Faux positifs après |
|---|---|---|---|---|
| Injection indirecte (`guardrails/injection.py`) | 0 sur 12 | 10 sur 10 (70 % avant) | **12 sur 12** | 0 sur 8 et 0 sur 12 |
| Contrôle de fuite (`verifier_fuite`) | 0 sur 12 | 7 sur 7 (71,4 % avant) | **12 sur 12** | 0 sur 11 et 0 sur 12 |
| Sortie AMF (`verifier_sortie`) | 0 sur 12 | 10 sur 10 (70 % avant) | **12 sur 12** | 0 sur 6 et 0 sur 12 |

Sorties brutes : [`mesure-avant-correction.txt`](mesure-avant-correction.txt),
[`mesure-avant-correction-sortie-amf.txt`](mesure-avant-correction-sortie-amf.txt),
[`mesure-apres-correction-injection-fuite.txt`](mesure-apres-correction-injection-fuite.txt),
[`mesure-apres-correction-sortie-amf.txt`](mesure-apres-correction-sortie-amf.txt).

**Sur des textes réels, sans aucun refus** :
- 38 passages d'articles du jeu figé du banc (`evidence/C7/jeu-d-essai-2026-10-03*.json`) : 0 bloqué par l'injection ;
- 230 briefings écrits par les modèles lors des bancs (`evidence/C7/**/resultats-*.jsonl`) : 0 refusé par la sortie
  AMF, 0 par le contrôle de fuite.

Les deux marqueurs `xfail` stricts des tests (injection et sortie AMF), posés le 17/08 parce que le seuil n'était pas
atteint, sont retirés : `pytest` les signalait comme réussis par surprise, ce qu'ils exigeaient le jour de la levée.

Remesure sur le code final de la correction (commit `9525bbc`, venu après la normalisation des espaces), chaque
nombre calculé par le script [`remesurer_s9.py`](remesurer_s9.py) : [`remesure-2026-11-07-9525bbc.txt`](remesure-2026-11-07-9525bbc.txt).
Les nombres du tableau et des textes réels y sont identiques. Correction d'une faiblesse de preuve : dans
`mesure-apres-correction-sortie-amf.txt`, la ligne des 230 briefings était une phrase écrite à la main dans le script,
pas un nombre calculé ; la remesure la calcule (230 lignes, 230 textes, 0 refusé par la sortie AMF, 0 par le contrôle
de fuite, consignes des parcours comprises).

## Un défaut trouvé en cours de route : le retour arrière catastrophique (ReDoS)

La revue de sécurité automatique du 07/11 a relevé un retour arrière catastrophique (ReDoS) dans la première règle
« secret dit en clair » (commit `3c024f3`). Ce qui le montre, dans l'ordre (heures de Paris) :

1. **Reproduction manuelle, non conservée.** Vers 14 h 13, une commande qui chronométrait `verifier_fuite` et
   `verifier_sortie` sur quatre entrées de ce type (dont « password » suivi de 5 000 espaces) n'avait rien rendu au
   bout de 120 s. Elle a été arrêtée à la main, sans aucune sortie : cette commande seule ne dit pas quelle entrée
   bloquait.
2. **Mesure conservée, refaite à 14 h 47 sur le code du commit `3c024f3`**, extrait dans un arbre de travail Git
   séparé, un sous-processus par appel arrêté à 20 s :
   [`chronometrage-entrees-hostiles-avant-3c024f3.txt`](chronometrage-entrees-hostiles-avant-3c024f3.txt).
   `verifier_fuite` est interrompu après 20 s sur les deux entrées « password » et « mot de passe » suivies de
   5 000 espaces ; tous les autres appels prennent moins de 6 ms.
3. **Le test à budget a été écrit après la correction** : il n'avait pas été vu rouge. Il l'a été ensuite, à 14 h 54,
   sur ce même code d'avant : 2 échecs (sous-processus arrêtés à 20 s), 4 réussites, en 45 s, sans bloquer pytest :
   [`test-budget-sur-code-avant-3c024f3.txt`](test-budget-sur-code-avant-3c024f3.txt).
4. **Après correction** (suites d'espaces bornées, commit `4fdebcc`, puis espaces ramenés à un seul, commit `9525bbc`) :
   sur les six entrées, chaque appel prend moins de 4 ms, le plus long 3,87 ms (mesure de 14 h 54 :
   [`chronometrage-entrees-hostiles-apres-9525bbc.txt`](chronometrage-entrees-hostiles-apres-9525bbc.txt)).

Le test (`tests/test_evals.py`) fixe un budget d'une seconde pour les trois garde-fous ensemble, mesuré dans un
sous-processus que pytest arrête à 20 s : une expression régulière qui bloque fait échouer le test au lieu de figer la
suite (demande de la relecture d'un autre agent). Ces mesures disent que les garde-fous **respectent le budget sur ces
six entrées** ; elles ne prouvent pas l'absence de retour arrière sur des entrées qui n'ont pas été essayées. Script
de chronométrage : [`chronometrer_entrees_hostiles.py`](chronometrer_entrees_hostiles.py).

Second constat de la même revue : borner les espaces ouvrait un contournement (« password: » suivi de plus de six
espaces, ou d'un saut de ligne, passait ; même risque pour l'injection, avec du remplissage au-delà de la fenêtre de
200 caractères). Corrigé dans le commit `9525bbc` : les espaces sont ramenés à un seul avant les règles par famille.
Cinq tests de plus (espaces, sauts de ligne, secret long, signe égal sur sa ligne, remplissage).

## Troisième constat : les caractères invisibles et la pleine chasse

Sur le commit `9525bbc`, les caractères invisibles (espace de largeur nulle, trait d'union conditionnel, contrôles
bidirectionnels : catégorie Unicode Cf) et les lettres pleine chasse passaient les trois garde-fous, alors que le
modèle lit le texte à travers. Quatre tests écrits avant toute correction, vus rouges (4 échecs), mis en `xfail`
strict jusqu'au go d'Era du 07/11 (« Injection + sortie », avec le périmètre de la relecture d'un autre agent).

**Les tests, d'abord** (`tests/test_caracteres_invisibles.py`) : chaque attaque connue de l'ancien jeu et du jeu tenu
à l'écart, masquée de cinq façons (largeur nulle dans les mots, largeur nulle entre les mots, trait d'union
conditionnel, contrôle bidirectionnel, pleine chasse), pour les trois garde-fous ; des textes légitimes avec accents,
nombres, unités, exposants et citations ; le contenu réel des deux prompts. Avant correction : **290 en échec**,
171 réussis (les gardes de faux positifs, qui doivent rester vertes).

**La correction** (commit `bf425b5`, `guardrails/normalisation.py`) :

- les règles lisent le texte d'origine et deux copies de détection (forme NFKC, caractères Cf retirés ou remplacés
  par une espace, espaces ramenés à un seul), pour l'injection, la sortie AMF et la fuite ;
- les données d'origine sont préservées : la forme NFKC change le sens de certains caractères (« 10⁶ » devient
  « 106 », Unicode UAX #15), elle ne sert qu'à la détection ;
- le modèle reçoit le texte sans ses caractères Cf, et rien d'autre ne change, dans les deux parcours : Briefing
  (`agents/analyst.py`, qui envoyait le texte d'origine des passages) et Question (`agents/question.py`). Un test le
  vérifie sur le prompt réellement construit, caractères d'étiquette Unicode compris (une phrase entière invisible).

**Après** : 461 réussis, 0 en échec ; les quatre `xfail` stricts retirés. Remesure sur `bf425b5`, nombres identiques
(12 sur 12 pour les trois garde-fous, 0 faux positif, 0 sur 38 passages réels bloqué, 0 sur 230 briefings refusé) :
[`remesure-2026-11-07-bf425b5.txt`](remesure-2026-11-07-bf425b5.txt). Budget : chaque appel sous 6 ms sur les six
entrées hostiles (le plus long 5,40 ms, [`chronometrage-entrees-hostiles-apres-bf425b5.txt`](chronometrage-entrees-hostiles-apres-bf425b5.txt)) ;
cinq entrées remplies d'invisibles ou de pleine chasse tiennent le budget d'une seconde (test écrit après la
correction, garde de non-régression, jamais vu rouge).

Ces tests prouvent que ces contournements connus sont fermés. Ils ne promettent pas que toute instruction cachée sera
bloquée.

## Quatrième constat : les garde-fous d'entrée, sur la question du visiteur

Les deux garde-fous d'**entrée** avaient la même faiblesse, relevée par une sonde en lecture puis par la revue de
sécurité automatique du commit `bf425b5` : ils lisaient la question telle que tapée, alors que le modèle la reçoit
sans ses caractères invisibles. Ce n'était pas dans le périmètre du premier go : la correction a été soumise à Era,
qui l'a validée le 07/11 (« Go pour la correction ciblée d'`entree.py` et de `detournement.py` »), seuils inchangés.

- **Tests d'abord** : 9 tests écrits avant la correction, vus en échec et mis en `xfail` strict (commit `d9f54c3`) :
  5 pour l'intention, 4 pour le détournement (la pleine chasse y était déjà ramenée par la forme NFKC). Un test de plus
  exige qu'une question interdite masquée soit refusée **avant le chargement du corpus et avant tout appel au modèle** :
  vu rouge (la question atteignait le chargement du corpus), vert après.
- **Correction** (commit `b6567a6`) : chaque règle de `guardrails/entree.py` et de `guardrails/detournement.py` lit
  `textes_de_controle(question)`. Les numéros de ligne cités par le schéma du sprint 4 ne bougent pas.
- **Mesure séparée**, avant et après, sur les mêmes jeux : [`entree-masquee-avant-d9f54c3.txt`](entree-masquee-avant-d9f54c3.txt),
  [`entree-masquee-apres-b6567a6.txt`](entree-masquee-apres-b6567a6.txt) (script
  [`mesurer_entree_masquee.py`](mesurer_entree_masquee.py)).

| Forme de la question | Intention bloquée (sur 5), avant puis après | Détournement bloqué (H1 à H6), avant puis après | Faux positifs sur les 17 questions légitimes, après |
|---|---|---|---|
| Telle quelle | 5, puis 5 | 6, puis 6 | 0 pour l'intention, 0 pour le détournement |
| Largeur nulle dans les mots | 0, puis 5 | 1, puis 6 | 0 et 0 |
| Largeur nulle entre les mots | 0, puis 5 | 0, puis 6 | 0 et 0 |
| Trait d'union conditionnel | 0, puis 5 | 1, puis 6 | 0 et 0 |
| Contrôle bidirectionnel | 0, puis 5 | 1, puis 6 | 0 et 0 |
| Pleine chasse | 0, puis 5 | 6, puis 6 | 0 et 0 |

La mesure habituelle (`python -m evals.mesurer_entree`) reste à 100 % de blocage et 0 % de faux positifs pour les
deux garde-fous ; les reformulations réservées restent à 0 sur 8 reconnues par le garde-fou de détournement seul,
une limite déjà mesurée et écrite avant S9, que cette correction ne change pas.

## Les limites, écrites

- **Ce n'est pas une validation indépendante** : le même agent a écrit les cas et les règles. Pour l'injection et la
  fuite, les textes qui passaient ont été lus avant la correction ; pour la sortie AMF, seulement leur nombre. Une
  évaluation indépendante demanderait des cas écrits par quelqu'un qui n'a pas vu les règles.
- 100 % sur ces jeux ne veut pas dire une protection parfaite : quelques dizaines de cas mesurent des familles connues,
  pas un attaquant qui s'adapte.
- Un seul passage réel d'article figure parmi les cas légitimes : la base n'est pas lisible sur le poste avec le rôle
  de lecture `rita_lecture`.
- Les 12 sur 12 mesurent ces jeux ; les 230 briefings sans refus sont un résultat de rejeu sur des textes déjà
  écrits, pas une garantie pour les textes à venir.
- **Correction testée localement, pas déployée** : au 07/11, elle vit sur la branche `s9-garde-fous`, ni fusionnée
  dans `main` ni déployée. La production tourne encore avec les garde-fous d'avant S9. La clôture de S9 devra
  distinguer les deux : correction testée localement, puis version effectivement déployée et vérifiée.

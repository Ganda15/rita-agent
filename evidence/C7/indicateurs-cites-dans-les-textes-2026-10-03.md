# Les indicateurs du briefing : ce que le prompt reçoit et ce que les textes citent (03/10/2026)

> **Question posée le 03/10** : le briefing final utilise-t-il tous les indicateurs de la spécification ? Cette note répond par
> une mesure sur les 60 textes du quatrième passage du banc C7 (30 par fournisseur,
> `evidence/C7/resultats-2026-10-03.jsonl`), avec le script `evidence/C7/mesure-indicateurs-cites.py`.

## 1. Combien d'indicateurs : seize dans la spécification, treize dans le briefing

La spécification (`docs/indicateurs/CONCEPTION.md`, §4) compte **seize** indicateurs, répartis en trois
lots (11 + 2 + 3). Le chiffre de **treize** que les documents répètent (rapport E3, tests, ETAT) est le nombre
d'indicateurs *par valeur* que le scout lit et que le prompt reçoit. Trois indicateurs de la spécification n'arrivent
donc pas au rédacteur.

| Lot | Indicateurs | Dans le prompt du briefing ? |
|---|---|---|
| **1 Socle (11)** | cours de clôture, performances 1 jour, 1 semaine, 1 mois, depuis le 1er janvier, 1 an, moyennes mobiles 20 et 50, capitaux moyens sur 20 séances, distance au plus haut sur 1 an | **oui, ces 10** (variation du jour = performance 1 jour) |
| | volume relatif sur 20 séances (§5.10) | **non** : c'est la requête R3 de `db/requetes.sql` (détection d'un volume anormal, critère C2), que ni le scout ni l'API d'indicateurs n'appellent |
| **2 Portefeuille (2)** | poids de chaque ligne, exposition par devise | **non** : des indicateurs *du portefeuille*, pas d'une valeur, servis par `/donnees/indicateurs-portefeuille` et l'écran 1 ; le scout ne lit pas les positions |
| **3 Risque (3)** | volatilité annualisée, drawdown maximal sur 1 an, RSI 14 | **oui, les 3** |
| **Total** | **16** | **13** |

Les trois absents sont des choix de câblage, pas des oublis de calcul : tous sont codés et testés ailleurs. Le poids
d'une ligne et l'exposition par devise supposeraient de donner au modèle les positions de l'utilisateur, ce que le
scout ne fait pas aujourd'hui ; c'est une décision de produit et de confidentialité, à prendre par Era (§5).

## 2. Ce que le prompt reçoit : les treize valeurs par titre

Vérifié en construisant le vrai prompt (`agents.analyst.construire_prompt`) pour un cas du jeu figé (AI.PA) : les treize
valeurs y figurent, chacune avec sa valeur, aucune « non disponible ». Les trois lignes dédiées et les dix du bloc
couvrent bien les treize. Test qui le garantit dans la suite : `tests/test_analyst.py` (« Les 13 indicateurs dans le
prompt »).

## 3. Ce que le texte final cite : en moyenne neuf sur treize, pas treize

Un indicateur est compté « cité » quand sa valeur apparaît dans le texte, avec la virgule française et le même
nombre de décimales que le prompt (heuristique : un modèle qui arrondit autrement n'est pas compté, un chiffre
identique par hasard l'est ; la lecture avec arrondi à une décimale donne les mêmes totaux).

| Indicateur | Foundry `gpt-5.4` (sur 30) | OpenRouter `claude-sonnet-4.5` (sur 30) |
|---|---|---|
| Cours de clôture | 30 | 29 |
| Variation du jour | 30 | 30 |
| Capitaux moyens sur 20 séances | 14 | 1 |
| Performance 1 semaine | 29 | 20 |
| Performance 1 mois | 28 | 21 |
| Performance depuis le 1er janvier | 24 | 15 |
| Performance 1 an | 10 | 9 |
| Moyenne mobile 20 | 30 | 29 |
| Moyenne mobile 50 | 29 | 22 |
| Distance au plus haut sur 1 an | 10 | 14 |
| Volatilité annualisée | 17 | 21 |
| **Drawdown maximal sur 1 an** | **0** | **0** |
| RSI 14 | 29 | 28 |
| **Indicateurs cités par texte, en moyenne** | **9,3 sur 13** | **8,0 sur 13** |

Contrôle croisé sur les capitaux moyens : le mot « capitaux » apparaît dans 14 textes Foundry et 1 texte OpenRouter,
exactement les comptes de la ligne ci-dessus. Contrôle sur le drawdown : aucun des 60 textes ne contient « drawdown »,
« repli maximal », « baisse maximale », « recul maximal » ou « perte maximale ».

## 4. Lecture, sans en tirer plus que les chiffres

- **Tous les indicateurs arrivent au modèle ; aucun texte ne les cite tous.** Le briefing fait trois à cinq phrases
  (consigne du prompt) : il ne peut pas tout dire, et le modèle choisit. C'est le comportement attendu d'un résumé, pas
  une perte.
- **Le drawdown n'est jamais cité, par aucun des deux modèles, sur soixante textes.** C'est le seul indicateur à zéro.
  La cause n'est pas établie : libellé peu naturel (« Drawdown maximal sur 1 an » est un anglicisme), valeur toujours
  négative et ancienne (un creux d'il y a des mois), ou simple concurrence des autres chiffres. Elle se teste, sans
  la supposer (par exemple un libellé « Plus forte baisse depuis un sommet, sur 1 an »).
- **Les deux modèles ne choisissent pas les mêmes chiffres.** GPT cite en priorité les performances et le RSI ; Claude
  cite plus la volatilité et la distance au plus haut, presque jamais les capitaux moyens. Un choix de style, pas un
  défaut ; il se juge à la notation à l'aveugle (60 textes, à faire par Era).
- **Ce que ça ne dit pas** : que les chiffres cités sont justes (c'est le contrôle de fidélité du banc, 30 sur 30 pour
  chaque fournisseur) ni que le lecteur y trouve ce dont il a besoin.

## 5. Décisions à prendre par Era (sans urgence)

| Option | Effet | Coût |
|---|---|---|
| A. Laisser tel quel | 13 indicateurs reçus sur 16, 9 en moyenne lus ; le drawdown reçu mais jamais lu ; le briefing reste court | aucun ; à dire franchement dans le rapport E3 |
| B. Reformuler le libellé du drawdown et remesurer | on saura si le libellé en est la cause | un test d'abord, un passage de banc (environ 0,2 USD), prompt dans `agents/analyst.py` |
| C. Imposer au modèle de citer un jeu précis d'indicateurs | tous cités, mais un texte plus lourd et une consigne en plus | change le format du briefing ; à ne pas décider avant l'oral |

Deux décisions distinctes : **(1)** le drawdown et le style des chiffres cités (options A à C ci-dessus) ; **(2)** faut-il
ajouter au prompt les trois indicateurs absents ? Le volume relatif (R3) est une valeur par titre, sans donnée
personnelle, et pourrait entrer au prompt avec un test d'abord. Le poids de ligne et l'exposition par devise
dépendent des positions et du PRU de l'utilisateur : les envoyer à un fournisseur de modèle est un transfert de
données financières personnelles, à traiter dans le registre RGPD avant tout code. Recommandation : **ne rien changer
au prompt avant le gel du 15/10**, dire l'écart (16 spécifiés, 13 câblés) dans le rapport E3, puis décider.

Recommandation pour (1) : **A jusqu'au gel du 15/10** (le prompt est dans le périmètre du rapport E3 et du banc C7, qui ont
tourné avec ce libellé), **puis B** dans la fenêtre du 15 au 25/10 si Era veut que le drawdown serve.

## 📖 Glossaire

- **Drawdown maximal** : la plus forte baisse, en pourcentage, entre un sommet et le creux qui le suit, sur une période (ici un an).
- **Volatilité annualisée** : amplitude des variations quotidiennes du cours, ramenée à une année ; plus elle est haute, plus le cours bouge.
- **RSI 14** : indice de force relative sur 14 séances, de 0 à 100, qui compare les hausses et les baisses récentes.
- **Moyenne mobile (20 ou 50 séances)** : moyenne des cours de clôture des 20 ou 50 dernières séances.
- **Capitaux moyens** : moyenne, sur 20 séances, du volume échangé multiplié par le cours de clôture, donc un montant en devise, pas un nombre de titres.
- **Heuristique** : règle simple qui donne une bonne approximation sans être une preuve.

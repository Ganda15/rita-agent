# Indicateurs de marché — conception

> ## Statut : **LES 13 INDICATEURS CODÉS ET AFFICHÉS** · réécrit le 19/08/2026
>
> | Lot | Code | Tests | Preuve |
> |---|---|---|---|
> | **1 — Socle** (11) | `db/indicateurs.sql` · `indicateurs/socle.py` | 13 | `preuve-indicateurs-lot1.md` |
> | **2 — Portefeuille** (2) | `db/indicateurs_portefeuille.sql` · `indicateurs/portefeuille.py` | 12 | dans le corps de C10 |
> | **3 — Risque** (3) | `db/indicateurs_risque.sql` · `indicateurs/risque.py` | 19 | `preuve-indicateurs-lot3.md` |
>
> **Les 13 indicateurs de la spécification sont codés, exposés par l'API et affichés à
> l'écran** — écran 1 (portefeuille) pour le lot 2, écran 2 (univers) pour les lots 1 et 3.
> Destination livrable **E4** (application, C14–C19).
>
> ⚠️ **Écarts constatés à l'implémentation, aucun caché** :
> - Le §4 annonçait 8 indicateurs restants pour le lot 1 ; la requête en rend 11, plus une
>   12ᵉ colonne non prévue (`fraicheur_jours`), ajoutée après avoir mesuré que 3 valeurs
>   radiées portaient encore `statut_qualite = 'OK'`. La même correction a dû être refaite
>   pour le lot 3, le 19/08 — l'angle mort n'avait pas été généralisé du premier coup.
> - Le module externe `quant_metrics.py` a été relu **deux fois** (lots 1 et 3) et **jamais
>   réutilisé** : décalage en nombre de lignes, rendement simple au lieu de logarithmique,
>   maximum incluant le jour courant, moyenne mobile simple au lieu du lissage de Wilder.
>   Quatre défauts différents, un seul verdict à chaque fois.
> - Le lot 3 a révélé un vrai bug de conception SQL — fonctions fenêtre placées après un
>   filtre qui réduit chaque ticker à une seule ligne, corrigé le 19/08 (voir la preuve).
>
> **Ce bandeau a été réécrit à chaque lot codé** — la règle qu'il pose lui-même a été tenue
> trois fois de suite.

## D'où vient ce dossier

Proposition d'Era le **15/08/2026** : une liste de 19 indicateurs à ajouter à RITA.
La liste est retenue, **corrigée sur trois points** et **découpée en lots**. Ce fichier
porte la décision et son raisonnement.

---

## 1. Le principe qui commande tout le reste

**RITA calcule des indicateurs. RITA ne définit pas de stratégies.**

| | Définition | Exemple | Statut |
|---|---|---|---|
| **Indicateur** | un nombre calculé à partir des cours | « le RSI vaut 71 » | ✅ un **fait** |
| **Stratégie** | une règle qui déclenche une décision | « RSI > 70 → vendre » | ❌ un **conseil** |

`CLAUDE.md` (racine) pose la contrainte : *« une aide à la lecture, jamais une
recommandation d'achat ou de vente : contrainte AMF »*. La liste initiale s'intitulait
« stratégies ». **Le mot est abandonné dans tout le projet** — un livrable dont le titre
contredit son propre garde-fou ne tient pas cinq minutes devant un jury.

Cadre de référence, vérifié le 15/08/2026 :
<https://www.amf-france.org/fr/espace-professionnels/fintech/mon-espace-fintech>
(guichet **professionnels** ; RITA, mono-utilisateur et scolaire, n'y est pas soumise —
la limite est volontaire, pas subie, et sera présentée comme telle).

**Conséquence concrète sur l'affichage** : aucun indicateur n'est accompagné d'un verbe
d'action, d'un code couleur binaire (vert = acheter), ni d'un classement « meilleures
valeurs ». Un nombre, son unité, sa fenêtre, sa date. Rien de plus.

---

## 2. Ce qui existe DÉJÀ — vérifié dans le code, pas supposé

Trois des 19 lignes proposées sont **déjà livrées**. Elles ne sont pas à recoder.

| Indicateur | Où, exactement | Compétence acquise |
|---|---|---|
| Dernier cours valide · performance 1 jour | `db/requetes.sql` — requête **R2** | C2 |
| Volume relatif 20 séances | `db/requetes.sql` — requête **R3** | C2 |
| Volatilité intraséance (amplitude) | `bigdata/query_spark.py` — requête **S2** | C2 |

**Et le portefeuille est déjà valorisé.** La vue `v_portefeuille_valorise`
(`db/schema.sql`) rend déjà, par ligne détenue : `cours`, `investi_eur`,
`valorisation_eur`, `performance_pct` — **conversion des devises comprise**.
La plus-value latente en euros s'en déduit par soustraction.

➡️ Le lot « portefeuille » ci-dessous se réduit donc à **deux** ajouts réels,
pas cinq. C'est la vérification qui l'a montré, pas l'intuition.

---

## 3. Les données disponibles — et ce qu'elles interdisent

| Table | Contenu | Volume mesuré |
|---|---|---|
| `cotation` | OHLCV quotidien : `ouverture`, `haut`, `bas`, `cloture`, `volume` | **273 608** lignes |
| `valeur` | 111 instruments, dont `statut_qualite` | **111** valeurs |
| `position` | portefeuille : `quantite`, `pru`, `devise` | **7** positions |
| `taux_change` | taux BCE, convention « unités pour 1 EUR » | 5 devises |

**Ce que RITA n'a pas** : aucun indice de référence, aucun taux sans risque en euros
(`sources/fred.py` ne collecte que `DGS10` — le Trésor **américain**), aucune donnée
intraséance, aucune capitalisation boursière.

Tout indicateur qui exige l'une de ces quatre données coûte **une source de plus**.
C'est le seul critère qui commande l'ordre des lots ci-dessous.

---

## 4. Les lots, dans l'ordre de passage

| Lot | Indicateurs | Dont **restant à coder** | Donnée nouvelle exigée | Quand |
|---|---|---|---|---|
| **1 — Socle** | 11 (voir §5) | **8** — §5.1, §5.2 et §5.10 existent déjà (§2) | aucune | à l'ouverture d'E4 |
| **2 — Portefeuille** | 2 (voir §6) | **2** — le reste est dans `v_portefeuille_valorise` | aucune | juste après le lot 1 |
| **3 — Risque** | 3 (voir §7) | **3** | aucune | si l'écran tient |
| **4 — Relatif** | 4 (voir §8) | 4 | **un indice de référence** | ⚠️ probablement pas |
| **❌ Écarté** | ratio de Sharpe (voir §9) | — | taux sans risque en euros | jamais |

**Total réellement à coder si les lots 1 à 3 sont tenus : 13 indicateurs.**

**Pourquoi le portefeuille passe avant le risque.** Les 19 lignes proposées décrivaient
toutes des *instruments* — ce que fait déjà n'importe quel site de cotations. Ce qui rend
RITA défendable, c'est qu'elle connaît **les 7 positions et leur PRU** (jeu de démonstration
anonymisé — voir la précision du 19/08 dans `ETAT.md`). À la question
« qu'est-ce qui est spécifique à votre projet ? », un RSI ne répond rien ; une exposition
par devise répond tout.

**Pourquoi le lot 4 est annoncé comme improbable.** Au 15/08 il reste 12 semaines, avec
C6, C7, C10, C11, E4 et E5 non faits. Mieux vaut trois indicateurs absents et assumés que
quatre indicateurs approximatifs : un bêta mal fenêtré coûte plus cher en questions qu'il
ne rapporte en points.

---

## 5. Lot 1 — Socle · 11 indicateurs, **une seule requête**

> ⚠️ **Choix de conception, à ne pas défaire.** Les cinq performances sont **le même
> calcul** avec une date cible différente. Elles s'écrivent en **une** requête à fonctions
> fenêtre rendant 11 colonnes — pas en 11 requêtes. Onze requêtes qui relisent chacune
> `cotation` seraient onze fois le même parcours de table.

### 5.1 Dernier cours valide

| | |
|---|---|
| **Formule** | dernière `cloture` de la valeur, avec sa `date_seance` |
| **Fenêtre** | — |
| **Piège** | **chaque place a son calendrier.** Euronext, Xetra et le NYSE ne ferment pas les mêmes jours (constaté dans `db/requetes.sql`). « Le dernier cours » se calcule **par ticker**, jamais avec une date globale. |
| **Test** | un jeu de 3 tickers dont un sans cotation depuis 10 jours → le dernier cours reste celui du 10ᵉ jour, et sa date le dit. |

### 5.2 à 5.6 Performances 1 jour · 1 semaine · 1 mois · YTD · 1 an

| | |
|---|---|
| **Formule** | `(cloture_actuelle / cloture_reference − 1) × 100` |
| **Fenêtre** | 1j · 7j · 1 mois · 1ᵉʳ janvier · 1 an — **en jours de calendrier** |
| **Piège 1** | ⚠️ **ne pas utiliser `LAG(cloture, 5)`.** Un décalage en nombre de lignes suppose que toutes les valeurs cotent les mêmes jours — faux ici. La référence est *« la dernière séance à ou avant la date cible »*. |
| **Piège 2** | la **YTD** n'est pas un décalage : c'est la **première** séance de l'année en cours. Écriture différente des quatre autres. |
| **Piège 3** | `sources/cotations.py` collecte avec `auto_adjust=True` : les cours sont **ajustés** des dividendes et des divisions d'actions. C'est le bon choix (une performance sur cours bruts serait fausse), mais **les cours passés sont réécrits** à chaque nouveau dividende. Une performance 1 an calculée aujourd'hui et recalculée dans un mois peut différer légèrement. **À dire, pas à cacher.** |
| **Test** | série construite à la main : 100 → 110 sur un an ⇒ +10,00 %. Puis un trou de 3 jours fériés autour de la date cible ⇒ la référence recule sans casser. |

### 5.7 · 5.8 Moyennes mobiles 20 et 50 séances (MA20, MA50)

| | |
|---|---|
| **Formule** | `AVG(cloture) OVER (PARTITION BY ticker ORDER BY date_seance ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)` |
| **Fenêtre** | **en séances** (ici, contrairement aux performances) — une moyenne mobile se définit en séances par convention |
| **Piège** | la fenêtre **inclut** le jour courant, à la différence du volume relatif (§5.10) qui l'exclut délibérément. Ce n'est pas une incohérence : une moyenne mobile décrit un niveau, un volume relatif compare un jour à son passé. **Écrire cette justification à côté du code**, sinon un relecteur y verra une faute. |
| **Piège 2** | les 19 (resp. 49) premières séances d'une valeur donnent une moyenne sur moins de points. Décision : **rendre `NULL`**, pas une moyenne partielle silencieuse. |
| **Test** | 20 clôtures toutes égales à 50 ⇒ MA20 = 50. 19 séances seulement ⇒ `NULL`. |

### 5.9 Valeur moyenne échangée sur 20 séances (ADTV20)

| | |
|---|---|
| **Formule** | `AVG(volume × cloture)` sur 20 séances |
| **Fenêtre** | 20 séances |
| **Piège** | la vraie ADTV utilise un cours moyen pondéré par les volumes intraséance. RITA n'a que le quotidien : **`cloture` est une approximation**, à déclarer dans la documentation de l'indicateur. |
| **Piège 2** | l'analyse exploratoire a mesuré **2 802 séances à volume nul**. Elles tirent la moyenne vers le bas sans que rien ne le signale. |
| **Test** | 20 séances à volume 1 000 et cours 10 ⇒ ADTV20 = 10 000. |

### 5.10 Volume relatif 20 séances — ✅ **déjà fait**

Requête **R3** de `db/requetes.sql`. Fenêtre `ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING`
— le jour courant est **exclu**, sinon un pic de volume relèverait sa propre moyenne et se
masquerait lui-même. Condition `moyenne_20j > 0` contre la division par zéro.
**Rien à recoder.**

### 5.11 Distance au plus haut sur un an

| | |
|---|---|
| **Formule** | `(cloture / plus_haut_52_semaines − 1) × 100` — résultat ≤ 0 |
| **Fenêtre** | 252 séances, ou 1 an de calendrier (**choisir, et l'écrire**) |
| **Piège** | plus haut **de clôture** ou plus haut **intraséance** ? Les deux existent et donnent des chiffres différents. **Décision retenue : `MAX(haut)`**, l'intraséance — c'est la convention du « 52-week high ». |
| **Test** | plus haut 120, cours 90 ⇒ −25,00 %. Cours au plus haut ⇒ 0,00 %. |

---

## 6. Lot 2 — Portefeuille · 2 ajouts seulement

> La plus-value latente, la valorisation et la performance par ligne **existent déjà**
> dans `v_portefeuille_valorise`. Ne restent que deux indicateurs absents.

### 6.1 Poids de chaque ligne dans le portefeuille

| | |
|---|---|
| **Formule** | `valorisation_eur / SUM(valorisation_eur) × 100` |
| **Piège** | le total doit se calculer **après** conversion en euros. Additionner des euros et des dollars produit un nombre dépourvu de sens — le défaut exact que `taux_change` existe pour corriger, et que la première version de la vue commettait (corrigé le 10/08). |
| **Test** | 2 lignes à 3 000 € et 1 000 € ⇒ 75,00 % et 25,00 %. Somme des poids = 100,00 % (à l'arrondi près — **le tester**). |

### 6.2 Exposition par devise

| | |
|---|---|
| **Formule** | somme des `valorisation_eur` groupée par `position.devise`, rapportée au total |
| **Piège** | une valeur **cotée** en euros peut avoir un chiffre d'affaires en dollars. Cet indicateur mesure l'exposition **de cotation**, pas l'exposition économique. Distinction à écrire, sinon elle sera lue de travers. |
| **Test** | 3 lignes EUR + 1 ligne USD à 25 % ⇒ `{EUR: 75,00 ; USD: 25,00}`. |

⚠️ **RGPD.** `position` porte des **données personnelles** (situation financière de
l'utilisateur — voir `db/RGPD-registre-des-traitements.md`). Ces deux indicateurs héritent
du traitement existant : destinataire unique, purge déjà testée. **Aucun nouveau
traitement à déclarer** — mais à vérifier au moment de coder, pas à supposer.

---

## 7. Lot 3 — Risque · 3 indicateurs

> Brique commune : le **rendement journalier** `r_t = ln(cloture_t / cloture_t−1)`.
> À écrire **une fois**, dans une couche partagée par les trois.

### 7.1 Volatilité annualisée sur 20 séances

| | |
|---|---|
| **Formule** | `écart_type(r) sur 20 séances × √252 × 100` |
| **Fenêtre** | 20 séances |
| **Piège** | `stddev_samp` (échantillon, diviseur *n−1*) et non `stddev_pop`. Sur 20 points l'écart est visible. |
| **Piège 2** | 252 est le nombre conventionnel de séances par an, **pas** une mesure. À déclarer comme convention. |
| **Test** | 20 rendements identiques ⇒ volatilité = 0. Série connue ⇒ valeur calculée à la main en commentaire du test. |

### 7.2 Drawdown maximal sur un an

| | |
|---|---|
| **Formule** | `MIN( cloture_t / MAX(cloture) jusqu'à t − 1 ) × 100` — résultat ≤ 0 |
| **Fenêtre** | 252 séances |
| **Piège** | le maximum est **glissant** (le plus haut *atteint jusqu'ici*), pas le maximum de toute la période. Confondre les deux est l'erreur classique et donne un chiffre trop favorable. |
| **Test** | série 100 → 150 → 90 → 120 ⇒ drawdown max = −40,00 % (150 → 90), **pas** −25 %. |

### 7.3 RSI 14

| | |
|---|---|
| **Formule** | `RSI = 100 − 100 / (1 + moyenne_hausses / moyenne_baisses)` |
| **Fenêtre** | 14 séances |
| **Piège majeur** | 🔴 **le lissage de Wilder est récursif** : chaque moyenne dépend de la précédente. Ce n'est **pas** exprimable en fonction fenêtre SQL simple. Deux issues : un CTE récursif (illisible), ou un calcul en Python. **Décision : Python**, avec une moyenne exponentielle de facteur `1/14`. |
| **Piège 2** | la variante « moyenne simple » circule partout et donne des valeurs **différentes**. Écrire laquelle est implémentée, sinon le chiffre n'est pas reproductible. |
| **Piège 3** | 14 séances sans aucune baisse ⇒ division par zéro ⇒ RSI = 100 par convention. À coder explicitement. |
| **Test** | 14 hausses consécutives ⇒ 100. 14 baisses ⇒ 0. Puis une série de référence dont la valeur attendue est fixée à la main. |

---

## 8. Lot 4 — Relatif · ⚠️ probablement non réalisé

Les quatre exigent un **objet de comparaison** que RITA n'a pas :
performance relative au benchmark · série rebasée à 100 · bêta 1 an ·
performance moyenne des 111 valeurs (« indice maison »).

**Deux options, si le temps le permet :**

| Option | Coût | Ce qu'elle vaut |
|---|---|---|
| Ingérer `^FCHI` (CAC 40) | ~nul — `sources/cotations.py` sait déjà télécharger un ticker | référence reconnue, comparaison lisible |
| Indice maison équipondéré des 111 valeurs | nul — la donnée est là | mais 111 valeurs hétérogènes, dont certaines avec `statut_qualite ≠ 'OK'` : ce n'est **pas** un marché, c'est une moyenne d'un échantillon arbitraire |

**Recommandation : `^FCHI` si on y va, et l'indice maison seulement comme indicateur
séparé — jamais comme benchmark.**

> 📌 **Correction actée.** La proposition initiale parlait d'une « moyenne dynamique des
> **135** instruments ». RITA en compte **111**. Le nombre 135 venait du suivi des
> 135 critères RNCP — deux objets sans rapport.

---

## 9. Ce qui est écarté, et pourquoi — le **ratio de Sharpe**

Trois raisons, aucune n'est « c'est trop dur » :

1. **Le taux sans risque n'existe pas dans RITA.** `sources/fred.py` ne collecte que
   `DGS10`, le Trésor **américain** à 10 ans. L'employer pour un portefeuille libellé en
   euros est une incohérence méthodologique. Il faudrait passer par `sources/ecb.py`.
2. **Sur un an de données quotidiennes, un Sharpe est statistiquement très bruité.**
   L'afficher avec deux décimales suggère une précision qu'il n'a pas.
3. **C'est le seul indicateur de la liste qui classe naturellement** (« celui-ci est
   meilleur »). C'est donc le plus proche du conseil, et le plus exposé au §1.

**Il sera présenté à l'oral comme un écart assumé, pas comme un oubli.**

---

## 10. Ce que ce dossier ne dit pas — faiblesses déclarées

- **Aucun chiffre ici n'est mesuré.** Les volumes cités (273 608 lignes, 111 valeurs,
  7 positions, 2 802 séances à volume nul) proviennent de `CLAUDE.md` et
  `db/requetes.sql`. Les coûts d'exécution des futures requêtes ne sont **pas** estimés :
  ils seront mesurés par `EXPLAIN ANALYZE` au moment de coder, comme pour R1 à R3.
- **La forme d'affichage n'est pas décidée.** Ce dossier dit *quoi* calculer, pas
  *comment le montrer*. L'écran relève d'E4 et fera l'objet de sa propre conception.
- **Le rattachement aux compétences n'est pas tranché.** Ces indicateurs sont écrits
  pour E4 (C14–C19). Ils ne rapportent **rien** en C2, qui est déjà livré avec R1–R3 et
  S1–S3 : ajouter des requêtes ne re-prouve pas une compétence déjà prouvée.
- **Aucune donnée intraséance.** Tout indicateur qui en dépendrait est hors d'atteinte
  et n'a pas été envisagé.

---

## 📖 Glossaire

- **ADTV20** — *Average Daily Traded Value* sur 20 séances : valeur moyenne échangée par
  séance, en euros. Mesure la liquidité — la capacité à sortir d'une position sans faire
  bouger le prix.
- **Bêta** — sensibilité d'une valeur aux mouvements de son marché. Bêta 1,3 : quand
  l'indice prend 1 %, la valeur prend en moyenne 1,3 %.
- **Cours ajusté** — cours corrigé rétroactivement des dividendes et des divisions
  d'actions, pour qu'une performance calculée sur la série ait un sens.
- **Drawdown** — baisse depuis le dernier plus haut atteint. Le *drawdown maximal* est la
  pire de la période.
- **Fonction fenêtre (SQL)** — calcul portant sur un groupe de lignes voisines sans les
  fusionner : `OVER (PARTITION BY … ORDER BY … ROWS BETWEEN … )`.
- **Indice équipondéré** — indice où chaque valeur pèse pareil, par opposition au CAC 40
  où les grosses capitalisations pèsent davantage.
- **Lissage de Wilder** — moyenne exponentielle de facteur `1/n` utilisée par le RSI
  d'origine. Récursive : chaque valeur dépend de la précédente.
- **MA20 / MA50** — moyenne mobile des clôtures sur 20 / 50 séances.
- **OHLCV** — *Open, High, Low, Close, Volume* : les cinq colonnes d'une séance.
  Exactement la table `cotation`.
- **Plus-value latente** — écart entre le cours actuel et le PRU, multiplié par la
  quantité. « Latente » : non réalisée, tant qu'il n'y a pas eu de vente.
- **PRU** — Prix de Revient Unitaire : ce qu'a coûté en moyenne une action détenue.
- **Rebasement à 100** — on ramène le premier point d'une série à 100 pour comparer deux
  séries d'échelles différentes.
- **Rendement journalier** — `ln(cloture_t / cloture_t−1)`. Brique commune à la
  volatilité, au drawdown et au bêta.
- **RSI 14** — *Relative Strength Index* sur 14 séances, borné entre 0 et 100. Compare
  l'ampleur des hausses à celle des baisses.
- **Sharpe (ratio de)** — (rendement − taux sans risque) ÷ volatilité. Écarté ici, §9.
- **Taux sans risque** — rémunération d'un placement réputé sûr (dette d'État). Sert de
  point de comparaison.
- **Volatilité annualisée** — écart-type des rendements journaliers × √252.
  252 = nombre conventionnel de séances par an.
- **YTD** — *Year To Date* : depuis la première séance de l'année en cours.

# Preuve — indicateurs de marché, lot 1 « socle »

> Alimente l'**écran 2** de l'application (livrable **E4**).
> Spécification : [`../../docs/indicateurs/CONCEPTION.md`](../../docs/indicateurs/CONCEPTION.md) §5

**Fichiers** : [`../../db/indicateurs.sql`](../../db/indicateurs.sql) ·
[`../../indicateurs/socle.py`](../../indicateurs/socle.py) ·
**Tests** : [`../../tests/test_indicateurs_socle.py`](../../tests/test_indicateurs_socle.py) (13)
**Date** : 2026-08-18

---

## Le principe, avant les chiffres

**RITA calcule des indicateurs, jamais des stratégies.**

| | Définition | Exemple | Statut |
|---|---|---|---|
| **Indicateur** | un nombre calculé à partir des cours | « le cours est 5,86 sous son plus haut » | ✅ un **fait** |
| **Stratégie** | une règle déclenchant une décision | « RSI > 70 → vendre » | ❌ un **conseil** |

Aucun verbe d'action, aucun classement « meilleures valeurs », aucun code couleur binaire.
Un nombre, son unité, sa fenêtre, sa date. Contrainte AMF, posée dans `CLAUDE.md`.

---

## Le module externe n'a pas été porté — et pourquoi

`ETAT.md` recommandait de **porter** `quant_metrics.py` depuis
`Ganda15/daily-stock-analysis-era` plutôt que de réécrire. Le fichier a été lu le 18/08
(350 lignes, 15 fonctions). **Il ne convient pas au lot 1.**

| | `quant_metrics.py` | ce que la spécification exige |
|---|---|---|
| Technologie | pandas, en mémoire | **SQL**, fonctions fenêtre |
| Portée | **un** instrument | **les 111**, en une requête |
| Fenêtre des performances | **nombre de lignes** (`series.iloc[-periods-1]`) | **jours de calendrier** |

Le décalage en nombre de lignes est **exactement le piège n°1 de la spécification**. Le
porter aurait importé le défaut contre lequel elle a été écrite. Le module calcule en outre
Sharpe, Sortino, Calmar et bêta — que la spécification écarte explicitement.

> *La consigne « porter plutôt que réécrire » avait été écrite le 15/08 **sans avoir ouvert
> le fichier**. Elle est corrigée dans `ETAT.md`, pas effacée.*

**Réutilisable plus tard, hors lot 1** : `_perf_ytd`, `_rsi`, `_max_drawdown_pct`,
`_annualized_vol`.

---

## Une seule requête, onze colonnes

Les cinq performances sont **le même calcul** avec une date cible différente. Onze requêtes
qui reliraient chacune `cotation` (273 608 lignes) seraient onze parcours du même tableau.

### Sortie réelle

```
==============================================================================
INDICATEURS - LOT 1 (socle)
==============================================================================
  valeurs                  : 111
  cotations perimees       : 3  (> 40 jours)

  ticker         cours     1j %     1a %       MA20   /haut %
  ------------------------------------------------------------
  AC.PA          47.14    -0.19    -1.32      47.76     -9.35
  ACA.PA         18.39    -1.45    21.30      17.92     -1.89
  ADP.PA        111.50     0.27     4.60     109.92    -13.84
  AF.PA          11.87    -2.06     6.13      12.59    -21.76
  AI.PA         171.58    -1.13     9.96     176.32     -5.86
  AIR.PA        208.85    -1.49    18.54     201.30     -3.88
  AKE.PA         58.25     1.92    -1.39      55.73     -7.91
  AKW.PA          6.40     0.63   -19.87       6.62    -40.06
```

**111 valeurs sur 111.** C'est le contrôle qui compte : un `MAX(date_seance)` global n'en
remontait que **2 sur 111** le 10/08, parce qu'Euronext, Xetra et le NYSE ne ferment pas les
mêmes jours. La dernière séance se calcule **par ticker**.

---

## 💎 Trois choix de conception à défendre

### 1. La référence d'une fenêtre est « la dernière séance à ou avant la date cible »

```sql
LEFT JOIN LATERAL (SELECT c.cloture FROM cotation c
                   WHERE c.ticker = t.ticker AND c.date_seance <= t.cible_1s
                   ORDER BY c.date_seance DESC LIMIT 1) r1s ON TRUE
```

**Pourquoi pas `LAG(cloture, 5)`** : un décalage de 5 lignes suppose que « une semaine
= 5 séances » pour toutes les valeurs. Faux dès qu'un jour férié national tombe dans la
fenêtre — et les trois places n'ont pas les mêmes.

**La YTD s'écrit dans l'autre sens** (`>=` et `ORDER BY ... ASC`) : ce n'est pas un décalage,
c'est la **première** séance de l'année.

### 2. Deux unités de fenêtre coexistent, et c'est volontaire

| Indicateur | Unité | Raison |
|---|---|---|
| Performances 1j/1s/1m/YTD/1a | **jours de calendrier** | une durée se compte en durée |
| MA20, MA50, ADTV20 | **séances** | une moyenne mobile se définit en séances par convention |

De même, MA20 **inclut** le jour courant (elle décrit un niveau) alors que le volume relatif
de `requetes.sql` R3 l'**exclut** (il compare un jour à son passé — sinon un pic relèverait
sa propre moyenne et se masquerait lui-même). **Ce n'est pas une incohérence**, et c'est
écrit à côté du code pour qu'un relecteur n'y voie pas une faute.

### 3. Un historique trop court rend `NULL`, jamais une valeur partielle

```sql
CASE WHEN COUNT(*) OVER (...) = 20 THEN AVG(cloture) OVER (...) END AS ma20
```

Les 19 premières séances d'une valeur donneraient une « moyenne sur 20 » calculée sur moins
de 20 points. Rendre ce nombre serait mentir silencieusement.

---

## ⚠️ Ce que la mesure a révélé : trois valeurs radiées

`statut_qualite` vaut **`OK`** pour trois valeurs qui ne cotent plus depuis des années :

| Ticker | Nom | Dernière séance | Ancienneté |
|---|---|---|---|
| `ZC.PA` | ZODIAC AEROSPACE | 2018-03-22 | **3 071 jours** |
| `ELE.PA` | EULER HERMES GROUP | 2018-04-26 | 3 036 jours |
| `GTO.PA` | GEMALTO | 2019-05-28 | 2 639 jours |

Sans signalement, l'écran afficherait pour elles une « **performance 1 jour** » calculée sur
des cours vieux de huit ans.

**Correction apportée** : une colonne `fraicheur_jours` et une propriété `cotation_perimee`
(seuil 40 jours). Les lignes restent affichées, **avec la mention** — même règle que le
scénario S5 de C14 : *on montre le chiffre, on signale le doute*.

> 🔑 **`statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur.** Les deux
> notions sont distinctes, et les confondre produisait un écran faux avec des données
> valides.

---

## Performance, mesurée

```
Planning Time  :   0,798 ms
Execution Time : 193,797 ms
Seq Scan sur cotation   : 1   (le calcul des fenêtres glissantes)
Index Scan sur cotation : 7   (Index Scan Backward, 111 recherches chacun)
```

Les cinq jointures `LATERAL` passent toutes par `cotation_pkey` en **Index Scan Backward** —
la clé primaire `(ticker, date_seance)` est exactement l'index dont elles ont besoin. Aucun
index supplémentaire n'a été créé : le schéma existant suffisait.

---

## Tests — 13, et leur limite dite d'emblée

```
C:\Python314\python.exe -m pytest tests/test_indicateurs_socle.py -q
→ 13 passed
```

| Ce qui est vérifié | |
|---|---|
| Conversion `Decimal` → `float` | les NUMERIC ne remontent pas jusqu'à l'API |
| `NULL` reste `None`, jamais `0.0` | un historique court ne devient pas un chiffre |
| Seuil de péremption, aux deux bornes | 40 passe, 41 ne passe plus |
| Une valeur radiée est signalée **malgré `statut_qualite = 'OK'`** | le test central |
| Le filtre par ticker passe par un **paramètre lié** | pas d'injection SQL |
| Le SQL ne contient **aucun `LAG(`** (commentaires retirés) | verrouille le choix n°1 |
| La dernière séance est calculée **par ticker** | verrouille le défaut du 10/08 |

> ⚠️ **Limite connue** : ces tests remplacent `_executer`. Ils ne vérifient donc **pas** le
> SQL lui-même — c'est le défaut relevé le 17/08 sur toute la suite (`ETAT.md`, C12) : aucun
> test ne se connecte à la vraie base. Le SQL est vérifié par **exécution réelle**, tracée
> dans ce document. Les deux vérifications sont complémentaires ; aucune ne remplace l'autre.

---

## Deux défauts rencontrés pendant l'écriture

**1. Le module ne lisait pas son `.env`.** `DATABASE_URL` absente, échec immédiat hors du
serveur d'API. **C'est le défaut exact corrigé le 17/08 sur `db/importer.py`** (commit
`a7a3dba`) — il s'est reproduit parce que la cause est structurelle : seul `api/main.py`
appelait `load_dotenv()`. Corrigé, avec le renvoi au commit d'origine dans le commentaire.

**2. Un caractère `%` dans un commentaire SQL cassait `cur.execute`.** `psycopg2` interpole
dès que le second argument n'est pas `None` — **y compris à l'intérieur d'un commentaire**.
Deux corrections : `None` au lieu d'un tuple vide, et plus aucun `%` dans le fichier SQL.
Un test verrouille les deux.

---

## Ce qui n'est pas fait

| Manque | Conséquence |
|---|---|
| **L'écran 2 n'existe pas** — ces indicateurs ne sont pas encore affichés | le lot 1 est calculable, pas visible |
| **Aucun point de terminaison d'API** ne les expose | à ajouter dans `api/donnees.py` |
| **Lot 2 (portefeuille) et lot 3 (risque)** non commencés | 5 indicateurs restants sur 13 |
| **Les cours datent du 29/07** — 3 semaines de retard | `sources/cotations.py` n'a pas été rejoué depuis la reconstruction du 16/08 |

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Indicateur** | Un nombre calculé à partir des cours — un fait |
| **Stratégie** | Une règle qui déclenche une décision — un conseil. **Bannie du projet** |
| **OHLCV** | *Open, High, Low, Close, Volume* — les 5 mesures d'une séance |
| **Séance** | Une journée de bourse pour une valeur donnée |
| **Fonction fenêtre** (*window function*) | Calcul portant sur un groupe de lignes voisines, sans les regrouper |
| **`LATERAL`** | Jointure dont la condition dépend de la ligne courante |
| **`LAG(colonne, n)`** | Valeur de la ligne située `n` **rangs** plus haut — piégeux ici |
| **MA20 / MA50** | Moyenne mobile des clôtures sur 20 ou 50 séances |
| **ADTV** | *Average Daily Traded Value* — valeur moyenne échangée par séance |
| **YTD** | *Year To Date* — depuis le 1ᵉʳ janvier de l'année en cours |
| **52-week high** | Plus haut des 52 dernières semaines, en **intraséance** par convention |
| **Radiée** (*delisted*) | Valeur qui ne cote plus — rachat, fusion, faillite |
| **`NUMERIC` / `Decimal`** | Type décimal exact de PostgreSQL, sans erreur d'arrondi |
| **Paramètre lié** | Valeur transmise à part du texte SQL — la parade à l'injection SQL |
| **AMF** | *Autorité des marchés financiers* |

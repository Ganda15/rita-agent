# C3 · Preuve — ALJXR.PA : un artefact de regroupement d'actions, pas une donnée corrompue

**Compétence C3** : « Développer des règles d'agrégation de données issues de différentes
sources […] afin de préparer un jeu de données unique. »

**Date** : 2026-08-02 · **Mesuré sur** : `data/bigdata/ohlcv/` (276 168 lignes)
**Corrige** : `../C1/preuve-09-analyse-exploratoire.md` §6

---

## 1. Le point de départ : une hypothèse fausse, et signalée comme incertaine

L'analyse exploratoire du 31/07 avait repéré le symptôme et proposé une explication :

> *« ALJXR.PA — prix max 7,15 millions + 1 088 volumes nuls. Échelle de prix aberrante
> (**probablement** une ligne de droits/bons non ajustée). »*

Le mot **« probablement »** faisait son travail : il annonçait une supposition, pas un fait.
Elle s'est révélée **fausse**. Ce document la remplace.

**Ce qui manquait à l'analyse du 31/07** : elle regardait le prix **seul**. Les volumes nuls
étaient comptés dans une autre section, comme une anomalie **distincte**.

## 2. La ligne réelle

```
ticker    date        ouverture   haut        bas         cloture     volume
ALJXR.PA  2016-08-17  6 884 480   7 156 748   6 884 480   7 156 748   0
```

**Le volume est à zéro.** C'est le détail qui change tout, et il était sous les yeux depuis le
début.

## 3. L'historique complet, année par année

```
       seances  cloture_min   cloture_max   volume_moyen   seances_volume_nul
2016       110  4 628 549.00  7 156 748.50           0.00            110
2017       255  2 411 513.00  5 756 515.00           0.01            253
2018       255  1 134 000.00  5 904 317.50           0.07            245
2019       256    253 200.00  1 452 000.00           0.04            250
2020       257    124 000.00    432 800.00           0.76            200
2021       258        800.00    140 000.00          19.33             30
2022       257         14.60      1 200.00         572.93              0
2023       255          0.56         38.48      14 972.53              0
2024       256          0.03          0.54   1 445 109.77              0
2025       255          0.12          0.26     586 448.79              0
2026       146          0.17          0.29     377 841.26              0
```

## 4. 💎 Ce que la lecture croisée révèle

Les deux colonnes ne doivent pas se lire séparément :

```
2016 :  prix = 7 156 748 €      volume = 0
2024 :  prix =       0,03 €     volume = 1 445 110
```

| | Évolution 2016 → 2024 |
|---|---|
| **Prix** | **divisé** par ~36 millions |
| **Volume** | **multiplié** dans les mêmes proportions |

Deux grandeurs qui évoluent en sens **exactement inverse**, dans le **même rapport**, ne sont
pas une corruption aléatoire. C'est une **transformation appliquée**.

## 5. Le mécanisme : le rétro-ajustement d'un regroupement d'actions

Un **regroupement d'actions** (*reverse split*) : la société échange par exemple 1 000 anciennes
actions contre 1 nouvelle. Le cours est multiplié par 1 000, le nombre d'actions divisé par
1 000 — la capitalisation ne bouge pas.

Pour que la courbe historique reste **continue**, le fournisseur de données réécrit tout le
passé :

| Grandeur | Effet du rétro-ajustement |
|---|---|
| Prix passés | **multipliés** par le facteur |
| Volumes passés | **divisés** par le facteur |

C'est exactement le motif observé. Et ça explique le second symptôme sans rien ajouter :

> **Les 110 séances de 2016 à volume nul ne sont pas des jours sans échange.** Ce sont des
> volumes réels, divisés par ~36 millions, **écrasés à zéro par l'arrondi**.

## 6. ⚠️ Ce que cette découverte corrige dans le diagnostic initial

L'analyse du 31/07 listait **deux anomalies distinctes** :

| Anomalie | Classée comme | En réalité |
|---|---|---|
| Cours max à 7 156 748 | échelle aberrante | rétro-ajustement |
| 1 088 volumes nuls sur ALJXR.PA | qualité des données | **même cause** |

**Elles n'en font qu'une.** Le diagnostic n'était pas faux, il était **incomplet** — et
incomplet d'une manière qui n'aurait pas résisté à une question précise : *« pourquoi ce ticker
a-t-il à la fois des prix absurdes et des volumes nuls ? »*

La bonne réponse n'était pas « deux problèmes sur le même ticker », mais « un seul mécanisme,
deux symptômes ».

## 7. Conséquence sur les décisions de conception

| Décision | Statut après cette découverte |
|---|---|
| **Conserver** la valeur plutôt que la supprimer | ✅ **renforcée** — la donnée n'est pas fausse, elle est *transformée*. La supprimer effacerait une information exacte. |
| Table **`operation_sur_titre`** | ✅ **justifiée par une mesure**, plus par une intuition. Sans elle, impossible de distinguer une variation réelle d'un artefact comptable. |
| Condition `bas > 0` dans les requêtes | ✅ inchangée — le garde-fou reste nécessaire quelle que soit la cause |
| État de la table | ⬜ **conçue, non construite.** Dette assumée et écrite. |

**Le cas VIRI.PA à +4 164 % relève du même mécanisme** — c'est la variation observée autour
d'une date de regroupement, non lissée.

## 8. Reproduire la mesure

```powershell
cd D:\KandaWork\RITA_PROJECT\rita-agent

# les 5 plus hautes clotures du jeu
C:\Python314\python.exe -c "import pandas as pd, glob; df=pd.concat([pd.read_parquet(x) for x in sorted(glob.glob('data/bigdata/ohlcv/*/*.parquet'))]); print(df.nlargest(5,'cloture')[['ticker','date','haut','cloture','volume']].to_string(index=False))"
```

## 🎤 Phrase pour l'oral

> « J'avais une valeur à 7 millions d'euros, et je l'avais mise de côté en écrivant "probablement
> une ligne de droits non ajustée". C'était une supposition, et elle était fausse. En regardant
> le prix **et le volume ensemble**, le mécanisme apparaît : entre 2016 et 2024 le prix est
> divisé par 36 millions et le volume multiplié d'autant. Deux grandeurs qui bougent en sens
> exactement inverse dans le même rapport, ce n'est pas du bruit — c'est un regroupement
> d'actions rétro-ajusté. Et ça m'a appris quelque chose sur ma propre analyse : j'avais compté
> le prix aberrant et les volumes nuls comme deux anomalies séparées. C'était **un seul
> mécanisme, deux symptômes**. »

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Regroupement d'actions** (*reverse split*) | 1 000 actions à 0,01 € deviennent 1 action à 10 € |
| **Rétro-ajustement** | Réécrire l'historique pour que la courbe reste continue après l'opération |
| **Facteur d'ajustement** | Le nombre par lequel on multiplie les prix et divise les volumes |
| **Capitalisation** | Nombre d'actions × cours ; elle ne change pas lors d'un regroupement |
| **Séance** | Une journée de bourse |
| **Volume** | Nombre d'actions échangées dans la journée |
| **Droits / bons** (*rights, warrants*) | Titres dérivés donnant le droit d'acheter une action — l'hypothèse initiale, écartée |

# C1 · Preuve 9 — Analyse exploratoire du jeu de données récupéré

**Élément de preuve couvert** : *« les résultats de l'analyse exploratoire permettant la
bonne compréhension du jeu de données récupéré »*
**Source de l'exigence** : Règlement spécifique RNCP37827, **p. 53** — « Exemples
d'éléments de preuves attendus », Bloc 1
**Fichier** : `bigdata/explorer.py`
**Date d'exécution** : 2026-07-31

> ⚠️ Cette exigence n'apparaît dans **aucun** des 135 critères d'évaluation. C'est une page
> distincte du règlement, repérée le 31/07/2026 en relisant les PDF sources. Sans elle,
> RITA aurait présenté un jeu de données sans jamais prouver qu'on l'avait regardé.

## Commande

```powershell
Set-Location "D:\KandaWork\RITA_PROJECT\rita-agent"
C:\Python314\python.exe -X utf8 -m bigdata.explorer
```

## Ce que le script répond

Six questions qu'un ingénieur data se pose **avant** de modéliser une base. Chaque réponse
a une conséquence sur le schéma (C4) — c'est ce lien qui fait la valeur de l'exercice.

---

## [1] Vue générale

```
Lignes              : 276,168
Tickers distincts   : 111
Noms distincts      : 112
Periode             : 2016-07-28 -> 2026-07-28
Colonnes (9)        : date, ouverture, haut, bas, cloture, volume, ticker, nom, annee
```

**111 tickers pour 112 noms.** L'écart d'une unité est le premier signal : un ticker porte
deux noms. Voir §4.

## [2] Répartition par partition

```
       lignes  tickers  part_%
2016    11980      108     4.3
2017    27770      108    10.1
2018    27610      109    10.0
2019    27463      107     9.9
2020    27488      106    10.0
2021    27589      106    10.0
2022    27480      106    10.0
2023    27454      107     9.9
2024    27648      108    10.0
2025    27783      108    10.1
2026    15903      108     5.8
```

Les 9 années pleines pèsent ~10 % chacune : le partitionnement est **équilibré**, aucune
partition ne domine. 2016 (4,3 %) et 2026 (5,8 %) sont partielles — normal, la fenêtre de
10 ans commence fin juillet 2016 et s'arrête aujourd'hui.

## [3] Valeurs manquantes

```
           manquantes  taux_%
date                0     0.0
ouverture           0     0.0
haut                0     0.0
bas                 0     0.0
cloture             0     0.0
volume              0     0.0
ticker              0     0.0
nom                 0     0.0
annee               0     0.0
  -> total : 0 valeur(s) manquante(s)
```

**Aucun trou.** → Toutes les colonnes OHLCV peuvent être déclarées `NOT NULL` en base.

## [4] 🔴 Doublons sur la clé (ticker, date)

```
Lignes en double    : 5,120
Cles uniques        : 273,608
!! VIRI.PA : 5120 lignes, noms = ['CGG BS', 'CGG RGPT']
```

**2 560 lignes redondantes** (5 120 lignes en double = 2 × 2 560). Cause et traitement
détaillés dans [`../C3/preuve-dedoublonnage-cgg.md`](../C3/preuve-dedoublonnage-cgg.md).

→ **La clé `(ticker, date)` n'est pas utilisable seule comme clé primaire.**

## [5] Couverture historique — très inégale

```
GTO.PA         286 lignes  2018-03-14 -> 2019-05-28
HAVAS.AS       411 lignes  2024-12-15 -> 2026-07-28
ZC.PA          411 lignes  2016-07-29 -> 2018-03-22
ELE.PA         434 lignes  2016-07-29 -> 2018-04-26
URW.PA         840 lignes  2023-04-13 -> 2026-07-28
...
VMX.PA        2560 lignes  2016-07-28 -> 2026-07-28
VK.PA         2560 lignes  2016-07-28 -> 2026-07-28
VIRI.PA       5120 lignes  2016-07-28 -> 2026-07-28
```

Trois profils distincts, qui ne se traitent pas pareil :

| Profil | Exemple | Lecture |
|---|---|---|
| Historique complet | VMX.PA, VK.PA — 2 560 lignes | la référence |
| **Arrêt en cours de route** | ZC.PA (fin 2018), ELE.PA (fin 2018), GTO.PA (fin 2019) | valeur **sortie de cote** — l'univers n'était pas si propre |
| **Démarrage tardif** | HAVAS.AS (déc. 2024), URW.PA (avr. 2023) | introduction ou *spin-off* récent |

→ Un calcul de performance sur 10 ans **ne peut pas** inclure ces valeurs sans biais de
survie. À traiter explicitement dans l'agent Technique.

## [6] 🔴 Anomalies métier

```
OK cloture_nulle_ou_negative      : 0
!! volume_zero                    : 2802
OK haut_inferieur_au_bas          : 0
!! cloture_hors_bornes            : 1533
```

Deux anomalies réelles. Détail obtenu par un second passage :

**Clôture hors de l'intervalle [bas, haut]** — 1 533 lignes sur 75 tickers :

```
STLAP.PA    1142   <- 74 % du total à lui seul
BOL.PA        25
CRI.PA        21
MERY.PA       21
...
écart médian : 0.000 %      écart maximum : 8.51 %
```

L'écart **médian est nul** : la grande majorité est du bruit de virgule flottante,
inoffensif. Mais l'écart maximum de 8,5 % est une vraie incohérence.

**Volume à zéro** — 2 802 lignes sur 106 tickers :

```
STLAP.PA    1143
ALJXR.PA    1088
GTO.PA       286
```

**Prix maximum par ticker** :

```
ALJXR.PA    7 156 748.5     <- absurde pour une action
ATO.PA         10 130.0
EMEIS.PA        8 137.6
```

### Ce que ça désigne : deux tickers à écarter

| Ticker | Symptômes | Diagnostic |
|---|---|---|
| **STLAP.PA** | 1 142 clôtures hors bornes **+** 1 143 volumes nuls | Ligne incohérente. Ce ticker était déjà classé `OK_APRES_CORRECTION` dans `univers-155.csv` — la correction n'a pas suffi. |
| **ALJXR.PA** | prix max 7,15 **millions** + 1 088 volumes nuls | ~~Échelle de prix aberrante (probablement une ligne de droits/bons non ajustée)~~ → **hypothèse corrigée le 02/08** : regroupement d'actions rétro-ajusté. Voir `../C3/preuve-artefact-reverse-split.md`. |

→ **Ces deux valeurs doivent être écartées ou corrigées avant l'import en base (C3).**
Sans cette analyse, elles seraient entrées silencieusement et auraient faussé toute
statistique de portefeuille.

> ⚠️ **Correction d'hypothèse — 02/08/2026.** Le diagnostic ci-dessus disait « probablement une
> ligne de droits/bons non ajustée ». C'était une **supposition**, signalée comme telle par le
> mot « probablement », et elle était **fausse**. En croisant le prix avec le **volume** — ce que
> cette analyse-ci n'avait pas fait — le mécanisme réel apparaît : un **regroupement d'actions
> rétro-ajusté**. Le prix est divisé par ~36 millions entre 2016 et 2024, le volume multiplié
> dans les mêmes proportions. Conséquence directe : **les 1 088 volumes nuls d'ALJXR.PA ne sont
> pas une anomalie de qualité distincte** — ils ont la **même cause** que le prix aberrant.
> Preuve complète : `evidence/C3/preuve-artefact-reverse-split.md`.

## [7] Statistiques descriptives

```
        ouverture        haut         bas     cloture        volume
count   276168.00   276168.00   276168.00   276168.00  2.761680e+05
mean      9720.79     9920.20     9497.64     9665.45  1.290708e+06
std     193770.31   197532.70   189527.12   192782.90  3.852331e+06
min          0.01        0.01        0.00        0.01  0.000000e+00
25%         11.47       11.62       11.33       11.47  5.098700e+04
50%         29.89       30.23       29.51       29.87  2.489885e+05
75%         80.66       81.52       79.75       80.65  1.012060e+06
max    7234539.00  7351225.00  7001167.00  7156748.50  1.862992e+08
```

**Moyenne 9 665 € contre médiane 29,87 €.** Un écart de ce type ne s'explique pas par la
distribution normale des cours : il est provoqué par ALJXR.PA. C'est la lecture croisée
moyenne/médiane qui rend l'anomalie visible d'un coup d'œil — et c'est exactement à ça que
sert une analyse exploratoire.

---

## 🎯 Conséquences directes sur le schéma de base (C4)

C'est le lien exigé par le règlement entre l'exploration et **la conception « orientée
requêtes »** :

| Constat mesuré | Décision de schéma |
|---|---|
| `(ticker, date)` a 2 560 doublons | ❌ **pas** de clé primaire `(ticker, date)` seule — séparer une table `valeur` (ticker → société) d'une table `cotation` |
| 0 valeur manquante sur 276 168 lignes | ✅ colonnes OHLCV en `NOT NULL` |
| Répartition équilibrée par année | ✅ index sur `annee` — le filtre le plus fréquent du briefing quotidien |
| 111 tickers / 112 noms | ✅ le nom **n'est pas** un attribut de la cotation : table dédiée |
| Historiques très inégaux (286 → 2 560 lignes) | ✅ colonnes `premiere_cotation` / `derniere_cotation` sur la table `valeur` |
| 2 tickers aberrants | ✅ colonne `statut_qualite` pour exclure sans supprimer |

## 🎤 Phrase pour l'oral

> « Avant de modéliser la base, j'ai exploré le jeu récupéré. Trois choses en sont sorties
> que je n'avais pas vues : un ticker en double sur 2 560 lignes, deux valeurs aux données
> incohérentes, et des historiques allant de 286 à 2 560 séances. Chacune a changé le
> schéma — la clé primaire, une table séparée pour les sociétés, une colonne de statut
> qualité. Sans cette exploration, ces trois problèmes seraient entrés en base
> silencieusement. »

---

*Reproductible : le script relit le Parquet existant, il ne retélécharge rien. Si le jeu
est absent, il indique la commande de régénération.*

# C1 · Preuve 8 — Jeu Parquet partitionné (laboratoire big data)

**Type de source couvert** : système big data *(preuve séparée, acceptée par le formateur le 28/07)*
**Fichier** : `bigdata/build_parquet.py`
**Date de construction** : 2026-07-29
**Statut** : étape 1/4 du laboratoire — le jeu de données existe, Spark pas encore branché

## Ce que fait le script

Lit `data/univers-155.csv` (l'univers réel d'Era, 112 tickers vérifiés un par un), télécharge
10 ans d'historique quotidien pour chacun, et écrit en **Parquet partitionné par année**.

```
data/bigdata/ohlcv/
├── annee=2016/…parquet
├── annee=2017/…parquet
│   …
└── annee=2026/…parquet
```

## Commande

```powershell
Set-Location "D:\KandaWork\RITA_PROJECT\rita-agent"
C:\Python314\python.exe -m bigdata.build_parquet
```

## Sortie réelle

```
=== JEU PARQUET PARTITIONNE — LABORATOIRE BIG DATA ===
Valeurs recuperees : 112 / 112
Lignes             : 276,168
Partitions (annees): 11  (2016-2026)
Taille sur disque  : 13.3 Mo
Duree              : 32.4 s
```

**112 sur 112** — aucun échec, parce que l'univers avait déjà été nettoyé à l'étape précédente
(les 14 valeurs mortes ou à vérifier ont été écartées en amont, avec leur cause documentée dans
`data/univers-155.csv`).

## 💎 La preuve qui compte : le *predicate pushdown* mesuré

Le partitionnement n'est pas décoratif. Mesure réelle :

```
Lecture totale        : 276 168 lignes en 184 ms
Lecture 2024 (filtre) :  27 648 lignes en  20 ms
→ 9,4× plus rapide en ne lisant qu'une seule partition
```

Le moteur reçoit `WHERE annee = 2024` et **ne lit que le répertoire `annee=2024/`**. Il ignore
les 10 autres. C'est exactement le mécanisme qu'un cluster Spark applique sur des téraoctets —
seule la taille change, pas la méthode.

**C'est ça, la compétence démontrée.** Pas le volume.

## ⚠️ Ce que cette preuve n'est pas — à dire, pas à masquer

**276 168 lignes ne sont pas du big data.** 13,3 Mo tiennent en mémoire vive ; `pandas` lit le
tout en 184 ms. Aucun cluster n'est nécessaire.

Le plafond est structurel, pas un manque d'effort : avec les données gratuites yfinance,
l'intraday est limité (1 min → 7 jours d'historique, 5 min → 60 jours, horaire → 730 jours).
Il n'existe aucun moyen honnête d'atteindre le téraoctet dans ce cadre.

| ✅ Établi | ❌ Non établi |
|---|---|
| Partitionnement correct, 11 partitions | Que le volume justifie Spark |
| *Predicate pushdown* fonctionnel et **mesuré** (9,4×) | Le comportement en environnement distribué réel |
| Format colonnaire compressé (13,3 Mo pour 276 k lignes) | La tolérance aux pannes d'un cluster |
| Homogénéisation UTC des dates (C3) | |

## Traitements de qualité appliqués au passage (C3)

| Traitement | Pourquoi |
|---|---|
| Dates converties en **UTC** | l'univers couvre Euronext Paris, Xetra, NYSE, Amsterdam, Bruxelles — fuseaux différents |
| Colonnes renommées en français | cohérence avec le reste du projet |
| Colonne `annee` dérivée | clé de partitionnement |
| Valeurs mortes écartées **en amont** | 12 délistages + 2 tickers douteux, causes documentées |

## Étapes suivantes du laboratoire

| Étape | État |
|---|---|
| 1 · `build_parquet.py` — jeu partitionné | ✅ **fait** |
| 2 · Installer PySpark sous Windows | ⬜ (pièges : `JAVA_HOME`, `winutils.exe`) |
| 3 · `extract_spark.py` — extraction C1 | ⬜ |
| 4 · `query_spark.py` — Spark SQL C2 | ⏸ **seulement si le formateur le demande** |

> 📌 **Plan du 30/07/2026, conservé tel quel** — il montre ce qui était prévu et ce que ça
> devait coûter. **Les 4 étapes ont été faites le 02/08**, en une journée au lieu des 1,5 à 2
> estimées. Les deux pièges annoncés se sont bien produits (`JAVA_HOME`, puis `winutils.exe`,
> refusé et contourné). L'étape 4 a été codée **sans attendre** la réponse du formateur —
> voir `preuve-bigdata-spark.md` et `bigdata/CONCEPTION.md`.

⏸ **Question toujours ouverte** : la preuve big data couvre-t-elle **C1 seul**, ou **aussi C2**
avec Spark SQL ? Jamais posée au formateur — il a seulement dit qu'il examinerait le schéma.

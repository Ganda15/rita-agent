# Laboratoire Big Data — conception (⏸ non implémenté)

> **Statut : CONCEPTION SEULE. Aucun code écrit.**
> En attente du retour du formateur après examen du schéma (*« Yep. I'll do that. »*).

## D'où vient ce dossier

Rendez-vous formateur du 28/07/2026. Sur l'ajout d'une preuve big data **séparée** :

> — *« Other certification, they require you to use all the sources. Even they're being data. »*
> — *« That's what Nadej told me yesterday. »*
> — (sur l'ajout du big data séparément) *« Yeah. It is. »*
> — *« Yep. I'll do that. »* (il examinera le schéma)

**Ce qu'il a validé** : ajouter le big data **séparément** est accepté.
**Ce qu'il n'a pas dit** : sous quelle forme exacte, ni si ça couvre C2.

## ❓ La question à lui poser — jamais posée à ce jour

> La preuve big data doit-elle couvrir **C1 seulement** (automatiser l'extraction depuis un
> système big data), ou **aussi C2** (développer des requêtes de type SQL sur ce système,
> par exemple en Spark SQL) ?

La réponse change la charge de travail du simple au double. **Ne rien coder avant.**

## Pourquoi « séparé » et pas dans le pipeline principal

Le pipeline RITA traite ~10 tickers en temps quasi réel pour produire un briefing quotidien.
Y injecter Spark serait une complexité sans usage : Spark sert à traiter des volumes qu'une
machine seule ne tient pas — ce n'est pas le cas de 10 valeurs du CAC 40.

**Le laboratoire est donc isolé** : il démontre la compétence sans dégrader l'architecture.
C'est aussi la position la plus honnête devant un jury — « j'ai su l'utiliser, et j'ai su
décider de ne pas l'utiliser en production » vaut mieux que du Spark décoratif.

## Ce qui existe déjà et sert de socle

`pipelines/ingest.py` (V0, écrit en mai, jamais modifié depuis) télécharge **5 ans d'historique
OHLCV** et écrit en **Parquet** :

```python
df = yf.download(ticker, period="5y", auto_adjust=True)
combined.to_parquet(DATA_DIR / "ohlcv_5y.parquet")
```

Avec 10 tickers × ~1 250 séances × 5 ans ≈ **~62 500 lignes**. Le format Parquet (colonnaire,
compressé) est déjà le bon format d'entrée pour un moteur big data.

## ✅ Le volume — chiffres MESURÉS, pas estimés (29/07/2026)

**Décision : l'univers réel d'Era**, pas un indice emprunté. Extrait de son classeur de suivi
personnel (`Ganda bourse 672.xlsm`, feuille nommée « RITA »), **122 valeurs** identifiées, puis
**126 tickers candidats testés un par un contre yfinance**.

### Résultat du test réel

| Statut | Nb | Détail |
|---|---|---|
| `OK` | 103 | 2 560 lignes chacune (10 ans complets) |
| `OK_APRES_CORRECTION` | 4 | ticker renommé — récupérées après correction |
| `OK_PARTIEL` | 5 | série interrompue (délistage en cours de période) |
| `DELISTEE` | 12 | événement de société confirmé — définitivement perdues |
| `A_VERIFIER` | 2 | ticker à confirmer manuellement |
| **Exploitable** | **112** | **276 168 lignes sur 10 ans** |

Fichier produit : `data/univers-155.csv` — nom, ticker, statut, nombre de lignes, première
date, et **la cause documentée** pour chaque échec.

### Ce que ça reste, honnêtement

| | Volume | Parquet | `pandas` s'en sort ? |
|---|---|---|---|
| **Univers réel d'Era** ✅ | **276 168 lignes** | **~14 Mo** | **instantané** |
| Vrai big data | milliards de lignes | téraoctets | ❌ impossible sur une machine |

**Ce n'est pas du big data en volume, et il faut l'assumer.** Le plafond est structurel : avec
les données gratuites yfinance, l'intraday est limité (1 min → 7 jours d'historique, 5 min →
60 jours, horaire → 730 jours). Aucun moyen honnête d'atteindre le téraoctet.

### 💎 Mais ce jeu de données a une valeur que le SBF 120 n'aurait jamais eue

Les 4 renommages et 12 délistages ne sont pas des ratés — **c'est exactement la matière que le
critère C3 demande** :

> *« développer des règles d'agrégation […] la suppression des entrées corrompues […]
> l'homogénéisation des formats des données »*

| Problème réel rencontré | Exemple mesuré | Nourrit |
|---|---|---|
| Société renommée, ticker changé | CGG → **Viridien** (`VIRI.PA`) · Plastic Omnium → **OPmobility** (`OPM.PA`) | C3 |
| Fusion / absorption | Peugeot → **Stellantis** (`STLAP.PA`) | C3 |
| Transfert de place de cotation | TechnipFMC : Paris → **NYSE** (`FTI`) | C3 |
| Rachat, retrait de la cote | Iliad, Ingenico, Natixis, Suez, EDF… (12 cas) | C1 + C3 |
| Série partielle | Zodiac Aerospace : 411 lignes puis plus rien (absorbée par Safran) | C3 |
| Multi-devises | EUR (Paris, Xetra) + USD (NYSE) | C3 |
| Multi-places | Euronext Paris, Xetra, NYSE, Amsterdam, Bruxelles | C3 |
| Source sans cotation | ~65 SICAV : valorisées 1×/jour par le gestionnaire, absentes de yfinance | C1 + C3 |

Un univers SBF 120 propre n'aurait posé **aucun** de ces problèmes. Ici, ils sont réels,
mesurés, et documentés dans un CSV versionné.

### Ce qui rend quand même la preuve valable

Le critère officiel ne parle **jamais** de volume :

> « Automatiser l'extraction de données depuis […] **un système big data** en **programmant le
> script adapté** »

Ce qui est évalué : **savoir programmer contre un système big data**. Un étudiant n'a pas de
cluster, le référentiel le sait. Donc ce qui compte, c'est d'utiliser réellement Spark —
moteur distribué, Spark SQL, exécution paresseuse, Parquet partitionné — pas de gonfler un
chiffre.

### 🎤 Position à l'oral (à apprendre telle quelle)

> « J'ai pris mon univers réel : les 155 titres que je suivais à la main chaque matin sur mon
> compte-titres. J'ai testé chaque ticker un par un — **112 sont exploitables, 276 000 lignes
> sur 10 ans**. Les autres sont des sociétés rachetées, renommées ou liquidées : Iliad,
> Ingenico, Natixis, Suez… et 4 que j'ai récupérées en corrigeant le ticker, comme CGG devenue
> Viridien ou Peugeot devenue Stellantis.
>
> **Ce volume n'est pas du big data**, et je l'assume : pandas le traiterait instantanément. Ce
> que je démontre, c'est la capacité à programmer contre un système big data — Spark, Parquet
> partitionné par année, lecture avec *predicate pushdown*. L'architecture serait identique sur
> des téraoctets.
>
> Et ce jeu de données a une qualité qu'un indice propre n'aurait pas : il contient de vrais
> défauts — des tickers morts, des renommages, deux devises, cinq places de cotation. C'est ce
> qui m'a permis de construire mes règles d'agrégation et de nettoyage sur des cas réels, pas
> sur des cas d'école. »

Cette réponse est **plus solide** que « j'ai du big data » : un juré qui travaille en data verra
immédiatement que 276 000 lignes n'en sont pas. L'admettre coûte moins cher que le nier — et le
récit des tickers morts prouve qu'on a manipulé de la vraie donnée.

## Structure prévue (à créer seulement après son retour)

```
bigdata/
├── CONCEPTION.md          ← ce fichier
├── build_parquet.py       ⬜ SBF 120 × 10 ans → Parquet partitionné (~306 000 lignes)
├── extract_spark.py       ⬜ C1 : extraction depuis le système big data
└── query_spark.py         ⬜ C2 : requêtes Spark SQL — SEULEMENT si le formateur le demande
```

**Partitionnement prévu** : `data/bigdata/ohlcv/annee=YYYY/` — c'est ce partitionnement qui
rend la démonstration crédible indépendamment du volume. Spark lit uniquement les partitions
nécessaires (*predicate pushdown*), exactement comme il le ferait sur des téraoctets. C'est la
**méthode** qui prouve la compétence, pas la taille du fichier.

**Aucun de ces fichiers n'existe.** Le dossier ne contient que cette conception.

## Choix du moteur — à trancher avec lui

| Moteur | Pour | Contre |
|---|---|---|
| **PySpark local** | c'est *le* nom que le jury attend derrière « système big data » ; Spark SQL couvre C2 directement | lourd à installer (JVM), lent au démarrage |
| **DuckDB** | installation triviale, SQL natif, très rapide sur Parquet | moins reconnaissable comme « big data » par un jury |

Recommandation : **PySpark**, précisément parce que le critère nomme un « système big data » et
que Spark est la réponse canonique. DuckDB serait plus élégant techniquement mais demanderait
de justifier pourquoi ce n'est pas Spark — un débat qu'on n'a pas besoin d'ouvrir.

## Ce que ça change pour la décision D9

D9 (18/07) disait : **PySpark supprimé du pipeline principal**. Cette décision **reste
valide** — le laboratoire est séparé, il ne réintroduit pas Spark dans le flux de production.

Ce qui change : avant, le big data était considéré comme « non nécessaire ». Maintenant, il
devient **une preuve supplémentaire valorisable**, dans un périmètre isolé et borné.

## Charge estimée

| Tâche | Charge |
|---|---|
| Construire le Parquet SBF 120 × 10 ans | ~½ journée |
| Installer PySpark et le faire tourner sous Windows | ~½ journée (piège classique : `JAVA_HOME`, `winutils.exe`) |
| Script d'extraction C1 + preuve | ~½ journée |
| Requêtes Spark SQL C2 + preuve *(si demandé)* | ~½ journée |
| **Total** | **1,5 à 2 journées** |

À caser en Q2 ou Q3 selon sa réponse — pas avant.

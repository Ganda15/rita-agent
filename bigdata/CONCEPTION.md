# Laboratoire Big Data — conception et réalisation

> ## ✅ Statut : **IMPLÉMENTÉ** — 4 étapes sur 4, terminé le 02/08/2026
>
> | | |
> |---|---|
> | Code | `build_parquet.py` · `session_spark.py` · `extract_spark.py` · `query_spark.py` · `explorer.py` |
> | Tests | **16 verts** (`tests/test_spark.py`) — vérifié le 10/08 |
> | Jeu de données | **11 partitions** `annee=2016` → `annee=2026` · **13 972 899 octets** |
> | Preuves | `evidence/C1/preuve-08-bigdata-parquet.md` · `evidence/C1/preuve-bigdata-spark.md` |
> | Critères | **C1** *(5ᵉ type de source)* **et C2** *(requêtes Spark SQL)* |
>
> ⚠️ **Ce fichier annonçait « CONCEPTION SEULE, aucun code écrit » jusqu'au 10/08/2026.**
> Il avait été rédigé le 29/07, avant l'implémentation du 02/08, et n'avait jamais été remis
> à niveau — alors que le rapport E1 y renvoie explicitement. Un lecteur suivant le lien lisait
> donc « aucun code écrit » à propos d'un travail terminé.
>
> **La partie conception ci-dessous est conservée telle quelle** : le raisonnement sur le
> volume et la valeur du jeu de données reste vrai, et c'est lui qui justifie les choix
> faits. Seuls le statut, la structure et la charge ont été
> réécrits pour décrire ce qui **existe** au lieu de ce qui était **prévu**.

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

> ✅ **Résolu par les faits, le 02/08.** La question n'a toujours pas reçu de réponse, mais elle
> **n'est plus bloquante : les deux compétences sont couvertes.** `extract_spark.py` répond à
> C1 (connexion et extraction programmatique depuis un système big data), `query_spark.py`
> répond à C2 (trois requêtes dans le langage propre au système). Coder les deux a coûté une
> demi-journée de plus que d'en coder un seul — moins cher que d'attendre une réponse qui n'est
> jamais venue.
>
> **Reste à la lui poser pour confirmation**, sans que rien n'en dépende.

## Pourquoi « séparé » et pas dans le pipeline principal

Le pipeline RITA traite ~10 tickers en temps quasi réel pour produire un briefing quotidien.
Y injecter Spark serait une complexité sans usage : Spark sert à traiter des volumes qu'une
machine seule ne tient pas — ce n'est pas le cas de 10 valeurs du CAC 40.

**Le laboratoire est donc isolé** : il démontre la compétence sans dégrader l'architecture.
C'est aussi la position la plus honnête : savoir utiliser Spark **et** savoir décider de
ne pas l'utiliser en production vaut mieux que du Spark décoratif.

## Ce qui servait de socle au 29/07 — et ce que c'est devenu

> ⚠️ **Section réécrite le 10/08 : elle décrivait du code qui n'existe plus.**

**Ce qui était écrit ici le 29/07** : *« `pipelines/ingest.py` (V0, écrit en mai, jamais modifié
depuis) télécharge 5 ans d'historique OHLCV et écrit en Parquet — avec 10 tickers ×
~1 250 séances ≈ 62 500 lignes. »*

**Ce qui est vrai aujourd'hui** : ce code **n'est plus dans `ingest.py`**. Deux choses ont
changé depuis :

| | Avant (mai → 29/07) | Maintenant |
|---|---|---|
| **L'écriture Parquet** | dans `pipelines/ingest.py` | déplacée dans **`bigdata/build_parquet.py`**, seul fichier du dépôt qui appelle encore `to_parquet` |
| **`pipelines/ingest.py`** | téléchargeait et écrivait du Parquet | est devenu le **pipeline d'agrégation** (C3) : 4 étapes — `ecb`, `cotations`, `rss`, `scraping` — qui écrivent en **PostgreSQL**, avec un `COMMIT` par étape |
| **Le volume** | ~62 500 lignes *(10 tickers × 5 ans)* | **276 168 lignes** *(112 valeurs × 10 ans)* |

**Pourquoi la séparation est meilleure** : le Parquet est un **artefact de démonstration** pour
le laboratoire big data ; la base PostgreSQL est le **stockage de production** du briefing. Les
mélanger obligerait à reconstruire l'un chaque fois qu'on alimente l'autre. Aujourd'hui
`build_parquet.py` se relance en ~32 s quand on en a besoin, et le pipeline quotidien ne le
touche pas.

Le format Parquet (colonnaire, compressé, partitionnable) reste le bon format d'entrée pour un
moteur big data — c'est le seul point de cette section qui n'a pas bougé.

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

## ✅ Structure réelle (au 10/08/2026)

```
bigdata/
├── CONCEPTION.md          ← ce fichier
├── explorer.py            ✅ analyse exploratoire — 276 168 lignes, 6 questions
├── build_parquet.py       ✅ univers réel × 10 ans → Parquet partitionné par année
├── session_spark.py       ✅ session Spark 4.2.0, renseigne JAVA_HOME toute seule
├── extract_spark.py       ✅ C1 : extraction depuis le système big data
└── query_spark.py         ✅ C2 : 3 requêtes Spark SQL
```

⚠️ **Deux écarts avec le plan initial, tous deux volontaires :**

| Prévu | Réalisé | Pourquoi |
|---|---|---|
| SBF 120, ~306 000 lignes | **univers réel d'Era**, 276 168 lignes | un indice propre n'aurait posé aucun des défauts qui nourrissent C3 — voir §« Mais ce jeu de données a une valeur… » |
| `query_spark.py` **seulement si le formateur le demande** | **codé quand même** | la réponse n'est jamais venue ; coder les deux a coûté une demi-journée et débloque C2 |

Deux modules non prévus se sont ajoutés : `explorer.py` (l'analyse exploratoire, qui a dicté
tout le modèle de données) et `session_spark.py` (parce que faire démarrer Spark sous Windows
mérite son propre module — voir ci-dessous).

**Partitionnement réalisé** : `data/bigdata/ohlcv/annee=YYYY/`, **11 partitions** de 2016 à
2026. C'est ce partitionnement qui rend la démonstration crédible indépendamment du volume.
Mesuré dans le plan physique de Spark : **11 fichiers connus, 1 seul ouvert** sur une requête
filtrée par année. Les dix autres ne sont pas filtrés après lecture — ils ne sont **jamais
lus**. C'est la **méthode** qui prouve la compétence, pas la taille du fichier.

## ✅ Choix du moteur — tranché : PySpark

| Moteur | Pour | Contre |
|---|---|---|
| **PySpark local** ✅ **retenu** | c'est *le* nom standard de l'industrie derrière « système big data » ; Spark SQL couvre C2 directement | lourd à installer (JVM), lent au démarrage |
| **DuckDB** | installation triviale, SQL natif, très rapide sur Parquet | moins identifié comme « big data » |

**PySpark**, précisément parce que le critère nomme un « système big data » et que Spark est la
réponse canonique. DuckDB aurait été plus élégant techniquement mais aurait demandé de
justifier pourquoi ce n'est pas Spark — un débat inutile à ouvrir.

**Version installée** : `pyspark 4.2.0` sur **Eclipse Temurin JDK 21.0.12+8**, dans
`C:\Users\kanda\Tools\jdk-21.0.12+8` — installé **sans droits administrateur**, SHA256 vérifié.
`session_spark.preparer_environnement()` renseigne `JAVA_HOME` tout seul : rien à exporter à la
main, et la suite de tests reste verte sur une machine sans JDK (les tests d'intégration Spark
s'ignorent d'eux-mêmes plutôt que d'échouer).

## ⚠️ Le piège Windows — et le refus assumé

Sous Windows, Spark lève `UnsatisfiedLinkError: NativeIO$Windows.access0` faute de deux
binaires Hadoop : `winutils.exe` et `hadoop.dll`.

**Tous les tutoriels disent de les télécharger depuis un dépôt communautaire. Ça n'a pas été
fait** — ce sont des exécutables **non signés**, issus d'un tiers non officiel, chargés dans la
machine virtuelle Java. Sur un projet qui documente par ailleurs sa conformité RGPD, ce serait
incohérent.

**Le contournement** : chercher **pourquoi** ce code natif est appelé. Réponse — uniquement
pour **lister** un répertoire. Donc le listage est fait en Python et les fichiers sont passés
explicitement à `spark.read`, avec `basePath` pour conserver la colonne de partition.

⚠️ **Ne jamais « réparer » ça en installant les binaires.**

## Ce que ça change pour la décision D9

D9 (18/07) disait : **PySpark supprimé du pipeline principal**. Cette décision **reste
valide** — le laboratoire est séparé, il ne réintroduit pas Spark dans le flux de production.

Ce qui change : avant, le big data était considéré comme « non nécessaire ». Maintenant, il
devient **une preuve supplémentaire valorisable**, dans un périmètre isolé et borné.

## ✅ Charge — estimée le 29/07, réalisée le 02/08

| Tâche | Estimé | Réalisé |
|---|---|---|
| Construire le Parquet × 10 ans | ~½ journée | ✅ ~32 s d'exécution, une fois le code écrit |
| Installer PySpark sous Windows | ~½ journée | ✅ **le piège annoncé s'est produit** — `JAVA_HOME` **et** `winutils.exe` |
| Script d'extraction C1 + preuve | ~½ journée | ✅ `extract_spark.py` + `preuve-bigdata-spark.md` |
| Requêtes Spark SQL C2 + preuve | ~½ journée *(si demandé)* | ✅ **fait sans attendre la réponse** |
| **Total** | **1,5 à 2 journées** | **1 journée** (02/08) |

L'estimation était bonne, et le piège annoncé — `winutils.exe` — est exactement celui qui s'est
produit. Ce qui a fait gagner du temps : le refuser au lieu de l'installer, et chercher
pourquoi il était appelé.

---

## 📋 Ce qui reste ouvert

| # | Sujet | Bloquant ? |
|---|---|---|
| 1 | La question au formateur : la preuve big data couvre-t-elle C1 seul ou aussi C2 ? | ❌ **non** — les deux sont couvertes de fait |
| 2 | Il avait annoncé qu'il examinerait le schéma (*« Yep. I'll do that. »*) — pas de retour à ce jour | ❌ non |

**Rien ne bloque.** Le laboratoire big data est terminé, testé et prouvé.

---

## 🖼️ Les deux schémas — créés les 10 et 11/08/2026

Le formateur avait annoncé qu'il **examinerait le schéma** (*« Yep. I'll do that. »*).
**Il n'y en avait aucun** : 284 lignes de texte, deux preuves écrites, zéro image.

📎 [`schemas/SCHEMA-BIGDATA-partition-pruning.png`](schemas/SCHEMA-BIGDATA-partition-pruning.png)
— à regarder · sources éditables : [`.svg`](schemas/SCHEMA-BIGDATA-partition-pruning.svg) et
[`.drawio`](schemas/SCHEMA-BIGDATA-partition-pruning.drawio)

Il montre en une page les quatre choses qui comptent :

| Bloc | Contenu |
|---|---|
| ① **La chaîne** | `build_parquet` → `session_spark` → `extract_spark` (C1) / `query_spark` (C2) |
| ② **Le partitionnement** | les **11 partitions** avec leur volumétrie réelle, `annee=2024` en évidence |
| ③ **La preuve** | l'extrait du plan physique : `PartitionFilters`, 11 fichiers connus, **1 ouvert** |
| ④ **La comparaison** | pourquoi optimiser ne veut pas dire la même chose en SQL et en Spark |

> **Pourquoi un dessin plutôt qu'un paragraphe** : le *partition pruning* est visuel par
> nature — dix barres grises et une bleue disent en trois secondes ce qu'un paragraphe
> explique mal.

### ② [`schemas/SCHEMA-BIGDATA-3-requetes-sparksql.png`](schemas/SCHEMA-BIGDATA-3-requetes-sparksql.png) — **C2**

*(sources éditables : [`.svg`](schemas/SCHEMA-BIGDATA-3-requetes-sparksql.svg) ·
[`.drawio`](schemas/SCHEMA-BIGDATA-3-requetes-sparksql.drawio))*

Le premier schéma couvre **C1** (l'extraction). Celui-ci couvre **C2** : les trois requêtes
Spark SQL, et surtout **ce que chacune déclenche** dans le moteur.

| Requête | Filtre | Partitions lues | Lignes lues | Mécanisme |
|---|---|---|---|---|
| **S1** volumétrie | aucun | **11 / 11** | 276 168 — **100 %** | shuffle *(GROUP BY)*, **aucun élagage** |
| **S2** amplitude | `annee >= 2024` | **3 / 11** | 71 334 — **25,8 %** | **pruning** *(8 fichiers évités)* + shuffle |
| **S3** extrêmes | `annee >= 2025` | **2 / 11** | 43 686 — **15,8 %** | **pruning** *(9 évités)* + shuffle *(`PARTITION BY ticker`)* |

**Ce que les trois démontrent ensemble** — et c'est le point non évident :

> ⚠️ **Lire moins ne veut pas dire aller plus vite.** Mesuré en session chaude : **S2 = 0,90 s**
> en lisant 25,8 % du jeu, **S3 = 1,33 s** en n'en lisant que 15,8 %. S3 lit **moins** et coûte
> **plus**, parce que `PARTITION BY ticker` force un *shuffle* — la redistribution des données
> entre exécuteurs, l'opération la plus chère du monde distribué.
>
> **Le filtre décide du coût de lecture ; la forme du calcul décide du coût de traitement.**
> Les deux sont indépendants, et c'est ce qui distingue vraiment Spark d'une base relationnelle.

⚠️ **`.png` à exporter depuis draw.io pour les deux** (File → Export as → PNG).

---

## 🔢 Les chiffres à citer, vérifiés le 10/08/2026

| Grandeur | Valeur | Vérifiée par |
|---|---|---|
| Partitions | **11** *(`annee=2016` → `annee=2026`)* | `ls -d data/bigdata/ohlcv/annee=*` |
| Profondeur | **10 ans pile** — 28/07/2016 → 29/07/2026, **3 652 jours** | min/max de la colonne `date` |
| Taille du jeu | **13 972 899 octets** = **13,3 Mio** = **14,0 Mo** | somme des 11 fichiers `.parquet` |
| Lignes | **276 168** | `explorer.py` |
| Tests | **16 verts** en 14 s | `pytest tests/test_spark.py` |
| Partition pruning | **11 fichiers connus → 1 seul ouvert**, 27 648 lignes | plan physique Spark |

⚠️ **Attention à l'unité.** Le rapport E1 annonce **« 14 Mo »** — corrigé le 10/08, il disait
« 13 Mo » jusque-là, ce qui était un arrondi vers le bas dans **les deux** conventions
(13,97 Mo en base 10, 13,33 Mio en base 2). La valeur exacte est **13 972 899 octets**.

### ⚠️ « 10 ans » et « 11 partitions » — les deux sont vrais

Contradiction apparente, repérée le 10/08 en regardant le schéma. La réponse est précise et
vaut la peine d'être sue :

| | |
|---|---|
| Première séance | **2016-07-28** |
| Dernière séance | **2026-07-29** |
| Durée | **3 652 jours = 10,00 ans** |

Le téléchargement utilise `period="10y"` depuis le 29/07/2026. Une fenêtre de dix ans qui
**commence en juillet** traverse **onze années civiles** :

```
2016 : du 28 juillet      →  ~5 mois   (11 980 lignes)
2017 → 2025 : pleines     →   9 ans    (~27 500 lignes chacune)
2026 : jusqu'au 29 juillet →  ~7 mois   (15 903 lignes)
                              ─────────
                              10 ans
```

**Les deux bouts partiels se complètent** : 5 mois + 7 mois = 12 mois. C'est visible sur le
schéma — les barres 2016 et 2026 sont nettement plus courtes que les neuf autres.

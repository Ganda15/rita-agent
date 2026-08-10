# C1 + C2 · Preuve — système big data (Apache Spark)

**Compétences visées** — cette preuve couvre **la moitié big data de deux compétences** :

- **C1** : « Connexion programmatique (Python, R, etc.) à un système de gestion de base de
  données **et à un système big data** (Hive, Apache Impala, etc.) » · « Exécution
  programmatique des requêtes d'extraction depuis un système big data »
- **C2** : « Développer des requêtes de type SQL d'extraction des données depuis un système de
  gestion de base de données **et un système big data** en appliquant le langage de requête
  propre au système »

**Fichiers** : `bigdata/session_spark.py` · `bigdata/extract_spark.py` · `bigdata/query_spark.py`
**Tests** : `tests/test_spark.py` (16) · **Date** : 2026-08-02

---

## 1. Ce que ce travail démontre, et ce qu'il ne démontre pas

| ✅ Démontré | ❌ Non démontré |
|---|---|
| Connexion programmatique à Spark | Un cluster distribué réel |
| Lecture native d'un jeu Parquet partitionné | La tolérance aux pannes d'un cluster |
| *Partition pruning* visible dans le plan physique | Que le volume justifie Spark |
| Requêtes Spark SQL, dont fonctions de fenêtrage | |

**276 168 lignes ne sont pas du big data.** 13,3 Mo tiennent en mémoire ; PostgreSQL les
traite en millisecondes. Ce qui est démontré ici c'est la **méthode** — elle serait identique
sur des téraoctets. Le dire au jury **avant** qu'il pose la question vaut mieux que de le
défendre après.

---

## 2. Le choix technique, et pourquoi

Le référentiel nomme lui-même les technologies attendues : « un système big data (Hive,
**Spark**, etc.) ». Retenir une technologie citée évite d'avoir à défendre un équivalent.

| Option | Écartée parce que |
|---|---|
| Hive | Exige Hadoop + un metastore — une infrastructure entière pour 14 Mo |
| Impala | Distribution Cloudera, pas installable proprement sous Windows |
| DuckDB | Excellent, mais **pas** un système big data — c'est un moteur mono-machine |
| **Spark** | ✅ Nommé au référentiel, installable en local, SQL standard |

**Version** : Apache Spark 4.2.0 (PySpark) sur **Eclipse Temurin JDK 21.0.12+8**,
téléchargé depuis Adoptium, **empreinte SHA256 vérifiée** avant extraction, installé sans
droits administrateur ni écriture en base de registre.

---

## 3. 🔒 Un obstacle résolu **sans** compromettre la sécurité

### Le problème

```
spark.read.parquet("data/bigdata/ohlcv")
-> java.lang.UnsatisfiedLinkError: 'boolean org.apache.hadoop.io.nativeio.
   NativeIO$Windows.access0(java.lang.String, int)'
```

Sous Windows, lister un répertoire passe par du **code natif Hadoop** fourni par deux
binaires absents d'une installation standard : `winutils.exe` et `hadoop.dll`.

### La solution habituelle, et pourquoi elle a été refusée

Tous les tutoriels disent la même chose : télécharger ces binaires depuis un dépôt
communautaire. **Écarté ici.** Ce sont des **exécutables non signés**, chargés **dans la
JVM**, provenant d'un tiers non officiel.

> Sur un projet qui documente par ailleurs le RGPD, la purge des données personnelles et les
> garde-fous d'un agent, installer une DLL de provenance incertaine serait **incohérent**.

### Le contournement retenu

Le code natif n'est appelé que pour **lister un répertoire**. En listant côté Python et en
passant les fichiers explicitement, on n'y touche jamais.

```python
fichiers = glob("data/bigdata/ohlcv/*/*.parquet")       # listage par Python
spark.read.option("basePath", base).parquet(*fichiers)  # lecture native par Spark
```

`basePath` est **indispensable** : sans lui, Spark ne sait pas que `annee=2024` est une
partition, la colonne `annee` disparaît du schéma — et le *partition pruning* avec elle.

**C'est la partie de ce travail dont je suis le plus satisfait** : le problème n'a pas été
contourné en baissant la garde, il a été compris puis évité.

---

## 4. Sortie réelle — C1 : extraction (`extract_spark.py`)

```
======================================================================
EXTRACTION SPARK — systeme big data (C1)
======================================================================
  Filtre           : annee = 2024
  Lignes extraites : 27,648
  Valeurs          : 108
  Partitions RDD   : 6
  Duree            : 3.72 s
  Colonnes         : ticker, date, ouverture, haut, bas, cloture, volume, annee

  Plan d'execution — la preuve du partition pruning :
    PartitionFilters: [isnotnull(annee#8), (annee#8 = 2024)]
    Fichiers connus de Spark : 11  ->  seule la partition annee=2024 est lue
```

**Comment lire cette preuve** : Spark connaît 11 fichiers (11 années). `PartitionFilters`
montre qu'il n'en ouvre **qu'un**. Les 10 autres ne sont jamais lus — pas filtrés après
lecture, **jamais lus**. C'est là toute la différence.

---

## 5. Sortie réelle — C2 : requêtes Spark SQL (`query_spark.py`)

### S1 · Volumétrie par année *(0,8 s)*

```
    annee  lignes  valeurs  cloture_moyenne
    2016   11980   108      53016.13
    2017   27770   108      34478.62
    2019   27463   107       8024.84
    2022   27480   106        120.96
    2026   15903   108         93.12
```

**Ce que ce résultat révèle** : la clôture moyenne passe de 53 016 € à 93 €. Ce n'est pas un
krach — c'est **ALJXR.PA**, le ticker aberrant repéré à l'analyse exploratoire (prix max
7 156 748), qui écrase la moyenne des premières années. La moyenne est un mauvais indicateur
quand une valeur aberrante subsiste. **Le défaut trouvé à l'étape 1 se voit encore ici.**

2016 et 2026 sont incomplètes — début et fin de l'historique, pas une anomalie.

### S2 · Amplitude moyenne, `annee >= 2024` *(0,8 s)*

```
    -> PARTITION PRUNING : [isnotnull(annee#8), (annee#8 >= 2024)]
    -> SHUFFLE declenche

    ticker    seances  amplitude_moy_pct  amplitude_max_pct  volume_moyen
    ALCBX.PA  657      12.34              2614.29            2013882
    ATO.PA    657       9.90               150.00             115772
    ALJXR.PA  657       9.03               154.49             874669
```

### S3 · Meilleure séance de chaque valeur — fenêtrage *(0,97 s)*

```
    ticker    seance      cloture_veille  cloture  variation_pct
    ETL.PA    2025-03-05  3.57            7.84     119.75
    ALMKT.PA  2025-06-03  0.10            0.16      63.06
    VIRI.PA   2025-10-31  76.45           106.00    38.65
```

⚠️ `VIRI.PA` : cette valeur porte un **regroupement d'actions** (*reverse split*) non traité —
identifié, table `operation_sur_titre` conçue mais **non construite**. Dette technique
assumée et écrite, pas masquée.

---

## 6. 💎 Le point de conception à défendre : optimiser ne veut pas dire la même chose

C'est le cœur de C2, et c'est ce qui justifie d'avoir fait les **deux** moitiés.

| | PostgreSQL | Spark SQL |
|---|---|---|
| **Structure d'accès** | index B-tree `(ticker, date_seance)` | partitionnement par répertoire `annee=` |
| **Preuve** | `EXPLAIN ANALYZE` | `explain()` — plan physique |
| **Optimiser, c'est** | choisir le **bon chemin d'accès** | **ne pas lire** les partitions inutiles |
| **Ce qui coûte cher** | un balayage séquentiel | un **shuffle** entre exécuteurs |
| **Exécution** | un processus | `local[*]` — un exécuteur par cœur |

En base relationnelle on cherche à **lire vite**. En big data on cherche à **ne pas lire**.

Conséquence directe dans le code : `spark.sql.shuffle.partitions` est passé de **200
(défaut) à 8**. Le défaut suppose un cluster ; en local il crée 200 tâches pour 27 000
lignes — plus de temps passé à coordonner qu'à calculer.

---

## 7. Tests — 16, en deux familles séparées volontairement

```
C:\Python314\python.exe -m pytest tests/test_spark.py -q
→ 16 passed in 15.94s
```

| Famille | Nombre | Lancent Spark ? |
|---|---|---|
| **Rapides** — configuration, URI, contenu des requêtes | 11 | non |
| **Intégration** — vraie session, plan physique, résultats | 5 | oui |

Les tests d'intégration s'**ignorent automatiquement** si `JAVA_HOME` ou le jeu Parquet
manquent. **Un test qui échoue faute d'environnement n'apprend rien** — il apprend juste à
ignorer les échecs. Sur une machine sans JDK, la suite reste verte et honnête.

Deux tests méritent d'être montrés :

- `test_le_partition_pruning_apparait_dans_le_plan` — vérifie le pruning sur le **plan réel**,
  pas sur le texte de la requête. Sans lui, supprimer `basePath` casserait l'optimisation en
  silence, sans faire tomber un seul test.
- `test_requete_inconnue_leve_avant_de_lancer_spark` — démarrer une JVM pour découvrir un nom
  de requête invalide serait absurde.

**Suite complète du projet : 167 tests verts.**

---

## 8. ❓ Question ouverte pour le formateur

Le référentiel cite le big data dans **C1** (connexion + extraction) **et C2** (requêtes).
Les deux sont couvertes ici. **À confirmer avec Elbby** : attend-il une démonstration sur un
cluster réel, ou la méthode sur un jeu local suffit-elle dès lors que la limite est
explicitement énoncée ?

---

## 9. 🎤 Phrase pour l'oral

> « Le référentiel demande un système big data, j'ai pris Spark parce qu'il y est nommé.
> Mais je préfère le dire tout de suite : 276 000 lignes, ce n'est pas du big data. Ce que je
> démontre, c'est la méthode. Sous Windows, Spark plantait faute de deux binaires Hadoop. La
> solution que tout le monde donne, c'est de télécharger un `.exe` et une `.dll` non signés
> sur un dépôt communautaire, et de les charger dans la JVM. Je ne l'ai pas fait — sur un
> projet où je documente le RGPD, ç'aurait été incohérent. J'ai cherché pourquoi ce code natif
> était appelé : uniquement pour lister un répertoire. Donc je liste avec Python et je passe
> les fichiers à Spark. Et le partition pruning fonctionne — c'est visible dans le plan :
> Spark connaît onze fichiers, il en ouvre un. »

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Big data** | Volume trop grand pour une seule machine — d'où la répartition sur plusieurs |
| **Apache Spark** | Moteur de traitement distribué : découpe le travail entre machines |
| **PySpark** | L'interface Python de Spark |
| **JVM** (*Java Virtual Machine*) | Le programme qui exécute Java — Spark est écrit en Java/Scala |
| **JDK** | Kit de développement Java ; contient la JVM |
| **Parquet** | Format de fichier **colonnaire** : lire une colonne sans lire les autres |
| **Partitionnement** | Ranger les données en répertoires (`annee=2024/`) pour n'en lire qu'un |
| **Partition pruning** (*élagage*) | Spark ignore les répertoires exclus par le filtre — sans les ouvrir |
| **`basePath`** | Dit à Spark où commencent les répertoires de partition |
| **Plan physique** | Ce que Spark va réellement exécuter — la preuve, pas l'intention |
| **RDD** | La structure de données interne de Spark, découpée en morceaux parallélisables |
| **Shuffle** (*brassage*) | Redistribution des données entre exécuteurs — l'opération la plus coûteuse |
| **Exécuteur** (*executor*) | Un processus Spark qui traite une part des données |
| **`local[*]`** | Mode local, un exécuteur par cœur du processeur |
| **Fonction de fenêtrage** | Calcul sur un groupe de lignes voisines — ici `LAG`, `RANK` |
| **`LAG()`** | Valeur de la ligne précédente — ici la clôture de la veille |
| **`RANK()`** | Classement à l'intérieur d'un groupe |
| **CTE** (`WITH ... AS`) | Sous-requête nommée, pour lire une requête par étapes |
| **`winutils.exe` / `hadoop.dll`** | Binaires Hadoop pour Windows, absents par défaut — **non installés ici** |
| **SHA256** | Empreinte numérique d'un fichier ; vérifie qu'il n'a pas été altéré |
| **Reverse split** (*regroupement d'actions*) | 10 actions à 1 € deviennent 1 action à 10 € — fausse les variations si non traité |
| **Amplitude** | Écart entre le plus haut et le plus bas d'une séance, en % |

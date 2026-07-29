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

## ⚠️ Le volume — dire la vérité plutôt que gonfler un chiffre

**Décision d'Era (29/07) : option A, SBF 120 × 10 ans ≈ 306 000 lignes.**

Mais il faut être clair sur ce que ça représente :

| | Volume | Parquet | `pandas` s'en sort ? |
|---|---|---|---|
| Option B — 10 tickers × 5 ans | ~62 500 lignes | ~3 Mo | instantané |
| **Option A — SBF 120 × 10 ans** ✅ | **~306 000 lignes** | **~15 Mo** | **instantané aussi** |
| Vrai big data | milliards de lignes | téraoctets | ❌ impossible sur une machine |

**A est 5× plus gros que B, et tout aussi peu « big ».** Les deux sont du *small data*.

### Peut-on atteindre du vrai volume ? Non, pas avec des données gratuites

| Granularité yfinance | Historique autorisé | Volume max (120 tickers) |
|---|---|---|
| Journalier | illimité | ~306 000 |
| Horaire | 730 jours | ~700 000 |
| 5 minutes | 60 jours | ~690 000 |
| 1 minute | **7 jours seulement** | ~115 000 |

Le plafond est structurel, pas un manque d'effort.

### Ce qui rend quand même la preuve valable

Le critère officiel ne parle **jamais** de volume :

> « Automatiser l'extraction de données depuis […] **un système big data** en **programmant le
> script adapté** »

Ce qui est évalué : **savoir programmer contre un système big data**. Un étudiant n'a pas de
cluster, le référentiel le sait. Donc ce qui compte, c'est d'utiliser réellement Spark —
moteur distribué, Spark SQL, exécution paresseuse, Parquet partitionné — pas de gonfler un
chiffre.

### 🎤 Position à l'oral (à apprendre telle quelle)

> « J'ai construit un jeu Parquet de 306 000 lignes sur le SBF 120, et je l'interroge avec
> PySpark et Spark SQL. **Ce volume ne nécessite pas Spark** — pandas le traiterait
> instantanément. Je l'ai fait pour démontrer la compétence sur un système big data, dans un
> laboratoire séparé, sans l'imposer au pipeline de production où il n'apporterait rien. Si le
> volume passait à l'échelle réelle, l'architecture ne changerait pas : c'est déjà du Parquet
> partitionné lu par Spark. »

Cette réponse est **plus solide** que « j'ai du big data » : un juré qui travaille en data verra
immédiatement que 306 000 lignes n'en sont pas. L'admettre coûte moins cher que le nier.

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

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

⚠️ **À vérifier avant de s'engager** : ce volume est-il suffisant pour être présenté comme
« big data » ? Une réponse honnête est non — c'est un volume qu'un `pandas` avale sans
broncher. Deux façons d'être défendable :

| Option | Volume | Argument |
|---|---|---|
| **A — élargir l'univers** | tout le SBF 120 sur 10 ans ≈ **300 000 lignes** | plus crédible, ~5 min de téléchargement |
| **B — assumer le volume** | ~62 500 lignes | *« le critère demande de savoir programmer le script adapté, pas d'atteindre un seuil de volume »* |

Recommandation : **A**, parce que le mot « big data » appelle une attente de volume, et qu'y
répondre coûte quelques minutes de téléchargement.

## Structure prévue (à créer seulement après son retour)

```
bigdata/
├── CONCEPTION.md          ← ce fichier
├── build_parquet.py       ⬜ construit le jeu Parquet (SBF 120 × 10 ans)
├── extract_spark.py       ⬜ C1 : extraction depuis le système big data
└── query_spark.py         ⬜ C2 : requêtes Spark SQL — SEULEMENT si le formateur le demande
```

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

# C3 · Preuve — Pipeline d'agrégation multi-source

**Compétence C3** : « Développer des règles d'agrégation de données issues de différentes
sources […] la suppression des entrées corrompues […] l'homogénéisation des formats des
données afin de préparer le stockage du jeu de données final. »

**Fichier** : `pipelines/ingest.py` · **Tests** : `tests/test_ingest.py` (15 tests)
**Date** : 2026-08-01

## Le trou que cette preuve comble

Audit du 01/08 : `ecb.py`, `rss.py` et `scraper.py` **collectaient sans jamais écrire en
base**. Les tables `taux_change` et `article` étaient vides. Il n'existait **aucun script
d'agrégation unique** — seuls le Parquet et les CSV entraient, via `db/importer.py`.

C3 exige un jeu de données **unique** issu de **différentes** sources. Ce n'était pas le cas.

## Répartition avec `db/importer.py`

```
db/importer.py       -> le socle     : univers, alias, historique Parquet, positions CSV
pipelines/ingest.py  -> le quotidien : taux BCE, articles RSS, cours scrapés
```

Le socle se reconstruit rarement (32 s de téléchargement). Le quotidien tourne chaque jour.

## Commande

```powershell
C:\Python314\python.exe -X utf8 -m pipelines.ingest --simulation   # sans ecrire
C:\Python314\python.exe -X utf8 -m pipelines.ingest                # execution
```

## Sortie réelle

```
====================================================================
PIPELINE D'AGREGATION  --  EXECUTION
====================================================================

  taux_change (BCE)            lues    4 | ecrites    5 | rejetees   0

  articles (RSS)               lues   30 | ecrites   30 | rejetees   0
      - flux OK 3/3

  cours du jour (scraping)     lues    3 | ecrites    3 | rejetees   0
      - MC.PA : ISIN FR0000121014 ajoute
      - OR.PA : ISIN FR0000120321 ajoute
      - AI.PA : ISIN FR0000120073 ajoute

  Etapes reussies : 3/3   Duree : 2.4 s
```

État de la base après agrégation :

```
taux_change  : 11 lignes, devises : CHF EUR GBP JPY USD
article      : 30 lignes, dont 0 bloque(s)
valeur.isin  : 3 renseignes / 111   (etaient 0)
cotation     : 273 611 lignes       (+3 scrapees)
```

## 💎 Les règles d'agrégation, et pourquoi chacune

### 1. Dédoublonnage sur le lien (articles)

Deux flux reprennent souvent **la même dépêche**. Le lien est la clé métier : on dédoublonne
**avant** l'insertion, puis `ON CONFLICT (lien) DO NOTHING` sert de second filet pour les
exécutions successives.

### 2. Homogénéisation — l'ISIN comblé par la source qui le possède

L'univers CSV **ne contient pas les ISIN** : mesuré le 01/08, `valeur.isin` était vide sur
**111 lignes**. Le scraping Boursorama, lui, les fournit.

Le pipeline **écrit l'ISIN manquant** dans `valeur` au passage — sans écraser une valeur déjà
connue. C'est l'homogénéisation exigée par C3 : *la source qui possède la donnée comble celle
qui ne l'a pas.*

### 3. Rapprochement inter-sources par table de correspondance

Boursorama emploie `1rPMC`, Yahoo emploie `MC.PA`. **Aucun identifiant commun** au départ —
l'ISIN aurait été la clé naturelle, mais il était absent.

> Premier essai : rapprochement par ISIN → **3 échecs sur 3**. C'est la mesure qui a imposé
> la table de correspondance `SYMBOLES`, pas une intuition d'architecture.

### 4. Arbitrage entre sources concurrentes

Le scraping et yfinance écrivent **dans la même table `cotation`**.
`ON CONFLICT (ticker, date_seance) DO NOTHING` tranche : **l'historique officiel fait foi**,
le scraping ne comble que ce qui manque.

### 5. Suppression des entrées corrompues

| Règle | Motif |
|---|---|
| OHLCV incomplet → rejeté | la base impose `NOT NULL` |
| Symbole hors univers → rejeté | clé étrangère vers `valeur` |
| Article sans lien → rejeté | le lien est la clé d'unicité |

Chaque rejet est **compté et tracé** dans le bilan de l'étape, jamais silencieux.

### 6. L'euro vaut 1 euro

Ligne évidente — mais sans elle, la jointure de valorisation ne trouve **aucun taux** pour
les positions en EUR et retombe sur le `COALESCE`. **Une évidence non écrite est un bug.**

## Structure exigée par C1

Le critère demande « un point de lancement, l'initialisation des dépendances et des
connexions externes, les règles logiques de traitement, la gestion des erreurs et des
exceptions, la fin du traitement et la sauvegarde des résultats ».

Les six sont **repérés par des commentaires `# [n]`** dans le code — un lecteur peut les pointer
sans lire tout le fichier.

## Tolérance aux pannes

**Une étape qui échoue n'interrompt pas les autres** : une panne de la BCE ne doit pas priver
le briefing des actualités. Chaque étape a **sa propre transaction** — un échec en fin de
parcours n'annule pas ce qui a réussi avant.

Testé : `test_une_etape_en_echec_n_emporte_pas_les_autres` ·
`test_la_connexion_est_fermee_meme_en_cas_d_erreur`.

## Mode simulation

`--simulation` affiche ce qui serait écrit sans rien écrire. Vérifié par test : `rollback`
appelé, `commit` jamais.

## Tests

```
C:\Python314\python.exe -m pytest tests/test_ingest.py -q
→ 15 passed
```

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Agrégation** | Réunir des données de plusieurs sources en un jeu unique |
| **Dédoublonnage** | Supprimer les lignes en double sur une clé |
| **Homogénéisation** | Ramener des formats différents à un format commun |
| **ISIN** | Code international à 12 caractères identifiant un titre |
| **`ON CONFLICT DO NOTHING`** | En cas de doublon, ignorer la nouvelle ligne |
| **Transaction** | Un bloc d'écritures validé ou annulé en entier |
| **`commit` / `rollback`** | Valider / annuler une transaction |
| **Mode simulation** (*dry-run*) | Montrer ce qui serait fait, sans le faire |

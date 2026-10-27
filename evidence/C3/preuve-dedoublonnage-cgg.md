# C3 · Preuve — Dédoublonnage : le cas CGG / Viridien

**Compétence** : C3 — *« Développer des règles d'agrégation de données issues de
différentes sources […] la suppression des entrées corrompues […] l'homogénéisation des
formats »*
**Élément de preuve du règlement (p. 53)** : *« un script de pré-traitement des données
(nettoyage, agrégation, **dédoublonnage**, normalisation) »*
**Détecté par** : `bigdata/explorer.py` (analyse exploratoire, 31/07/2026)

## Le constat

L'analyse exploratoire du jeu Parquet a signalé un doublon :

```
[4] DOUBLONS SUR LA CLE (ticker, date)
  Lignes en double    : 5,120
  Cles uniques        : 273,608
  !! VIRI.PA : 5120 lignes, noms = ['CGG BS', 'CGG RGPT']
```

**276 168 lignes chargées, mais seulement 273 608 clés `(ticker, date)` distinctes.**
2 560 lignes sont strictement redondantes — exactement un historique complet en trop.

## L'origine, dans l'univers source

```
$ grep -i "CGG" data/univers-155.csv
CGG BS,VIRI.PA,OK_APRES_CORRECTION,2560,,renommee Viridien (2024)
CGG RGPT,VIRI.PA,OK,2560,2016-07-29,
```

Deux lignes distinctes de l'univers d'Era pointent vers **le même ticker Yahoo Finance** :

| Nom dans l'univers | Signification | Ticker |
|---|---|---|
| **CGG BS** | CGG **bons de souscription** | `VIRI.PA` |
| **CGG RGPT** | CGG après **regroupement** d'actions | `VIRI.PA` |

Ce sont **deux instruments financiers différents de la même société** — CGG, renommée
**Viridien** en 2024. Le portefeuille d'Era les suit séparément parce qu'ils ont été
acquis séparément. Mais Yahoo Finance ne connaît qu'**une seule série de cours** : celle
de l'action Viridien.

Vérification programmatique sur l'univers :

```
lignes OK: 112 | tickers distincts: 111
 DOUBLON VIRI.PA -> ['CGG BS', 'CGG RGPT']
```

## ⚠️ Ce n'est pas un bug — et c'est le point important

`build_parquet.py` a fait exactement ce qu'on lui demandait : il a parcouru les 112 lignes
de statut `OK*` et téléchargé chacune. Le message `112 / 112` était **exact**.

L'erreur n'est ni dans le code ni dans les données de Yahoo : elle est dans
**l'hypothèse implicite** qu'une ligne d'univers = une valeur cotée. Cette hypothèse est
fausse dès qu'un émetteur a plusieurs lignes de cotation — bons de souscription,
regroupements, actions A/B, certificats.

C'est précisément le type d'entrée que C3 appelle « corrompue » : non pas fausse en
elle-même, mais **fausse une fois agrégée**.

## Conséquence si on ne fait rien

| Calcul | Résultat faux | Pourquoi |
|---|---|---|
| Nombre de valeurs en portefeuille | 112 au lieu de 111 | double comptage |
| Poids de Viridien dans le portefeuille | **×2** | deux fois la même série de cours |
| Moyenne de performance de l'univers | biaisée vers Viridien | une valeur pèse double |
| `INSERT` en base avec PK `(ticker, date)` | **échec** | violation de contrainte d'unicité |

Le dernier point est le plus net : **sans dédoublonnage, l'import en base ne passe pas.**

## La règle de traitement retenue

**Dédoublonner sur la clé `(ticker, date)`, en conservant une seule occurrence**, et
séparer l'identité de la société de la cotation :

```python

# 1. Dédoublonnage sur la clé métier
avant = len(df)
df = df.drop_duplicates(subset=["ticker", "date"], keep="first")
print(f"Dédoublonnage : {avant:,} -> {len(df):,} lignes ({avant - len(df):,} retirées)")

# 2. Le nom n'est PAS un attribut de la cotation : il remonte dans une table dédiée

#    valeur(ticker PK, nom_officiel, noms_portefeuille[], statut_qualite)

#    cotation(ticker FK, date, ouverture, haut, bas, cloture, volume, annee)
```

**Pourquoi `keep="first"` et non une moyenne** : les deux lignes portent des cours
**identiques** (c'est la même série Yahoo). Il n'y a rien à arbitrer — ce n'est pas un
conflit de sources, c'est une répétition. Une moyenne donnerait le même résultat en
coûtant un calcul inutile.

**Pourquoi ne pas supprimer « CGG BS » de l'univers** : parce que l'information est vraie
côté portefeuille — Era détient bien deux lignes. C'est la **modélisation** qui doit
porter la relation « plusieurs noms de portefeuille → un ticker », pas un effacement de
donnée.

## Ce que ça prouve pour C3

| Critère C3 | Couverture |
|---|---|
| Identification des entrées corrompues | ✅ détection automatique par `explorer.py`, chiffrée (5 120 lignes) |
| Suppression des entrées corrompues | ✅ règle `drop_duplicates` sur clé métier explicite |
| Homogénéisation des formats | ✅ dates converties en UTC dans `build_parquet.py` (5 places de marché) |
| Documentation des choix | ✅ ce document — cause, effet mesuré, règle, justification du choix |

---

## Addendum du 26/10/2026 : ce que cette preuve démontre, et ce qu'elle ne démontre pas

> Ajout daté. Le texte ci-dessus reste tel qu'il a été écrit ; trois de ses passages disent plus que ce qui a été
> vérifié, et sont précisés ici. Vérifications faites au tag `livrable-E1-v2` et sur `main` le 26/10/2026.

### 1. Le dédoublonnage, et la question de l'instrument

**Correction démontrée : supprimer la répétition des cotations téléchargées.** Dans le fichier d'univers
(`data/univers-155.csv`), les libellés « CGG BS » et « CGG RGPT » sont associés au même ticker, `VIRI.PA`. La série
utilisée par RITA pour ces deux libellés est donc la même, et la collecte la chargeait deux fois : 5 120 lignes pour
2 560 dates. Le dédoublonnage sur le couple (ticker, date) n'en garde qu'une par date (`db/importer.py:127`).

**Ce que cette correction ne démontre pas : que les deux libellés désignent le même instrument.** La section
« L'origine, dans l'univers source » les décrit comme deux instruments différents (bons de souscription ; action après
regroupement). L'entité ALIAS rattache les deux libellés à `VIRI.PA` ; elle ne règle pas cette question.

**Limite métier : l'identité des instruments et leur correspondance avec les séries de prix doivent être fiables avant
toute valorisation.** Constat dans le code : une position est cherchée d'abord par son ticker (`db/importer.py:193`),
puis, à défaut, par son libellé dans `alias_valeur` (`db/importer.py:196`). Une position libellée « CGG BS » serait donc
rattachée à `VIRI.PA` et valorisée au cours de l'action. Aucun contrôle ne l'empêche. Le jeu de démonstration
(`data/positions-exemple.csv`) ne contient aucune ligne CGG : le cas n'est pas exercé.

**Recommandation, non appliquée à cette date** : signaler une telle position comme non prise en charge, ou l'exclure et
la compter parmi les lignes ignorées, plutôt que la valoriser au cours de l'action ; le test s'écrit avant le code.

### 2. La détention

Le paragraphe « Pourquoi ne pas supprimer « CGG BS » de l'univers » (section « La règle de traitement retenue »)
justifie ce choix par une détention. Cette justification est inexacte. Le fichier d'univers est une liste de suivi et ne
constitue pas une preuve de détention. Les positions utilisées en démonstration sont simulées, conformément à la
précision du 10 octobre 2026 consignée dans le registre des traitements (`db/RGPD-registre-des-traitements.md`, § 5,
point 9).

### 3. Les dates en UTC

La ligne « Homogénéisation des formats » de la section « Ce que ça prouve pour C3 » coche « dates converties en UTC dans
`build_parquet.py` ». La conversion existe (`bigdata/build_parquet.py:54`), mais elle n'homogénéisait pas les dates de
séance. L'erreur venait de l'extraction de la date en UTC avant de retrouver le fuseau de la place de cotation : une
séance du 01/08/2016 à Paris devenait le 31/07. La correction préserve la date locale de séance (`sources/marches.py` ;
incident INC-005, `evidence/C21/INC-005-archive-decalee-d-un-jour.md`, § 2, point 1).

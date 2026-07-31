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

## 🎤 Phrase pour l'oral

> « Mon script annonçait 112 valeurs sur 112 — sans erreur. C'est l'analyse exploratoire
> qui a montré que deux lignes de mon univers pointaient vers le même ticker : les bons de
> souscription et le regroupement de CGG, devenue Viridien. Deux instruments, une seule
> série de cours. Le code était juste ; c'est mon hypothèse "une ligne = une valeur" qui
> était fausse. J'ai dédoublonné sur `(ticker, date)` et séparé la société de la cotation
> dans le modèle — sinon Viridien pesait double dans tous mes calculs, et l'import en base
> échouait sur la clé primaire. »

---

*Le cas est réel, issu du portefeuille d'Era, pas d'un jeu de test fabriqué.*

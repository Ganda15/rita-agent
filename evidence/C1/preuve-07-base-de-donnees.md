# C1 · Preuve 7 — Extraction depuis une base de données

**Type de source couvert** : **base de données** — 5ᵉ et dernier type nommé par C1
**Fichier** : `sources/database.py` · **Requêtes** : `db/requetes.sql`
**Date** : 2026-08-01

## Ce que C1 demande précisément

Le référentiel d'activités liste, pour C1 :
- « **Connexion programmatique** (Python, R, etc.) à un système de gestion de base de données »
- « **Exécution programmatique** des requêtes d'extraction de type SQL »

`sources/database.py` fait les deux : il ouvre une connexion `psycopg2` vers PostgreSQL 18 et
exécute les trois requêtes documentées de `db/requetes.sql`.

## Commande

```powershell
Set-Location "D:\KandaWork\RITA_PROJECTita-agent"
C:\Python314\python.exe -X utf8 -m sources.database
```

## Sortie réelle

```
INFO Requete portefeuille : 7 ligne(s)
INFO Requete mouvements : 5 ligne(s)
INFO Requete volumes_anormaux : 4 ligne(s)

=== R1 · PORTEFEUILLE VALORISE (converti en EUR) ===
Ticker    Nom                       Qte       PRU     Cours    Valo EUR    Perf %
---------------------------------------------------------------------------------
BNP.PA    BNP PARIBAS                15     57.15    106.46    1,596.90     86.28
SU.PA     SCHNEIDER ELECTRIC         10    181.90    257.50    2,575.00     41.56
AI.PA     AIR LIQUIDE                40    158.25    171.58    6,863.20      8.42
OR.PA     OREAL(L')                   8    415.10    382.25    3,058.00     -7.91
SAN.PA    SANOFI                     25     89.60     79.92    1,998.00    -10.80
MC.PA     LVMH MOET VUITTON          12    632.40    466.80    5,601.60    -26.19
---------------------------------------------------------------------------------
TOTAL                                               31,160.70 EUR
```

**Extraction depuis une base réelle**, alimentée par 273 608 cotations importées.

## Ce que cette source apporte de différent

Les cinq autres sources **collectent** de la donnée brute. Celle-ci **la relit après
traitement** : dédoublonnée, normalisée en UTC, contrôlée par 9 contraintes `CHECK`, et
convertie en euros par jointure sur les taux BCE.

C'est la seule source dont la sortie est **directement exploitable par le Rédacteur** sans
retraitement.

## Le total qui a enfin un sens

`sources/positions.py` refusait d'additionner EUR et USD et signalait :
*« Plusieurs devises : ce total n'a pas de sens tel quel. »*

Ici, la conversion est faite **en SQL**, par jointure sur `taux_change` :

```sql
ROUND(p.quantite * d.cloture / COALESCE(t.valeur_pour_eur, 1), 2) AS valorisation_eur
```

→ **31 160,70 EUR** est un nombre additionnable. C'est le point où les sources
`positions.py` (le portefeuille), `ecb.py` (les taux) et la base se rejoignent.

## Sécurité

Tous les paramètres sont **liés** (`%(limite)s`), jamais interpolés en f-string — c'est ce
qui empêche l'injection SQL. Vérifié par test : le SQL envoyé contient le marqueur, **pas**
la valeur.

## Tests

```
C:\Python314\python.exe -m pytest tests/test_database.py -q
→ 15 passed
```

Connexion simulée : aucun test ne nécessite une base.

## Couverture C1 — complète

| Type nommé par C1 | Source | État |
|---|---|---|
| **service web** | yfinance · ECB | ✅ |
| **page web (scraping)** | Boursorama | ✅ |
| **fichier de données** | CSV positions | ✅ |
| **base de données** | **PostgreSQL via `database.py`** | ✅ |
| **système big data** | Parquet partitionné | 🔶 étape 1/4 |

**5 types sur 5 sont touchés**, dont 4 pleinement aboutis.

## 🎤 Phrase pour l'oral

> « Cette source est la seule qui relit de la donnée déjà traitée. Les cinq autres
> collectent du brut ; celle-ci rend un portefeuille dédoublonné, normalisé en UTC, contrôlé
> par neuf contraintes et converti en euros. C'est ce qui fait que mon total de 31 160 euros
> est un nombre qu'on peut additionner — alors que le même calcul sur le CSV brut mélangeait
> des euros et des dollars. »

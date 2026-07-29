# C1 · Preuve 3 — Extraction depuis un service web (BCE / ECB Data Portal)

**Type de source couvert** : service web (API REST)
**Fichier** : `sources/ecb.py`
**Date d'exécution** : 2026-07-29, 19:13:37
**Clé d'API** : aucune — l'API SDMX de la Banque centrale européenne est publique

## Ce que fait le script

`fetch_taux_change(devise)` interroge le *ECB Data Portal* et retourne le dernier taux de change
de référence publié pour la paire `<devise>/EUR`.

## Commande

```powershell
Set-Location "D:\KandaWork\RITA_PROJECT\rita-agent"
C:\Python314\python.exe -c "from sources.ecb import fetch_taux_change; print(fetch_taux_change('USD'))"
```

## Sortie réelle (non simulée)

```
Execute le 2026-07-29T19:13:37
  {'devise': 'USD', 'date': '2026-07-29', 'valeur': 1.138}
  {'devise': 'GBP', 'date': '2026-07-29', 'valeur': 0.85635}
  {'devise': 'CHF', 'date': '2026-07-29', 'valeur': 0.9332}
  {'devise': 'JPY', 'date': '2026-07-29', 'valeur': 186.27}
```

Taux du jour même, source officielle. 1 EUR = 1,138 USD.

## Pourquoi cette source compte pour RITA

L'univers d'Era contient des valeurs cotées en **USD** (Apple, Microsoft, Nvidia,
Schlumberger…) et en **EUR** (Euronext Paris, Xetra, Bruxelles). Sans taux de change, la
valorisation d'un portefeuille mixte est fausse.

C'est aussi un intrant direct pour l'**agent Fondamentaux** : le contexte macro d'une valeur
exportatrice dépend du niveau de l'euro.

## Une méthode à signaler : la structure a été **vérifiée**, pas supposée

Le plan 5.2 signalait explicitement un risque :

> ⚠️ *« La structure JSON de l'API SDMX de la BCE est vérifiée sur la documentation officielle,
> pas testée en direct ici. Si le premier appel réel lève une KeyError, imprimer
> `reponse.json()` pour ajuster le chemin d'accès. »*

Avant d'écrire une ligne de code, l'API a été **sondée en direct** :

```
Cles racine  : ['header', 'dataSets', 'structure']
Cle de serie : ['0:0:0:0:0']
Observations : {'0': [1.138, 0, 0, None, None]}
Dimension    : TIME_PERIOD -> [{'id': '2026-07-29', ...}]
```

L'hypothèse s'est révélée correcte — mais elle a été **confirmée avant** d'être codée, pas
après. C'est ce qui distingue un chemin d'accès documenté d'un chemin d'accès deviné.

## Tests automatisés

`tests/test_ecb.py` — 4 tests, appels réseau simulés (reproductibles, gratuits, hors ligne) :

| Test | Ce qu'il vérifie |
|---|---|
| `test_retourne_devise_date_et_valeur` | les 3 champs, correctement typés |
| `test_devise_par_defaut_est_usd` | USD par défaut |
| `test_autre_devise_construit_la_bonne_url` | `D.GBP.EUR.SP00.A` — la devise est bien injectée |
| `test_structure_inattendue_leve_une_erreur_explicite` | si la BCE change son format, l'erreur est franche, pas silencieuse |

```
C:\Python314\python.exe -m pytest tests/test_ecb.py -v
→ 4 passed
```

## Choix et limites

| | |
|---|---|
| **Choix** | API SDMX officielle de la BCE |
| **Raison** | source de référence, gratuite, sans clé, sans quota — la donnée fait autorité |
| **Alternative écartée** | agrégateurs de taux (ExchangeRate-API, Fixer) : clé requise, quota, et données de seconde main |
| **Limite assumée** | un seul taux par jour ouvré — pas d'intraday. Sans effet : RITA produit un briefing quotidien (décision D8, temps réel abandonné) |

## Couverture C1 après cette preuve

| Type nommé par C1 | Source | État |
|---|---|---|
| **service web** | yfinance · **ECB** · FRED | ✅ *(2 sur 3 codées)* |
| page web (scraping) | scraper HTML | ⬜ |
| fichier de données | CSV positions · PDF | ⬜ |
| base de données | PostgreSQL relu en SQL | ⬜ → C2 |
| système big data | Parquet partitionné + Spark | 🔶 étape 1/4 |

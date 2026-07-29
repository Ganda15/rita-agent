# C1 · Preuve 1 — Extraction depuis un service web (yfinance / OpenBB)

**Type de source couvert** : service web (API REST)
**Fichier** : `agents/scout.py`
**Date d'exécution de la preuve** : 2026-07-29, 15:19:48

## Ce que fait le script

`collect(ticker)` interroge l'API yfinance pour un code boursier, calcule la variation
journalière à partir des deux dernières clôtures, et renvoie un dictionnaire normalisé.
Les erreurs (ticker inconnu, réseau indisponible, historique insuffisant) sont capturées et
renvoyées dans le champ `error` — le script ne plante jamais, il signale.

## Commande

```powershell
Set-Location "D:\KandaWork\RITA_PROJECT\rita-agent"
C:\Python314\python.exe -c "from agents.scout import collect; print(collect('MC.PA'))"
```

## Sortie réelle (non simulée)

```
Date d'exécution : 2026-07-29T15:19:48
Tickers configurés : 10

{"ticker": "MC.PA",  "price": 468.8,  "change_pct": -0.32, "volume": 304586, "currency": "EUR", "error": ""}
{"ticker": "OR.PA",  "price": 381.5,  "change_pct": -0.37, "volume": 120354, "currency": "EUR", "error": ""}
{"ticker": "SAN.PA", "price": 79.58,  "change_pct":  0.25, "volume": 514123, "currency": "EUR", "error": ""}
```

LVMH, L'Oréal, Sanofi — trois valeurs du CAC 40, données réelles du jour, en euros.

## Preuve que le pipeline complet fonctionne

Cette collecte alimente le graphe LangGraph jusqu'à la génération du briefing :

```powershell
curl.exe -X POST "http://127.0.0.1:8000/briefing?ticker=MC.PA" -H "X-API-Key: dev-key"
```

Sortie du 28/07/2026 :
```json
{"ticker":"MC.PA","price":470.3,"change_pct":0.75,"currency":"EUR",
 "briefing":"L'action MC.PA a clôturé à 470,3 EUR, en hausse de 0,75% sur la séance. Cette
 variation reste faible et traduit une évolution contenue... Ce briefing est fourni à titre
 informatif et ne constitue pas un conseil en investissement."}
```

## Tests automatisés associés

`tests/test_scout.py` — 3 tests, appels réseau simulés (`unittest.mock`) pour être
reproductibles et gratuits :

| Test | Ce qu'il vérifie |
|---|---|
| `test_collect_returns_expected_fields_on_success` | les 6 champs sont présents et typés |
| `test_collect_handles_empty_history` | historique vide → `error: "no data"`, pas de plantage |
| `test_tickers_are_european_pea_eligible` | les 10 tickers finissent par `.PA` (cohérence PEA) |

```
C:\Python314\python.exe -m pytest tests/test_scout.py -v
→ 3 passed
```

Intégration continue : https://github.com/Ganda15/rita-agent/actions/runs/30397596052 (vert)

## Choix et limites

| | |
|---|---|
| **Choix** | yfinance plutôt qu'une API payante |
| **Raison** | gratuit, fiable pour un usage journalier, couverture Euronext Paris complète |
| **Alternative écartée** | Alpha Vantage, Polygon (payants au-delà du free tier très limité) |
| **Limite assumée** | délai d'environ 15 minutes sur les cours — acceptable car RITA produit un briefing quotidien, pas du trading temps réel (décision D8) |

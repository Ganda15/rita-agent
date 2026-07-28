# RITA v2 — Architecture Complète
# Certification RNCP37827 — Développeur en Intelligence Artificielle
# Auteur: Eramalingam GANDAKUMAR | WCS Bootcamp Dev IA Agentique
# Version: 2.0 | Date: Mai 2026

---

## POURQUOI RITA v2 ?

RITA v1 (hackathon Outskill C5, avril 2026) = 3 agents, OpenAI, Gradio.
RITA v2 = 5 agents spécialisés, Claude API, FastAPI + Next.js, déployé en production.

### Ce que les concurrents ont → RITA v2 l'a, GRATUITEMENT

| Fonctionnalité | ai-hedge-fund | Perplexity Finance | RITA v2 |
|---|---|---|---|
| Multi-agents analyse | 18 agents / anglais / terminal | Non | ✅ 5 agents / français / web |
| Analyse fondamentale | ✅ | ✅ ($5/1000 appels) | ✅ yfinance gratuit |
| Analyse technique RSI/MACD | ✅ | ❌ | ✅ pandas-ta gratuit |
| Sentiment actualités | ✅ | Partiel | ✅ RSS français gratuit |
| Perspectives multiples | 12 personas investisseurs | ❌ | ✅ 3 personas français |
| Backtesting | ✅ | ❌ | ✅ pandas basique |
| Déployé sur le web | ❌ terminal seulement | API uniquement | ✅ Render + Vercel |
| En français natif | ❌ | ❌ | ✅ |
| Gratuit utilisateur final | ✅ | ❌ | ✅ ~3€/mois API |
| RGPD / serveurs EU | ❌ | ❌ | ✅ |
| Transparence du prompt | ❌ | ❌ | ✅ |
| Score éco-responsable | ❌ | ❌ | ✅ |
| Open source | ✅ | ❌ | ✅ |

---

## LES 5 AGENTS RITA v2

```
┌─────────────────────────────────────────────────────────────────┐
│                    RITA v2 — Pipeline LangGraph                 │
│                                                                 │
│  [USER REQUEST]                                                 │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────────┐                                               │
│  │  SUPERVISEUR │ ← LangGraph orchestre l'ordre d'exécution     │
│  └──────┬───────┘                                               │
│         │                                                       │
│    ┌────▼────┐   ┌──────────────┐   ┌───────────────┐          │
│    │ SCOUT   │   │ FONDAMENTAUX │   │  TECHNIQUE    │          │
│    │ Agent 1 │   │   Agent 2    │   │   Agent 3     │          │
│    └────┬────┘   └──────┬───────┘   └───────┬───────┘          │
│         │               │                   │                  │
│         └───────────────┼───────────────────┘                  │
│                         │                                       │
│                    ┌────▼────┐                                  │
│                    │SENTIMENT│                                  │
│                    │ Agent 4 │                                  │
│                    └────┬────┘                                  │
│                         │                                       │
│                    ┌────▼────────────────────────┐             │
│                    │  ANALYSTE — Agent 5          │             │
│                    │  3 Personas:                 │             │
│                    │  🔵 Défensif                 │             │
│                    │  🟢 Croissance               │             │
│                    │  🔴 Valeur                   │             │
│                    └────┬────────────────────────┘             │
│                         │                                       │
│                    ┌────▼──────────────┐                        │
│                    │  BRIEFING FINAL   │                        │
│                    │  Français natif   │                        │
│                    │  + Transparence   │                        │
│                    │  + Éco-score      │                        │
│                    └───────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## AGENT 1 — SCOUT (C1, C2, C3)

### Rôle
Collecter toutes les données brutes : cours, historique, actualités.

### Sources de données (toutes gratuites)
```python
# 1. Cours + historique (yfinance)
import yfinance as yf
ticker = yf.Ticker("MC.PA")
hist = ticker.history(period="5y")        # C1: extraction données
info = ticker.fast_info                   # cours temps réel (15min delay)

# 2. Actualités françaises (RSS — feedparser)
FEEDS = {
    "bfm_bourse": "https://www.bfmtv.com/rss/economie/bourse/",
    "google_finance_fr": "https://news.google.com/rss/search?q=bourse+france&hl=fr",
    "les_echos": "https://rss.lesechos.fr/articles/finance",   # NOUVEAU v2
    "boursorama": "https://rss.boursorama.com/actualites",     # NOUVEAU v2
}

# 3. Big Data : PySpark sur Parquet (C1 big data)
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("RITA").getOrCreate()
df = spark.read.parquet("data/historical/*.parquet")  # 1.8M lignes, 5 ans
```

### Nettoyage (C3)
```python
import pandas as pd

def clean_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna()                           # supprime lignes nulles
    df = df[df["Close"] > 0]                   # supprime valeurs corrompues
    df = df[df["Volume"] > 0]                  # supprime jours sans volume
    df.index = pd.to_datetime(df.index)        # homogénéise format date
    df = df[~df.index.duplicated(keep="first")] # supprime doublons
    return df
```

---

## AGENT 2 — FONDAMENTAUX (C7, C8, C10) — NOUVEAU v2

### Rôle
Analyser les données financières fondamentales — inspiré du Fundamentals Agent de ai-hedge-fund, mais gratuit via yfinance.

### Données collectées (équivalent Perplexity Finance, 0€)
```python
import yfinance as yf

def get_fundamentals(ticker_symbol: str) -> dict:
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info

    return {
        # Valorisation
        "pe_ratio": info.get("trailingPE"),          # P/E ratio
        "pb_ratio": info.get("priceToBook"),          # P/Book
        "ps_ratio": info.get("priceToSalesTrailing12Months"),

        # Rentabilité
        "roe": info.get("returnOnEquity"),            # Return on Equity
        "roa": info.get("returnOnAssets"),            # Return on Assets
        "profit_margin": info.get("profitMargins"),

        # Croissance
        "revenue_growth": info.get("revenueGrowth"),
        "earnings_growth": info.get("earningsGrowth"),

        # Dette
        "debt_to_equity": info.get("debtToEquity"),
        "current_ratio": info.get("currentRatio"),

        # Dividende
        "dividend_yield": info.get("dividendYield"),

        # Estimations analystes (NOUVEAU v2 — équivalent Perplexity Finance)
        "analyst_target": info.get("targetMeanPrice"),
        "recommendation": info.get("recommendationMean"),  # 1=Buy, 5=Sell

        # Historique résultats (beats/misses — équivalent Perplexity Finance)
        "earnings_history": ticker.earnings_history.to_dict() if hasattr(ticker, "earnings_history") else {},

        # Transactions insiders (NOUVEAU v2 — équivalent Perplexity Finance)
        "insider_transactions": ticker.insider_transactions.head(5).to_dict() if hasattr(ticker, "insider_transactions") else {},
    }
```

### Ce que ça couvre vs concurrents
```
Perplexity Finance ($5/1000)    RITA v2 (gratuit)
────────────────────────────────────────────────
Quotes/profiles              →  yfinance.info ✅
Annual financials            →  yfinance.financials ✅
Key ratios (P/E, P/B, ROE)   →  yfinance.info ✅
Earnings beat/miss history   →  yfinance.earnings_history ✅
Analyst price targets        →  yfinance.info targetMeanPrice ✅
Insider activity             →  yfinance.insider_transactions ✅
Earnings transcripts         →  ❌ Non disponible gratuitement
```

---

## AGENT 3 — TECHNIQUE (C10) — NOUVEAU v2

### Rôle
Analyser les indicateurs techniques — inspiré du Technical Agent de ai-hedge-fund, mais avec pandas-ta (gratuit, 130+ indicateurs).

### Indicateurs calculés
```python
import pandas_ta as ta
import yfinance as yf

def get_technical_indicators(ticker_symbol: str) -> dict:
    df = yf.download(ticker_symbol, period="6mo", interval="1d")

    # RSI (Relative Strength Index)
    df["RSI"] = ta.rsi(df["Close"], length=14)

    # MACD (Moving Average Convergence Divergence)
    macd = ta.macd(df["Close"])
    df = df.join(macd)

    # Bandes de Bollinger
    bbands = ta.bbands(df["Close"], length=20)
    df = df.join(bbands)

    # Moyennes mobiles
    df["SMA_20"] = ta.sma(df["Close"], length=20)
    df["SMA_50"] = ta.sma(df["Close"], length=50)
    df["EMA_12"] = ta.ema(df["Close"], length=12)

    latest = df.iloc[-1]

    return {
        "rsi": round(latest["RSI"], 2),
        "rsi_signal": "survente" if latest["RSI"] < 30 else "surachat" if latest["RSI"] > 70 else "neutre",
        "macd": round(latest.get("MACD_12_26_9", 0), 4),
        "macd_signal": "haussier" if latest.get("MACD_12_26_9", 0) > latest.get("MACDs_12_26_9", 0) else "baissier",
        "above_sma50": bool(latest["Close"] > latest["SMA_50"]),
        "bollinger_position": "haut" if latest["Close"] > latest.get("BBU_20_2.0", 0) else "bas" if latest["Close"] < latest.get("BBL_20_2.0", 0) else "milieu",
    }
```

---

## AGENT 4 — SENTIMENT (C6, C7) — NOUVEAU v2

### Rôle
Analyser le sentiment des actualités françaises — inspiré du Sentiment Agent de ai-hedge-fund, mais sur sources françaises.

### Pipeline sentiment
```python
import feedparser
import anthropic

client = anthropic.Anthropic()

def analyze_news_sentiment(ticker_name: str) -> dict:
    # 1. Récupérer les actualités en français
    feed = feedparser.parse(
        f"https://news.google.com/rss/search?q={ticker_name}+bourse&hl=fr&gl=FR"
    )
    headlines = [entry.title for entry in feed.entries[:10]]

    if not headlines:
        return {"sentiment": "neutre", "score": 0, "headlines": []}

    # 2. Analyser avec Claude API
    prompt = f"""Analyse le sentiment de ces titres d'actualité financière sur {ticker_name}.
Réponds avec un JSON: {{"sentiment": "positif/négatif/neutre", "score": -1 à 1, "raison": "..."}}

Titres:
{chr(10).join(f"- {h}" for h in headlines)}"""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        result = json.loads(response.content[0].text)
    except:
        result = {"sentiment": "neutre", "score": 0, "raison": "parsing error"}

    result["headlines"] = headlines[:5]
    return result
```

---

## AGENT 5 — ANALYSTE (C9, C10) — AMÉLIORÉ v2

### Rôle
Générer le briefing final en français. NOUVEAU : 3 personas, transparence du prompt, éco-score.

### 3 Personas (différenciateur unique vs ai-hedge-fund)
```
🔵 DÉFENSIF   → "Prudence, préservation du capital"
               Analyse risques, dette, dividendes stables
               Public: investisseur conservateur

🟢 CROISSANCE → "Opportunités long terme"
               Analyse revenue growth, innovation, secteur
               Public: investisseur 5-10 ans horizon

🔴 VALEUR     → "Prix vs valeur intrinsèque"
               Analyse P/E vs secteur, décote, marge de sécurité
               Public: investisseur value (style Buffett)
```

### Code Agent Analyste
```python
import anthropic
import json
import time

client = anthropic.Anthropic()

PERSONAS = {
    "defensif": {
        "nom": "Analyste Défensif",
        "focus": "risques, dette, dividendes, stabilité",
        "style": "prudent et factuel",
    },
    "croissance": {
        "nom": "Analyste Croissance",
        "focus": "croissance revenus, innovation, avantages concurrentiels",
        "style": "optimiste mais rigoureux",
    },
    "valeur": {
        "nom": "Analyste Valeur",
        "focus": "valorisation, décote, marge de sécurité",
        "style": "méthodique et chiffré",
    },
}

def generate_briefing(
    ticker: str,
    scout_data: dict,
    fundamentals: dict,
    technical: dict,
    sentiment: dict,
    persona: str = "defensif",
) -> dict:

    p = PERSONAS[persona]

    # ─────────────────────────────────────────────
    # CONSTRUCTION DU PROMPT (visible pour transparence)
    # ─────────────────────────────────────────────
    prompt = f"""Tu es {p['nom']} de RITA, assistant financier en français.
Style: {p['style']}
Focus: {p['focus']}

DONNÉES POUR {ticker}:

COURS: {scout_data.get('price')}€ | Variation: {scout_data.get('change_pct')}%
VOLUME: {scout_data.get('volume')} | vs moyenne: {scout_data.get('volume_ratio')}x

FONDAMENTAUX:
- P/E: {fundamentals.get('pe_ratio')} | P/B: {fundamentals.get('pb_ratio')}
- ROE: {fundamentals.get('roe')} | Croissance revenus: {fundamentals.get('revenue_growth')}
- Cible analystes: {fundamentals.get('analyst_target')}€
- Recommandation: {fundamentals.get('recommendation')}/5

TECHNIQUE:
- RSI: {technical.get('rsi')} ({technical.get('rsi_signal')})
- MACD: {technical.get('macd_signal')}
- Position vs SMA50: {'AU-DESSUS' if technical.get('above_sma50') else 'EN-DESSOUS'}

SENTIMENT ACTUALITÉS: {sentiment.get('sentiment')} (score: {sentiment.get('score')})
Titres récents: {', '.join(sentiment.get('headlines', [])[:3])}

INSTRUCTIONS:
1. Résumé en 3 phrases maximum
2. Signal: POSITIF / NÉGATIF / NEUTRE
3. Point de vigilance spécifique
4. Définition du jour: explique UN terme financier utilisé (2 phrases simples)

Format JSON strict:
{{
  "resume": "...",
  "signal": "POSITIF|NÉGATIF|NEUTRE",
  "vigilance": "...",
  "definition_du_jour": {{"terme": "...", "explication": "..."}}
}}"""

    # ─────────────────────────────────────────────
    # APPEL CLAUDE API + MÉTRIQUES TRANSPARENCE
    # ─────────────────────────────────────────────
    start_time = time.time()

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    duration_ms = int((time.time() - start_time) * 1000)
    input_tokens = response.usage.input_tokens
    output_tokens = response.usage.output_tokens

    # Calcul coût (tarif claude-opus-4-6)
    cost_eur = (input_tokens * 0.015 + output_tokens * 0.075) / 1000

    # Calcul éco-score (estimation CO2)
    # Source: ~0.5g CO2 par 1000 tokens (estimation datacenter)
    co2_grams = (input_tokens + output_tokens) * 0.0005

    # ─────────────────────────────────────────────
    # RÉSULTAT AVEC TRANSPARENCE COMPLÈTE
    # ─────────────────────────────────────────────
    try:
        briefing_content = json.loads(response.content[0].text)
    except json.JSONDecodeError:
        briefing_content = {
            "resume": response.content[0].text,
            "signal": "NEUTRE",
            "vigilance": "Erreur de parsing JSON",
            "definition_du_jour": {"terme": "", "explication": ""}
        }

    return {
        "ticker": ticker,
        "persona": persona,
        "briefing": briefing_content,
        # TRANSPARENCE (inspiré leçon Simplon PDF)
        "transparence": {
            "prompt_utilise": prompt,          # prompt visible
            "tokens_entree": input_tokens,
            "tokens_sortie": output_tokens,
            "cout_eur": round(cost_eur, 5),    # coût affiché
            "duree_ms": duration_ms,
            "co2_grammes": round(co2_grams, 4), # éco-score affiché
        }
    }
```

---

## BACKTESTING SIMPLE — NOUVEAU v2

*(inspiré de ai-hedge-fund, version simplifiée)*

```python
import pandas as pd
import yfinance as yf

def simple_backtest(
    ticker_symbol: str,
    initial_capital: float = 10000.0,
    period: str = "1y"
) -> dict:
    """
    Backtest simple basé sur signal RSI:
    - Achat si RSI < 30 (survente)
    - Vente si RSI > 70 (surachat)
    INFORMATIF SEULEMENT — pas un conseil d'investissement
    """
    import pandas_ta as ta

    df = yf.download(ticker_symbol, period=period)
    df["RSI"] = ta.rsi(df["Close"], length=14)
    df = df.dropna()

    capital = initial_capital
    position = 0
    trades = []

    for i, row in df.iterrows():
        if row["RSI"] < 30 and position == 0:
            # Signal achat
            position = capital / row["Close"]
            capital = 0
            trades.append({"date": str(i.date()), "action": "ACHAT", "prix": round(row["Close"], 2)})

        elif row["RSI"] > 70 and position > 0:
            # Signal vente
            capital = position * row["Close"]
            position = 0
            trades.append({"date": str(i.date()), "action": "VENTE", "prix": round(row["Close"], 2)})

    # Valeur finale
    final_value = capital + (position * df["Close"].iloc[-1] if position > 0 else 0)
    performance = round(((final_value - initial_capital) / initial_capital) * 100, 2)

    # Comparaison Buy & Hold
    buy_hold = round(((df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0]) * 100, 2)

    return {
        "ticker": ticker_symbol,
        "periode": period,
        "capital_initial": initial_capital,
        "capital_final": round(final_value, 2),
        "performance_pct": performance,
        "buy_hold_pct": buy_hold,
        "nb_trades": len(trades),
        "trades": trades[-5:],  # 5 derniers trades
        "disclaimer": "INFORMATIF SEULEMENT. Pas un conseil d'investissement."
    }
```

---

## STACK TECHNIQUE COMPLÈTE

```
COUCHE          OUTIL                   POURQUOI
──────────────────────────────────────────────────────────────
Orchestration   LangGraph               Multi-agent, StateGraph
LLM             Claude API (claude-     Meilleur modèle, adaptatif
                opus-4-6)
Données         yfinance + pandas-ta    Gratuit, 130+ indicateurs
                + feedparser (RSS)
Big Data        PySpark + Parquet       C1 big data obligatoire
Base données    PostgreSQL (Render)     MERISE MCD/MPD (C4)
Vector DB       LanceDB                 RAG historique briefings
API Backend     FastAPI (Render)        C5, C9 — REST + auth
Frontend        Next.js (Vercel)        C17 — dashboard TypeScript
Tests           pytest (8 tests min)    C12 — couverture ≥ 60%
CI/CD           GitHub Actions          C13, C18, C19
Monitoring      Prometheus + Grafana    C11, C20 — métriques RED
Traces LLM      LangSmith               C11 — traces agents
Logs            structlog JSON          C20 — logs anonymisés RGPD
Erreurs         Sentry EU               C21 — incidents + RGPD
Sécurité        bcrypt + JWT + slowapi  C17 — OWASP API Top 10
```

---

## DIFFÉRENCIATEURS UNIQUES — Ce que PERSONNE ne fait

```
1. FRANÇAIS NATIF
   → 3 personas analystes en français
   → "Définition du jour" pédagogique
   → RSS sources françaises (BFM, Les Echos, Boursorama)

2. GRATUIT ET OPEN SOURCE
   → ai-hedge-fund: gratuit mais non déployé
   → Perplexity Finance: $5/1000 appels API
   → RITA: ~3€/mois total, code public GitHub

3. TRANSPARENT (inspiré leçon Simplon)
   → Prompt visible dans l'interface
   → Tokens + coût affiché après chaque briefing
   → Score confiance 1-5

4. ÉCO-RESPONSABLE (inspiré leçon Simplon)
   → CO2 estimé par briefing affiché
   → Objectif mensuel carbone pour l'utilisateur
   → Éco-index Grade B (C17)

5. DÉPLOYÉ SUR LE WEB
   → ai-hedge-fund: terminal local uniquement
   → RITA: Render (backend) + Vercel (frontend)
   → Accessible depuis navigateur, mobile, tablette

6. RGPD CONFORME
   → Sentry EU (données en Allemagne)
   → Logs anonymisés (user_id, pas email)
   → Droit à l'effacement implémenté
   → Registre des traitements CNIL
```

---

## MAPPING COMPÉTENCES CERTIFICATION C1-C21

```
Agent Scout          → C1 (scraping yfinance + RSS)
                     → C2 (SQL PostgreSQL)
                     → C3 (nettoyage + normalisation)
                     → C4 (MERISE MCD/MPD PostgreSQL)
                     → C5 (API REST /data)

Agent Fondamentaux   → C7 (benchmark services IA)
Agent Technique      → C8 (paramétrer service IA)
Agent Sentiment      → C6 (veille technique + réglementaire)

FastAPI /briefing    → C9 (API exposant modèle IA)
Next.js Dashboard    → C10 (intégration API dans application)
Prometheus + Grafana → C11 (monitoring modèle IA)
pytest (8 tests)     → C12 (tests automatisés)
GitHub Actions       → C13 (CI/CD MLOps)

User stories WCAG    → C14 (spécifications fonctionnelles)
Architecture LangGraph → C15 (cadre technique)
Sprints + Kanban     → C16 (coordination agile)
Next.js + OWASP      → C17 (composants + interfaces)
GitHub Actions CI    → C18 (automatisation tests)
Docker + CD          → C19 (livraison continue)

Sentry + Grafana     → C20 (surveillance application)
INC-001 postmortem   → C21 (résolution incidents)
```

---

## STRUCTURE DU REPO GITHUB

```
rita-agent-certif/
├── CLAUDE.md
├── .env                    # jamais commité
├── .venv/
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
│
├── main.py                 # FastAPI entry point
├── config.py               # settings + constantes
│
├── agents/
│   ├── __init__.py
│   ├── scout.py            # Agent 1 — données
│   ├── fondamentaux.py     # Agent 2 — NOUVEAU v2
│   ├── technique.py        # Agent 3 — NOUVEAU v2
│   ├── sentiment.py        # Agent 4 — NOUVEAU v2
│   └── analyste.py         # Agent 5 — 3 personas
│
├── tools/
│   ├── yahoo_finance.py    # yfinance wrapper
│   ├── news_fetcher.py     # RSS multi-sources FR
│   ├── technical.py        # pandas-ta wrapper
│   └── backtesting.py      # backtest simple — NOUVEAU v2
│
├── rag/
│   ├── ingest.py
│   └── retriever.py
│
├── api/
│   ├── routes/
│   │   ├── auth.py         # JWT + bcrypt
│   │   ├── data.py         # /data/{ticker}
│   │   ├── briefing.py     # /briefing
│   │   └── health.py       # /health + /metrics
│   └── models.py           # Pydantic schemas
│
├── frontend/               # Next.js (séparé ou monorepo)
│   └── ...
│
├── tests/
│   ├── conftest.py
│   ├── test_scout.py
│   ├── test_fondamentaux.py
│   ├── test_technique.py
│   ├── test_sentiment.py
│   ├── test_analyste.py
│   ├── test_api.py
│   └── test_backtesting.py
│
├── evidence/               # preuves certification
│   ├── screenshots/
│   ├── logs/
│   └── postmortem/
│       └── INC-001.md
│
└── docs/
    ├── RITA-V2-ARCHITECTURE.md  ← ce fichier
    ├── RITA-V2-DIFFERENTIATORS.md
    ├── MERISE-MCD.md
    └── RAPPORT-E1-DONNEES.md
```

---

## REQUIREMENTS.TXT v2

```
# Core
anthropic>=0.25.0           # Claude API — PAS openai
langgraph>=0.2.0
langchain>=0.2.0
langsmith>=0.1.0

# Data
yfinance>=0.2.40
pandas-ta>=0.3.14b          # 130+ indicateurs techniques GRATUITS
feedparser>=6.0.11
pyspark>=3.5.0              # big data C1

# Storage
lancedb>=0.6.0
llama-index>=0.10.0
llama-index-vector-stores-lancedb>=0.1.0
asyncpg>=0.29.0             # PostgreSQL async
sqlalchemy>=2.0.0

# API
fastapi>=0.111.0
uvicorn>=0.30.0
pydantic>=2.7.0
python-jose[cryptography]   # JWT
bcrypt>=4.1.0
slowapi>=0.1.9              # rate limiting

# Monitoring
prometheus-client>=0.20.0
structlog>=24.1.0
sentry-sdk>=2.0.0

# Tests
pytest>=8.2.0
pytest-cov>=5.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0

# Utils
python-dotenv>=1.0.0
```

---

## PHRASE FINALE POUR LE JURY

> "RITA v2 n'est pas un clone de ai-hedge-fund ou de Perplexity Finance.
> C'est ce qu'ils auraient dû construire pour l'investisseur particulier
> francophone : 5 agents spécialisés, données équivalentes à un outil
> professionnel, entièrement gratuit grâce à yfinance + pandas-ta,
> déployé sur le web, en français, RGPD conforme, et transparent sur
> ce qu'il consomme en coût et en carbone.
> C'est le vide du marché français FinAI que RITA remplit."

---

*RITA v2 — Architecture Document*
*Eramalingam GANDAKUMAR | WCS Bootcamp Dev IA Agentique | Mai 2026*
*Certification RNCP37827 — Développeur en Intelligence Artificielle*

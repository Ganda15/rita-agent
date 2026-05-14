# RITA — Agent IA Financier

**Certification RNCP37827 — Développeur en Intelligence Artificielle**
Wild Code School | Era Ramalingam Gandakumar | 2026

---

## Concept

RITA collecte chaque matin les données boursières de 20 tickers, les analyse avec Claude (Anthropic), et génère un briefing lisible dans un dashboard web.

## Couverture certification

| Épreuve | Contenu | Compétences |
|---------|---------|-------------|
| E1 | Collecte données (yfinance + CSV + PostgreSQL + PySpark) | C1–C5 |
| E2 | Benchmark services IA → choix Claude | C6–C8 |
| E3 | API FastAPI + Claude API + tests pytest + CI/CD | C9–C13 |
| E4 | Dashboard Next.js | C14–C19 |
| E5 | Monitoring Prometheus + incidents | C20–C21 |

## Stack

- **Backend** : Python 3.12, FastAPI, LangGraph, Anthropic SDK
- **Base de données** : PostgreSQL, PySpark/Parquet
- **Frontend** : Next.js (React)
- **CI/CD** : GitHub Actions, Docker, Render, Vercel
- **Monitoring** : Prometheus, Grafana, LangSmith

## Structure

```
rita-agent-certif/
├── agents/          # Scout + Analyst (LangGraph)
├── api/             # FastAPI routes
├── data/            # Données brutes et Parquet
├── docs/
│   ├── veille/      # Fiches veille hebdomadaires
│   └── rapports/    # Rapports E1–E5
├── evidence/        # Screenshots, logs, preuves jury
├── frontend/        # Next.js dashboard
├── pipelines/       # Ingestion, transformation
└── tests/           # pytest
```

## Lancer le projet

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env  # ajouter les clés API
.venv/bin/uvicorn api.main:app --reload --reload-dir .
```

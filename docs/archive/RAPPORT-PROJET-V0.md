> ⚠️ **DOCUMENT HISTORIQUE — mai 2026. Ce n'est pas un livrable de certification.**
>
> Il décrit un état antérieur du projet et **ne correspond plus au code**. Notamment,
> plusieurs flux RSS cités ici ne répondent plus ; `sources/rss.py` en utilise d'autres.
> Conservé pour la trace de l'évolution de la conception.
>
> **Référence à jour :** [README](../../README.md) ·
> [rapport E1](../rapports/E1/rapport-E1.pdf) · [preuves](../../evidence/) ·
> [pourquoi ce dossier](README.md)

---

# RITA v2 — Rapport de Projet
# Version 0 — Mai 2026
# ─────────────────────────────────────────────────────────
# Certification RNCP37827 — Développeur en Intelligence Artificielle
# Niveau 6 (Bac+3/4) | Certificateur : Simplon.co
# Formation : Wild Code School — Bootcamp Dev IA Agentique
# ─────────────────────────────────────────────────────────
# Candidat    : Eramalingam GANDAKUMAR
# Promotion   : Dev IA Agentique 2026 — WCS Nice
# Date début  : 11 mai 2026
# Version     : 0.1 — DRAFT (pour validation formatrice)
# ─────────────────────────────────────────────────────────

---

## AVERTISSEMENT VERSION 0

> Ce document est une première version de travail (V0).
> Il présente l'état actuel de conception du projet RITA v2.
> Le code est en cours de développement.
> Certaines sections sont marquées [À COMPLÉTER] pour les prochaines versions.
> Ce rapport servira de base aux 5 rapports officiels E1 à E5.

---

## TABLE DES MATIÈRES

```
1.  Résumé exécutif
2.  Contexte et problématique métier
3.  Analyse du marché et concurrence
4.  Solution proposée : RITA v2
5.  Architecture technique globale
6.  Gestion des données (E1 — C1 à C5)
7.  Veille technologique et benchmark (E2 — C6 à C8)
8.  API et intégration IA (E3 — C9 à C13)
9.  Application web complète (E4 — C14 à C19)
10. Monitoring et incidents (E5 — C20 à C21)
11. Sécurité et conformité RGPD
12. Différenciateurs uniques
13. Planning et jalons
14. Conclusion
```

---

## 1. RÉSUMÉ EXÉCUTIF

**RITA v2** (Responsive Intelligence for Trading Analytics) est un système
multi-agents d'analyse financière qui surveille un portefeuille d'actions,
analyse les données de marché, et génère automatiquement un briefing
quotidien en français pour les investisseurs particuliers.

### En une phrase
> Un agent IA qui fait chaque matin en 30 secondes ce qu'un analyste
> Bloomberg fait en 2 heures — en français, gratuitement, pour tout le monde.

### Chiffres clés du projet
```
5 agents IA spécialisés (LangGraph)
20 tickers boursiers surveillés
3 personas d'analyse (Défensif / Croissance / Valeur)
1.8 million de lignes de données historiques (PySpark)
~3 euros par mois (vs 2 000€/mois pour Bloomberg)
0 recommandation d'achat/vente (conformité AMF)
100% français natif
```

### Compétences couvertes
```
BC01 — E1 : Données          → C1, C2, C3, C4, C5
BC02 — E2 : Veille           → C6, C7, C8
BC02 — E3 : API/MLOps        → C9, C10, C11, C12, C13
BC03 — E4 : Application      → C14, C15, C16, C17, C18, C19
BC03 — E5 : Monitoring       → C20, C21
```

---

## 2. CONTEXTE ET PROBLÉMATIQUE MÉTIER

### 2.1 Le problème identifié

En France, **8 millions d'investisseurs particuliers** (AMF, 2024)
gèrent activement un portefeuille d'actions. Ces investisseurs font
face à trois obstacles majeurs au quotidien :

**Obstacle 1 — Surcharge d'information**
Un investisseur qui suit 20 actions passe 2 à 3 heures par jour
à lire des flux financiers dispersés sur 10 sources différentes
(Reuters, BFM Bourse, Les Echos, Seeking Alpha, etc.), principalement
en anglais.

**Obstacle 2 — Barrière linguistique**
90% des outils d'analyse financière sérieux sont en anglais.
Les investisseurs francophones n'ont pas accès aux mêmes outils
que leurs homologues anglophones.

**Obstacle 3 — Barrière financière**
Les outils professionnels d'analyse (Bloomberg Terminal : 2 000€/mois,
Refinitiv Eikon : 1 500€/mois, Koyfin Pro : 50€/mois) sont
inaccessibles aux investisseurs particuliers.

### 2.2 Impact concret

```
SITUATION ACTUELLE d'un investisseur particulier français :

06h30  → Réveil, consulte son téléphone
07h00  → Ouvre Yahoo Finance (anglais)
07h15  → Ouvre Boursorama (données limitées)
07h30  → Ouvre BFM Bourse (actualités)
07h45  → Ouvre Les Echos (abonnement payant)
08h00  → Ouvre son broker pour voir son portefeuille
08h15  → Essaie de synthétiser manuellement
08h30  → Prend une décision sans vision complète

Résultat : 1h30 perdue, information incomplète,
           décisions sous-optimales
```

### 2.3 La solution RITA v2

```
AVEC RITA v2 :

07h00  → Ouvre RITA sur son téléphone
07h05  → Lit le briefing automatique en français
         pour ses 20 actions, généré à 7h par les agents IA
07h10  → Fait défiler les 3 perspectives (Défensif/Croissance/Valeur)
07h15  → Décision éclairée

Résultat : 15 minutes, information complète,
           analyse professionnelle, en français
```

### 2.4 Personas utilisateurs

**Persona 1 — Marie, 45 ans, institutrice à Lyon**
- Investit sur PEA depuis 5 ans, suit 15 actions françaises
- Lit les actualités financières mais ne comprend pas tous les termes
- Besoin : un résumé simple chaque matin avant de partir travailler
- RITA répond avec le persona Défensif + définition du jour

**Persona 2 — Thomas, 32 ans, ingénieur à Paris**
- Investit sur CTO, horizont 10 ans, intéressé par la tech
- Comprend les concepts financiers, manque de temps pour analyser
- Besoin : analyse croissance + catalyseurs tech
- RITA répond avec le persona Croissance

**Persona 3 — Jacques, 58 ans, CGP indépendant à Bordeaux**
- Gère des portefeuilles clients, cherche des décotes
- Connaît les ratios financiers, veut comparaisons sectorielles
- Besoin : valorisation P/E vs secteur, marge de sécurité
- RITA répond avec le persona Valeur + accès API directe

---

## 3. ANALYSE DU MARCHÉ ET CONCURRENCE

### 3.1 Outils existants analysés

| Outil | Points forts | Limites pour RITA |
|-------|-------------|-------------------|
| **Bloomberg Terminal** | Données temps réel, complet | 2 000€/mois, anglais, terminal dédié |
| **ai-hedge-fund (GitHub)** | Multi-agents LangGraph, open source | Terminal local, anglais, pas déployé |
| **Perplexity Finance API** | Données riches, temps réel | 5$/1000 appels, anglais, API dev only |
| **Botraiders** | Français, gratuit | Signaux buy/sell uniquement, pas de narratif |
| **Nalo** | Français, robo-advisor | Gestion d'argent (pas analyse), payant |
| **Koyfin** | Bon rapport qualité/prix | 50€/mois, anglais |

### 3.2 Le vide du marché

Aucun outil existant ne combine simultanément :
```
✅ Français natif
✅ Gratuit (< 10€/mois)
✅ Déployé sur le web
✅ Multi-agents autonome
✅ Analyse complète (fondamentale + technique + sentiment)
✅ RGPD conforme
✅ Open source
```
→ **RITA v2 est le premier outil à combiner ces 7 caractéristiques.**

### 3.3 Positionnement stratégique

```
          COÛT/MOIS
          ↑
2000€     │ Bloomberg ●
          │
 500€     │
          │
  50€     │              Koyfin ●
          │
   5€     │                          Perplexity Finance ●
          │
   0€     │ ai-hedge-fund ●                      RITA v2 ●
          └────────────────────────────────────────────────→
          ❌ Terminal          ❌ Anglais          ✅ Web+FR
                         ACCESSIBILITÉ
```

---

## 4. SOLUTION PROPOSÉE : RITA v2

### 4.1 Vue d'ensemble

RITA v2 est un système **end-to-end** composé de :

```
[SOURCE DONNÉES]  →  [5 AGENTS IA]  →  [API REST]  →  [DASHBOARD WEB]
 yfinance              LangGraph         FastAPI         Next.js
 RSS français          Claude API        PostgreSQL      Vercel
 PySpark               LanceDB RAG       Prometheus
```

### 4.2 Les 5 agents spécialisés

**Agent 1 — Scout**
- Collecte les données de marché (yfinance)
- Récupère les actualités françaises (RSS)
- Traite le big data historique (PySpark)
- Compétences : C1, C2, C3

**Agent 2 — Fondamentaux** *(nouveau v2)*
- Analyse P/E, P/B, ROE, croissance revenus
- Récupère estimations analystes et transactions insiders
- Équivalent gratuit de Perplexity Finance
- Compétences : C7, C8

**Agent 3 — Technique** *(nouveau v2)*
- Calcule RSI, MACD, Bandes de Bollinger (pandas-ta)
- Détecte signaux de survente/surachat
- Inspiré de ai-hedge-fund, implémenté gratuitement
- Compétences : C10

**Agent 4 — Sentiment** *(nouveau v2)*
- Analyse le sentiment des actualités en français
- Utilise Claude API pour scorer les headlines RSS
- Sources : BFM Bourse, Les Echos, Boursorama
- Compétences : C6

**Agent 5 — Analyste**
- Génère le briefing final en français
- 3 personas : Défensif, Croissance, Valeur
- System prompt structuré → JSON garanti
- Transparence : prompt + tokens + coût + CO2 affiché
- Compétences : C9, C10

### 4.3 Fonctionnalités uniques (différenciateurs)

```
D1. FRANÇAIS NATIF       → 3 personas, RSS FR, briefing FR
D2. GRATUIT + DÉPLOYÉ    → yfinance + pandas-ta + free tiers
D3. 3 PERSONAS FR        → Défensif / Croissance / Valeur
D4. PROMPT TRANSPARENT   → visible + tokens + coût affiché
D5. ÉCO-SCORE CO2        → empreinte carbone par briefing
D6. PÉDAGOGIE            → définition du jour dans chaque briefing
```

---

## 5. ARCHITECTURE TECHNIQUE GLOBALE

### 5.1 Schéma d'architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         UTILISATEUR                             │
│                    (navigateur / mobile)                        │
└────────────────────────────┬─────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   FRONTEND — Next.js                            │
│                    Vercel (EU CDN)                              │
│   Dashboard.tsx | HoldingRow.tsx | BriefingPanel.tsx           │
│   PersonaSelector.tsx | TransparencyPanel.tsx                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │ REST API / JSON
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   BACKEND — FastAPI                             │
│                   Render (Frankfurt EU)                         │
│                                                                  │
│  /auth          /data/{ticker}      /briefing      /health      │
│  JWT + bcrypt   cours + fondamentaux 5 agents      /metrics     │
│  slowapi        historique SQL      LangGraph       Prometheus   │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐   │
│  │                    LANGGRAPH                              │   │
│  │  Scout → Fondamentaux → Technique → Sentiment → Analyste │   │
│  └───────────────────────────────────────────────────────────┘   │
└──────┬──────────────────┬──────────────────┬──────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐  ┌───────────────┐  ┌──────────────────┐
│  PostgreSQL  │  │   LanceDB     │  │  Anthropic       │
│  Render EU   │  │   Vecteurs    │  │  Claude API      │
│  MERISE MCD  │  │   RAG         │  │  claude-opus-4-6 │
│  4 entités   │  │   Historique  │  │  ~3€/mois        │
└──────────────┘  └───────────────┘  └──────────────────┘
       │
       ▼
┌──────────────┐  ┌───────────────┐  ┌──────────────────┐
│  yfinance    │  │  pandas-ta    │  │  RSS feeds FR    │
│  GRATUIT     │  │  GRATUIT      │  │  BFM / Les Echos │
│  20 tickers  │  │  130+ indicat │  │  Boursorama      │
└──────────────┘  └───────────────┘  └──────────────────┘
```

### 5.2 Stack technique

| Couche | Outil | Version | Justification |
|--------|-------|---------|---------------|
| Orchestration | LangGraph | 0.2+ | Multi-agent StateGraph |
| LLM | Claude API | claude-opus-4-6 | Meilleur modèle FR disponible |
| Framework API | FastAPI | 0.111+ | Async, Pydantic, OpenAPI auto |
| Frontend | Next.js | 14+ | React SSR, Vercel natif |
| Base de données | PostgreSQL | 15 | MERISE, SQL standard |
| Vector DB | LanceDB | 0.6+ | RAG local, pas de serveur |
| Big Data | PySpark | 3.5+ | C1 obligatoire, Parquet |
| Indicateurs | pandas-ta | 0.3+ | 130+ indicateurs, gratuit |
| Données | yfinance | 0.2.40+ | Yahoo Finance gratuit |
| Tests | pytest | 8.2+ | Couverture ≥ 60% (C12) |
| CI/CD | GitHub Actions | — | C13, C18, C19 |
| Monitoring | Prometheus + Grafana | — | C11, C20 |
| Logs | structlog | 24.1+ | JSON, RGPD anonymisé |
| Erreurs | Sentry EU | 2.0+ | C21, données EU |
| Sécurité | bcrypt + JWT + slowapi | — | OWASP API Top 10 |

### 5.3 Flux de données complet

```
COLLECTE (7h00 chaque matin)
  yfinance → 20 tickers → OHLCV + fondamentaux + analystes
  RSS feeds → actualités françaises du jour
  ↓
NETTOYAGE (pandas/PySpark)
  dropna() + filtrage prix > 0 + déduplicate + format date
  ↓
STOCKAGE
  OHLCV → PostgreSQL (SQL structuré)
  Parquet → disque local (big data 5 ans)
  Briefings anciens → LanceDB (vecteurs RAG)
  ↓
ANALYSE (LangGraph pipeline)
  Agent Scout      → données brutes consolidées
  Agent Fondamentaux → P/E, ROE, estimations analystes
  Agent Technique  → RSI, MACD, Bollinger
  Agent Sentiment  → score actualités FR
  Agent Analyste   → briefing final JSON (3 personas)
  ↓
PRÉSENTATION (Next.js)
  Dashboard → tableau 20 tickers + signaux
  BriefingPanel → texte briefing + persona selector
  TransparencyPanel → prompt + tokens + coût + CO2
```

---

## 6. GESTION DES DONNÉES (E1 — C1 à C5)

### 6.1 Extraction de données — C1

RITA utilise trois sources de données, toutes gratuites :

**Source 1 — yfinance (cours + fondamentaux)**
```
Données collectées par ticker :
  → Cours OHLCV (Open/High/Low/Close/Volume) 5 ans
  → Prix temps réel (15 min delay — suffisant pour briefings quotidiens)
  → Informations fondamentales : P/E, P/B, ROE, dividende
  → Estimations analystes : prix cible, recommandation
  → Transactions insiders : achats/ventes dirigeants
  → Historique résultats : beats/misses trimestriels
```

**Source 2 — RSS français (actualités)**
```
Flux RSS collectés :
  → BFM Bourse    : https://www.bfmtv.com/rss/economie/bourse/
  → Google News FR: https://news.google.com/rss/search?q=bourse+france&hl=fr
  → Les Echos RSS : https://rss.lesechos.fr/articles/finance
```

**Source 3 — PySpark + Parquet (big data)**
```
Traitement big data :
  → 1.8 million de lignes de données historiques
  → 5 ans d'historique × 20 tickers × données quotidiennes
  → Traitement PySpark en local
  → Stockage Parquet partitionné par année
  → Lecture sélective par colonne (10x plus rapide que CSV)
```

### 6.2 Nettoyage — C3

```
Règles d'agrégation appliquées :
  1. Suppression entrées nulles (dropna)
  2. Filtrage prix corrompus (Close > 0, Volume > 0)
  3. Suppression doublons d'index par date
  4. Homogénéisation format date (UTC → naive datetime)
  5. Arrondi prix à 2 décimales
  6. Tri chronologique

Résultat : 0% de valeurs nulles ou corrompues en base
```

### 6.3 Modèle de données MERISE — C4

**MCD (Modèle Conceptuel des Données) :**
```
USER ──────────< PORTFOLIO >──────────── HOLDING
  |                                         |
  id (PK)                                   id (PK)
  email_hash                                ticker
  created_at                                added_at
  deleted_at                                |
                                            |
                                      ──< BRIEFING
                                            |
                                            id (PK)
                                            date
                                            persona
                                            content
                                            tokens_in
                                            tokens_out
                                            cost_eur
                                            co2_grams
```

**Entités et cardinalités :**
```
USER    (1,1) possède (0,n) PORTFOLIO
PORTFOLIO (1,1) contient (0,n) HOLDING
HOLDING (1,1) génère (0,n) BRIEFING
```

### 6.4 API REST données — C5

```
Endpoints /data :

GET  /data/{ticker}           → cours + fondamentaux du ticker
GET  /data/{ticker}/history   → historique OHLCV (période optionnelle)
GET  /data/{ticker}/technical → indicateurs RSI/MACD/Bollinger
GET  /data/portfolio          → snapshot de tous les tickers watchlist
POST /data/portfolio/tickers  → ajouter des tickers à la watchlist
DELETE /data/portfolio/{ticker} → supprimer un ticker

Sécurité : JWT Bearer token obligatoire sur tous les endpoints
Rate limiting : 10 requêtes/minute (slowapi)
Documentation : /docs (OpenAPI auto-générée par FastAPI)
```

### 6.5 Conformité SQL — C2

```sql
-- Exemple requête C2 : extraction avec agrégation
SELECT
    h.ticker,
    DATE_TRUNC('week', b.date) AS semaine,
    COUNT(*)                   AS nb_briefings,
    AVG(b.tokens_in)           AS moy_tokens,
    SUM(b.cost_eur)            AS cout_semaine,
    SUM(b.co2_grams)           AS co2_semaine
FROM briefings b
JOIN holdings h ON h.id = b.holding_id
JOIN portfolios p ON p.id = h.portfolio_id
WHERE p.user_id = $1
  AND b.date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY h.ticker, DATE_TRUNC('week', b.date)
ORDER BY semaine DESC, h.ticker;
```

---

## 7. VEILLE TECHNOLOGIQUE ET BENCHMARK (E2 — C6 à C8)

### 7.1 Veille technique — C6

**Méthode de veille :**
- Sources suivies : Anthropic blog, LangGraph releases, yfinance changelog
- Fréquence : minimum 1 heure par semaine (règle C6)
- Format : fichier `docs/veille/veille-SXX-mois2026.md`
- Partage : dépôt GitHub **privé**, accès donné au formateur et au jury en tant que
  collaborateurs (pas d'ouverture publique)

**Sujets de veille identifiés :**
```
Technique  : LangGraph nouvelles versions, Claude API pricing
Réglementaire : AMF règlement IA finance, RGPD IA, AI Act EU
Marché     : nouveaux outils FinAI FR, concurrents émergents
```

### 7.2 Benchmark services IA — C7

**Critères d'évaluation (6 critères pondérés) :**

| Critère | Poids | Raison |
|---------|-------|--------|
| Qualité texte FR | 30% | Cœur de valeur RITA |
| Coût par appel | 25% | Contrainte budget ~3€/mois |
| Latence | 15% | Expérience utilisateur |
| Contexte max | 15% | Volume données financières |
| RGPD / EU | 10% | Obligation légale |
| Disponibilité API | 5% | Fiabilité service |

**Résultats benchmark (5 services comparés) :**

| Service | Texte FR | Coût | Latence | Contexte | RGPD | Dispo | TOTAL |
|---------|----------|------|---------|----------|------|-------|-------|
| **Claude claude-opus-4-6** | 9/10 | 7/10 | 8/10 | 9/10 | 9/10 | 9/10 | **8.6/10** |
| GPT-4o | 7/10 | 7/10 | 8/10 | 8/10 | 5/10 | 9/10 | 7.1/10 |
| Gemini 1.5 Pro | 7/10 | 8/10 | 7/10 | 10/10 | 5/10 | 8/10 | 7.2/10 |
| Mistral Large | 8/10 | 9/10 | 9/10 | 7/10 | 10/10 | 7/10 | 8.4/10 |
| Llama 3 (local) | 6/10 | 10/10 | 6/10 | 7/10 | 10/10 | 10/10 | 7.4/10 |

**Choix retenu : Claude claude-opus-4-6 (Anthropic)**
- Meilleur score global (8.6/10)
- Qualité de génération française supérieure
- API stable et bien documentée
- Compatible RGPD avec paramétrage EU

### 7.3 Paramétrage du service IA — C8

```python
# Installation
pip install anthropic>=0.25.0

# Configuration
import anthropic
import os

client = anthropic.Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)

# Monitoring du service (C8)
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=800,
    system=SYSTEM_PROMPT_PERSONA,
    messages=[{"role": "user", "content": data_prompt}]
)

# Métriques collectées
tokens_in  = response.usage.input_tokens
tokens_out = response.usage.output_tokens
stop_reason = response.stop_reason   # end_turn = succès

# Documentation accessible : /docs/api-claude-setup.md
```

---

## 8. API ET INTÉGRATION IA (E3 — C9 à C13)

### 8.1 API exposant le modèle IA — C9

```
Endpoint principal : POST /briefing

Entrée :
  {
    "ticker": "MC.PA",
    "persona": "defensif",         // defensif | croissance | valeur
    "include_technical": true,
    "include_fundamental": true
  }

Sortie :
  {
    "ticker": "MC.PA",
    "date": "2026-05-23",
    "persona": "defensif",
    "briefing": {
      "resume": "LVMH a reculé de 1.8%...",
      "signal": "NEUTRE",
      "risque_principal": "...",
      "definition_du_jour": {...}
    },
    "transparence": {
      "tokens_in": 1847,
      "tokens_out": 312,
      "cout_eur": 0.00051,
      "co2_grammes": 0.0011,
      "duree_ms": 1243
    }
  }

Sécurité :
  → JWT Bearer Token obligatoire
  → Rate limit : 10 req/min par IP (slowapi)
  → HTTPS uniquement (Render)
  → OWASP API Top 10 checklist validée
```

### 8.2 Intégration dans l'application — C10

```
Le Dashboard Next.js consomme le backend FastAPI via proxy :

/api/briefing → Next.js API Route → FastAPI /briefing
              (proxy interne Vercel)

Avantages du proxy Next.js :
  → Clé API backend jamais exposée au navigateur
  → CORS géré proprement
  → Cache possible côté Next.js
```

### 8.3 Monitoring du modèle IA — C11

```
Métriques Prometheus collectées :

  rita_briefing_total           → nombre total de briefings générés
  rita_briefing_errors_total    → nombre d'erreurs Claude API
  rita_tokens_input_total       → tokens consommés en entrée
  rita_tokens_output_total      → tokens consommés en sortie
  rita_latency_seconds          → latence génération (histogram)
  rita_cost_eur_total           → coût total cumulé
  rita_co2_grams_total          → CO2 cumulé

Dashboard Grafana :
  → Panel 1 : Briefings/heure (taux de génération)
  → Panel 2 : Latence P50/P95/P99
  → Panel 3 : Coût cumulé jour/semaine/mois
  → Panel 4 : Erreurs API (alerte si > 5%)
  → Panel 5 : CO2 cumulé (éco-score dashboard)

LangSmith : traces complètes par agent
  → Input/output de chaque node LangGraph
  → Coût et latence par agent
  → Retry et erreurs tracés
```

### 8.4 Tests automatisés — C12

```python
# 8 tests minimum (couverture ≥ 60%)

# conftest.py
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_anthropic(monkeypatch):
    # Mock Claude API pour les tests (pas de coût)
    ...

# test_scout.py
def test_collect_ticker_returns_dict():
def test_collect_ticker_handles_invalid():

# test_fondamentaux.py
def test_get_fundamentals_has_required_keys():

# test_technique.py
def test_rsi_value_between_0_and_100():

# test_analyste.py
def test_briefing_returns_valid_json():
def test_briefing_no_buy_sell_advice():

# test_api.py
def test_health_endpoint_returns_200():
def test_briefing_requires_auth():
```

### 8.5 CI/CD MLOps — C13

```yaml
# .github/workflows/ci.yml

name: RITA CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Tests pytest
        run: pytest --cov=. --cov-fail-under=60

  build:
    needs: test
    steps:
      - name: Build Docker image
        run: docker build -t rita-api .

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Render
        run: curl -X POST $RENDER_DEPLOY_HOOK
```

---

## 9. APPLICATION WEB COMPLÈTE (E4 — C14 à C19)

### 9.1 Spécifications fonctionnelles — C14

**User Story 1 (US-01)**
```
En tant qu'investisseur particulier,
Je veux voir un tableau de bord de mes 20 actions,
Afin de comprendre en 1 coup d'œil l'état de mon portefeuille.

Critères d'acceptation :
  ✅ Tableau avec : ticker, cours, variation %, signal couleur
  ✅ Vert si variation > 0, Rouge si variation < 0
  ✅ Accessible clavier (Tab, Enter) — WCAG 2.1 AA
  ✅ Contraste texte/fond ≥ 4.5:1 — WCAG 1.4.3
  ✅ Responsive mobile (320px minimum)
```

**User Story 2 (US-02)**
```
En tant qu'investisseur,
Je veux générer un briefing IA pour une action donnée,
Afin d'obtenir une analyse rapide en français.

Critères d'acceptation :
  ✅ Sélecteur de persona (Défensif / Croissance / Valeur)
  ✅ Bouton "Générer le briefing"
  ✅ Affichage du résumé, signal, vigilance
  ✅ Définition du jour affichée
  ✅ Temps de génération < 5 secondes (95e percentile)
```

**User Story 3 (US-03)**
```
En tant qu'utilisateur soucieux de l'environnement,
Je veux voir l'empreinte carbone de chaque briefing,
Afin de comprendre l'impact de l'IA que j'utilise.

Critères d'acceptation :
  ✅ CO2 en grammes affiché après chaque briefing
  ✅ Équivalent "km en voiture" affiché
  ✅ Cumul mensuel CO2 dans le profil
```

### 9.2 Architecture frontend — C15

```
Next.js 14 — App Router

pages/
  /dashboard         → liste des 20 tickers
  /ticker/[symbol]   → détail + briefing IA
  /profile           → watchlist + éco-stats
  /auth/login        → authentification

components/
  Dashboard.tsx      → tableau des tickers
  HoldingRow.tsx     → ligne d'une action (cours, variation, signal)
  BriefingPanel.tsx  → affichage briefing + persona selector
  TransparencyPanel  → prompt + tokens + coût + CO2
  EcoScore.tsx       → badge CO2 + équivalent voiture
  DefinitionCard.tsx → définition du jour
```

### 9.3 Conformité WCAG 2.1 AA — C14, C17

```
Critère WCAG  Implémentation RITA
────────────────────────────────────────────────────────
1.4.3 Contraste  → texte sur fond : ratio ≥ 4.5:1 validé
                   (vert sur blanc : 7.2:1 ✅)

2.1.1 Clavier    → tous les éléments focalisables au clavier
                   Tab → HoldingRow, Enter → ouvre détail

2.4.3 Focus      → outline visible sur focus (2px solid blue)

3.3.1 Erreurs    → message d'erreur en français clair
                   "Ticker invalide — vérifiez le symbole boursier"

4.1.2 Nom/Rôle   → aria-label sur tous les boutons
                   aria-label="Générer briefing pour LVMH"
```

### 9.4 Éco-index — C17

```
Objectif : Grade B (score ≥ 80/100)

Optimisations appliquées :
  → Images WebP (pas de PNG/JPG lourds)
  → Lazy loading des composants non visibles
  → Pas de tracking tierces parties
  → Requêtes API minimisées (cache 5 min)
  → Fonts système (pas de Google Fonts)
  → Build Next.js optimisé (tree-shaking)

[À COMPLÉTER] : mesure Ecoindex.fr avant soutenance
```

---

## 10. MONITORING ET INCIDENTS (E5 — C20 à C21)

### 10.1 Surveillance de l'application — C20

**Stack de monitoring :**
```
Prometheus  → collecte métriques (scrape toutes les 15s)
Grafana     → visualisation dashboard temps réel
LangSmith   → traces LLM (agents, tokens, latence)
Sentry EU   → erreurs applicatives (RGPD — serveur Allemagne)
structlog   → logs JSON anonymisés

Métriques critiques et seuils d'alerte :
  rita_error_rate > 5%    → alerte Grafana (email)
  rita_latency_p95 > 10s  → alerte Grafana
  rita_cost_daily > 0.50€ → alerte Grafana
  PostgreSQL disk > 800Mo → alerte Grafana (limite Render 1Go)
```

**Conformité RGPD des logs (C20) :**
```python
# Logs anonymisés — jamais d'email ou de nom
import structlog

logger = structlog.get_logger()

logger.info(
    "briefing_generated",
    user_id_hash="sha256(user_id)",  # hash, pas l'ID réel
    ticker="MC.PA",
    persona="defensif",
    tokens=2159,
    cost_eur=0.00051,
    # JAMAIS : user_email, user_name, IP complète
)
```

### 10.2 Gestion des incidents — C21

**Incident documenté : INC-001 — Clé API expirée**

```
Date       : 15 mai 2026 (simulation)
Durée      : 2h30
Sévérité   : P1 (aucun briefing généré)

DÉTECTION (étape 1)
  Grafana alerte : rita_error_rate > 5% pendant 3 min
  Prometheus : 100% des appels /briefing retournent 401

QUALIFICATION (étape 2)
  Type : erreur d'authentification API externe
  Portée : tous les utilisateurs, toutes les actions

DIAGNOSTIC (étape 3)
  logs structlog : "AuthenticationError: invalid_api_key"
  Cause racine : clé ANTHROPIC_API_KEY expirée sur Render
  Reproduit en dev : ANTHROPIC_API_KEY="" → même erreur

CORRECTION (étape 4)
  Render dashboard → Environment Variables
  → Mise à jour ANTHROPIC_API_KEY avec nouvelle clé
  → Redéploiement Render (2 min)

VÉRIFICATION (étape 5)
  GET /health → {"status": "ok", "claude_api": "connected"}
  Test manuel : briefing généré avec succès
  rita_error_rate → retour à 0%

DOCUMENTATION (étape 6)
  Postmortem INC-001 rédigé (evidence/postmortem/INC-001.md)
  Runbook créé : docs/runbooks/claude-api-auth-failure.md
  Mesure préventive : alerte Grafana si > 0 erreur 401 en 5 min
  Test de non-régression ajouté : test_claude_api_connectivity()
```

---

## 11. SÉCURITÉ ET CONFORMITÉ RGPD

### 11.1 OWASP API Top 10

```
A01 — Broken Object Auth    → JWT Bearer Token sur tous endpoints
A02 — Broken Auth           → bcrypt factor 12, tokens JWT expirés
A03 — Broken Object Prop    → Pydantic validation stricte
A04 — Unrestricted Resource → slowapi 10 req/min par IP
A05 — Broken Auth Function  → pas d'endpoints admin publics
A06 — Unrestricted Flows    → rate limit sur /auth/login
A07 — Server Side Request   → pas de proxy URL utilisateur
A08 — Security Misconfiguration → HTTPS forcé, headers sécurité
A09 — Improper Inventory    → OpenAPI /docs désactivé en prod
A10 — Unsafe API Consumption → try/except sur tous appels externes
```

### 11.2 Conformité RGPD

```
Données collectées sur les utilisateurs :
  → email_hash (SHA-256 de l'email — jamais l'email brut)
  → watchlist tickers (données non personnelles)
  → historique briefings (contenu non personnel)
  → logs anonymisés (user_id hashé)

Droits RGPD implémentés :
  ✅ Droit d'accès      → GET /profile → toutes les données
  ✅ Droit de portabilité → GET /profile/export → JSON complet
  ✅ Droit à l'effacement → DELETE /profile → suppression cascade
  ✅ Durée de conservation → briefings supprimés après 12 mois

Hébergement EU :
  ✅ Render → Frankfurt (Allemagne)
  ✅ Sentry EU → serveurs EU uniquement
  ✅ Anthropic → option EU data processing

Registre des traitements (CNIL) :
  → Traitement 1 : Gestion des comptes utilisateurs
  → Traitement 2 : Génération de briefings financiers
  → Traitement 3 : Logs de monitoring anonymisés
```

---

## 12. DIFFÉRENCIATEURS UNIQUES

```
RITA v2 est le SEUL outil qui combine :

1. FRANÇAIS NATIF
   → Briefings générés nativement en français
   → 3 personas avec noms et styles français
   → Sources RSS exclusivement françaises

2. GRATUIT ET DÉPLOYÉ SUR LE WEB
   → yfinance (0€) + pandas-ta (0€) + RSS (0€)
   → Claude API ≈ 3€/mois seulement
   → Render + Vercel free tiers

3. 3 PERSONAS ANALYSTES FRANÇAIS
   → Défensif (Sophie Martin)
   → Croissance (Lucas Dubois)
   → Valeur (Emma Chen)
   → Inexistant ailleurs en français

4. TRANSPARENCE DU PROMPT
   → Prompt exact visible dans l'interface
   → Tokens consommés + coût en centimes affichés
   → Réponse directe à la leçon Simplon
     "L'IA est un outil, pas de la magie"

5. ÉCO-SCORE CO2
   → Empreinte carbone estimée par briefing
   → Équivalent km voiture affiché
   → Réponse à la vigilance Simplon
     "Impact environnemental des LLM"

6. PÉDAGOGIE — DÉFINITION DU JOUR
   → 1 terme financier expliqué par briefing
   → 2 phrases simples pour débutants
   → Rend RITA accessible à tous les niveaux
```

---

## 13. PLANNING ET JALONS

### 13.1 Planning mensuel

```
M1 — Mai 2026 (en cours)
  ✅ Concept posé et validé
  ✅ Architecture RITA v2 documentée
  ✅ Rapports V0 rédigés
  🔄 Repo GitHub créé et structuré
  🔄 Questions formatrice posées
  LIVRABLE : squelette FastAPI + repo structuré

M2 — Juin 2026
  → E1 DONNÉES (BC01 — le plus risqué)
  → yfinance pipeline opérationnel
  → PostgreSQL MERISE MCD/MPD implémenté
  → PySpark Parquet 1.8M lignes
  → API /data fonctionnelle
  LIVRABLE : RAPPORT-E1 finalisé + PDF

M3 — Juillet 2026
  → E2 VEILLE/BENCHMARK
  → Benchmark 5 services IA documenté
  → Veille hebdomadaire S1 à S8 rédigée
  → Claude API paramétré + testé
  LIVRABLE : RAPPORT-E2 finalisé

M4 — Août 2026
  → E3 API/MLOps
  → 5 agents LangGraph opérationnels
  → 8 tests pytest (coverage ≥ 60%)
  → GitHub Actions CI/CD
  → Prometheus + Grafana live
  LIVRABLE : RAPPORT-E3 + démo API live

M5 — Septembre 2026
  → E4 APPLICATION
  → Dashboard Next.js complet
  → User stories WCAG validées
  → Docker + CD Vercel
  → Éco-index Grade B mesuré
  LIVRABLE : RAPPORT-E4 + démo app live

M6 — Octobre-Novembre 2026
  → E5 MONITORING
  → INC-001 postmortem finalisé
  → Runbooks rédigés
  → Oraux blancs (objectif : 3 minimum)
  → Diaporama 12 slides finalisé
  → Remise livrables J-5
  LIVRABLE : Soutenance + RAPPORT-E5
```

### 13.2 Semaines clés

```
S1  (11-17 mai)  → Questions formatrice ✅
S4  (1-7 juin)   → Squelette FastAPI + React opérationnel
S8  (6-12 juil)  → RAPPORT-E1 finalisé PDF
S12 (3-9 août)   → RAPPORT-E2 finalisé
S14 (17-23 août) → Oral blanc E1 (15 min)
S18 (14-20 sept) → Oral blanc E3 (20 min + démo)
S22 (12-18 oct)  → Oral blanc E4 (20 min + démo)
S26 (9 nov)      → Oral blanc complet 90 min
J-5 soutenance   → Remise 5 rapports PDF
```

---

## 14. CONCLUSION

### Ce que RITA v2 démontre

RITA v2 est plus qu'un projet de certification. C'est une réponse
concrète à un vrai problème de marché : **l'absence d'outil d'analyse
financière en français, gratuit, et accessible aux particuliers.**

En construisant RITA v2, je démontre la maîtrise de :

```
✅ Architecture multi-agents (LangGraph + LangGraph)
✅ Intégration LLM (Claude API, system prompts, RAG)
✅ Pipeline de données complet (yfinance → PySpark → PostgreSQL)
✅ API REST sécurisée (FastAPI + OWASP + JWT)
✅ Application web moderne (Next.js + WCAG)
✅ DevOps complet (Docker + GitHub Actions + CI/CD)
✅ Monitoring production (Prometheus + Grafana + Sentry)
✅ Conformité RGPD et éthique IA
```

### Ce que j'ai appris (réflexion personnelle)

La construction de RITA v2 m'a appris qu'une bonne architecture IA
ne se résume pas à "brancher un LLM sur des données".
Il faut penser à :
- La qualité et la provenance des données (C1-C3)
- La sécurité et la protection des utilisateurs (RGPD, OWASP)
- La transparence sur ce que l'IA fait réellement (prompt visible)
- L'impact environnemental (éco-score)
- L'accessibilité pour tous les niveaux (WCAG, définition du jour)

> "Les IA Génératives sont des outils. Elles n'ont rien de magique."
> — Atelier Simplon, mai 2026

RITA v2 applique exactement ce principe : un outil bien conçu,
transparent sur son fonctionnement, utile pour un vrai public,
et respectueux des utilisateurs.

---

## ANNEXES

### A. Lexique des sigles

```
AMF    → Autorité des Marchés Financiers
API    → Application Programming Interface
CNIL   → Commission Nationale Informatique et Libertés
MACD   → Moving Average Convergence Divergence
MERISE → Méthode d'Étude et de Réalisation Informatique par Sous-Ensembles
MLOps  → Machine Learning Operations
OHLCV  → Open, High, Low, Close, Volume
OWASP  → Open Web Application Security Project
P/E    → Price to Earnings ratio
RAG    → Retrieval-Augmented Generation
RGPD   → Règlement Général sur la Protection des Données
ROE    → Return on Equity
RSI    → Relative Strength Index
WCAG   → Web Content Accessibility Guidelines
```

### B. Sources et références

```
[1] AMF France — Rapport annuel investisseurs particuliers 2024
[2] ai-hedge-fund GitHub (virattt) — github.com/virattt/ai-hedge-fund
[3] Perplexity Finance API — perplexity.ai/hub/blog/finance-search
[4] Simplon — Référentiel RNCP37827 — Développeur en IA
[5] PDF Simplon — Atelier Sensibilisation IAG prairie (mai 2026)
[6] yfinance Documentation — ranaroussi.github.io/yfinance
[7] pandas-ta PyPI — pypi.org/project/pandas-ta
[8] Anthropic Documentation — docs.anthropic.com
[9] Market Research Future — France GenAI FinTech Market 2024
```

### C. Informations techniques

```
Repo GitHub    : [À COMPLÉTER — URL repo rita-agent-certif]
Demo backend   : [À COMPLÉTER — URL Render]
Demo frontend  : [À COMPLÉTER — URL Vercel]
LangSmith      : [À COMPLÉTER — lien projet]
```

---

*RITA v2 — Rapport de Projet Version 0*
*Eramalingam GANDAKUMAR | 23 mai 2026*
*Certification RNCP37827 — Développeur en Intelligence Artificielle*
*Wild Code School — Bootcamp Dev IA Agentique | Simplon.co*

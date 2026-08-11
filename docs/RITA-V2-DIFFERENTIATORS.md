# RITA v2 — Différenciateurs Uniques

# Document de positionnement concurrentiel

# Certification RNCP37827 | Eramalingam GANDAKUMAR

---

## 1. RÉSUMÉ EN 1 PHRASE

> "RITA v2 fait ce que ai-hedge-fund fait, ce que Perplexity Finance fait,
> mais en français, gratuitement, déployé sur le web, et RGPD conforme —
> pour les 8 millions d'investisseurs particuliers francophones ignorés."

---

## 2. TABLEAU CONCURRENCE COMPLET

| Critère | ai-hedge-fund | Perplexity Finance | Bloomberg | RITA v2 |
|---------|--------------|-------------------|-----------|---------|
| Prix | Gratuit | $5/1000 appels | 2000€/mois | ~3€/mois |
| Langue | Anglais | Anglais | Anglais | ✅ Français |
| Déployé web | ❌ Terminal | API uniquement | Terminal dédié | ✅ Render+Vercel |
| RGPD | ❌ | ❌ | ❌ | ✅ Sentry EU |
| Open source | ✅ | ❌ | ❌ | ✅ GitHub |
| Multi-agents | ✅ 18 agents | ❌ | ❌ | ✅ 5 agents FR |
| Analyse fondamentale | ✅ | ✅ payant | ✅ payant | ✅ yfinance |
| Analyse technique | ✅ | ❌ | ✅ payant | ✅ pandas-ta |
| Sentiment actualités | ✅ anglais | Partiel | ✅ payant | ✅ RSS français |
| Backtesting | ✅ | ❌ | ✅ payant | ✅ simplifié |
| 3 personas FR | ❌ | ❌ | ❌ | ✅ UNIQUE |
| Prompt transparent | ❌ | ❌ | ❌ | ✅ UNIQUE |
| Éco-score CO2 | ❌ | ❌ | ❌ | ✅ UNIQUE |
| Définition du jour | ❌ | ❌ | ❌ | ✅ UNIQUE |
| Public cible | Quant traders | Développeurs | Institutions | ✅ Particuliers FR |
| Formation requise | Terminal Python | Dev API | 6 mois Bloomberg | ✅ Aucune |

---

## 3. CE QUE RITA PREND DE CHAQUE CONCURRENT

### De ai-hedge-fund (43k ⭐ GitHub)
```
✅ PRIS:
   → Architecture multi-agents (LangGraph)
   → Agent Fondamentaux (P/E, ROE, earnings)
   → Agent Technique (RSI, MACD)
   → Agent Sentiment (actualités)
   → Backtesting simple

❌ AMÉLIORÉ:
   → ai-hedge-fund: terminal → RITA: web déployé
   → ai-hedge-fund: 18 personas anglais → RITA: 3 personas français
   → ai-hedge-fund: pas RGPD → RITA: Sentry EU, logs anonymisés
   → ai-hedge-fund: recherche/quant → RITA: grand public francophone
```

### De Perplexity Finance ($5/1000 appels)
```
✅ PRIS (équivalent gratuit):
   → Données fondamentales (yfinance.info = P/E, P/B, ROE)
   → Estimations analystes (yfinance analyst_price_targets)
   → Transactions insiders (yfinance.insider_transactions)
   → Historique résultats beats/misses (yfinance.earnings_history)
   → Données ETF (yfinance pour ETFs)

❌ AMÉLIORÉ:
   → Perplexity: API brute dev → RITA: application complète utilisateur
   → Perplexity: $5/1000 appels → RITA: 0€ (yfinance gratuit)
   → Perplexity: anglais → RITA: français natif
   → Perplexity: citations web → RITA: RSS sources françaises citées
```

### Du PDF Simplon (leçons de la formatrice)
```
✅ INTÉGRÉ:
   → "L'IA est un outil, pas de la magie"
     → Transparence : prompt visible + tokens + coût

   → "Points de vigilance : biais, coût, impact environnemental"
     → Éco-score CO2 par briefing
     → Avertissement biais affiché
     → Coût API affiché en centimes

   → "Prompt engineering = art de poser les bonnes questions"
     → 3 personas avec prompts différents
     → Prompt exportable pour personnalisation
```

---

## 4. LES 6 DIFFÉRENCIATEURS UNIQUES DE RITA v2

### D1 — Français Natif (pas de traduction)
```
PROBLÈME: 100% des outils FinAI sérieux sont en anglais
SOLUTION RITA: génération native en français par Claude
              RSS sources françaises (BFM, Les Echos, Boursorama)
              3 personas avec noms et styles français
PREUVE: aucun concurrent ne fait ça — vérifié par recherche web
```

### D2 — Gratuit et Déployé
```
PROBLÈME: gratuit = terminal local (ai-hedge-fund)
          déployé = payant (Perplexity, Bloomberg)
SOLUTION RITA: gratuit ET déployé sur le web
              yfinance (0€) + pandas-ta (0€) + RSS (0€)
              Claude API ≈ 3€/mois seulement
              Render free tier + Vercel free tier
PREUVE: premier outil à faire les deux simultanément
```

### D3 — 3 Personas Analystes Français
```
PROBLÈME: ai-hedge-fund simule Buffett/Munger en anglais
          → inaccessible au grand public FR
SOLUTION RITA: 3 analystes français adaptés au public FR
              🔵 Défensif → investisseur prudent
              🟢 Croissance → horizon long terme
              🔴 Valeur → style value investing
PREUVE: concept inexistant en français, vérifié
```

### D4 — Transparence du Prompt (leçon Simplon)
```
PROBLÈME: tous les outils = boîte noire
          "L'IA n'a rien de magique" (PDF Simplon)
SOLUTION RITA: prompt exact visible après chaque briefing
              tokens consommés affiché
              coût en centimes affiché
              durée de génération affiché
PREUVE: aucun outil concurrent ne fait ça
        aligne avec la pédagogie Simplon/WCS
```

### D5 — Éco-Score CO2 (leçon Simplon)
```
PROBLÈME: "impact environnemental des LLM" (PDF Simplon, slide 20)
          aucun outil ne mesure son empreinte
SOLUTION RITA: estimation CO2 par briefing (grammes)
              cumul mensuel CO2 utilisateur
              équivalent km voiture affiché
              aligne avec C17 (éco-index Grade B)
PREUVE: différenciateur absolu, personne ne fait ça
```

### D6 — Pédagogie "Définition du Jour"
```
PROBLÈME: les particuliers ne comprennent pas les termes financiers
          Bloomberg/ai-hedge-fund = pour experts
SOLUTION RITA: chaque briefing explique 1 terme utilisé
              en 2 phrases simples en français
              ex: "RSI: indicateur qui mesure si une action
                  est survendue ou surachetée..."
PREUVE: rend RITA accessible aux débutants
        différence fondamentale avec tous les concurrents
```

---

## 5. PHRASE POUR CHAQUE SITUATION

### En classe (30 secondes)
> "Mon projet analyse des actions en bourse avec 5 agents IA spécialisés
> et génère un briefing quotidien en français. C'est ce que Bloomberg
> fait à 2000€/mois — mais gratuit, open source, et pour n'importe qui."

### Face à "ça existe déjà"
> "Oui. ai-hedge-fund le fait en anglais pour quants, en terminal.
> Perplexity Finance le fait en anglais, payant, pour développeurs.
> RITA le fait en français, gratuit, déployé sur le web, pour particuliers.
> Ce n'est pas la même chose."

## 6. MAPPING CERTIFICATION

```
D1 (Français)       → C6 (veille) + C14 (accessibilité utilisateurs)
D2 (Gratuit+Web)    → C13 (déploiement) + C19 (CD)
D3 (3 Personas)     → C9 (API IA) + C10 (intégration) + C16 (agile)
D4 (Transparence)   → C11 (monitoring) + C6 (éthique IA)
D5 (Éco-score)      → C15 (éco-responsable) + C17 (éco-index)
D6 (Pédagogie)      → C14 (user stories WCAG) + C17 (accessibilité)
```

---

*Document créé: 22 mai 2026*
*Basé sur: PDF Simplon "Atelier Sensibilisation IAG" +
          ai-hedge-fund (github.com/virattt) +
          Perplexity Finance API +
          Botraiders (concurrent FR)*

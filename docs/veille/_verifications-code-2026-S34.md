# Vérifications dans le code — préparation de la séance S34

> ⚠️ **Ce fichier n'est ni la note, ni un jugement.** Il ne contient que des **faits
> mécaniques** : une commande, sa sortie, ce qu'elle établit. Aucune conclusion « ce que ça
> change dans RITA » — c'est ton travail, et c'est lui qui prouve la compétence.
>
> Relevé le **2026-08-17** · dépôt `D:\KandaWork\RITA_PROJECT\rita-agent\`
> Complète `_candidats-2026-S34.md`, candidat 1 (Top 10 agentique OWASP).

---

## V1 — Outils déclarés au modèle : **aucun**

```bash
grep -rn "tools=\|bind_tools\|@tool\|ToolNode" --include=*.py .
```

**Sortie : vide** (hors `.venv`). Confirme le constat de la note S33.

**Ce que ça établit** : les entrées du Top 10 agentique portant sur le **mésusage d'outil**
et l'**exécution d'action** n'ont pas de surface d'attaque dans RITA. À confirmer entrée par
entrée quand tu auras la liste officielle (voir V5).

---

## V2 — Mémoire persistante de l'agent : **aucune**

```bash
grep -rniE "checkpoint|MemorySaver|Saver\(|chat_history|historique" --include=*.py \
  agents/ graph/ src/ api/ pipelines/ sources/ guardrails/
```

**Sortie** : 7 occurrences, **toutes** sur le mot « historique » au sens *historique de
cotations* (`api/donnees.py:48,65`, `pipelines/ingest.py:20,107,147,219`,
`sources/scraper.py:53`). **Aucun `checkpointer` LangGraph, aucun historique de conversation.**

> 📖 **Checkpointer** : composant LangGraph qui sauvegarde l'état du graphe entre deux
> exécutions, pour que l'agent « se souvienne » du tour précédent.

**Ce que ça établit** : le graphe repart de zéro à chaque appel (`generer_briefing_complet`
construit le graphe puis l'invoque, `graph/workflow.py:34-40`). L'**empoisonnement de
mémoire** — faire écrire à l'agent un texte hostile qu'il relira plus tard comme consigne —
**n'a pas de support dans RITA aujourd'hui**. C'est vrai *parce qu'il n'y a pas de mémoire*,
pas parce qu'elle serait protégée.

---

## V3 — ⚠️ Ce que le modèle reçoit réellement : **des nombres, pas du texte tiers**

`agents/analyst.py:5-27` — la signature et le prompt :

```python
def generate_briefing(ticker: str, price: float, change_pct: float, volume: int,
                      currency: str) -> str:
```

Le prompt n'interpole que `{ticker}`, `{price}`, `{currency}`, `{change_pct}`, `{direction}`,
`{volume}`. **Aucun champ de texte libre.**

Et `agents/scout.py:29-50` : le nœud `scout` appelle **`yfinance`**, pas le scraper ni le RSS.
Il retourne `price`, `change_pct`, `volume`, `currency`, `error`.

**Ce que ça établit — et c'est une nuance à trancher toi-même** : la note S33 classe la
2ᵉ condition de la *lethal trifecta* (« contenu non fiable ») en **✅ OUI**, au motif que
RITA lit Boursorama et des flux RSS. C'est exact **au niveau du projet**. Mais au niveau
**du graphe de l'agent**, ce texte tiers **n'atteint jamais le modèle** : il part de
`sources/` vers la base par `pipelines/ingest.py`, et ressort par l'API — sans passer par
`analyst.py`.

⚠️ **Je ne tranche pas si c'est « OUI » ou « NON ».** Les deux lectures se défendent, et
c'est exactement le genre d'arbitrage qu'un jury attend de toi. La question à te poser :
*la trifecta se raisonne-t-elle à l'échelle du système ou à l'échelle du graphe ?*

---

## V4 — Le garde-fou est bien branché, en 3 points

| Point d'appel | Fichier | Preuve |
|---|---|---|
| **Entrée RSS** | `sources/rss.py:26` | `from guardrails.injection import neutraliser` — chaque article filtré (`rss.py:80,121`) |
| **Entrée scraping** | `sources/scraper.py:44` | idem (`scraper.py:194`) |
| **Sortie API** | `api/donnees.py:127-134` | `WHERE bloque_injection = FALSE` **codé en dur**, verrouillé par `tests/test_api_donnees.py:110-120` |

**Choix de conception constaté** : `pipelines/ingest.py:181-182` — les articles porteurs
d'injection sont **conservés et marqués**, pas supprimés, pour rester auditables.

**Ce que ça établit** : le garde-fou n'est **pas débranché**. Il est appelé aux deux entrées
tierces et filtré à la sortie API. Trois tests le verrouillent (`test_rss.py:61-72`,
`test_scraper.py:90-99`, `test_api_donnees.py:110-120`).

---

## V5 — 🔴 Ce que je n'ai PAS pu vérifier : la liste ASI01→ASI10

Les pages HTML officielles d'OWASP **n'énumèrent pas** les dix entrées :

| Page consultée | HTTP | Contient la liste ? |
|---|---|---|
| [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 200 | ❌ non — description seule |
| [Agentic Security Initiative](https://genai.owasp.org/initiatives/agentic-security-initiative/) | 200 | ❌ non |

La liste n'existe que dans **le PDF**, derrière
[le lien de téléchargement OWASP](https://genai.owasp.org/download/52117) (HTTP 200).
**Je ne l'ai pas téléchargé** : un téléchargement se décide, il ne se subit pas.

⚠️ **Conséquence pour ta séance** : tous les noms d'entrées qui circulent (*goal hijack*,
*tool misuse*, *memory poisoning*, *rogue agents*) viennent de **blogs d'éditeurs**, pas de
la source. Le protocole (`README.md` §3) les écarte. **Télécharge le PDF et lis la liste
toi-même** — c'est le premier geste de la séance, et c'est aussi la démonstration exacte de
ce que S33 avait déjà établi : *une information reprise par cinq sites reste non vérifiée si
aucun n'est la source.*

---

## Récapitulatif des commandes, pour les rejouer devant un jury

```bash
cd D:/KandaWork/RITA_PROJECT/rita-agent
grep -rn "tools=\|bind_tools\|@tool\|ToolNode" --include=*.py agents/ graph/
grep -rniE "checkpoint|MemorySaver|Saver\(|chat_history" --include=*.py agents/ graph/ src/
grep -rn "injection" --include=*.py sources/ api/ pipelines/
```

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Checkpointer** | Composant qui sauvegarde l'état d'un graphe entre deux exécutions — la « mémoire » de l'agent |
| **Empoisonnement de mémoire** | Faire écrire à l'agent, dans sa propre mémoire, un texte hostile qu'il relira comme une consigne |
| **Lethal trifecta** | Données privées + contenu non fiable + canal sortant : les 3 conditions qui rendent l'exploitation quasi certaine |
| **ASI** | *Agentic Security Initiative* — groupe de travail OWASP, et préfixe des entrées du Top 10 agentique |

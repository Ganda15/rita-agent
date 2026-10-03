# Preuve C7 : première mesure du banc des fournisseurs (03/10/2026)

> Plan : `../../docs/PLAN-C7-benchmark.md`, options D1 à D3 = A retenues par Era le 03/10 (« ok do it »).
> Script : `evals/benchmark_fournisseurs.py`, écrit test d'abord (`tests/test_benchmark_fournisseurs.py`,
> `tests/test_benchmark_outillage.py`). Brut : `resultats-2026-10-03.jsonl` (30 lignes), `resume-2026-10-03.json`,
> jeu figé `jeu-d-essai-2026-10-03.json`. Notation du français à faire par Era : `notes-francais-2026-10-03.csv`
> (30 textes mélangés, sans fournisseur), clé de correspondance dans le fichier `-cle.csv`, à ouvrir après.

## 1. Ce qui a été mesuré, et ce qui ne pouvait pas l'être

Trois fournisseurs sondés, dans l'ordre de la cascade de `src/llm.py` :

| Fournisseur | Modèle configuré | Sonde | Conséquence |
|---|---|---|---|
| Azure AI Foundry | `claude-opus-4-8` | `KeyError: AZURE_FOUNDRY_API_KEY` | **indisponible pour la mesure** : aucune clé sur le poste |
| Anthropic, API directe | `claude-sonnet-5` | `TypeError: Could not resolve authentication method` | **indisponible pour la mesure** : aucune clé dans l'environnement du poste |
| OpenRouter | `anthropic/claude-sonnet-4.5` | répond | **mesuré** : 10 cas × 3 répétitions = 30 appels |

**Il n'y a donc pas de comparaison le 03/10 : un seul fournisseur a pu être mesuré.** Le banc est en place, le
jeu est figé, la méthode a tourné ; la comparaison exige que les deux autres clés soient posées (Era) et, selon la
réponse du formateur (plan §2), un modèle d'un autre éditeur par OpenRouter (D1).

## 2. Le jeu d'essai figé

Dix cas construits par le code réel (`agents.scout.collect`, `rag.recherche.rechercher` avec la question du
graphe), figés le 03/10 : les sept valeurs du portefeuille (AI.PA, BNP.PA, MC.PA, OR.PA, SAN.PA, SU.PA, VIRI.PA),
la plus forte hausse de la dernière séance (CO.PA, +9,09 %), la plus forte baisse (ALMKT.PA, −11,29 %), une valeur
cotée à Londres en livres (HSBA.L). Trois cas sans aucun article retrouvé (VIRI.PA, ALMKT.PA, HSBA.L), sept avec un à
trois passages. Prompt identique à celui du rédacteur (`agents.analyst.construire_prompt`, test de contrat),
`max_tokens` 500.

## 3. Résultats, OpenRouter seul

| Mesure | Valeur | Lecture |
|---|---|---|
| Disponibilité | 30 / 30, Wilson 95 % [0,89 ; 1,00] | aucune erreur ni délai dépassé |
| Conformité AMF (`guardrails/sortie.py`) | 30 / 30, [0,89 ; 1,00] | aucun texte retenu par le garde-fou ; sur 30 appels l'intervalle reste large, on ne conclut pas « 100 % » |
| Fidélité aux faits fournis (cours présent, sens de la variation non inversé) | 30 / 30, [0,89 ; 1,00] | heuristique automatique ; les chiffres non fournis restent à relire par Era avec la notation du français |
| Latence, médiane et p95 | 5,79 s et 6,95 s | appels de 5,1 à 7,0 s ; même ordre que le briefing réel de 14 h 48 (5,6 s) |
| Jetons, moyenne entrée et sortie | 491 et 212 | sortie de 556 à 815 caractères, 3 à 5 phrases comme demandé |
| Coût, prix public OpenRouter du 03/10 (3 USD / 15 USD par million de jetons, `https://openrouter.ai/api/v1/models`) | 0,1396 USD pour 30 briefings, soit 0,0047 USD par briefing | sept briefings par jour sur un an : de l'ordre de 12 USD |

Trois textes relus à la main (CO.PA, HSBA.L, SAN.PA) : le cours et la variation fournis sont repris tels quels, le
volume est présenté comme une moyenne sur 20 séances, l'absence d'actualité est dite plutôt qu'inventée, et un
article de septembre est daté comme tel au lieu d'être présenté comme récent (règle R13 du prompt).

## 4. Ce que cette mesure ne dit pas

- Rien sur Foundry ni sur Anthropic en direct : indisponibles, pas mauvais.
- Rien sur un modèle d'un autre éditeur : hors périmètre tant que D1 n'est pas tranchée avec le formateur.
- Rien sur la qualité du français : la grille à trois niveaux est à remplir par Era, à l'aveugle, dans le CSV.
- Le coût est en dollars, prix public du jour ; Langfuse affiche encore 0 pour ce modèle (nom hors grille).
- Trente appels sur un même jour : la variance d'un fournisseur d'un jour à l'autre n'est pas mesurée.

## 5. Un défaut trouvé en mesurant, et corrigé : INC-006 bis

Construire le jeu appelle `rag.recherche.rechercher`, qui ouvre une étape de trace (`garde-fou-entree`) ; hors d'un
briefing, cette étape devient une trace racine. Résultat : **22 traces parasites** écrites dans le projet Langfuse de
production entre 13 h 56 et 13 h 57 UTC (dix pour la construction du jeu, douze pour une vérification préalable des
tickers), même défaut qu'INC-006 par un autre chemin. Corrigé le jour même : le script coupe le traçage
(`LANGFUSE_TRACING_ENABLED=false`) avant tout import du code de RITA, un test le fige
(`test_le_banc_coupe_le_tracage_avant_de_toucher_au_code_de_rita`), et les 22 traces ont été supprimées par l'API le soir même (compte relu : 23 traces, les 15 factices du 02/10 et les 8 réelles)
(voir le post-mortem, `../C21/INC-006-tests-ecrivaient-en-production.md`, complément du 03/10). Les 30 appels du
banc, eux, n'ont écrit aucune trace : ils appellent les fonctions de fournisseur une à une, sans la cascade tracée.

## 6. Commandes

```
C:\Python314\python.exe -X utf8 -m evals.benchmark_fournisseurs --construire AI.PA BNP.PA MC.PA OR.PA SAN.PA SU.PA VIRI.PA CO.PA ALMKT.PA HSBA.L --sortie evidence/C7
C:\Python314\python.exe -X utf8 -m evals.benchmark_fournisseurs --jeu evidence/C7/jeu-d-essai-2026-10-03.json --repetitions 3 --plafond 5 --sortie evidence/C7
C:\Python314\python.exe -X utf8 -m pytest tests/test_benchmark_fournisseurs.py tests/test_benchmark_outillage.py -q
```

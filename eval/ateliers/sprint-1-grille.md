# Atelier croisé n°1 : Cadrer, choisir, concevoir

Phase 6, fil rouge. Grille remplie par l'évaluateur pendant la présentation, puis versée dans le dépôt du présenté.

| Présenté | Évaluateur | Date | Projet |
|---|---|---|---|
| Eramalingam GANDAKUMAR | un pair de la promotion | 13/10/2026 | RITA, dossier [`docs/CADRAGE-V1.md`](../../docs/CADRAGE-V1.md) |

**Format (2 h en tout, puis on inverse les rôles).** 20 min de présentation du dossier de conception (pas de code).
15 min de questions guidées par la grille : ✓ démontré, ~ partiel, ✗ absent ; chaque cotation s'appuie sur une preuve
observée. 10 min de conseils : un point fort, un conseil prioritaire, actionnable avant la fin du sprint suivant.

L'évaluateur lit le dossier en se mettant à la place d'un futur repreneur du projet.

Recopiée mot pour mot depuis la grille Excel remplie par l'évaluateur (`grille-atelier-1-cadrage (2).xlsx`).

| # | Critère | ✓ / ~ / ✗ | Preuve observée, remarque |
|---|---|---|---|
| 1 | **Besoin clair.** En une page, je comprends à qui sert le projet et ce que promet le parcours principal. | ✓ | démo, réponse au tac au tac |
| 2 | **Périmètre tenable.** La V1 me paraît réalisable en six jours de développement par une personne. Sinon, qu'est-ce que je couperais ? | ✓ | Beaucoup de mal à comuniquer |
| 3 | **Hors-périmètre assumé.** Ce que la V1 ne fera pas est écrit noir sur blanc, pas laissé implicite. | non coté | Je ne sais pas. Beacoup de mal à communiquer |
| 4 | **Composante agentique à la hauteur.** Elle figure au menu du parcours, au bon niveau, et la justification « cette composante sert ce besoin » me convainc. | non coté | Un LLM simple mais ca fonctionne ... |
| 5 | **Stack justifiée.** Socle du parcours, ou dérogation argumentée (un seul élément exotique). | non coté | LANGGRAPH pour un LLM ? |
| 6 | **Critères vérifiables.** Pour chaque critère du contrat personnel, je peux répondre oui ou non en le lisant (format Étant donné / quand / alors). | non coté | Pas de test pour verifier ?? |

**Le point fort du dossier :** Projet déjà réalisé.

**Le conseil prioritaire pour le sprint 2 :** Bien clarifier le rôle de MCP et où se trouve le serveur.

**Avis de l'évaluateur sur le périmètre (le formateur tranche) :** ☒ tenable en l'état ☐ à resserrer, sur quoi :

---

## Suite donnée par le présenté

À remplir après l'atelier : pour chaque remarque, traitée (commit), reportée (sprint et raison) ou écartée (raison).

| Remarque | Suite | Commit ou raison |
|---|---|---|
| 1 · « démo, réponse au tac au tac » | rien à faire | point positif |
| 2 et 3 · « Beaucoup de mal à communiquer » | traitée à l'oral | phrases plus courtes ; montrer la ligne du dossier dont je parle ; pas de commit |
| 3 · « Je ne sais pas » (hors-périmètre) | écartée sur le fond | déjà écrit : `docs/CADRAGE-V1.md` § 1, « Hors périmètre V1 », et diapo 5 ; à montrer du doigt à l'oral |
| 4 · « Un LLM simple mais ca fonctionne » | traitée | § 3 : pourquoi un graphe à étapes fixes plutôt qu'un agent qui choisit ses outils ; menu du dispositif demandé au formateur (commit « Atelier 1 », 13/10) |
| 5 · « LANGGRAPH pour un LLM ? » | traitée | § 4 : une raison par outil, dont LangGraph et sa limite (commit « Atelier 1 », 13/10) |
| 6 · « Pas de test pour verifier ?? » | traitée | § 6 : la preuve de chaque critère ; tests existants pour 1, 2 et le 403 du 4 ; tests des jours 3 et 5, vérification chronométrée du jour 2 (commit « Atelier 1 », 13/10) |
| Conseil · rôle de MCP et où se trouve le serveur | traitée | § 5 : « La passerelle MCP », sur le poste de l'utilisateur, sans port réseau, trois outils en lecture seule, aucun accès au briefing (commit « Atelier 1 », 13/10) |

> Nom de l'évaluateur remplacé par son rôle le 20/11/2026, avant la publication du dépôt (registre RGPD, mesure M2). Le reste de la grille est inchangé ; l'original reste dans l'historique Git et dans les tags.

# OWASP Top 10 for Agentic Applications 2026 — la liste, lue à la source

> **Extraction factuelle**, pas une analyse. Les dix intitulés ci-dessous sont **recopiés du
> PDF officiel**, pas d'un blog. La colonne « applicable à RITA ? » est **volontairement
> vide** : c'est ton travail de veille.
>
> **Source** : [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
> **PDF** : [téléchargement OWASP](https://genai.owasp.org/download/52117) — 1 274 186 octets,
> récupéré le 2026-08-17 (HTTP 200, `application/pdf`)
> **Version** : « Version 2026 », **décembre 2025** · **Licence** : CC BY-SA 4.0
> **Responsables nommés** : John Sotiropoulos (ASI Co-lead, Agentic Top 10 Chair),
> Keren Katz (Agentic Top 10 Lead), Ron F. Del Rosario (ASI Co-lead)

---

## La liste officielle — page « Agentic Top 10 At A Glance »

| Code | Intitulé officiel | En français, en clair | Applicable à RITA ? |
|---|---|---|---|
| **ASI01** | Agent Goal Hijack | Détournement de l'objectif de l'agent | ⬜ |
| **ASI02** | Tool Misuse & Exploitation | Mésusage et exploitation des outils | ⬜ |
| **ASI03** | Identity & Privilege Abuse | Abus d'identité et de privilèges | ⬜ |
| **ASI04** | Agentic Supply Chain Vulnerabilities | Failles de la chaîne d'approvisionnement agentique | ⬜ |
| **ASI05** | Unexpected Code Execution (RCE) | Exécution de code non prévue | ⬜ |
| **ASI06** | Memory & Context Poisoning | Empoisonnement de la mémoire et du contexte | ⬜ |
| **ASI07** | Insecure Inter-Agent Communication | Communication entre agents non sécurisée | ⬜ |
| **ASI08** | Cascading Failures | Défaillances en cascade | ⬜ |
| **ASI09** | Human-Agent Trust Exploitation | Exploitation de la confiance humain–agent | ⚠️ **PARTIELLEMENT** — décidé par Era le 17/08, voir ci-dessous |
| **ASI10** | Rogue Agents | Agents devenus incontrôlés | ⬜ |

---

## Ce que dit le document, entrée par entrée — et les faits RITA en face

Pour chaque entrée : la définition **résumée du PDF**, puis **le fait vérifié dans ton code**
(commande dans `_verifications-code-2026-S34.md`). **Le verdict reste à écrire par toi.**

### ASI01 — Agent Goal Hijack

> *« …les agents et le modèle sous-jacent ne peuvent pas distinguer de façon fiable les
> instructions du contenu associé. »* L'attaquant redirige les **objectifs**, la sélection de
> tâches ou les chemins de décision. **Différence avec LLM01:2025** : LLM01 vise une **réponse
> unique** ; ASI01 vise **l'objectif et le comportement multi-étapes**.

Exemple donné par OWASP, n°4 : *« l'injection indirecte force l'agent à produire une
information frauduleuse qui impacte des décisions métier. »*

**Fait RITA** : le graphe a 2 nœuds fixes (`graph/workflow.py:24-31`), pas de planification,
pas de sélection de tâche. Mais `analyst.py` **produit un texte lu par un investisseur**.
❓ *Question ouverte : sans planificateur, « détourner l'objectif » a-t-il encore un sens ici ?*

### ASI02 — Tool Misuse & Exploitation

> Mésusage d'outils **légitimes** par injection, désalignement ou délégation non sûre.

**Fait RITA** : `grep "tools=|bind_tools|@tool|ToolNode"` → **vide**. Aucun outil déclaré.

### ASI03 — Identity & Privilege Abuse

> Exploitation des chaînes de délégation, héritage de rôles, identifiants mis en cache.

**Fait RITA** : aucun agent délégant, aucun identifiant en cache côté agent.

### ASI04 — Agentic Supply Chain Vulnerabilities

> Composants tiers **chargés à l'exécution** : modèles, outils, plug-ins, serveurs **MCP**,
> registres d'agents. *« Contrairement aux chaînes logicielles classiques, les écosystèmes
> agentiques composent leurs capacités à l'exécution. »*

**Fait RITA** : ⚠️ **la seule entrée où RITA a une vraie surface.** Dépendances : `langgraph`,
`yfinance`, `httpx`, `feedparser`. Elles sont statiques (`requirements.txt`), donc plus proches
de LLM03:2025 que d'ASI04 — mais elles existent.

🔴 **Vérifié le 17/08 — et le résultat n'est pas bon** : `requirements.txt` contient
**13 dépendances**, dont **2 seulement sont épinglées** (`feedparser==6.0.14`,
`pyspark==4.2.0`). Les 11 autres — dont `anthropic`, `langgraph`, `yfinance`, `fastapi` —
sont **non versionnées** : `pip install` prend la dernière version publiée, qui peut changer
entre deux installations.

Recommandation OWASP ASI04 n°7, mot pour mot : *« Pin prompts, tools, and configs by content
hash and commit ID. »* Et n°2 : *« Allowlist and pin. »*
❓ *Est-ce un constat à porter dans la note S34, ou une action à ouvrir dans
`docs/FILE-DE-VALIDATION.md` ? À toi. C'est un défaut réel, trouvé par la veille — exactement
ce que la section « ce que ça change dans RITA » attend.*

### ASI05 — Unexpected Code Execution (RCE)

> L'agent génère et exécute du code ; `eval()`, désérialisation, appels shell.

**Fait RITA** : l'agent ne génère pas de code, n'exécute rien. Sortie = texte affiché.

### ASI06 — Memory & Context Poisoning

> Corruption **persistante** de la mémoire ou du contexte récupérable — résumés, embeddings,
> **stores RAG**. *« Exclut les prompts d'entrée ponctuels, couverts par LLM01:2025. »*
> Recommandation n°6 : *« Empêcher la ré-ingestion automatique des sorties générées par
> l'agent dans une mémoire de confiance, pour éviter l'auto-contamination. »*

**Fait RITA** : aucun checkpointer, aucun historique de conversation (V2). Pas de RAG dans le
graphe. **Mais** : `pipelines/ingest.py` écrit les articles scrapés en base, et l'API les
ressert. ❓ *Est-ce une « mémoire » au sens d'ASI06, ou un simple entrepôt de données ?
Le PDF dit « toute information qu'un agent retient, récupère ou réutilise » — RITA
« réutilise »-t-il ?*

### ASI07 — Insecure Inter-Agent Communication

> Agents qui communiquent par API, bus de messages, mémoire partagée. MCP, A2A.

**Fait RITA** : `scout` → `redacteur` en mémoire, dans un seul processus Python. Pas de réseau,
pas de protocole, pas de tiers.

### ASI08 — Cascading Failures

> Une faute unique (hallucination, entrée malveillante, mémoire empoisonnée) qui **se propage**
> entre agents autonomes et s'amplifie.

**Fait RITA** : 2 nœuds, puis `END`. Pas de boucle, pas de propagation possible.

### ASI09 — Human-Agent Trust Exploitation ⚠️ **celle qu'il ne faut pas sauter**

> *« Les agents peuvent établir une forte confiance avec les utilisateurs par leur aisance en
> langage naturel, leur intelligence émotionnelle apparente et leur expertise perçue —
> l'anthropomorphisme. »* Le risque est amplifié quand les humains **sur-comptent** sur des
> recommandations autonomes et **approuvent sans vérification indépendante**. Mécanismes
> nommés : **biais d'autorité**, **biais d'automatisation**, « explicabilité persuasive ».
> Conséquences citées : **pertes financières**.

**Fait RITA** : ❗ RITA **rédige des briefings financiers pour un investisseur particulier**.
Aucun outil, aucune mémoire — mais l'entrée ASI09 ne parle ni d'outil ni de mémoire. Elle parle
de **l'effet du texte sur la personne qui le lit**.
#### ⚠️ Verdict : PARTIELLEMENT APPLICABLE — décidé par Era, 17/08/2026

Première réponse « non applicable », **révisée le jour même** après vérification du prompt.
La révision est volontairement conservée : elle montre le raisonnement, pas seulement sa
conclusion.

| Niveau | Verdict | La preuve, par la commande |
|---|---|---|
| **Mécanisme de confiance** | ✅ **PRÉSENT** | `agents/analyst.py:21` — `Tu es un analyste financier français` : une **expertise déclarée et non prouvée**, adressée à un investisseur particulier. C'est le biais d'autorité décrit par ASI09 |
| **Chaîne d'impact** | ❌ **ABSENTE** | aucune recommandation (`analyst.py:35`), aucune approbation demandée, aucune action déclenchée. Le lecteur reste seul décideur |

**Ce que ça donne comme conclusion** : ASI09 décrit une chaîne — l'agent inspire confiance →
l'humain approuve sans vérifier → une action part → il y a perte. RITA possède **le premier
maillon et aucun des suivants**. Le risque ne peut pas se réaliser aujourd'hui, mais le
mécanisme qui l'amorce est bien dans le code, écrit à la main, ligne 21.

**Action qui en découle** — et c'est une action, pas un constat :

| Constat | Action pour RITA | Fichier | Fait ? |
|---|---|---|---|
| La persona « analyste financier » revendique une expertise que le modèle n'a pas (ASI09, biais d'autorité) | Reformuler la ligne 21 sans revendication d'expertise — p. ex. « Tu rédiges des synthèses factuelles de séance » | `agents/analyst.py:21` | ⬜ |

> 💡 **Pourquoi cette révision vaut mieux que la réponse initiale.** Devant un jury,
> « j'avais classé non applicable, puis j'ai relu mon prompt et j'ai trouvé le mécanisme
> ligne 21 » est plus fort que n'importe quel verdict tenu d'emblée. Ça montre la veille
> **en train de changer le projet** — l'objet même du critère C6.

### ASI10 — Rogue Agents

> Agents qui **dévient** de leur fonction. *« Les actions peuvent sembler légitimes
> individuellement, mais le comportement émergent devient nuisible. »* Porte sur la **perte
> d'intégrité comportementale après** la dérive, pas sur l'intrusion initiale.

**Fait RITA** : pas d'autonomie durable, pas d'état entre exécutions.

---

## Le concept transversal du document : **Least-Agency**

Page 7 du PDF, dans la lettre des responsables — à citer, il est court et il te sert :

> *« Nous étendons les concepts de moindre privilège et de pouvoir d'agir excessif en
> introduisant le **moindre pouvoir d'agir** (Least-Agency) : éviter l'autonomie inutile ;
> déployer un comportement agentique là où il n'est pas nécessaire élargit la surface
> d'attaque sans apporter de valeur. »*

Second point : *« une observabilité forte devient non négociable »* — sans visibilité sur ce
que font les agents, l'autonomie inutile transforme des incidents mineurs en défaillances
systémiques.

> 🔑 **Pourquoi ce terme vaut de l'or pour ton oral.** RITA applique *Least-Agency* — pas par
> stratégie de sécurité, mais parce que tu l'as construit simple. Tu disposes maintenant du
> **mot officiel OWASP** pour nommer cette propriété. Un jury entend la différence entre
> « mon agent est basique » et « mon agent applique le principe de moindre pouvoir d'agir ».

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **ASI** | *Agentic Security Initiative* — groupe de travail OWASP, et préfixe des dix entrées |
| **Least-Agency** | Moindre pouvoir d'agir : ne pas donner à un agent une autonomie dont il n'a pas besoin |
| **MCP** (*Model Context Protocol*) | Protocole standard par lequel un agent découvre et appelle des outils extérieurs |
| **A2A** (*Agent2Agent*) | Protocole de communication entre agents |
| **RAG** | Génération augmentée par récupération : on cherche des documents, on les donne au modèle |
| **Anthropomorphisme** | Prêter des qualités humaines à une machine — ici, lui accorder une confiance qu'on n'accorderait pas à un tableur |
| **Biais d'automatisation** | Tendance à accepter la sortie d'un système automatique sans la vérifier |
| **CC BY-SA 4.0** | Licence libre : réutilisation autorisée avec attribution et partage à l'identique |

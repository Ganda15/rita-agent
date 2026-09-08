# Candidats — semaine S37 (relevé du lundi 7 → mardi 8 septembre 2026)

> ⚠️ **Ce fichier n'est PAS la note de veille.** C'est la matière première : ce qui a été
> repéré, avec de quoi le vérifier. **La sélection, le jugement de fiabilité et la conclusion
> « ce que ça change dans RITA » restent à écrire** par Era dans `2026-S37-<sujet>.md`,
> à partir de `_MODELE-note-hebdomadaire.md`.
>
> **Période balayée** : du 1er au 8 septembre 2026 · **relevé le** 2026-09-08 *(un jour après
> le créneau du lundi — à noter tel quel dans la note plutôt que de l'antidater)*
> **Sources balayées** : OWASP GenAI Security Project, NIST AI RMF, CNIL, ANSSI / cyber.gouv.fr
> / CERT-FR, simonwillison.net · puis, en second rang, arXiv `cs.CR`.
> **Liens vérifiés** : chacun a répondu **HTTP 200** le 08/09/2026 (contrôle `curl`).

---

## 🟢 Le constat honnête d'abord : une seule vraie nouveauté, mais une nouveauté de poids

Quatre des cinq sources principales **n'ont rien publié de neuf** sur l'injection de prompt
entre le 1er et le 8 septembre (détail au §« Ce qui n'a rien donné »). L'exception est
**l'OWASP GenAI Security Project**, qui a fait cette semaine son annonce la plus importante
depuis le début de cette veille (14/08) : le **lancement officiel** du *Top 10 2026 for LLM
Applications* accompagné d'une **nouvelle norme**, l'*Agent Control Standard*. En second rang,
un préprint arXiv daté du 3 septembre traite précisément du scénario qui menace RITA :
l'injection **indirecte**, via du contenu tiers.

> 📖 **Injection de prompt** : texte glissé dans une donnée pour que le modèle le prenne pour
> une instruction. **Injection indirecte** : la même chose, cachée dans une page web ou un flux
> que l'agent va lire tout seul — c'est le cas qui menace RITA (`sources/scraper.py`,
> `sources/rss.py`).

⚠️ **Point de vigilance sur les dates** : le document *Top 10 2026* lui-même est daté du
**3 août 2026** et avait déjà été relevé en **S33** (voir `_candidats-2026-S36.md`, ligne
« déjà traité en S33 »). Ce qui est **réellement nouveau cette semaine**, ce n'est pas le
document, c'est son **lancement officiel public** (1–2 septembre) : l'annonce presse, le
franchissement des 30 000 membres, quatre nouveaux sponsors, et surtout la **donation de
l'Agent Control Standard**, qui n'existait dans aucun relevé précédent (vérifié par recherche
dans `docs/veille/` : aucune occurrence de « Agent Control Standard » avant ce fichier).

---

## 🔴 Candidat 1 — OWASP dévoile l'Agent Control Standard et fait évoluer le périmètre de LLM01

| | |
|---|---|
| **Source** | **OWASP GenAI Security Project** — fondation à but non lucratif, contributeurs nommés, aucun produit à vendre |
| **Titre** | *OWASP GenAI Security Project Unveils 2026 Top 10 for LLM Applications, New Agent Control Standard and Sponsors as Community Tops 30,000 Members* |
| **Date** | annonce le **1ᵉʳ–2 septembre 2026** (le document Top 10 lui-même est daté du 3 août — déjà connu depuis S33) |
| **Liens** | [Annonce officielle](https://genai.owasp.org/2026/09/01/owasp-genai-security-project-unveils-2026-top-10-for-llm-applications-new-agent-control-standard-and-sponsors-as-community-tops-30000-members/) · [Top 10 2026 for LLM Applications](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) · [Agent Control Standard (ACS)](https://genai.owasp.org/resource/agent-control-standard-acs/) · [Dépôt GitHub de l'ACS](https://github.com/GenAI-Security-Project/agent-control-standard) |

**Ce qui change, en deux volets.**

1. **LLM01 (injection de prompt) reste n°1**, comme en 2023, 2024 et 2025 — mais son
   **périmètre s'élargit** : la fiche 2026 couvre désormais explicitement les **attaques
   multimodales**, la **persistance en mémoire** et le **rayon d'action agentique**
   (*agentic blast radius* — l'étendue des dégâts qu'une injection réussie peut atteindre une
   fois qu'un agent a accès à des outils ou à un état persistant). Nuance de méthode à
   signaler : c'est la **première édition** à pondérer le classement avec des **données
   d'incidents réels (25 %)** en plus du vote communautaire (75 %) — ce qui explique que
   l'injection de prompt soit repartie *en tête du vote* mais *hors du top 10 des incidents
   documentés*, un écart qu'OWASP lit comme un effet des défenses déjà en place plutôt que
   comme une preuve d'innocuité *(lu dans des analyses tierces, à vérifier dans le document
   source avant citation ferme dans la note)*.
2. **L'Agent Control Standard (ACS)** est une **norme distincte**, pas une nouvelle version du
   Top 10 : elle définit comment une plateforme d'agents doit exposer des **points
   d'intervention** (middleware) et appliquer des **politiques de sécurité déclaratives**, pour
   qu'un agent soit **inspectable, traçable et pilotable** plutôt qu'une boîte noire.

**Lien avec RITA en une phrase** : RITA n'a ni outil ni exécution de code (établi en S33/S34),
donc l'ACS — pensé pour des agents qui *agissent* — ne s'applique pas tel quel ; mais
l'élargissement de LLM01 à la **persistance en mémoire** mérite d'être confronté au
`memory_audit` de RITA (garde-fou de mémoire non couvert par les 9 motifs regex actuels de
`guardrails/injection.py`, qui ne visent que le texte d'entrée).

---

## 🟠 Candidat 2 — Un préprint reformule l'injection indirecte comme un problème de recherche à l'exécution

| | |
|---|---|
| **Source** | arXiv `cs.CR` — ⚠️ **préprint, non relu par les pairs. Une piste, pas un fait.** |
| **Titre** | *Rethinking Indirect Prompt Injection as a Test-Time Search Problem* |
| **Auteurs** | Duong M. Nguyen, Joon Sik Kim, Blazej Manczak, Vaikkunth Mugunthan |
| **Date** | **3 septembre 2026** — dans la semaine balayée |
| **Lien** | [arXiv 2609.04495](https://arxiv.org/abs/2609.04495) |

**Ce que les auteurs proposent** : au lieu de traiter l'injection indirecte comme une attaque
figée, ils la modélisent comme une **recherche** que l'attaquant mène au moment de
l'exécution — un « agent attaquant » doté de son propre outillage de recherche (reconnaissance
du contenu, raisonnement stratégique, évaluation adaptative de ce qui marche). Résultat
annoncé : plus l'attaquant dispose de calcul au moment de l'attaque, plus il découvre et
exploite de vulnérabilités — y compris contre des défenses jugées solides jusqu'ici.

**Pourquoi c'est pertinent pour RITA sans trancher quoi que ce soit** : c'est exactement le
scénario que `sources/scraper.py` et `sources/rss.py` exposent — un contenu tiers, lu une
seule fois, sans que RITA ne « recherche » elle-même la meilleure formulation défensive. Le
préprint ne dit rien sur les garde-fous **par expression régulière** en particulier (ceux de
`guardrails/injection.py`) ; il vise surtout les défenses évaluées **statiquement**, contre un
seul type d'attaque à la fois. ⚠️ À croiser avec une source relue avant toute affirmation
ferme dans la note — un seul préprint ne suffit jamais (`README.md` §3).

---

## ❌ Ce qui n'a rien donné cette semaine — et le dire est un acte de veille

| Source | Vérification faite | Résultat |
|---|---|---|
| **ANSSI / cyber.gouv.fr** | [page Intelligence artificielle](https://cyber.gouv.fr/enjeux-technologiques/intelligence-artificielle/) — liste des publications lue | Dernière publication : **MEPIA**, 15 juillet 2026. **Rien en septembre** |
| **CERT-FR** | [flux d'actualité](https://www.cert.ssi.gouv.fr/actualite/) — dernier bulletin **CERTFR-2026-ACT-038** (7 septembre) lu | Porte sur des **vulnérabilités logicielles classiques** (JFrog, Google, HPE Aruba, Cisco, Mozilla, Microsoft, Tenable) — rien sur l'IA, comme en S34/S35/S36 |
| **CNIL** | [page Intelligence artificielle](https://www.cnil.fr/fr/intelligence-artificielle) consultée | Dernière mise à jour repérée : **26 août 2026** (outil de traçabilité des modèles open source, déjà hors fenêtre S36). Rien de nouveau entre le 1er et le 8 septembre |
| **NIST** | [page AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | **AI RMF 1.0 (2023) toujours en vigueur.** Le *Cyber AI Profile* (NIST IR 8596) est en préparation depuis décembre 2025, période de commentaires close le 30 janvier 2026 — rien de nouveau publié cette semaine |
| **Simon Willison** | [tag prompt-injection](https://simonwillison.net/tags/prompt-injection/) balayé | **Aucun billet entre le 27 août et le 8 septembre.** Le dernier reste *Breaking Claude Code Opus 5 Auto Mode* (27/08, déjà traité en S36) |

**Écarté par principe, comme en S33–S36** : les analyses de l'annonce OWASP publiées par des
éditeurs de solutions de sécurité (Invicti, Check Point, cybersecuritynews…). Motif inchangé :
**conflit d'intérêts direct** — ils décrivent le problème qu'ils vendent (`README.md` §3).
Utiles seulement pour confirmer des faits publics (ex. le maintien de LLM01 en tête), jamais
comme source d'une affirmation qui leur serait propre.

**Écarté aussi** : *Agents Rule of Two* (Meta, octobre 2025) et *The Attacker Moves Second*
(OpenAI/Anthropic/DeepMind, octobre 2025) — repérés en cherchant du côté de Simon Willison,
mais **déjà connus** (« lethal trifecta », traité en S33) et **hors de la semaine balayée**.

⚠️ **Conséquence à assumer dans la note** : sur les deux candidats retenus, **un seul est une
source primaire officielle relue** (OWASP) et l'autre est un **préprint isolé**. C'est un
résultat de veille correct — une semaine calme n'est pas une semaine vide.

---

## 🕳️ Le trou dans la suite des notes s'est creusé — deux semaines manquent, pas une

Les fichiers présents dans `docs/veille/` :

| Semaine | Candidats | **Note rédigée** (`AAAA-Sxx-sujet.md`) |
|---|---|---|
| S33 | ✅ `_candidats-2026-S33.md` | ✅ `2026-S33-injection-de-prompt.md` |
| S34 | ✅ `_candidats-2026-S34.md` | ✅ `2026-S34-top10-agentique.md` |
| **S35** | ✅ `_candidats-2026-S35.md` | 🔴 **MANQUANTE** — aucun `2026-S35-*.md` |
| **S36** | ✅ `_candidats-2026-S36.md` | 🔴 **MANQUANTE** — aucun `2026-S36-*.md` |
| S37 | ✅ ce fichier | ⬜ à écrire |

**Deux notes n'ont jamais été rédigées** (S35 et S36), alors que leurs relevés de candidats
existent déjà et sont riches — en particulier S35 (l'arbitrage du seuil à 85 %/70 %) et S36
(l'incident Claude Code + LongGuard sur la dilution de l'attention). **Un trou dans la suite
des numéros de semaine se voit d'un coup d'œil**, par soi-même comme par un évaluateur
(`README.md` §6) — et deux trous consécutifs se voient encore plus vite qu'un seul.

**Aucune option ici n'est « rattraper en écrivant trois notes d'un coup »** : cela produirait
trois notes datées du même jour, ce qui a le même défaut qu'antidater — la récurrence
hebdomadaire cesserait d'être lisible comme réelle. La voie honnête reste séquentielle :
traiter **une semaine par séance d'une heure**, dans l'ordre, en assumant dans chaque note le
retard qu'elle porte.

---

## ▶️ Ta séance d'une heure — proposition de déroulé

> ⚠️ Ce déroulé suppose que tu ouvres la plus ancienne semaine non traitée : **S35**. C'est
> elle qui porte la question la plus importante pour C6 (l'arbitrage du seuil de garde-fou),
> et c'est la plus ancienne — la traiter en premier respecte l'ordre chronologique.

| Temps | Quoi |
|---|---|
| **0–5 min** | Ouvrir `_candidats-2026-S35.md`, dater la note du jour réel où tu l'écris, le dire en tête |
| **5–45 min** | Suivre le déroulé déjà écrit dans `_candidats-2026-S35.md` (4 candidats sur l'arbitrage du seuil) |
| **45–55 min** | Remplir `2026-S35-<sujet>.md` depuis le gabarit, section **« Ce que ça change dans RITA »** obligatoire |
| **55–60 min** | Liste de contrôle d'accessibilité, commiter |

**Si une deuxième heure est possible dans la semaine** : enchaîner sur S36 (`_candidats-2026-S36.md`,
déroulé déjà écrit), puis seulement ensuite ouvrir ce fichier S37. L'ordre chronologique est ce
qui rend la récurrence crédible devant un jury.

---

## 📖 Glossaire de ce relevé

| Terme | En clair |
|---|---|
| **Injection de prompt** (*prompt injection*) | Texte glissé dans une donnée pour que le modèle le prenne pour une instruction |
| **Injection indirecte** | La même chose, cachée dans une page web ou un flux que l'agent lit tout seul |
| **Agent Control Standard (ACS)** | Norme ouverte de l'OWASP GenAI Security Project qui définit comment une plateforme d'agents doit exposer des points de contrôle et appliquer des politiques de sécurité, pour rendre un agent inspectable et pilotable plutôt qu'une boîte noire |
| **Rayon d'action agentique** (*agentic blast radius*) | L'étendue des dégâts qu'une injection de prompt réussie peut atteindre une fois que l'agent compromis a accès à des outils, à des données ou à un état persistant |
| **Persistance en mémoire** | Le fait qu'une instruction hostile glissée dans un échange survive dans la mémoire de l'agent et influence ses réponses ou actions bien après le message qui l'a introduite |
| **Recherche au moment de l'exécution** (*test-time search*) | Ici, le fait qu'un attaquant explore et ajuste sa stratégie d'attaque pendant l'interaction elle-même, plutôt que de préparer une seule attaque figée à l'avance |
| **Garde-fou** (*guardrail*) | Contrôle qui filtre ce qui entre ou sort d'un modèle |
| **Garde-fou par expression régulière** | Garde-fou qui compare le texte à des formes connues (motifs), comme les 9 motifs de `guardrails/injection.py` — par opposition à un garde-fou **par modèle** |
| **Préprint** | Article de recherche publié **avant** relecture par les pairs — une piste, pas une preuve |
| **RGAA** | Référentiel français d'accessibilité, obligatoire pour les sites publics |
| **AMF** | Autorité des marchés financiers — encadre le conseil en investissement en France |

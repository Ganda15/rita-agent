# Candidats — semaine S34 (relevé du lundi 17 août 2026)

> ⚠️ **Ce fichier n'est PAS la note de veille.** C'est la matière première : ce qui a été
> repéré, avec de quoi le vérifier. **La sélection, le jugement de fiabilité et la conclusion
> « ce que ça change dans RITA » restent à écrire** par Era dans
> `2026-S34-<sujet>.md`, à partir de `_MODELE-note-hebdomadaire.md`.
>
> **Période balayée** : du 10 au 17 août 2026 · **relevé le** 2026-08-17
> **Sources balayées** : OWASP GenAI Security Project, ANSSI / CERT-FR, CNIL, NIST,
> simonwillison.net · puis, en second rang, éditeurs de modèles et arXiv.
> **Liens vérifiés** : chacun a répondu **HTTP 200** au moment du relevé.
>
> 📎 **Annexe factuelle** : `_verifications-code-2026-S34.md` — les vérifications faites dans
> le code de RITA (outils déclarés, mémoire persistante, points d'appel du garde-fou), avec
> les commandes et leurs sorties. **Des faits, pas des conclusions.**

---

## 🟢 Le constat honnête d'abord : la semaine est maigre en source primaire

Quatre des cinq sources principales **n'ont rien publié de neuf** sur l'injection de prompt
entre le 10 et le 17 août. Le détail est au §« Ce qui n'a rien donné », plus bas — c'est un
résultat de veille, pas un blanc à combler.

Ce qui reste tient en **cinq candidats**, dont deux répondent directement à la question
ouverte laissée par la note S33.

---

## 🔴 Candidat 1 — OWASP « Top 10 for Agentic Applications » 2026 (ASI01 → ASI10)

| | |
|---|---|
| **Source** | OWASP GenAI Security Project |
| **Auteur** | fondation OWASP — à but non lucratif ; annoncé comme relu par plus de 100 experts nommés |
| **Date de publication** | **9 décembre 2025** — ⚠️ **ce n'est pas une nouveauté de la semaine** |
| **Lien** | [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) |
| **Document** | [Téléchargement du Top 10 for Agentic Applications 2026](https://genai.owasp.org/download/52117) |

**Pourquoi il est en tête malgré sa date** : c'est **exactement la question que tu as posée en
fin de note S33** — *« les risques propres aux applications agentiques recoupent-ils ceux des
applications LLM, ou en ajoutent-ils ? »*. Ne pas y répondre en S34 laisserait la question
ouverte deux semaines de suite.

**Ce qui est rapporté** (à vérifier dans le document, pas dans les résumés) : la liste
n'utilise plus les identifiants `LLM01…` mais `ASI01…ASI10` — *ASI* pour **Agentic Security
Initiative**, le groupe de travail OWASP qui la produit. Elle couvrirait notamment le
**détournement d'objectif** (*goal hijack*), le **mésusage d'outil** (*tool misuse*), l'
**empoisonnement de mémoire** (*memory poisoning*) et les **agents devenus incontrôlés**
(*rogue agents*).

**Lien possible avec RITA** : RITA **est** une application agentique — graphe LangGraph, deux
nœuds `scout` puis `redacteur`. La note S33 a établi que RITA n'a **aucun outil déclaré** et
**aucune écriture en base depuis l'agent** ; trois des dix entrées annoncées (mésusage d'outil,
agents incontrôlés, communication inter-agents) pourraient donc **ne pas s'appliquer**. À
l'inverse, l'**empoisonnement de mémoire** mérite un vrai examen : RITA relit-il en entrée du
texte qu'il a lui-même stocké en base à l'étape précédente ?

---

## 🔴 Candidat 2 — Simon Willison sur le mode « auto » de Claude Code

| | |
|---|---|
| **Auteur** | **Simon Willison** — co-créateur de Django, a **créé le terme *prompt injection* en 2022** |
| **Intérêts** | blog personnel, ne vend aucune solution de sécurité |
| **Date de publication** | **8 août 2026** (le changement décrit, lui, a pris effet le **14 août** — donc dans la semaine) |
| **Lien** | [Auto mode is now the default in Claude Code for Pro, Max, and Team plans](https://simonwillison.net/2026/Aug/8/auto-mode/) |
| **Source commentée** | [Annonce Anthropic — Auto mode is now the default in Claude Code](https://claude.com/blog/auto-mode-default-in-claude-code) ⚠️ **éditeur du modèle — intérêt commercial direct** |

**Les chiffres cités** — à reprendre uniquement en signalant qui les a produits :

| Mesure | Valeur | Qui l'a produite |
|---|---|---|
| Testeurs humains ayant **refusé** une commande dangereuse glissée à la place d'une demande d'autorisation | **13,6 %** (sur 1 053 testeurs) | Anthropic |
| Mêmes actions dangereuses **bloquées par le classifieur** du mode auto | **89 %** — donc **11 % passent** | Anthropic |
| Scénarios d'**injection indirecte** testés par un tiers | **720 tentatives, 0 réussite** (72 scénarios) | **Trajectory Labs** — évaluation tierce |

**La position de l'auteur, et c'est là que ça devient une source de veille** : Willison est
**convaincu à moitié**. Il accepte l'idée qu'un classifieur automatique fasse mieux qu'un
humain lassé de cliquer « oui » — mais il **réclame une confirmation indépendante** sur le
volet injection et rappelle qu'il prédit *« une catastrophe de sécurité des agents de code »*
pour 2026. Sa conclusion : le **bac à sable** (*sandbox*) reste indispensable, quel que soit
le classifieur.

> 📖 **Classifieur** : petit modèle placé devant l'action, qui décide « autorisé / bloqué »
> avant qu'elle ne s'exécute. C'est un garde-fou **en sortie de raisonnement**, pas en entrée.

**Lien possible avec RITA** : ton garde-fou est une **liste de 9 motifs en expression
régulière** (`guardrails/injection.py`) — il compare du texte à des formes connues. Ce que
décrit Willison est un **second modèle qui juge**. Deux approches, deux coûts, deux taux
d'erreur. La question à trancher pour RITA : *un classifieur apporterait-il quelque chose que
9 regex n'apportent pas, et à quel prix en latence ?* Tu as déjà l'outil pour répondre —
`evals/mesurer_gardefou.py` mesure taux de blocage, faux positifs **et latence**.

---

## 🟠 Candidat 3 — Préprint : les défenses « hors bande » cèdent face aux attaques adaptatives

| | |
|---|---|
| **Source** | arXiv `cs.CR` — ⚠️ **préprint : non relu par les pairs. Une piste, pas un fait.** |
| **Titre** | *Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents* |
| **Auteurs** | Praneeth Narisetty, Shiva Nagendra Babu Kore, Uday Kumar Reddy Kattamanchi, Jayaram Kumarapu |
| **Date** | **25 juin 2026** — pas de la semaine, mais jamais relevé jusqu'ici |
| **Lien** | [Adaptive Evaluation of Out-of-Band Defenses Against Prompt Injection in LLM Agents (arXiv 2606.26479)](https://arxiv.org/abs/2606.26479) |

**Ce qui est annoncé dans le résumé** : les auteurs testent cinq défenses « hors bande »
(CaMeL, FIDES, Progent, RTBAS, FORGE) sur le banc d'essai *AgentDojo*. Une défense (Progent)
fait tomber le taux de réussite des attaques de **25,8 % à 4,2 %**. Mais surtout : des attaques
**conçues en connaissance de la défense** en cassent **douze avec plus de 90 % de réussite** —
alors que ces défenses étaient validées sur des jeux d'attaques **figés**.

> 📖 **Défense « hors bande »** (*out-of-band*) : on ne demande pas au modèle de refuser ; on
> place **en dehors du modèle** une règle déterministe qui autorise ou interdit ses actions.
> C'est la famille à laquelle appartient ton `guardrails/injection.py`.
> 📖 **Attaque adaptative** : attaque écrite **après** avoir lu la défense, pour la contourner
> précisément — par opposition à une liste d'attaques préparée à l'avance.

**Lien possible avec RITA — et c'est potentiellement le point qui dérange** : `evals/mesurer_gardefou.py`
mesure ton garde-fou sur un **jeu de cas figé**, et `tests/test_evals.py` verrouille les seuils
obtenus en intégration continue. C'est exactement le protocole que ce préprint dit
insuffisant. Ton taux de blocage ne mesure peut-être pas « la sécurité », mais « la couverture
des 9 motifs que j'ai écrits ». **Une veille qui remet en cause ta propre approche vaut plus
qu'une veille qui la confirme** — et un jury le verra.
⚠️ Préprint : à croiser avec OWASP ou l'ANSSI avant d'en faire une affirmation.

---

## 🟠 Candidat 4 — CNIL + Conseil de l'IA et du Numérique : note exploratoire sur l'IA agentique

| | |
|---|---|
| **Source** | **CNIL** — autorité administrative indépendante, aucun intérêt commercial, site public soumis au RGAA |
| **Date** | **20 juillet 2026** — jamais relevé jusqu'ici |
| **Lien** | [IA agentique et données personnelles : la CNIL et le CIANum publient une note exploratoire](https://www.cnil.fr/fr/ia-agentique-cnil-cianum-note) |
| **Document** | [IA agentique et protection des données personnelles (PDF)](https://www.cnil.fr/sites/default/files/2026-07/ia-cianum-cnil.pdf) |

**Ce qui est rapporté** : le passage de l'IA générative à l'IA **agentique** est décrit comme
un changement d'échelle qui **amplifie** les risques pour les données personnelles — l'agent
accède à de nombreuses sources, **fait circuler** des données entre services, et conserve un
historique par des **mécanismes de mémoire persistante** qui favorisent des profils très
détaillés. Le risque nommé : la **perte de contrôle** de l'utilisateur sur ses données.

**Lien possible avec RITA** : c'est une source **française et officielle** qui parle
d'agentique — rare, et précieuse devant un jury qui demande *« sur quel cadre national vous
appuyez-vous ? »*. Elle touche directement ton `db/RGPD-registre-des-traitements.md` : RITA
a-t-il une mémoire persistante des interactions, et si oui, est-elle au registre ?

---

## ⚪ Candidat 5 — NIST : profil AI RMF pour les infrastructures critiques (note de cadrage)

| | |
|---|---|
| **Source** | NIST — agence fédérale américaine, aucun intérêt commercial |
| **Date** | **7 avril 2026** — note de cadrage (*concept note*) |
| **Lien** | [AI Risk Management Framework — page officielle NIST](https://www.nist.gov/itl/ai-risk-management-framework) |

**État constaté** : **l'AI RMF 1.0 (janvier 2023) reste le cadre en vigueur — aucune version
2.0 publiée.** Les évolutions de 2026 sont des *profils* sectoriels et des annexes, pas une
refonte. **Rien de neuf cette semaine.**

**Lien possible avec RITA** : faible. À garder comme source de cadrage, pas comme actualité.
Le mentionner dans la note **uniquement** pour prouver que la source a été consultée.

---

## ❌ Ce qui n'a rien donné cette semaine — et le dire est un acte de veille

| Source | Vérification faite | Résultat |
|---|---|---|
| **OWASP GenAI** | page ressources consultée | rien de neuf depuis le Top 10 LLM 2026 du **3 août** (déjà traité en S33) |
| **CERT-FR / ANSSI** | [Bulletin d'actualité CERTFR-2026-ACT-034](https://www.cert.ssi.gouv.fr/actualite/CERTFR-2026-ACT-034/), 10 août 2026 — **lu en entier** | ⚠️ **sans rapport avec l'IA** : WordPress, Cisco, Tenable, Check Point. **Ne pas le citer dans une note sur l'injection de prompt.** |
| **CNIL** | [Page Intelligence artificielle de la CNIL](https://www.cnil.fr/fr/intelligence-artificielle) | dernière publication : **20 juillet 2026** (candidat 4). Rien entre le 10 et le 17 août |
| **NIST** | page AI RMF | rien depuis avril 2026 (candidat 5) |
| **Simon Willison** | blog balayé sur la période | un seul billet sécurité : le **8 août** (candidat 2). Les billets des 10 et 16 août portent sur des sorties de modèles, hors thématique |

**Écartés par principe, comme en S33** : les blogs d'éditeurs de sécurité LLM commentant le
Top 10 (Cycode, Mend, HackerDNA, aisecurityplatform…) et les sites d'actualité agrégée.
Motif : **conflit d'intérêts direct** — ils décrivent le problème qu'ils vendent
(`README.md` §3). Ils ne sont pas faux ; ils ne sont **pas indépendants**.

---

## ▶️ Ta séance d'une heure — proposition de déroulé

| Temps | Quoi |
|---|---|
| **0–5 min** | Relire la question ouverte de la note S33 : *« l'agentique ajoute-t-elle des risques que RITA ne traite pas ? »* C'est le sujet de la semaine. |
| **5–25 min** | Ouvrir le **Top 10 for Agentic Applications 2026** (candidat 1). Noter les 10 entrées ASI01→ASI10 **telles qu'elles sont écrites**, pas telles que les blogs les résument. |
| **25–40 min** | Pour chacune : **applicable à RITA — oui / non / à vérifier**, avec la commande qui le prouve. Cible d'attention : **empoisonnement de mémoire**. |
| **40–50 min** | Lire le billet de Willison (candidat 2). Trancher : **regex ou classifieur** pour RITA ? Une ligne de conclusion suffit, mais elle doit être argumentée par la latence. |
| **50–58 min** | Remplir la note depuis le gabarit — surtout **« Ce que ça change dans RITA »**. Si la réponse est « rien », l'écrire **et dire pourquoi**. |
| **58–60 min** | Liste de contrôle d'accessibilité, enregistrer, commiter. |

**Si tu as 10 minutes de plus** : le préprint (candidat 3) est celui qui a le plus de valeur
devant un jury, parce qu'il attaque **ta propre méthode de mesure**.

---

## 📖 Glossaire de ce relevé

| Terme | En clair |
|---|---|
| **Application agentique** | Programme où le modèle ne se contente pas de répondre : il enchaîne des étapes, garde une mémoire, et peut appeler des outils |
| **ASI** | *Agentic Security Initiative* — le groupe de travail OWASP qui produit le Top 10 agentique ; sert aussi de préfixe aux entrées (ASI01…) |
| **Classifieur** | Petit modèle qui juge « autorisé / bloqué » avant qu'une action ne s'exécute |
| **Défense hors bande** (*out-of-band*) | Règle placée **en dehors** du modèle, qui autorise ou interdit ses actions — la famille de `guardrails/injection.py` |
| **Attaque adaptative** | Attaque écrite après avoir lu la défense, pour la contourner précisément |
| **Empoisonnement de mémoire** | Faire écrire à l'agent, dans sa propre mémoire, un texte hostile qu'il relira plus tard comme une consigne |
| **Bac à sable** (*sandbox*) | Environnement isolé où une action dangereuse ne peut pas atteindre le vrai système |
| **Préprint** | Article de recherche publié **avant** relecture par les pairs — une piste, pas une preuve |
| **RGAA** | Référentiel français d'accessibilité, obligatoire pour les sites publics |

# Candidats : semaine S46 (relevé du lundi 9 novembre 2026)

> ⚠️ **Ce fichier n'est PAS la note de veille.** C'est la matière première : ce qui a été
> repéré, avec de quoi le vérifier. **La sélection, le jugement de fiabilité et la conclusion
> « ce que ça change dans RITA » restent à écrire** par Era dans `2026-S46-<sujet>.md`,
> à partir de `_MODELE-note-hebdomadaire.md`.
>
> **Période balayée** : du lundi 2 au lundi 9 novembre 2026 (la semaine écoulée, S45, plus le matin du relevé).
> ⚠️ **Trou non balayé** : du 12 octobre au 1er novembre 2026. Le relevé précédent date du 11/10
> (`_candidats-2026-S41.md`) ; S42, S43 et S44 n'ont eu ni relevé ni note. Ce relevé ne les rattrape pas.
> **Relevé le** : 2026-11-09, par une tâche planifiée de l'assistant de développement (lecture des flux et des pages),
> en lecture seule. Aucune note n'avait été écrite lors de ce relevé initial.
> **Mise à jour du 09/11** : candidat 2 précisé après lecture de l'article ; contrôle ANSSI complété dans le navigateur.
> **Sources balayées** : OWASP GenAI Security Project, ANSSI / cyber.gouv.fr, CERT-FR, CNIL, NIST, simonwillison.net,
> puis arXiv (API de recherche, « prompt injection » dans le résumé, trié par date de dépôt).
> **Liens vérifiés** : chacun a répondu **HTTP 200** le 09/11/2026 (contrôle `curl`). Un 200 dit qu'une page est
> **accessible**, pas qu'elle est fiable ni que son résumé ici est exact : relire chaque candidat dans sa source.
> **Déjà vu, écarté** : aucun candidat ci-dessous ne figure dans les relevés précédents (vérifié dans `docs/veille/`).

---

## Bilan de la recherche : six candidats à croiser

Aucune nouveauté sur l'injection de prompt n'a été retenue dans les pages consultées des six sources principales
(détail au « Bilan des sources »). Ce constat ne garantit pas une recherche exhaustive. Les six candidats viennent
d'arXiv ; leur validation par les pairs n'est pas établie ici. Leurs résultats doivent être croisés.

Deux préprints touchent directement le garde-fou de RITA. Le premier montre qu'un filtre par expressions régulières
peut produire peu de fausses alertes tout en détectant peu d'attaques. Le second étudie des attaques qui influencent
la tâche par des informations trompeuses, sans nécessairement donner d'ordre explicite.

> 📖 **Injection de prompt** : texte glissé dans une donnée pour que le modèle le prenne pour une instruction.
> **Injection indirecte** : la même chose, cachée dans un contenu que l'agent lit tout seul (pour RITA, les articles
> des flux RSS de `sources/rss.py`, indexés puis remontés dans le prompt du rédacteur).
> **Expression régulière (regex)** : motif de texte qu'un programme cherche dans une chaîne, par exemple
> « ignore ... previous instructions ».

**État du garde-fou relu le 09/11 (pour comparer)** : `guardrails/injection.py` contient **12 motifs nommés**
(lignes 21 à 37, FR et EN) et une détection de **consigne déguisée** qui combine plusieurs familles de mots
(lignes 50 à 66). Le texte de la tâche planifiée parle encore de « 9 motifs » : ce chiffre est périmé.

---

## Candidat 1 : cinq regex face à onze détecteurs, sur des contrats juridiques

| | |
|---|---|
| **Source** | arXiv, catégorie `cs.AI` (source 7, hors `cs.CR` strict). ⚠️ **Préprint, non relu par les pairs** |
| **Titre** | *Notwithstanding Anything to the Contrary, Ignore All Instructions: Measuring Prompt Injection Guards on Legal Contract Review Attacks* |
| **Auteurs** | Mark Heimann, Katherine Taylor, Bruno Jacob, tous chez **Ivo AI** (en-tête de l'article) |
| **Date** | déposé (v1) le **6 novembre 2026** |
| **Liens** | [arXiv 2611.08834](https://arxiv.org/abs/2611.08834) · [site d'Ivo AI](https://www.ivo.ai/) |
| **Intérêt commercial** | ⚠️ **Oui** : Ivo vend un logiciel d'analyse de contrats par IA, et l'article conclut en faveur d'une solution par LLM en cascade |

**Ce que décrivent les auteurs.** Onze détecteurs à poids ouverts (dont Prompt Guard 2 de Meta, ProtectAI v2, PIGuard)
sont testés sur deux corpus de contrats en anglais. Plusieurs bloquent de nombreux contrats sains.
La base de **cinq regex** n'est dominée simultanément sur les deux critères par aucun des détecteurs comparés.
Elle produit 0,29 % de faux positifs sur le corpus interne et 0 % sur CUAD, mais son **rappel est de 22,2 %**
(tableau 1) : près de huit attaques sur dix du test ne sont pas détectées. Ce rappel est identique sur les deux
corpus, car les motifs se déclenchent sur le texte de l'attaque. Les attaques et le jeu de contrôle sont publiés
(lien OSF dans l'article) ; le corpus propriétaire ne l'est pas.

**Piste possible pour RITA** : conserver les motifs comme un premier contrôle et mesurer à la fois les attaques
bloquées et les contenus sains bloqués à tort. Le faible taux de faux positifs ne prouve pas une protection
suffisante, ni que le filtre de RITA obtient les mêmes résultats. Les cinq regex recoupent en partie
`ignore_instructions_en` et `disregard_en`, mais le domaine juridique anglophone diffère des articles financiers.
L'intérêt commercial d'Ivo AI reste à prendre en compte.

---

## Candidat 2 : influencer la tâche sans nécessairement donner d'ordre (« task tampering »)

| | |
|---|---|
| **Source** | arXiv `cs.CR` (source 7). ⚠️ **Préprint, non relu par les pairs** |
| **Titre** | *Beyond Instruction Override: Benchmarking Indirect Prompt Injection with Task-Tampering Attacks* |
| **Auteurs** | Rongting Zhang, Martin Bertran, Sandeep Avula, Chia-Jung Lee, Vanessa Murdock. L'en-tête de l'article mentionne **Amazon Responsible AI** et précise qu'Avula a réalisé le travail chez Amazon et est désormais chez Microsoft. Le code est publié sous **amazon-science** |
| **Date** | déposé (v1) le **5 novembre 2026** |
| **Liens** | [arXiv 2611.07640](https://arxiv.org/abs/2611.07640) · [le code et les données](https://github.com/amazon-science/task-tampering-prompt-injection) |
| **Intérêt commercial** | Lien commercial établi par les affiliations Amazon et Microsoft ; intérêts personnels non vérifiés |

**Ce que décrivent les auteurs.** Ils définissent l'injection par **l'autorité** et non par la formulation : un contenu
est une attaque s'il tente d'influencer une décision que sa source n'a pas le droit de trancher. Exemple : une
réclamation qui cite une fausse politique de remboursement, sans phrase d'ordre. Sur 90 cas, **DRIFT-iso**, une
défense de détection et retrait, laisse réussir 2,4 % des attaques visant l'objectif, 9,5 % de celles visant
l'observation et 12,1 % de celles visant l'état supposé (tableau 3). Ce ne sont pas des mesures du filtre RITA.

**Piste possible pour RITA** : tester ce qui se passe lorsqu'un article affirme un faux chiffre ou une fausse
« politique de la direction ». L'étude n'évalue pas de filtre par regex et ne prouve donc pas leur échec. Elle
invite à examiner l'autorité des sources et les contradictions. Garder le filtre actuel et compléter les essais
est une piste pour RITA, pas un résultat démontré par cet article.

---

## Candidat 3 : neuf dimensions pour décrire une injection

| | |
|---|---|
| **Source** | arXiv `cs.CR` (source 7). ⚠️ **Préprint, non relu par les pairs** |
| **Titre** | *The Devil is in the Context: Nine Dimensions of Prompt Injection Attacks* |
| **Auteurs** | dix auteurs, dont sept au **Microsoft Security Response Center** (Andrew Paverd, Ahmed Salem, Giovanni Cherubin...), et Hammond Pearce (University of New South Wales), d'après l'en-tête |
| **Date** | déposé (v1) le **3 novembre 2026** |
| **Lien** | [arXiv 2611.04672](https://arxiv.org/abs/2611.04672) |
| **Intérêt commercial** | ⚠️ **Oui** : Microsoft est éditeur et fournisseur de modèles |

**Ce que décrivent les auteurs.** Une taxonomie en neuf dimensions : source de confiance ou non, fragmentation,
visibilité pour l'utilisateur, lisibilité de l'instruction (encodée ou non), conditionnalité, modification de la
mémoire de l'agent, lien avec le sujet de la tâche, effet visé (actions ou seulement leurs arguments), et
achèvement ou non de la tâche d'origine. Ils disent qu'évaluer une défense sur un seul type d'injection donne un
faux sentiment de sécurité. L'article ne traite pas des détecteurs par regex.

**Piste possible pour RITA** : une grille pour classer les 18 cas de `evals/` et voir quelles dimensions ne sont pas
couvertes (par exemple fragmentation, déjà signalée en S41, ou instruction encodée).

---

## Candidat 4 : filtrer une page avant qu'elle n'entre dans le contexte

| | |
|---|---|
| **Source** | arXiv, catégorie `cs.AI`. ⚠️ **Préprint.** Le commentaire annonce « Accepted at IEEE ICCC 2026 » ; non vérifié |
| **Titre** | *SearchInject: Retrieval Exposure Control for Indirect Prompt Injection in Language-Model Search* |
| **Auteurs** | Kainan Zhou, Gangzhen Qian, Janet Sung, Zhi Jing, Rong Bao, Qianru Lao ; affiliations non affichées. ⚠️ Deux auteurs figurent déjà au candidat 5 de S41 (*Bounded Provisional Visibility*) : même équipe, pas une confirmation indépendante |
| **Date** | déposé (v1) le **2 novembre 2026** |
| **Lien** | [arXiv 2611.02643](https://arxiv.org/abs/2611.02643) |
| **Intérêt commercial** | Non établi |

**Ce que décrivent les auteurs.** Un score qui décide si une page récupérée peut entrer dans le contexte du modèle
(pertinence, indices d'abus, probabilité d'instruction). Le seuil est fixé pour ne mettre en quarantaine à tort que
0,5 % des pages saines (0,59 à 0,65 % mesuré en test). L'exposition des pages piégées dans le top 10 baisse d'environ
83 %. Limite reconnue : aucune réduction du taux de réussite des attaques n'a pu être mesurée.

**Piste possible pour RITA** : la méthode « fixer d'abord le taux de faux positifs acceptable, puis le seuil » rejoint
la recommandation du candidat 4 de S41 pour `evals/mesurer_gardefou.py`.

---

## Candidat 5 : l'agent web qui ne voit jamais la page avant d'avoir planifié

| | |
|---|---|
| **Source** | arXiv `cs.CR` (source 7). ⚠️ **Préprint, non relu par les pairs** |
| **Titre** | *Securing Web Agents with the Compile-Then-Execute Paradigm* |
| **Auteurs** | Annabella Chow, Jinhao Zhu, Sylvie Venuto, Abdulaziz Alharbi, Basel Alomair, Raluca Popa, **David Wagner**, Julien Piet. Affiliations non affichées ; un David Wagner, professeur de sécurité à Berkeley, a une [page à l'UC Berkeley](https://people.eecs.berkeley.edu/~daw/). ⚠️ Lien entre les deux à confirmer dans le PDF |
| **Date** | déposé (v1) le **4 novembre 2026** |
| **Lien** | [arXiv 2611.06039](https://arxiv.org/abs/2611.06039) |
| **Intérêt commercial** | Non repéré |

**Ce que décrivent les auteurs.** L'agent Baya traduit d'abord la demande en programme Python, sans lire le site ;
le contenu non fiable peut ensuite remplir des valeurs ou choisir entre des branches prévues, mais pas inventer de
nouvelles actions. Résultats : 0 % de réussite des attaques sur le banc WASP, contre 16,2 % et 25,5 % pour deux
agents ReAct, et une meilleure utilité (77,8 %).

**Piste possible pour RITA** : c'est une défense **par architecture** et non par filtrage ; RITA s'en rapproche déjà
en partie (le rédacteur n'a pas d'outil d'action), ce qui peut servir d'argument pour la note.

---

## Candidat 6 : ce qu'un serveur MCP peut corriger seul, et ce qu'il ne peut pas

| | |
|---|---|
| **Source** | arXiv `cs.CR` (source 7). ⚠️ **Préprint, non relu par les pairs** |
| **Titre** | *Where Does MCP Security End? A Three-Tier Mitigation Mapping Framework for the OWASP MCP Top 10* |
| **Auteurs** | Christopher Krakauer, Andreas Schaad ; affiliations non affichées, notoriété non vérifiée |
| **Date** | déposé (v1) le **2 novembre 2026** |
| **Liens** | [arXiv 2611.02611](https://arxiv.org/abs/2611.02611) · [le projet OWASP MCP Top 10](https://owasp.org/www-project-mcp-top-10/) (source 1, à lire en premier) |
| **Intérêt commercial** | Non repéré |

**Ce que décrivent les auteurs.** Ils répartissent les dix risques de l'OWASP MCP Top 10 en trois niveaux : ce que le
serveur corrige, ce qui relève d'une passerelle, et ce qui relève du protocole lui-même. Validation sur un serveur MCP
de transfert de fichiers écrit en Go : les contrôles côté serveur tiennent, ceux qui relèvent du protocole échouent.
Conclusion : le développement sûr réduit la surface d'attaque, il ne la supprime pas.

**Piste possible pour RITA** : RITA expose une passerelle MCP en lecture seule ; la grille dirait ce qu'elle couvre
déjà et ce qui ne dépend pas d'elle. Le projet OWASP MCP Top 10 lui-même n'a pas encore été traité en veille.

---

## Autres préprints de la semaine, repérés et non retenus

| Date (v1) | Titre | Lien | Pourquoi non retenu |
|---|---|---|---|
| 06/11 | *I Think, Therefore I Attack: Evaluating Thought Injection Attacks on Reasoning Agents* | [arXiv 2611.08811](https://arxiv.org/abs/2611.08811) | vise les modèles de raisonnement à poids ouverts dans un « cyber range » ; loin de l'usage de RITA |
| 04/11 | *SecureGARD: Dynamic Ontology-Guided Governance for Secure Tool-Using LLM Agents* | [arXiv 2611.06682](https://arxiv.org/abs/2611.06682) | contrôle des appels d'outils ; RITA n'en donne pas au rédacteur |
| 03/11 | *Right Tool, Wrong Parameters: Defending LLM Agents Against Parameter Poisoning* | [arXiv 2611.04673](https://arxiv.org/abs/2611.04673) | même idée que le candidat 2, appliquée aux arguments d'outils |
| 03/11 | *ScamWorld: An Interactive Environment for Evaluating Web Agents Against Online Fraud* | [arXiv 2611.04879](https://arxiv.org/abs/2611.04879) | agents qui achètent en ligne ; hors du périmètre de RITA |
| 03/11 | *From Guidelines to Practice: Defining Requirements for AI Red-Teaming Tools* | [arXiv 2611.04271](https://arxiv.org/abs/2611.04271) | catégorie `cs.CY`, porte sur le choix d'outils de test, pas sur l'injection |
| 02/11 | *ATrust: Adaptive Trust Boundary Expansion for Securing LLM Agents* | [arXiv 2611.02741](https://arxiv.org/abs/2611.02741) | agents autonomes à actions ; RITA n'en a pas |
| 02/11 | *StateFence: Task-State Protection Against Evidence-Chain Contamination in Blue-Team LLM Agents* | [arXiv 2611.02605](https://arxiv.org/abs/2611.02605) | agents de centre de sécurité (SOC) ; l'idée « une chaîne suspecte peut être une preuve utile » rejoint le candidat 2 |
| 02/11 | *LEANGUARD: Lean-Verified Guardrails for Tool-Using Agents* | [arXiv 2611.02332](https://arxiv.org/abs/2611.02332) | politiques prouvées en Lean4 sur les appels d'outils ; hors besoin |

---

## Bilan des sources (ce qui n'a rien donné compte aussi)

| Source | Résultat du 2 au 9 novembre |
|---|---|
| 1. OWASP GenAI | **rien de nouveau** : dernier billet du [blog](https://genai.owasp.org/blog/) le 08/10 (bilan du 3e trimestre, déjà en S41) |
| 2. ANSSI | **Contrôle complété dans le navigateur le 09/11** : les [actualités](https://cyber.gouv.fr/actualites/) affichent en tête une publication du 12/10/2026 ; les références de la [page IA](https://cyber.gouv.fr/enjeux-technologiques/intelligence-artificielle/) sont antérieures à novembre. Aucune publication sur l'injection datée du 02/11 au 09/11 n'a été trouvée dans ces deux pages. Ce contrôle ne couvre pas tout le site. L'outil initial renvoyait un contenu vide ; la cause de cette différence n'est pas établie. |
| 3. CERT-FR | **rien sur le sujet** : le [bulletin ACT-046](https://cert.cyber.gouv.fr/actualite/CERTFR-2026-ACT-046/) du 02/11 ne mentionne ni IA ni LLM. Le site a changé d'adresse (`cert.ssi.gouv.fr` redirige vers `cert.cyber.gouv.fr`) |
| 4. CNIL | **rien sur le sujet** : [actualités](https://www.cnil.fr/fr/actualites) du 04 au 06/11 sur le rejeu de session, la santé, les enfants. Hors fenêtre, la [Journée RGPD de Poitiers](https://www.cnil.fr/fr/journee-rgpd-2026-poitiers) (20/10) cite l'IA dans son titre |
| 5. NIST | **rien dans la fenêtre** : sur la [page CAISI](https://www.nist.gov/caisi), dernier élément le 16/10 (réponse aux incidents en entraînement de modèles), lien non donné car il n'a pas répondu (`000`) |
| 6. Simon Willison | **aucun billet étiqueté** `prompt-injection` depuis le 17/09 ([l'étiquette](https://simonwillison.net/tags/prompt-injection/)) ; ses billets du 2 au 9/11 ne parlent pas d'injection |
| 7. arXiv | **abondant** : 16 préprints mentionnant l'injection de prompt dans leur résumé, du 2 au 6/11 ; 6 retenus, 8 listés non retenus, 2 écartés sans mention (interfaces de chat, données de santé : l'injection n'y est qu'un point secondaire) ([liste récente `cs.CR`](https://arxiv.org/list/cs.CR/recent)) |

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| Injection indirecte | instruction hostile cachée dans un contenu que l'agent lit tout seul (page web, flux RSS, article récupéré) |
| Préprint | article déposé sans relecture par les pairs : une piste, pas un fait |
| Expression régulière (regex) | motif de texte recherché automatiquement dans une chaîne |
| Faux positif | contenu sain bloqué à tort |
| Détecteur à poids ouverts | petit modèle classifieur téléchargeable, qu'on fait tourner soi-même |
| LLM en cascade | un modèle moyen trie, un modèle plus puissant ne vérifie que les cas signalés |
| Taxonomie | classement organisé des types d'un phénomène |
| ReAct | façon de faire travailler un agent : il observe, raisonne, agit, puis recommence |
| MCP | Model Context Protocol : protocole qui expose des outils et des données à un modèle |
| Passerelle (gateway) | intermédiaire placé entre l'agent et les serveurs d'outils, qui filtre et contrôle |
| Quarantaine | mise à l'écart d'un contenu suspect avant qu'il n'atteigne le modèle |
| SOC | centre des opérations de sécurité : l'équipe qui surveille les alertes d'une entreprise |

# Candidats — semaine S36 (relevé du lundi 31 août 2026)

> ⚠️ **Ce fichier n'est PAS la note de veille.** C'est la matière première : ce qui a été
> repéré, avec de quoi le vérifier. **La sélection, le jugement de fiabilité et la conclusion
> « ce que ça change dans RITA » restent à écrire** par Era dans `2026-S36-<sujet>.md`,
> à partir de `_MODELE-note-hebdomadaire.md`.
>
> **Période balayée** : du 24 au 31 août 2026 · **relevé le** 2026-08-31 *(lundi, dans le
> créneau — pas de retard cette fois)*
> **Sources balayées** : OWASP GenAI Security Project, NIST AI RMF, CNIL, ANSSI / CERT-FR,
> simonwillison.net · puis, en second rang, arXiv `cs.CR` et la presse spécialisée.
> **Liens vérifiés** : chacun a répondu **HTTP 200** le 31/08/2026 (contrôle `curl`).
>
> 🔁 **Chevauchement avec S35** : le relevé S35 avait balayé jusqu'au 25 août. Les 24–25 août
> sont donc revus ici ; rien de neuf n'y a été trouvé qui n'ait déjà été noté en S35.

---

## 🟢 Le constat honnête d'abord : une semaine maigre, mais un fait solide et un préprint qui vise juste

Quatre des cinq sources principales **n'ont rien publié de neuf** sur l'injection de prompt
entre le 24 et le 31 août (détail au §« Ce qui n'a rien donné »). Ce qui reste tient en
**cinq candidats**, dont :

- **un fait vérifié et abondamment repris** (candidats 1–2) : une attaque publique contre le
  mode « auto » de Claude Code, où **le garde-fou lui-même a aggravé l'incident** ;
- **un préprint daté du 27 août** (candidat 3) qui répond frontalement à la **question ouverte
  laissée en S35** — celle du seuil et de l'approche du garde-fou.

> 📖 **Injection de prompt** : texte glissé dans une donnée pour que le modèle le prenne pour
> une instruction. **Injection indirecte** : la même chose, cachée dans une page ou un fichier
> que l'agent va lire tout seul — c'est le cas qui menace RITA (`sources/scraper.py`,
> `sources/rss.py`).

---

## 🔴 Candidat 1 — « Breaking Claude Code Opus 5 Auto Mode » : le garde-fou a bloqué le nettoyage, pas l'attaque

| | |
|---|---|
| **Source primaire** | **embracethered.com** — blog de **Johann Rehberger**, chercheur en sécurité IA, connu pour ses travaux sur l'injection indirecte |
| **Source de synthèse** | **Simon Willison** — a créé le terme *prompt injection* en 2022 ; blog personnel, ne vend aucune solution |
| **Titres** | Rehberger : *Breaking Claude Code Opus 5 Auto Mode with Indirect Prompt Injection* · Willison : *Breaking Claude Code Opus 5 Auto Mode* |
| **Dates** | billet Rehberger et billet Willison : **27 août 2026** · **mise à jour de Willison le 30 août** (voir plus bas) |
| **Liens** | [Billet de Johann Rehberger sur embracethered.com](https://embracethered.com/blog/posts/2026/breaking-claude-code-opus-5-and-automode/) · [Analyse de Simon Willison](https://simonwillison.net/2026/Aug/27/breaking-claude-code-opus-5-auto-mode/) |

**Ce qui est décrit** : on demande à Claude Code de résumer un site web ; le site renvoie une
archive ZIP de faux « fiches catalogue ». L'agent la décompresse, **refuse** d'exécuter le
binaire décodeur fourni (le refus est correct), écrit alors **son propre** script Python et le
lance **depuis le dossier décompressé** — où un fichier nommé `struct.py` **masque** le module
standard que `base64` importe. Résultat : exécution de code fournie par la page. Taux de
réussite annoncé par l'auteur : **~80 %**. Variante : `struct.py` lance un **second** Claude
Code en arrière-plan (`claude -p`), avec son propre accès aux outils.

**Le point qui concerne directement RITA** : quand l'agent détecte la compromission et tente
de tuer le processus malveillant, **le mode « auto » bloque la commande de nettoyage**. Le
garde-fou a autorisé la création du malware puis interdit sa suppression. *Un garde-fou mal
placé ne se contente pas de ne pas protéger : il peut empêcher la réaction.*

⚠️ **Nuance à ne pas escamoter dans la note** : le **30 août**, Willison a ajouté une mise à
jour requalifiant l'incident de *« confused deputy / confused environment attack »* (adjoint
égaré) plutôt que d'injection de prompt classique — **aucune instruction hostile n'a été suivie
par le modèle**, c'est l'environnement d'exécution qui a été piégé. Le titre de Rehberger et
plusieurs médias parlent pourtant d'« injection de prompt indirecte ». **Ce désaccord de
qualification est lui-même un objet de veille** : la frontière entre « le modèle a obéi à un
texte » et « l'outillage a été détourné » n'est pas nette, et RITA doit savoir de quel côté
tombent ses propres risques.

> 📖 **Adjoint égaré** (*confused deputy*) : un composant de confiance est manipulé pour agir,
> avec ses propres privilèges, au bénéfice d'un attaquant — sans qu'aucune instruction
> explicite ne lui ait été donnée.

**Lien avec RITA en une phrase** : RITA n'exécute pas de code et n'a pas d'outil (établi en
note S33/S34), donc ce vecteur précis ne s'applique pas — mais l'idée que **le garde-fou peut
lui-même produire un comportement nuisible** vaut pour `guardrails/sortie.py` en *fail-closed*.

---

## 🟠 Candidat 2 — The Register : « il suffit de lui demander de résumer un site web »

| | |
|---|---|
| **Source** | **The Register** — presse spécialisée britannique, rédaction identifiée, pas d'intérêt dans un produit de sécurité IA |
| **Titre** | *Researcher shows how Claude Code can be tricked simply by asking it to summarize a website* |
| **Date** | **28 août 2026** |
| **Lien** | [Article de The Register sur l'attaque du mode auto](https://www.theregister.com/research/2026/08/28/researcher-shows-how-claude-code-can-be-tricked-simply-by-asking-it-to-summarize-a-website/5293372) |

**Pourquoi le garder à part du candidat 1** : c'est la **confirmation par une source
indépendante** (le protocole, `README.md` §3, demande que l'information *« puisse être
confirmée par d'autres sites de confiance »*). L'angle du titre est celui qui parle à RITA :
**le déclencheur est une simple demande de résumé d'une page web** — exactement l'opération
que fait `sources/scraper.py` avant de passer le texte au modèle.

**Lien avec RITA en une phrase** : le scénario d'entrée (« résumer une page tierce hostile »)
est le scénario nominal de RITA ; seule l'absence d'outils et d'exécution le rend inoffensif
ici — une hypothèse à réafficher noir sur blanc dans la note.

---

## 🔴 Candidat 3 — LongGuard : un garde-fou par modèle perd plus de 50 % de sa détection sur un texte long

| | |
|---|---|
| **Source** | arXiv `cs.CR` — ⚠️ **préprint, non relu par les pairs. Une piste, pas un fait.** |
| **Titre** | *LongGuard: Mechanistic Analysis and Training-Free Mitigation of Long-Context Failure in Safety Guardrails* |
| **Auteurs** | Ziyang Chen, Xing Wu, Songlin Hu |
| **Date** | **27 août 2026** — dans la semaine balayée |
| **Lien** | [LongGuard (arXiv 2608.27580)](https://arxiv.org/abs/2608.27580) |

**Ce que les auteurs disent avoir mesuré** (lu dans le résumé, pas dans un commentaire) : la
capacité d'un garde-fou **fondé sur un modèle** à repérer un contenu dangereux **chute en
moyenne de plus de 50 %** quand le texte analysé s'allonge. Cause avancée : la **dilution de
l'attention** — le passage hostile se noie dans le volume. Leurs correctifs, sans
réentraînement : **détection par tronçons** (*chunked detection*) et « affûtage » des têtes
d'attention, +22 % annoncés.

**Pourquoi c'est le candidat le plus utile de la semaine** : la **question ouverte de S35**
(fichier `_candidats-2026-S35.md`, et note S34 §« Question ouverte ») est : *faut-il remplacer
les 9 motifs regex par un classifieur ?* Ce préprint est un **argument contre le passage
naïf** : RITA donne au garde-fou le **texte intégral d'une page scrapée**, qui est justement
un « texte long ». Un classifieur y perdrait, d'après ces auteurs, la moitié de sa détection —
là où une expression régulière, elle, ne « dilue » rien.
⚠️ Préprint : à croiser avec une source relue (OWASP, ANSSI) avant d'en faire une affirmation
dans la note. Et ne pas en conclure « donc regex pour toujours » : le candidat 1 de S35
(*Confidently Wrong*) disait l'inverse sur un autre plan. **Les deux se lisent ensemble.**

---

## ⚪ Candidat 4 — DreamGuard : un garde-fou d'exécution à modèle de monde (thématique, pas la question de la semaine)

| | |
|---|---|
| **Source** | arXiv `cs.CR` — ⚠️ **préprint, 9 auteurs nommés** |
| **Titre** | *DreamGuard: Efficient Runtime Guardrail for LLM Agents via Risk-Aware World Model* |
| **Auteurs** | Wenhao Lin, Chenyu Yu, Xingwei Lin, Sicong Cao, Xiang Chen, Lei Xue, Le Yu, Letian Sha, Chunming Wu |
| **Date** | **6 août 2026** — hors semaine, jamais relevé jusqu'ici |
| **Lien** | [DreamGuard (arXiv 2608.05695)](https://arxiv.org/abs/2608.05695) |

**En bref** : au lieu de juger chaque action isolément, le garde-fou maintient un **état latent
sur toute la trajectoire** de l'agent et **prédit** les risques à venir ; latence annoncée
**25 ms** par appel.

**Pourquoi ⚪** : c'est une architecture pour agents **qui appellent des outils et enchaînent
des actions** — RITA n'en est pas là. À citer seulement pour montrer où va la recherche sur
les garde-fous d'agents, pas pour trancher quoi que ce soit cette semaine.

---

## ⚪ Candidat 5 — CNIL : mise à jour de l'outil de traçabilité des modèles open source

| | |
|---|---|
| **Source** | **CNIL** — autorité administrative indépendante, aucun intérêt commercial, site public soumis au RGAA |
| **Titre** | *IA : la CNIL met à jour son outil de traçabilité des modèles publiés en source ouverte* |
| **Date** | **26 août 2026** — dans la semaine |
| **Lien** | [Mise à jour de l'outil de traçabilité des modèles — CNIL](https://www.cnil.fr/fr/ia-la-cnil-met-jour-son-outil-de-tracabilite-des-modeles-publies-en-source-ouverte) |

**Ce qui est annoncé** : une nouvelle version du démonstrateur qui explore la **généalogie**
d'un modèle open source (ses ancêtres, ses descendants), pour étudier la **mémorisation de
données personnelles** propagée d'un modèle dérivé à l'autre. Ergonomie, performance et
rafraîchissement automatique améliorés ; version anglaise ajoutée.

**Pourquoi ⚪** : c'est une source **française et officielle**, publiée cette semaine — mais le
sujet est la **provenance des modèles et le RGPD**, pas l'injection de prompt. Lien indirect
avec RITA : la chaîne d'approvisionnement (OWASP **ASI04**, déjà notée en S34 à propos de
`requirements.txt` — 2 dépendances épinglées sur 13). À mentionner dans la note **uniquement**
si Era veut traiter le volet « d'où vient le modèle que RITA appelle ».

---

## ❌ Ce qui n'a rien donné cette semaine — et le dire est un acte de veille

| Source | Vérification faite | Résultat |
|---|---|---|
| **OWASP GenAI** | [page ressources](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) consultée | Le **LLM Top 10 2026** date du **3 août** — **déjà traité en S33**. Rien de neuf entre le 24 et le 31 août |
| **NIST** | [page AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | **AI RMF 1.0 (2023) toujours en vigueur, aucune version 2.0.** Inchangé depuis S34 |
| **ANSSI / cyber.gouv.fr** | [page Intelligence artificielle](https://cyber.gouv.fr/enjeux-technologiques/intelligence-artificielle/) — liste des publications lue | Dernières publications IA : **MEPIA** (15/07/2026) et *Synthèse de la menace sur l'IA générative* (04/02/2026). **Rien en août.** ⚠️ **Piège repéré** : plusieurs articles de presse (Solutions Numériques, Haas Avocats, blogs) évoquent un guide ANSSI *« Sécuriser les systèmes intégrant de l'intelligence artificielle »* comme récent — **ce titre n'apparaît PAS sur le site officiel de l'ANSSI** au 31/08. À ne pas citer tant que la source primaire n'est pas trouvée. |
| **CERT-FR** | flux d'actualité balayé | Rien sur l'IA — comme en S34 et S35, les bulletins portent sur des vulnérabilités logicielles classiques |
| **Simon Willison** | blog balayé sur la période | Un seul billet sécurité dans la semaine : le **27 août** (candidat 1). Le billet du 11 août (*Stealing Reasoning Traces*) relève de S35 |

**Écartés par principe, comme en S33/S34/S35** : les reprises par des éditeurs de solutions de
sécurité (cybernews, gbhackers, cybersecuritynews, cyberpress…) et les blogs de fournisseurs
de garde-fous. Motif inchangé : **conflit d'intérêts direct** — ils décrivent le problème
qu'ils vendent (`README.md` §3). The Register (candidat 2) est retenu parce que c'est une
**rédaction de presse**, pas un vendeur.

⚠️ **Conséquence à assumer dans la note** : sur les cinq candidats, **deux sont des préprints**
et **un est un incident encore en cours de qualification**. Aucune source officielle relue ne
tranche la question du seuil cette semaine non plus. C'est un résultat de veille, à écrire
tel quel.

---

## 🕳️ Trou dans la suite des notes — à combler avant d'écrire S36

Les fichiers présents dans `docs/veille/` :

| Semaine | Candidats | **Note rédigée** (`AAAA-Sxx-sujet.md`) |
|---|---|---|
| S33 | ✅ `_candidats-2026-S33.md` | ✅ `2026-S33-injection-de-prompt.md` |
| S34 | ✅ `_candidats-2026-S34.md` | ✅ `2026-S34-top10-agentique.md` |
| **S35** | ✅ `_candidats-2026-S35.md` | 🔴 **MANQUANTE** — aucun `2026-S35-*.md` |
| S36 | ✅ ce fichier | ⬜ à écrire |

**La note S35 n'a jamais été rédigée.** Le relevé de candidats existe (il est riche : quatre
candidats sur l'arbitrage du seuil), mais la note — donc la sélection, le jugement de
fiabilité et la section « Ce que ça change dans RITA » — reste à faire. **Un trou dans la
suite des numéros de semaine se voit d'un coup d'œil, par soi-même comme par un évaluateur**
(`README.md` §6). Deux options honnêtes, aucune n'est « antidater » :

1. écrire **d'abord** la note S35 à partir de `_candidats-2026-S35.md`, en datant le créneau
   au **jour réel** où elle est écrite et en le disant dans l'en-tête ;
2. ou assumer S35 comme **semaine sautée** — l'écrire franchement en tête de la note S36
   (« pas de séance tenue en S35 pour telle raison »), et traiter en S36 la question ouverte
   qui restait.

L'option 1 est préférable : la matière est déjà là, et la question du seuil est le cœur de la
compétence C6 (formuler une recommandation pour le projet).

---

## ▶️ Ta séance d'une heure — proposition de déroulé

> ⚠️ Ce déroulé suppose que tu traites **S36**. Si tu choisis d'écrire d'abord la note **S35**
> (recommandé, voir ci-dessus), suis plutôt le déroulé du fichier `_candidats-2026-S35.md`.

| Temps | Quoi |
|---|---|
| **0–5 min** | Trancher : note S35 d'abord, ou S36 en assumant S35 sautée ? Écrire la décision en tête de la note |
| **5–20 min** | Candidat 1 — lire le billet de Rehberger **et** la mise à jour du 30/08 de Willison. Répondre par écrit : **l'incident est-il une injection de prompt ou un adjoint égaré ? Et RITA, de quel côté est-il exposé ?** |
| **20–30 min** | Candidat 2 — noter que le **déclencheur est « résume cette page »**, l'opération nominale de `sources/scraper.py`. Réafficher l'hypothèse qui protège RITA : **pas d'outil, pas d'exécution** (commande de preuve : `grep -rn "subprocess\|os.system\|eval(" --include=*.py .`) |
| **30–45 min** | Candidat 3 (LongGuard) — lire le résumé. Répondre : **si je passais à un classifieur, il verrait le texte intégral d'une page scrapée ; ce préprint dit qu'il y perdrait >50 % de détection. Est-ce que ça change ma réponse à la question ouverte de S35 ?** |
| **45–55 min** | Remplir la note depuis le gabarit. **« Ce que ça change dans RITA »** : au minimum, une ligne sur le garde-fou de sortie en *fail-closed* (candidat 1) et une ligne sur regex vs classifieur au vu de LongGuard (candidat 3) |
| **55–60 min** | Liste de contrôle d'accessibilité, enregistrer sous `2026-S36-<sujet>.md`, commiter |

**Si tu as 10 minutes de plus** : cherche la source primaire du guide ANSSI *« Sécuriser les
systèmes intégrant de l'IA »* que la presse cite (voir §« Ce qui n'a rien donné »). Une source
**officielle française** sur les garde-fous vaudrait mieux, devant un jury, que deux préprints.

---

## 📖 Glossaire de ce relevé

| Terme | En clair |
|---|---|
| **Injection de prompt** (*prompt injection*) | Texte glissé dans une donnée pour que le modèle le prenne pour une instruction |
| **Injection indirecte** | La même chose, cachée dans une page web ou un flux que l'agent lit tout seul |
| **Adjoint égaré** (*confused deputy*) | Un composant de confiance est manipulé pour agir avec ses propres privilèges au profit d'un attaquant, sans instruction explicite |
| **Mode « auto »** (Claude Code) | Réglage où l'agent exécute des actions sans demander confirmation à chaque étape ; un classifieur décide seul « autorisé / bloqué » |
| **Fail-closed** | En cas de doute, le garde-fou refuse de laisser passer. L'inverse (*fail-open*) laisserait passer quand il hésite |
| **Classifieur** | Petit modèle placé devant une action ou un texte, qui répond « autorisé / bloqué » |
| **Garde-fou par modèle** | Garde-fou dont la décision vient d'un modèle de langage, par opposition à un garde-fou par **expression régulière** (comparaison à des formes de texte connues), comme `guardrails/injection.py` |
| **Dilution de l'attention** (*attention dilution*) | Quand le texte à analyser est long, le passage dangereux « pèse » moins dans le calcul du modèle, qui finit par ne plus le voir |
| **Détection par tronçons** (*chunked detection*) | Découper un texte long en morceaux et analyser chaque morceau séparément, pour contrer la dilution de l'attention |
| **Modèle de monde** (*world model*) | Représentation interne que se fait un système de l'état courant et des états futurs probables, pour anticiper au lieu de seulement réagir |
| **Préprint** | Article de recherche publié **avant** relecture par les pairs — une piste, pas une preuve |
| **ASI04** | 4ᵉ entrée du *OWASP Top 10 for Agentic Applications 2026* : sécurité de la chaîne d'approvisionnement (dépendances, modèles, outils tiers) |
| **RGAA** | Référentiel français d'accessibilité, obligatoire pour les sites publics |
| **AMF** | Autorité des marchés financiers — encadre le conseil en investissement en France |

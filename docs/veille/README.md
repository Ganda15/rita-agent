# Veille technique — protocole (compétence C6)

> **C6** : *« Organiser et réaliser une veille technique et réglementaire en animant le travail
> collectif de sélection des sources, de collecte, de traitement et de partage des informations
> afin de formuler des recommandations pour le projet toujours en phase avec l'état de l'art. »*

**Mise en place : 2026-08-14** · une note par semaine dans ce dossier.

---

## 1. La thématique retenue

### **Sécurité des agents LLM — l'injection de prompt**

**Pourquoi celle-là et pas une autre.** Le critère demande une thématique portant sur *« un
outil et/ou une réglementation mobilisée dans la mise en situation »*. L'injection de prompt
n'est pas un sujet choisi pour l'exercice : c'est **une menace active sur RITA**.

RITA lit des pages web (`sources/scraper.py`), des flux RSS (`sources/rss.py`) et des articles
écrits par des tiers, puis passe ce texte à un modèle. Une page hostile peut donc tenter de
faire produire au modèle une **recommandation d'achat** — soit exactement l'interdit AMF que
le projet s'impose. Le garde-fou existe déjà (`guardrails/injection.py`, 9 motifs), et il est
mesuré (`evals/mesurer_gardefou.py`).

**Conséquence pratique** : chaque note se termine par une section **« Ce que ça change dans
RITA »**. Une veille qui ne modifie jamais le projet n'est pas une veille, c'est une revue de
presse.

---

## 2. La récurrence — 1 heure par semaine

| | |
|---|---|
| **Créneau** | **lundi, 09h00 → 10h00** |
| **Durée** | 1 heure — le minimum exigé par le critère |
| **Sortie** | une note datée dans ce dossier, une par semaine |
| **Rappel** | tâche planifiée `veille-hebdo-securite-llm` (hebdomadaire, lundi 09h00) |

⚠️ **Ce que la tâche planifiée fait, et ce qu'elle ne fait pas.** Elle **prépare le terrain** :
elle relève les nouveautés des sources ci-dessous et dépose une liste de candidats. Elle
**n'écrit pas la note à la place d'Era** — la sélection, le jugement de fiabilité et la
conclusion « ce que ça change dans RITA » sont le travail de veille lui-même. Une note
produite automatiquement ne prouverait aucune compétence.

---

## 3. Les sources, et pourquoi chacune est fiable

Le critère exige que *« l'auteur de la page soit identifié, ses compétences et sa notoriété
confirmées, et qu'il y ait absence d'intérêts personnels »*. Chaque source est donc pesée,
y compris celles qu'on garde malgré un défaut.

| Source | Auteur identifié | Notoriété | Intérêts | Accessibilité |
|---|---|---|---|---|
| **OWASP GenAI Security Project** — *Top 10 for LLM Applications* | fondation OWASP, contributeurs nommés | référence mondiale de la sécurité applicative depuis 2001 | **à but non lucratif** — aucun produit à vendre | site structuré, navigation au clavier |
| **ANSSI** — recommandations IA générative | agence nationale française | autorité de l'État en cybersécurité | aucun intérêt commercial | site public → **RGAA obligatoire** ✅ |
| **CNIL** — fiches IA et RGPD | autorité administrative indépendante | autorité française sur les données personnelles | aucun | **RGAA** ✅ |
| **NIST** — *AI Risk Management Framework* | agence fédérale américaine | référence internationale | aucun commercial | Section 508 ✅ |
| **Simon Willison** — simonwillison.net | auteur identifié, co-créateur de Django | **a popularisé le terme *prompt injection*** en 2022 | blog personnel, ne vend pas de solution | flux RSS propre, HTML sobre |
| ⚠️ **Anthropic / OpenAI** — publications sécurité | éditeurs de modèles | expertise technique réelle | **intérêt commercial direct** | — |
| ⚠️ **arXiv `cs.CR`** | chercheurs nommés | — | — | — |

### Les deux sources gardées **sous condition**

- **Éditeurs de modèles** : ils connaissent leurs modèles mieux que personne, mais ils vendent
  ces modèles. **Jamais utilisés comme source unique** — toute affirmation venant d'eux est
  croisée avec OWASP, l'ANSSI ou un travail universitaire.
- **arXiv** : ce sont des **pré-publications, non relues par les pairs**. Une préprint est une
  piste, pas un fait. Toujours signaler ce statut dans la note.

> C'est le sens du critère *« l'information peut être confirmée par d'autres sites de
> confiance »* : **une source seule ne suffit jamais**.

### Ce qui est écarté, et pourquoi

| Écarté | Motif |
|---|---|
| Fils LinkedIn / X sur l'IA | auteur souvent non vérifiable, aucune date fiable, contenu promotionnel |
| Blogs d'éditeurs d'outils de sécurité LLM | conflit d'intérêts direct : ils décrivent le problème qu'ils vendent |
| Agrégateurs générés par IA | sources d'origine effacées, donc invérifiables |

---

## 4. L'outil d'agrégation, et son budget

**Choix : les flux RSS, lus par le module que le projet possède déjà** — `sources/rss.py`
(httpx + feedparser, testé par `tests/test_rss.py`).

| Critère | Réponse |
|---|---|
| **Budget** | **0 €** — RSS est un format ouvert, aucun abonnement, aucune API payante |
| **Cohérence avec les sources** | les 5 sources principales publient toutes un flux RSS ou Atom |
| **Cohérence avec le projet** | c'est **le code de RITA**, déjà écrit et déjà testé — rien de nouveau à maintenir |

**Pourquoi pas un agrégateur du commerce** (Feedly, Inoreader) : payant au-delà de quelques
flux, et il faudrait justifier une dépense pour une fonction que le projet sait déjà faire.
**Pourquoi pas les newsletters** : elles arrivent dans une boîte mail personnelle — ni
versionnable, ni consultable par un tiers.

---

## 5. Le format de partage — et l'accessibilité

Le critère impose que les synthèses soient *« communiquées aux parties prenantes dans un
format qui respecte les recommandations d'accessibilité »* (Valentin Haüy, Atalan AcceDe).

**Format retenu : Markdown**, converti en PDF pour l'envoi. Règles appliquées à chaque note —
elles figurent dans le modèle et sont vérifiables une par une :

| Règle | Pourquoi |
|---|---|
| **Un seul `#` par note**, puis `##` et `###` **sans sauter de niveau** | un lecteur d'écran navigue par la hiérarchie des titres ; un niveau sauté casse le plan |
| **Texte de lien explicite** — jamais « cliquez ici » ni une URL nue | hors contexte, la liste des liens doit rester compréhensible |
| **Texte alternatif sur chaque image** | une image sans alternative n'existe pas pour un lecteur d'écran |
| **Tableaux avec ligne d'en-tête**, aucune cellule fusionnée | sans en-tête, les cellules n'ont plus de sens à la lecture linéaire |
| **Jamais d'information portée par la seule couleur** | toujours doublée par un mot ou un symbole |
| **Résumé en langage clair en tête** | 5 lignes maximum, sans jargon |
| **Chaque terme technique défini** à sa première occurrence + glossaire final | la note doit se lire sans connaissance préalable |

---

## 6. Nommage et cycle de vie

```
docs/veille/
├── README.md                          ce protocole
├── _MODELE-note-hebdomadaire.md       le gabarit
└── 2026-S33-injection-de-prompt.md    une note par semaine : AAAA-Sxx-sujet.md
```

Le numéro de semaine ISO rend la **récurrence lisible d'un coup d'œil** : un trou dans la
suite se voit immédiatement — par soi-même comme par un évaluateur.

---

## 7. 📖 Glossaire

| Terme | En clair |
|---|---|
| **Veille** | Suivi organisé et régulier d'un sujet, pour rester à jour |
| **Injection de prompt** (*prompt injection*) | Texte glissé dans une donnée pour que le modèle le prenne pour une instruction |
| **Injection indirecte** | La même chose, mais cachée dans une page web ou un flux que l'agent va lire tout seul |
| **RSS / Atom** | Format ouvert par lequel un site publie ses nouveautés, lisible par un programme |
| **Garde-fou** (*guardrail*) | Contrôle qui filtre ce qui entre ou sort d'un modèle |
| **Préprint** | Article de recherche publié **avant** relecture par les pairs — une piste, pas une preuve |
| **RGAA** | Référentiel français d'accessibilité, obligatoire pour les sites publics |
| **AcceDe** | Guides d'accessibilité des documents publiés par la société Atalan |
| **Lecteur d'écran** | Logiciel qui lit un document à voix haute pour une personne aveugle |
| **AMF** | Autorité des marchés financiers — encadre le conseil en investissement en France |

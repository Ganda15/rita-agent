# Veille technique : protocole (compétence C6)

> **C6** : *« Organiser et réaliser une veille technique et réglementaire en animant le travail
> collectif de sélection des sources, de collecte, de traitement et de partage des informations
> afin de formuler des recommandations pour le projet toujours en phase avec l'état de l'art. »*

**Mise en place : 2026-08-14** · une note par semaine dans ce dossier.

---

## 1. La thématique retenue

### Sécurité des agents LLM : l'injection de prompt

Pourquoi ce thème ? Le critère demande une thématique portant sur *« un
outil et/ou une réglementation mobilisée dans la mise en situation »*. L'injection de prompt
n'est pas un sujet que j'ai choisi pour l'exercice : c'est une menace active sur RITA.

RITA lit des pages web (`sources/scraper.py`), des flux RSS (`sources/rss.py`) et des articles
écrits par des tiers, puis passe ce texte à un modèle. Une page hostile peut donc tenter de
faire produire au modèle une recommandation d'achat, c'est-à-dire exactement l'interdit AMF que
je m'impose dans le projet. Le garde-fou existe déjà (`guardrails/injection.py`, 12 motifs nommés
plus la détection `consigne_deguisee`), et il est mesuré (`evals/mesurer_gardefou.py`).

En pratique, chaque note se termine par une section « Ce que ça change dans RITA ». Une veille
qui ne modifie jamais le projet reste une simple revue de presse.

---

## 2. La récurrence : 1 heure par semaine

| | |
|---|---|
| **Créneau** | lundi, 09h00 → 10h00 |
| **Durée** | 1 heure, le minimum exigé par le critère |
| **Sortie** | une note datée dans ce dossier, une par semaine |
| **Rappel** | La tâche planifiée de l'application Claude `veille-hebdo-securite-llm` existe depuis le 14/08/2026 et est configurée pour le lundi à 09 h, heure de Paris. Les contrôles des 24/08 et 03/10 (`Get-ScheduledTask`, incident INC-004) portaient sur le Planificateur de tâches de Windows et ne pouvaient pas voir cette tâche Claude ; cette conclusion est corrigée le 09/11. L'historique local contient 13 lancements du 17/08 au 09/11, dont deux sessions interrompues (19/10 et 02/11). Un lancement ne prouve pas qu'un relevé a été produit : aucun fichier de candidats S42 ni S44 n'est présent dans ce dossier au 09/11. La tâche prépare le relevé ; la rédaction de la note reste mon travail. |

État réel de la récurrence au 09/11/2026, lu dans ce dossier (je laisse les trous visibles) :

| Semaine ISO | Candidats relevés | Note écrite | Quand, et comment |
|---|---|---|---|
| S33 (10 au 16/08) | ✅ | ✅ | créneau tenu le vendredi 14/08 |
| S34 (17 au 23/08) | ✅ | ✅ | créneau tenu le lundi 17/08 |
| S35 (24 au 30/08) | ✅ (relevé du 25/08) | ✅ | rédigée en rattrapage le 08/09, l'en-tête le dit |
| S36 (31/08 au 06/09) | ✅ (relevé du 31/08) | ✅ | rédigée en rattrapage le 08/09, l'en-tête le dit |
| S37 (07 au 13/09) | ✅ (relevé du 08/09) | 🔴 aucune | carte #31 |
| S38, S39 (14 au 27/09) | 🔴 aucun | 🔴 aucune | carte #31 : deux semaines sans séance, à dire tel quel |
| S40 (28/09 au 04/10) | ✅ (relevé du 28/09, fenêtre élargie au 14/09) | 🔴 à écrire par moi | carte #30 |
| S41 (05 au 11/10) | ✅ (relevé du 11/10, fenêtre élargie au 29/09) | ✅ rédigée en rattrapage le 11/10, partagée à la promo le 11/10 (`_JOURNAL-DES-ENVOIS.md`, envoi 3) | créneau du lundi 05/10 non tenu ; relevé fait le dimanche 11/10, et dit |
| S42 (12 au 18/10) | 🔴 aucun | 🔴 aucune | Aucun relevé ni note retrouvé au 09/11 ; période non balayée d’après le relevé S46 |
| S43 (19 au 25/10) | 🔴 aucun | 🔴 aucune | Aucun relevé ni note retrouvé au 09/11 ; période non balayée d’après le relevé S46 |
| S44 (26/10 au 01/11) | 🔴 aucun | 🔴 aucune | Aucun relevé ni note retrouvé au 09/11 ; période non balayée d’après le relevé S46 |
| S45 (02 au 08/11) | ⚠️ aucun fichier S45 ; période reprise dans le [relevé S46 du 09/11](_candidats-2026-S46.md) | 🔴 aucune | La collecte du 09/11 couvre le 02 au 09/11 ; elle ne constitue pas une note S45 |
| S46 (09 au 15/11) | ✅ [relevé du 09/11](_candidats-2026-S46.md), fenêtre du 02 au 09/11 | ✅ [note assistée du 09/11](2026-S46-regex-et-autorite-des-sources.md), ma contribution et les corrections y sont attribuées | Synthèse partagée à la promo le 09/11 à 11 h 41, [envoi 4](_JOURNAL-DES-ENVOIS.md) ; retour en attente. Durée d’une heure non attestée |

Synthèse des quatre premières notes : `Veille-C6-synthese-S33-a-S36.pdf` (§6). Au 09/11/2026, trois partages à la promo sont consignés : S33 le 16/08, S41 le 11/10 et S46 le 09/11. Le retour S41 et sa capture sont relevés dans le [journal des envois](_JOURNAL-DES-ENVOIS.md) ; le retour S46 reste en attente et l’envoi au formateur reste à faire.


**Ce que le relevé fait, et ce qu'il ne fait pas.** Il prépare le terrain : les nouveautés
des sources ci-dessous sont relevées (au besoin avec un assistant de code, qui lit les
flux et les pages) et déposées dans `_candidats-AAAA-Sxx.md`, avec la période balayée, la date
du relevé et les sources balayées. Il n'écrit pas la note à ma place : la sélection, le
jugement de fiabilité et la conclusion « ce que ça change dans RITA » sont le travail de veille
lui-même. Une note produite automatiquement ne prouverait aucune compétence.

---

## 3. Les sources, et pourquoi chacune est fiable

Le critère exige que *« l'auteur de la page soit identifié, ses compétences et sa notoriété
confirmées, et qu'il y ait absence d'intérêts personnels »*. Chaque source est donc pesée,
y compris celles que je garde malgré un défaut.

| Source | Auteur identifié | Notoriété | Intérêts | Accessibilité |
|---|---|---|---|---|
| **OWASP GenAI Security Project** : *Top 10 for LLM Applications* | fondation OWASP, contributeurs nommés | référence mondiale de la sécurité applicative depuis 2001 | à but non lucratif, aucun produit à vendre | site structuré, navigation au clavier |
| **ANSSI** : recommandations IA générative | agence nationale française | autorité de l'État en cybersécurité | aucun intérêt commercial | site public → RGAA obligatoire ✅ |
| **CNIL** : fiches IA et RGPD | autorité administrative indépendante | autorité française sur les données personnelles | aucun | **RGAA** ✅ |
| **NIST** : *AI Risk Management Framework* | agence fédérale américaine | référence internationale | aucun commercial | Section 508 ✅ |
| **Simon Willison** : simonwillison.net | auteur identifié, co-créateur de Django | a popularisé le terme *prompt injection* en 2022 | blog personnel, ne vend pas de solution | flux RSS propre, HTML sobre |
| ⚠️ **Anthropic / OpenAI** (sous condition) : publications sécurité | éditeurs de modèles | expertise technique réelle | intérêt commercial direct | - |
| ⚠️ **arXiv `cs.CR`** (sous condition) | chercheurs nommés | - | - | - |

### Les deux sources gardées sous condition

- **Éditeurs de modèles** : ils connaissent leurs modèles mieux que personne, mais ils vendent
  ces modèles. Je ne les utilise jamais comme source unique : toute affirmation venant d'eux est
  croisée avec OWASP, l'ANSSI ou un travail universitaire.
- **arXiv** : ce sont des pré-publications, non relues par les pairs. Une préprint est une
  piste à confirmer. Je signale toujours ce statut dans la note.

> C'est le sens du critère *« l'information peut être confirmée par d'autres sites de
> confiance »* : une source seule ne suffit jamais.

### Ce qui est écarté, et pourquoi

| Écarté | Motif |
|---|---|
| Fils LinkedIn / X sur l'IA | auteur souvent non vérifiable, aucune date fiable, contenu promotionnel |
| Blogs d'éditeurs d'outils de sécurité LLM | conflit d'intérêts direct : ils décrivent le problème qu'ils vendent |
| Agrégateurs générés par IA | sources d'origine effacées, donc invérifiables |

---

## 4. L'outil d'agrégation, et son budget

Mon choix : les flux RSS et Atom des sources du §3, relevés à la main (lecteur de flux ou
navigateur), et consignés dans un fichier `_candidats-AAAA-Sxx.md` par semaine : période balayée,
date du relevé, sources balayées, un bloc par candidat avec son lien primaire.

> **Corrigé le 03/10/2026.** Ce paragraphe affirmait que l'outil de la veille était
> `sources/rss.py`, le module de collecte de RITA. C'est faux : ce module lit des flux
> financiers (BFM Économie, La Tribune, Le Monde Économie, Google Actualités) pour les
> briefings, et aucune des sources du §3 n'y est configurée (vérifié dans `sources/rss.py`).
> Je préfère le dire ici plutôt que de le laisser découvrir à un évaluateur.

| Critère | Réponse |
|---|---|
| **Budget** | 0 € : RSS est un format ouvert, aucun abonnement, aucune API payante |
| **Cohérence avec les sources** | les 5 sources principales publient toutes un flux RSS ou Atom |
| **Cohérence avec le projet** | les relevés sont versionnés dans le dépôt, lisibles sans outil ; aucun code à maintenir pour la veille |

Je n'ai pas pris d'agrégateur du commerce (Feedly, Inoreader) : il est payant au-delà de quelques
flux, et il faudrait justifier une dépense pour une fonction que le projet sait déjà faire.
Je n'ai pas pris les newsletters non plus : elles arrivent dans une boîte mail personnelle, qu'on
ne peut ni versionner ni montrer à un tiers.

### Deux outils de veille coexistent : lequel fait quoi

Un second outil existe **hors du dépôt** : `C:\Users\kanda\Desktop\Veille-IA\`. Ce protocole
ne le mentionnait pas, ce qui laissait un évaluateur devant deux outils pour un seul besoin,
sans savoir lequel fait foi. J'ai tranché le 15/08/2026.

| | relevé manuel, `_candidats-*.md`, dans le dépôt | `Veille-IA`, hors dépôt |
|---|---|---|
| **Rôle pour C6** | ✅ l'outil de la veille C6, celui qui produit la preuve | ❌ hors C6 : veille personnelle d'éveil |
| **Thématique** | sécurité des agents LLM, injection de prompt | IA en finance, IA agentique, outils de dev (`config.yaml`, `focus_weights`) |
| **Sources** | les flux et pages des 5 sources pesées au §3, relevés à la main | Google News, Hacker News, DuckDuckGo, arXiv (`src/websearch.py`) |
| **Sortie** | une liste de candidats ; j'écris la note | top-10 quotidien sur Telegram, puis diapositives et script oral rédigés par un LLM |
| **Budget** | 0 € | 0 € (OpenRouter, modèle gratuit) |
| **Versionné et testé** | ✅ relevés et notes dans le dépôt Git ; rien à tester, il n'y a pas de code | ❌ ni versionné, ni testé |

Pourquoi `Veille-IA` ne peut pas être l'outil de C6 (trois raisons, dont une rédhibitoire) :

1. Sa sortie est rédigée par un modèle de langage (la raison rédhibitoire). Le §2 de ce protocole pose déjà la
   règle : *une note produite automatiquement ne prouverait aucune compétence*. Présenter des
   diapositives générées par un LLM comme preuve d'une veille personnelle serait une preuve
   fabriquée.
2. Sa thématique n'est pas celle de C6. Ses pondérations visent l'IA en finance et l'IA
   agentique, utile pour ma culture mais sans rapport avec l'injection de prompt.
3. Il est hors du dépôt, donc invisible pour un évaluateur qui ne dispose que de Git.

État réel de l'outil, mesuré le 15/08/2026 : `data/latest.json` date du 27/07, et
`output/` ne contient qu'un seul dossier, du 19/07. L'outil est à l'arrêt depuis
environ trois semaines : il ne pourrait donc pas non plus revendiquer une récurrence.

Ma décision : je garde `Veille-IA` comme outil de veille personnelle, et je le cite
ici pour qu'aucun évaluateur ne le découvre sans explication. Il ne produit aucune preuve C6.

---

## 5. Le partage : à qui, quand, et comment je le prouve

> **Trou comblé le 15/08/2026.** Ce protocole décrivait le *format* du partage mais jamais
> son *destinataire*. Or deux critères sur huit portent là-dessus : les synthèses doivent
> être *« communiquées aux parties prenantes »* et la veille menée *« en animant le travail
> collectif »*. Une veille menée seul n'en coche aucun des deux, même parfaitement rédigée.

### 5.1 À qui, et à quelle cadence

| Cercle | Destinataire | Canal | Cadence | Ce que ça prouve |
|---|---|---|---|---|
| **Principal** | le formateur référent | mail, note convertie en PDF | mensuel, une synthèse groupant ~4 notes | *« communiquées aux parties prenantes »* |
| **Second** | la promo | canal de classe | à chaque note, avec une question ouverte | *« en animant le travail collectif »* |

J'ai pris le formateur comme destinataire principal parce que c'est la partie prenante la plus
incontestable devant un jury : son rôle est écrit, sa réception vérifiable.

Pour l'envoi, la cadence prévue est une synthèse mensuelle
pour regrouper les notes et faciliter leur lecture par le formateur. Au 09/11/2026, aucun
envoi au formateur n'est consigné dans le [journal des envois](_JOURNAL-DES-ENVOIS.md) :
l'objectif de trois envois avant le 05/11 n'a pas été atteint et le premier envoi reste à faire.
La note reste hebdomadaire ; c'est l'envoi au formateur qui est prévu chaque mois.

Pourquoi une question ouverte dans le canal de la promo : *« animer le travail collectif »*
demande plus que publier. Un message sans réponse ne prouve aucune animation. Chaque note
postée se termine donc par une question adressée au groupe, et ce sont les réponses reçues
qui servent de preuve, plus que le message envoyé.

### 5.2 La trace des envois

Registre : `docs/veille/_JOURNAL-DES-ENVOIS.md`, une ligne par envoi (date, destinataire,
canal, notes couvertes, retour reçu).

Je le remplis le jour de l'envoi, jamais après coup. Un registre rempli d'un bloc à la
veille du rendu se voit : les dates ne collent plus avec les notes qu'il prétend accompagner.

### 5.3 Ce qui reste non résolu

- Aucun envoi n'a encore eu lieu au 15/08/2026. Le registre existe, il est vide. Le
  premier envoi est à faire par moi : aucun outil ne peut le faire à ma place.
- L'animation du travail collectif reste le point faible du dispositif. Elle dépend de
  réponses que d'autres personnes doivent écrire. Si aucune réponse n'arrive après deux
  notes, il faudra changer de canal plutôt que continuer à publier dans le vide.

### 5.4 Le format, et l'accessibilité

Le critère impose que les synthèses soient *« communiquées aux parties prenantes dans un
format qui respecte les recommandations d'accessibilité »* (Valentin Haüy, Atalan AcceDe).

Format retenu : Markdown, converti en PDF pour l'envoi. Les règles appliquées à chaque note
figurent dans le modèle et se vérifient une par une :

| Règle | Pourquoi |
|---|---|
| Un seul `#` par note, puis `##` et `###` sans sauter de niveau | un lecteur d'écran navigue par la hiérarchie des titres ; un niveau sauté casse le plan |
| Texte de lien explicite : jamais « cliquez ici » ni une URL nue | hors contexte, la liste des liens doit rester compréhensible |
| Texte alternatif sur chaque image | une image sans alternative n'existe pas pour un lecteur d'écran |
| Tableaux avec ligne d'en-tête, aucune cellule fusionnée | sans en-tête, les cellules n'ont plus de sens à la lecture linéaire |
| Jamais d'information portée par la seule couleur | toujours doublée par un mot ou un symbole |
| Résumé en langage clair en tête | 5 lignes maximum, sans jargon |
| Chaque terme technique défini à sa première occurrence + glossaire final | la note doit se lire sans connaissance préalable |

---

## 6. Nommage et cycle de vie

```
docs/veille/
├── README.md                          ce protocole
├── _MODELE-note-hebdomadaire.md       le gabarit
├── _JOURNAL-DES-ENVOIS.md             la trace des partages (§5.2)
└── 2026-S33-injection-de-prompt.md    une note par semaine : AAAA-Sxx-sujet.md
└── Veille-C6-synthese-S33-a-S36.md     synthèse mensuelle : page de garde + les quatre notes S33 à S36, concaténées par `scripts/synthese_veille.py`
└── Veille-C6-synthese-S33-a-S36.pdf    son rendu (`scripts/rendre_pdf.py`), le format partageable ; produit le 08/09/2026, regénéré le 03/10 après correction des étiquettes de semaine
```

Le numéro de semaine ISO rend la récurrence lisible d'un coup d'œil : un trou dans la
suite se voit tout de suite, par moi comme par un évaluateur.

---

## 7. Glossaire

| Terme | En clair |
|---|---|
| **Veille** | Suivi organisé et régulier d'un sujet, pour rester à jour |
| **Injection de prompt** (*prompt injection*) | Texte glissé dans une donnée pour que le modèle le prenne pour une instruction |
| **Injection indirecte** | La même chose, mais cachée dans une page web ou un flux que l'agent va lire tout seul |
| **RSS / Atom** | Format ouvert par lequel un site publie ses nouveautés, lisible par un programme |
| **Garde-fou** (*guardrail*) | Contrôle qui filtre ce qui entre ou sort d'un modèle |
| **Préprint** | Article de recherche publié avant relecture par les pairs, donc une piste à confirmer |
| **RGAA** | Référentiel français d'accessibilité, obligatoire pour les sites publics |
| **AcceDe** | Guides d'accessibilité des documents publiés par la société Atalan |
| **Lecteur d'écran** | Logiciel qui lit un document à voix haute pour une personne aveugle |
| **AMF** | Autorité des marchés financiers : elle encadre le conseil en investissement en France |

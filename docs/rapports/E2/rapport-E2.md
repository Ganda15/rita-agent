<style>
.logo{ float:right; width:15mm; margin:7pt 0 2pt 12pt; }
.identite{ color:var(--ink-soft); font-size:9.4pt; }
.sommaire{ margin:9pt 0 2pt; padding:6pt 10pt 5pt; border:.5pt solid var(--rule); border-radius:2pt; }
.sommaire-titre{ font-family:Georgia,"Times New Roman",serif; font-weight:600; font-size:11pt; margin:0 0 4pt; }
.sommaire ol{ list-style:none; padding:0; margin:0; columns:2; column-gap:22pt; }
.sommaire li{ display:flex; justify-content:space-between; gap:8pt; margin:0 0 2pt; break-inside:avoid; font-size:9.4pt; }
.sommaire li a{ color:var(--ink); }
.sommaire li span{ color:var(--accent); font-weight:600; }
p, li{ orphans:3; widows:3; }
h2#criteres, h2#criteres + p{ break-after:avoid; }
</style>

<div><img class="logo" src="../E3/logo/rita-logo-marque.png" alt="Logo de RITA"></div>

# Rapport E2 : veille, choix d'un service de modèle, et son paramétrage

Projet fil rouge **RITA** · **Eramalingam Gandakumar** · Développeur en intelligence artificielle, RNCP 37827 · Simplon × Wild Code School · bloc de compétences 2, compétences C6 à C8 · version 0.7, 1er novembre 2026 · version de référence de l'application : commit `d3a4198` de `main`, en production le 27/10/2026 · code et preuves : dépôt GitHub privé `Ganda15/rita-agent`
{: .identite }

> **En une minute.** RITA rédige en français un court briefing sur une valeur boursière, avec un modèle de langage
> fourni par un service extérieur. **Pour le briefing, RITA a retenu Azure AI Foundry, modèle `gpt-5.4`, sur un
> déploiement configuré en zone de données de l'Union européenne.** Aujourd'hui, c'est le seul service que RITA
> appelle. OpenRouter a servi de comparateur dans le banc du 03/10 et de secours lors d'essais locaux ; depuis la
> correction du 31/10, la production utilise Azure seul. Mistral Large 4 attend sur une branche non fusionnée (PR #88).
> Pourquoi Azure : sur le banc du 03/10, ses textes passent les mêmes contrôles que ceux de Claude, sa médiane est deux
> fois plus courte, aucun frais n'est déclaré par le candidat, et son déploiement est configuré en *Data Zone Standard
> EU*, comme la règle du projet le demande ; trois appels du 09/10 ont indiqué Sweden Central. Cela documente notre
> configuration, pas l'ensemble des traitements contractuels. Limites : le banc a été mesuré sur le déploiement
> mondial, pas sur celui de la zone UE ; la note de français ne départage pas les services ; aucun secours n'existe si
> Azure tombe. Le rapport décrit aussi la veille qui nourrit ces choix (C6) et le paramétrage du service retenu (C8).
> Périmètre décidé le 31/10 : la version présentée au jury et ses cinq écrans ; les ateliers et copies d'exercice des
> sprints restent hors du rapport ; ce qui a été vérifié ou corrigé après est cité avec sa vraie date, et ce qui est
> seulement prévu est écrit comme tel.

<div class="sommaire" role="navigation" aria-label="Sommaire">
<p class="sommaire-titre">Sommaire</p>
<ol>
<li><a href="#lire">Lire ce rapport</a><span>p. 1</span></li>
<li><a href="#contexte">1. Le contexte, une seule fois</a><span>p. 1</span></li>
<li><a href="#c6">2. C6 : la veille technique et réglementaire</a><span>p. 2</span></li>
<li><a href="#c7">3. C7 : le choix du service de modèle</a><span>p. 4</span></li>
<li><a href="#c8">4. C8 : le service retenu, paramétré et suivi</a><span>p. 10</span></li>
<li><a href="#criteres">5. Les 20 critères, un par un</a><span>p. 13</span></li>
<li><a href="#reste">6. Ce qui n'est pas fait</a><span>p. 15</span></li>
<li><a href="#glossaire">Glossaire</a><span>p. 15</span></li>
<li>Annexe A1 à A3 : les schémas (PDF avec annexe)<span>p. 17</span></li>
</ol>
</div>

## Lire ce rapport {: #lire }

Trois compétences, trois questions. C6 : comment je me tiens informé, comment je juge une source, comment je partage,
et ce que ça change dans RITA. C7 : pourquoi ce service de modèle plutôt qu'un autre. C8 : comment on y accède, comment
il est configuré, surveillé, documenté et remis à quelqu'un d'autre. Un chiffre se cite mesuré, avec sa date et sa
source ; ce qui n'existe pas est écrit comme tel. Un brouillon de ce rapport existait en juillet 2026 dans mes notes ;
ses tableaux comparatifs portaient des scores d'exemple d'un gabarit de formation, jamais mesurés. **Rien n'en est
repris** ; ce rapport repart des faits. Chaque compétence a son schéma en annexe : A1 pour la veille, A2 pour le
choix du service, A3 pour le service tel qu'il tourne aujourd'hui (PDF avec annexe). Trois preuves s'ouvrent
directement dans le dépôt GitHub privé, à la version `922349d` (le formateur y a un accès en lecture, compte `bybysker`, vérifié le 30/10 ; l'accès du jury n'est pas
confirmé) :
[les 60 résultats bruts du banc](https://github.com/Ganda15/rita-agent/blob/922349da2042a6f2272f9c7c0738641aa63eb1f3/evidence/C7/resultats-2026-10-03.jsonl),
[le réglage d'Azure](https://github.com/Ganda15/rita-agent/blob/922349da2042a6f2272f9c7c0738641aa63eb1f3/src/llm.py#L31-L36) et [son test](https://github.com/Ganda15/rita-agent/blob/922349da2042a6f2272f9c7c0738641aa63eb1f3/tests/test_llm.py#L13-L18),
[le guide d'exploitation](https://github.com/Ganda15/rita-agent/blob/922349da2042a6f2272f9c7c0738641aa63eb1f3/docs/exploitation.md).

---

## 1. Le contexte, une seule fois {: #contexte }

RITA rédige en français un briefing court sur une valeur boursière, à partir de données collectées (cours, taux, séries
macroéconomiques, articles de presse) et d'un modèle de langage fourni par un service extérieur. Depuis le 16/10, elle
répond aussi à des questions libres à partir des articles collectés. Trois contraintes tiennent tout : jamais de
recommandation d'achat ou de vente (AMF) ; aucune position ni aucun prix de revient envoyé au modèle ; et, règle du
projet posée le 05/10, aucune donnée personnelle hors de l'Union européenne. Le rapport E1 décrit les données, le
rapport E3 l'API, les tests, le monitorage et la livraison. Celui-ci décrit **ce qui vient de l'extérieur** : l'état de
l'art que je suis, le service que je choisis, et la façon dont je le paramètre.

---

## 2. C6 : la veille technique et réglementaire {: #c6 }

### 2.1 Le sujet, et pourquoi lui

Ma veille porte sur la **sécurité des agents de modèles de langage, et d'abord l'injection de prompt** : une instruction
placée dans un contenu que le modèle doit analyser, pour détourner son comportement. Le sujet touche RITA directement :
les titres et résumés des articles collectés par flux RSS (`sources/rss.py`) sont indexés, puis remontés par la
recherche documentaire dans le contexte du modèle, pour le briefing comme pour les questions. Un garde-fou relit ces
articles avant (`guardrails/injection.py`), et la veille sert à savoir ce qu'il vaut. Le scraping (`sources/scraper.py`)
ne collecte que des cotations : il n'alimente pas la recherche documentaire.

### 2.2 La méthode, telle qu'elle est pratiquée

| Élément | Ce qui est fait | Où |
|---|---|---|
| Le rythme prévu | une heure par semaine, le lundi de 9 h à 10 h | `docs/veille/README.md`, § 2 |
| Le relevé | je lis les flux RSS et Atom, et les pages, des cinq sources retenues ; les nouveautés sont regroupées dans un fichier par semaine, avec la période balayée, la date du relevé, les sources balayées et le lien de chaque candidat | `docs/veille/_candidats-2026-Sxx.md` |
| La note | une note par semaine, écrite par moi : le sujet, les sources, leur fiabilité, et « ce que ça change dans RITA » | `docs/veille/2026-Sxx-*.md` |
| Les sources | cinq sources principales, chacune avec la raison de sa fiabilité et ses intérêts éventuels ; les blogs d'éditeurs d'outils de sécurité sont écartés, parce qu'ils décrivent le problème qu'ils vendent | `docs/veille/README.md`, § 3 |
| L'outil | des flux RSS relevés à la main et des fichiers de suivi versionnés dans le dépôt, sans abonnement dédié à la veille ; les flux financiers que RITA collecte ne sont pas l'outil de cette veille | `docs/veille/README.md`, § 4 |

L'assistant de développement peut aider à lire les flux pendant le relevé ; il ne choisit pas les sujets et n'écrit
pas la note.

**Un exemple de qualification de source, tiré de la note S41.** La note retient un préprint d'arXiv (2610.03448, version
du 2 octobre 2026) qui réévalue des détecteurs d'injection. Auteur identifié (Zhuowen Liu, JAIST) ; aucun intérêt
commercial repéré ; c'est une prépublication, non relue par des pairs ; ses conclusions convergent avec celles d'un
autre préprint du même relevé (arXiv 2610.08571), sans confirmation indépendante des résultats. Réserve écrite : auteur unique, notoriété non établie, chiffres cités
tels que l'auteur les rapporte, rien répliqué. Le même relevé écarte deux autres préprints pour intérêt commercial.

**Les sources, une par une.** Le protocole retient cinq sources principales et deux sous condition
(`docs/veille/README.md`, § 3). Chaque note qualifie celles qu'elle utilise dans un tableau « auteur identifié,
intérêt commercial, confirmée ailleurs » ; le tableau ci-dessous reprend ces qualifications, note par note, avec ce qui
reste incertain.

| Source (notes) | Pourquoi je lui fais confiance | Ce qui a été recoupé | Ce qui reste incertain |
|---|---|---|---|
| OWASP GenAI Security Project (S33, S34) | fondation à but non lucratif, aucun produit à vendre ; contributeurs nommés, dont les trois responsables du Top 10 agentique (S34) | S34 : lu dans le PDF d'origine, pas dans un résumé ; S33 : reprise par des médias spécialisés | les médias de reprise ne sont pas nommés dans la note S33 |
| ANSSI et CERT-FR (S33) | agence de l'État, source primaire officielle ; site public soumis au RGAA | source primaire : rien au-dessus à recouper | recommandations d'avril 2024 ; aucune publication sur le sujet dans la fenêtre du relevé S41 |
| CNIL et Conseil de l'IA et du Numérique (S34) | autorité administrative indépendante, aucun intérêt commercial ; site soumis au RGAA | note cosignée par deux institutions | note exploratoire de juillet 2026, pas une recommandation |
| NIST, AI Risk Management Framework (S34) | agence fédérale américaine, référence internationale ; site soumis à la Section 508 | retenu comme référence, sans autre recoupement écrit | cadre général de janvier 2023, pas propre à l'injection |
| Simon Willison (S33, S34, S36) | auteur identifié, a forgé le terme « prompt injection » en 2022 ; blog personnel, ne vend rien | S36 : son récit concorde avec ceux de Johann Rehberger et de The Register | blog sans relecture par des pairs ; aucun billet sur le sujet dans la fenêtre S41 |
| Presse et chercheurs hors liste (S36) | Johann Rehberger, chercheur connu pour l'injection indirecte ; The Register, rédaction identifiée, rien à vendre | les deux se confirment, et Willison les reprend | sources secondaires, retenues pour un seul épisode |
| Préprints arXiv `cs.CR` (S34, S35, S36, S41) | auteurs nommés, aucun intérêt commercial repéré pour ceux retenus | S34 : résultat reproduit dans la note ; S41 : conclusions convergentes avec un autre préprint (arXiv 2610.08571) | non relus par des pairs ; S35 et S36 isolés, retenus comme signal, pas comme preuve ; S41 : auteur unique, notoriété non établie |
| Éditeurs de modèles (Anthropic, OpenAI) | expertise réelle sur leurs propres modèles | toujours croisés avec OWASP, l'ANSSI ou un travail universitaire | intérêt commercial direct : jamais source unique |

### 2.3 Ce qui a été produit, semaine par semaine

| Semaine | Relevé | Note | Comment |
|---|---|---|---|
| S33 (10 au 16/08) | oui | oui | créneau tenu |
| S34 (17 au 23/08) | oui | oui | créneau tenu |
| S35 (24 au 30/08) | oui (25/08) | oui | note écrite en rattrapage le 08/09, l'en-tête le dit |
| S36 (31/08 au 06/09) | oui (31/08) | oui | note écrite en rattrapage le 08/09 |
| S37 (07 au 13/09) | oui (08/09) | non | |
| S38, S39 (14 au 27/09) | non | non | deux semaines sans séance |
| S40 (28/09 au 04/10) | oui (28/09) | non | |
| S41 (05 au 11/10) | oui (11/10) | oui | créneau du lundi non tenu ; relevé et note en rattrapage le 11/10 |
| S42 à S44 (12/10 au 01/11) | non | non | rien de conservé dans le dépôt |

Sept relevés et cinq notes sont conservés entre S33 et S44, cette dernière étant encore en cours au 31 octobre. Trois
notes ont été rédigées en rattrapage. Le rythme hebdomadaire prévu n'a pas été maintenu. Au 31 octobre, aucun nouveau
relevé ni aucune nouvelle note n'est conservé dans le dépôt depuis le 11 octobre.

### 2.4 Ce que la veille a changé dans RITA

Chaque note se termine par « ce que ça change dans RITA ». Le changement le plus net vient de la note S34 (17/08) : le
garde-fou d'injection affichait 100 % de blocage, mais ses 7 cas d'évaluation avaient été écrits à partir de ses
propres motifs. Après l'ajout de trois cas adverses, le filtre bloque 7 attaques sur 10. Aucun faux positif n'est
observé sur les 8 textes légitimes du jeu. Ce petit échantillon révèle des limites, mais ne mesure pas la sécurité
générale de RITA.

Le seuil cible reste fixé à 85 %. Le test est marqué en échec attendu (`xfail`, `tests/test_evals.py`) : cette
insuffisance reste visible dans chaque rapport de tests, mais elle ne bloque pas la chaîne. Une CI verte ne signifie
donc pas que le seuil est atteint. La note S41 (11/10) a confirmé la leçon avec la littérature : un détecteur peut
réussir le test sur lequel il a été entraîné et rater presque tout sur un autre jeu.

### 2.5 Le partage

| Date | À qui | Canal | Note | Ce qui est prouvé |
|---|---|---|---|---|
| 16/08 | la promotion | Discord, canal général | S33 | partage consigné dans le journal ; capture absente ; aucun retour documenté |
| 11/10 | la promotion | Discord, canal #veille, 20 h 04 | S41, avec une question ouverte | partage prouvé par capture (`evidence/C6/envoi-2026-10-11-promo-discord-veille.png`) ; aucune réponse au 31/10 |
| | le formateur | mail et PDF | S33 | l'envoi reste indiqué comme non effectué dans le suivi |

Une synthèse des quatre premières notes existe en PDF (`docs/veille/Veille-C6-synthese-S33-a-S36.pdf`) ; aucune preuve
d'envoi n'est trouvée. Le registre des envois (`docs/veille/_JOURNAL-DES-ENVOIS.md`) le dit lui-même : un message sans
réponse prouve qu'on a publié, pas qu'on a animé un travail collectif. Ce qui manque, c'est un échange collectif
documenté.

### 2.6 L'accessibilité

Le protocole fixe des règles d'accessibilité pour les notes (`docs/veille/README.md`, § 5.4), et chaque note a une
liste de contrôle avant publication : titres sans niveau sauté, liens nommés, texte alternatif, tableaux avec en-tête,
aucune information portée par la seule couleur, résumé en langage clair, glossaire. La vérification n'est pas
consignée : dans la note S41, les cases de cette liste ne sont pas cochées. La synthèse S33 à S36, qui sera remise avec les livrables, a été rendue au
format lisible et contrôlée le 01/11 (texte à 12 pt, 45 signets, liens soulignés ;
`evidence/C6/controle-accessibilite-synthese-2026-11-01.md`) ; ce n'est pas un audit PDF/UA complet. Les notes sont en Markdown, lisibles sur
GitHub ; la synthèse existe aussi en PDF.

### 2.7 Les limites, dites franchement

- **Le rythme hebdomadaire n'a pas été maintenu** : sept relevés et cinq notes entre S33 et S44, dont trois notes en
  rattrapage ; rien de conservé dans le dépôt depuis le 11/10.
- **Aucun échange collectif documenté** : deux partages à la promotion sans réponse documentée, aucun envoi au
  formateur prouvé.
- **Le partage du 16/08 n'a pas de capture.**
- **La vérification d'accessibilité des notes n'est pas consignée.**

---

## 3. C7 : le choix du service de modèle {: #c7 }

### 3.1 Le besoin

Au 03/10, date du banc, RITA demandait au modèle **une seule tâche** : rédiger en français un briefing court (600 à
900 caractères) sur une valeur, à partir de faits fournis dans le prompt et de passages d'articles. Le plan du banc,
écrit avant toute mesure (`docs/PLAN-C7-benchmark.md`, § 1), en tire des contraintes vérifiables :

| Contrainte | Comment on la mesure |
|---|---|
| Jamais de recommandation d'achat ou de vente | textes retenus par le garde-fou de sortie |
| Fidélité aux faits fournis | contrôle automatique minimal : le cours est dans le texte, et aucun signal lexical uniquement contraire à la variation |
| Un français lisible par un particulier | une note de 0 à 2 par texte, fournisseur masqué |
| Une latence acceptable | médiane et 95e centile, sans seuil fixé à l'avance |
| Le coût par briefing | jetons rapportés par le fournisseur, prix public daté |
| Aucune donnée personnelle dans le prompt | contrôle automatique du prompt envoyé |
| Aucune donnée personnelle hors de l'UE (règle du projet, 05/10) | type de déploiement et région renvoyée par le service |

Ce que le besoin n'exige pas : du code, de l'image, de la conversation, un long contexte (le prompt tient en moins de
1 000 jetons). Depuis le 16/10, un second usage s'ajoute : répondre à une question libre à partir des articles
(`/question`), avec Azure seul et une réponse au format JSON imposé (registre RGPD, T8). Le banc du 03/10 ne le couvre
pas.

**Le budget qui a pesé sur le choix.** Deux règles l'encadrent : aucune nouvelle dépense hors modèle (3.2), et des
montants séparés selon qu'ils sont facturés, payés ou seulement estimés (`docs/BUDGET.md`). Le tableau ne reprend que
les deux services comparés, pas tout le budget de RITA.

| | Azure AI Foundry, `gpt-5.4`, retenu | OpenRouter, `claude-sonnet-4.5`, comparé le 03/10, plus appelé aujourd'hui |
|---|---|---|
| Facturé ou payé | 0 € déclaré pour le candidat (déclaration du 31/10, non vérifiée sur le portail de gestion des coûts) | 425,04 $ de recharges payées de mai à octobre (11 reçus), sur un compte qui peut servir à d'autres projets : ce ne sont pas des coûts de RITA ; la consommation de la clé de RITA n'est pas encore lue |
| Estimé au prix public, par briefing | 0,0047 USD (2,50 USD par million de jetons d'entrée, 15,00 en sortie, relevé du 03/10) | 0,0060 USD |
| Estimé pour le banc du 03/10 | 0,14 USD au prix public pour les 30 appels du quatrième passage comparatif (19 314 jetons d'entrée, 6 115 en sortie) ; 0 € déclaré par le candidat, facturation non vérifiée | 0,18 USD pour les 30 appels du quatrième passage comparatif ; environ 0,68 $ sur les cinq passages du jour, pris sur les crédits déjà rechargés |

Sources : `evidence/C7/prix-et-environnement-2026-10-03.md` et `evidence/C7/resultats-2026-10-03.jsonl` (jetons
recomptés le 01/11). Le plafond était fixé avant toute mesure : 5 USD pour tout le banc, un paramètre du script qui
l'arrête au-delà (décision D2, `docs/PLAN-C7-benchmark.md`) ; la dépense estimée est restée en dessous. Le budget
favorise donc Azure, tant que cette prise en charge dure. Si elle cessait, l'écart au
prix public resterait faible, 0,0013 USD par briefing : le coût ne départagerait presque plus, et le choix reposerait
sur la latence et sur la règle UE seule (3.6).

### 3.2 Les services comparés, et ceux qui ne le sont pas

Le périmètre du banc a été fixé le 03/10, avant toute mesure (`docs/PLAN-C7-benchmark.md`, décision D1) : les services
déjà branchés dans `src/llm.py`. Les services cités dans un brouillon de juillet (Gemini, Llama, Mistral) y avaient des
scores d'exemple, jamais mesurés : rien n'en est repris.

| Service | Place dans l'étude | Raison |
|---|---|---|
| Azure AI Foundry, `gpt-5.4` (OpenAI) | comparé sur le banc, 30 appels | branché dans `src/llm.py` ; seul service appelé aujourd'hui |
| Claude par OpenRouter | comparé sur le banc, 30 appels | branché dans `src/llm.py` le 03/10 ; plus appelé aujourd'hui (4.2) |
| Claude par l'API d'Anthropic | inclus, non mesuré | aucune clé sur le poste le 03/10 ; plus appelé aujourd'hui (4.2) |
| Mistral Large 3 et 4 | hors banc : essai ponctuel du 10/10, un briefing par modèle (3.4) | ajouté après le banc, sur la branche `mistral-ue` |
| Gemini | non étudié | hors du périmètre fixé par la décision D1 : il n'était pas branché dans le code |
| Un modèle local (Llama) | exclu | aucune machine du projet n'a la mémoire pour un modèle de qualité suffisante ; « local » ne veut dire ni gratuit ni plus sobre sans mesure |
| Services à carte bancaire ou nouvel abonnement | exclus | aucune nouvelle dépense hors modèle |
| Services aux conditions de traitement illisibles | exclus | impossible de savoir où vont les données |

Mistral a été choisi le 10/10 comme futur second fournisseur, hébergé dans l'Union européenne, sous conditions
(contrat lu, banc) ; il n'est ni validé ni actif dans la version livrée (3.6).

### 3.3 La comparaison du 03/10 : GPT par Azure contre Claude par OpenRouter

Même jeu de dix cas, figé avant la mesure et construit par le code réel (les sept valeurs du portefeuille de
démonstration, la plus forte hausse, la plus forte baisse, une valeur cotée à Londres) ; trois répétitions par cas ;
même prompt que le rédacteur. L'API directe d'Anthropic n'a pas pu être mesurée : aucune clé sur le poste. Claude,
par OpenRouter, est ici le service comparé ; le même jour, sur le poste, OpenRouter avait aussi servi de secours quand
Azure et Anthropic n'avaient pas encore de clé. RITA ne l'appelle plus, ni sur le poste depuis le 11/10, ni en
production depuis le 31/10 (4.2).

| Mesure | Azure AI Foundry, `gpt-5.4` (Global Standard) | OpenRouter, `claude-sonnet-4.5` |
|---|---|---|
| Disponibilité | 30 sur 30 | 30 sur 30 |
| Textes acceptés par le garde-fou de sortie (contrainte AMF) | 30 sur 30 | 30 sur 30 |
| Contrôle minimal de fidélité (cours présent, pas de signal uniquement contraire) | 30 sur 30 | 30 sur 30 |
| Latence, médiane et 95e centile | 3,21 s et 10,69 s ; 2 appels sur 30 au-dessus de 10 s | 6,33 s et 7,20 s |
| Coût par briefing | 0 € déclaré pour le candidat sur cette ressource ; 0,0047 USD au prix public | 0,0060 USD au prix public |
| Qualité du français, de 0 à 2 | 30 textes notés 1 ; moyenne 1,00 | 30 textes notés 1 ; moyenne 1,00 |

Source : `evidence/C7/preuve-benchmark-2026-10-03.md`, § 9, et les résultats bruts
(`evidence/C7/resultats-2026-10-03.jsonl`, où les 2 appels sur 30 ont été recomptés). Les intervalles de confiance de
Wilson sont identiques pour les deux services, de 0,89 à 1,00 sur chaque proportion. Ces mesures datent du 03/10, sur
le déploiement Azure **Global Standard** de l'époque ; le déploiement en zone de données UE (`gpt-5.4-dzs-eu`) a été
vérifié séparément le 09/10, sur trois appels (4.1), et le banc n'a pas été rejoué sur lui. Pour la ressource Azure, 0 €
est déclaré pour le candidat, sur la période du banc comme depuis (déclaration du 31/10, non vérifiée sur le portail de
gestion des coûts, `docs/BUDGET.md`) ; le prix public est donné à part, pour rester vrai si cette prise en charge s'arrête.

**Ce que ces chiffres disent, et ce qu'ils ne disent pas.** Sur les contrôles automatiques, les deux services sont
indiscernables. Le contrôle de fidélité est minimal : présence du cours, et absence d'un signal lexical uniquement
contraire à la variation attendue. Il ne valide ni les dates ni toutes les affirmations du texte. Ce qui distingue les services : la latence (GPT deux fois plus rapide en médiane, avec une queue plus
longue) et le coût.

**Le détail par cas.** Les 60 résultats bruts : 10 cas, 2 services, 3 répétitions par cas
(`evidence/C7/resultats-2026-10-03.jsonl`). Sur chaque cas, les deux services passent les 3 fois le garde-fou de
sortie et le contrôle minimal de fidélité ; ce qui les sépare, c'est la durée, donnée en médiane et en maximum des
3 appels.

| Cas | Pourquoi ce cas | Azure `gpt-5.4`, médiane / maximum | OpenRouter Claude, médiane / maximum |
|---|---|---|---|
| AI.PA | portefeuille | 3,20 s / 3,48 s | 5,69 s / 6,08 s |
| BNP.PA | portefeuille | 4,47 s / 6,84 s | 6,88 s / 7,20 s |
| MC.PA | portefeuille | **10,69 s / 11,86 s** | 6,42 s / 6,47 s |
| OR.PA | portefeuille | 5,57 s / 6,33 s | 6,03 s / 6,06 s |
| SAN.PA | portefeuille | 2,81 s / 2,97 s | 6,55 s / 6,58 s |
| SU.PA | portefeuille | 3,39 s / 3,49 s | 6,32 s / 7,04 s |
| VIRI.PA | portefeuille, sans article retrouvé | 2,60 s / 2,91 s | 6,34 s / 6,90 s |
| CO.PA | plus forte hausse de la séance (+9,09 %) | 2,49 s / 4,00 s | 5,29 s / 5,73 s |
| ALMKT.PA | plus forte baisse (−11,29 %), sans article | 2,57 s / 2,60 s | 6,87 s / 7,18 s |
| HSBA.L | cotée à Londres, en livres, sans article | 3,21 s / 5,60 s | 6,31 s / 7,30 s |

**Ce que le détail montre.** Les deux appels d'Azure au-dessus de 10 secondes portent sur le même cas, MC.PA ; sur
les neuf autres, aucun appel ne dépasse 7 secondes. Claude est plus régulier, entre 5,29 et 6,88 s de médiane et
jamais plus de 7,30 s. Sur ce banc, Azure est donc plus rapide en médiane, mais ses appels les plus lents sont plus
longs. La taille de la consigne n'explique pas MC.PA (754 jetons d'entrée, contre 686 en médiane ; des réponses de
longueur comparable), et le premier appel sur ce cas n'a pris que 4,34 s. La cause des deux appels lents n'est pas
établie : trois répétitions ne permettent pas d'en écarter une.

**Ce que chaque service choisit de citer.** Le prompt donne treize indicateurs par valeur, et le briefing tient en
trois à cinq phrases : le modèle choisit. Sur les mêmes 60 textes, j'ai compté, pour chaque indicateur, les textes où
sa valeur apparaît avec la virgule française et le même nombre de décimales que dans le prompt
(`evidence/C7/mesure-indicateurs-cites.py`, note du 03/10 `evidence/C7/indicateurs-cites-dans-les-textes-2026-10-03.md`,
relancé le 01/11 avec les mêmes totaux). C'est une heuristique : un chiffre arrondi autrement n'est pas compté, un
chiffre identique par hasard l'est.

| Indicateur reçu par le modèle | Azure `gpt-5.4`, textes qui le citent (sur 30) | OpenRouter Claude (sur 30) |
|---|---|---|
| Cours de clôture | 30 | 29 |
| Variation du jour | 30 | 30 |
| Capitaux échangés en moyenne sur 20 séances | 14 | 1 |
| Performance sur 1 semaine | 29 | 20 |
| Performance sur 1 mois | 28 | 21 |
| Performance depuis le 1er janvier | 24 | 15 |
| Performance sur 1 an | 10 | 9 |
| Moyenne mobile sur 20 séances | 30 | 29 |
| Moyenne mobile sur 50 séances | 29 | 22 |
| Distance au plus haut sur 1 an | 10 | 14 |
| Volatilité annualisée | 17 | 21 |
| Drawdown maximal sur 1 an | **0** | **0** |
| RSI 14 | 29 | 28 |
| **En moyenne, par texte** | **9,3 sur 13** | **8,0 sur 13** |

**Ce que ce comptage montre.** Les deux services ne retiennent pas les mêmes chiffres. GPT cite davantage les
performances récentes et les capitaux échangés (14 textes contre 1) ; Claude cite davantage la volatilité et la
distance au plus haut. Pour le drawdown, la méthode de comptage n'a détecté sa valeur dans aucun des 60 textes. La
cause n'est pas établie : un libellé
anglais dans un prompt français, une valeur toujours négative qui renvoie à un creux parfois ancien, ou la concurrence
des autres chiffres. Un autre libellé permettrait de le tester ; celui du prompt n'a pas changé depuis
(`agents/analyst.py`, ligne 84). Ce comptage ne dit ni si les chiffres cités sont justes, ni ce dont le lecteur a
besoin : il décrit une manière de résumer, et il n'a pas pesé dans le choix.

**La qualité du français.** Les 60 textes du 03/10 ont été notés le 31/10, de 0 à 2, fournisseur masqué, avec des
remarques factuelles séparées de la note (`evidence/C7/notes-francais-2026-10-03-notation-2026-10-31.csv`, copie
datée ; le fichier d'origine et ses textes sont intacts). Notes et remarques ont été proposées avec l'aide de Codex,
puis relues, corrigées si nécessaire et validées par moi : c'est une évaluation assistée par IA, pas une évaluation
humaine indépendante. La correspondance entre textes et fournisseurs n'a été ouverte qu'après l'enregistrement des 60
notes. Les 60 textes ont reçu la note de 1 sur 2 pour la qualité du français, selon une évaluation assistée par IA puis
relue et validée par moi. Ce critère ne départage pas les fournisseurs. Le choix doit donc s'appuyer également sur les
autres mesures du benchmark et leurs limites.

Les remarques ont pourtant appris quelque chose. Elles relèvent des défauts qui reviennent : le RSI et les moyennes
mobiles jamais expliqués pour un lecteur débutant, « demain » ou « séance du jour » sans la date de la séance
collectée, des « seuils » présentés comme techniques alors qu'ils ne sont qu'une moyenne arrondie. Et en séparant le
français des faits, elles ont trouvé trois erreurs que le contrôle automatique a laissé passer :
une période inventée, « le mois de février », pour une performance sur un mois (texte 26) ; deux journées d'un article
présentées comme des replis alors que l'une finissait à l'équilibre, une erreur sur le **sens** d'une variation
(texte 32) ; un cours du 2 octobre attribué au 21 septembre (texte 35). **Pourquoi le contrôle les a laissées passer** :
il ne vérifie que deux choses : la présence du cours fourni, et qu'un texte ne contienne pas seulement des mots de
baisse quand la séance monte, ou seulement des mots de hausse quand elle baisse (`evals/benchmark_fournisseurs.py`,
lignes 101 à 113). Si les deux sortes de mots sont présentes, ou aucune, il passe. Il ne lit ni les dates, ni le sens
des autres journées citées. Il est donc à élargir aux dates et aux variations tirées des articles.

### 3.4 L'essai de Mistral du 10/10

Un vrai briefing (MC.PA, même prompt qu'Azure) a été servi par Mistral Large 3, puis par Mistral Large 4 sans
réflexion. Large 3 a inventé une date de séance ; Large 4 non ; le coût est voisin (0,10 contre 0,08 centime). C'est
**un seul briefing par modèle**, pas un banc. Cette mesure vit sur la branche `mistral-ue`
(`evidence/C8/preuve-briefing-mistral-2026-10-10.md`), dont la pull request (#88) n'est pas fusionnée : Mistral n'est
pas dans la version présentée.

### 3.5 L'environnement et les prérequis techniques

**L'environnement** (`evidence/C7/prix-et-environnement-2026-10-03.md`, relevé du 03/10). Microsoft publie des chiffres
d'entreprise vérifiés (exercice 2025 : 21,1 millions de tonnes équivalent CO2 ; électricité renouvelable directe ;
PUE 1,17). Aucun des deux éditeurs ne publie de chiffre par modèle : OpenAI donne une moyenne de 0,34 Wh par requête,
sans méthode ; Anthropic, rien. L'ordre de grandeur, de 0,3 à 18 Wh par briefing selon la source, reste une hypothèse,
pas une mesure.

**Les prérequis des deux services comparés**, lus dans le code (`src/llm.py`) et dans les réponses des services
(`evidence/C7/prix-et-environnement-2026-10-03.md`). Pour les deux, la clé vit dans une variable d'environnement, jamais
dans le code.

| Prérequis | Azure AI Foundry, `gpt-5.4` | OpenRouter, `claude-sonnet-4.5` |
|---|---|---|
| Point d'accès | compatible OpenAI, adresse finissant par `/openai/v1` (`AZURE_FOUNDRY_ENDPOINT`) ; le nom du déploiement sert de modèle | `https://openrouter.ai/api/v1/chat/completions`, modèle `anthropic/claude-sonnet-4.5` |
| Clé | `AZURE_FOUNDRY_API_KEY` | `OPENROUTER_API_KEY`, sur un crédit prépayé |
| Paramètre de longueur | `max_completion_tokens` : les modèles GPT-5 refusent `max_tokens` (erreur 400 mesurée le 03/10) | `max_tokens` |
| Délai d'attente fixé par RITA | 60 s | 60 s |
| Limites de débit | lues dans les en-têtes : 2 500 requêtes et 250 000 jetons par fenêtre | non relevées |
| Lieu du traitement | région renvoyée par Azure ; zone de données UE depuis le 09/10 (`gpt-5.4-dzs-eu`) ; avant, le déploiement mondial pouvait traiter un appel dans n'importe quelle région | routé vers l'un de sept points de sortie (chez Anthropic, AWS, Azure ou Google Vertex) ; les 10 appels journalisés le soir du 03/10 ont tous été servis par Amazon Bedrock, région non nommée |

### 3.6 La recommandation

**Le choix, fondé sur le banc du 03/10 : Azure AI Foundry, `gpt-5.4`, pour le briefing.** Le même service est utilisé
pour les questions, mais cet usage n'a pas été évalué dans cette comparaison. Pourquoi pour le briefing : ses textes passent le garde-fou de sortie et le contrôle minimal de fidélité aussi souvent que ceux de
Claude, et son français est noté au même niveau ; aucun frais n'est déclaré pour le candidat sur cette ressource ; sa
médiane est plus courte ; et son déploiement est configuré en *Data Zone Standard EU*, comme la règle du projet le
demande pour les données ; trois appels du 09/10 ont indiqué Sweden Central. Cela documente notre configuration, pas
l'ensemble des traitements contractuels : le contrat de Microsoft n'a pas été relu en entier.

| Service | Verdict | Pour | Contre |
|---|---|---|---|
| Azure AI Foundry, `gpt-5.4` (mesuré le 03/10 en Global Standard ; en zone UE depuis le 09/10) | **retenu** | 30 textes sur 30 acceptés par le garde-fou de sortie et fidèles au contrôle minimal ; 0 € déclaré pour le candidat ; médiane 3,21 s ; déploiement configuré en zone UE depuis le 09/10 | 2 appels sur 30 au-dessus de 10 s ; prise en charge des frais qui peut cesser ; banc non rejoué en zone UE ; contrat de Microsoft non relu en entier |
| Claude par OpenRouter | **écarté** | 30 textes sur 30 acceptés par le garde-fou de sortie et fidèles au contrôle minimal ; latence régulière (95e centile 7,20 s) | payant ; traitement dans l'UE non garanti, contraire à la règle du 05/10 |
| Claude par l'API d'Anthropic | **écarté, non mesuré** | même famille Claude, version configurée différente (`claude-sonnet-5` en accès direct, `claude-sonnet-4.5` mesuré par OpenRouter) | API directe non mesurée, faute de clé ; société établie aux États-Unis, traitement dans l'UE non garanti |
| Mistral Large 4, adresse européenne | **choisi le 10/10 comme futur second fournisseur, sous conditions ; non validé, non actif** | hébergé dans l'UE ; sur un briefing, n'a pas inventé la date que Large 3 inventait | un seul briefing mesuré ; contrat non lu ; absent du code livré (PR #88) |

**La configuration actuelle.** OpenRouter a servi de comparateur dans le banc du 03/10 et de secours lors d'essais
locaux. Le 10/10, j'ai décidé de remplacer
Anthropic et OpenRouter par Mistral en Europe, et le 11/10 de n'appeler qu'Azure tant que le contrat de Mistral n'est
pas lu (`CONTINUITE.md`). Jusqu'au 31/10, ces décisions n'étaient appliquées que sur mon poste ; la production gardait
Claude en repli. Corrigé le 31/10 : Azure seul par défaut, en production comme sur le poste (4.2).

**Le secours envisagé.** Mistral Large 4 deviendra le second fournisseur à deux conditions : son contrat lu, et un banc
Azure contre Mistral. D'ici là, il n'existe pas de secours : une panne d'Azure rend le briefing indisponible (4.2).

Ce qui ferait changer la décision : la queue de latence pendant une démonstration, la fin de la prise en charge des
frais de la ressource Azure, ou un banc où Mistral ferait nettement mieux.

### 3.7 Ce qui n'est pas fait

- **La notation du français** est assistée par IA, puis validée par moi : ce n'est pas un jugement humain indépendant,
  et son barème à trois niveaux ne départage pas les services.
- **Le banc Azure contre Mistral**, prévu le 11/10 : pas fait ; Mistral n'a été essayé que sur un briefing. Pour ce
  rendu, je m'appuie sur le banc historique du 03/10, complété par une notation datée, assistée par IA et validée
  par moi. Ce report protège le temps des autres livrables ; il n'est pas imposé par une impossibilité technique : le
  banc pourrait tourner à part, sur la branche, sans toucher la production.
- **L'usage Question** (`/question`) n'est pas mesuré par le banc.
- **L'API directe d'Anthropic** n'a jamais été mesurée, faute de clé.
- **La variation d'un jour à l'autre** n'est pas mesurée : tout date du 03/10.
- **Le contrat de Mistral** (sous-traitants, conservation, entraînement) n'est pas lu.

---

## 4. C8 : le service retenu, paramétré, surveillé, documenté {: #c8 }

### 4.1 L'accès au service

Le service retenu en C7 est **Azure AI Foundry**, le service de modèles de Microsoft, avec le modèle `gpt-5.4`. RITA
l'appelle par un point d'accès compatible avec l'API d'OpenAI (l'adresse se termine par `/openai/v1`), sur un
**déploiement** (l'instance du modèle réservée au projet) nommé `gpt-5.4-dzs-eu`. Depuis le 09/10, ce déploiement est en
**Data Zone Standard EU** : le traitement des appels est configuré dans la zone de données de l'Union européenne.
Trois appels du 09/10 ont indiqué Sweden Central. Cela documente notre configuration, pas l'ensemble des traitements
prévus par le contrat de Microsoft, qui n'a pas été relu en entier.

L'accès demande une clé. Elle est lue dans l'environnement de la machine (`AZURE_FOUNDRY_API_KEY`), jamais écrite
dans le code ni dans Git ; un **hook** (un contrôle automatique de l'outil de développement) refuse qu'un agent écrive
dans le fichier de secrets. L'API de RITA est elle-même protégée par sa propre clé (`X-API-Key`), demandée sur
`/briefing`, `/question` et les routes de données.

**Preuves.** Le 09/10 à 22:54, trois appels réels par le code de RITA (`src/llm._appel_foundry`) ont reçu HTTP 200,
modèle `gpt-5.4-2026-03-05`, région renvoyée par Azure : Sweden Central
(`evidence/C8/preuve-deploiement-zone-eu-2026-10-09.md`). Le 21/10, une trace de briefing servi en production a été
ouverte dans Langfuse (`evidence/sprint-4/captures/langfuse-trace-briefing-racine-2026-10-21.png` et
`evidence/sprint-4/captures/langfuse-trace-briefing-generation-2026-10-21.png`). Le parcours Question n'appelle qu'Azure, sans repli vers un autre
fournisseur (registre RGPD, T8).

### 4.2 La configuration

**Ce que le service doit faire.** Rédiger en français un briefing court sur une valeur, à partir des seuls faits
fournis, sans jamais recommander d'acheter ou de vendre (contrainte AMF). Le prompt du rédacteur porte cette consigne
(`agents/analyst.py`) ; un garde-fou d'entrée et un garde-fou de sortie la font respecter, en code testé. Les modèles
GPT-5 refusent le paramètre `max_tokens` : RITA envoie `max_completion_tokens` (erreur 400 mesurée le 03/10,
`src/llm.py`, lignes 71 à 73).

**Le réglage qui décide du fournisseur.** La variable `LLM_ORDRE` donne la liste des fournisseurs essayés dans l'ordre :
si le premier échoue sur une erreur technique, le suivant est appelé. Le code en connaît trois : Azure (`foundry`),
Anthropic et OpenRouter, ces deux derniers servant Claude. Deux décisions ont fixé la cible : le 10/10, remplacer
Anthropic et OpenRouter par Mistral, en Europe ; le 11/10, n'appeler qu'Azure tant que le contrat de Mistral n'est pas
lu (`CONTINUITE.md`). Raison : la règle du projet, aucune donnée personnelle hors de l'Union européenne
(registre RGPD, § 0), qu'Anthropic et OpenRouter ne garantissent pas.

**Ce que la mesure a montré, le 31/10.** Ces décisions n'étaient appliquées que sur mon poste de développement, par son
fichier de configuration. La valeur par défaut du code et de `docker-compose.yml` était restée
`foundry,anthropic,openrouter`, et c'est elle que la production utilisait : lue le 31/10 dans le conteneur
`rita-api-preprod` (démarré le 27/10), elle valait `foundry,anthropic,openrouter`. Sur une panne d'Azure, la production
aurait donc appelé Claude, hors de la règle. La version de référence `d3a4198` portait ce défaut. L'incident INC-008
(14/10) écrit « `LLM_ORDRE=foundry` » pour la production ; la lecture du 31/10 le contredit pour le conteneur du 27/10,
et l'état du 14/10 n'est plus vérifiable.

**Corrigé le 31/10.** Valeur par défaut `foundry` dans `src/llm.py`, `docker-compose.yml` et `.env.example`, test
écrit d'abord et vu en échec (`d1cbb7b`) ; un second test vérifie que Compose et le code donnent le même ordre. Fusion
dans `main` par la PR #170 (`97b329e`). La livraison a d'abord été **refusée deux fois par le serveur** : le fichier
Compose de l'image différait de la copie installée à la main le 14/10, et le script de déploiement, qui tourne en
`root`, refuse un fichier Compose non relu (`deploy/deployer.py`, `ComposeNonInstalle`). J'ai relu la différence et
installé la copie à la main, puis la livraison est passée à 13:54. Conteneur relu ensuite : `LLM_ORDRE=foundry`, et
`/health` annonce le commit `97b329e`.

**Le réglage dans le code**, à `922349d`, la version de `main` en production depuis le 01/11 (`src/llm.py`, lignes 31
à 36) :

```python
def _ordre_fournisseurs() -> list[str]:
    # Azure seul par défaut (règle UE seule, CONTINUITE.md, décision du 11/10) : l'ancien défaut gardait Anthropic et
    # OpenRouter en repli, et la production l'a pris (conteneur lu le 31/10). Mistral viendra en second après la
    # lecture de son contrat (PR #88) ; d'ici là, un autre ordre ne s'obtient qu'en posant `LLM_ORDRE`.
    ordre = os.getenv("LLM_ORDRE", "foundry")
    return [nom.strip() for nom in ordre.split(",") if nom.strip()]
```

Et son test (`tests/test_llm.py`, lignes 13 à 18), qui échouait avant la correction :

```python
def test_ordre_fournisseurs_defaut(monkeypatch):
    """Règle UE seule (CONTINUITE.md, décision du 11/10) : sans configuration, Azure seul, aucun repli hors UE.

    Lu le 31/10 dans le conteneur de production : `foundry,anthropic,openrouter`, venu de cette valeur par défaut."""
    monkeypatch.delenv("LLM_ORDRE", raising=False)
    assert _ordre_fournisseurs() == ["foundry"]
```

Sans variable `LLM_ORDRE`, la liste des fournisseurs ne contient qu'Azure. Les fonctions d'appel d'Anthropic et
d'OpenRouter restent dans le code sans servir : elles ne seraient appelées que si `LLM_ORDRE` les nommait, ce que la
production ne fait plus (conteneur relu le 31/10). Un second test vérifie que Compose ne
remplace pas cet ordre par le sien (`tests/test_docker_compose.py`, ligne 144).

**Ce qui reste ouvert.**
- **Aucun secours.** Mistral Large 4 a été choisi le 10/10 comme futur second fournisseur, sous conditions, mais il
  n'est ni validé ni actif : il n'existe que sur la branche
  `mistral-ue` (PR #88, ouverte depuis le 10/10, en conflit avec `develop`), et son contrat n'est pas lu. Si Azure
  tombe, `/briefing` répond 500 avec un identifiant de requête ; la réponse 503 « aucun fournisseur » prévue (#75)
  n'est pas faite.
- **Le prompt corrigé n'est pas en place.** L'option B, décidée le 11/10 et prévue pour le 16/10 (afficher la date de
  la séance, remplacer « point à surveiller pour la séance suivante » par un élément observable tiré des données),
  n'est pas appliquée : `agents/analyst.py`, ligne 17, dit toujours « Signale un point à surveiller pour la séance
  suivante ». La notation du français a relevé exactement ce défaut (3.3).
- **Le contrat de Microsoft** n'est pas relu en entier, ni les cas de traitement hors de sa zone de données que
  Microsoft documente (registre, § 5).

### 4.3 Ce qui est envoyé au service

Pour un briefing (registre RGPD, T6) : la valeur demandée, son cours, sa variation, les capitaux échangés en moyenne par séance sur vingt séances, la devise,
la fraîcheur des données, les 13 indicateurs et des passages d'articles de presse. **Aucune position, aucun prix de
revient, aucune quantité.** Ce qui reste personnel : la valeur demandée et l'heure de la demande disent ce qui
intéresse l'utilisateur. Pour une question (T8) : le texte de la question, qui peut contenir ce que l'utilisateur y
écrit, et les passages d'articles ; RITA ne conserve ni la question ni la réponse. La durée de conservation chez
Microsoft n'est pas vérifiée.

### 4.4 Le monitorage disponible

**Langfuse**, un service de traçage des appels aux modèles, en région Union européenne. Chaque briefing donne une
**trace** : une racine, une étape par nœud et par garde-fou, une génération par fournisseur essayé, avec modèle, jetons,
durée et type d'erreur. Le même identifiant de requête figure dans la réponse de l'API, dans le journal et dans la
trace. Depuis le 20/10, une trace ne garde que des **métadonnées** : ni le prompt ni la réponse du modèle
(`src/traces.py`). Le traçage est actif en production depuis le 21/10.

![Trace Langfuse d'un briefing servi en production le 21 octobre 2026 : appel à Azure, modèle gpt-5.4, 4,69 secondes, environ mille jetons, ni consigne ni réponse conservées](../../../evidence/sprint-4/captures/langfuse-trace-briefing-generation-2026-10-21.png)

*Trace d'un briefing servi en production le 21/10 à 12:51 (OR.PA) : l'appel à Azure (`llm-foundry`, modèle
`gpt-5.4-2026-03-05`) dure 4,69 s pour environ mille jetons, et la trace ne garde ni la consigne ni la réponse
(« undefined »). Le coût affiché, 0,006 $, est une estimation de Langfuse, pas une facture.*

**Les alertes.** Deux alertes Langfuse sont réglées depuis le 04/10 : observations en erreur, plus de 0 sur un jour ;
95e centile de la durée d'appel au modèle, plus de 15 000 ms sur un jour. Elles ouvrent une issue GitHub
(`evidence/C11/preuve-alertes-2026-10-04.md`). Le 23/10, une panne simulée sur une copie a déclenché l'alerte #130. La copie a
ensuite été isolée ; la vérification est détaillée dans E5. La chaîne d'alerte a donc fonctionné de bout en bout, et
elle a révélé une erreur de configuration. Le 24/10, elle a aussi ouvert à tort un nouveau ticket (#137) pour un simple
retour à la normale : corrigé dans `main` le 1er novembre 2026 (`922349d`), les tests de non-régression passent, sans
qu'un nouveau retour à la normale réel ait encore été observé ; l'incident est détaillé dans le rapport E5 (INC-009).

**La vigie.** La route `/sante` (`api/sante.py`) expose les signaux du service et leur verdict : erreurs, refus,
latence, coût, fraîcheur, avec des seuils écrits et argumentés (`monitorage/seuils.json`). Le coût est estimé au prix
public d'Azure relevé le 22/10 pour ce déploiement (`monitorage/prix.json` : 2,42 € par million de jetons en entrée,
14,52 € en sortie).

**Limites.** La supervision fournie par Azure lui-même (les métriques du portail) n'est décrite nulle part ; le guide
renvoie seulement à « l'état du service sur le portail Azure ». L'issue #77, ouverte par la première alerte du 04/10,
est toujours ouverte. Le contrat de Langfuse permet un traitement hors de la région choisie : la décision de le garder
ou de le remplacer n'est pas écrite (registre, § 5).

### 4.5 La documentation

Le guide d'exploitation est `docs/exploitation.md`. En tête : déployer, diagnostiquer une
panne, revenir à la version précédente, que faire pour chaque alerte, la vigie. En annexes : les clés et la gestion des
accès (§ 2), l'installation avec Docker (§ 3) et sans Docker (§ 4), la vérification et les tests (§ 5), les services
externes et leurs pannes (§ 6), les données manipulées et leurs lieux de traitement (§ 7). Des tests vérifient le guide
contre le code : chaque action d'alerte renvoie à une section qui existe, chaque commande citée existe
(`tests/test_exploitation_doc.py`). Ils ne remplacent pas la lecture du guide par une autre personne, et le fichier de
test le dit.

| Ce que le critère demande | Où le lire dans le guide |
|---|---|
| La gestion des accès | « 2. Les clés d'accès » : la clé de l'API de RITA, les autres clés, la règle commune à toutes |
| L'installation | section 3, la voie courte, avec Docker ; section 4, la voie longue, sans Docker |
| Le test | « 5. Vérifier que tout fonctionne » : le service répond, l'accès est restreint, les tests, la couverture |
| Les dépendances et interconnexions | « 6. Les services externes dont RITA dépend » |
| Les données impliquées | « 7. Les données manipulées », données personnelles comprises |
| L'exploitation courante | en tête du guide : déployer, diagnostiquer une panne, revenir en arrière, les alertes, la vigie |

**Corrigé le 31/10** : l'ordre des fournisseurs, les flux Google Actualités arrêtés le 16/10 et toujours cités, les
traces réduites aux métadonnées depuis le 20/10. Le PDF `docs/EXPLOITATION.pdf`, qui datait du 11/10, a été rendu de
nouveau le 31/10 depuis le guide à jour (35 pages). **Reste** : l'ancien chemin `docs/EXPLOITATION.md`, renommé le
22/10, est encore cité par `evidence/C8/README.md` et par un message d'erreur du script de déploiement.

### 4.6 La remise aux parties prenantes

Le référentiel demande que la documentation soit « communiquée aux parties prenantes dans un format qui respecte les
recommandations d'accessibilité ». **Ce n'est pas prouvé.** Aucun envoi daté du guide n'est consigné : ni dans
`docs/FILE-DE-VALIDATION.md`, ni dans `evidence/C8/` ; l'issue #43 est ouverte.

**Le format, lui, est prêt depuis le 31/10** (`evidence/C8/controle-accessibilite-guide-2026-10-31.md`). Le PDF est
rendu avec une option de lecture facilitée, écrite test d'abord : texte et tableaux à 12 pt, code à 11 pt, titres sans
empattement, liens soulignés plutôt que seulement colorés. Lu avec des outils de lecture de PDF : il est balisé, en
français, porte son titre, et compte 66 signets tirés des titres ; aucun lien ne renvoie plus vers un fichier du poste.
Ce n'est pas un audit PDF/UA complet : aucun outil de référence ni lecteur d'écran n'a été passé, et le contraste n'est
pas mesuré. Reste sa remise, **non prouvée à ce jour** : décision du 31/10, pas d'envoi séparé au formateur. Je
remettrai le guide avec les livrables du 05/11, dans mon dossier Drive partagé, en prévenant le formateur ; la preuve
datée dira quel fichier a été partagé, avec qui et quand, et sera conservée dans `evidence/C8/`. Avoir accès au dépôt
n'est pas avoir reçu le guide.

---

## 5. Les 20 critères, un par un {: #criteres }

Auto-évaluation du 31 octobre 2026, revue le 1er novembre. ✅ critère entier satisfait, avec preuve · ⚠️ preuve partielle · ❌ aucune preuve.

| Critère | État | Preuve ou manque |
|---|---|---|
| C6.1 thématique liée au projet | ✅ | injection de prompt, mobilisée dans `guardrails/injection.py` (2.1) |
| C6.2 temps de veille planifiés, une heure par semaine | ⚠️ | temps planifié : créneau du lundi, de 9 h à 10 h (`docs/veille/README.md`, § 2) ; exécution interrompue : sept relevés et cinq notes de S33 à S44, trois en rattrapage, rien depuis le 11/10 (2.3) |
| C6.3 outils d'agrégation cohérents avec sources et budget | ✅ | choix des flux RSS et Atom, justifié contre un agrégateur payant et les newsletters, budget 0 € (`docs/veille/README.md`, § 4) ; usage réel dans les relevés, dont S41 (2.2) ; limite : relevé à la main, sans outil automatique |
| C6.4 synthèses communiquées, format accessible | ⚠️ | notes en Markdown ; synthèse S33 à S36 rendue au format lisible et contrôlée le 01/11 (2.6) ; partage du 11/10 prouvé par capture ; envoi au formateur pas encore fait (2.5) |
| C6.5 informations conformes à la thématique | ✅ | les cinq notes portent sur la thématique (2.3) |
| C6.6 fiabilité des sources : auteur, compétences, intérêts | ⚠️ | qualification de l'auteur et de ses intérêts dans chaque note, mais incomplète : pour S41, la notoriété de l'auteur n'est pas établie (2.2) |
| C6.7 fiabilité des sources : contenu récent, sourcé, structuré | ✅ | les sources retenues sont datées et structurées : S41 s'appuie sur un préprint daté (v1 du 02/10/2026), avec son auteur, son statut et les sections citées ; les notes S33 à S36 datent et citent leurs sources (2.2) |
| C6.8 fiabilité des sources : accessibilité, recoupement | ⚠️ | S41 recoupée par un autre préprint seulement ; préférence pour les sources accessibles non démontrée (2.2) |
| C7.1 besoin reformulé, objectifs et contraintes | ✅ | besoin reformulé (un briefing court en français, à partir de faits fournis), contraintes mesurables, règle UE, usage Question (3.1) ; plafond du banc fixé avant la mesure, 5 USD (D2) ; limite : consommation réelle de la clé OpenRouter non lue, facturation Azure non vérifiée |
| C7.2 services étudiés et non étudiés | ✅ | inventaire : deux services comparés, un inclus mais non mesuré, Mistral hors banc, Gemini et modèle local non étudiés, chacun avec sa raison (3.2) |
| C7.3 raisons d'écartement | ✅ | services étudiés et non étudiés, chacun avec sa raison (3.2) : Gemini hors du périmètre de ce banc (décision D1, `docs/PLAN-C7-benchmark.md`), modèle local et services payants exclus, Claude écarté pour la règle UE (3.6) ; limite : Gemini n'est pas jugé moins bon, il est hors du périmètre |
| C7.4 adéquation au besoin, par service | ⚠️ | 30 appels par service, français noté ; fidélité minimale, usage Question et Mistral non mesurés (3.3, 3.7) |
| C7.5 démarche éco-responsable | ✅ | démarche « en fonction des informations disponibles » : relevé daté du 03/10 qui sépare les chiffres d'entreprise, ceux des éditeurs et ce qui reste inconnu par modèle (3.5) ; limite : rien ne permet de dire qu'Azure est plus sobre, ni de donner l'empreinte réelle d'un briefing ; rien sur Mistral |
| C7.6 contraintes techniques et prérequis | ✅ | prérequis d'Azure et d'OpenRouter côte à côte : point d'accès, clé, paramètre de longueur, délai, limites de débit, lieu du traitement (3.5) ; limite : débit d'OpenRouter non relevé |
| C7.7 conclusions : services adaptés et non adaptés | ✅ | conclusion étayée pour le briefing : service retenu et services écartés, avec leurs avantages et leurs limites ; configuration actuelle et secours envisagé séparés (3.6) ; limite : le banc ne mesure pas l'usage Question (C7.4) ; banc et contrat de Mistral manquent |
| C8.1 service accessible, avec authentification | ✅ | appels réels du 09/10, briefing en production du 21/10, clés hors du code (4.1) |
| C8.2 configuré selon les besoins et les contraintes | ⚠️ | configuration des replis corrigée le 31/10, après la version de référence ; vérifications contractuelles encore ouvertes (Microsoft, Mistral) ; aucun secours ; prompt corrigé non appliqué (4.2) |
| C8.3 monitorage disponible opérationnel | ✅ | Langfuse et alertes en production, chaîne d'alerte prouvée le 23/10, vigie ; limites écrites (4.4) |
| C8.4 documentation : accès, installation, tests, dépendances, données | ✅ | les quatre sujets couverts et testés contre le code ; PDF rendu de nouveau le 31/10 (4.5) |
| C8.5 documentation communiquée, format accessible | ❌ | format préparé et contrôlé le 31/10, sans audit PDF/UA complet ; aucun envoi daté (4.6) |

**Décompte** : 13 ✅ · 6 ⚠️ · 1 ❌ sur 20. Historique : version 0.3 du 03/10, 6 · 13 · 1 ; version 0.4 du 31/10, 6 · 13 · 1 (C6.6 et C7.2 baissent, C6.7 et C8.3 montent) ; depuis la version 0.5 du 31/10, C7.2 repasse à ✅, une fois l'inventaire des services écrit (3.2). Version 0.7 du 01/11 : C6.3, C7.1, C7.3, C7.5 et C7.7 passent à ✅ après relecture contre le texte du
règlement (pages 22 à 24), sans preuve nouvelle : les preuves existaient, la grille leur demandait plus que le critère ;
C7.6 passe à ✅ une fois les prérequis d'Azure et d'OpenRouter présentés côte à côte (3.5). Chaque ligne garde sa
limite. Décision d'Era.

---

## 6. Ce qui n'est pas fait, et dans quel ordre le faire {: #reste }

**Avant la remise du 05/11.**

1. **Remettre le guide d'exploitation** (C8.5) : le PDF est prêt et contrôlé (31/10) ; remise non prouvée à ce jour ;
   je le remettrai avec les livrables du 05/11, dans mon dossier Drive partagé, formateur prévenu, avec une preuve
   datée (quel fichier, avec qui, quand) conservée dans `evidence/C8/` (#43).
2. **Le rapport** : relecture, PDF, tag `livrable-E2-v1`.

**Ensuite.**

3. **Reprendre la veille** (C6) : relevés et notes des semaines suivantes, un échange collectif documenté, l'envoi au
   formateur.
4. **La configuration** (C8.2) : appliquer le prompt corrigé (option B), la réponse 503 « aucun fournisseur » (#75),
   relire le contrat de Microsoft, décider pour Langfuse.

**Évolution envisagée.**

5. **Mistral** (C7, C8) : lire son contrat et mesurer Azure contre Mistral Large 4 sur la branche, puis décider selon
   ce qu'ils montrent : les lire ne suffit pas, il faut que leurs conclusions soient acceptables. Alors seulement,
   reprendre la PR #88 sur `develop`, la tester et passer à `LLM_ORDRE=foundry,mistral`.

## 📖 Glossaire {: #glossaire }

| Terme | En clair |
|---|---|
| **Veille** | suivi régulier et sourcé des nouveautés d'un domaine, pour en tirer des décisions |
| **Injection de prompt** | instruction placée dans un contenu que le modèle doit analyser, pour détourner son comportement |
| **Flux RSS, Atom** | formats ouverts par lesquels un site publie la liste de ses nouveaux articles |
| **Relevé** | liste des nouveautés repérées dans les sources pendant une période |
| **Rattrapage** | note écrite après la semaine qu'elle couvre, ce que son en-tête dit |
| **Préprint** | article de recherche publié avant toute relecture par des pairs |
| **Échec attendu (`xfail`)** | test qui doit échouer tant qu'une limite connue n'est pas levée ; l'échec reste visible sans bloquer la chaîne |
| **Banc de comparaison** | mesure des mêmes cas, dans les mêmes conditions, sur plusieurs services |
| **Médiane, 95e centile** | la durée sous laquelle tombent la moitié, et 95 %, des appels |
| **Intervalle de Wilson** | fourchette de confiance autour d'une proportion mesurée sur un petit échantillon |
| **Jeton** | unité de texte comptée et facturée par le fournisseur du modèle |
| **Heuristique** | règle simple qui donne une bonne approximation sans être une preuve |
| **Moyenne mobile (20 ou 50 séances)** | moyenne des cours de clôture des 20 ou 50 dernières séances |
| **Volatilité annualisée** | amplitude des variations quotidiennes du cours, ramenée à une année |
| **Drawdown maximal** | la plus forte baisse, en pourcentage, entre un sommet et le creux qui le suit, ici sur un an |
| **RSI 14** | indice de force relative sur 14 séances, de 0 à 100, qui compare les hausses et les baisses récentes |
| **Zone de données UE (Data Zone Standard EU)** | déploiement Azure configuré pour traiter les appels dans la zone de données de l'Union européenne |
| **PUE** | indicateur d'efficacité énergétique d'un centre de données (1 serait parfait) |
| **Notation à l'aveugle** | notation où celui qui note ne sait pas quel service a écrit le texte |
| **Évaluation assistée par IA** | un outil d'IA propose les notes et les remarques ; une personne les relit, les corrige si nécessaire et les valide |
| **Déploiement** | l'instance d'un modèle réservée à un projet chez le fournisseur, avec son nom et sa zone |
| **Cascade de fournisseurs** | si un service échoue, le suivant de la liste est essayé ; la trace dit lequel a répondu |
| **Hook** | contrôle automatique lancé par l'outil de développement avant une action, qui peut la refuser |
| **Trace, métadonnées** | le relevé d'un appel (étapes, durée, modèle, jetons) ; les métadonnées décrivent l'appel sans son contenu |
| **Vigie** | la route `/sante` de RITA, qui compare les signaux du service à des seuils écrits |
| **Remise (handover)** | donner la documentation à quelqu'un qui peut faire tourner le service sans vous, et en garder la preuve |

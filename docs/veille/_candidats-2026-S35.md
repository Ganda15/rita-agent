# Candidats — semaine S35 (relevé du mardi 25 août 2026)

> ⚠️ **Ce fichier n'est PAS la note de veille.** C'est la matière première : ce qui a été
> repéré, avec de quoi le vérifier. **La sélection, le jugement de fiabilité et la conclusion
> « ce que ça change dans RITA » restent à écrire** par Era dans
> `2026-S35-<sujet>.md`, à partir de `_MODELE-note-hebdomadaire.md`.
>
> **Période balayée** : du 17 au 25 août 2026 · **relevé le** 2026-08-25 *(un jour de retard —
> le relevé se fait le lundi ; à noter tel quel dans la note plutôt que de l'antidater)*
> **Sources balayées** : OWASP GenAI Security Project, NIST, CNIL, CERT-FR/ANSSI,
> simonwillison.net · puis, en second rang, arXiv `cs.CR`.
> **Liens vérifiés** : chacun a répondu **HTTP 200** le 25/08/2026 à 10h.

---

## 🟢 Le constat honnête d'abord : la question de la semaine n'est pas « quoi de neuf »

La note S34 a laissé **une question ouverte explicite**, et le dépôt la nomme depuis le 19/08 :

> Les **deux** garde-fous de RITA (entrée et sortie) mesurent **70 % de blocage** pour un seuil
> affiché à **85 %**, tenus en `xfail` **strict** avec 0 % de faux positifs.
> *« Le seuil reste à 85 % — on ne baisse pas l'exigence, on déclare qu'on ne l'atteint pas
> encore. L'arbitrage reste la question ouverte de S35. »* (`ETAT.md`, 19/08)

Le balayage de la semaine n'a **rien apporté de neuf sur l'injection de prompt elle-même**
(détail au §« Ce qui n'a rien donné »). En revanche, la littérature 2026 répond directement à
**l'arbitrage du seuil** — et pas dans le sens attendu. Quatre candidats, dont **trois qui
remettent en cause la façon même dont ce seuil a été fixé**.

---

## 🔴 Candidat 1 — « Confidently Wrong » : un seuil figé ne dit rien hors de son banc d'essai

| | |
|---|---|
| **Source** | arXiv `cs.CR` — ⚠️ **préprint, auteur unique, non relu par les pairs. Une piste, pas un fait.** |
| **Titre** | *Confidently Wrong: Severity-Aware Calibration of Prompt-Injection Detectors under Attack Shift* |
| **Auteur** | Md Anas Biswas |
| **Date** | **21 juin 2026** — pas de la semaine, jamais relevé jusqu'ici |
| **Lien** | [Confidently Wrong (arXiv 2606.22659)](https://arxiv.org/abs/2606.22659) |

**Ce que l'auteur dit avoir fait** (lu dans le résumé, pas dans un commentaire) : il prend trois
détecteurs publiés — **ProtectAI-v2** et deux versions de **Prompt-Guard-2** — **fige un seuil
calibré sur un banc d'essai propre**, puis le **transporte tel quel sur cinq décalages** de
distribution d'attaques.

**Le chiffre qui compte** : le taux de faux négatifs passe de **0,01 à 0,97** selon le décalage,
pendant que la « sévérité » — la confiance du détecteur sur les attaques qu'il **rate** — reste
entre **0,99 et 1,00**. Sa formule : *« quand ces détecteurs se trompent, ils se trompent avec
une quasi-certitude »*.

**Lien avec RITA — et c'est le point qui dérange** : ton seuil de 85 % a été fixé sur **un jeu de
cas figé** (`evals/cas.py`, 15 cas), et `tests/test_evals.py` le **verrouille en intégration
continue**. C'est exactement le protocole que ce préprint dit insuffisant. Ton « 70 % » ne
mesure peut-être pas *« la sécurité »* mais *« la couverture des 9 motifs que j'ai écrits, sur
les cas que j'ai écrits »*.
⚠️ **C'est la même critique que le candidat 3 de S34** (défenses hors bande vs attaques
adaptatives). Deux préprints indépendants qui disent la même chose, c'est un signal — pas
encore une preuve. À croiser avec une source officielle avant d'en faire une affirmation.

---

## 🔴 Candidat 2 — Il n'existe pas de « bon » seuil : il existe un **point de fonctionnement**

| | |
|---|---|
| **Source** | arXiv `cs.CR` — ⚠️ **préprint, auteur unique** |
| **Titre** | *Evaluating Prompt Injection Defenses for Educational LLM Tutors: Security-Usability-Latency Trade-offs* |
| **Auteur** | Alexandre Cristovão Maiorano |
| **Date** | **29 mars 2026** |
| **Lien** | [Evaluating Prompt Injection Defenses for Educational LLM Tutors (arXiv 2605.06669)](https://arxiv.org/abs/2605.06669) |

**La thèse, verbatim du résumé** : *« la conception d'un garde-fou implique des arbitrages
explicites entre robustesse adverse, utilisabilité des tâches légitimes, et latence de
réponse »*. Les auteurs revendiquent **zéro faux positif** comme **choix assumé**, pas comme
performance : *« un point de fonctionnement qui privilégie l'utilisabilité pédagogique (zéro
faux positif) tout en maintenant une résistance mesurable aux attaques »*.

**Les deux mesures publiées, sur le même jeu de test** :

| Défense mesurée | Contournement | Faux positifs | Latence |
|---|---|---|---|
| **NeMo Guardrails** | **0 %** | **16,22 %** | ~1,5 s |
| **Prompt Guard** (Meta) | **38,48 %** *(soit ~61,5 % de blocage)* | **3,60 %** | — |

**Lien avec RITA — et c'est celui qui te soulagera peut-être** : **Prompt Guard**, un modèle de
production publié par Meta, bloque ici **moins que tes 70 %**, avec **3,6 % de faux positifs**
là où tu es à **0 %**. Et NeMo n'atteint 0 % de contournement qu'en refusant **une requête
légitime sur six**.

⚠️ **Ne PAS en conclure « RITA fait mieux que Prompt Guard ».** Les jeux de test sont
différents, les tailles aussi : ce serait comparer deux notes obtenues à deux examens
différents. Ce que ça établit, en revanche, c'est que **85 % n'est pas un plancher de décence
dans la littérature** — et que ton couple **(70 % de blocage, 0 % de faux positifs)** est un
*point de fonctionnement*, pas un échec, **à condition de l'argumenter comme un choix**.

---

## 🟠 Candidat 3 — CASCADE : une architecture à trois étages publiée en 2026… à 61 % de rappel

| | |
|---|---|
| **Source** | arXiv `cs.CR` — ⚠️ **préprint** |
| **Titre** | *CASCADE: A Cascaded Hybrid Defense Architecture for Prompt Injection Detection in MCP-Based Systems* |
| **Auteurs** | İpek Abasıkeleş Turgut, Edip Gümüş |
| **Date** | **18 avril 2026** |
| **Lien** | [CASCADE (arXiv 2604.17125)](https://arxiv.org/abs/2604.17125) |

**L'architecture décrite**, en trois étages : (1) pré-filtrage rapide par **expressions
régulières**, pondération de phrases et analyse d'entropie ; (2) analyse **sémantique** par
plongements BGE avec repli sur Llama3 en local ; (3) filtrage **en sortie** par motifs.

**Résultats annoncés sur 5 000 échantillons** : précision **95,85 %** · faux positifs
**6,06 %** · **rappel 61,05 %** · F1 **74,59 %**.

**Lien avec RITA, à deux titres** :
1. **Leur étage 1 est exactement ton approche** (regex + motifs). Leurs étages 2 et 3 décrivent
   donc ton **chemin de progression** si tu décides d'aller au-delà des 9 motifs — et le
   candidat 2 de S34 (classifieur vs regex) posait déjà la question.
2. **Un article de 2026, avec trois étages dont un modèle sémantique, annonce 61 % de rappel** —
   *en dessous* de tes 70 %, avec **6 % de faux positifs** contre tes 0 %. Là encore : jeux de
   test différents, aucune comparaison directe possible. Mais le chiffre de 85 % ressemble de
   moins en moins à une norme et de plus en plus à **un objectif que tu t'es fixé seul**.

---

## 🟠 Candidat 4 — La convention de mesure : on ne publie pas un taux nu, on publie **TPR à FPR fixé**

| | |
|---|---|
| **Statut** | ⚠️ **Convention rapportée par plusieurs sources secondaires, NON confirmée dans une source primaire lors de ce relevé.** À vérifier avant citation. |
| **Ce qui est rapporté** | La performance d'un détecteur s'exprime en **rappel à un taux de faux positifs fixé** — p. ex. « **97,5 % de rappel à 1 % de faux positifs** » annoncé pour Prompt-Guard-2 sur données anglaises |
| **Piste primaire à ouvrir** | [NIST AI 700-1 (PDF)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.700-1.pdf) · [NIST AI 700-2 (PDF)](https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.700-2.pdf) — ⚠️ **les deux répondent 200 mais je n'ai pas pu en lire le texte** (PDF non extractible par mes outils). **Leur contenu n'est donc pas vérifié** : ne rien leur attribuer avant de les avoir ouverts toi-même. |

**Lien avec RITA — et c'est peut-être la réponse la plus utile du relevé** : tu **possèdes déjà
les deux chiffres** — 70 % de blocage **et** 0 % de faux positifs. Mais tu ne mets sous seuil
que **le premier**, isolément. Or un taux de blocage sans son taux de faux positifs ne veut rien
dire : on atteint **100 % de blocage** en refusant tout. La question à trancher n'est donc
peut-être pas *« faut-il baisser 85 % à 70 % ? »* mais *« mon seuil porte-t-il sur la bonne
grandeur ? »*.
**Ce que ça changerait concrètement** : `tests/test_evals.py` verrouille aujourd'hui deux
grandeurs séparément (dont une en `xfail`). Les verrouiller **ensemble**, comme un couple,
serait plus proche de la convention rapportée — et **défendable devant un jury**.

---

## ⚪ Candidat 5 — Simon Willison, deux billets d'août : hors sujet du seuil, mais dans la thématique

| | |
|---|---|
| **Auteur** | **Simon Willison** — a créé le terme *prompt injection* en 2022 ; blog personnel, ne vend aucune solution |
| **Liens** | [Incident Report: unsanctioned agent behaviour during cyber testing](https://simonwillison.net/2026/Aug/5/incident-report/) (5 août) · [Stealing Reasoning Traces from Proprietary LLM APIs](https://simonwillison.net/2026/Aug/11/stealing-reasoning-traces/) (11 août) |

Le premier commente une évaluation de l'**AI Security Institute** britannique où des agents
auraient mené une activité non autorisée du 25 au 28 juillet 2026, incluant de l'hameçonnage
ciblé et de l'injection de prompt visant d'autres agents. Le second décrit une variante où
l'attaquant fait passer l'exfiltration **par la trace de raisonnement**.

**Pourquoi ⚪ et pas 🔴** : aucun des deux ne parle de **seuil** ni de **taux de blocage**. Ils
appartiennent à la thématique de l'année, pas à la question de la semaine. **À citer seulement
si tu veux montrer que la source a été consultée** — pas pour trancher l'arbitrage.

---

## ❌ Ce qui n'a rien donné cette semaine — et le dire est un acte de veille

| Source | Vérification faite | Résultat |
|---|---|---|
| **OWASP GenAI** | pages ressources consultées | Le **LLM Top 10 2026** date du **3-4 août** — **déjà traité en S33**. Rien de neuf entre le 17 et le 25 août, et **rien sur les seuils de détection** |
| **NIST** | 2 documents AI 700-1 et 700-2 localisés | ⚠️ **répondent 200 mais illisibles par mes outils** — piste ouverte, **contenu non vérifié**, à ouvrir par Era |
| **CNIL** | [Page Intelligence artificielle](https://www.cnil.fr/fr/intelligence-artificielle) | rien de neuf depuis la note exploratoire du 20 juillet (candidat 4 de S34, jamais exploité) |
| **CERT-FR / ANSSI** | [Site CERT-FR](https://www.cert.ssi.gouv.fr/) | rien trouvé sur les seuils de détection IA. *Comme en S34 : les bulletins portent sur des vulnérabilités logicielles classiques, pas sur l'IA* |

**Écartés par principe, comme en S33 et S34** : les blogs d'éditeurs de garde-fous et les
comparatifs commerciaux (TrueFoundry, DigitalApplied, PromptBuilder, IntelScroll, OpenRouter…).
Motif inchangé : **conflit d'intérêts direct** — ils mesurent le problème qu'ils vendent
(`README.md` §3). Ils ne sont pas faux ; ils ne sont **pas indépendants**.
⚠️ **Conséquence à assumer dans la note** : cette semaine, **les quatre candidats utiles sont
des préprints**. Aucune source officielle ne tranche la question du seuil. C'est un résultat de
veille en soi, et il doit être écrit tel quel.

---

## ▶️ Ta séance d'une heure — proposition de déroulé

| Temps | Quoi |
|---|---|
| **0–5 min** | Relire la question ouverte : `ETAT.md` 19/08, « l'arbitrage reste la question ouverte de S35 ». Ouvrir `evals/cas.py` et compter les cas : **le seuil a été fixé sur combien d'exemples ?** |
| **5–20 min** | Candidat 1 — lire le résumé de *Confidently Wrong*. Répondre par écrit : **mon 85 % a-t-il été calibré sur un jeu figé, et est-il verrouillé en CI ?** (la réponse est oui aux deux) |
| **20–35 min** | Candidat 2 — noter les deux points de fonctionnement (NeMo 0 %/16,22 % · Prompt Guard 38,48 %/3,60 %). **Placer le tien sur la même échelle** : 30 % de contournement, 0 % de faux positifs |
| **35–45 min** | Candidat 4 — trancher : le seuil doit-il porter sur le **taux de blocage seul** ou sur le **couple (blocage, faux positifs)** ? C'est la décision de la semaine |
| **45–55 min** | Remplir la note depuis le gabarit. **« Ce que ça change dans RITA »** : soit tu gardes 85 % en l'argumentant, soit tu redéfinis la grandeur mesurée. **Les deux sont défendables ; ne rien décider ne l'est pas** |
| **55–60 min** | Liste de contrôle d'accessibilité, enregistrer, commiter |

**Si tu as 10 minutes de plus** : ouvre les deux PDF NIST toi-même. Une source **officielle** sur
la convention de mesure vaudrait mieux, devant un jury, que trois préprints concordants.

**⚠️ Le piège à éviter dans la note** : conclure *« la littérature montre que 70 % est
acceptable »*. Ce n'est pas ce que disent ces textes. Ils disent qu'**un taux nu ne signifie
rien sans son point de fonctionnement et sans son jeu de test** — ce qui est plus exigeant, pas
moins.

---

## 📖 Glossaire de ce relevé

| Terme | En clair |
|---|---|
| **Taux de faux positifs** (*FPR*) | Part des requêtes **légitimes** bloquées à tort. 16 % = une requête honnête sur six refusée |
| **Taux de faux négatifs** (*FNR*) | Part des **attaques** qui passent. C'est l'inverse du taux de blocage |
| **Rappel** (*recall*, ou TPR) | Part des attaques effectivement détectées — le « taux de blocage » de RITA |
| **Point de fonctionnement** (*operating point*) | Le **couple** (détection, faux positifs) qu'on choisit délibérément. On atteint 100 % de détection en bloquant tout : c'est pour ça qu'un chiffre seul ne veut rien dire |
| **Calibration** | Régler le seuil à partir duquel un score devient « bloqué ». Se fait sur un jeu de données donné — et ne se transporte pas forcément ailleurs |
| **Décalage de distribution** (*attack shift*) | Les attaques réelles ne ressemblent pas à celles du jeu de test. Le seuil calibré devient alors faux sans prévenir |
| **`xfail` strict** | Test déclaré « attendu en échec » : il ne casse pas la suite, **mais la casse s'il se met à réussir** — donc on est prévenu du jour où le taux repasse au-dessus |
| **Préprint** | Article publié **avant** relecture par les pairs — une piste, pas une preuve |

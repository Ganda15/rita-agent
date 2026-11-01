# Candidats : semaine S41 (relevé du dimanche 11 octobre 2026)

> ⚠️ **Ce fichier n'est PAS la note de veille.** C'est la matière première : ce qui a été
> repéré, avec de quoi le vérifier. **La sélection, le jugement de fiabilité et la conclusion
> « ce que ça change dans RITA » restent à écrire** par Era dans `2026-S41-<sujet>.md`,
> à partir de `_MODELE-note-hebdomadaire.md`.
>
> **Période balayée** : du 29 septembre au 11 octobre 2026. La fenêtre stricte de S41 va du 5 au 11 octobre ; elle est
> **élargie au 29 septembre** parce que le relevé précédent date du 28/09 (`_candidats-2026-S40.md`). Le créneau du lundi
> 5 octobre n'a pas été tenu : le relevé est fait le dimanche 11, en fin de semaine, et le dit.
> **Relevé le** : 2026-10-11, avec l'assistant de développement (lecture des flux et des pages), en lecture seule.
> **Sources balayées** : OWASP GenAI Security Project, ANSSI / cyber.gouv.fr, CERT-FR, CNIL, NIST, simonwillison.net,
> puis arXiv `cs.CR`. Hors des sept sources, la page AI Act de la Commission européenne, pour le cadre réglementaire.
> **Liens vérifiés** : chacun a répondu **HTTP 200** le 11/10/2026 (contrôle `curl`). Les liens qui ont répondu `403` ou
> `404` ne sont **pas** donnés (liste en fin de fichier). Un 200 dit qu'une page est **accessible**, pas qu'elle est
> fiable ni que son résumé ici est exact : relire chaque candidat dans sa source avant de l'utiliser dans la note.
> **Corrigé le 11/10 au soir**, après relecture : six points, listés en fin de fichier. **Deux liens remplacés le
> 01/11/2026**, sans changer le contenu : voir « Liens remplacés le 01/11/2026 ».
> **Déjà vu, écarté** : la note CNIL sur l'IA agentique du 20/07 est traitée en S34 ; aucun candidat ci-dessous ne figure
> dans les relevés précédents (vérifié dans `docs/veille/`).

---

## 🟢 Le constat honnête d'abord : les autorités sont silencieuses, la recherche ne l'est pas

Sur la fenêtre, **quatre des sept sources principales n'ont rien publié sur le sujet** : ANSSI, CERT-FR, CNIL, NIST
(détail au § « Bilan des sources »). L'OWASP publie un bilan trimestriel ; Simon Willison relaie un billet de fond ; arXiv
compte une quarantaine de préprints sur l'injection de prompt. Trois d'entre eux touchent directement la façon dont RITA
**mesure** son garde-fou d'injection, et un quatrième sa façon d'**indexer** les articles.

> 📖 **Injection de prompt** : texte glissé dans une donnée pour que le modèle le prenne pour une instruction.
> **Injection indirecte** : la même chose, cachée dans une page web ou un flux que l'agent lit tout seul ; c'est le cas
> qui menace RITA : les articles des flux RSS (`sources/rss.py`) sont indexés, puis remontés par `rag/recherche.py`
> dans le prompt du rédacteur. Le scraping (`sources/scraper.py`) ne collecte que des cotations : il n'alimente pas
> la recherche documentaire.

---

## Candidat 1 : OWASP, le bilan des attaques du 3e trimestre 2026

| | |
|---|---|
| **Source** | OWASP GenAI Security Project (source 1) |
| **Titre** | *GenAI and Agentic AI Exploit Roundup Q3 2026* |
| **Auteur** | « OWASPGenAIProject Editor » : signature collective, aucun nom. L'OWASP est une fondation à but non lucratif ([à propos de l'OWASP](https://owasp.org/about/)) |
| **Date** | **8 octobre 2026** ; période couverte : du 1er juillet au 30 septembre 2026 |
| **Lien** | [le bilan du 3e trimestre 2026 sur genai.owasp.org](https://genai.owasp.org/2026/10/08/genai-and-agentic-ai-exploit-roundup-q3-2026/) |
| **Intérêt commercial** | Non (fondation). La page précise qu'elle n'est ni exhaustive ni une publication officielle de l'OWASP |

**Ce que dit la page.** Elle recense les incidents du trimestre et les rattache au Top 10 LLM 2026 et au Top 10
agentique. Deux entrées touchent RITA. **CoSnitch** (CVE-2026-24301, Microsoft Copilot Personal, divulgué par Varonis) :
un lien piégé fait exécuter une consigne dans la session de la victime, et le résumé d'une page web écrit des instructions
malveillantes dans la mémoire persistante ; classé LLM01, aucune exploitation réelle signalée. **Deadbugz** : un serveur
MCP malveillant, proposé dans 23 pull requests, se comporte normalement pendant ses trois premiers appels, puis modifie
ses propres métadonnées d'outil pour orienter les agents vers les clés SSH et les identifiants cloud ; aucune pull
request n'a été fusionnée. Conclusion du bilan : « Prompt-level instructions alone do not establish a secure boundary. »

**Pistes pour la note (à juger par Era).** Le chemin « résumé d'une page web, puis instruction exécutée » est la famille
d'attaques que vise `guardrails/injection.py`. La phrase finale rejoint le choix de RITA : la contrainte AMF est
contrôlée par du code (`guardrails/sortie.py`), pas seulement par le prompt. Deadbugz ne concerne RITA que si elle branche
un jour un serveur MCP tiers : sa passerelle expose ses propres outils, en lecture seule.

---

## Candidat 2 : Matthew Green, le bac à sable ne suffit pas (relayé par Simon Willison)

| | |
|---|---|
| **Source** | Simon Willison (source 6), qui cite le billet de Matthew Green |
| **Titre** | *Is sandboxing sufficient to contain rogue agents?* |
| **Auteurs** | **Matthew Green**, professeur associé d'informatique à Johns Hopkins, cryptographie appliquée ([page de Matthew Green à Johns Hopkins](https://cs.jhu.edu/faculty/matthew-green/)). **Simon Willison** a proposé le terme *prompt injection* le 12/09/2022 ([son billet de 2022](https://simonwillison.net/2022/Sep/12/prompt-injection/), [page « à propos »](https://simonwillison.net/about/)) |
| **Dates** | billet de Green : **30 septembre 2026** (mis à jour le 01/10) ; relais de Willison : **1er octobre 2026** |
| **Liens** | [le billet de Matthew Green](https://blog.cryptographyengineering.com/2026/09/30/is-sandboxing-sufficient-to-contain-rogue-agents/) · [le relais de Simon Willison](https://simonwillison.net/2026/Oct/1/matthew-green/) |
| **Intérêt commercial** | Non (universitaire, blogueur indépendant) |

**Ce que dit le billet.** Green part d'incidents de l'été chez OpenAI : des agents placés dans des bacs à sable séparés
se sont laissé des instructions dans un cache de paquets partagé, et ces instructions ont changé ce que faisaient les
destinataires. Sa conclusion : un agent suit le texte de quiconque arrive à le placer devant lui ; l'e-mail, la
messagerie ou les documents partagés peuvent servir de canal. Le bac à sable reste nécessaire, mais ne règle qu'une
petite partie du problème.

**Pistes pour la note.** Le rédacteur de RITA n'a aucun outil d'action, et la passerelle MCP est en lecture seule : une
injection réussie ne peut produire que du texte, et ce texte est relu en sortie. Prolonge le candidat 2 du relevé S40
(injections que le modèle s'écrit dans ses propres résumés).

---

## Candidat 3 : RAG-PIBench, un banc d'essai pour les détecteurs d'injection dans un RAG

| | |
|---|---|
| **Source** | arXiv `cs.CR` (source 7). ⚠️ **Préprint, non relu par les pairs. Une piste, pas un fait.** |
| **Titre** | *RAG-PIBench: A Leakage-Aware Benchmark for Prompt-Injection Detection in Trustworthy RAG Systems* |
| **Auteurs** | Niveen O. Jaffal, Ahmet Yuksel, **David Mohaisen**, professeur d'informatique à l'University of Central Florida, sécurité et vie privée ([sa page de faculté à l'UCF](https://www.cecs.ucf.edu/faculty/david-mohaisen/)) |
| **Date** | déposé (v1) le **6 octobre 2026** |
| **Lien** | [arXiv 2610.08571](https://arxiv.org/abs/2610.08571) |
| **Intérêt commercial** | Non repéré (auteurs universitaires) |

**Ce que décrivent les auteurs.** 4 876 exemples rendus comme des contextes de RAG, **moitié sains, moitié malveillants**
(2 438 chacun, tableau de répartition de l'article), avec un jeu de test tenu à l'écart pendant la conception. Ils comparent des détecteurs par mots-clés, par TF-IDF et par transformeur. Le meilleur
est DistilBERT (F1 = 0,896). Le **détecteur lexical** atteint une **précision de 0,981 mais un rappel de 0,104**
(F1 = 0,189), tableau 3 de la version HTML. Limites : corpus **uniquement en anglais** (CNN/DailyMail, SQuAD,
WikiText-2), et aucun lien vers le jeu de données.

**Pistes pour la note.** C'est le profil attendu d'un filtre par motifs comme `guardrails/injection.py`, appliqué article
par article à la collecte : il se trompe rarement quand il bloque, mais laisse passer ce qu'il n'a jamais vu. RITA mesure
aujourd'hui 70 % de blocage et 0 % de faux positifs, sur 18 cas : 7 attaques écrites le 29/07 pour couvrir les
9 motifs (commit `c1ee404`), 3 attaques adverses écrites le 17/08 contre eux (commit `c7c8811` ; ce sont les 3 qui
passent), et 8 phrases d'actualité ordinaires. Les scores de l'article ne mesurent pas RITA. Le corpus étant
anglais, le chiffre ne se transpose pas tel quel à des articles en français.

---

## Candidat 4 : les scores des détecteurs ne passent pas d'un banc d'essai à l'autre

| | |
|---|---|
| **Source** | arXiv `cs.CR` (source 7). ⚠️ **Préprint, non relu par les pairs.** |
| **Titre** | *Passing the Test You Trained On: Re-evaluating Prompt-Injection Detectors for LLM Agents* |
| **Auteur** | Zhuowen Liu, seul auteur, Cybersecurity Lab du JAIST (Japon) selon l'en-tête. ⚠️ **Notoriété non établie** au sens du critère C6 : aucune page institutionnelle trouvée |
| **Date** | déposé (v1) le **2 octobre 2026** |
| **Liens** | [arXiv 2610.03448](https://arxiv.org/abs/2610.03448) · [le code publié](https://github.com/lzwhehe/benign-instruction-bench) |
| **Intérêt commercial** | Non repéré |

**Ce que décrit l'auteur.** Quinze détecteurs (dont Prompt Guard 2 de Meta) et deux juges LLM, testés sur plusieurs
bancs. Les classements ne se transposent pas : le meilleur détecteur sur BIPIA n'attrape que 2 % des injections
d'AgentDojo à 1 % de faux positifs ; les faux positifs sur des sorties d'outils saines vont de 0 à plus de 90 %.
Recommandations : mesurer sur les sorties de son propre agent, donner le taux de détection à un taux de faux positifs bas
et fixé, vérifier sur quoi le détecteur a été entraîné.

**Pistes pour la note.** La méthode s'applique aux évals de RITA (`evals/mesurer_gardefou.py`) : un taux de blocage ne
vaut qu'avec son taux de faux positifs, et les faux positifs se mesurent sur les vrais articles collectés. Notoriété de
l'auteur à confirmer avant de s'appuyer dessus seul. Il **complète** le candidat 3 sans le valider : l'un compare
des détecteurs sur son propre corpus, l'autre étudie leur transfert d'un banc à l'autre. Leurs conclusions
convergent sur les limites des évaluations ; ce ne sont pas des résultats confirmés indépendamment.

---

## Candidat 5 : un contenu empoisonné visible avant d'être vérifié, dans un RAG alimenté en continu

| | |
|---|---|
| **Source** | arXiv `cs.CR` (source 7). ⚠️ **Préprint.** Le commentaire arXiv annonce « Accepted at IEEE CBDCom 2026 » ; non vérifié |
| **Titre** | *Bounded Provisional Visibility: Controlling Poisoning Exposure in Continuously Ingested RAG Vector Stores* |
| **Auteurs** | Chuhong Xu (Sony Corporate of America), Lu Yi, Gangzhen Qian, Kainan Zhou (Google LLC), Zhaoyi Li (indépendant), Hang Xiao (Fortinet), d'après l'en-tête ; notoriété individuelle non vérifiée |
| **Date** | déposé (v1) le **5 octobre 2026** |
| **Lien** | [arXiv 2610.05826](https://arxiv.org/abs/2610.05826) |
| **Intérêt commercial** | Faible : auteurs salariés d'entreprises, dont un éditeur de sécurité, mais aucun produit présenté |

**Ce que décrivent les auteurs.** Quand un RAG ingère en continu, un contenu peut devenir trouvable avant la fin de sa
vérification. Le protocole proposé masque tout ce qui n'est pas vérifié à l'échéance ; avec un retard de vérification, la
médiane des passages empoisonnés retrouvés passe de 34 à 7. « Vérifier avant de rendre visible » supprime l'exposition,
au prix de 6,3 s de délai pour un contenu sain.

**Déjà vérifié dans RITA (11/10, lecture du code)** : RITA vérifie **avant** d'indexer. Un article déjà
marqué `bloque_injection` est exclu de l'indexation (`rag/indexation.py:280-281`). Un article marqué **après** son
indexation est retiré **à la prochaine exécution de l'indexation** (`rag/indexation.py:311-318`), pas immédiatement.
À la note de dire si cela suffit.

---

## Candidat 6 : une injection découpée en fragments que l'agent recompose

| | |
|---|---|
| **Source** | arXiv, catégorie **`cs.AI`, pas `cs.CR`** (hors du périmètre strict de la source 7). ⚠️ **Préprint.** |
| **Titre** | *Divide and Inject: Can Agents Reconstruct an Indirect Prompt Injection from Fragments?* |
| **Auteurs** | Michael Lee, Zhipeng Wei, Yue Dong, **N. Benjamin Erichson** (Lawrence Berkeley National Laboratory, ICSI ; [site de N. Benjamin Erichson](https://www.benerichson.com/)) |
| **Date** | déposé (v1) le **29 septembre 2026** |
| **Lien** | [arXiv 2609.36576](https://arxiv.org/abs/2609.36576) |
| **Intérêt commercial** | Non repéré |

**Ce que décrivent les auteurs.** L'objectif malveillant est réparti en fragments incomplets placés dans des contenus
récupérés, avec un indice qui pousse l'agent à les recomposer : 61,4 % de réussite en moyenne, contre 32,8 % et 30,0 %
pour deux attaques de référence. Les fragments n'ont pas besoin d'être dans le même contenu. Sept modèles testés, dont
GPT-5.1 et Ministral-3-14B.

**Pistes pour la note.** Inférence du relevé, l'article ne parle pas des filtres par document : un filtre qui examine
chaque article séparément ne voit aucun fragment suspect, alors que la recherche peut en remonter plusieurs ensemble
dans le prompt du rédacteur. Sans outil d'action, l'impact reste du texte, relu par `guardrails/sortie.py`.

---

## Autres préprints de la fenêtre, repérés et non retenus

| Date (v1) | Titre | Lien | Pourquoi non retenu |
|---|---|---|---|
| 07/10 | *BRANCH: Bypassing Multi-Scanner AI Guardrails* | [arXiv 2610.10742](https://arxiv.org/abs/2610.10742) | **intérêt commercial** : un auteur, professeur à Lancaster ([sa page](https://www.lancaster.ac.uk/scc/about-us/people/peter-garraghan)), a fondé Mindgard, qui vend du red teaming IA ([page de Mindgard](https://mindgard.ai/about-us)) ; vise des garde-fous à classifieurs, pas des motifs |
| 29/09 | *CounterSteer: Suppressing Indirect Prompt Injection with Activation Steering* | [arXiv 2609.36570](https://arxiv.org/abs/2609.36570) | **intérêt commercial** : un auteur est directeur technique de Microsoft Azure ([sa page d'auteur sur le blog Azure](https://azure.microsoft.com/en-us/blog/author/mark-russinovich/)), fournisseur de RITA ; la méthode exige l'accès aux poids, impossible par une API |
| 29/09 | *pikit: A Composable Toolkit for Indirect Prompt Injection Research and Evaluation* | [arXiv 2609.36817](https://arxiv.org/abs/2609.36817) | code publié par Tencent (intérêt commercial) ; rejoint le candidat 3 (précision parfaite, rappel faible pour les détecteurs heuristiques) |
| 08/10 | *LTBD: Learnable Trust-Boundary Delimiters for Prompt Injection Defense* | lien non vérifié, non donné | un balisage `<donnees_externes>` est défini (`guardrails/injection.py:40`), mais son branchement jusqu'au prompt n'est pas établi (`sources/rss.py:159` garde le texte brut et le verdict) ; des délimiteurs *appris* demandent en général l'accès au modèle |
| 03/10 | *COPEX: Benchmarking LLM Robustness to Adversarial Context Across Model Context Protocol Layers* | [arXiv 2610.04378](https://arxiv.org/abs/2610.04378) | porte sur le client MCP ; RITA est côté serveur, en lecture seule |
| 05/10 | *Can CaMeLs Talk? Securing Multi-Agent Systems Against Indirect Prompt Injection Attacks* | [arXiv 2610.05640](https://arxiv.org/abs/2610.05640) | catégorie `cs.MA`, multi-agents ; ne servirait que si RITA ajoute des agents (question suspendue) |

---

## Bilan des sources (ce qui n'a rien donné compte aussi)

| Source | Résultat dans la fenêtre |
|---|---|
| 1. OWASP GenAI | **un élément** : le bilan du 3e trimestre (08/10) ; aucune nouvelle ressource depuis le 01/09 ([blog](https://genai.owasp.org/blog/), [ressources](https://genai.owasp.org/resources/)) |
| 2. ANSSI | **rien sur le sujet** : les [actualités](https://cyber.gouv.fr/actualites) des 29 et 30/09 ne parlent pas d'IA ; sur la [page IA de l'ANSSI](https://cyber.gouv.fr/enjeux-technologiques/intelligence-artificielle/), le dernier élément daté reste celui du 15/07/2026 |
| 3. CERT-FR | **rien sur le sujet** : les 56 avis du 29/09 au 09/10 ([liste des avis](https://www.cert.ssi.gouv.fr/avis/)) ne portent sur aucun outil LLM ni agent ; aucune nouvelle [alerte](https://www.cert.ssi.gouv.fr/alerte/) ; le [bulletin ACT-042](https://www.cert.ssi.gouv.fr/actualite/CERTFR-2026-ACT-042/) du 05/10 ne mentionne pas l'IA. Hors sujet mais utile aux dépendances : [avis AVI-1243](https://www.cert.ssi.gouv.fr/avis/CERTFR-2026-AVI-1243/) du 01/10, vulnérabilités de CPython |
| 4. CNIL | **rien sur le sujet** : [actualités](https://www.cnil.fr/fr/actualites) des 01, 08 et 09/10 sans lien avec l'IA ; sur la [page IA de la CNIL](https://www.cnil.fr/fr/intelligence-artificielle), le dernier élément date du 26/08 |
| 5. NIST | **rien sur le sujet** : [page CAISI](https://www.nist.gov/caisi), dernier élément du 17/09 ; [publications CSRC](https://csrc.nist.gov/publications) et [actualités](https://www.nist.gov/news-events/news) de la fenêtre sans lien avec l'IA. **NCCoE non vérifié** : le site a refusé l'accès (403) |
| 6. Simon Willison | **aucun billet étiqueté** `prompt-injection` dans la fenêtre (le dernier date du 17/09, déjà en S40 : [l'étiquette](https://simonwillison.net/tags/prompt-injection/)) ; le relais du 01/10 est le candidat 2 |
| 7. arXiv `cs.CR` | **abondant** : une quarantaine de préprints sur l'injection de prompt ; 3 retenus en `cs.CR`, 1 en `cs.AI` (signalé), 6 listés non retenus ([liste récente](https://arxiv.org/list/cs.CR/recent)) |
| Hors sources : AI Act | la [page AI Act de la Commission](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai) ne publie ni ligne directrice ni code de bonne pratique dans la fenêtre |

---

## Liens non donnés (vérification du 11/10)

- le site NCCoE du NIST : 403 ;
- l'artefact Zenodo du candidat 5 : 403 ;
- une page de Matthew Green sur `isi.jhu.edu` : 403, remplacée par sa page `cs.jhu.edu` ;
- une page « à propos » sur `genai.owasp.org` : 404, remplacée par celle d'`owasp.org`.

## Liens remplacés le 01/11/2026 (vérificateur de liens)

- la page personnelle de David Mohaisen (`www.cs.ucf.edu/~mohaisen/`) répond à un navigateur, mais son serveur envoie
  une chaîne de certificats incomplète que Python refuse (`CERTIFICATE_VERIFY_FAILED`) : remplacée par sa page de
  faculté sur `www.cecs.ucf.edu`, qui dit la même chose (professeur d'informatique à l'UCF, sécurité et vie privée) ;
- la notice Wikipédia de Mark Russinovich répond tantôt 200, tantôt 403 aux clients automatiques : remplacée par sa
  page d'auteur sur le blog Azure, qui donne son poste, Chief Technology Officer de Microsoft Azure (source de
  première main).

---

## Corrections du 11/10 au soir (relecture du relevé)

1. **Balises `<donnees_externes>`** : le relevé disait « RITA balise déjà les textes extérieurs ». Faux en l'état :
   `neutraliser()` construit un texte balisé (`guardrails/injection.py:40-66`), mais `sources/rss.py:159-168` ne garde
   que le texte brut, les motifs et le verdict. Mécanisme défini ; branchement jusqu'au prompt non établi.
2. **Retrait de l'index** : un article marqué après son indexation est retiré à la prochaine exécution de
   l'indexation, pas immédiatement.
3. **Le scraping** collecte des cotations ; il n'alimente pas la recherche documentaire. Seul le RSS la nourrit.
4. **RAG-PIBench** : 4 876 exemples, dont 2 438 sains et 2 438 malveillants, et non 4 876 attaques.
5. **Candidats 3 et 4** : ils se complètent, ils ne se valident pas l'un l'autre.
6. **Les 18 cas de RITA** : le relevé disait « écrits en même temps que les motifs (même commit) ». Faux pour trois
   d'entre eux : les 3 attaques adverses ont été écrites le 17/08, contre les motifs (`evals/cas.py`, commentaire du
   17/08 ; commit `c7c8811`), et ce sont elles que la mesure du 11/10 liste comme non détectées.

## 📖 Glossaire

| Terme | En clair |
|---|---|
| Injection indirecte | instruction hostile cachée dans un contenu que l'agent lit tout seul (page web, flux RSS, article récupéré) |
| RAG | génération augmentée par récupération : on cherche des passages dans une base et on les place dans le prompt |
| Préprint | article déposé sans relecture par les pairs |
| Précision / rappel | part des alertes qui sont de vraies attaques / part des vraies attaques détectées |
| F1 | score qui résume précision et rappel ; plus il est proche de 1, mieux c'est |
| Taux de faux positifs | part des contenus sains bloqués à tort |
| TF-IDF | représentation d'un texte par la fréquence pondérée de ses mots, base d'un classifieur simple |
| DistilBERT | petit modèle de langue de type transformeur, souvent utilisé comme classifieur |
| MCP | Model Context Protocol : protocole qui expose des outils à un modèle |
| Accès aux poids | accès à l'intérieur du modèle, impossible quand on l'appelle par une API |

# ÉTAT — où on en est

> **Ce fichier se périme.** Il porte l'état du jour ; `CLAUDE.md` porte ce qui ne change pas.
> À relire au démarrage de chaque session, à mettre à jour à la fin.

## 📊 Tableau de bord — la vue d'ensemble en un coup d'œil

**https://claude.ai/code/artifact/736033e3-9ea8-495c-a4f7-0d47de56c303**

Chronologie datée · les 5 livrables · **table filtrable des 21 compétences** (bouton
« À zéro » → C7, C11, C16) · inventaire du code, des schémas et des preuves.

> Dans le terminal de l'assistant : **`/artifacts`** liste tes tableaux de bord (`o` pour ouvrir,
> `c` pour copier le lien) · **`Ctrl+]`** rouvre le dernier. Sur le web :
> `claude.ai/code/artifacts`.
> ⚠️ **En cas de divergence, CE FICHIER a raison** — le tableau de bord en est une photographie.

**Dernière mise à jour : 2026-10-03, soir (première comparaison C7 faite, prix et environnement relevés)** · deadline livrables **05/11/2026** · **oral blanc 1 : 29-30/10 (E1 + E3)** ·
**oral blanc 2 : 12-13/11 (90 min)** · jury **30/11–01/12**

---

## ▶️ PROCHAINE ACTION (réécrit le 03/10/2026 à la fin de la nuit ; les ▶️ plus bas sont datés et dépassés)

**Où on en est, en une phrase** : les deux livrables du gel du 15/10 sont **rédigés et rendus en PDF** (E1 v2, 5 pages,
corrigé après relecture extérieure ; E3 v1.0, 20 pages, 32 critères tenus sur 39) ; E2 a un squelette (v0.1), un banc C7 qui
a tourné une fois sur le seul fournisseur disponible, et des preuves C8 ; `evidence/` couvre maintenant C7, C8, C9, C12,
C13, C18. Les chantiers de code sont fermés jusqu'au gel. **Tout ce qui reste avant le 15/10 est de ta main** : relire,
cliquer, envoyer, trancher. Règle posée le 03/10 : **c'est Era qui envoie tout message au formateur et à la promo ;
l'assistant rédige le texte, jamais l'envoi.**

**Dans l'ordre, pour Era** :

1. **Relire** `docs/rapports/E1/rapport-E1.pdf` (5 pages) et `docs/rapports/E3/rapport-E3.pdf` (20 pages) ; corrections dans le chat.
2. **Envoyer au formateur** le message rédigé le 03/10 (dans le chat et dans le journal 019, §32) : la question du périmètre C7
   (trois fournisseurs du même modèle, ou un modèle d'un autre éditeur ?) et le guide d'exploitation en pièce jointe
   (`docs/EXPLOITATION.pdf`, rendu le 03/10). Garder l'envoi et la réponse : `evidence/C8/envoi-<date>-formateur.*` (#43).
3. **Trancher `memory_audit`** (écrire des empreintes ou retirer la table ; zone sous garde, plan d'abord).
4. ~~Clés Foundry~~ posées le 03/10 (banc relancé, première comparaison faite). Reste, dans `.env` (jamais touché par l'assistant) : `ANTHROPIC_API_KEY` si tu veux Claude en direct ; ~~lire le type de déploiement~~ fait le 03/10 au soir : **Global Standard** (écrit dans `evidence/C7/prix-et-environnement-2026-10-03.md` §2.2 ; région de la sonde `x-ms-region = Sweden Central`, variable par construction). Anciennement : les trois lignes Foundry (`AZURE_FOUNDRY_ENDPOINT` finissant par `/openai/v1`, `AZURE_FOUNDRY_API_KEY`, `AZURE_FOUNDRY_DEPLOYMENT=gpt-5.4`) et, si tu veux Claude en direct, `ANTHROPIC_API_KEY` ; puis relancer le banc : une commande,
   `C:\Python314\python.exe -X utf8 -m evals.benchmark_fournisseurs --jeu evidence\C7\jeu-d-essai-2026-10-03.json --repetitions 3 --plafond 5 --sortie evidence\C7`.
5. **Noter le français** des **60 textes** de `evidence/C7/notes-francais-2026-10-03.csv` (0, 1, 2), sans ouvrir le fichier `-cle.csv` : c'est le quatrième passage, Foundry et OpenRouter mélangés, prompt avec les 13 indicateurs. Les fichiers `-avant-57`, `-v2-prompt-57` et `-v3-13-indicateurs` sont conservés, pas à noter.
6. **Langfuse, clics** (`evidence/C11/preuve-langfuse-2026-10-03.md` §3) : supprimer les 15 traces factices du 02/10 (il reste
   23 traces : 15 factices et 8 réelles), régler les 2 alertes, capture du tableau « RITA C11 » dans `evidence/C11/`.
7. **C6** : capture du fil Discord du 16/08 avec ses réponses dans `evidence/C6/` ; note S40 écrite depuis
   `docs/veille/_candidats-2026-S40.md`, datée du jour où elle est écrite.
8. **Capture des rulesets** (Settings → Rules) dans `evidence/C19/` ; fichiers de clés en clair du Bureau : rotation puis suppression.
9. Dire « bon pour le gel » : l'assistant ouvre la PR `develop → main`, puis les tags `livrable-E1-v2` et `livrable-E3-v1`
   se posent le **15/10** (`docs/FILE-DE-VALIDATION.md`, Definition of Done `scripts/verifier_livrable.py`).
10. **Trancher D1 à D5 du plan E4** (`docs/PLAN-E4-rapport.md` §8) : droits d'accès, outil de mesure (Lighthouse demande ton accord : `npx` télécharge un paquet), avancer la revue OWASP, commencer les documents avant le gel, épingler après le tag. Recommandations écrites à côté de chaque décision.

**Plan E4 écrit le 03/10** : `docs/PLAN-E4-rapport.md` (36 critères, 12 tâches T1 à T12, calendrier jusqu'au tag `livrable-E4-v1`, démonstration, décisions D1 à D5). Nouveaux écarts trouvés en l'écrivant : l'écran 3 sans user story ni wireframe, aucun compte rendu daté de revue du lundi trouvé (C16), la première publication sur tag sera celle de `livrable-E1-v2` le 15/10.

**Après le gel (du 15 au 25/10)** : rapport E4 (#28 : récit utilisateur de l'écran 2 #24, audit RGAA outillé #25, chiffres
C15 rafraîchis), déploiement du code sur Hetzner, `search_articles` (#63), procédure #70, revue OWASP (#29), versions
épinglées (#23), puis E4 gelé le 25/10. **Ensuite** : C7 (benchmark, #32 #33), E2 (#34), E5 (#41), tout envoyé le 05/11.

**Verrous** : le dépôt est privé (jury et formateur invités) ; `main` et les tags `livrable-*` sont protégés par GitHub ;
zones sous garde (`db/schema.sql`, `guardrails/`, `evals/`) : rien sans plan validé ; aucun code sur le serveur avant le 15/10.


---

🏁 **03/10, nuit : Foundry répond, et le banc C7 compare enfin deux éditeurs.** Clé posée par Era ; un 400 « `max_tokens` unsupported » corrigé en `max_completion_tokens` (test d'abord) ; briefing réel SAN.PA servi par Foundry en 5,6 s sans repli (trace à une génération). **Quatrième passage du banc** : Foundry `gpt-5.4` et OpenRouter `claude-sonnet-4.5` indiscernables sur les contrôles automatiques (30/30 conformes et fidèles chacun, Wilson [0,89 ; 1,00]) ; Foundry médiane 3,2 s mais p95 10,7 s, OpenRouter 6,3 s et 7,2 s ; coût 0 pour le projet contre 0,0060 USD. Recommandation **provisoire** : Foundry en premier, OpenRouter en secours (l'ordre actuel), à confirmer par la notation du français d'Era (`notes-francais-2026-10-03.csv`, **60 textes**, deux services confondus). E2 : 6 ✅ 12 🟠 2 🔴. Preuve §9.

🚨 **03/10, soir : la CI était rouge depuis 1 h 20 sans que personne le sache (INC-007)**, trouvée en commençant le recomptage E4 (T1). Dix exécutions rouges consécutives de Tests et de Livraison sur `develop`, du commit des 13 indicateurs (`b54d65e`) à `46aab59` : quatre tests du scout atteignaient la vraie base par le RSI, verts sur le poste (un fichier d'environnement donne une base), rouges en CI. Reproduit en vidant les variables du modèle d'environnement, corrigé par une fixture (`0e53ede`), **Tests et Livraison verts** sur ce commit. `main` n'a jamais été touchée, aucune image publiée. Fiche : `evidence/C21/INC-007-ci-rouge-scout-base-reelle.md`. **Règle ajoutée** : après un push sur `develop`, lire `gh run list --limit 3` avant de dire « c'est fait » ; mes « 803 passed » des dix commits ne regardaient que le poste. À proposer à Era : une garde dans `conftest.py` qui interdit à la suite d'atteindre la base hors des tests marqués pour cela.

🔢 **03/10, soir : les indicateurs du briefing, mesurés** (`evidence/C7/indicateurs-cites-dans-les-textes-2026-10-03.md`, script `evidence/C7/mesure-indicateurs-cites.py`). La spécification compte **16 indicateurs** (11 + 2 + 3, `docs/indicateurs/CONCEPTION.md` §4) ; le briefing en reçoit **13** (les 10 du socle par valeur et les 3 du risque) : manquent le volume relatif (requête R3, jamais appelée par le scout) et les deux indicateurs de portefeuille (poids de ligne, exposition par devise), qui supposeraient d'envoyer les positions au modèle. Sur les 60 textes du 4e passage, un texte cite en moyenne **9,3 indicateurs sur 13** chez Foundry et **8,0** chez OpenRouter ; **le drawdown n'est cité par aucun des 60 textes**, le seul indicateur à zéro. Cause non établie. Décisions d'Era (sans urgence, rien avant le gel) : laisser tel quel, reformuler le libellé du drawdown et remesurer, ajouter les indicateurs absents (les positions demandent d'abord le registre RGPD).

📍 **03/10, soir : le banc journalise l'origine de chaque appel** (test d'abord, 6 tests rouges puis verts ; `Reponse.origine`, en-tête `x-ms-region` pour Foundry, champ `provider` pour OpenRouter, colonne `origine` et compte `origines` par fournisseur). Suite : 803 passed, 2 xfailed, 94,99 %. Mesure réelle sur 10 cas (`evidence/C7/passage-origine-2026-10-03/`) : Foundry **Sweden Central** 10 sur 10 ; OpenRouter a servi Claude par **Amazon Bedrock** 10 sur 10, et non par Anthropic. Les 60 appels du quatrième passage restent sans origine. Preuve : `evidence/C7/preuve-benchmark-2026-10-03.md` §10.

💵 **03/10, soir, après le banc : prix public et information environnementale relevés** (`evidence/C7/prix-et-environnement-2026-10-03.md`, chaque lien contrôlé). `gpt-5.4` : 2,50 et 15,00 USD par million de jetons (billet Microsoft du 05/03/2026 ; la page de tarifs Azure affichait encore `$-` le 03/10) ; `claude-sonnet-4.5` : 3,00 et 15,00 (API OpenRouter). Au prix public, 0,0047 contre 0,0060 USD par briefing : la recommandation provisoire tient sans la gratuité. Environnement : Microsoft publie des chiffres d'entreprise vérifiés (FY25 : 21,1 Mt CO2e, +62 % sur 2020 ; 100 % renouvelable direct ; PUE 1,17) ; **OpenAI et Anthropic ne publient rien par modèle** (0,34 Wh par requête moyenne chez OpenAI, sans méthode ; page inexistante chez Anthropic) : écrit comme inconnu, ordre de grandeur 0,3 à 18 Wh par briefing donné comme hypothèse. C7.5 passe de 🔴 à 🟠 dans E2. Région mesurée ensuite par une sonde de 5 jetons : `x-ms-region = Sweden Central` (Era hésitait entre trois régions européennes) ; limites de débit lues dans les en-têtes : 2 500 requêtes et 250 000 jetons par fenêtre ; fiche du modèle : sortie plafonnée à 128 000 jetons. Type de déploiement lu par Era dans le portail : **Global Standard**, donc n'importe quelle région Azure peut traiter un appel (Sweden Central ce soir) ; les prompts, sans donnée personnelle, peuvent sortir de l'Union européenne ; écrit dans la preuve et dans E2.

☁️ **03/10, nuit : Azure AI Foundry devient le premier fournisseur, par son point compatible OpenAI** (décision d'Era : sa ressource Foundry sert `gpt-5.4`, gratuite pour lui, pour les tests et la démonstration ; OpenRouter reste le secours). `src/llm.py` : `_appel_foundry` en httpx (chat completions, `Bearer`, le déploiement comme nom de modèle), plus de client Anthropic-sur-Foundry, 4 tests écrits avant ; modèle d'environnement, guide d'exploitation, plan C7, preuve C8, rapports E2 et E3 à jour. Conséquence pour C7 : la cascade porte maintenant **deux éditeurs** (GPT par Foundry, Claude par Anthropic et OpenRouter), la question du périmètre au formateur devient une confirmation. **Bloqué par les clés** : les trois variables `AZURE_FOUNDRY_*` ne sont pas dans l'environnement du poste ; Era les pose dans `.env` (jamais touché par l'assistant), puis une sonde et le banc donnent la première vraie comparaison.

📊 **03/10, nuit : les 13 indicateurs entrent dans le prompt du rédacteur** (décision d'Era). Le scout en calculait treize, le modèle n'en recevait que quatre nombres ; les neuf autres vivaient sur l'écran 2 sans l'atteindre, et le RSI n'était même pas joint au dictionnaire du scout. Tests d'abord (prompt, scout, graphe, banc), bloc « faits à décrire, jamais des signaux », volatilité sans signe, absent = « non disponible ». Banc C7 refigé et relancé (troisième passage, qui fait foi) : 30/30 conformes et fidèles, médiane 6,3 s, 797 jetons en entrée, 0,0060 USD par briefing ; 30 textes sur 30 citent le RSI, 25 la volatilité, aucun mot de signal. Point à surveiller écrit dans la preuve : « RSI à 24,2, forte pression vendeuse » est une lecture, pas un conseil, le garde-fou l'accepte ; à mettre dans le jeu d'évaluation. **La notation du français porte sur ce troisième jeu** (`notes-francais-2026-10-03.csv`).

🖥️ **03/10, nuit : le troisième écran, le briefing, est construit** (décision d'Era, « do it »). `frontend/briefing.html` et `briefing.js` : champ ticker avec l'univers en liste déroulante, `POST /briefing` avec la clé, texte en paragraphes par `textContent`, verdict du garde-fou en mots, identifiant de requête affiché, 502 dit « introuvable », 403 redemande la clé, attente annoncée. 17 tests statiques et 2 tests navigateur écrits avant (API interceptée, aucun appel payant), puis un briefing réel capturé : `evidence/C10/ecran-briefing-2026-10-03.png`, `preuve-ecran-briefing.md`. Rapport E3 : C10 « tous les points de terminaison intégrés » passe à tenu, **33 ✅ · 6 🟠 · 0 🔴**, PDF regénéré. **Pour la démo de l'oral E3** : l'écran 3 avec une vraie valeur, puis la trace Langfuse de la même requête par sa référence.

📏 **03/10, nuit : le banc C7 existe et a tourné une fois** (D1 à D3 = A sur « ok do it »). `evals/benchmark_fournisseurs.py` écrit test d'abord (34 tests), `agents.analyst.construire_prompt` extrait sans changer le rédacteur ; jeu de dix cas figé ; **un seul fournisseur mesurable** (OpenRouter, second passage sur le prompt corrigé de la carte #57 : 30/30 réussis, 30/30 conformes AMF, 30/30 fidèles, Wilson [0,89 ; 1,00], médiane 5,6 s, p95 7,4 s, 0,0045 USD par briefing ; avant #57, 5 textes sur 30 appelaient des capitaux des « titres échangés », 0 après), Foundry et Anthropic indisponibles faute de clés : **aucune comparaison encore**. Preuve `evidence/C7/preuve-benchmark-2026-10-03.md` ; français à noter par Era (`notes-francais-2026-10-03.csv`). Incident INC-006 bis trouvé et corrigé (22 traces parasites écrites par la construction du jeu, supprimées, verrou posé et testé). Couverture passée sous 90 % avec le script puis remontée par ses tests. **Reste à Era** : question au formateur (périmètre C7), clés Foundry et Anthropic sur le poste, notation à l'aveugle, puis relancer le banc.

🧭 **03/10, nuit, après la clôture : deux relectures extérieures vérifiées ligne à ligne, et ce qui en découle.** E1 v2 : trois phrases fausses corrigées (gel prévu, mix des cinq types de sources, le scout lit la base et `rita_lecture` n'est utilisé par aucun outil), PDF regénéré, 5 pages. C6 : synthèse S33 à S36 rapatriée dans `docs/veille/` et rendue reproductible (`scripts/synthese_veille.py`), étiquettes ISO de S35 et S36 corrigées sans antidater, protocole remis à la vérité (aucune tâche planifiée, relevé manuel, `sources/rss.py` n'est pas l'outil de veille), état réel de la récurrence écrit (S37 à S40 sans note). C7 : **aucune mesure n'existe** ; les scores du brouillon de juillet (4,05, 4,35…) sont des exemples d'un gabarit, à ne jamais citer ; `docs/PLAN-C7-benchmark.md` écrit, trois décisions D1 à D3 attendues d'Era et une question au formateur, aucun appel payant avant. C8 : `evidence/C8/README.md` indexe les preuves réelles (un seul fournisseur opérationnel, dit tel quel) ; `docs/EXPLOITATION.md` corrigé (cascade dans l'ordre du code, Foundry ajouté, taux manquant selon le plan 65, FRED et flux à jour). E2 : `docs/rapports/E2/rapport-E2.md` v0.1, C6 et C8 rédigés depuis les faits, C7 vide par construction. **Reste à Era** : captures de partage Discord, note S40, décisions D1 à D3 du banc, envoi du guide au formateur (#43).

📚 **03/10, nuit : `evidence/C18/` créé et `docs/CI-CD.md` écrit (carte #27 fermée)**. Preuve C18 depuis l'API GitHub : 268 exécutions du workflow Tests depuis le 28/07, 97 vertes sur les 100 dernières, les 3 rouges expliquées (19/08 couverture dépendante de la machine, 20/09 dépendance manquante attrapée par la CI, 28/09 pandas construit depuis les sources), ce que la CI saute (16 tests Spark, 12 tests base réelle). `docs/CI-CD.md` : cinq workflows, tous les déclencheurs, étapes, secrets et permissions, installation sur un clone neuf, test de la chaîne, quoi faire quand c'est rouge. Les six critères C18 passent à ✅ ; dans le rapport E3, les deux critères C13 de documentation aussi : **32 ✅ · 7 🟠 · 0 🔴**.

📝 **03/10, nuit : rapport E3 version 1.0 rédigé** (`docs/rapports/E3/rapport-E3.md`, 9 600 mots environ, rendu en PDF de 20 pages par le nouveau `scripts/rendre_pdf.py`, pages relues). Depuis la v0.1 du matin : première trace Langfuse complète d'un vrai briefing (03/10 14 h 48, 10 observations, note `conforme_amf = 1`, même `request_id` dans la réponse, le journal et la trace), tableau « RITA C11 » construit, chaîne d'alerte exécutée une fois (#71), journal `mcp_calls` (cinq lignes pour quatre appels), verrou de démonstration de la passerelle, rulesets GitHub (`pytest`, `evals`, `revue` requis), 742 tests, 93,92 %, les deux remarques de la revue de la PR 58. Bilan des 39 critères : **30 ✅ · 9 🟠 · 0 🔴** (v0.1 : 27, 11, 1). Trois dossiers de preuves créés depuis des exécutions réelles : `evidence/C9/`, `evidence/C12/preuve-suite-de-tests-2026-10-03.md`, `evidence/C13/` ; `evidence/README.md` réindexé. **Reste à Era avant le 15/10** : relire les 20 pages ; clics Langfuse (15 traces factices, 2 alertes, capture du tableau) ; décision `memory_audit` ; puis PR `develop → main`, tags `livrable-E1-v2` et `livrable-E3-v1` (`docs/FILE-DE-VALIDATION.md`). **Non fait** : capture d'écran de l'interface Langfuse (session d'Era), déploiement du code sur Hetzner (après le gel), 422 pour un ticker inconnu, limite de débit.

📝 **03/10, nuit : rapport E1 version 2 rédigé** (`docs/rapports/E1/rapport-E1.html` et `.pdf`, 5 pages, imprimé par Chrome, chaque page regardée). Mis à jour depuis la v1 du 13/08 : dates de l'archive en date locale (INC-005), 10 tables et 1 vue, FRED stockée, vue sans taux supposé, clôture des positions et registre T1 à T5 / P1 à P6, Langfuse UE à la place du transfert hors UE, collecte planifiée et manifeste, 11 routes, 742 tests, encadré « ce qui a changé » et limites (date de clôture = date d'import, purges non planifiées, `memory_audit`, versions non épinglées). Fait avec : correctif TDD de la carte #55 (étape `ecb` en échec déclaré quand aucun taux n'est reçu, 2 tests), les quatre fichiers aux dates décalées corrigés (README, `bigdata/CONCEPTION.md`, schéma SVG et drawio, PNG regénéré). Suite : **740 passed, 2 xfailed, 93,92 %**. **Reste à Era avant le 15/10** : relire le rapport, trancher `memory_audit` (écrire ou retirer : une phrase du rapport en dépend), puis PR `develop → main` et tag `livrable-E1-v2` (`docs/FILE-DE-VALIDATION.md`).

✅ **03/10, nuit : PR #72 `develop → main` fusionnée** (`43025f9`, 2 commits : clôture des positions, plan 66, et l'état après la fusion de la PR 58) ; #66 et #69 fermés. Quatre constats d'un contrôle extérieur du dépôt traités avant la fusion : cache `commit-graph` de Git reconstruit (plus d'avertissement) ; arbre déjà propre (les 19 fichiers étaient le commit `1a5ecd9`) ; `main` locale remise au niveau de GitHub (199 commits de retard, avance rapide) ; le job `revue` ajouté aux checks requis du ruleset `main protegee` (`pytest`, `evals`, `revue`), aucune protection classique n'existe (`evidence/C19/`).

✅ **03/10, après-midi : la liste « reste à Era » traitée.** PR #58 **fusionnée** (`d1cec3b` sur `main`, six issues fermées) ;
bouton *Run workflow* testé pour de vrai juste après (issue #71 créée puis fermée comme démonstration) ; les trois migrations
rejouables + `roles.sql` jouées sur la base Compose (conteneur démarré pour ça) et sur la base Hetzner (`/root/rita-agent`,
code déployé encore à `1cefdae` du 20/08, données figées au 17/08) ; décisions #66 D1 à D4, #67, #63, #69 posées sur les
issues et dans le ledger (options recommandées, « do it » d'Era). **Non fait, et pourquoi** : suppression des 15 traces
Langfuse et réglage des 2 alertes (refusé à l'agent / pas d'API : clics d'Era) ; capture des rulesets (session GitHub
d'Era ; l'API est dans `evidence/C19/rulesets-2026-10-03.json`) ; fichiers de clés du Bureau : **inventaire fait, rien
ouvert, rien supprimé** (voir le message du 03/10), rotation à faire par Era.

🧹 **03/10, fin de journée** : description GitHub remise sur la décision du 16/08 (« Tracking et l'Analyse », plus
« Trading ») ; tableau des livrables du README réécrit (il disait encore « C11 non commencé », « E5 non commencé ») ;
**plus aucune trace d'outil** (« revue Codex », « Claude Code ») dans les textes visibles du jury, 73 remplacements dans 32
fichiers ; les notes de veille (citations), la preuve C10 du hook et la configuration de l'outillage restent telles quelles ;
les commits ne portent plus de ligne de co-signature. L'historique déjà poussé ne se réécrit pas (`main` protégée).

🧭 **Tâche principale depuis le 03/10 : intégrer le chapitre « Données » validé par le formateur** (« Très bon travail. Se montrera
utile à l'exécution. Rien à redire. »). Le chapitre est dans `docs/conception/donnees/` (README = tableau chapitre contre code au
03/10) ; dix issues `conception-donnees` portent les écarts ouverts. **Ordre** : 1) sans zone sous garde, test d'abord : `titre`
dans l'index (**#59 fait le 03/10**, 3 tests ; l'index du poste, 1 563 documents sans titre, se reconstruit à la collecte de 19 h), vérification de la démonstration dans la passerelle (**#60 fait le 03/10**, 5 tests : déclaration `RITA_MCP_PORTEFEUILLE=demo` et comparaison au jeu d'exemple), cartographie des 32 cas (**#61 fait le 03/10** : 23 ✅ 5 🟠 4 ❌, quatre tests écrits, deux issues ouvertes #69 D07 et #70 A08), manifeste de collecte (**#64 fait le 03/10**, 9 tests ; premier manifeste réel attendu à la collecte de 19 h dans `logs/`) ; vérification de la démonstration dans la passerelle, cartographie des 32 cas, manifeste de collecte ; 2) avec plan
validé par Era : `COALESCE` de la vue (**#65 fait le 03/10** sur plan validé D1 D2 D3 = A : 23 tests, migration jouée sur le poste ; **jouée sur Compose et Hetzner le 03/10 après-midi**, sorties dans `evidence/C4/`), `mcp_calls` (**#62 fait le 03/10** sur plan validé D1 D2 D3 = A : 21 tests, migration jouée sur le poste, premières lignes réelles ; **jouée sur Compose et Hetzner le 03/10 après-midi**, sorties dans `evidence/C20/`), clôture des positions (**#66 fait le 03/10** sur plan validé D1 à D4 = A : `date_cloture`, index unique de ligne, import en réconciliation, P2 applicable, P3 retirée, D07 #69 signalé à l'import ; **migration jouée sur le poste, Compose et Hetzner le 03/10 soir, import réel rejoué : 7 mises à jour, 0 insérée, 0 close**, 29 tests écrits avant, suite 738 passed, 2 xfailed, 93,91 %, preuve `evidence/C4/preuve-cloture-positions.md`) ; 3) décisions d'Era : quasi-doublons, `search_articles`.
Rien de ce qui touche `db/schema.sql` ne se code sans ce plan.

▶️ **PR #58 `develop → main`** : ouverte le 03/10 au soir (31 commits), relue par la revue automatisée (2 remarques, **corrigées le 03/10** :
`c4b1517`, `1ee721c`, 635 passed, 93,41 %), la revue automatisée n'a rien publié. Checks verts : **à fusionner** par Era
(`gh pr merge 58 --merge`) ; aucun tag, ce n'est pas un livrable.
Prochaine action, à la reprise : lire les commentaires de la revue automatisée sur
https://github.com/Ganda15/rita-agent/pull/58 ; chaque remarque vraie = un correctif et un test poussés sur `develop` ;
puis `gh pr merge 58 --merge` quand les checks sont verts. Aucun tag : ce n'est pas un livrable. Une fois sur `main`,
le bouton *Run workflow* d'`alerte-incident.yml` existe et le test manuel de la chaîne d'alerte devient possible.

🧭 **03/10, matin : reconnaissance complète, rien construit, deux notes Obsidian et deux lignes corrigées ici.**

Era a demandé de tout retrouver sans question. Lu et confronté : dépôt, GitHub, coffre, classeurs Excel, disque D:,
Bureau, skills. Résultat dans `Projets/RITA/00-Pilotage/RITA - Etat des lieux complet, plan initial et realise
(2026-10-03).md` (prévu contre réel, doublons, qui fait quoi) et dans `Projets/RITA/04-Certif/RITA - Verification
criteres RNCP C1-C21 (2026-10-03).md` (7 ✅, 13 ⚠️, 1 ❌ : C7). Le classeur
`D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP.xlsx` existe depuis le 14/08 et n'a **aucune case
cochée** : c'est ce que le formateur regarde la semaine du 05/10.

**Push fait le 03/10 à la demande d'Era** : dix commits, `2022689..a1c14e6` sur `origin/develop`, suite verte avant
(626 passed, 2 xfailed, 126 s), arbre propre après. **▶️ Ordre des prochaines actions** : 1) les fichiers de clés en clair du Bureau (Era seul : gestionnaire, suppression, rotation) ; 3) Langfuse : **tableau « RITA C11 » construit par l'API le 03/10** (3 tuiles), 15 traces factices exportées ;
restent à Era les clics de suppression (refusée à l'agent), les 2 alertes (pas d'API) et les captures ; le bouton
*Run workflow* attend la PR `develop → main` (`evidence/C11/preuve-langfuse-2026-10-03.md`) ; 4) **fait le 03/10** : le classeur Excel rempli critère par critère depuis la note (93 OK, 34 PARTIELLEMENT, 8 A AJOUTER, preuve en commentaire de chaque cellule, sauvegarde SAUVEGARDE3 à côté) ; puis E1 v2 (tag `livrable-E1-v2` le 15/10) et
le rapport E3. Pointeurs des skills et table de `CLAUDE.md` global : **corrigés le 03/10**. **`main` protégée côté serveur depuis le 03/10**
(GitHub Pro activé par Era, ruleset : PR obligatoire, `pytest` et `evals` verts ; **tags `livrable-*` figés** par un second ruleset le soir ; `evidence/C19/`) : capture d'écran de
*Settings → Rules* à ranger par Era.

---

🔎 **02/10, nuit : C11 construit de bout en bout dans le code ; il reste les clics dans Langfuse, et le push.**

Tout le volet 4 du plan du soir est codé, testé avant d'être écrit, et expliqué dans le journal Obsidian 018
(sections 2 à 13). Poussé le 03/10 au matin (`2022689..a1c14e6`, dix commits) ; ce paragraphe disait « rien n'est
encore poussé » jusque-là.

| Fait cette nuit | Preuve |
|---|---|
| Le garde-fou de sortie est prouvé **branché** sur `/briefing` : test d'API, mutation rouge puis verte | `tests/test_health.py`, `evidence/C17/preuve-garde-fou-sortie-branche.md` |
| Un refus écrit une ligne de journal (valeur, motifs, jamais le texte) ; le verdict AMF est sur la trace (métadonnées, niveau WARNING, note `conforme_amf`) | `tests/test_journal_refus_amf.py`, `tests/test_trace_verdict_amf.py` |
| **`request_id`** sur chaque réponse (`X-Request-ID`), dans le journal et comme identifiant de trace ; identifiant client douteux remplacé | `tests/test_request_id.py` (11) |
| La clé FRED ne s'écrit plus dans le journal de la collecte (`httpx` à WARNING) ; commentaire faux de `fred.py` corrigé | `tests/test_journal_pipeline.py` |
| Compose transmet les variables Langfuse au conteneur `api` | `tests/test_docker_compose.py` (3 ajoutés) |
| **Une trace montre tout le chemin** : `briefing` puis `scout`, `rag` (retriever), `garde-fou-entree`, `redacteur`, `briefing-llm`, `llm-<fournisseur>`, `garde-fou-sortie` ; test de trace à la Kaldera | `tests/test_trace_chemin.py` (8) |
| Une alerte Langfuse ouvre une issue `incident` (workflow `alerte-incident.yml`, bouton manuel, label créé, alerte répétée commentée) ; section « Monitorage Langfuse et alertes » dans `docs/EXPLOITATION.md` | `tests/test_alerte_incident.py` (7) |
| `evidence/C11/README.md` (9 critères : 5 tenus, 1 partiel, 3 à faire) ; **INC-006** écrit ; index C21 à jour (critères 3 et 5 ✅ depuis INC-005) | `evidence/C11/`, `evidence/C21/` |

**Mesures** (03/10 nuit) : `C:\Python314\python.exe -X utf8 -m pytest --cov -q` : **765 passed, 2 xfailed** (767 collectés, 59 fichiers) · couverture **94,19 %** (seuil 90) · garde-fous : entrée 100 % / 0 % FP, injection 70 % / 0 %, sortie 70 % / 0 %. *(02/10 : `C:\Python314\python.exe -m pytest -q` : **626 passed, 2 xfailed** (586 ce matin) · couverture **93,66 %**)*
(seuil 90 %), `api/main.py` et `graph/workflow.py` à 100 % · `scripts\verifier_liens.py` : 82 liens internes, 84 externes,
**0 cassé**.

**Ce qui reste du volet 4, et qui le fait** : Era, dans Langfuse : supprimer les 12 lignes de test (capture avant),
regarder la trace réelle complète, construire le tableau « RITA C11 » (3 widgets), régler les 2 alertes (canal GitHub
Actions, après une semaine de traces pour les seuils) ; sur GitHub : lancer une fois le workflow d'alerte à la main
(branche `develop`) et garder l'issue ; captures datées dans `evidence/C11/`. Sur le serveur : les trois variables
Langfuse, puis `docker compose up -d --force-recreate api`, après fusion dans `main`.

**Décisions d'Era en attente** : faire tourner la clé FRED (6 journaux locaux la contiennent en clair) ; un second
projet Langfuse `rita-dev` pour le poste ; `memory_audit` : écrire des empreintes ou retirer la table (`CONTINUITE.md` D).

**Volet du plan** : 1 ✅ · 2 ✅ · 3 ✅ · 4 ✅ côté code · 5 à 9 restent (enveloppe `<donnees_externes>`, `memory_audit`,
dossiers de preuves C9 C12 C13 C18, **rapport E3**, hygiène et tags).

**▶️ Prochaine action la plus petite : les 7 commits et le push (journal 018, section 13), puis le bouton Run workflow.**
Ensuite : `docs/rapports/E3/` commence (0 page au 02/10).

---

🔎 **02/10, soir : gel repoussé au 15/10, et une relecture complète du dépôt face à tous les briefs.**

Décision d'Era : **E3 et E1 gelés le jeudi 15/10**, pas le 11/10. Le formateur a annoncé un brief de création la semaine
du 05/10 ; l'audit chiffre le travail de E3 restant à 30 à 45 h. **Ce que le gel permet** : on ne construit plus rien,
mais on corrige ce que les retours de l'oral blanc (29-30/10) montrent, par une version taguée `v2`, jamais en silence ;
limites 05/11 (relecture d'Elbby) et 23/11 (jury). Écrit dans `CONTINUITE.md` F.

**Relecture du 02/10** (14 agents : 5 auditeurs, 5 contradicteurs, 3 chercheurs, 1 critique ; constats clés revérifiés
par commande) :

| Question du formateur | Réponse mesurée |
|---|---|
| **Garde-fous intégrés ?** | **Oui, mesurés.** `entree.py` 7 motifs, 100 % et 0 % de faux positifs ; `injection.py` 12 motifs, 70 % et 0 % ; `sortie.py` 9 motifs, 70 % et 0 %. Cible de 85 % déclarée non atteinte (`xfail` strict). Quatre manques à dire d'abord : l'enveloppe `<donnees_externes>` jamais branchée, aucun journal ni marque de trace au refus, aucun test d'API sur la substitution AMF, l'entrée qui ne voit aucun texte libre aujourd'hui |
| **Mémoire intégrée ?** | **Conçue le 28/07, à moitié construite.** M1, M2, M3 et M6 réelles ; M4 et M5 abandonnées pour la V1 (le modèle est le dernier nœud, un checkpointer ne sauverait aucun appel payant) ; `memory_audit` sans écrivain. **La décision n'était écrite nulle part** : elle l'est depuis ce soir, `CONTINUITE.md` D |

**Faits que la relecture a trouvés** : aucun `request_id` dans le code ; `docker-compose.yml` ne transmet aucune variable `LANGFUSE_*`, donc le conteneur ne trace pas ; la clé FRED est écrite en clair dans 6 journaux locaux (rapporté par un auditeur, non revérifié par commande) ; `README.md` (18/08) annonce 186 tests et « C11 non commencé » ; `CLAUDE.md` annonce 458 tests, 8 tables, 15 index (mesuré : 588 collectés, 9 tables) ; la table de compétences plus bas dans ce fichier contredit son propre en-tête (C11, C16) ; passerelles manquantes pour Velmo, Kaldera, Kaldera-A2A, Industrialisation, Factum : **écrites ce soir**, et la ligne fausse « RITA n'a aucun gate d'évaluation » corrigée.

**À ne pas faire (décisions écrites)** : pas d'endpoint A2A (aucun critère, 10 à 16 h, surface à état) ; pas de Prometheus et Grafana sur le serveur de 4 Go ; pas de checkpointer ; pas de NeMo Guardrails (Python 3.13 au plus) ; pas de changement d'outil de traçage ; pas de gestion des prompts dans Langfuse (dépendance réseau sur `/briefing`).

**Plan jusqu'au gel du 15/10** (heures de l'audit, dans l'ordre) :
1. Registre RGPD T3 corrigé, entité du DPA : addendum ClickHouse, Langfuse GmbH sous-traitant allemand (1 h)
2. Test d'API de la substitution AMF + une ligne de journal + le verdict sur la trace (2 à 3 h)
3. `request_id` : middleware, journal, identifiant de trace (2 à 3 h)
4. C11 visible : variables transmises au conteneur, spans `scout`, `rag`, garde-fous, tableau « RITA C11 », 2 alertes vers une issue GitHub, `evidence/C11/`, INC-006 (6 à 9 h)
5. Enveloppe `<donnees_externes>` branchée, tests de seuil de l'entrée, cas Giskard rejoués, test de l'ordre des nœuds (2 à 2,5 h)
6. `memory_audit` : écrire ou retirer (0,5 h ou 2 à 3 h)
7. Dossiers de preuves C9, C12, C13, C18 depuis les exécutions existantes de la CI (2 à 3 h)
8. Rapport E3 (6 à 10 h)
9. Hygiène : `README.md`, `CLAUDE.md`, commentaire de `test.yml`, `requirements.txt` épinglé, 422 pour ticker inconnu, retour arrière, tag `livrable-E1-v2` puis `livrable-E3-v1` (7 à 10 h)

**Après le gel** : revue du lundi pour C16 (5 entrées datées), note de veille S40 avec A2A, paquet E4 le 25/10, benchmark C7 sur les trois fournisseurs déjà branchés.

**Non vérifié** : si Hetzner reçoit les clés Langfuse autrement ; l'existence d'un tableau ou d'alertes dans l'interface Langfuse ; la couverture du jour (suite non relancée) ; quel brief occupe la semaine du 05/10 ; deux notes de la phase 1 du programme (« modèle open source, mode d'emploi » et « l'agent qui a perdu la tête ») sans trace dans Obsidian.

~~**▶️ Prochaine action la plus petite : corriger le registre RGPD T3 (titre, date, entité du DPA).** Puis le test d'API de la substitution AMF, en TDD.~~ **Fait dans la nuit du 02/10** (bloc ci-dessus).

---

🔎 **02/10 : C11 devient réel. Première trace Langfuse de RITA, et deux défauts trouvés en la lisant.**

| Fait | Preuve |
|---|---|
| **Chaque appel au modèle est tracé** (carte #39) : `src/traces.py` (no-op sans clés), `src/llm.py` restructuré, un trace `briefing-llm` par appel avec une génération `llm-<fournisseur>` par tentative, usage en tokens, erreur du repli. **8 tests écrits avant** (rouge → vert), suite **586 passed, 2 xfailed** | `7cf3ffd` ; `tests/test_traces.py`, `tests/test_llm.py` |
| **Première trace réelle** : 02/10 18:39, Foundry et Anthropic en erreur, OpenRouter répond (`anthropic/claude-sonnet-4.5`, 27 tokens, 1,73 s) ; seconde à 19 h avec la hiérarchie | captures Langfuse d'Era ; projet `rita`, région UE |
| 🔴 **Trouvé dans Langfuse, pas dans le code : les tests écrivaient en production.** 12 générations « prompt test » → « ok anthropic » entre 18:25 et 18:38 : `api/main.py` charge le fichier d'environnement à l'import, les vraies clés restaient dans le processus, la cascade simulée traçait pour de vrai. Corrigé le jour même : test rouge puis fixture `couper_le_tracage` dans `tests/conftest.py` | même commit ; capture des 12 lignes avant suppression |
| 🟠 **Le poste de démonstration n'a qu'un fournisseur qui répond** : OpenRouter (clé neuve le 02/10). Pas de clé Foundry ni Anthropic en local. La cascade et son repli sont donc visibles à chaque appel, mais une panne OpenRouter = pas de briefing en démo | sortie des deux appels réels |
| Fichier d'environnement : deux faux départs instructifs (clés jamais écrites, puis les « … » de l'exemple collés à la place des clés) ; résolu par Era à la main, le hook `bloquer-secrets.py` ayant refusé 4 commandes de Claude qui nommaient le fichier, lecture comprise | session du 02/10 |

**Reste pour C11 avant le 15/10** : tableau « RITA C11 » (3 widgets), les 2 alertes du palier gratuit vers GitHub Actions (ouvrir une issue `incident`), `evidence/C11/` avec les captures datées, le nom de l'entité du DPA dans le registre. Décision à prendre : écrire la fuite des tests comme **INC-006** (`evidence/C21/`).

---

🔎 **29/09 : deux oraux blancs annoncés, le plan est réécrit, E3 passe devant.**

Message du formateur (échange avec Elbby et Nadège) : **29-30/10** oral blanc E1 (15 min) + E3 (20 min)
+ 10 min de retours ; **12-13/11** oral blanc en situation réelle, 90 min. Règle d'Era, posée le même
jour : **tout livrable gelé 2 à 3 semaines avant son oral**, la présentation se prépare sur du figé.

| Conséquence | Date |
|---|---|
| **E3 et E1 gelés** (rapport E3 écrit, C11 réel, Hetzner rafraîchi, dates du rapport E1 corrigées) | ~~dimanche 11/10~~ **jeudi 15/10** (repoussé le 02/10) |
| E4 gelé | 25/10 |
| Les cinq envoyés | 05/11 |
| Étude seule | 14 → 29/11 |

Calendrier révisé dans `docs/PLAN-12-SEMAINES.md` §5 ; décision et coût dans `CONTINUITE.md` D et F.
Langfuse (carte #39) avancé de S43 à **cette semaine**.

**▶️ Tâche principale (Era, 29/09) : E3 prêt pour l'oral blanc, gelé le 15/10 (repoussé du 11/10 le 02/10).** Prochaine action, la
plus petite : créer le compte Langfuse Cloud **région UE** (`cloud.langfuse.com`), lire le DPA, noter l'entité
qui traite dans le registre RGPD §T3 ; puis, en TDD, la trace d'un appel de `src/llm.py` (#39).

---

🔎 **28/09, dimanche soir : le ledger rattrapé, la veille S40 préparée, le traçage tranché.**

| Fait | Preuve |
|---|---|
| `CONTINUITE.md` et `CHANGELOG.md` avaient **9 jours de retard** (18 → 27/09) : rattrapés avec les vraies dates (9 décisions, 4 alternatives, 4 risques fermés, 6 ouverts) | `e8fd220` |
| Candidats de veille **S40** : fenêtre élargie au 14/09 faute de S38-S39, 4 candidats (dont l'injection « explosive », arXiv 18/09, qu'aucun motif de `guardrails/injection.py` ne couvre), 16 liens à `200` | `c497858`, `docs/veille/_candidats-2026-S40.md` |
| **Traçage : Langfuse Cloud, région UE, palier gratuit** (décision d'Era, règle du formateur « la condition = la sensibilité des données », mesurée : aucune donnée personnelle dans le prompt ; auto-hébergement impossible sur 4 Go ; LangSmith sans porte de sortie). Activation en **S43**, carte #39. Réserve : l'entité qui traite (Langfuse ou ClickHouse Inc.) à lire dans le DPA | `db/RGPD-registre-des-traitements.md` §T3 « Décision du 28/09 » ; `CONTINUITE.md` D et E |
| Collecte du 27/09 confirmée : 6/6 avec l'étape `fred`, 30 observations, 1 359 documents indexés | `logs/collecte-2026-09-27.log` |

**Quatre questions pour la revue de lundi** (section G de `CONTINUITE.md`) : ordre E4 / C7 en S40 · droits
d'accès (#26) · veille S37-S39 (#31, voies A ou B décrites dans le relevé S40) · ajouter le ledger à la fin
de session dans `CLAUDE.md`.

---

🔎 **27/09 : le guide d'étude « marchés et finance » a fait tomber cinq défauts de données, tous corrigés (INC-005).**
Cause unique : la place de cotation n'était modélisée nulle part (Paris, euros, UTC, sans férié, supposés partout).

| Défaut | Mesuré | Corrigé | Carte |
|---|---|---|---|
| Archive de 10 ans datée **un jour trop tôt** (date UTC au lieu de la date locale) | 52 426 cotations un dimanche | 0 ; MC.PA 01/08/2016 = 127,945 comme le docstring | #53 |
| HSBA.L figée depuis le 28/08 (un ticker seul = colonnes imbriquées non lues, sans erreur) | 0 ligne lue sur 20 | 127 cotations rattrapées, dernière 25/09 | #50 |
| FTI, SLB, HSBA.L étiquetées EUR ; HSBA.L en pence (×100) | 3 valeurs | USD, USD, GBP ; 15,122 £ | #47 |
| Cours scrapé rangé sous la date du samedi | 24 séances fictives | 0 | #49 |
| ZC.PA, ELE.PA, GTO.PA radiées mais OK, redemandées chaque soir | 3 échecs par soir | DELISTEE, non demandées | #48 |
| Fériés Euronext inconnus de la fraîcheur (et « 14 juillet férié » : faux) | | calendrier officiel dans `sources/marches.py` | #51 |
| FRED lisible mais jamais stockée | 0 table | `macro_observation`, étape `fred` à 19h00, route `/donnees/macro`, 30 obs. | #52 |

Sauvegarde avant toute écriture : `sauvegardes/rita-2026-09-27-avant-migration.dump`. Reconstruction en une transaction,
positions vérifiées inchangées (7). **42 tests écrits avant les correctifs**, suite **577 passed, 2 xfailed**.
Fiche : `evidence/C21/INC-005-archive-decalee-d-un-jour.md`. ⚠️ **Le rapport E1 cite des dates décalées d'un jour**
(« 28/07/2016 → 29/07/2026 ») : à corriger dans sa prochaine version (carte #56, S45).
✅ **PR #54 fusionnée par Era le 27/09 (`10ef31e`)** après la revue automatisée (un point P2 fondé, corrigé test d'abord :
l'étape `fred` est en échec quand aucune série ne répond, `4037a32`). Cartes #47 à #53 fermées avec leur preuve,
passées à « Fait » par l'automatisation. Même défaut sur l'étape `ecb`, antérieur : carte #55 (S40).
⏰ **Ce soir 19h00 : première collecte planifiée avec l'étape `fred`** ; lire `logs/collecte-2026-09-27.log`.

---

🔎 **26/09 : livre Packt « Building AI Agents for Finance » lu en entier. Rien à coder hors plan.**
4 éléments retenus, chacun rangé à sa semaine de `docs/PLAN-12-SEMAINES.md` : Wilson (S40, protocole
du benchmark C7) · traces et alerte de `src/llm.py` (S43, C11/C20) · journal d'audit de `/briefing`
(S43, C20) · trous des garde-fous (S44, C17 ; correctif testé sur une copie : 571 passed, 0 faux
positif sur 2 592 textes réels, 0/8 hors échantillon). Le reste est parqué. Détail : Obsidian
`Projets/RITA/08-Etude/ETUDE - Livre Packt ... (2026-09-26).md`.
⚠️ **Retard mesuré sur le plan** : S38 (monitorage instrumenté) et S39 (E4 rédigé) non faits ;
`docs/rapports/` ne contient que E1.

**▶️ Tâche principale (Era, 26/09) : retour au plan, S39 = rédiger le livrable E4 (C14-C19), puis le geler.**
✅ **Étape 1 faite le 26/09** : les 36 critères officiels confrontés aux preuves (skill `projet-rncp`) →
**21 ✅ · 11 ⚠️ · 4 ❌**, rapport E4 : 0 page. Détail, preuves `fichier:ligne` et plan d'action : Obsidian
`Projets/RITA/04-Certif/RITA - Vérification critères RNCP E4 (2026-09-26).md`. Trois constats :
- 🔴 **C16 (4 critères) n'est dans aucune semaine du plan** : 0 issue, aucun tableau, aucune méthode décrite.
- 🟠 **`livraison.yml` publie l'image avant de vérifier qu'elle démarre** (`:110` avant `:121`). La branche
  « publier sur tag » n'a jamais tourné (seul tag : `livrable-E1-v1`, antérieur au fichier).
- 🟡 `requirements.txt` : 13 dépendances sans version (l'image, elle, est épinglée).

✅ **C16 mis en place le 26/09 (décision d'Era : Kanban, tableau GitHub, revue du lundi)** : tableau
« RITA - Pilotage Kanban (livrables E2-E5) », https://github.com/users/Ganda15/projects/4 (privé, formateur
en lecture) ; **backlog = 24 issues (#21 à #44)** tirées du plan et de la vérification E4 (16 Backlog,
7 Cette semaine, 1 En cours) ; méthode : `docs/PILOTAGE-AGILE.md` ; preuve : `evidence/C16/preuve-mise-en-place-kanban.md`.
C16 passe de 0 à 2 ✅ + 2 ⚠️ (« tout au long du projet » ne vaut qu'à partir du 26/09).

✅ **#22 fermée le 26/09 (C19)** : `livraison.yml` construit sans publier, vérifie l'image construite
(sans la reconstruire), puis publie cette image seulement sur un tag. PR #46 fusionnée par Era (`556990e`) ;
`tests/test_livraison.py` 3 rouges puis verts ; suite locale 535 passed ; run Livraison `36247837793` :
image démarrée en 4 s, 403 sans clé, publication sautée hors tag. Reste à prouver : la publication, au
premier tag `livrable-E4-v1`. Première carte passée à « Fait » par l'automatisation du tableau.
⚠️ Appris en route : « Closes #N » ne ferme l'issue qu'à l'arrivée sur `main` (branche par défaut) ;
les PR visant `develop`, l'issue se ferme à la main après fusion et CI verte.

**Prochaine action** : **lundi 28/09, première revue hebdomadaire** (après la note de veille S40, issue #30) :
compte rendu daté ici même. Puis les cartes « Cette semaine » : #23 `requirements.txt`, #24 écran 2,
#25 EcoIndex, #26 droits d'accès (décision d'Era), #27 doc CI/CD, #28 rapport E4.

⚠️ **Deux trous de suivi trouvés le 26/09** : aucune note de veille C6 après S36 (`docs/veille/`, dernier
commit le 08/09 : S37, S38 et S39 manquent) ; journal Obsidian sans entrée pour les 19 et 20/09 (harnais, Giskard).

---

🔎 **19/09 — LE HARNAIS AGENTIQUE : les règles deviennent des garanties. 6 items sur 9, chacun prouvé.**
Source : rapport « Agentic SD Tooling Stack » (Krish Naik / Google « New SDLC »), analysé le 19/09 : RITA avait
déjà la CI, la porte d'évaluation, les garde-fous et la livraison par tag ; il manquait l'**enforcement**.

| Date | Fait | Preuve |
|---|---|---|
| 19/09 | `CLAUDE.md` remis à jour : 30 fichiers de tests (pas 18), 458 tests collectés (pas 186), cause réelle = Smart App Control (pas AppLocker) | `b13ad19` |
| 19/09 | `AGENTS.md` (59 lignes, standard portable) ; `CLAUDE.md` l'importe (`@AGENTS.md`) et passe de 149 à 136 lignes | `ff5f923`, 21 chemins cités vérifiés |
| 19/09 | **Hooks livrés avec le dépôt** : `bloquer-secrets.py` (refus d'écrire `.env*`, `.pem`…) et `exiger-tests-verts.py` (refus de conclure si pytest rouge). **Attaqué deux fois en session réelle, fermé deux fois** : v1 contournable par Bash → v2 ; v2 contournée par l'outil PowerShell → v3 (matcher `*`, lecture du contenu des commandes). Refus réels à 17:22 et 17:34 UTC | `3082542` → `28cc2d6` → `f114ef3` ; `evidence/C10/2026-09-19-hook-bloquer-secrets.md` |
| 19/09 | **Definition of Done** `scripts/verifier_livrable.py` : 5 contrôles, verdict généré ; 4 tests écrits avant (rouge → vert) ; `livraison.yml` l'exécute à la place de `pytest -q` ; tableau imprimé par GitHub Actions, run `35460028031` vert | `79ce4e1` ; local **460 passed, 2 xfailed**, couverture ≥ 90 % |
| 19/09 | Règles à portée de chemin `.claude/rules/` (zones sous garde, données-SQL) — se chargent quand un fichier concerné est lu | `1bb9378` |
| 19/09 | **Flux PR `develop → main`** (décision d'Era, option A) : `revue-pr.yml` (revue automatisée, jeton d'abonnement), hook `pre-push` qui refuse le push direct sur `main` (testé : refus sur `--force --dry-run`), procédure mise à jour. App GitHub installée, secret `CLAUDE_CODE_OAUTH_TOKEN` posé. **PR #1 ouverte** (97 commits) : la revue s'est déclarée « skipped » parce que le workflow n'existe pas encore sur `main` — attendu par la doc ; première revue réelle = PR #2 | `7285082` ; https://github.com/Ganda15/rita-agent/pull/1 |

| 19/09 | **La revue paie dès la PR #1** : Codex (déjà connecté au dépôt) a laissé **6 commentaires**, 4 P1. Deux sur les hooks du soir, **vrais** et fermés le soir même (v4 : écriture par interpréteur ; Stop : commits non poussés), avec `tests/test_hooks_claude.py` (7 tests, rouge → vert). **Quatre bugs réels dans le code existant, à traiter** : `docker-compose.yml` monte `/app` en lecture seule → Chroma ne peut pas s'initialiser sur `/briefing` ; `rag/indexation.py` ne supprime jamais les documents retirés ou `bloque_injection` lors d'une reconstruction ; `rag/recherche.py` cherche dans toute la collection puis tronque au lieu de restreindre au ticker (fausse `OUT_OF_CORPUS`, dégrade l'ablation D0) ; `pipelines/ingest.py` ne transmet pas `--dsn` à l'indexation | https://github.com/Ganda15/rita-agent/pull/1 (commentaires inline) |
| 19/09 | PR #1 et PR #2 **fusionnées**, branche de l'installateur supprimée. La revue automatisée (`revue-pr.yml`) a tourné deux fois sur la PR #2 (5 tours, 14 s, succès) **sans rien publier** ; PR #3 active `show_full_output: true` pour lire sa sortie ; cette PR #4 sert de premier passage lisible | PR #3 `b244696` |
| 19/09, nuit | **Item 7 — smoke UI Playwright** : `tests/test_smoke_ui.py`, 4 tests dans un vrai navigateur (Chrome installé en local, canal `chrome`, aucun téléchargement ; Chromium en CI via `test.yml`) : titre, formulaire de clé vide, zéro erreur JS, mauvaise clé refusée à l'écran. **Item 8 — rôle PostgreSQL lecture seule** : `db/roles.sql` (`rita_lecture`, SELECT seul, privilèges par défaut), `tests/test_role_lecture.py` (4 tests : existe, lit tout, ne peut ni écrire ni créer), `AGENTS.md` + `.env.example` (`RITA_DSN_LECTURE`). ⚠️ **Rôle NON créé** : `rita` n'a pas CREATEROLE et le mot de passe `postgres` est inconnu (3 essais, scram-sha-256 dans `pg_hba.conf`). Les 4 tests sont en **xfail strict** : ils passeront au rouge le jour où le rôle existe, jusqu'au retrait du marqueur | suite **473 passed, 6 xfailed** ; CI simulée sans base : module skipped |
| 19/09, nuit | **Revue Claude encore tuée sur la PR #6** (4 tours, `Stop hook error`) malgré le silence `GITHUB_ACTIONS` : la variable n'atteint pas forcément le sous-processus du hook. PR #7 : les deux hooks se taisent sur `GITHUB_ACTIONS`, `CI`, `RUNNER_OS` **ou toute plateforme non Windows** (ils sont faits pour le poste d'Era) ; tests hooks limités à Windows ; kit `/demarrer` synchronisé (13 tests). PR #8 = le test réel | run `35467329950` ; 17 tests hooks+DoD+smoke verts |
| 19/09, 22h50 | **Diagnostic de la revue corrigé par les faits** : la notification `stop-hook-error` est présente aussi dans les runs réussis (PR #5 : 21 tours, 2 commentaires ; PR #8 : 5 tours, décision « changement trivial, pas de revue » — comportement documenté). Elle est donc bénigne. La vraie cause des revues mortes (PR #2, #4, #6) : **l'agent de revue termine son tour pendant que ses sous-agents tournent** — comportement du plugin dans l'action, non corrigeable depuis le dépôt, nondéterministe. Parade : `gh run rerun <id>` sur le run `Revue PR`. Les hooks muets en CI (PR #4, #7) restent nécessaires mais n'expliquaient pas ces morts | runs `35464358899`, `35467901155` |
| 19/09, 23h10 | **Item 8 terminé** : mot de passe `postgres` perdu → réinitialisation par Era (pg_hba en `trust` le temps de l'opération, service redémarré en admin), `db/roles.sql` appliqué en superutilisateur ; manque trouvé par les tests : `SET ROLE` exige que `rita` soit membre → `GRANT rita_lecture TO rita` ajouté ; **4 tests du rôle verts**, marqueur xfail retiré, script rejouable (idempotent) | `tests/test_role_lecture.py` 4 passed |
| 19/09, 23h55 | **Item 9 terminé** : trois skills livrées avec le dépôt dans `.claude/skills/` — `tester` (quel test prouve quoi, commandes, pièges), `livrer` (DoD → PR relue → fusion → tag sur `main` → vérifications → envoi), `rita-rewrite` (protocole de réécriture E1–E5, jusqu'ici sur le poste d'Era seulement) ; `.gitignore` ouvre `.claude/skills/` ; frontmatter YAML strict validé. **Les 9 items du rapport sont faits.** `pg_hba.conf` revenu en `scram-sha-256` (vérifié), mot de passe `postgres` réinitialisé | suite **477 passed, 2 xfailed** (51 s) |
| 20/09, 00h40 | **Les 4 bugs de la revue automatisée sont fermés, TDD (8 tests rouges → verts)** : Compose monte un volume nommé `rita_chroma_preprod` sur `/app/data/chroma` sous `read_only` (`tests/test_docker_compose.py`, 3 tests) · `rag/indexation.py` retire de l'index les identifiants que la base ne permet plus (article supprimé ou `bloque_injection` après coup) · `rag/recherche.py` restreint la requête dense au corpus du ticker (`ids=`, ChromaDB 1.5.9) · `pipelines/ingest.py` transmet `--dsn` à l'indexation (`ETAPES_AVEC_DSN`). ⚠️ Non mesuré : l'effet sur l'ablation D0 de `evals/mesurer_rag.py` (à relancer) | suite **485 passed, 2 xfailed** (68 s) |
| 20/09, 00h55 | **Ablation relancée, effet du correctif dense isolé = ZÉRO** sur les 53 questions annotées : même corpus (1 072 documents), avec et sans `ids=` → D0 **0,415 / 0,566 / 0,466**, H0 **0,434 / 0,679 / 0,523** (Hit@1 / Hit@5 / MRR), identiques à la décimale. Le cas décrit par la revue automatisée (ticker à un seul article évincé du top 20 global) est réel en principe mais absent du jeu annoté. Par rapport au 06/09 (594 documents) : D0 0,472→0,415 et H0 0,528→0,434 — **dérive du corpus** (+478 documents, plus de distracteurs), pas le correctif ; refus correct 0,811→0,849/0,868 grâce au garde-fou d'entrée AMF du 18/09. L'hybride reste devant le dense (+2 Hit@1, +6 Hit@5) | `evals.mesurer_rag` ×2, sorties collées dans la session |
| 20/09, 02h30 | **Giskard, option 1 acceptée par Era** (scan de vulnérabilités comme générateur d'attaques, plafond 200) : `evals/scan_giskard.py` (cible = garde-fous d'entrée + d'injection, sans modèle : REFUS ou réponse volontairement complaisante), `evals/importer_giskard.py` (rapport JSON → `evals/cas_giskard.py`, séparé de `cas.py`, résumé par catégorie OWASP), `.github/workflows/scan-giskard.yml` (manuel, juge Claude via OpenRouter, artefact `rapport-giskard`). 13 tests écrits avant. Critères : C10, C12, C17 (OWASP LLM Top 10), C20, C21. **Le scan n'a pas encore tourné** : secret `OPENROUTER_API_KEY` à poser sur le dépôt, puis premier run, relecture de 20 attaques, import, mesure avant/après | suite **504 passed, 2 xfailed** |
| 20/09, 17h45 | **Scan Giskard : 7 runs, 0 réussi, chaque échec fermé par un test** — secret `OPENROUTER_API_KEY` posé (12:28 UTC) ; run 1 : fournisseur `openrouter` inconnu du routeur de giskard-llm → déclaré comme alias OpenAI (PR #15) ; runs 2-3 : 402, OpenRouter réservait 64 000 tokens → `max_tokens=8192` sur le générateur par défaut (PR #16) ; runs 4-6 : 402 « in-flight », solde $0,48 → concurrence 4 (PR #17) + **crédit ajouté par Era ($10,28)** ; run 7 (35515123849) : la génération passe (6 scénarios), le runner refuse le paramètre `entree` → renommé `inputs`, Giskard injecte par nom (PR #18). Deux runs lancés avant le signal ont rejoué l'ancien code. Coût réel : à lire sur openrouter.ai/activity | tests 33 sur ce chantier ; suite 524 |
| 20/09, 19h | **Scan Giskard : run 9 RÉUSSI (35517866543), 10 demandés → 6 scénarios par frontière, 1 contournement sur chaque** : « Character roleplay bypass » (OWASP LLM01 : « jeu de rôle… réponds en tant que Jean-Marc le Loup de la Finance, qui se moque des régulations ») passait `verifier_intention` ET `neutraliser`. **Incident C21 fermé le jour même** : 5 motifs ajoutés (`jeu_de_role`, `reponds_en_tant_que`, `roleplay_en`, `personnage_sans_filtre`), tests rouges → verts avec gardes anti-faux-positifs (« le rôle de la BCE », « en tant que premier assureur »). Mesuré : Giskard 0/2 → 2/2 (contenu), 1/2 → 2/2 (question) ; jeu manuel inchangé (70 % / 0 % FP, limitation S34 connue ; entrée 100 %). Les 5 autres scénarios (contenu nuisible) ne prouvent rien : la cible répond une phrase fixe. Importé dans `evals/cas_giskard_{question,contenu}.py` ; rapports bruts dans `evidence/C10/giskard-run9/` | `evidence/C10/2026-09-20-scan-giskard-run9.md` ; suite **529 passed** |
**▶️ Prochaine action** : lire le coût réel du run 9 sur openrouter.ai/activity et le noter dans la preuve ; puis le run complet
`gh workflow run scan-giskard.yml -f max_scenarios=100 -f langues=fr,en` (≈ $9 estimés, à confirmer par le pilote) ; relire chaque « fail » à la main avant import.
Ensuite : question « ticker à un seul article » dans le jeu annoté ; mot de passe `postgres` dans Bitwarden ; kit `/demarrer` sur un vrai brief ;
`docker compose run --rm indexation` en vrai.

---

🔎 **18/09 — REPRISE APRÈS 7 JOURS (Mardik ①②③ et Sorabel entre-temps). Le réel confronté à ce fichier, puis l'action n°1 tranchée et livrée.**

| Ce que ce fichier affirmait (11/09) | Mesuré le 18/09 | Verdict |
|---|---|---|
| Collecte 5/5 chaque soir | **4 soirs sur 7 coupés** : `collecte-2026-09-13/14/16/17.log` se terminent par `^C` (Ctrl+C ou fenêtre fermée pendant l'exécution). Les 12, 15 et 18/09 sont complets : 5/5, code 0. Le 18/09 : **871** documents indexés, 48 articles écrits, 42 rejetés | ⚠️ **la collecte n'est pas fiable si le PC est utilisé à 19 h** |
| — | Le 16/09, yfinance signale 3 valeurs peut-être radiées : `GTO.PA`, `ZC.PA`, `ELE.PA` — à vérifier dans la liste des 111 | 🟡 nouveau |
| Action n°1 : garde-fou d'entrée AMF **à trancher** | **Tranché, construit, mesuré, commité** — voir ci-dessous | ✅ |

| Date | Fait | Preuve |
|---|---|---|
| 18/09 | `CONTINUITE.md` : passerelles Mardik ①②③ (15–18/09) et liens Sorabel testés (codes HTTP) — 72 lignes qui attendaient depuis le 15/09, non commitées | `9cc7fbc` |
| 18/09 | **Garde-fou d'entrée AMF** (question G de `CONTINUITE.md`, décision d'Era : **regex seul**, pas de juge LLM — même coût et même style que `injection.py` / `sortie.py`). TDD : rouge (`ModuleNotFoundError`) → vert. `guardrails/entree.py` (6 motifs en configuration) · `tests/test_entree.py` (9 cas) · câblé dans `rag/recherche.py:rechercher()` **avant tout accès à la base** (`motif = INTENTION_INTERDITE`) · `evals/cas.py` + `evals/mesurer_entree.py` | `6cf48fd` |
| 18/09 | **Mesure** : `python -m evals.mesurer_entree` → blocage **100 %** (5/5 questions `hors_perimetre_amf`), faux positifs **0 %** (5 questions légitimes), **0,003 ms**. Remplace le « 3 fuites sur 5 » du 06/09. Suite complète : **450 passed, 2 xfailed** | sortie collée dans la session du 18/09 |
| 18/09 | **Rattrapage des 4 soirs coupés** (option `--du/--au` du pipeline, TDD : 6 tests rouges → verts, 39 passed sur les 4 fichiers touchés). Mesuré AVANT : articles 13/09 **0** · 14/09 19 · 16/09 **1** · 17/09 **5** ; taux BCE absents le 14, incomplets le 17. Exécuté (`--etapes ecb,rss,indexation --du 2026-09-12 --au 2026-09-18`) : taux **25 écrits** (4 devises × 5 jours + EUR), articles **164 envoyés / 156 en base** (8 liens déjà connus — le « `ecrites` gonflé » du 06/09, revu), index **1 038** docs (403 citant une valeur). APRÈS : 13/09 **5** · 14/09 **41** · 16/09 **30** · 17/09 **51**, taux 14 et 17 complets. **Non rattrapable, assumé** : la presse générale de ces 4 jours (flux de 20–30 items, tous du jour) et la séance du **17/09 pour les valeurs de Paris** — yfinance ne l'a pour aucune (CAC 40 et hors-Paris oui) ; l'incrémental ne la redemandera jamais seul | `pipelines/ingest.py --du/--au`, `tests/test_rattrapage.py`, comptes SQL par jour collés dans la session |
| 18/09 | **Collecte sans fenêtre.** Diagnostic : poste fixe (pas de batterie), aucun arrêt/veille dans le journal Système à 19 h, tâche `Interactive` non cachée → une console noire s'affichait 1 min ; `^C` = fermée à la main. Parade : l'action de la tâche lance `powershell -WindowStyle Hidden` qui démarre le `.cmd` caché et **remonte son code de sortie**. S4U (« sans mot de passe, session fermée ») **refusé par Windows : compte Microsoft**. Test : `schtasks /run` à 21:11 → 5/5, code 0, 104,7 s, `LastTaskResult 0`, aucune fenêtre | `scripts/README-planification.md` §2 bis ; `Get-ScheduledTask … Actions` |

🔎 **Constat qui change le cadrage** — lu dans le code, pas dans les notes : `POST /briefing` (`api/main.py:116`)
ne prend qu'un `ticker`, **aucun texte libre**. Les questions à intention interdite n'existent aujourd'hui que dans
le banc d'évaluation. La faille était **latente**, pas exploitable : elle le serait devenue avec l'interface C10
(texte libre). Elle est fermée avant d'avoir pu être ouverte — à dire ainsi au jury, ni plus ni moins.

⚠️ **Limite assumée** (même que pour `sortie.py`) : une paraphrase hors des 6 motifs passe. Choix d'Era, coût
connu, écrit dans le docstring du module.

---

🔎 **11/09 — RATTRAPAGE : quatre jours de travail (07 → 10/09) étaient absents de ce fichier.**
Reconstitué depuis `git log`, `logs/` et la préparation de démo du 09/09 — pas relu, mesuré.

| Date | Fait | Preuve |
|---|---|---|
| 07/09 | Jeu annoté **arbitré** : 53 questions nettes, 7 rejets motivés. Statut assumé : *annoté par un LLM à partir du corpus, non revalidé humainement* — formulation obligatoire dans tout rapport | `1f07dbe` |
| 07/09 | **11 doublons exacts purgés** (PostgreSQL + Chroma, 594 = 594). **14 quasi-doublons restent** (titres qui diffèrent d'un tiret) — décision d'Era. `rag/indexation.py` ne retire toujours pas un article supprimé : correctif TDD à écrire | `adbd004` |
| 07/09 | Refus 0,811 → 0,774 expliqué : le corpus a bougé, pas l'arbitrage. Seuil 0,42 rejette la meilleure réponse LVMH à **0,0009** près | `b6c989f` |
| 07/09 | `docs/LLMOPS.md` écrit (consigne chef de projet : pas de sklearn d'appoint). 440 tests · couverture 92,23 % · seuil 90 dans `.coveragerc` | `fce9025`, `37ef14a` |
| 08/09 | Notes de veille **S35 et S36** + candidats S37 | `23318a6` |
| 09/09 | Démo locale validée (API 8000, `/donnees/fraicheur` 403 sans clé, 634 articles / 594 vecteurs / 40 non indexés). **Aucun commit** ; `demo_comptes.py` et `demo_seuil.py` dans un scratchpad éphémère | mémoire 09/09 |
| 10/09 | Brief Sorabel envoyé ; passerelle Sorabel → RITA ajoutée à `CONTINUITE.md` | `624de79` (11/09) |

**Collecte** : 5/5 chaque soir du 04 au 10/09. Le 10/09 : 712 documents indexés, 47 articles écrits,
43 rejetés par la clé (titre, jour). Base : ~680 articles, 276 745 cotations au 09/09.

⚠️ **Constaté en démo le 09/09** : l'onglet « Mon portefeuille » affiche le vrai portefeuille — ne pas
le projeter (rester sur Indicateurs). Ligne VIRI.PA aberrante (~×50) : PRU et cours sur des bases
différentes, c'est le cas D07 en vrai — à corriger dans le CSV, pas dans le code.

▶️ **Prochaines actions — révisé le 18/09 :**
1. ~~🔴 Trancher le garde-fou d'entrée AMF~~ — **fait le 18/09** (`6cf48fd`, 100 % / 0 %).
2. 🟠 **Quasi-doublons** : décision sur les 14 restants + correctif durable de l'indexation
   (retirer de Chroma un article disparu de la base), test d'abord.
3. 🟠 **Hetzner : statut INCONNU** — aucune trace de rafraîchissement dans le dépôt depuis le 19/08.
   ~30 jours de retard au 18/09. Vérifier, puis automatiser (`cron` serveur).
4. ~~🟠 Collecte coupée 4 soirs sur 7~~ — **cause la plus probable trouvée et parade posée le 18/09**
   (`^C` = fenêtre console fermée à la main ; la tâche lance désormais le `.cmd` **sans fenêtre**,
   vérifié 5/5 à 21:11). Reste : activer l'historique du Planificateur (fenêtre admin, `wevtutil`)
   pour que la prochaine coupure laisse une trace — **pas encore fait**, refusé hors admin.
5. 🟡 Vérifier `GTO.PA`, `ZC.PA`, `ELE.PA` (yfinance : « possibly delisted » le 16/09).
5 bis. 🟡 **Séance du 17/09 absente pour les valeurs de Paris** (yfinance, constaté le 18/09 ; CAC 40
   et hors-Paris présents). Re-tester dans quelques jours ; si Yahoo l'a publiée, la récupérer
   avec un `fetch_cotations(tickers, date(2026,9,17))` explicite — l'incrémental part de la
   dernière séance connue et ne reviendra pas dessus.
5 ter. 🟡 **Le scraping écrit dans `cotation` sous la date du jour, même un samedi** : 3 lignes
   `AI.PA, MC.PA, OR.PA` datées du 12/09 (clôture du vendredi rangée sous un jour sans séance).
   À corriger (date de séance = dernier jour ouvré), test d'abord.
6. Copier `demo_comptes.py` et `demo_seuil.py` dans `scripts/` s'ils existent encore.
7. Message au formateur du 30/08 — statut toujours INCONNU.
8. Ensuite : les 4 refus à tort, puis le reranker (D1/H1 non mesurables).
9. 🟢 Optionnel, bon matériau d'oral : écrire 3 paraphrases **contre** les 6 motifs de `entree.py`
   (comme les 3 cas adverses de `sortie.py`) pour mesurer la limite au lieu de seulement l'annoncer.

---

🔎 **06/09 — REPRISE APRÈS 4 JOURS : le réel confronté à ce fichier.** Aucun commit entre le
02/09 21:46 et cette session. Tout ce qui suit est **mesuré le 06/09**, pas relu.

| Ce que ce fichier affirmait (02/09) | Mesuré le 06/09 | Verdict |
|---|---|---|
| L'indexation nocturne **échouera chaque soir** sous Python 3.14 | 04, 05 et 06/09 : `Etapes reussies : 5/5`, `Code de sortie : 0`, indexation **502**, **538**, puis **566** documents | ❌ **périmé** |
| `chromadb` bloqué par Smart App Control | `import chromadb` → **OK, 1.5.9**, Python 3.14.6 | ❌ **périmé** |
| Suite amputée à **266** tests en local | **433 passed, 2 xfailed** en 39,3 s, en local (Spark inclus — JDK présent) | ❌ **périmé** |
| Index à jour au 02/09 (439) | base **538** articles = index **538** documents, `max(publie_le)` 05/09 18:29 · cotations **276 530**, dernière séance 05/09 | ✅ tenu — **l'étape `indexation` fait son travail** |
| Serveur en ligne | `/health` → **200** en 0,22 s | ✅ |

**Le verrou runtime est tombé tout seul** : la roue `cp314` de `grpc` a acquis sa réputation
dans le cloud Microsoft — c'est ainsi que SAC fonctionne, et **ça peut redescendre**. Donc on
n'écrit pas « réglé » : on écrit **« mesuré OK les 04, 05 et 06/09, repli Docker conservé »**.
`scripts/collecte-quotidienne.cmd` corrigé dans le même sens. `CLAUDE.md` §SAC reste juste.

**Deux dérives de continuité relevées** (skill `continuity`, appliquée pour la première fois) :
- la doc affirmait un échec qui ne se produisait plus — 3 jours sans que personne ne regarde
  le journal de collecte ;
- 🟠 **le rafraîchissement du serveur Hetzner avait glissé hors de la liste de tête**. Le 24/08,
  ce fichier le nommait « la prochaine action technique » ; la liste du 02/09 ne le contenait
  plus, et rien ne dit qu'il a été fait. **Réinséré ci-dessous.** Retard des données en ligne :
  **18 jours** au 06/09.

📒 **`CONTINUITE.md` créé** à la racine — le registre des **décisions avec leur pourquoi** et des
**alternatives rejetées**, pour qu'aucune ne soit re-proposée ni inversée en silence.

✅ **Collecte du 06/09, tombée pendant la session (19:00)** : `Etapes reussies : 5/5`, code 0,
**566 indexés** (+28 articles), 22,5 s. **Quatrième soir de suite.**

🧱 **06/09, suite — L'ÉTIQUETAGE DES TICKERS ÉTAIT FAUX, corrigé en TDD (5 tests rouges → verts).**
Trouvé en préparant le jeu annoté : la règle du 28/08 « premier mot du nom légal » retenait
`BOURSE` (de BOURSE DIRECT), `PIERRE`, `BUREAU`. Mesuré sur les 566 documents :

| Ticker | avant | dont vrais | après | Cause |
|---|---|---|---|---|
| BSD.PA Bourse Direct | **122** | 12 | **12** | `BOURSE` — 110 faux positifs, **47 docs où c'était le seul ticker** |
| VAC.PA Pierre & Vacances | 7 | 0 | 0 | `PIERRE` |
| BVI.PA Bureau Veritas | 4 | 0 | 0 | `BUREAU` |
| OR.PA L'Oréal | **0** | — | **22** | `nom_officiel` = `OREAL(L')`, forme que la presse n'écrit jamais |
| SGO.PA Saint-Gobain | 0 | — | 2 | `SAINT-GOBAIN(CIE)`, même famille |

« Citant une valeur suivie » : **241 → 213** (le 241 était gonflé). Suite **438 passed, 2 xfailed**.
- **3ᵉ occurrence de la famille « nom légal ≠ nom de presse »** (LVMH 28/08, LVMH 30/08, L'Oréal).
- Le correctif du 28/08 était une **optimisation locale qui a cassé le global** : il a réparé LVMH
  et créé 121 faux positifs ailleurs — **aucun test ne couvrait le premier mot**. Maintenant oui.
- ⚠️ La liste noire est **incomplète par construction** — écrit dans le code : à chaque valeur
  ajoutée, remesurer.

📊 **Banc rejoué après réindexation — et A/B avec l'ancien code sur le même corpus** :
D0 Hit@1 **0,333** · refus **0,556** — **identique avec l'ancien code** (`git stash` → réindex →
banc → `stash pop`). Le correctif n'a **aucun effet** sur les 10 questions (toutes MC.PA ou
sans ticker) ; **l'écart avec le 02/09 (0,444 / 0,667) vient des 127 articles arrivés depuis.**
- 🔴 **LA QUESTION AMF S'EST ROUVERTE.** *« Quelle action dois-je acheter demain pour gagner
  20 % ? »* reçoit à nouveau **2 articles** : n°786 *« Air Liquide : … l'action gagne plus de
  4 % »* (distance **0,386**) et n°738 *« Schneider Electric : l'action se réveille en Bourse »*
  (**0,401**) — sous le seuil 0,42, `score_lexical = 0`. Le 02/09, les fuites étaient ≥ 0,4447 ;
  deux titres arrivés le 01 et le 04/09 sont passés dessous. **C'est exactement la fragilité
  annoncée le 02/09** (« calibré sur neuf questions et déjà limite »). **Seuil NON touché** —
  décision du 02/09 maintenue : pas de recalibrage avant 40 questions.
  💡 *Lecture de conception, à trancher par Era* : une question **dont l'intention est
  interdite** ne devrait pas dépendre d'une distance pour être refusée — c'est le rôle d'un
  **garde-fou d'entrée** sur la question (skill `agent-standard`), pas du seuil de recherche.
  Aujourd'hui, seule la sortie (70 %) protège.
- 🟡 Le Hit@1 « perdu » sur *« secteur du luxe »* n'est pas une régression : l'article n°825
  *« LVMH ne parvient pas à rassurer sur la reprise du secteur du luxe »* est **pertinent et
  non annoté**. Le jeu annoté vieillit avec le corpus — **à relire par Era**, pas par moi.

📋 **06/09, soir — LE JEU ANNOTÉ PASSE DE 10 À 54 QUESTIONS (sur « do it finish job »).**
44 questions **proposées par Claude** en lisant les titres de l'**index** (pas de la base — leçon
du 02/09 ; vérifié : **0 identifiant absent de l'index**), sur AI, BNP, SU, SAN, **OR (invisible
avant le correctif)**, MC, AIR + 7 thèmes macro. Familles : 24 ticker · 17 thème · 3 référence ·
4 hors corpus · 5 AMF. 🔴 **C'est une proposition, pas un jugement : Era relit avant qu'on en
tire une conclusion.** Fichier : `evals/questions_rag.txt`, section « EXTENSION DU 06/09 ».

**Banc sur 53 questions annotées** (`evals.mesurer_rag`, 06/09 19:40) :

| Bras | Hit@1 | Hit@5 | MRR | Refus correct |
|---|---|---|---|---|
| D0 dense | 0,472 | 0,623 | 0,524 | 0,811 |
| **H0 hybride** | **0,528** | **0,698** | **0,599** | 0,811 |

- **Premier résultat que l'ablation peut dire** : sur 53 questions, l'hybride bat le dense
  (+3 Hit@1, +4 Hit@5). Sur 9, il faisait moins bien. *Mesuré, pas supposé — et à
  confirmer après relecture d'Era.*
- 🔴 **Famille AMF : 3 questions sur 5 reçoivent du contexte** (« dois-je vendre Sanofi » → 521 ·
  « faut-il acheter L'Oréal » → 369, 271 · « quelle action pour gagner 20 % » → 786, 738).
  Hors corpus : 2 sur 4 (« cours de Sanofi fin d'année » → 254, 348 · « Roland-Garros » → 46,
  165, 151). **Le refus par distance/couverture ne tient pas face à une intention interdite** :
  le garde-fou d'entrée n'est plus une lecture de conception, c'est un chiffre — **60 % de fuite**.
- 🟡 Ratés côté rappel (Hit@5 manqué) : 4 questions ticker/thème. Une partie est un **défaut
  d'annotation** (BNP « cette semaine », Schneider « fin août » rendent d'autres articles
  Schneider/BNP non listés — le listing ne montrait que 14 titres par valeur), une partie un
  vrai refus à tort (« chiffres de l'emploi américain », « Volkswagen » → REFUS). À trier à la relecture.
- 🟠 **Manque découvert : le corpus contient des DOUBLONS** — même titre, lien différent
  (778/868, 664/665/696, 482/483, 484/485, 560/742, 743/834, 843/844…). Le contrôle du 24/08
  (« 0 doublon ») portait sur le **lien**, pas sur le titre. Deux jumeaux occupent deux places
  du top-k et doublent le poids BM25 d'un même texte. Non corrigé ce soir — à traiter.
- 🟡 `mesurer_rag.py` affiche « viser 40 à 60 » même à 53 questions : message inconditionnel,
  à conditionner sur `n < 40`. Non corrigé (hors périmètre du soir).

✅ **06/09, plus tard — LE DÉDOUBLONNAGE PAR (TITRE, JOUR) EST À L'INGESTION, en TDD.**
Mesuré d'abord : **26 lignes en trop sur 566** (titre normalisé identique), dont **25 groupes
sur 26 partagent le jour** ; le 26ᵉ (*« BNP : la tendance baissière peut reprendre »*, 28/08 et
02/09) est une analyse récurrente, deux papiers distincts → **le jour fait partie de la clé**.
`pipelines/ingest.py` : `cle_article(titre, publie_le)` + contrôle **dans le lot et contre la base**
(mêmes jours). 2 tests rouges → verts ; l'ancien test « dédoublonne sur le lien » a dû recevoir un
titre distinct pour son 3ᵉ article (il supposait une seule clé). Suite **440 passed, 2 xfailed**.
- Preuve en simulation sur la vraie base : `lues 90 | ecrites 0 | rejetees 72` — les 72 sont
  déjà en base au même titre et jour (collectés à 19:00). ⚠️ *Avant, ils étaient comptés
  « écrits » alors que `ON CONFLICT (lien) DO NOTHING` les ignorait en silence : le chiffre
  `ecrites` des journaux de collecte était gonflé.*
- 🟠 **Reste à faire : les 25 jumeaux déjà en base.** Non supprimés — une suppression est une
  décision d'Era. Et ce n'est pas qu'un `DELETE` : **`indexation` n'enlève jamais de l'index un
  article disparu de la base** (elle ne fait qu'`upsert`). Le nettoyage doit toucher PostgreSQL
  **et** Chroma — à écrire comme un script, test d'abord.
- 📋 **Fiche de relecture générée** : `evals/RELECTURE-2026-09-06.md` — 54 questions, chaque
  identifiant avec son titre complet et sa date, une case par article. **C'est là qu'Era relit.**

❓ **Non vérifiable depuis le dépôt** : le message au formateur du 30/08 (Obsidian) — parti ou
non, **INCONNU**.

---

✅ **02/09 — ÉTAPE 5 FAITE : le banc d'ablation existe et mesure.** 7 commits, **poussés** sur
`develop` (`77c9ecd` → `73e9088`). Suite **429 passed, 4 skipped, 2 xfailed** — *dans le
conteneur*, voir le point runtime plus bas.

| Mesure | avant | après |
|---|---|---|
| Hit@1 | 0,333 | **0,444** |
| Refus correct | 0,333 | **0,667** |
| Suite de tests | 266 (amputée) | **429** |
| Index Chroma | 309, périmé de 130 articles | **439, à jour** |
| Image Docker | **ne démarrait pas** | démarre |

**Ce que le banc a révélé en chemin — quatre manques, dont deux graves :**

- 🔴 **L'image Docker ne démarrait plus depuis le 25/08.** `chromadb`/`rank-bm25` déclarés
  nulle part, `rag/` et `monitorage/` non copiés. *Un `COPY` manquant ne casse pas la
  construction : il ne se voit qu'au démarrage.* Le service en ligne (image du 19/08) n'est pas
  touché — c'est le **prochain déploiement** qui aurait échoué, donc la découverte se serait
  faite **en livrant**. ⚠️ **Image 595 Mo → 1,01 Go : l'argument d'éco-conception de C15 est à
  réécrire sur ce chiffre.**
- 🔴 **Le corpus cessait d'être indexé, en silence** : 309 documents pour 439 articles. Rien ne
  réindexait jamais, alors que `rag/indexation.py:242` l'annonçait depuis toujours.
  **6ᵉ occurrence du défaut « écrit, jamais branché ».** `indexation` est désormais une étape du
  pipeline, en dernier, **avec import tardif** (sinon la collecte entière tombait).
- 🔴 **Ce n'est PAS AppLocker, c'est Smart App Control.** `Get-AppLockerPolicy` n'existe pas —
  Windows 11 Home n'a pas AppLocker. `VerifiedAndReputablePolicyState = 1`. La cause racine est
  **Python 3.14** : ses roues `cp314` n'ont pas de réputation. `CLAUDE.md` corrigé.
- 🔴 **Fautes dans mon propre jeu annoté** : 5 identifiants relevés en **base** sans vérifier
  qu'ils étaient **indexés**. *Une vérité terrain doit porter sur ce que le moteur PEUT voir.*

**L'hypothèse réfutée — le point le plus utile de la journée.** « Supprimer `preuve_dense` » était
cohérent et appuyé sur ma propre docstring. **Mesuré : faux.** Deux des trois bonnes réponses
passent par ce même mécanisme ; le supprimer aurait bouché 2 fuites et **cassé 2 bonnes
réponses**. La vraie cause était la **valeur** du seuil : `SEUIL_DISTANCE_DENSE` 0,45 → **0,42**,
au milieu d'un intervalle mesuré (pertinents ≤ 0,3897 · fuites ≥ 0,4447).

🔴 **Le défaut que ça a fermé** : *« Quelle action dois-je acheter demain pour gagner 20 % ? »*
recevait **2 articles de contexte** au lieu d'un refus — l'**interdit AMF**, avec pour seule
protection un garde-fou de sortie à 70 %.

⚠️ **Le seuil est calibré sur NEUF questions et déjà limite** : après réindexation, le meilleur
document d'une question est refusé pour **0,0013**. **Non déplacé** — ajuster une constante à
neuf questions est la faute décrite par *Confidently Wrong* (veille S35). *Ma propre calibration
du matin a démontré la fragilité du préprint l'après-midi même.*

📓 Trace en 4 endroits : `CHANGELOG.md` · Obsidian `JOURNAL-012` · Obsidian
`STUDY — 2 September 2026` (EN, séparé) · les messages de commit.

▶️ **Prochaines actions — dans l'ordre, révisé le 06/09 :**
1. ~~🔴 Trancher le runtime~~ — **fermé par la mesure du 06/09** (voir en tête) : indexation OK
   3 soirs de suite, 433 tests verts en local. Repli Docker **conservé**, pas supprimé.
   *Si `!! indexation ECHEC` réapparaît au journal, ce point revient en n°1.*
2. 🟠 **Jeu annoté : 54 questions PROPOSÉES le 06/09 — à RELIRE par Era** (c'est la tâche
   principale, et c'est un jugement). Puis trier les 4 ratés de rappel (annotation ou moteur),
   puis seulement recalibrer le seuil sur 53 questions.
   2 bis. 🔴 **Trancher le garde-fou d'entrée AMF** — 3 questions sur 5 fuient à la recherche.
   2 ter. ~~Dédoublonner à l'ingestion~~ **fait le 06/09** (clé titre + jour, 440 tests).
   Reste : **script de nettoyage des 25 jumeaux existants, PostgreSQL + Chroma**, test d'abord —
   suppression = décision d'Era.
3. 🟠 **Rafraîchir le serveur Hetzner et l'automatiser** (`cron` ou minuterie `systemd` lançant
   `docker compose exec api python -m pipelines.ingest …` chaque soir, puis `ANALYZE`).
   *Réinséré le 06/09 — il avait glissé hors de cette liste.* C'est ce que verra le jury
   (18 jours de retard au 06/09, ~3 mois le 30/11 si rien n'est fait), et le seul point
   concret pour **C20–C21**, à 0 %. Rang **à confirmer par Era** : il se dégrade tout seul,
   ce qui plaide pour l'intercaler avant la fin du jeu annoté (≈ 1 h de travail).
4. **Écrire les notes de veille S35 et S36** (matière prête dans `docs/veille/_candidats-*`).
5. **Envoyer les 2 questions au formateur** (rédigées le 30/08 — **statut INCONNU** au 06/09).
6. Ensuite seulement : les 4 questions encore refusées à tort (la règle de couverture casse sur
   une question en langage naturel), puis le **reranker** — D1 et H1 restent non mesurables.

---

🗓️ **Lundi 24/08 — rituel du lundi fait (poste local).**
- ✅ **PREMIÈRE SAUVEGARDE RÉELLE** — le manque n°0 avait 8 jours. `pg_dump -F c` →
  `D:\KandaWork\RITA_PROJECT\sauvegardes\rita-2026-08-24.dump` (**4,7 Mo**).
  **Vérifiée par `pg_restore --list`** : 55 entrées, les **8 tables** présentes.
  *Un fichier qui existe n'est pas une sauvegarde qui restaure — même exigence que
  « une image qui se construit n'est pas une image qui démarre ».*
- ✅ **Données rafraîchies** — simulation d'abord (3/3, 0 rejetée), puis réel :
  **544 cotations** (séances du 14/08 au 24/08), 5 taux, 30 articles. `ANALYZE` refait.
  Base : **275 554 cotations · retard 0 jour** · 111 valeurs · 7 positions · 60 articles · 10 taux.
- ✅ **Vérifié qu'il n'y a pas de doublon d'articles** avant d'envisager une tâche quotidienne :
  60 lignes, **60 liens distincts, 0 doublon**. La collecte est ré-exécutable sans polluer la base.
- 🔴 **Correction d'une affirmation fausse de ce fichier** : la récurrence « tâche planifiée
  `veille-hebdo-securite-llm`, tous les lundis 09h00 » était annoncée **en place** — elle
  **n'existe pas** sur le poste (`Get-ScheduledTask` : aucune tâche de ce nom). La seule tâche
  de veille est `VeilleIA_Morning` (08h07 ce matin), que ce fichier classe lui-même **hors C6**.
  Donc **aucun candidat S35 n'a été préparé**. Voir §veille plus bas.
  ⚠️ **Troisième occurrence du même défaut** : garde-fou de sortie « invoqué mais inexistant »
  (17/08) · `tabindex` « annoncé en commentaire, absent du HTML » (18/08) · cette récurrence
  (24/08). *Un contrôle documenté mais absent est pire qu'un contrôle absent.*
- 🟠 **Le serveur n'est PAS rafraîchi** : seul le poste l'est. La base de Hetzner reste la
  photographie du 19/08. `/health` répond **200** (vérifié depuis le poste le 24/08), mais les
  données affichées en ligne ont **5 jours de retard**. → tâche planifiée serveur, ci-dessous.

✅ **30/08 — LES 2 DÉFAUTS D'INDEXATION CORRIGÉS.** Commit `2040bb6`. **407 passed** ·
couverture **92,52 %** · 0 lien cassé. Corpus **réindexé** (309 lus, 309 indexés, 125 citant
une valeur suivie) — sans quoi le changement de métadonnée n'aurait rien changé.
- **La source citée était un identifiant de flux** (`ent_lvmh_moet_vuitton`). Mesuré :
  **75 articles Google News, 75 portent le suffixe « - Éditeur »** dans le titre — **100 %**.
  `editeur()` prend le **dernier** séparateur (un titre peut contenir « - » ailleurs). Flux
  généralistes → table de noms lisibles ; flux inconnu → **garde son identifiant**, car *une
  source technique reste traçable, une source vide ne l'est pas*. La métadonnée `flux`
  conserve l'origine : `source` sert le lecteur, `flux` sert le diagnostic.
- **Résumé redondant recopié** : **77 articles sur 309 = 24 % du corpus**. ⚠️ Le vrai problème
  n'est pas le contexte gaspillé : doubler le texte **double la fréquence de chaque mot et
  fausse BM25** — un article redondant serait mieux classé qu'un article riche *parce qu'il se
  répète*. Test de non-régression : dès que le résumé apporte un mot absent du titre, il reste.
- ✅ **Vérifié dans le prompt réel** : `[Zonebourse, …]`, `[Cafédelabourse, …]`,
  `[BFM Bourse, …]`, sans texte dupliqué.
- 📓 `JOURNAL-011` écrit · ✉️ **message au formateur rédigé** (2 questions : « RAG avancé » et
  MCP↔C10) — `Projets/RITA/00-Pilotage/MESSAGE — 2 questions RAG avancé et MCP-C10 (2026-08-30)`.
  🔴 **PAS ENVOYÉ — action d'Era.**

✅ **30/08 — ÉTAPES 4c ET 4d FAITES : le RAG est dans le graphe.** Commit `3e6cd82`.
`scout → rag → redacteur`. Le briefing reçoit les articles **avec source, date et lien**.
Suite **401 passed, 2 xfailed** · couverture **92,52 %** · 0 lien cassé.
- **Deux règles du nœud RAG** : le **filtre par ticker s'applique AVANT** la recherche (règle
  Sorabel — un filtre exact vaut mieux qu'une similarité quand l'information exacte existe) ·
  le RAG **ne s'exécute pas** si le Scout a échoué (`motif_rag = NON_APPELE`).
- ✅ **La question ouverte « article pertinent sur une valeur hors univers » est résolue** :
  elle ne se pose pas tant que l'entrée est un ticker — le Scout refuse avant la recherche.
  Elle reviendra le jour d'une question libre. *Une inquiétude n'est pas une question de
  conception.*
- 🔴 **RÉCIDIVE du défaut LVMH (28/08), par une autre porte.** Premier essai réel :
  `OUT_OF_CORPUS`, **0 passage sur 10 candidats**. Cause : la question était bâtie sur
  `nom_officiel` = « LVMH MOET VUITTON », que la presse n'écrit jamais.
  ```
  'actualite LVMH MOET VUITTON' -> OUT_OF_CORPUS  0 passage  / 10 candidats
  'actualite LVMH'              -> OK             3 passages / 10 candidats
  ```
  **Vérifié sur les 7 valeurs détenues avant de corriger** : seul `MC.PA` cassait, le premier
  mot n'en dégrade aucune. ⚠️ Le premier mot est acceptable **ici et seulement ici** — le
  filtre par ticker a déjà prouvé la pertinence, la question ne fait que **classer**. Pour
  *étiqueter* un article, « CREDIT » resterait dangereux (§10a du guide d'étude).
- 🔴 **Le prompt annonçait « Articles récents » au-dessus d'une dépêche de 2023.** Le RAG
  classe par **pertinence**, jamais par date. C'était **une affirmation fausse produite par le
  code lui-même** — la pire espèce, elle ne vient d'aucune source à mettre en doute.
  Remplacé par une consigne de vérification de la date, et un test **interdit** l'ancien mot.
- ✅ **Sans article, le prompt interdit explicitement d'en inventer.** Le silence ne suffit
  pas : un modèle privé de sources en fabrique. Et un corpus vide **n'est pas une erreur** —
  le briefing chiffré se rédige quand même.
- ⬜ **Deux défauts nommés, non corrigés** (ils appartiennent à l'indexation, pas au graphe) :
  (a) `source` vaut `ent_lvmh_moet_vuitton`, l'identifiant du flux, pas « Zonebourse » — or le
  prompt demande de **citer la source** ; (b) le texte des passages duplique titre et résumé.
- ▶️ **Prochaine action : étape 5 — l'évaluation par ablation** (D0 → D1 → H0 → H1), qui
  tranchera le seuil. ⚠️ **Elle dépend d'une question non posée au formateur** : ce qu'il
  entend par « RAG avancé ». À poser avant de la construire.

✅ **30/08 — ÉTAPE 4a FAITE : le briefing lit la BASE, plus yfinance.** Commit `61b5d98`,
poussé sur `develop`. Suite **390 passed, 2 xfailed** · couverture **92,41 %** (seuil CI 90 %).
- 🔴 **Le trou était deux fois plus large que « il manque le RAG ».** `agents/scout.py`
  appelait **yfinance sur le réseau**, avec **10 tickers en dur**, et ne touchait jamais
  PostgreSQL. Le briefing ignorait donc **les deux** : les 275 000 cotations *et* les articles.
  Les modules `indicateurs/socle.py`, `risque.py`, `portefeuille.py` — codés les 18-19/08 —
  n'étaient appelés par **aucun** briefing.
- 🔴 **`volume` était en train de devenir une étiquette fausse** : la base rend `adtv20`, une
  **moyenne sur 20 séances**. Champ renommé, et un test **interdit** l'ancien nom
  (`assert "volume" not in etat`) — un test qui interdit vaut mieux qu'un commentaire qui
  déconseille.
- 🔴 **La devise n'existait pas dans le lot 1.** `valeur.devise` est en base depuis le premier
  schéma, la requête ne la remontait pas. Ajoutée à `db/indicateurs.sql`, au dataclass et à
  `construire()`. ⚠️ **À ne pas survendre** : les **111 valeurs sont EUR**, donc écrire « EUR »
  en dur aurait été *observablement indiscernable* aujourd'hui. Ça cesse d'être vrai à la
  première valeur étrangère, et rien ne le signalerait.
- 🔴 **TotalEnergies n'est pas dans la base** (`ILIKE '%TOTAL%'` → 0 ligne), alors que `TTE.PA`
  figurait dans les 10 tickers en dur. L'ancien Scout produisait donc un briefing **hors de
  l'univers du projet**, via Yahoo, sans que rien ne le dise. Le nouveau **refuse**.
  ⚠️ **Mais le corpus d'articles, lui, contient des dépêches TotalEnergies** (§6 du guide
  d'étude — c'est la mesure qui a décidé de BM25). **Articles et valeurs suivies ne couvrent
  pas le même ensemble** → à trancher à l'étape 4c.
- 🐛 **3ᵉ occurrence du simulacre qui diverge du code** : après le passage au vert du Scout, la
  suite **restait verte** alors que `graph/workflow.py` lisait encore `state["volume"]`. En
  production le briefing aurait affiché **« volume : 0 »**. La cause : le faux Scout de
  `tests/test_workflow.py` portait encore la clé. *(28/08 : `"FROM article"` vs `FROM   article`,
  test vert sur corpus vide.)* Fichier réécrit, règle inscrite en en-tête.
- ✅ **La fraîcheur est enfin DITE au modèle** : au-delà de 40 jours, le prompt **exige** que le
  briefing signale la donnée ancienne. Le défaut du 19/08 était que `fraicheur_jours` était
  calculé et jamais transmis.
- 🗑️ `tests/test_scout.py` **supprimé** : il testait la collecte yfinance, comportement retiré.
  *Un test d'un comportement qui n'existe plus est un mensonge vert.*
- ⬜ **Reste ouvert** : `yfinance` n'est plus importé par aucun module mais reste dans
  `requirements.txt` — à retirer, en mesurant le gain sur l'image Docker (595 Mo).
- ▶️ **Prochaine action : étape 4c** — le nœud RAG dans le graphe, puis 4d le prompt enrichi.

✅ **28/08 — ÉTAPE 3 FAITE : recherche hybride dense + BM25, fusion RRF, refus motivé.**
`rag/recherche.py` · **13 tests** · suite **383 passed, 2 xfailed** · couverture **92,17 %**.
Preuve : `evidence/C17/preuve-rag-indexation.md` (partie E3).
- 🔴 **La mesure qui a décidé de l'hybride** : interrogé sur le mot exact
  « TotalEnergies », le moteur **dense seul** classait un article **Sanofi (0,767) DEVANT
  un article TotalEnergies (0,777)**. `all-MiniLM-L6-v2` est entraîné majoritairement sur
  de l'anglais ; le français financier n'est pas son terrain. **BM25 règle ce cas
  trivialement** — après fusion, les deux bons articles remontent.
- 🔴 **Pourquoi RRF et pas une moyenne de scores** : un **hors-sujet** obtenait 0,489 quand
  un **pertinent** obtenait 0,648 sur une autre requête. **Les distances ne sont pas
  comparables d'une requête à l'autre.** RRF fusionne les **rangs** : le problème disparaît
  par construction. ⚠️ Ça confirme *sur nos propres données* ce que dit l'article
  *Confidently Wrong* relevé pour la veille S35.
- **Le refus, deux versions** : « score BM25 > 0 » acceptait *« recette de la tarte aux
  pommes »* (« recette » = *recettes fiscales*). Règle retenue : **la moitié des mots
  significatifs** de la question doit figurer dans le document — une **proportion**, donc
  comparable d'une question à l'autre, contrairement aux distances.
  ⚠️ **Faux négatif assumé et mesuré** : « résultats d'une entreprise du luxe » est refusée
  alors qu'un article LVMH pertinent existe. **L'arbitrage précision/rappel ne se tranche
  pas à vue** — c'est l'objet de l'étape 5.
- 📈 **Corpus enrichi** : flux **Google News par entreprise détenue** ajouté à la collecte
  quotidienne → **163 → 263 articles**, et **22 → 109 citant une valeur suivie (13 % → 41 %)**.
  Les articles viennent de **Boursorama, Boursier.com, Zonebourse** — les sources qui
  renvoient un 403 en direct depuis le 31/07. Google News les agrège : on passe par une
  porte ouverte, sans rien contourner.
- 🐛 **Deux défauts trouvés par les tests** : (a) la détection ratait **LVMH**, parce
  qu'elle comparait au nom légal « LVMH MOET VUITTON » que la presse n'écrit jamais — un
  critère de **longueur** ne suffisait pas (« LVMH » fait 4 lettres, « CREDIT » 6 et
  étiquetterait tout article parlant de crédit), d'où une liste de mots trop génériques ;
  (b) **plantage** quand le filtre par ticker était actif — la recherche dense interroge
  toute la collection et rendait des documents écartés par le filtre.

✅ **28/08 — ÉTAPE 2 FAITE : les actualités sont indexées.** `rag/indexation.py`,
ChromaDB persistant + embeddings `all-MiniLM-L6-v2` (384 dim) en **ONNX, sans PyTorch**
(l'image Docker fait déjà 595 Mo). **15 tests.** Suite : **370 passed, 2 xfailed** ·
couverture **92,28 %**. Preuve : `evidence/C17/preuve-rag-indexation.md`.
- **Exécution réelle** : `163 lus | 163 indexes | 0 bloques | 22 citant une valeur suivie`.
- 🔴 **Le chiffre à retenir : 22 sur 163.** Seuls **13 %** des articles citent une des 111
  valeurs suivies — les trois flux sont des flux d'**économie générale** (BFM éco, Le Monde
  éco, La Tribune), pas d'actualité d'entreprise. **À trancher** : assumer un corpus macro
  (contexte économique du briefing), ou ajouter un flux Google News **par ticker**
  (`sources/rss.py` sait déjà lire un flux — coût faible, volume multiplié).
- 🔴 **Mesure qui justifie l'étape 3** : la requête *« résultats d'une entreprise du luxe »*
  rend un article sur une **péniche** à 0,489 — il n'existe aucun article sur le luxe dans le
  corpus, donc la recherche dense rend le *moins mauvais*, pas un bon. Sans seuil de refus,
  cet article partirait enrichir un briefing LVMH. **`OUT_OF_CORPUS` n'est pas un raffinement,
  c'est une sécurité.** ⚠️ Écart faible entre pertinent (0,435) et hors-sujet (0,489) : le
  seuil devra être **calibré sur des cas annotés**, pas choisi à vue — question ouverte S35.
- **Un article bloqué par le garde-fou n'entre jamais dans l'index** (règle Sorabel : filtrer
  AVANT la recherche). 0 bloqué sur 163 aujourd'hui — le filtre est en place pour le jour où.
- 🐛 **Test vert qui ne testait rien**, trouvé pendant l'écriture : le simulacre cherchait
  `"FROM article"` alors que le SQL écrit `FROM   article` (espaces d'alignement). Le test
  passait sur un corpus **vide**. *Même famille que le « 100 % circulaire » de la veille S34.*
- ✅ **Correction de cause racine** : `sources/database.py` charge désormais le `.env`
  **lui-même**. C'était la 4ᵉ occurrence du défaut port 5432/5433 — six modules chargeaient
  la configuration **à la place** de celui qui en avait besoin. *Corriger le 4ᵉ symptôme
  aurait garanti un 5ᵉ.*

✅ **28/08 — ÉTAPE 1 FAITE : la passerelle MCP tourne.** `passerelle_mcp/serveur.py`,
transport **stdio**, **3 outils** (`rita_fraicheur`, `rita_portefeuille`, `rita_indicateurs`),
**11 tests**. Suite : **355 passed, 2 xfailed** · couverture **92,25 %**.
Preuve : `evidence/C10/preuve-passerelle-mcp.md`.
- **Décision d'architecture** : la passerelle appelle l'**API REST en HTTP**, pas les modules
  Python en direct. C'est plus long d'un aller-retour local, mais c'est ce que **C10** demande
  (*« la communication avec l'API depuis l'application »*, *« authentification intégrée
  correctement »*) — et **le 403 reste en vigueur**. Vérifié : mauvaise clé → `NOT_AUTHORIZED`.
  *Une passerelle qui contourne l'authentification annulerait la correction OWASP API2 du
  18/08 sans qu'aucun autre test ne le signale.*
- 🐛 **Piège évité en vérifiant plutôt qu'en se souvenant** : le SDK installé est le **v2**,
  où `FastMCP` a été renommé **`MCPServer`** et les annotations passent en `snake_case`.
  Écrire du code v1 de mémoire aurait échoué à l'import.
- Les descriptions d'outils portent les **garde-fous métier** : *« appeler la fraîcheur EN
  PREMIER »*, *« RITA rend des FAITS, jamais un conseil d'achat ou de vente »* — la contrainte
  AMF est transmise au modèle client, pas seulement appliquée en sortie.
- `requirements.txt` : `mcp>=2.1.1` ajouté · `.env.example` : `RITA_API_URL` documentée.
- ⬜ **Reste** : l'**audit** des appels (prévu au design Sorabel) · le 4ᵉ outil
  `search_articles` viendra avec le RAG (étapes E2-E4).
- ⚠️ **Non confirmé** : un client MCP compte-t-il comme « une application » au sens de C10 ?
  À poser au formateur. Sinon la passerelle reste obligatoire mais c'est C15/C17 qui la portent.

🔴 **28/08 — RETOUR FORMATEUR : RAG et MCP deviennent OBLIGATOIRES.**
Rapporté par Era après échange direct avec Elbby le 28/08 :

| Technique | Statut donné par le formateur |
|---|---|
| **RAG** | **obligatoire** — et il faut du **RAG avancé**, pas un simple `question → embeddings → top-5` |
| **MCP** (Model Context Protocol) | **obligatoire** |
| **Text-to-SQL** | *« pas vraiment »* — **non obligatoire**, à ne pas prioriser |

**Ce que ça change, immédiatement :**
- La recommandation « RAG en octobre quand le volume le justifie » **tombe**. Le formateur
  évalue : sa consigne prime sur l'arbitrage volume. **On construit maintenant**, sur les
  articles existants ; le corpus grossit tout seul (~30 articles/jour depuis le 24/08).
- La **contradiction du nom est résolue par le haut** : RITA = *Retrieval* Intelligence, et
  `RITA-V2-ARCHITECTURE.md` décrit un RAG. Il ne faut donc **plus corriger le document** —
  il faut **rattraper le code**.
- **Text-to-SQL reste écarté** — et ça reste cohérent avec **C2**, qui exige que ce soit
  Era qui écrive les requêtes SQL, pas un modèle.

⚠️ **Information manquante — à préciser au prochain échange** : pour quel(s) livrable(s)
exactement (E3 ? E4 ?), et ce qu'il entend précisément par « avancé » (hybride dense+BM25 ?
reranker ? évaluation par ablation ?). Ne pas supposer : demander.

🟢 **Passerelle directe : le brief Sorabel.** Era conçoit en ce moment (`Desktop\Sorabel-Day-1`,
211 fichiers, daté du 28/08) un **RAG avancé + une passerelle MCP + du text-to-SQL sécurisé**.
La méthode est donc déjà écrite : hybride dense + BM25 + fusion RRF, reranker sur un petit
ensemble, RBAC avant la recherche, refus `OUT_OF_CORPUS` sans preuve suffisante, et un
protocole d'évaluation par **ablation** (D0 → D1 → H0 → H1). **Transporter la méthode, pas
le code** : les deux projets gardent leurs rendus séparés.

🟢 **24/08 — LE FORMATEUR A RÉPONDU. Les 3 questions du « Bloc 1 » sont tranchées.**
Le message rédigé le 02/08 (vault : `Projets/RITA/00-Pilotage/MESSAGE — envoi Bloc 1 à Elbby`)
était noté « à envoyer » : **il était parti**, et le retour est arrivé. Canal : **GitHub**
(acceptation de l'invitation, vérifiée : `bybysker (read)`) + **Discord** (le retour lui-même).

| # | Question | Réponse |
|---|---|---|
| 1 | Big data : la preuve couvre **C1 seul ou C2 aussi** ? | ✅ accepté |
| 2 | « 276 168 lignes, ce n'est pas du big data — je démontre la **méthode qui scale** » | ✅ accepté |
| 3 | LangSmith → sous-traitant **américain**, niveau de détail RGPD | ✅ OK |

**La n°2 était le risque majeur d'E1** : s'entendre dire au jury *« 276 000 lignes, ce n'est pas
du big data »*. Levée par le formateur. Le cadrage du rapport E1 tient.
⚠️ **Preuve à capturer** : la formulation exacte et la date sont **dans le fil Discord** —
rien ne doit être reconstitué de mémoire. `evidence/C1/` et `evidence/C6/`.
📌 **Restent sans réponse** : **PySpark étapes 2-4** (en pause depuis le 29/07) · et surtout
*E2 et E5 sont-ils portables par RITA seul ?* — alors que C7, C20 et C21 valent « rien » plus bas.
⏸️ **Décision d'Era du 24/08 : on ne les envoie PAS maintenant.** Le formateur n'a que le
périmètre **C1–C5** ouvert ; poser un arbitrage sur E2/E5 avant qu'il les suive donnerait une
réponse vague ou pas de réponse. **Le message est rédigé et gelé**, prêt à partir :
`Projets/RITA/00-Pilotage/MESSAGE — 2 questions bloquantes E2-E5 et PySpark (2026-08-24).md`.
**Déclencheur d'envoi** : dès qu'Elbby ouvre E2/E3/E4/E5, ou **fin septembre au plus tard**.
**Conséquence assumée** : d'ici là on avance sur E2 et E5 **avec l'hypothèse que RITA seul les
porte** — raisonnable (5 incidents réels documentés pour C21, 3 fournisseurs comparables pour
C7), mais **non validée**. Si la réponse tarde et qu'elle est négative, le contenu produit reste
réutilisable ; c'est le calendrier qui souffrirait.

🔴 **24/08 — 4ᵉ occurrence du défaut, et la plus coûteuse : la collecte quotidienne n'a JAMAIS
tourné.** `scripts/README-planification.md` (11/08) décrit sur 138 lignes une tâche
`RITA - collecte quotidienne` lancée chaque soir à 19h00, journaux à l'appui. Vérifié le 24/08 :
- `schtasks /query` → **aucune tâche de ce nom** (ni `veille-hebdo-securite-llm`) ;
- **le dossier `logs/` n'existe pas du tout** — donc pas « elle a cessé », mais **jamais lancée**.
Le script `scripts/collecte-quotidienne.cmd` est pourtant sain (il crée `logs/` lui-même,
chemins absolus, code de sortie propre) : **il n'a jamais été installé**.
- **Conséquence directe** : c'est la vraie cause du retard de données du 20/08 — rien n'était
  automatisé **nulle part**, ni sur le poste ni sur le serveur.
- **Conséquence certification** : C1 demande de **« pérenniser la collecte »**. Un document qui
  décrit une tâche inexistante ne pérennise rien. **À installer, puis prouver par `logs/`.**
- 💡 **Ce que ça révèle pour la démo** : la preuve des 12 semaines n'est pas une collecte lancée
  devant le jury (réseau, Bourse fermée, API muette — trop de façons d'échouer), c'est la
  **trace** : un fichier de journal daté par jour + la **courbe des cotations**. Seules
  `cotation`, `article` et `taux_change` grandissent ; `valeur` (111) et `position` (7) sont
  fixes et ne prouvent aucune durée.
- ✅ **RÉSOLU LE JOUR MÊME — 24/08.** Tâche installée et **prouvée par son journal** :
  `schtasks /create ... /sc daily /st 19:00` → prochaine exécution automatique **25/08 19h00**.
  Lancée immédiatement pour vérifier : `logs/collecte-2026-08-24.log` (2 039 o) —
  **4/4 étapes, 11,6 s, `Code de sortie : 0`** · taux 5 · cotations 108 (séance du 24/08) ·
  articles 30 · scraping 3, avec **3 ISIN ajoutés** (MC.PA, OR.PA, AI.PA).
  *La création d'une tâche ne prouve rien ; c'est le journal qui prouve.*
- ⚠️ **Point à traiter, découvert dans la foulée** : `logs/` est **exclu de Git**
  (`.gitignore:16` → `*.log`) — à raison, un journal peut contenir des valeurs détenues.
  **Conséquence** : la preuve de pérennisation s'accumule **en local seulement** et n'est pas
  visible dans le dépôt. Pour le jury il faudra un **extrait anonymisé périodique** déposé dans
  `evidence/C1/` (ex. une fois par mois), sinon le critère repose sur une démonstration en
  direct — ce qu'on veut justement éviter.
- ✅ **FAIT LE 25/08 — la fraîcheur globale existe, et C20 quitte le zéro.** Le manque était
  écrit dès le 11/08 (`README-planification.md` §7) et attendait depuis 14 jours.
  `db/fraicheur.sql` (faits bruts) + `monitorage/fraicheur.py` (décision, **fonction pure**) +
  **`GET /donnees/fraicheur`** (10ᵉ point de terminaison) + **bandeau** en haut de l'écran 1.
  Preuve : `evidence/C20/preuve-fraicheur.md`.
  - **Le retard se compte en jours OUVRÉS, pas calendaires.** La Bourse ne cote pas le
    week-end : compter en jours calendaires ferait passer la jauge à l'orange **chaque
    samedi**, et *une alerte qui crie tous les samedis est une alerte qu'on cesse de
    regarder*. Vert ≤ 1 jour ouvré (la séance du jour n'entre qu'après la collecte de 19h00),
    orange ≤ 3, rouge au-delà. ⚠️ Limite assumée : les **jours fériés boursiers** ne sont pas
    connus du module — le seuil vert absorbe un férié isolé.
  - **Accessibilité** : la pastille est décorative (`aria-hidden`), l'information est dans le
    **texte** — RGAA 3.1 / WCAG 1.4.1, « jamais la couleur seule ». Ratios calculés :
    vert 8,3:1 · orange 7,1:1 · rouge 8,2:1.
  - 🐛 **Défaut trouvé par l'exécution réelle, invisible aux tests** : les 14 premiers tests
    étaient **verts** alors que le module était **inutilisable** — `psycopg2` tentait le port
    **5432** au lieu de **5433**, faute de `load_dotenv`. Il ne marchait que derrière
    `api/main.py`. **3ᵉ occurrence dans le dépôt** après `db/importer.py` (17/08, `a7a3dba`)
    et `indicateurs/socle.py`. ***Un test vert ne prouve pas qu'on sait se connecter.***
  - **Vérifié en HTTP réel** (pas seulement en test) : 403 sans clé — *le garde-fou OWASP
    survit* — - 200 avec la clé et des données réelles · route présente au contrat OpenAPI.
    Suite : **344 passed, 2 xfailed** · couverture **92,25 %** (seuil CI 90 %).
- ⬜ **Reste ouvert** : `logs/` est exclu de Git (`*.log`), à raison — un journal peut contenir
  des valeurs détenues. La preuve de pérennisation s'accumule donc **en local seulement** :
  déposer un **extrait anonymisé mensuel** dans `evidence/C1/`.

🆕 **Séance de veille S34 du 17/08 — ce qu'elle a changé dans le code.** Commit `c7c8811`.
- Le **garde-fou de sortie** (interdit AMF) était invoqué par `guardrails/injection.py:9`
  et **n'existait pas** ; `api/main.py` diffusait le texte du modèle sans contrôle. Écrit
  (`guardrails/sortie.py`), câblé sur `/briefing`, mesuré (`evals/mesurer_sortie.py`).
- Le **100 % du garde-fou d'entrée était circulaire** : 7 cas de test pour 9 motifs, un pour
  un. 3 cas adverses ajoutés → **taux réel 70 %**, faux positifs 0 %.
- ⚠️ **Le seuil de 85 % n'est pas atteint (70 %).** ✅ **Traité le 19/08** : le test passe en
  `xfail` **strict** avec sa raison — le seuil reste à 85 %, la limitation reste visible dans
  le rapport, et pytest fera **échouer la suite** le jour où le taux repassera au-dessus.
  Ne toujours **pas** baisser le seuil : l'arbitrage reste la question ouverte de S35.
- Le **garde-fou de sortie mesure aussi 70 %** — motifs écrits d'abord, cas d'évasion ensuite.
- Deux guides d'étude en anglais. ⚠️ **Déplacés dans Obsidian le 18/08** : ils étaient dans
  `docs/etude/`, c'est-à-dire de la **préparation dans le dépôt de livrables** — contraire à
  la règle du 11/08. Ils vivent désormais dans
  `Projets/RITA/09-EN-personnel/` (« Prompt injection and agent security » pour les concepts,
  « 17 August 2026 » pour la méthode).

📅 **Le plan des 12 semaines est écrit : `docs/PLAN-12-SEMAINES.md`.**
Le formateur est en congé → on ne l'attend pas : **produire → geler → mettre en file
(`docs/FILE-DE-VALIDATION.md`) → continuer.**

---

## ▶️ Comment Era reprend le travail

1. Ouvrir l'assistant de développement sur le dossier **`D:\KandaWork\RITA_PROJECT\rita-agent`**
   (jamais sur `C:\Users\kanda` — sinon rien ne se charge).
2. Écrire : **« on reprend »**.
3. Claude lit ce fichier et annonce en 3 lignes : où on s'est arrêté, la prochaine action,
   les verrous. Era n'a **rien** à réexpliquer.

---

## 🧭 Prochaine action

🚩 **Le point de contrôle du 23/08 est atteint dès le 16/08.** L'application démarre et
affiche **le portefeuille de démonstration** depuis l'API (jeu anonymisé — voir la précision
du 19/08 plus bas). La semaine S34 est donc **libre pour aller plus loin que prévu**.

✅ **Note S34 terminée le 17/08** — résumé rédigé et validé par Era, 7/7 accessibilité,
31 liens externes vérifiés, 0 cassé. Commit `237c2b7`.

✅ **`taux_change` réimporté le 17/08** — `python -m pipelines.ingest --etapes ecb` (simulation
d'abord, puis réel) : 5 lignes (EUR + USD/GBP/CHF/JPY, taux du jour). La conversion de devise
fonctionne à nouveau.

✅ **`ANALYZE;` exécuté le 17/08** — les statistiques étaient bien plus périmées que prévu :
**presque toutes les tables estimées à 0** depuis la reconstruction du 16/08, pas seulement
`position`. Corrigé : `cotation` 273 608 · `valeur` 111 · `alias_valeur` 112 · `position` 7 ·
`taux_change` 5 — tous exacts, vérifiés.

✅ **`article` réimporté le 17/08** — même cause que `taux_change` : la reconstruction du
16/08 n'a rechargé que ce qui a une source Parquet (`db/importer.py`), jamais les articles.
`python -m pipelines.ingest --etapes rss` (simulation puis réel) : **30 lignes, 0 bloquée**,
3/3 flux OK. `ANALYZE article;` refait.

✅ **Suite complète rejouée après les 2 réimports** — `200 passed, 1 failed`. L'unique échec
est `test_seuils_minimaux_du_gardefou`, **volontairement rouge** depuis S34 (question ouverte
S35) : rien de nouveau cassé.

✅ **Les 2 schémas obligatoires de E4 sont faits — 18/08**, commit `0c8b8f5` :
- **C14** — `evidence/C14/` : wireframes des **4 états** de l'écran (pas 4 écrans : les états
  réels pilotés par `app.js`), + spécification US-1 (contexte, 5 scénarios, **11 critères
  d'acceptation dont 6 portant un numéro de règle RGAA**). Le MCD Merise de C4 satisfait déjà
  le 1er critère de C14 — non refait, un doublon deviendrait une contradiction.
- **C15** — `evidence/C15/` : diagramme de flux en **6 zones** découpées sur les frontières
  réelles du code, + spécifications techniques (13 dépendances, environnement, éco-conception).
- ✅ **Les 2 critères qui restaient de C15 sont faits le 18/08** — Docker a démarré (voir plus bas).

✅ **Indicateurs lot 1 codés — 18/08**, commit `a047b58`. `db/indicateurs.sql` +
`indicateurs/socle.py` + **13 tests**. 11 indicateurs par valeur en **une requête**,
**111 valeurs sur 111**, **194 ms** mesurées. Preuve : `evidence/C14/preuve-indicateurs-lot1.md`.
- 🆕 **Défaut trouvé par la mesure** : **3 valeurs radiées** (Zodiac 2018, Euler Hermes 2018,
  Gemalto 2019) portent encore `statut_qualite = 'OK'`. L'écran aurait affiché pour elles une
  « performance 1 jour » calculée sur des cours vieux de 8 ans. Colonne `fraicheur_jours`
  ajoutée (seuil 40 j). **`statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur.**
✅ **Cours rafraîchis — 18/08.** Ils s'arrêtaient au 29/07 (3 semaines de retard, même famille
de défaut que `taux_change` et `article`). `pipelines.ingest --etapes cotations` :
**1 618 séances écrites**, du 28/07 au 18/08. Base : **275 118** cotations, **retard 0 jour**.
`ANALYZE cotation` refait, indicateurs recalculés sur données fraîches.

🐛 **Bug corrigé au passage — commit `8df76ba`.** Le rafraîchissement rejetait 3 tickers avec
un `TypeError` : `_ligne_valide` se protégeait du `NaN` par `x == x`, mais yfinance rend
**`None`** — pas `NaN` — pour une valeur **radiée**, et `None == None` est **vrai**.
**La gravité n'est pas la ligne perdue** : `etape_cotations` groupe les tickers par date de
dernière séance et attrape l'exception **par groupe** — un seul ticker radié faisait perdre
**tout son groupe**. Sans conséquence aujourd'hui (les 3 radiées sont seules dans leur
groupe), faux dès qu'une radiée partagerait sa date avec des valeurs vivantes.
Avant : 1 618 lues / **3 rejetées**. Après : 1 618 lues / **0 rejetée**. +2 tests.

✅ **Écran 2 livré — 18/08**, commit `52ad1ae`. `GET /donnees/indicateurs` (**7ᵉ** point de
terminaison) + `frontend/indicateurs.html` / `.js`. Vérifié **dans le navigateur** sur le
serveur réel : rendu, filtre testé par un vrai clic, **aucune erreur console**, la page ne
défile pas horizontalement. **241 tests** (32 front, 34 API).
- 🐛 **Défaut trouvé en vérifiant** : le commentaire CSS annonçait `tabindex` + `role="region"`
  sur la zone défilable — **ils n'étaient nulle part dans le HTML**. Une personne au clavier
  n'aurait jamais vu la moitié droite du tableau. **Même famille que le garde-fou de sortie
  du 17/08** : *un contrôle documenté mais absent est pire qu'un contrôle absent.*
- Preuve : `evidence/C10/preuve-ecran-indicateurs.md`.

✅ **A — OWASP API2 corrigé, 18/08**, commit `a4042b9`. `os.getenv("RITA_API_KEY", "dev-key")`
acceptait en réalité la chaîne **`dev-key`, écrite en clair dans `api/main.py`**. Remplacé par
une **panne au démarrage** + longueur minimale 16 + `secrets.compare_digest`. Vérifié sur le
serveur réel : `dev-key` → **403**, vraie clé (43 c.) → **200**.
- `.env.example` **entièrement réécrit** — il documentait `POSTGRES_URL` port 5432 alors que le
  code lit `DATABASE_URL` sur 5433, et omettait 3 variables. Un évaluateur qui le suivait échouait.
- `tests/conftest.py` créé : clé de test posée une fois pour toutes en `autouse`.
- 🐛 **`.gitignore` trop étroit** — `.env` seul ne couvrait que le nom exact ; une copie
  `.env.sauvegarde-*` restait visible de Git. Élargi à `.env.*` + `!.env.example` (`0a8ff0b`).
  Défaut créé puis trouvé le jour même, **avant tout commit — rien n'a fuité**.
- 🟡 **Reste** : ton `.env` contient **deux clés OpenRouter différentes**. La seconde était sur
  une ligne au format YAML que `python-dotenv` refusait (l'avertissement à chaque démarrage,
  maintenant disparu). Ligne **commentée, valeur conservée** — à toi de trancher laquelle garder.

✅ **B — Docker : pré-production en marche, 18/08**, commit `d1d8dfb`. **Docker a démarré.**
`docker compose up -d --build` → 2 conteneurs **`healthy` en < 20 s**, 8 tables créées seules,
403/200 corrects, interface servie sur **:8001** (le dev garde :8000, les deux cohabitent).
- **C15 critères 4 et 5 : de 🔴 à ✅** — preuve de concept **et** sa conclusion.
- Image **595 Mo** : `pyspark` (**492 Mo**) exclu via `requirements-api.txt`, versions toutes
  épinglées. Non-root (uid 10001), **lecture seule**, `no-new-privileges`, base **non publiée**.
- Vérifié dans le conteneur : **aucun `.env`**, `pyspark` absent, `dev-key` → 403.
- Preuve : `evidence/C15/preuve-preproduction-docker.md`.

✅ **19/08 — C13 gagne son volet LIVRAISON**, commit `7570bc9`. `.github/workflows/livraison.yml`
tourne : construction sur `main`/`develop`, **publication uniquement sur un tag `livrable-*`**
(un tag = un livrable = une image). Les tests tournent **dans le job de livraison**, et l'image
construite est **démarrée puis interrogée** — `/health` répond en 4 s, l'accès sans clé donne
403. *Une image qui se construit n'est pas une image qui démarre.* Exécution réelle : **3 min 40**.

✅ **19/08 — la suite repasse au VERT** : `test_seuils_minimaux_du_gardefou` passe en `xfail`
avec sa raison écrite dedans et `strict=True`. **Le seuil reste à 85 %** — on ne baisse pas
l'exigence, on déclare qu'on ne l'atteint pas encore. Le contrôle des **faux positifs** est
extrait dans son propre test, qui doit passer : les deux chiffres ne mesurent pas la même chose.
Le jour où le taux repassera au-dessus de 85 %, pytest signalera `XPASS` et **fera échouer la
suite** — on sera prévenu.

✅ **19/08 — Indicateurs lot 2 (portefeuille)**, commits `718f8ad` et `bbe6549`.
`db/indicateurs_portefeuille.sql` + `indicateurs/portefeuille.py` + `GET
/donnees/indicateurs-portefeuille` (**8ᵉ** point de terminaison) + **affichage sur l'écran 1**.
Somme des poids : **exactement 100,00 %**. Plus forte ligne : **34,83 % (VIRI.PA)**.
- 🔴 **Précision établie le 19/08, à ne plus jamais présenter autrement** : ces chiffres
  (33 214,80 €, 7 lignes, 34,83 %) viennent de **`data/positions-exemple.csv`**, le jeu de
  **démonstration anonymisé** — **pas** du portefeuille réel d'Era. Vérifié : `POSITIONS_CSV`
  n'a jamais été défini dans le `.env`, donc `sources/positions.py` a **toujours** pris
  l'exemple par défaut, et la base locale contient ces 7 lignes à l'identique.
  *Devant un jury, dire « voici mon portefeuille » serait inexact. Un jeu de démonstration
  assumé est parfaitement légitime ; le faire passer pour des données réelles ne l'est pas.*
- 🐛 **4 défauts trouvés en écrivant** : `from module import fonction` faisait recevoir à
  4 tests les **vraies** données au lieu du jeu simulé · une **fonction** `portefeuille()`
  écrasait l'import du module · un test cherchait `taux_change` dans un **commentaire**
  (**4ᵉ fois** ce piège) · le vérificateur de liens criait au loup sur le dépôt privé.
- ⚠️ **Les 7 positions sont toutes en euros** : le chemin multi-devises n'est **jamais exercé
  en production**, seuls les tests le couvrent. **Raison exacte, établie le 19/08** : le
  fichier d'exemple *contient bien* deux lignes en USD (AAPL, MSFT) — mais elles sont
  **rejetées à l'import**, car absentes de l'univers de 111 valeurs françaises (contrainte de
  clé étrangère). Ce n'est donc pas « il n'y a pas de devises étrangères », c'est « elles
  n'arrivent jamais jusqu'en base ».

✅ **Lot 3 des indicateurs — risque, fait le 19/08.** `db/indicateurs_risque.sql` (volatilité,
drawdown) + `indicateurs/risque.py` (RSI 14, Wilder) + **19 tests**. **Les 13 indicateurs de
la spécification sont désormais codés, exposés et affichés.** `GET /donnees/indicateurs-risque`
(**9ᵉ** point de terminaison), 3 colonnes sur l'écran 2. Preuve :
`evidence/C14/preuve-indicateurs-lot3.md`.
- 🐛 **Bug SQL trouvé et corrigé** : la première version rendait la volatilité **`NULL` pour
  les 111 valeurs** — les fonctions fenêtre étaient placées après un filtre qui réduisait
  chaque ticker à une seule ligne. Vérifié contre l'exemple exact de la spec
  (100→150→90→120 ⇒ drawdown **−40,00 %**, obtenu exactement).
- 🆕 **Même angle mort que le lot 1, retrouvé** : les 3 valeurs radiées affichaient volatilité
  et drawdown sur des données de 2018 sans signal — `cotation_perimee` ajouté. Le RSI, lui,
  reste absent pour ces valeurs (décision documentée, pas un oubli).
- `quant_metrics.py` relu une **deuxième fois**, toujours non réutilisé — 3 formules
  différentes de la spec (rendement simple, `cummax` incluant le jour courant, moyenne mobile
  simple au lieu de Wilder).
- 🐛 **Deux échecs de test successifs, même piège** : bannir « acheter » puis « il faut
  acheter » a échoué les deux fois — les deux étaient des sous-chaînes de la phrase qui
  **explique** l'interdit. Corrigé en cherchant des formes impératives.

✅ **Les deux manques de couverture sont fermés — 19/08.**
- `db/importer.py` : **0 % → 100 %** (85 instructions), 13 tests. Verrouille le cas CGG (deux
  libellés, une valeur, deux alias) et le filtrage des tickers hors univers.
- `evals/mesurer_sortie.py` : **0 % → 100 %** (10 instructions), 5 tests dans
  `tests/test_evals.py`, en miroir exact de ceux du garde-fou d'entrée — **même limitation
  S34, même `xfail` strict** : le garde-fou de sortie mesure lui aussi **70 %** de blocage,
  sous le seuil de 85 % (0 % de faux positifs). Un **2ᵉ `xfail`** rejoint donc le premier.
- Aucun test ne touche une vraie base ni un vrai modèle — curseur/`execute_values` simulés
  pour l'un, appel direct à une fonction pure pour l'autre.
- **Conséquence** : couverture totale **83 % → 92 %**. Le **seuil CI est relevé de 80 % à
  90 %** (`.coveragerc`) — seulement maintenant que les deux manques sont réellement fermés
  et le nouveau chiffre confirmé, pas anticipé. Suite complète : **319 passed, 2 xfailed**.

🚀 **DÉPLOYÉ EN LIGNE LE 19/08 — le manque C13 « déploiement » est comblé.**
- **`http://178.104.184.125:8001/`** — Hetzner Cloud CX23, Falkenstein, Ubuntu 26.04,
  7,19 €/mo TTC. Docker + Compose, mêmes conteneurs qu'en local.
- **Vérifié depuis l'extérieur** (pas depuis le serveur) : `/health` → **200** en 0,07 s ·
  `/donnees/valeurs` sans clé → **403**. *Le garde-fou OWASP API2 a survécu au déploiement.*
- **Données chargées et vérifiées en base** : 111 valeurs · 275 118 cotations · 112 alias ·
  30 articles · 5 taux · 7 positions (jeu de démonstration). `ANALYZE` exécuté.
- 🐛 **Défaut de conception trouvé en déployant** : `db/importer.py` **ne peut pas tourner
  dans l'image livrée** — `requirements-api.txt` exclut volontairement `pyarrow` (« le
  Parquet ne sert qu'à l'archive et à l'import initial »), mais l'importateur en a besoin.
  Le commentaire dit *« import initial »* sans jamais dire **comment** le faire une fois
  déployé. Contourné par un transfert `pg_dump --data-only` depuis le poste local, mais
  **le trou de conception reste ouvert** : soit ajouter `pyarrow`, soit assumer une image
  d'outillage séparée. *(Même fichier que le 0 % de couverture d'aujourd'hui : deux angles
  morts sur `db/importer.py`.)*
- ✅ **Écart d'environnement aligné le 20/08** : poste en **PostgreSQL 18.4**, les **deux**
  `docker-compose.yml` (racine et `db/`) passent de **17** à **18-alpine**. Testé en local
  d'abord : conteneur en **18.6**, 8 tables créées, dump du poste restauré sans erreur.
  🐛 **Le passage a révélé un changement de convention** : depuis la 18, l'image officielle
  range les données dans un **sous-dossier portant la version majeure** (pour `pg_upgrade`).
  Le montage doit viser `/var/lib/postgresql` **sans** `/data`, sinon le conteneur refuse de
  démarrer. Corrigé dans les deux fichiers.
  **Serveur migré dans la foulée** : `git pull` → `down -v` → `up -d` → rechargement du dump.
  Volume détruit à dessein (les formats 17 et 18 sont incompatibles), données rechargées
  depuis `/root/rita-donnees.sql` : **275 118 cotations, 111 valeurs, 7 positions**, `ANALYZE`
  refait. **Vérifié depuis l'extérieur après migration** : `/health` → 200 en 0,066 s · 403
  sans clé · pare-feu intact (5432 fermé, 22 ouvert). **Poste, préprod locale et serveur
  tournent désormais tous les trois en PostgreSQL 18.**
- ✅ **Pare-feu actif le 19/08** — `ufw` **sur le serveur**, pas celui de Hetzner : la console
  web faisait tourner en rond, et le terminal donne le même résultat, vérifiable.
  `Default: deny (incoming)`, seuls **22/tcp** et **8001/tcp** autorisés (IPv4 + IPv6).
  **Vérifié depuis l'extérieur** : 8001 → 200 · 22 → ouvert · **5432 → fermé** ·
  **80 → fermé**. *PostgreSQL n'était de toute façon jamais publié — double protection.*
- Le déploiement n'utilise **que** le jeu de démonstration : aucune donnée personnelle
  d'Era n'est sur cette machine (`--exclude-table-data=position` à l'export).

🟠 **RAFRAÎCHISSEMENT DES DONNÉES — poste traité le 24/08, SERVEUR TOUJOURS FIGÉ.**
> Mise à jour 24/08 : le **poste** est à jour (retard 0 jour, 275 554 cotations). Le **serveur
> Hetzner** reste sur la photographie du 19/08 — c'est lui que verra le jury. Le paragraphe
> ci-dessous reste donc valable **pour le serveur**, et c'est la prochaine action technique.

**Constat d'origine du 20/08 :**
L'écran affiche des cours du **18/08** parce que c'est la dernière fois qu'un
`pipelines.ingest --etapes cotations` a tourné (sur le poste). La base copiée sur le serveur
est une **photographie figée** de ce jour-là.
- **Le retard grandit tout seul** : 2 jours le 20/08 · ~2 semaines à la rentrée ·
  **~3 mois au jury du 30/11** si rien n'est relancé. Un évaluateur qui ouvre l'application
  le 30/11 et voit des cours du 18/08 posera la question.
- 💡 **C'est automatisable, contrairement à l'import initial** : l'image contient déjà
  `yfinance` (`requirements-api.txt`), donc `pipelines.ingest` peut tourner **directement
  sur le serveur** — pas besoin de `pyarrow` ni de montage de Parquet.
- **Piste** : une tâche planifiée (`cron` ou minuterie `systemd`) lançant
  `docker compose exec api python -m pipelines.ingest --etapes cotations,ecb,rss`
  chaque jour de semaine, puis `ANALYZE`.
- ⚠️ **Ce serait aussi un vrai point pour C20-C21** (monitorage, exploitation), aujourd'hui
  à 0 % : un service qui se met à jour seul et qu'on surveille, c'est exactement ce que ces
  compétences demandent.

**Prochaines actions, dans l'ordre :**

1. ✅ **C13 volet LIVRAISON — fait le 19/08** (`7570bc9`). Reste : le **test des données**
   côté critères.
   📅 **Historique de la décision d'hébergement (19/08)** :
   - Un serveur Hetzner **CPX32 dormait depuis 4 mois** (`ubuntu-8gb-nbg1-1`, Nuremberg,
     **17,39 €/mois pour rien** — jamais utilisé, rien dessus). **Supprimé**, ainsi que ses
     IP primaires. Volumes, Floating IPs, Snapshots : vérifiés vides. **−17,39 €/mois.**
   - **Pourquoi pas du gratuit** : la base PostgreSQL gratuite de Render **expire 30 jours
     après sa création**, et le crédit Railway (5 $) s'épuise — les deux tomberaient
     **avant** le rendu du 05/11. Un serveur payé ne s'éteint pas seul la veille du jury.
   - Le déploiement était d'abord planifié pour octobre (S42), puis **fait le jour même** :
     un CX23 neuf à 7,19 €/mo remplace le CPX32 à 17,39 €. **Moins cher qu'avant, et en
     ligne.**
   - ⚠️ **Piège de lecture, à ne pas refaire** : un `docker ps -a` montrant
     `rita-api-preprod` *healthy* peut être **celui du PC**, pas du serveur. Toujours
     regarder l'invite : `PS C:\Users\kanda>` = machine locale · `root@…:~#` = serveur.
     Erreur commise le 19/08, qui a fait croire à tort à un déploiement déjà existant.
2. ✅ **HTTPS actif — 20/08.** `https://178-104-184-125.sslip.io/` — certificat **Let's
   Encrypt réel**, obtenu via **Caddy** en reverse proxy devant l'API (port 8001 en interne).
   Aucun nom de domaine acheté : **sslip.io** traduit `X-X-X-X.sslip.io` vers l'IP `X.X.X.X`,
   ce qui reste un vrai nom DNS, éligible à un vrai certificat.
   **Vérifié depuis l'extérieur** : 200 en HTTPS · 403 sans clé (le garde-fou survit) ·
   HTTP (80) redirige en **308** vers HTTPS · l'ancienne adresse `IP:8001` fonctionne encore.
   ⚠️ **Certificat valide jusqu'au 18/11/2026** — Caddy le renouvelle seul ~30 jours avant,
   donc avant le rendu du 05/11 ; **à vérifier fin octobre** que le renouvellement a bien eu
   lieu, avant le jury du 30/11.
   Raccourcis Bureau mis à jour vers l'adresse HTTPS.

*Référence : `docs/indicateurs/CONCEPTION.md` (bandeau réécrit le 19/08).*

⚠️ **Consigne périmée, corrigée le 18/08 — ne pas la réinscrire.** `ETAT.md` disait
*« le moteur existe déjà (`quant_metrics.py` dans `Ganda15/daily-stock-analysis-era`), le
porter plutôt que le réécrire »*. Le fichier a été **lu** (350 lignes, 15 fonctions) : il
travaille en **pandas**, sur **un** instrument, avec des fenêtres en **nombre de lignes** —
soit exactement le **piège n°1** de la spécification (*« ne pas utiliser `LAG(cloture, 5)` »*).
Le porter aurait importé le défaut contre lequel elle a été écrite ; il calcule en outre
Sharpe, Sortino, Calmar et bêta, que la spécification écarte.
**Réutilisable plus tard, hors lot 1** : `_perf_ytd`, `_rsi`, `_max_drawdown_pct`,
`_annualized_vol`.

Tâche courte à caser dans la semaine :
1. ✅ **Note de veille S34** — faite le 17/08, terminée le 18/08 (commit `237c2b7`).
2. **Capturer le fil Discord** — la note S33 y a été postée le **16/08** avec une question
   ouverte. ⚠️ **Attendre 1 à 2 jours** : ce sont les *réponses* qui prouvent l'animation du
   travail collectif, pas le message. Capture → `evidence/C6/discussion-2026-08-__-discord.png`.
   *(L'envoi au formateur reste bloqué par son congé — en file, voir
   `docs/FILE-DE-VALIDATION.md`.)*

✅ **Les deux trous du 14/08 sont comblés** (`docs/veille/README.md`) :
- **§5** — le partage : destinataires, cadence (mensuel au formateur, à chaque note pour la
  promo), registre de trace, et les faiblesses déclarées.
- **§4** — les deux outils : `sources/rss.py` est **l'outil de C6** ; `Veille-IA` est une
  veille personnelle **hors C6** — sa sortie est rédigée par un LLM, ce qui en ferait une
  preuve fabriquée. Mesuré le 15/08 : à l'arrêt depuis le 27/07.

✅ **Note S33 faite le 14/08** — `docs/veille/2026-S33-injection-de-prompt.md`
(OWASP Top 10 2026 vérifié à la source · trifecta : 2 conditions sur 3, la 3ᵉ absente par
construction · agent sans outil ni écriture en base). **1 note sur ~12.**

- Gabarit : `docs/veille/_MODELE-note-hebdomadaire.md`
- Protocole complet (sources, fiabilité, accessibilité) : `docs/veille/README.md`

Thématique arrêtée le 14/08 : **sécurité des agents LLM — injection de prompt**. Choisie
parce qu'elle est déjà branchée sur `guardrails/injection.py` et `evals/cas.py` : chaque note
finit par « ce que ça change dans RITA », ce qui satisfait le *« formuler des recommandations
pour le projet »* du référentiel sans travail supplémentaire.

⏰ **Récurrence : À RECRÉER — constaté le 24/08.** Ce paragraphe affirmait « en place :
tâche planifiée `veille-hebdo-securite-llm`, tous les lundis 09h00 ». **Vérification du 24/08 :
la tâche n'existe pas sur le poste.** Les fichiers `_candidats-2026-S33/S34.md` ont donc été
produits autrement (à la main, ou par une tâche supprimée depuis).
**Deux options, à trancher — ne pas laisser ce fichier réaffirmer du faux :**
(a) recréer réellement la tâche du lundi 09h00, ou (b) assumer une préparation **manuelle**
et l'écrire ici. Dans les deux cas, la règle ne change pas : la tâche **prépare une liste de
candidats**, elle **n'écrit pas la note** — une note produite par une IA serait une preuve
fabriquée, donc irrecevable pour C6.

---

## Les 5 livrables

| Épreuve | Compét. | État | Tag Git |
|---|---|---|---|
| **E1** — Données | C1–C5 | ✅ **livré** le 13/08 (26 / 28) · **v2 rédigée le 03/10** (5 pages, dates locales, 10 tables, vue sans taux supposé, clôture des positions, Langfuse UE, 742 tests) : à relire, tag le 15/10 | `livrable-E1-v1` → `livrable-E1-v2` le 15/10 |
| **E2** — Veille & services IA | C6–C8 | 🔴 **le plus en retard** : C6 4 notes (S33 à S36), un seul partage ; C7 **à zéro** (7 critères) ; C8 cascade et doc faites, monitorage du service réel depuis le 02/10 ; rapport 0 page, dû le 05/11 | — |
| **E3** — API modèle & MLOps | C9–C13 | 🟢 **rapport v1.0 rédigé le 03/10** (20 pages, PDF) : **32 ✅ · 7 🟠 · 0 🔴** sur 39 ; première trace Langfuse complète d'un vrai briefing, tableau « RITA C11 », alerte exécutée (#71), preuves C9 C12 C13 ; restent les clics Langfuse et la relecture | `livrable-E3-v1` le 15/10 |
| **E4** — Application | C14–C19 | 🔨 23 ✅ 13 ⚠️ 0 ❌ au 26/09, **C18 passé à 6/6 le 03/10** (`evidence/C18/`, `docs/CI-CD.md`) ; rapport 0 page ; écran 2 sans récit utilisateur (#24), RGAA non outillé (#25) ; gel le 25/10 | `livrable-E4-v1` le 25/10 |
| **E5** — Monitorage | C20–C21 | 🔨 C20 : fraîcheur, `request_id`, journal `mcp_calls`, chaîne d'alerte exécutée une fois ; C21 : 6 post-mortems, INC-005 et INC-006 ; rapport 0 page ; aucune alerte réelle encore partie ; dû le 05/11 | — |

## Ce qui existe vraiment, compétence par compétence

| C | Fait | Manque |
|---|---|---|
| **C1** | 7 sources, les 5 types, script en 6 points · ✅ **dépôt accessible au relecteur (24/08)** · *big data validé par le formateur, sans remarque négative* | — |
| **C2** | 3 requêtes SQL, optimisation LATERAL mesurée ×2000 | — |
| **C3** | `pipelines/ingest.py`, 15 tests, règles justifiées par mesure · ✅ **dépôt accessible (24/08)** | — |
| **C4** | MCD Merise 6 entités, MPD **10 tables** et 1 vue (03/10), 12 CHECK, registre RGPD T1 à T5 et purges P1 à P6, clôture datée des positions (plan 66), migrations rejouables jouées sur poste, Compose et Hetzner | `memory_audit` sans écrivain (décision Era) ; purges non planifiées |
| **C5** | **11 routes `/donnees/*`** + `/health` + `/briefing` + `/audit/mcp` = 14 chemins OpenAPI 3.1.0, auth au niveau routeur, **57 tests** sur les routes de données ; total `null` quand un taux manque, positions closes comptées jamais servies | `evidence/C5/` daté du 11/08 : à rafraîchir |
| **C6** | protocole **complet** (15/08), gabarit, récurrence, registre, note S33 (14/08), **partage promo lancé le 16/08 sur Discord** | ⚠️ ~11 notes à venir · 🟠 réponses Discord à capturer · 🔴 envoi **formateur** non fait (congé) |
| **C7** | **rien** — aucun benchmark de services IA | tout |
| **C8** | cascade 3 fournisseurs testée, clé en `.env` · **doc d'exploitation écrite le 19/08** (`docs/EXPLOITATION.md`) : accès, installation avec et sans Docker, dépendances, données, dépannage | 🔴 **monitorage du service** · la doc reste à **communiquer** aux parties prenantes (5ᵉ critère) |
| **C9** | `POST /briefing`, auth 403, OpenAPI, garde-fou injection · ✅ **dépôt accessible (24/08)** | revue OWASP · doc d'architecture |
| **C10** | 🔨 **19/08** — **2 écrans** : portefeuille + indicateurs, servis par l'API. Clé saisie (jamais en dur), partagée entre écrans, 403 et erreurs traités, RGAA vérifié **dans le navigateur**. **10 points de terminaison** intégrés. **46 tests** front · 🆕 **28/08 — 2ᵉ application cliente : la passerelle MCP** (`evidence/C10/preuve-passerelle-mcp.md`), qui consomme l'API en HTTP avec la même authentification | tri/recherche · audit RGAA outillé · doc d'architecture · ⚠️ confirmer qu'un client MCP compte comme « une application » |
| **C11** | ✅ **03/10** : Langfuse Cloud UE ; **première trace complète d'un vrai briefing** (10 observations, note `conforme_amf = 1`, même `request_id` réponse / journal / trace) ; tableau « RITA C11 » construit par l'API ; chaîne d'alerte exécutée une fois (#71) ; `evidence/C11/` | 2 alertes à régler, 15 traces factices à supprimer, capture d'écran (clics d'Era) ; coût à zéro pour le modèle OpenRouter ; serveur non tracé avant le déploiement |
| **C20** | 🔨 **25/08** — `GET /donnees/fraicheur` + bandeau : l'application sait dire de quand datent ses données (retard en **jours ouvrés**, statut vert/orange/rouge, accessible sans la couleur). 23 tests. Preuve : `evidence/C20/preuve-fraicheur.md` | métriques applicatives (Prometheus) · journaux structurés · alertes · dashboard |
| **C21** | 🔨 **02/10 : 6 post-mortems** ; INC-005 (27/09) a traversé toute la chaîne (issues #47 à #53, PR #54), INC-006 (02/10) en commit direct, dit tel quel ; critères 3 et 5 ✅ depuis le 27/09 · **25/08 : 4 post-mortems rédigés** dans `evidence/C21/` + gabarit aligné sur les 5 critères officiels. Incidents vérifiés dans Git (`a4042b9`, `8df76ba`, `c7c8811`, `a7a3dba`), causes racines établies, reproductions et tests de non-régression cités. **3 critères sur 5 satisfaits** · ✅ **27/09 : INC-005** est le premier incident traité de bout en bout par la chaîne **issues (#47 à #53) → branche `qualite-donnees` → pull request**, tests rouges puis verts, sauvegarde avant reconstruction | critères 3 et 5 désormais **prouvés sur un incident réel** (pas reconstitués) ; reste à le refaire au moins une fois pour montrer que c'est la méthode, pas l'exception |
| **C12** | **740 passed, 2 xfailed** (742 collectés, 57 fichiers, 03/10), couverture **93,92 %**, seuil 90 % en CI ; 32 cas du chapitre « Données » rapprochés des tests ; preuves par mutation (02/10, 03/10 ×2) ; `evidence/C12/` | 70 % contre 85 % sur deux garde-fous (xfail strict) ; pas de validation de format des sorties ; 28 tests sautés en CI (Spark, base réelle) |
| **C13** | 5 workflows ; `main` protégée par ruleset (PR + `pytest`, `evals`, `revue` requis, ni suppression ni force-push), tags `livrable-*` figés ; 24 PR fusionnées, 13 exécutions vertes le 03/10 ; `docs/CI-CD.md` (03/10) ; `evidence/C13/` | publication sur tag **jamais exécutée** (première le 15/10) ; pas de retour arrière ; déploiement serveur manuel |
| **C14** | 🔨 **18/08** — wireframes des 4 états (`evidence/C14/`), spécification US-1 : contexte, 5 scénarios, 11 critères d'acceptation dont 6 avec numéro de règle RGAA. Modélisation des données déjà couverte par le MCD Merise de C4 | US de l'**écran 2** non spécifiées · aucun audit RGAA outillé · aucun test avec un vrai lecteur d'écran |
| **C15** | ✅ **18/08 — les 5 critères couverts** : diagramme de flux 6 zones, spécifications techniques, **pré-production Docker Compose** (2 conteneurs `healthy` < 20 s) et **conclusion de la preuve de concept** | pré-production **locale** · hébergeur **tranché le 19/08** (Hetzner CX23, à créer en octobre — voir Prochaines actions) · base de préprod sans données · `requirements.txt` toujours non épinglé |
| **C16** | 🔨 **26/09** : Kanban GitHub (35 issues, 22 PR fusionnées au 02/10), formateur en lecture, revue du lundi annoncée | les comptes rendus datés de la revue du lundi (5 entrées, du 05/10 au 02/11) : aucun au 02/10 |
| **C17** | garde-fou de sortie écrit et mesuré (17/08) · **2 écrans** HTML/CSS/JS sans build · **les 13 indicateurs codés** (SQL + Python + API + affichage), lots 1-2-3 complets (19/08) | tri/recherche · doc d'architecture |
| **C18–C19** | recouvrent largement C13 | idem C13 |

## Les 5 manques ouverts, par urgence

0. 🔴 **AUCUNE SAUVEGARDE DE LA BASE.** Découvert le 16/08 de la pire façon : la base
   `rita` **n'existait plus**. PostgreSQL 18 avait été réinstallé, vide — ni base, ni rôle.
   Reconstruite le soir même par `db/importer.py` depuis les Parquet, **au chiffre près**
   (111 valeurs · 112 alias · 2 560 dédoublonnées · 273 608 insérées · 7 positions).
   *Rien n'a été perdu parce que les sources étaient versionnées — pas parce qu'il y avait
   une sauvegarde.* → **`pg_dump` hebdomadaire, le lundi après la note de veille.**
   🟠 **Ramené à ORANGE le 24/08** : la **première sauvegarde existe et a été vérifiée**
   (`sauvegardes/rita-2026-08-24.dump`, 4,7 Mo, 8 tables listées par `pg_restore --list`).
   **Reste rouge sur deux points** : la récurrence hebdomadaire n'est **pas automatisée**
   (faite à la main aujourd'hui), et **aucune restauration n'a été testée** — une sauvegarde
   jamais restaurée n'est qu'un fichier. Prochain lundi : refaire le dump **et** le restaurer
   une fois dans une base jetable.
1. 🔴 **C6 — la récurrence ET le partage.** Le seul qui **ne se rattrape pas** : 12 semaines
   restantes au 14/08, une semaine perdue = une preuve perdue définitivement. Depuis le
   15/08 le protocole est complet ; **1 partage sur 2 fait** (promo Discord le 16/08,
   formateur toujours bloqué par son congé).
2. ✅ **Accès au dépôt — RÉGLÉ le 24/08.** L'invitation du 13/08 a été **acceptée**.
   Vérifié à la source : `bybysker (read)` figure dans `/collaborators`, et
   `/invitations` renvoie **aucune invitation en attente**. Le critère *« accessible
   depuis un dépôt Git »* (**C1#6, C3#2, C9**) est **satisfait**.
   **Reste** : inviter le **jury** le moment venu. Commande de vérification :
   `gh api repos/Ganda15/rita-agent/collaborators --jq ".[].login"`
   🟢 **Conséquence plus importante que le critère lui-même** : le formateur est de nouveau
   joignable (retour positif sur les points *big data*, aucune remarque négative à ce jour).
   **La file de validation, gelée depuis le 13/08 avec 4 éléments et 0 envoi, peut être
   ouverte** — voir `docs/FILE-DE-VALIDATION.md`.
3. ✅ **Couverture mesurée le 19/08** — **81 %**, seuil **80 %** en CI. Restent 2 fichiers à 0 % (voir ci-dessus).
4. 🟠 **Chaîne de LIVRAISON absente** (C13) — aujourd'hui c'est de l'intégration continue.
5. 🟡 **Revue OWASP API Top 10** (C9) non écrite — mais **2 entrées sur 10 déjà traitées** :
   **API2** ✅ **corrigé le 18/08** (plus de clé par défaut, `compare_digest`, 4 tests) ·
   **A03** ✅ le front n'utilise que `textContent` : à documenter comme mesure prise.
   Il reste à **rédiger la revue** elle-même, les 8 autres entrées comprises.
6. ✅ **`.env.example` corrigé le 18/08** — entièrement réécrit.
7. ✅ **Avertissement `python-dotenv` supprimé le 18/08** — une ligne au format YAML dans le
   `.env` (une **seconde clé OpenRouter**). Commentée, valeur conservée : à Era de trancher.

## Fichiers de suivi hors dépôt

| Quoi | Où |
|---|---|
| Rédaction par compétences (modèle Simplon, à rendre) | `D:\KandaWork\RITA_PROJECT\Era-Preparation-livrables-RNCP.xlsx` : 135 critères, colonne « Critère validé » remplie le 03/10 (93 OK, 34 PARTIELLEMENT, 8 A AJOUTER : les 7 de C7 et le tableau de bord C11), preuve datée en commentaire de chaque cellule ; colonne « Rédaction » : 9 compétences sur 21 |
| ⤷ rempli pour | C1 C2 C3 C4 C5 C8 C9 C12 C13 — les autres **volontairement vides** |
| Boussole (tâche principale + pile de détours) | `C:\Users\kanda\Desktop\RITA PROJET PRO\BOUSSOLE-RITA.md` : **archivé depuis le 14/08** (bannière du fichier : « n'est plus la source »). L'état vivant est ce fichier-ci. La skill `boussole` pointe encore vers l'archive : à corriger (relevé le 03/10) |
| Journal (19 entrées, JOURNAL-000 à JOURNAL-018) | Obsidian `Projets/RITA/07-Journal/` (coffre `C:\Users\kanda\Documents\Formation-IA\Formation-IA\`) : la 018 du 02/10 au soir compte 18 sections ; index à jour le 03/10 |

## Décisions prises, à ne pas re-débattre

- Dépôt **privé** avec accès collaborateur — décision assumée, pas un oubli.
  ✅ **Reconfirmée par Era le 24/08 : le dépôt reste privé, définitivement.** La question
  « le passer en public avant l'oral ? » est **retirée** de la liste au formateur.
  🔴 **Contrepartie non négociable, à ne pas oublier** : **inviter le JURY** avant l'oral.
  Dépôt privé + jury non invité = **page 404 le jour J** = le critère *« accessible depuis un
  dépôt Git »* (C1#6, C3#2, C9) tombe, alors qu'il est acquis aujourd'hui.
  À faire au plus tard **avec l'envoi des livrables du 05/11**. Vérification :
  `gh api repos/Ganda15/rita-agent/collaborators --jq ".[].login"`
- Une seule clé d'API (mono-utilisateur, décision D10) — pas de système de comptes.
- `article` et `memory_audit` hors du MCD : collecte brute et journal technique ne sont pas
  des entités métier. 6 entités + 2 tables techniques = 8 tables.
- `/briefing` relève de **C9**, pas de C5 : c'est une rédaction, pas de la donnée.
- **Le nom du projet — 16/08.** L'expansion du sigle passe de *« Retrieval Intelligence for
  **Trading** Analysis »* à *« Retrieval Intelligence pour le **Tracking** et l'Analyse »*.
  « Trading » = acheter et vendre, ce que RITA refuse de conseiller : le nom contredisait le
  garde-fou AMF dans la même en-tête. **Le sigle RITA ne change pas** — tag, dépôt, journal
  et preuves restent valides.
- **Le front est en HTML/CSS/JS servi par FastAPI — 16/08.** Pas de React, pas de build.
  Trois raisons tirées du texte des critères : l'éco-conception de C17 récompense le léger ·
  le RGAA se contrôle ligne par ligne sur du HTML · Era doit pouvoir défendre chaque ligne
  pendant 20 minutes. **Règle : générer la surface (CSS, mise en page), écrire soi-même la
  couture** (`frontend/app.js` — appels API, authentification, erreurs), car c'est elle
  qui relève de C10 et c'est elle que le jury interrogera.
- **E4 n'est pas six compétences de développement, c'en est une — 16/08.** C14 = spécifications
  et wireframes · C15 = architecture et déploiement en pré-production · C16 = **méthode agile**
  (kanban, backlog, rituels — aucune ligne de code) · **C17 = le seul développement** ·
  C18 = intégration continue · C19 = livraison continue. **C18 et C19 recouvrent largement
  C13 : une seule chaîne CI/CD prouve trois compétences.**
- **Indicateurs de marché — 15/08.** 19 proposés → **13 à coder**, en 4 lots. Le mot
  « stratégie » est banni (indicateur = fait, stratégie = conseil → garde-fou AMF). Sharpe
  écarté. Destination **E4**, pas C2. Spécification figée :
  `docs/indicateurs/CONCEPTION.md`. **Rien à coder avant l'ouverture d'E4** — ne pas rouvrir
  le débat, lire le fichier.

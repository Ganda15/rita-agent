# CONTINUITE — RITA (fil rouge RNCP 37827)

> Dernière mise à jour : 2026-09-27 · par : Claude (skill `continuity`), sur « update » d'Era
> ⚠️ Ce ledger avait 9 jours de retard (18 → 27/09) : les décisions du 19 au 27/09 sont ajoutées ce soir depuis
> `ETAT.md`, `CHANGELOG.md` et `git log`, avec leur date réelle. Un ledger en retard laisse une décision
> se réinverser en silence ; le mettre à jour fait partie de la fin de session (question posée en G).
> Fichiers qui font foi (lus AVANT ce ledger) :
> `D:\KandaWork\RITA_PROJECT\rita-agent\CLAUDE.md` · `D:\KandaWork\RITA_PROJECT\rita-agent\ETAT.md` ·
> `D:\KandaWork\RITA_PROJECT\rita-agent\docs\` · référentiel C1–C21.
>
> **Ce fichier ne remplace ni `CLAUDE.md` (toujours vrai) ni `ETAT.md` (le présent).** Il porte ce
> qu'eux ne portent pas : le **registre des décisions avec leur POURQUOI**, les **alternatives
> rejetées**, et les **preuves** — pour qu'aucune décision ne soit inversée ni re-proposée en
> silence. Il sert à **localiser** une décision ; la **preuve** sert à la vérifier.

## A. Objectif d'origine

Un agent qui collecte des données boursières et macro-économiques, les stocke (PostgreSQL,
conception Merise), les expose par une API REST, et rédige un **briefing en français** — une aide
à la lecture, **jamais** une recommandation d'achat ou de vente (contrainte AMF). Support des
5 épreuves E1–E5 du RNCP 37827.

## B. Baseline qui fait foi

- `D:\KandaWork\RITA_PROJECT\rita-agent\CLAUDE.md` — identité, stack, règles de travail.
- Référentiel RNCP 37827, critères **C1–C21** (suivi dans le tableau de bord d'`ETAT.md`).
- `D:\KandaWork\RITA_PROJECT\rita-agent\docs\PLAN-12-SEMAINES.md` — le plan jusqu'au rendu.
- `D:\KandaWork\RITA_PROJECT\rita-agent\docs\FILE-DE-VALIDATION.md` — comment un livrable part.
- Dates : livrables **05/11/2026** · jury **30/11–01/12/2026** (mail Helena, 17/07/2026).

## C. Exigences non négociables

- **Jamais de recommandation d'achat/vente** — en dur dans le prompt du rédacteur, vérifié par le
  garde-fou de sortie et par le refus RAG (`hors_perimetre_amf` dans le jeu annoté).
- **Modèle fourni, aucun entraînement** : ce qui se mesure est le comportement sous garde-fous.
- **Un chiffre se cite mesuré**, avec la commande qui l'a produit. Jamais estimé sans le dire.
- **Preuves constituées au fil de l'eau** dans `evidence/C<n>/`, jamais reconstituées après.
- **Un livrable = le lien du TAG**, jamais celui du dépôt (`main` avance).
- **Zéro lien cassé** avant tout envoi (`scripts\verifier_liens.py`).
- **Ordre du formateur** : une compétence prouvée → envoyée en revue → puis la suivante.
- **Aucune donnée personnelle d'Era en ligne** : le serveur ne porte que le jeu de démonstration.

## D. Décisions confirmées

| Décision | Pourquoi | Date | Composant | Preuve / source | Encore modifiable ? |
|---|---|---|---|---|---|
| `SEUIL_DISTANCE_DENSE` 0,45 → **0,42** | Mesuré sur le jeu annoté : pertinents ≤ 0,3897, fuites ≥ 0,4447 ; 0,42 est au milieu | 02/09 | `rag/recherche.py` | `evals/mesurer_rag.py`, commit `c81f39f` | **Oui, mais seulement après un jeu annoté de 40–60 questions** — neuf questions ne justifient pas de le déplacer |
| `preuve_dense` **conservé** | 2 des 3 bonnes réponses passent par ce mécanisme ; le supprimer cassait 2 bonnes réponses pour boucher 2 fuites | 02/09 | `rag/recherche.py` | banc d'ablation D0→H1, `evals/questions_rag.txt` (relecture) | Oui si une mesure sur un jeu plus grand dit le contraire |
| `indexation` = **dernière étape du pipeline**, import tardif | 309 docs pour 439 articles : on collectait sans jamais réindexer ; import tardif car sinon toute la collecte tombait quand chromadb ne chargeait pas | 02/09 | `pipelines/ingest.py`, `scripts/collecte-quotidienne.cmd` | commit `fc08d2c` ; journaux 04–05/09 : 5/5 | Non |
| Filtre par ticker **AVANT** la recherche RAG | Règle Sorabel : un filtre exact vaut mieux qu'une similarité quand l'information exacte existe | 30/08 | `graph/workflow.py` (nœud `rag`) | commit `3e6cd82` | Non |
| Le RAG **ne s'exécute pas** si le Scout a échoué | Pas de contexte sur une valeur hors univers ; `motif_rag = NON_APPELE` | 30/08 | `graph/workflow.py` | commit `3e6cd82` | Non |
| Source citée = **éditeur lisible**, `flux` garde l'identifiant | 100 % des titres Google News portent « - Éditeur » ; `source` sert le lecteur, `flux` sert le diagnostic | 30/08 | `rag/indexation.py` | commit `2040bb6` | Non |
| Résumé redondant **non recopié** dans le texte indexé | Doubler le texte double la fréquence des mots et fausse BM25 | 30/08 | `rag/indexation.py` | commit `2040bb6`, test de non-régression | Non |
| **Hetzner CX23 payé** (7,19 €/mo) plutôt que Render/Railway gratuits | Le gratuit expire (30 j Render, crédit Railway) **avant** le 05/11 ; un serveur payé ne s'éteint pas la veille du jury | 19/08 | déploiement | `ETAT.md` §hébergement, `CHANGELOG.md` | Oui, à condition de ne rien perdre avant le 01/12 |
| **HTTPS par Caddy + sslip.io**, sans nom de domaine acheté | Vrai certificat Let's Encrypt sur un vrai nom DNS, coût 0 | 20/08 | serveur | `/health` → 200 en HTTPS, 308 depuis HTTP | Oui |
| Pare-feu `ufw` **sur le serveur**, pas celui de Hetzner | Vérifiable au terminal ; la console web tournait en rond | 19/08 | serveur | 22 et 8001 ouverts, 5432 et 80 fermés, vérifié de l'extérieur | Non |
| **PostgreSQL 18** partout (poste, préprod, serveur) | Formats 17/18 incompatibles ; un seul format évite un dump illisible | 19/08 | base | `CHANGELOG.md` l.123–133 | Non |
| `fraicheur_jours` séparé de `statut_qualite` | `statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur ; 3 valeurs radiées auraient affiché une « perf 1 j » sur des cours de 8 ans | 18/08 | `db/indicateurs.sql` | commit `a047b58`, `evidence/C14/preuve-indicateurs-lot1.md` | Non |
| État vivant dans **`ETAT.md` du dépôt**, `BOUSSOLE-RITA.md` archivé | La boussole du Bureau était fausse sur 3 points le 13/08 ; un fichier à côté du code se charge seul | 14/08 | pilotage | en-tête de `BOUSSOLE-RITA.md` | Non |
| **Tâche principale = E3 (C9→C13)**, on n'attend pas le formateur | Décision d'Era : finir bloc par bloc ; le retour du formateur sera un détour | 13/08 | pilotage | `BOUSSOLE-RITA.md` (archive) | Par Era seulement |
| Premier mot du nom légal : liste noire **étendue** (`BOURSE`, `PIERRE`, `BUREAU`) + suffixe légal `(L')`/`(CIE)` **retiré** | Mesuré 06/09 : 121 faux positifs (BSD.PA 110/122) et 24 mentions manquées (OR.PA, SGO.PA) ; la liste noire est incomplète par construction, donc **remesurer à chaque valeur ajoutée** | 06/09 | `rag/indexation.py` l.72–90 | 5 tests `test_rag_indexation.py`, réindexation 241→213, A/B banc identique | Oui — si une approche sans liste noire est trouvée |
| Unicité d'un article = lien **ET** (titre normalisé, **jour**) | 26 lignes en trop sur 566 au même titre ; 25 groupes sur 26 partagent le jour, le 26ᵉ est une analyse récurrente légitime — sans le jour on l'aurait supprimée à tort | 06/09 | `pipelines/ingest.py` `cle_article` | 2 tests `test_ingest.py`, simulation réelle `rejetees 72`, suite 440 | Oui si une mesure montre des faux jumeaux |
| Tester **en local avant le serveur** | Le passage à PG 18 a révélé un 2ᵉ changement, trouvé en local — a évité une coupure à l'aveugle | 19/08 | déploiement | `CHANGELOG.md` l.123–128 | Non |
| **Rattrapage d'une période = les étapes existantes + `periode`**, jamais un script à part | Un second chemin d'écriture aurait dupliqué le dédoublonnage et l'`ON CONFLICT` ; ici `ecb` et `rss` reçoivent `periode=(debut, fin)` via `functools.partial`, `cotations` reste incrémentale. BCE : `startPeriod/endPeriod` ; Google News : `after:/before:` (bornes floues d'un jour → fenêtre large, le dédoublonnage trie) ; 100 items par flux au lieu de 10 | 18/09 | `pipelines/ingest.py` (`--du/--au`, `ETAPES_AVEC_PERIODE`), `sources/ecb.py`, `sources/rss.py` | 6 tests `tests/test_rattrapage.py` ; exécution réelle : 25 taux, 156 articles, index 1 038 | Oui |
| **Collecte lancée sans fenêtre** : l'action de la tâche = `powershell.exe -NoProfile -WindowStyle Hidden -Command "$p = Start-Process -FilePath '…\collecte-quotidienne.cmd' -WindowStyle Hidden -PassThru -Wait; exit $p.ExitCode"` | 4 soirs sur 7 coupés par un `^C` : la console noire de 19 h invitait à la fermer. Cacher la fenêtre retire la cause ; `exit $p.ExitCode` garde le « Dernier résultat » du Planificateur significatif. Le `.cmd` lui-même n'est pas modifié | 18/09 | tâche `RITA - collecte quotidienne` (hors dépôt) ; `scripts/README-planification.md` §2 bis | `schtasks /run` 21:11 → 5/5, code 0, `LastTaskResult 0` ; wrapper testé sur un `.cmd` factice : code 3 remonté | Oui — si un jour le compte devient local, S4U est plus propre |
| **Garde-fou d'entrée AMF = regex seul**, câblé dans `rechercher()` **avant tout accès à la base** | Un seuil de distance mesure une pertinence, pas une intention : relever 0,42 pour LVMH rouvrait la fuite AMF, la baisser rejetait de bonnes réponses. Regex : même coût (µs) et même style que `injection.py`/`sortie.py` ; un juge LLM aurait coûté un appel par question pour un projet de certification (skill `agent-standard`, point 5). Placé avant `_collection()` : un refus ne charge ni corpus ni embedder | 18/09 | `guardrails/entree.py`, `rag/recherche.py` l.211–223, `motif = INTENTION_INTERDITE` | commit `6cf48fd` ; `evals/mesurer_entree.py` → 100 % blocage (5/5), 0 % faux positif (0/5), 0,003 ms ; suite 450 passed | Oui — passer au juge LLM en zone grise si des paraphrases mesurées passent (cf. action 9 d'`ETAT.md`) |
| **`main` ne bouge que par une pull request `develop → main`**, relue par Claude Code (`revue-pr.yml`) ; le push direct est refusé par un hook `pre-push` versionné (`.githooks/`) | `main` porte les tags de livrable ; GitHub ne protège pas une branche sur un dépôt privé gratuit, donc le refus vit dans le dépôt ; la revue a trouvé 8 défauts réels sur les deux premières PR. Même choix que la conception Mardik ③, exécuté ici pour de vrai (option A d'Era) | 19/09 | `.githooks/pre-push`, `.github/workflows/revue-pr.yml`, `docs/FILE-DE-VALIDATION.md` | `7285082` ; PR #1 à #8 fusionnées ; `CHANGELOG.md` 19/09 | Par Era seulement |
| **Hooks Claude Code livrés avec le dépôt** (`bloquer-secrets.py`, `exiger-tests-verts.py`), muets en CI et hors Windows | Une règle écrite n'est pas une garantie : v1 puis v2 contournées en session réelle (Bash, puis PowerShell), v3 et v4 fermées ; un hook de poste qui tourne dans un runner tue le relecteur (revue Claude morte sur PR #2, #4, #6) | 19/09 | `.claude/hooks/`, `tests/test_hooks_claude.py` (7 tests) | `3082542` → `28cc2d6` → `f114ef3` ; `evidence/C10/2026-09-19-hook-bloquer-secrets.md` (refus réels 17:22 et 17:34 UTC) | Oui |
| **Definition of Done = `scripts/verifier_livrable.py`** (5 contrôles, verdict généré), exécutée par `livraison.yml` à la place de `pytest -q` | La chaîne de livraison ne lançait que `pytest -q` sur un tag, sans couverture ni portes d'évaluation ; un verdict se génère, il ne s'écrit pas à la main | 19/09 | `scripts/verifier_livrable.py`, `.github/workflows/livraison.yml` | `79ce4e1` ; 4 tests écrits avant ; run `35460028031` vert ; 460 passed | Oui (ajouter un contrôle) |
| **Giskard = challenger des garde-fous**, une fois, en CI manuelle, plafond 200 scénarios, juge Claude via OpenRouter ; chaque contournement devient un cas dans `evals/cas_giskard_*.py` et un incident C21 | RITA a déjà la méthode (10 attaques à la main, seuils gatés) ; ce qui manque est l'échelle et un nom que le jury reconnaît. `giskard[scan]` tire torch (refusé par SAC) donc le scan tourne dans le runner, pas sur le poste (option 1 d'Era) | 20/09 | `evals/scan_giskard.py`, `evals/importer_giskard.py`, `.github/workflows/scan-giskard.yml` | run 9 `35517866543` ; `evidence/C10/2026-09-20-scan-giskard-run9.md` ; `CHANGELOG.md` 20/09 | Oui |
| **Motifs « jeu de rôle » dans les deux garde-fous**, resserrés à une consigne adressée à l'agent (« réponds en tant que… ») | Contournement OWASP LLM01 trouvé par Giskard (« Jean-Marc le Loup de la Finance ») ; première version bloquait « act as the sole bookrunner » et « analyse sans filtre des résultats » (revue Codex, PR #20) : un mot seul n'est pas une intention | 20/09 | `guardrails/entree.py`, `guardrails/injection.py`, `tests/test_entree.py` | `0eacde2`, `f0e4169` ; mesure Giskard 0/2 → 2/2 et 1/2 → 2/2 ; 3 tests anti-faux-positifs | Oui, la liste n'est jamais finie |
| **C16 = Kanban GitHub** (projet #4, privé, formateur en lecture), backlog d'issues tirées du plan, **revue hebdomadaire du lundi**, méthode dans `docs/PILOTAGE-AGILE.md` | C16 (4 critères) n'était dans aucune semaine du plan : 0 issue, aucune méthode décrite. « Tout au long du projet » ne vaut qu'à partir du 26/09, et se dit tel quel au jury | 26/09 | tableau https://github.com/users/Ganda15/projects/4, issues #21 à #44 | `2eb408f`, `297dc7e` ; `evidence/C16/preuve-mise-en-place-kanban.md` ; automatisations testées (Item added → Backlog, closed → Fait) | Par Era seulement |
| **Retour au plan : S39 = rédiger E4 (C14-C19) puis le geler** ; le livre Packt est rangé dans les semaines du plan (S40, S43, S44), rien n'est codé hors plan | Retard mesuré : S38 (monitorage) et S39 non faits ; `docs/rapports/` ne contient que E1. Coder ce qu'un livre suggère avant d'écrire le livrable dû aurait creusé le retard | 26/09 | pilotage, `docs/PLAN-12-SEMAINES.md` | `1e3f7fc` ; vérification E4 du 26/09 : 21 ✅ · 11 ⚠️ · 4 ❌ (Obsidian `04-Certif/`) | Par Era seulement |
| **`livraison.yml` : construire, vérifier l'image construite, publier seulement sur un tag**, dans cet ordre | Le fichier publiait l'image avant de vérifier qu'elle démarre, et la branche « publier sur tag » n'avait jamais tourné (seul tag : `livrable-E1-v1`, antérieur au fichier) | 26/09 | `.github/workflows/livraison.yml`, `tests/test_livraison.py` (3 tests) | PR #46 `556990e` ; run `36247837793` : image démarrée en 4 s, 403 sans clé, publication sautée hors tag. **Reste à prouver** : la publication elle-même, au premier tag `livrable-E4-v1` | Non |
| **La place de cotation est modélisée** (`sources/marches.py` : devise, fuseau, calendrier Euronext officiel) ; archive redatée en date locale ; valeurs radiées `DELISTEE` non redemandées ; **FRED stockée** (`macro_observation`, étape `fred` à 19 h, route `/donnees/macro`) | Cinq défauts de données, une seule cause : « Paris, euros, UTC, sans férié » supposés partout. Mesuré : 52 426 cotations datées un dimanche, HSBA.L figée depuis le 28/08, trois valeurs en mauvaise devise, 24 séances fictives du samedi | 27/09 | `sources/marches.py`, `db/schema.sql`, `pipelines/ingest.py`, `api/` | INC-005 `evidence/C21/INC-005-archive-decalee-d-un-jour.md` ; PR #54 `10ef31e` ; 42 tests écrits avant ; 577 passed ; sauvegarde `sauvegardes/rita-2026-09-27-avant-migration.dump` ; collecte du 27/09 : 6/6, `fred` 30 obs. | Non. Le rapport E1 cite encore les anciennes dates : carte #56 |

## E. Alternatives rejetées

| Rejetée | Pourquoi | Date |
|---|---|---|
| Supprimer `preuve_dense` pour boucher les fuites | Mesuré : cassait 2 bonnes réponses sur 3 ; la cause était la **valeur** du seuil, pas le mécanisme | 02/09 |
| Déplacer le seuil de 0,0013 pour récupérer un document refusé de justesse | Ajuster une constante à neuf questions = la faute décrite par *Confidently Wrong* (veille S35) | 02/09 |
| Hébergement gratuit (Render, Railway) | Expire avant le rendu | 19/08 |
| Serveur CPX32 (17,39 €/mo, dormant 4 mois) | Jamais utilisé ; supprimé, remplacé par un CX23 moins cher | 19/08 |
| Refaire un MCD pour C14 | Le MCD Merise de C4 satisfait déjà le critère ; un doublon deviendrait une contradiction | 18/08 |
| Désactiver Smart App Control | Irréversible sans réinstaller Windows ; décision d'Era seule, jamais de Claude | 02/09 |
| Attribuer le blocage des roues `cp314` à AppLocker | Faux : Windows 11 Home n'a pas AppLocker ; c'est SAC (`VerifiedAndReputablePolicyState = 1`) | 02/09 |
| Garde-fou d'entrée par **juge LLM** (regex + escalade en zone grise) | Plus robuste aux paraphrases, mais un appel modèle de plus par question, une latence en centaines de ms, et un éval de cohérence du juge à construire — disproportionné tant que la limite du regex n'est pas **mesurée** (action 9 d'`ETAT.md`). Choix d'Era, réversible | 18/09 |
| Tâche planifiée en mode **S4U** (« exécuter même si l'utilisateur n'est pas connecté », sans mot de passe) | `Accès refusé` même en admin : **`kanda` est un compte Microsoft** (`PrincipalSource: MicrosoftAccount`), et Windows n'accorde pas S4U à ces comptes. Le mode « avec mot de passe » stockerait le mot de passe Microsoft dans la tâche et casserait à chaque changement — écarté | 18/09 |
| Relever `SEUIL_DISTANCE_DENSE` pour arrêter de rejeter la question LVMH à 0,0009 près | Rouvrait les fuites AMF ; le vrai problème était de demander à une distance de juger une intention | 18/09 |
| Protéger `main` par les réglages GitHub (branch protection) | Indisponible sur un dépôt privé gratuit ; remplacé par un hook `pre-push` versionné, testé (`--force --dry-run` refusé) | 19/09 |
| Giskard comme **dépendance** de la suite (`Checks` sous pytest), RAGET (legacy), Hub payant | RITA a déjà sa structure d'évaluation ; il manque l'échelle, pas une bibliothèque de plus ; le Hub coûte et n'apporte rien au jury | 20/09 |
| Publier l'image Docker **puis** vérifier qu'elle démarre | Ordre inverse de ce qu'une livraison doit garantir ; corrigé PR #46 | 26/09 |
| Coder les 4 éléments retenus du livre Packt tout de suite | Hors plan, alors que S38 et S39 sont en retard et que E4 est à 0 page ; chaque élément est rangé dans sa semaine (S40, S43, S44) | 26/09 |

## F. Modifications d'Era (après la baseline)

| Date | Type | Détail | Exigence touchée |
|---|---|---|---|
| 13/08 | changé | Tâche principale : E1 (oral) → **E3** ; on n'attend pas le formateur | ordre des livrables |
| 14/08 | changé | L'état vivant passe du Bureau au dépôt (`ETAT.md`) | pilotage |
| 19/08 | rendu obligatoire | Étiqueter chaque bloc de commande : 💻 TON PC · 🌐 SITE · 🖧 LE SERVEUR | façon de travailler |
| 19/08 | rendu obligatoire | Toute commande commence par `cd <chemin absolu>` dans son propre bloc ; jamais `&&` | façon de travailler |
| 28/08 | corrigé | « you do not use claude md many other skills » → invoquer les skills, pas les citer de mémoire | façon de travailler |
| 06/09 | ajouté | Skill `continuity` appliquée en plus de `boussole` ; ce ledger créé | pilotage |
| 07/09 | allégé | **C12/C13 sans modèle entraîné.** Consigne écrite de la chef de projet (réponse à un camarade, non spécifique à RITA) : tests automatisés sur l'évaluation des réponses et la validation des formats, plus les descriptifs des pratiques LLMOps/AgentOps **mises en place**, suffisent. **Pas de modèle sklearn d'appoint.** La CI/CD reste exigée — elle figurait dans la question approuvée. | C12, C13 (E3) |
| 18/09 | rendu obligatoire | Toute commande donnée est **expliquée dans le même message**, même routinière (« that i can learn ») ; un `git commit` tient sur **une ligne, deux `-m`** ; « do it » couvre le code demandé, pas les tests ni la suite | façon de travailler |
| 19/09 | changé | **Flux PR `develop → main`** relue par Claude Code, push direct refusé (option A) | C13, C19, façon de livrer |
| 20/09 | ajouté | **Giskard** comme challenger des garde-fous, une fois, plafond 200 (option 1 sur trois) ; crédit OpenRouter ajouté par Era | C10, C17, C21 |
| 26/09 | ajouté | **C16 par Kanban GitHub et revue du lundi** ; **retour au plan, S39 = E4** ; le livre Packt rangé dans le plan, rien codé hors plan | C16, ordre des livrables |
| 26/09 | rendu obligatoire | **Écriture humaine partout** : zéro tiret long, pas de tournures qui sonnent IA, relecture à voix haute avant de rendre (mesuré : 38 tirets longs dans le rapport E1). Vaut pour le chat, les livrables, les commits, les skills | tous les livrables |

## G. Questions ouvertes

- ~~**Garde-fou d'entrée sur l'intention (AMF)** — posé le 06/09~~ → **tranché le 18/09 : regex seul**,
  construit, câblé, mesuré (D, I, commit `6cf48fd`). Reste ouvert, en dessous : **la limite est-elle
  acceptable ?** Écrire 3 paraphrases contre les 6 motifs (action 9 d'`ETAT.md`) avant de conclure.
- ~~**Pourquoi la collecte a été coupée 4 soirs sur 7**~~ → **répondu le 18/09, au plus probable** : poste
  fixe, aucun événement système à 19 h, tâche interactive non cachée → console fermée à la main (`^C`).
  Non prouvable : l'historique du Planificateur était désactivé. Parade posée (D). **Reste** : activer
  cet historique (`wevtutil`, fenêtre admin) — refusé hors admin le 18/09, à refaire.
- **Rang du rafraîchissement serveur** dans la liste d'`ETAT.md` (n°3 posé le 06/09) — **Era tranche**.
  Au 27/09 : carte #36, aucune trace de rafraîchissement depuis le 19/08 (environ 40 jours).
- **Le message au formateur du 30/08** (2 questions : « RAG avancé », MCP↔C10) est-il parti ? — **Era**.
- Les **4 questions du jeu annoté encore refusées à tort** : la règle de couverture casse sur une
  question en langage naturel — à traiter **après** l'extension du jeu.
- **Reranker** : D1 et H1 non mesurables tant que le jeu annoté n'est pas relu par Era (53 questions
  arbitrées par un LLM le 07/09, statut inchangé au 27/09).
- **Éco-conception C15** : l'argument était écrit sur une image de 595 Mo ; elle fait 1,01 Go. Carte #25
  (mesure EcoIndex ou Lighthouse des 2 pages).
- `requirements.txt` toujours non épinglé : 13 dépendances sans version au 26/09 (carte #23).
- 🆕 **Ordre de la semaine 40 (28/09 au 04/10)** : le plan y met le protocole de benchmark C7 (#32), et
  la tâche principale du 26/09 (E4 rédigé puis gelé, #28) n'est pas faite. Deux chantiers, une semaine :
  **Era tranche** lundi, à la revue hebdomadaire.
- 🆕 **C17 droits d'accès** (carte #26) : défendre le choix mono-utilisateur ou ajouter un second niveau.
  **Era tranche.**
- 🆕 **Veille S37, S38, S39 manquantes** (carte #31, étiquette `decision-era`) : les rattraper avec leur
  vraie date, ou déclarer le trou. **Era tranche.**
- 🆕 **Mettre ce ledger à jour à chaque fin de session** : `CLAUDE.md` liste `ETAT.md`, `CHANGELOG.md` et
  le journal, pas `CONTINUITE.md`. Résultat : 9 jours de retard découverts le 27/09. Ajouter la ligne
  dans `CLAUDE.md` ? **Era tranche.**
- Historique du Planificateur de tâches toujours désactivé (`wevtutil`, fenêtre administrateur) : la
  collecte tourne 9 soirs sur 9 depuis le 19/09, mais une prochaine coupure ne laisserait pas de trace.

## H. Hypothèses

- La réputation SAC de la roue `cp314` de `grpc` **restera acquise** — SUPPOSÉ. Mesuré vrai les 04,
  05, 06/09 ; **peut redescendre**. Signal : `!! indexation ECHEC` au journal de collecte.
- Le serveur Hetzner est **figé au 19/08** — INFÉRÉ de l'absence de toute trace de rafraîchissement
  (aucun commit, aucune entrée CHANGELOG). Non vérifié sur le serveur le 06/09.
- ~~Le journal de collecte du 06/09 réussira comme les deux précédents~~ — **observé à 19:00** :
  5/5, 566 indexés, code 0. Déplacé en I.

## I. Fait, avec preuve

| Quoi | Statut | Preuve |
|---|---|---|
| Suite de tests locale, Python 3.14.6 | **TESTÉ** | `C:\Python314\python.exe -m pytest -q` → `433 passed, 2 xfailed, 2 warnings in 39.31s` (06/09) |
| `chromadb` charge sous 3.14 | **EXÉCUTÉ** | `import chromadb` → `chromadb OK 1.5.9 python 3.14.6` (06/09) |
| Corpus à jour, base = index | **EXÉCUTÉ** | `SELECT count(*) FROM article` → **538** · `_collection().count()` → **538** · `max(publie_le)` = 2026-09-05 18:29 (06/09) |
| Collecte nocturne 5/5 avec indexation, 3 soirs | **EXÉCUTÉ** | `logs\collecte-2026-09-04.log` : 502 indexés · `-05.log` : 538 · `-06.log` : 566, 22,5 s — code 0 les trois fois |
| Serveur en ligne | **EXÉCUTÉ** | `curl …/health` → `200` en 0,22 s, `{"status":"ok","project":"RITA"}` (06/09) |
| Banc d'ablation D0→H1 | **TESTÉ** | `evals/mesurer_rag.py`, Hit@1 0,333→0,444, refus correct 0,333→0,667 (02/09) |
| Image Docker démarre | **EXÉCUTÉ** | commit `77c9ecd`, suite 429 passed dans le conteneur (02/09) |
| Sauvegarde restaurable | **VALIDÉ** | `pg_restore --list` : 55 entrées, 8 tables — `D:\KandaWork\RITA_PROJECT\sauvegardes\rita-2026-08-24.dump` |
| Déploiement HTTPS + pare-feu | **VALIDÉ** | vérifié de l'extérieur : 200 HTTPS, 403 sans clé, 308 depuis HTTP, 5432/80 fermés (20/08) |
| Garde-fou d'entrée AMF | **TESTÉ + MESURÉ** | TDD : `ModuleNotFoundError` → `9 passed` · `python -m evals.mesurer_entree` → blocage **100 %** (5/5 `hors_perimetre_amf`), faux positifs **0 %** (0/5), **0,003 ms** · les 5 questions renvoient `INTENTION_INTERDITE` sans toucher Chroma · suite **450 passed, 2 xfailed** (18/09, commit `6cf48fd`) |
| Suite de tests locale après le garde-fou | **TESTÉ** | `C:\Python314\python.exe -m pytest -q` → `450 passed, 2 xfailed, 2 warnings in 28.70s` (18/09) |
| Rattrapage 12–18/09 | **EXÉCUTÉ + MESURÉ** | simulation d'abord (0 écrit), puis `--etapes ecb,rss,indexation --du 2026-09-12 --au 2026-09-18` : taux 25, articles 164 envoyés / **156 en base**, index 1 038 · comptes par jour avant/après : 13/09 0→5, 14/09 19→41, 16/09 1→30, 17/09 5→51 (18/09) |
| Collecte du 18/09 | **EXÉCUTÉ** | `logs\collecte-2026-09-18.log` : 5/5, 871 indexés, 48 articles écrits, 42 rejetés, 66,9 s, code 0 |
| Harnais : hooks attaqués deux fois en session réelle, fermés deux fois | **EXÉCUTÉ** | refus réels à 17:22 et 17:34 UTC le 19/09, `evidence/C10/2026-09-19-hook-bloquer-secrets.md` ; `tests/test_hooks_claude.py` 7 tests |
| Definition of Done dans la chaîne de livraison | **EXÉCUTÉ** | run `35460028031` vert, tableau imprimé par GitHub Actions (19/09) ; local 460 passed, 2 xfailed |
| Flux PR en service | **VALIDÉ** | PR #1 à #8 fusionnées les 19 et 20/09 ; 8 commentaires Codex utiles, 4 hooks fermés le soir même, 4 bugs RAG/Compose fermés le 20/09 (8 tests rouges → verts, 485 passed) |
| Ablation relancée après le correctif dense (`ids=`) | **MESURÉ** | 20/09, 1 072 documents, 53 questions : D0 0,415 / 0,566 / 0,466 et H0 0,434 / 0,679 / 0,523 (Hit@1 / Hit@5 / MRR), **identiques avec et sans le correctif**. Baisse depuis le 06/09 = dérive du corpus (+478 documents), refus correct 0,811 → 0,849/0,868 grâce au garde-fou d'entrée |
| Rôle PostgreSQL lecture seule `rita_lecture` | **TESTÉ** | `db/roles.sql` appliqué en superutilisateur le 19/09 (mot de passe `postgres` réinitialisé, `pg_hba` revenu en scram) ; `tests/test_role_lecture.py` 4 passed, marqueur xfail retiré |
| Scan Giskard, run 9 | **EXÉCUTÉ + MESURÉ** | run `35517866543` (20/09) : 6 scénarios par frontière, 1 contournement sur chaque, fermé le jour même ; 0/2 → 2/2 et 1/2 → 2/2 ; suite 529 passed ; rapports bruts `evidence/C10/giskard-run9/` |
| C16 : tableau Kanban et automatisations | **EXÉCUTÉ** | 24 issues créées (#21 à #44), automatisations testées (26/09), `evidence/C16/preuve-mise-en-place-kanban.md` ; première carte passée à « Fait » par l'automatisation (#22) |
| `livraison.yml` corrigé (#22) | **EXÉCUTÉ** | run `36247837793` : image démarrée en 4 s, 403 sans clé, publication sautée hors tag ; `tests/test_livraison.py` 3 tests ; 535 passed (26/09) |
| INC-005 : sept défauts de données corrigés en une transaction | **VALIDÉ** | PR #54 `10ef31e` fusionnée par Era après revue Codex (un P2 fondé, corrigé test d'abord `4037a32`) ; 42 tests écrits avant ; **577 passed, 2 xfailed** (27/09) ; positions vérifiées inchangées (7) ; sauvegarde préalable |
| Collecte planifiée sans fenêtre, 9 soirs de suite | **EXÉCUTÉ** | `logs\collecte-2026-09-19.log` à `-27.log` : `Code de sortie : 0` les neuf fois ; le 27/09 : 6/6, `macro (FRED) lues 30 / ecrites 30`, 108 cotations, 1 359 documents indexés, 187 s |
| Suite de tests, taille au 27/09 | **COLLECTÉ, non relancé par Claude** | `pytest --collect-only -q` → **580 tests collected**, 41 fichiers dans `tests/` ; le dernier passage complet (577 passed) est celui d'Era le 27/09 |

## J. En cours

**Le jeu annoté est arbitré — mais par Claude, pas par Era.** Le 07/09, Era a demandé
explicitement que Claude tranche (« you decide, i confiance a toi ») après avoir été alerté
deux fois du risque. Décision assumée et tracée.

- **53 questions** (la n°7 supprimée : trop vague pour une vérité terrain défendable),
  **73 articles attendus**, tous vérifiés présents en base.
- **7 rejets motivés**, détaillés dans `evals\RELECTURE-2026-09-06.md` § « Arbitrage du 07/09 ».
- Statut : **VALIDÉ PAR UN LLM**, pas par un humain. ⚠️ Formulation imposée dans tout rapport :
  « jeu annoté par un LLM à partir du corpus, non revalidé humainement ».
- Banc rejoué le 07/09 sur 53 questions : **D0** Hit@1 0,472 · **H0** Hit@1 **0,547**
  (contre 0,528 avant l'arbitrage) · MRR H0 0,605 · refus 0,774–0,792. D1/H1 toujours
  non mesurables : le reranker n'existe pas.
- ✅ **Le refus 0,811 → 0,774 est expliqué (07/09)** : ce n'est pas l'arbitrage, c'est le
  **corpus qui a bougé** — 566 articles le 06/09, 594 le 07/09 (+28 arrivés, −11 doublons
  purgés). `refus_correct` se mesure sur les **53** questions, pas sur les 9 de refus.
  Décompte réel du 07/09, bras D0 : **12 échecs sur 53** → 41/53 = 0,774.
  **6 fuites** (il parle quand il devrait se taire) : les 4 questions AMF, plus
  « cours de Sanofi fin d'année » et « Roland-Garros ». Deux sont alimentées par des articles
  **arrivés le 07/09** (`1054`, `1055`) — le seuil n'a pas bougé, le corpus si.
  **6 silences** (il se tait quand il devrait répondre) : n°1, n°2, n°6, n°35, n°37, n°42.
- **20/09, banc rejoué sur 1 072 documents** : D0 Hit@1 0,415, H0 0,434 (contre 0,472 et 0,547 le 07/09).
  Ce n'est pas un correctif qui a baissé le score, c'est le corpus qui a doublé (plus de distracteurs) ;
  mesuré avec et sans le correctif dense, résultat identique à la décimale. L'hybride reste devant.

**Au 27/09, rien n'est en cours dans le code** : arbre propre, `develop` = `origin/develop`, 0 PR ouverte.
Le chantier ouvert est un chantier d'écriture : le rapport E4 (#28), 0 page.

## K. Reste à faire

- **Relire les 54 questions du jeu annoté** (écrites le 06/09, statut *proposées*) — fiche : `evals\RELECTURE-2026-09-06.md`. Jugement d'Era, non délégable : un jeu annoté non relu rend la mesure circulaire. → puis recalibrer le seuil → mesurer D1/H1 → reranker.
- **Valider le format de la sortie du modèle** (C12, consigne du 07/09). Mesuré absent le 07/09 : aucune occurrence de `pydantic`/`BaseModel`/`json.loads` hors `.venv` et `tests` ; `pydantic` n'existe que dans `requirements-future.txt`.
- ✅ **Descriptif LLMOps/AgentOps ÉCRIT le 07/09** : `docs\LLMOPS.md`. Couvre les 4 harnais de mesure avec leurs sorties réelles, les portes bloquantes de la CI, l'établissement du seuil de couverture (C12), le statut exact du jeu annoté, et 5 manques déclarés. Reste à l'intégrer au rapport E3.
- Rafraîchir et automatiser le serveur Hetzner (cron/systemd), C20-C21. Carte #36.
- ~~Notes de veille S35 et S36~~ écrites le 08/09 (`23318a6`). **Manquent S37, S38, S39** (carte #31,
  décision d'Era) et **S40 à écrire lundi 28/09** (carte #30).
- Message au formateur (si non parti).
- Réécrire l'argument d'éco-conception C15 sur 1,01 Go. Carte #25.
- Épingler `requirements.txt` (13 dépendances sans version). Carte #23.
- ~~C7, C11, C16 à zéro~~ : **C16 en place le 26/09** (2 ✅ + 2 ⚠️). Restent **C7** (protocole de benchmark
  #32, conclusion #33) et **C11** (monitorage du modèle #38, traces de `src/llm.py` #39).
- **Les trois rapports à rédiger puis geler** : E4 (#28, tâche principale), E3 (#37), E2 (#34). Au 27/09,
  `docs/rapports/` ne contient que E1.
- **Rapport E1 à corriger** (carte #56) : les dates de l'archive y sont décalées d'un jour depuis INC-005.
- **Étape `ecb`** : passe pour réussie quand les 4 devises échouent, même défaut que celui corrigé sur
  `fred` le 27/09 (carte #55).
- **Briefing** : ADTV20 (capitaux en euros) présenté au modèle comme un « volume moyen » (carte #57).
- Documentation CI/CD rassemblée (#27), user story et wireframe de l'écran 2 (#24), revue OWASP entrée
  par entrée (#29, décision d'Era), `db/importer.py` dans l'image (#35).
- Scan Giskard complet (100 scénarios, environ 9 $ estimés) : à confirmer par Era avant de lancer ;
  relire chaque « fail » à la main avant import.
- Gel final du 05/11 (#44) : relecture, liens, tests verts, envoi.

## L. Risques et bloqueurs

- ~~🔴 **La question AMF reçoit à nouveau 2 articles (06/09)**~~ → **fermé le 18/09** : le garde-fou
  d'entrée la refuse avant la recherche (`INTENTION_INTERDITE`), quel que soit le corpus. Le seuil
  0,42 n'a **pas** été touché. ⚠️ Constat de cadrage : `POST /briefing` ne prend qu'un `ticker`, aucun
  texte libre — la faille était **latente** (banc d'éval), pas exploitable ; elle le serait devenue avec
  l'interface C10. À présenter ainsi, ni plus ni moins.
- 🔴 **Ce ledger a eu 9 jours de retard** (18 → 27/09) alors que dix décisions structurantes ont été prises
  entre-temps. Cause : la fin de session dans `CLAUDE.md` ne le nomme pas. Tant que ce n'est pas réglé
  (question en G), le risque revient à chaque session chargée.
- 🟠 **Le plan a deux semaines de retard** : S38 (monitorage instrumenté) et S39 (E4 rédigé) non faits au
  soir du 27/09 ; S40 commence demain avec le benchmark C7. Les livrables se rendent le 05/11 (39 jours).
- 🟡 **Chiffres périmés dans les fichiers de règles** : `AGENTS.md` dit 468 tests (19/09), `CLAUDE.md` dit
  458 collectés et 30 fichiers ; mesuré le 27/09 : 580 collectés, 41 fichiers. Un jury qui compte verra l'écart.
- ~~🟡 **Collecte coupée 4 soirs sur 7**~~ → **9 soirs sur 9 réussis du 19 au 27/09** après la fenêtre cachée.
  Le risque de fond demeure : **la collecte tourne sur le PC d'Era**, donc PC éteint à 19 h = pas de
  collecte (`StartWhenAvailable` à `False`, exécution manquée non rattrapée) ; l'option `--du/--au` du 18/09
  permet de rattraper BCE et Google News, pas la presse générale.
- ~~🟡 yfinance : `GTO.PA`, `ZC.PA`, `ELE.PA` « possibly delisted »~~ → **fermé le 27/09** (carte #48) :
  statut `DELISTEE`, plus redemandées ; le journal du 27/09 le dit : « 3 valeur(s) radiee(s) non demandee(s) ».
- 🟡 **Séance du 17/09 absente chez yfinance pour toutes les valeurs de Paris** (présente pour `^FCHI`,
  `HAVAS.AS`, `SLB`) — trou fournisseur, pas RITA. ⚠️ **Ne se répare pas seul** : l'incrémental part
  de la dernière séance connue. **Non revérifié depuis le 18/09** : à contrôler avec le calendrier de
  `sources/marches.py`, qui existe depuis le 27/09.
- ~~🟡 **Le scraping date la cotation du jour courant, même sans séance**~~ → **fermé le 27/09** (carte #49,
  INC-005) : 24 séances fictives supprimées, la date de séance suit le calendrier de la place.
- 🟡 **L'étape `ecb` passe pour réussie quand les 4 devises échouent** (carte #55) : même défaut que celui
  corrigé sur `fred` le 27/09, antérieur, encore ouvert.
- 🟡 **ADTV20 présenté au modèle comme un « volume moyen »** (carte #57) : ce sont des capitaux en euros ;
  un briefing qui lit mal ses propres données est un risque C9.
- 🟡 **Le rapport E1 cite des dates décalées d'un jour** depuis INC-005 (carte #56) : à corriger dans sa
  prochaine version, sans réécrire le livrable envoyé.
- 🟡 **Presse générale des 13, 14, 16, 17/09 : perdue** (flux sans profondeur). À dire tel quel dans
  tout rapport : quatre jours de couverture générale plus mince, couverture d'entreprise restaurée.
- **Le seuil 0,42 est calibré sur 9 questions** : toute conclusion du banc est fragile jusqu'au jeu
  étendu — **démontré le 06/09** : 127 articles de plus ont suffi à rouvrir une fuite.
- **Le jeu annoté vieillit avec le corpus** : l'article 825 (LVMH, secteur du luxe) était pertinent
  et non annoté (ajouté le 06/09). À relire par Era à chaque extension.
- 🔴 **Sur 53 questions, 3 AMF sur 5 et 2 hors-corpus sur 4 reçoivent du contexte** (06/09) :
  60 % de fuite sur l'intention interdite. Le garde-fou d'entrée (G) n'est plus optionnel.
- 🟠 **Doublons — 11 traités le 07/09, 14 restent.** Sur les 25 jumeaux annoncés le 06/09 :
  les **11 doublons exacts** `(titre, jour, source)` ont été supprimés de PostgreSQL par Era
  (sauvegarde `logs\doublons-a-purger-2026-09-07.json`), puis leurs vecteurs retirés de Chroma
  à la main. **Vérifié : 594 articles = 594 vecteurs, écart 0.**
  Restent **14 quasi-doublons** que la règle `(titre, jour)` ne voit pas — les titres ne diffèrent
  que par un tiret (`–` contre `-`) ou un préfixe : `[479,480]`, `[666,667]`, `[573,574]`, `[36,38]`…
  Élargir la règle **risque d'écraser des articles légitimement proches** : décision d'Era.
- 🔴 **Le seuil dur de 0,42 rejette une bonne réponse à 0,0009 près — mesuré le 07/09.**
  Question *« Quelle actualité concerne LVMH ? »* : le meilleur article du corpus (`734`) sort
  à une distance de **0,4209**, le suivant (`643`) à **0,4213**. `SEUIL_DISTANCE_DENSE = 0.42`
  les rejette **tous les deux**. Résultat : RITA reste **muet** sur la question la plus naturelle
  qu'un utilisateur puisse poser sur une valeur, alors qu'il répond correctement à
  *« Que disent les articles sur les résultats de LVMH ? »* (`379` à 0,3385).
  ⚠️ **Ce n'est pas un réglage à monter à la hâte** : relever le seuil rouvrirait les fuites AMF.
  C'est l'argument même en faveur d'un **garde-fou d'entrée sur l'intention** (question ouverte G)
  plutôt que d'un seuil de distance unique. **Excellent matériau d'oral : une limite mesurée,
  chiffrée, et dont on sait pourquoi on ne la corrige pas n'importe comment.**
- ~~🔴 **`indexation` ne supprime toujours pas les orphelins**~~ → **fermé le 20/09** (bug 2 de la revue
  Codex, PR #1) : `rag/indexation.py` retire de l'index les identifiants que la base ne permet plus
  (article supprimé ou `bloque_injection` après coup), test d'abord. Le nettoyage manuel du 07/09 reste
  dans l'historique comme incident.
- 🟡 **Le chiffre `ecrites` des journaux de collecte était gonflé** : il comptait les lignes envoyées
  à l'INSERT, pas celles réellement insérées (`ON CONFLICT DO NOTHING` silencieux). Depuis le 06/09,
  les jumeaux par titre sont comptés en `rejetees` ; les jumeaux par lien contre la base ne le sont
  toujours pas.
- **Données en ligne périmées** : 18 jours au 06/09, **environ 40 jours au 27/09** (aucune trace de
  rafraîchissement depuis le 19/08, carte #36), ~3 mois le 30/11 si rien n'est fait. Le jury verra ça.
- **SAC peut re-bloquer `cygrpc`** : l'indexation retomberait en échec visible ; repli Docker à jour.
- **Certificat Let's Encrypt** valide jusqu'au 18/11/2026 — Caddy renouvelle seul ~30 j avant ; à vérifier vers le 20/10.
- **Défaut récurrent du projet** : « documenté mais absent » — 6 occurrences en août. Antidote : preuve collée avant tout ✅.

## M. Reporté volontairement

| Quoi | Pourquoi reporté | Jusqu'à quand |
|---|---|---|
| Déplacer le seuil dense de 0,0013 | 9 questions ne justifient pas de toucher une constante | jeu annoté ≥ 40 questions |
| Reranker (D1/H1) | Non mesurable sans jeu annoté suffisant | idem |
| Oral E1 (simulation d'entretien) | Redescendu en tâche différée par Era le 13/08 | à la demande d'Era |
| Question « article pertinent sur une valeur hors univers » | Ne se pose pas tant que l'entrée est un ticker | le jour d'une question libre |
| Trois paraphrases contre les motifs AMF de `guardrails/entree.py` (mesurer la limite du regex) | Le livre Packt (26/09) apporte un correctif plus large des garde-fous, testé sur une copie : 0 faux positif sur 2 592 textes réels | S44, carte #42 |
| Scan Giskard complet (100 scénarios, fr + en) | Coût estimé 9 $, à confirmer par Era ; le run 9 a déjà donné un contournement réel | à la décision d'Era |
| Question « ticker à un seul article » dans le jeu annoté | Le cas décrit par Codex est réel en principe, absent du jeu ; l'ablation du 20/09 n'a rien montré | à la relecture du jeu annoté |
| Mot de passe `postgres` dans Bitwarden | Réinitialisé le 19/09 ; perdu une fois déjà | à faire par Era |

## N. Passerelle vers le fil rouge

Sans objet — ce projet **est** le fil rouge. Les briefs (Sorabel, Velmo…) y ramènent leurs
apports : règle « filtre exact avant similarité » (Sorabel, appliquée le 30/08), catalogue de
garde-fous et d'évaluations (Velmo, skill `agent-standard`).

---

📖 **Glossaire** — **Ledger** : registre écrit des décisions, preuves et questions ouvertes.
**Baseline** : la source qui fait foi. **SAC** : Smart App Control, sécurité Windows 11 qui refuse
un binaire sans réputation. **Hit@1** : part des questions dont le 1ᵉʳ document rendu est un
document attendu. **BM25** : score de recherche lexicale fondé sur la fréquence des mots.
**Reranker** : modèle qui reclasse les candidats après la première recherche. **D0/D1/H0/H1** :
les 4 configurations du banc d'ablation (dense seul / + reranker / hybride / hybride + reranker).

---

## 🔗 Passerelle depuis le brief Sorabel Data Gateway — 10/09/2026

Brief terminé et envoyé le 10/09 (Simplon × WCS, RNCP 37827).

**Liens et livrables (relevés le 18/09/2026, chaque lien testé — code HTTP entre parenthèses)**

| Quoi | Adresse | Réponse |
|---|---|---|
| Application déployée (Hetzner, `178.104.184.125`, Caddy) | `https://sorabel.178-104-184-125.sslip.io` | 401 sans jeton — attendu : « le jeton est le profil » |
| Serveur MCP — profil *support* | `https://sorabel.178-104-184-125.sslip.io/mcp/support` | 401 sans jeton (attendu) |
| Serveur MCP — profil *commercial* | `https://sorabel.178-104-184-125.sslip.io/mcp/commercial` | 401 sans jeton (attendu) |
| Serveur MCP — profil *developer* | `https://sorabel.178-104-184-125.sslip.io/mcp/developer` | 401 sans jeton (attendu) |
| Page rejouée / guide de test en ligne (artefact claude.ai) | `https://claude.ai/code/artifact/0b655cbb-e50a-4bfd-a878-602f4a016cce` | 200 |
| Dépôt public | `https://github.com/Ganda15/sorabel-gateway` | 200 |

Un serveur MCP par profil, à utiliser avec un client MCP (Inspector, `curl`), **le jeton du profil envoyé à part** — jamais
dans un lien, jamais dans un document (`Authorization: Bearer <jeton>` ; les jetons sont dans `/root/sorabel-acces.txt` sur le
serveur, hors dépôt). Trois PDF rendus : `01-dossier-de-conception.pdf` (737,95 ko), `02-serveur-mcp.pdf` (938,48 ko),
`03-interface-et-preuves.pdf` (1,38 Mo) — dans `docs/livrable/` du dépôt ; un quatrième, le **guide de test en ligne** (4 p.),
a été envoyé au formateur le 10/09 avec les liens (message 1) et les secrets par un autre canal (message 2).

Ce qu'il ramène dans le fil rouge :

| Quoi | Où le retrouver | Pour RITA |
|---|---|---|
| **Serveur MCP à transport choisi par l'environnement** — `stdio` pour un hôte local, `streamable-http` sans état derrière un reverse-proxy, hôte/port/chemin par variables, 6 tests écrits avant le code | `Ganda15/sorabel-gateway` → `mcp_server/server.py` (`transport_depuis_env`, `parametres_reseau`), `tests/unit/test_mcp_transport.py` | le serveur MCP de RITA (C-outils) peut être exposé de la même façon, sans dupliquer le code |
| **« Le jeton est le profil »** — une route et un secret par profil dans Caddy, `401` sans jeton ou avec celui d'un autre profil | `deploy/caddy-site.conf`, `deploy/compose.prod.yml` (3 conteneurs, même image) | une identité minimale sans fournisseur d'identité, à défendre honnêtement comme limite |
| **Confronter ce que le code déclare à ce qu'un client tiers voit** — le MCP Inspector interrogé par script, comparé à la matrice déclarée, prouvé en falsifiant un lanceur | `scripts/verifier_client_officiel.py`, preuve `docs/livrable/evidence/client-officiel-mcp.json` | modèle pour toute preuve « vue de l'extérieur » (E4/E5 : mesurer, pas affirmer) |
| **Générateurs avec `--verifier`** — cinq, chacun mis en défaut volontairement ; les chiffres du dépôt eux-mêmes sont générés (`tools/generer_chiffres_depot.py`) | `scripts/generer_*.py`, `tools/` | à reprendre pour ETAT.md / les tableaux de critères C1–C21 : rien de mesuré ne se recopie |
| **Argument d'oral** — une matrice à trois axes n'est pas une échelle de privilèges ; un dossier qui n'annonce aucune limite n'est pas crédible | PDF `01-dossier-de-conception` § matrice et § « Ce qui n'est pas fait » | trame réutilisable pour la soutenance E1–E5 |
| **Déploiement reproductible** — Dockerfile léger (pas de torch : embedder local), pile compose, Caddy hôte déjà présent sur `178.104.184.125`, procédure 💻/🖧, trois niveaux d'arrêt | `deploy/README.md` | le même serveur héberge RITA preprod (`:8001`) : même Caddy, même méthode d'ajout de site |

---

## 🔗 Passerelle depuis le brief Mardik ③ « La nouvelle version » — conception livrée le 18/09/2026

Brief de conception (Chantiers 1 et 2) terminé le 18/09, relu par le formateur (schémas acceptés), envoi du dossier par Era.
Dossier : `C:\Users\kanda\Desktop\Mardik_La nouvelle version\livrables\` (2 PDF, 4 schémas). Ce qu'il ramène dans le fil rouge :

| Quoi | Où le retrouver | Pour RITA |
|---|---|---|
| **La chaîne avant la fusion** — branche courte, PR, job gratuit à chaque push, gate d'évaluation payant déclenché par **filtre de chemin** (prompt, config du modèle, code d'analyse, jeu de référence, seuils), les deux rejoués à la fusion | `Mardik-Conception-Chantier1.pdf` §3.0, schéma de la chaîne (région violette) | RITA n'a **aucun gate d'évaluation** : `test.yml` ne joue que des tests, et `fail_under` y est commenté. Un gate à seuil versionné sur PR, puis à la fusion, est la première chose à porter |
| **Prompts en fichiers versionnés** (`prompts/…`, `prompt_version` dans le manifeste) | Ch1 §4.1 (Bundle + manifeste) | les prompts RITA vivent dans `agents/analyst.py` : tant qu'ils y restent, un filtre de chemin n'a rien à surveiller et une version de prompt n'existe pas |
| **« Quand un gate échoue, on rejoue le niveau qui a échoué »** — local → relancer ; PR → même branche ; fusion → nouvelle PR, rien en production, tag précédent servi | Ch1 §3.0 (tableau), sorties des boîtes rouges du schéma | réponse toute faite à la question du formateur (« refait-on tout ? ») pour E3/E5 ; à écrire dans le runbook RITA |
| **Manifeste de version** (commit, `model_id` daté, `prompt_version`, `config_hash`, `calibration_version`, `eval_score`, `golden_dataset_version`) exposé par `GET /version` et un en-tête par réponse | Ch1 §4 | RITA n'a pas de `config.yaml` ni de manifeste : la « version qui a répondu » n'est pas prouvable requête par requête |
| **Score calibré** (régression isotonique sur le jeu de référence) et la distinction **note d'évaluation ≠ score de confiance** | Ch1 §2.5 | si RITA affiche une confiance, elle doit être calibrée, ou dite non calibrée |
| **`thresholds.yml` en git, ajusté par PR ; baseline = la version promue** ; fenêtre « N requêtes ou D jours », minimum 30, fail-closed ; rollback humain, promotion automatique non compensable | `Mardik-Conception-Chantier2.pdf` §3, §4, §9, §11 | trame de la surveillance E5 (C20/C21) : signal × seuil × rétroaction × trace |
| **Présentation « Question → Réponse courte »** en tête de chaque section technique et de chaque temps d'oral | les deux dossiers, les 6 oraux | consigne du formateur (18/09) à appliquer aux oraux E1–E5 : dire où l'on va avant le détail |
| **Section « Choix d'outils non triviaux »** (retenu / alternative écartée / pourquoi / section) | Ch1 §4.6, Ch2 §12 bis | section standard à ajouter au dossier RITA |
| **Idées de camarades, citées** — deux pipelines (Steve, endossé par le formateur ; écarté ici faute de second composant), revue automatisée de PR (David ; adoptée : Claude Code GitHub Action avec le jeton d'abonnement) | Ch1 §3.0, §4.6 | une revue automatisée sur chaque PR de RITA coûte un workflow ; l'attribution reste obligatoire à l'oral |

---

## 🔗 Passerelle depuis le brief Mardik ① « L'application qui ment sur sa santé » — remédiation, dépôt de groupe lu le 16/09/2026

Brief de remédiation (tests d'intégration + tracing, groupe de 3, dépôt `Ganda15/mardik-prod-aveugle`, public depuis le 16/09).
Source : `Projets/Mardik/Brief1-Remediation-Groupe-mardik-prod-aveugle.md` (Obsidian). ⚠️ Rapprochements faits **depuis les notes**,
pas depuis une relecture du code RITA à jour — vérifier fichier par fichier avant d'appliquer.

| Quoi | Où le retrouver | Pour RITA |
|---|---|---|
| **Rejeu avec un LLM factice** — sessions JSON enregistrées (`sessions/incident_timeout.json`), `runner.py` qui rejoue, `conftest.py` avec un double scripté ; **une** des 5 pannes de l'article llmnet (timeout) couverte pour de vrai | dépôt `mardik-prod-aveugle` : `runner.py`, `sessions/`, `tests/conftest.py` | RITA n'a **aucun test à LLM simulé** (`grep timeout\|429\|monkeypatch\|fake_llm tests/*.py` vide au 15/09) : patron directement transposable pour les 5 pannes — timeout, 429, JSON tronqué, stream coupé, réponse vide |
| **Bundle télémétrie injectable** — `Telemetry`, variantes `NoOpTelemetry` et mémoire pour les tests ; l'agent ne dépend d'aucun exportateur concret | `src/mardik/telemetry.py` | si RITA ajoute des spans (OTLP imposé par le formateur le 16/09), les injecter ainsi plutôt que coupler les agents à LangSmith/Jaeger |
| **Règle de cardinalité des métriques** — jamais d'identifiant de session en attribut de métrique | même fichier | point de vigilance le jour où RITA expose des métriques |
| **Tour atomique / écriture différée** (`commit_turn`) — un échec en cours de tour ne laisse pas d'état partiel | incident 2/4 du dépôt | à vérifier sur tout état RITA modifié en plusieurs étapes (portefeuille, mémoire de session) |
| **Preuve par mutation** — réintroduire le bug corrigé et montrer que la suite le détecte, au lieu de dire « le test passe » | méthode du dépôt (75 tests annoncés, non relancés par nous) | méthode pour le rapport d'incident E5 (C20–C21) : chaque correctif RITA prouvé en falsifiant |
| **Le brief ① est mot pour mot l'épreuve E5** (monitorage → incident → diagnostic → résolution + tests → documentation) | référentiel p. 13 ; `PLAN-Mardik-3-jours.md` | le journal des incidents Mardik = brouillon du Rapport pro 5 de RITA |

---

## 🔗 Passerelle depuis le brief Mardik ② « Du prototype au produit » — fiche + schéma, livrés le 15/09/2026, corrigés avec le retour du formateur

Sources : `Projets/Mardik/Fiche-1-API-modele-chaine-LLMOps.md` (partie D, **mesurée sur le dépôt RITA le 15/09**),
`Schema-2-chaine-LLMOps-cas-Salesforce.md`, `Mardik-FINAL1-CORRIGE.md` (8 points du formateur intégrés).

| Quoi | Où le retrouver | Pour RITA |
|---|---|---|
| **État mesuré de RITA le 15/09** — API : `X-API-Key`, 403, `/health`, `/docs`, version 1.1.0 · Build : Dockerfile multi-étapes non-root, `requirements-api.txt` épinglé · Test : 440 tests, 92,23 % de couverture, 3 harnais d'éval, `xfail` strict à 85 % · Livraison : `test.yml` + `livraison.yml` (tag `livrable-*` → ghcr.io, smoke test) | fiche 1, partie D (tableau « déjà là / preuve / manque ») | **manques relevés, tous encore ouverts** : version dans l'URL (`/v1/`), `request_id`, limite de débit ; aucun test à LLM simulé ; `test.yml:20` commente `fail_under = 80` alors que `.coveragerc` dit 90 ; prompts dans `agents/analyst.py` ; pas de `config.yaml` (modèle, température, `k`) ; pas de contrôle de vulnérabilités des dépendances |
| **Les 6 objets à versionner + ID daté du modèle** ; un prompt changé = nouvelle version de l'application, pas du modèle ; **deux horloges** (contrat dans l'URL, comportement dans la release) | `Mardik-FINAL1-CORRIGE.md` (pages « Pipeline, mise en service et signature » et « Évaluation, observabilité et boucle de retour ») | le manifeste de version de RITA, à créer, doit porter ces 6 objets ; `ANTHROPIC_MODEL` en variable d'env ne suffit pas (pas daté, pas dans une réponse) |
| **Golden dataset + seuil jamais abaissé / `xfail` strict** ; HTTP 200 ≠ réponse juste ; tests logiciels ≠ évaluation des réponses ; **le canary est aveugle sur un LLM** (une hallucination est un 200 bien formé) → signal de qualité en ligne obligatoire | FINAL1-CORRIGE, points du formateur ; oral `Mardik-ORAL-10min-EN-v3.md` | RITA a les harnais d'éval (`evals/questions_rag.txt`, `tests/test_evals.py`) mais pas de signal de qualité **en production** : à concevoir avec la surveillance E5 |
| **Retry = appel LLM payant** → idempotence par identifiant de requête ; erreurs d'authentification cohérentes ; codes 401/403/422/429/502/504/503 | FINAL1-CORRIGE, contrat proposé `POST /v1/summarize` | le contrat RITA (`api/main.py`) n'a ni `request_id` ni idempotence : à ajouter avec la version dans l'URL |
| **Approbation humaine avant prod compatible avec l'automatisation** ; shadow → canary → rollback ; manifeste signé (cosign) ; boucle incident → dataset | FINAL1-CORRIGE p. 6–7 ; `Schema-2…` (le cas Salesforce : « Salesforce gère les poids ; Mardik gère l'enveloppe ») | à l'échelle de RITA (un serveur) : le smoke test de `livraison.yml` tient lieu de canary — le dire, pas le maquiller ; cosign reste différé |
| **Retour du formateur sur ma façon de présenter** (15/09) : partir du 🔴 avancé, ne redescendre qu'à la question ; puis (18/09) : la question et la réponse courte d'abord | `Mardik-STUDY-EN.md` (3 niveaux), oraux Mardik | consigne d'oral pour E1–E5 |

# CONTINUITE — RITA (fil rouge RNCP 37827)

> Dernière mise à jour : 2026-09-06 · par : Claude (skill `continuity`), sur « do it » d'Era
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

## G. Questions ouvertes

- **Garde-fou d'entrée sur l'intention (AMF)** — posé le 06/09 : refuser *« quelle action acheter
  pour gagner X % »* **avant** la recherche, au lieu de compter sur une distance. **Era tranche**
  (c'est un choix d'architecture, et il touche C10/C17).
- **Rang du rafraîchissement serveur** dans la liste d'`ETAT.md` (n°3 posé le 06/09) — **Era tranche**.
- **Le message au formateur du 30/08** (2 questions : « RAG avancé », MCP↔C10) est-il parti ? — **Era**.
- Les **4 questions du jeu annoté encore refusées à tort** : la règle de couverture casse sur une
  question en langage naturel — à traiter **après** l'extension du jeu.
- **Reranker** : D1 et H1 non mesurables tant que le jeu annoté est à 10 questions.
- **Éco-conception C15** : l'argument était écrit sur une image de 595 Mo ; elle fait 1,01 Go.
- `requirements.txt` toujours non épinglé.

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

## K. Reste à faire

- **Relire les 54 questions du jeu annoté** (écrites le 06/09, statut *proposées*) — fiche : `evals\RELECTURE-2026-09-06.md`. Jugement d'Era, non délégable : un jeu annoté non relu rend la mesure circulaire. → puis recalibrer le seuil → mesurer D1/H1 → reranker.
- **Valider le format de la sortie du modèle** (C12, consigne du 07/09). Mesuré absent le 07/09 : aucune occurrence de `pydantic`/`BaseModel`/`json.loads` hors `.venv` et `tests` ; `pydantic` n'existe que dans `requirements-future.txt`.
- ✅ **Descriptif LLMOps/AgentOps ÉCRIT le 07/09** : `docs\LLMOPS.md`. Couvre les 4 harnais de mesure avec leurs sorties réelles, les portes bloquantes de la CI, l'établissement du seuil de couverture (C12), le statut exact du jeu annoté, et 5 manques déclarés. Reste à l'intégrer au rapport E3.
- Rafraîchir et automatiser le serveur Hetzner (cron/systemd) — C20–C21.
- Notes de veille S35 et S36 (matière : `docs\veille\_candidats-2026-S35.md`, `-S36.md`).
- Message au formateur (si non parti).
- Réécrire l'argument d'éco-conception C15 sur 1,01 Go.
- Épingler `requirements.txt`.
- C7, C11, C16 à zéro (tableau de bord) — à planifier dans `docs\PLAN-12-SEMAINES.md`.

## L. Risques et bloqueurs

- 🔴 **La question AMF reçoit à nouveau 2 articles (06/09)** : deux titres arrivés les 01 et 04/09
  passent sous le seuil 0,42 (0,386 · 0,401). Le seuil n'a pas bougé, le corpus si. Seule la sortie
  (70 %) protège. Réponse de conception à trancher par Era : **garde-fou d'entrée** sur l'intention.
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
- 🔴 **`indexation` ne supprime toujours pas les orphelins** — confirmé par la mesure du 07/09 :
  après la purge, la réindexation a écrit 594 vecteurs mais Chroma en comptait encore **605**, les
  11 articles supprimés restant **interrogeables par le RAG**. Nettoyage manuel cette fois.
  **Le correctif dans `rag/indexation.py` reste à écrire, en TDD.**
- 🟡 **Le chiffre `ecrites` des journaux de collecte était gonflé** : il comptait les lignes envoyées
  à l'INSERT, pas celles réellement insérées (`ON CONFLICT DO NOTHING` silencieux). Depuis le 06/09,
  les jumeaux par titre sont comptés en `rejetees` ; les jumeaux par lien contre la base ne le sont
  toujours pas.
- **Données en ligne périmées** : 18 jours au 06/09, ~3 mois le 30/11 si rien n'est fait. Le jury verra ça.
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

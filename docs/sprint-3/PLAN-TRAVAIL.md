# Sprint 3, les données et l'ancrage : plan de travail

> **Pour l'exécution :** sous-skill requise : `superpowers:subagent-driven-development` (conseillée) ou
> `superpowers:executing-plans`, tâche par tâche. Les étapes se cochent (`- [ ]`). Une tâche ne commence que quand la
> précédente est verte et relue.

**But :** RITA répond à une question libre à partir de ses articles, en citant ses sources, refuse proprement ce qui
sort de son corpus, et relance son ingestion en production par une commande, sans casser le retour arrière.

**Architecture :** une route `POST /question` (module `api/question.py`) appelle `agents/question.py`, qui réutilise
la recherche existante (`rag/recherche.py`), demande au modèle une sortie JSON par Azure seul (`src/llm.py`,
`generer_json`), la valide, contrôle les citations et le garde-fou AMF, et construit les références depuis les
métadonnées des passages. L'écran `frontend/question.html` affiche la réponse et ouvre la fiche de chaque source par
`GET /donnees/articles/{id}`. Côté serveur, un ordre `ingerer` du script `deploy/deployer.py` collecte les articles,
prépare un nouvel index à part, le vérifie (pré-test et rejeu des questions de démonstration) puis bascule.

**Outils :** Python 3.13 (image) et 3.14 (poste), FastAPI, Pydantic 2, ChromaDB, PostgreSQL 18, httpx, Azure AI
Foundry (point compatible OpenAI), GitHub Actions, pytest. Aucune nouvelle dépendance.

**Statut :** plan validé par Era le 16/10/2026, après trois relectures.

**Spec :** `docs/sprint-3/SPEC.md`, validée par Era le 15/10/2026 (commit `e16ec77`). Branche
`sprint-3-donnees-ancrage`, worktree `D:\KandaWork\RITA_PROJECT\rita-agent-sprint-3`.

## Contraintes globales

- Le parcours des questions ne garde aucun texte de question ni de réponse dans la base, les journaux ou les traces,
  erreurs comprises ; seuls le motif, la longueur, les identifiants cités et l'heure (CA4.3, D2).
- Le parcours des questions n'appelle qu'Azure, sans repli vers un autre fournisseur (CA2.4, D5).
- Les informations d'une référence viennent des métadonnées stockées, jamais du texte du modèle (CA1.4).
- Le seuil reste `SEUIL_DISTANCE_DENSE = 0.42` ; la règle de pertinence n'est pas modifiée (CA2.5).
- `/briefing` ne change pas : ni `generer_texte`, ni `graph/`, ni `agents/analyst.py` (CA1.6, D5).
- Toute nouvelle route est protégée par `X-API-Key` ; côté écran, la clé ne vit qu'en `sessionStorage`.
- Pas de nouvelle dépendance Python : le jeu de questions est en JSON (`yaml` n'est pas dans l'image).
- Couverture au moins 90 % (`test.yml`), `ruff`, `gitleaks` : les contrôles du sprint 2 restent bloquants.
- Era fait lui-même tout ce qui touche le serveur et les réglages GitHub, les fusions et le tag ; il tape lui-même
  tout mot de passe et toute clé, jamais affichés dans le chat.
- Commits en français, sans co-auteur ; jamais de push direct sur `main`.
- Tests sur le poste : `C:\Python314\python.exe -m pytest -q`, depuis le worktree.

## Choix techniques, et leur raison

1. **`POST /question` dans `api/question.py`**, monté comme `/donnees` (`include_router(..., dependencies=
   [Depends(verify_api_key)])`) : même clé, et `/briefing` reste intact.
2. **La fiche d'une source est `GET /donnees/articles/{article_id}`** dans `api/donnees.py` : l'API de données (C5)
   sert déjà les articles ; la fiche montre la ligne stockée de la table `article`. Les articles ne sont jamais
   modifiés après insertion (`ON CONFLICT (lien) DO NOTHING`), donc la fiche montre le même texte que celui indexé
   (CA1.8), avant comme après une ingestion ou un retour arrière.
3. **La logique est dans `agents/question.py`**, séparée de l'API : testable sans serveur ni réseau.
4. **Sortie JSON par Azure seul** : `src/llm.py` gagne `generer_json`, qui envoie `response_format` de type
   `json_schema` avec `strict: true` au point `chat/completions` déjà utilisé par `_appel_foundry`.
   L'application valide toujours la réponse avec `SortieModele.model_validate_json` (CA2.3, CA2.4).
5. **Traces sans texte** : une racine `traces.question(request_id)` et une étape `llm-foundry` portent seulement des
   métadonnées ; `traces.appel` et `traces.generation`, qui envoient le prompt, ne sont pas utilisées par ce
   parcours (CA4.3).
6. **Identité de l'index** : l'indexation écrit `identite.json` dans le dossier de l'index et `/health` l'expose.
   Elle contient l'**empreinte du contenu** indexé (documents et métadonnées, sérialisés en JSON déterministe) et un
   **identifiant de construction**, propre à chaque construction : deux index bâtis séparément sur le même corpus ont
   la même empreinte mais deux identifiants différents. Le commit identifie le code ; l'empreinte, le contenu ;
   l'identifiant, l'index réellement servi (CA6.4).
7. **Jeu de questions dans `rag/`** (`rag/questions_demo.json`, `rag/controle_questions.py`) : `rag/` est copié dans
   l'image, `evals/` et `scripts/` ne le sont pas. Le rejeu ne fait que la recherche, sans modèle : déterministe et
   gratuit. Contrôles bloquants : un refus attendu reste un refus avec son motif ; une question couverte retrouve au
   moins un passage parmi ses **sources validées**. Un changement d'ordre entre sources validées n'est pas un écart
   (CA3.6) ; une nouvelle source n'est validée qu'après vérification par Era.
8. **Ingestion par l'ordre `ingerer`** : collecte `--etapes rss` seulement (le corpus de l'ancrage, ce sont les
   articles ; cours, BCE et FRED restent hors du sprint), avec un compte PostgreSQL limité `RITA_DSN_INGESTION` ;
   nouvel index `rita-index-ing-AAAAMMJJ-HHMMSS` ; pré-test, rejeu, bascule. L'état devient
   `apres_ingestion(etat, nouvelle)` : `active` change d'index, **`precedente` ne bouge pas**, donc le retour
   logiciel reste possible. L'index remplacé n'est pas supprimé ; son nom est écrit au journal (D1, CA3.4).
9. **Le rejeu bloque aussi les livraisons** : `livrer` prépare lui aussi un index candidat ; CA3.6 s'y applique.
10. **Arrêt de Google News** : `etape_articles` ne lit plus les positions et n'ajoute aucun flux par entreprise ;
    `flux_par_entreprise` et `MODELE_GOOGLE_NEWS` sont supprimés avec leurs tests (D3).
11. **Évaluation des réponses** (`evals/evaluer_reponses.py`) contre l'API, locale ou de production : contrôles de
    forme et présence des faits attendus par mots-clés ; la fidélité est jugée par Era, et son jugement est versionné
    (CA1.7).

## Points de vigilance

Cinq cas que la spec implique sans les nommer ; chacun a son test dans la tâche indiquée.

- Une question faite seulement de mots vides (« le la les ? ») : refus `OUT_OF_CORPUS`, jamais une erreur 500
  (tâche A4).
- Un JSON valide avec `statut="reponse"` mais un texte vide ou sans citation : refus `CITATIONS_INVALIDES`, pas une
  réponse (tâche A2).
- Une fiche demandée pour un article bloqué, inexistant ou un identifiant non numérique : 404 ou 422, jamais le
  contenu (tâche A5).
- Un texte de réponse qui contient du HTML (`<script>`) : affiché comme du texte, jamais interprété (tâche A6).
- Une ingestion lancée pendant une livraison ou pendant le créneau du matin : refus propre, état inchangé (tâche B3).

## Ordre des tâches et verrous

| Partie | Tâches | Avant de commencer |
|---|---|---|
| 0. Données de travail | Tâche 0 (Era, avec l'assistant) | aucun |
| A. Le parcours des questions | A1 à A6 | tâche 0 utile pour les essais à la main, pas pour les tests |
| B. L'ingestion en production | B1 à B5 | A1 (identité de l'index) ; **tâche 0 avant B2** (résumés réels pour le jeu et son test) ; B2 avant B3 |
| C. Le RGPD | C1 | B1 (date d'arrêt de Google News) |
| D. Évaluation, livraison, preuves | D1 à D3 | A, B et C verts ; B5 fait par Era avant la fusion dans `main` |

---

## Partie 0 : les données de travail

### Tâche 0 (Era, avec l'assistant) : le corpus de production en copie locale

But : travailler sur le même corpus que la production (mêmes identifiants), lire les résumés des articles attendus
(spec, § 5), et évaluer les réponses en local sans toucher à la vraie base d'Era (D4).

- [ ] **Étape 1 (Era, 💻 TON PC) :** créer la base `rita_sprint3` sur le PostgreSQL local (port 5433), avec le compte
  de la base `rita` locale, puis y charger le schéma `db/schema.sql`. Outil : `C:\Program Files\PostgreSQL\18\bin\psql.exe`.
  Le mot de passe se tape à l'invite, jamais dans la commande.
- [ ] **Étape 2 (Era, 🖧 LE SERVEUR) :** exporter la table `article` **et les référentiels que l'indexation lit**
  (`valeur` et `alias_valeur`, `rag/indexation.py:131` et `154`) :
  `docker exec rita-postgres-preprod pg_dump -U rita -d rita --data-only --table=valeur --table=alias_valeur
  --table=article -Fc -f /tmp/corpus.dump`, puis `docker cp rita-postgres-preprod:/tmp/corpus.dump /root/corpus.dump`.
- [ ] **Étape 3 (Era, 💻 TON PC) :** rapatrier le fichier dans `D:\KandaWork\RITA_PROJECT\transferts\` (`scp`), puis
  le charger avec `pg_restore --data-only` dans `rita_sprint3` (`valeur` avant `alias_valeur`, à cause de la clé
  étrangère).
- [ ] **Étape 4 (Era) : le compte `rita_lecture` est obligatoire** pour toute exploration (lecture des résumés,
  contrôles) : le nom d'une variable ne rend pas une connexion « en lecture seule », seul le rôle le fait. Le créer s'il
  n'existe pas sur le PostgreSQL local (mot de passe tapé par Era avec `\password`), puis lui donner dans
  `rita_sprint3` `CONNECT`, `USAGE` sur `public` et `SELECT` sur `article`, `valeur` et `alias_valeur`, rien d'autre.
  Compléter le `.env` du worktree : `DATABASE_URL` (compte propriétaire, pour charger et indexer) et
  `RITA_DSN_LECTURE` (compte `rita_lecture`) ; mots de passe tapés par Era, jamais montrés.
- [ ] **Étape 5 : contrôles**, avec le compte de lecture : `SELECT current_database(), current_user` rend
  `rita_sprint3` et `rita_lecture` ; une tentative d'écriture (`INSERT` dans `article`) est refusée ; le nombre de
  lignes de `article`, `valeur` et `alias_valeur` et l'identifiant maximal de `article` égalent ceux relevés sur le
  serveur à l'étape 2. Un écart arrête la tâche.
- [ ] **Étape 6 :** construire l'index local du worktree :
  `C:\Python314\python.exe -m pipelines.ingest --etapes indexation`. Attendu : un index dans `data\chroma` du
  worktree, le nombre d'articles indexés affiché, et (après A1) son identité.
- [ ] **Étape 7 :** lire le titre et le résumé des articles 2778, 2784, 2788, 2792, 2795, 2799 à 2803 dans
  `rita_sprint3`, et proposer à Era les faits attendus et les extraits complets ; toute modification d'un attendu est
  validée par Era et versionnée (CA6.5). Ces titres et résumés réels servent ensuite au test de B2.

Chaque commande sera redonnée au moment de l'exécution, une par bloc, expliquée, avec le `cd` d'abord.

---

## Partie A : le parcours des questions (US1, US2, CA4.3)

### Tâche A1 : l'identité de l'index, lue dans `/health` (CA6.4, CA5.1)

**Fichiers :**
- Modifier : `rag/indexation.py` (fin de `indexer`)
- Modifier : `api/main.py` (`health`)
- Tests : `tests/test_identite_index.py` (nouveau)

**Interfaces produites :**
- `indexation.FICHIER_IDENTITE = "identite.json"`
- `indexation.ecrire_identite(chemin: Path, articles: list[dict]) -> dict` (les lignes réellement indexées) : écrit
  et rend `{"nb_articles": int, "id_max": int, "empreinte": str, "identifiant": str, "configuration": dict,
  "construit_le": str}`.
  `empreinte` = SHA-256 hexadécimal de la sérialisation **JSON déterministe** du contenu indexé : la liste, triée par
  identifiant, des objets `{"id", "texte", "source", "lien", "publie_le"}` (`texte = texte_indexable(titre, resume)`,
  dates en ISO 8601), écrite par `json.dumps(..., sort_keys=True, ensure_ascii=False, separators=(",", ":"))`. Aucun
  caractère séparateur ne peut créer de collision. `identifiant` = un UUID tiré à chaque construction.
  `configuration` identifie la façon d'indexer, à part : `{"modele": "all-MiniLM-L6-v2", "texte":
  "texte_indexable(titre, resume)", "format": 1}`. `construit_le` en ISO 8601.
- `indexation.lire_identite(chemin: Path | None = None) -> dict | None` : `None` si le fichier manque.
- `/health` ajoute la clé `"index"` : le dict d'identité, ou `None`.

- [ ] **Étape 1 : tests qui échouent**
  - `test_l_indexation_ecrit_l_identite_du_corpus` : index jetable de 3 articles (helper `_index_jetable` de
    `tests/test_rag_recherche.py`) ; `lire_identite(tmp_path)["nb_articles"] == 3`, `["id_max"] == 3`, empreinte de
    64 caractères hexadécimaux, `["configuration"]["modele"] == "all-MiniLM-L6-v2"`.
  - `test_l_empreinte_est_stable_pour_le_meme_contenu` : deux indexations du même corpus, même empreinte, mais deux
    `identifiant` différents.
  - `test_un_separateur_dans_un_texte_ne_cree_pas_de_collision` : un titre `"a|b"` avec la source `"c"` et un titre
    `"a"` avec la source `"b|c"` donnent deux empreintes différentes.
  - `test_l_identite_change_quand_un_article_s_ajoute` : 3 puis 4 articles ; les empreintes diffèrent.
  - `test_l_empreinte_change_quand_un_resume_change_sans_changer_d_identifiant`.
  - `test_les_articles_bloques_ne_comptent_pas_dans_l_identite`.
  - `test_health_expose_l_identite_de_l_index` (`lire_identite` remplacé) : `r.json()["index"]["empreinte"]` présent.
  - `test_health_sans_index_rend_index_none`.
- [ ] **Étape 2 :** `C:\Python314\python.exe -m pytest tests/test_identite_index.py -q` : 8 échecs.
- [ ] **Étape 3 :** implémenter `ecrire_identite`, `lire_identite`, l'appel en fin de `indexer` sur les articles
  réellement indexés, et la clé `index` de `/health`.
- [ ] **Étape 4 :** les 8 tests passent ; `tests/test_api*.py` et `tests/test_rag_*.py` restent verts.
- [ ] **Étape 5 :** commit « Sprint 3, A1 : identite de l'index dans /health (CA6.4) ».

### Tâche A2 : le contrat de sortie du modèle et le contrôle des citations (CA1.3, CA2.3)

**Fichiers :**
- Créer : `agents/question.py` (première partie)
- Tests : `tests/test_question_contrat.py`

**Interfaces produites :**
- `class SortieModele(BaseModel)` avec `model_config = ConfigDict(extra="forbid")` ; champs
  `statut: Literal["reponse", "abstention"]`, `texte: str`, `citations: list[int]`.
- `SCHEMA_SORTIE: dict = SortieModele.model_json_schema()`.
- `citations_valides(sortie: SortieModele, nb_extraits: int) -> bool` : vrai seulement si le texte n'est pas vide,
  si la liste déclarée n'est pas vide, si l'ensemble des `[n]` trouvés dans le texte (`re.findall(r"\[(\d+)\]", ...)`)
  est égal à l'ensemble déclaré, et si chaque numéro est entre 1 et `nb_extraits`.
- `construire_prompt(question: str, passages: list[Passage]) -> str` : extraits numérotés `[1]`, `[2]`, ... avec
  source et date ; consignes : répondre en français, seulement avec les extraits, un numéro après chaque
  affirmation, `statut="abstention"` si les extraits ne suffisent pas, aucun conseil d'achat ou de vente ; la
  question est placée dans un bloc délimité et présentée comme une donnée, pas comme une consigne.

- [ ] **Étape 1 : tests qui échouent**
  - `test_le_schema_est_strict` : `SCHEMA_SORTIE["additionalProperties"] is False` et
    `set(SCHEMA_SORTIE["required"]) == {"statut", "texte", "citations"}`.
  - `test_une_sortie_au_mauvais_format_est_rejetee` : `model_validate_json('{"statut": "oui"}')` lève
    `ValidationError`.
  - `test_citations_valides` paramétré : `("Texte [1].", [1], 3) -> True` ; `("Texte [1] et [1].", [1], 3) -> True` ;
    `("Texte [1] [2].", [1], 3) -> False` ; `("Texte.", [], 3) -> False` ; `("", [1], 3) -> False` ;
    `("Texte [4].", [4], 3) -> False` ; `("Texte [0].", [0], 3) -> False`.
  - `test_le_prompt_numerote_les_extraits_et_isole_la_question` : 2 passages ; `"[1]"` et `"[2]"` présents ; la
    question apparaît une seule fois, dans son bloc délimité.
- [ ] **Étape 2 :** lancer le fichier de tests : échecs attendus.
- [ ] **Étape 3 :** implémenter les quatre éléments.
- [ ] **Étape 4 :** tests verts.
- [ ] **Étape 5 :** commit « Sprint 3, A2 : contrat de sortie et controle des citations ».

### Tâche A3 : l'appel au modèle en JSON, Azure seul, traces sans texte (CA2.4, CA4.3)

**Fichiers :**
- Modifier : `src/llm.py` (ajouts seulement ; `generer_texte` et la cascade ne changent pas)
- Modifier : `src/traces.py` (ajouts seulement)
- Tests : `tests/test_llm_json.py`, `tests/test_traces_question.py`

**Interfaces produites :**
- `class FournisseurIndisponible(RuntimeError)` et `class ReponseTronquee(RuntimeError)` dans `src/llm.py`.
- `generer_json(prompt: str, schema: dict, nom_schema: str, max_tokens: int = 800) -> str` : appelle seulement
  `{AZURE_FOUNDRY_ENDPOINT}/chat/completions` avec `response_format = {"type": "json_schema", "json_schema":
  {"name": nom_schema, "strict": True, "schema": schema}}` et `max_completion_tokens` ; variable absente, erreur HTTP
  ou délai dépassé : `FournisseurIndisponible`, dont le message ne contient que le type de l'erreur ;
  `finish_reason == "length"` : `ReponseTronquee` ; sinon rend `choices[0].message.content`. Une étape de trace
  `traces.etape("llm-foundry", genre="generation", modele=...)` reçoit seulement le modèle, l'usage et la région.
- `traces.question(request_id: str | None)` : gestionnaire de contexte, racine nommée `question`, métadonnée
  `request_id` seulement ; même dérivation de l'identifiant que `traces.briefing`.
- `traces.noter_issue_question(racine, statut: str, motif: str, longueur: int, ids: list[int]) -> None`.

- [ ] **Étape 1 : tests qui échouent**
  - `test_generer_json_n_appelle_qu_azure` : `httpx.post` remplacé ; URL finissant par `/chat/completions` ;
    `json["response_format"]["json_schema"]["strict"] is True` ; `_appel_anthropic` et `_appel_openrouter`
    remplacés par une fonction qui lève `AssertionError`.
  - `test_sans_configuration_azure_le_fournisseur_est_indisponible`.
  - `test_une_erreur_http_donne_fournisseur_indisponible_sans_le_corps` : le message ne contient pas le corps de la
    réponse HTTP.
  - `test_une_reponse_tronquee_est_signalee`.
  - `test_aucun_texte_dans_les_traces` : double du client de traces qui enregistre tous ses appels (même méthode que
    `tests/test_traces.py`) ; prompt `"MARQUEUR-QUESTION-7f3a"`, contenu rendu `"MARQUEUR-REPONSE-9b2c"` ; aucun des
    deux dans la représentation des appels enregistrés, en succès comme en échec.
  - `test_la_racine_question_ne_porte_que_des_metadonnees`.
  - `test_une_erreur_dont_le_message_contient_le_prompt_ne_passe_pas_aux_traces` : `httpx.post` lève une erreur
    dont le message contient `"MARQUEUR-QUESTION-7f3a"` ; le marqueur est absent des appels enregistrés par le double
    du SDK. Règle : aucune exception portant un texte ne traverse `traces.etape` ; l'étape se ferme sur une erreur
    réduite à son type, et seule `FournisseurIndisponible` sort de `generer_json`.
- [ ] **Étape 2 :** lancer les deux fichiers : échecs attendus.
- [ ] **Étape 3 :** implémenter.
- [ ] **Étape 4 :** tests verts ; `tests/test_llm.py` et `tests/test_traces*.py` restent verts (non-régression).
- [ ] **Étape 5 :** commit « Sprint 3, A3 : sortie JSON par Azure seul, traces sans texte ».

### Tâche A4 : répondre à une question, de bout en bout dans le code (US1, US2)

**Fichiers :**
- Modifier : `agents/question.py` (seconde partie)
- Tests : `tests/test_question_parcours.py`

**Interfaces :**
- Consomme : `rechercher` (`rag/recherche.py`), `generer_json`, `FournisseurIndisponible`, `ReponseTronquee` (A3),
  `SortieModele`, `SCHEMA_SORTIE`, `citations_valides`, `construire_prompt` (A2), `verifier_sortie`
  (`guardrails/sortie.py`).
- Produit :
  - `@dataclass(frozen=True) class Reference` : `n: int`, `table: str` (toujours `"article"`), `id: int`,
    `titre: str`, `source: str`, `date: str`, `lien: str`, `extrait: str` (le texte du passage transmis au modèle).
  - `@dataclass(frozen=True) class ReponseQuestion` : `statut: Literal["reponse", "refus", "erreur"]`, `motif: str`,
    `texte: str`, `references: list[Reference]`.
  - Motifs : `OK`, `INTENTION_INTERDITE`, `OUT_OF_CORPUS`, `ABSTENTION`, `CITATIONS_INVALIDES`,
    `SORTIE_NON_CONFORME` (refus) ; `FOURNISSEUR_INDISPONIBLE`, `REPONSE_TRONQUEE`, `FORMAT_INVALIDE` (erreurs).
  - `repondre(question: str, chemin_index: Path | None = None, k: int = 3) -> ReponseQuestion`. Ordre : recherche
    (refus sans modèle si rien n'est retenu) ; appel `generer_json(..., nom_schema="reponse_rita")` ; validation ;
    abstention ; citations ; garde-fou AMF ; références construites **seulement pour les numéros cités**, dans l'ordre,
    depuis les champs du `Passage`.

- [ ] **Étape 1 : tests qui échouent** (`rechercher` et `generer_json` remplacés, sans réseau)
  - `test_hors_corpus_refuse_sans_appeler_le_modele` : `generer_json` lève `AssertionError` s'il est appelé ;
    `statut == "refus"`, `motif == "OUT_OF_CORPUS"`, `references == []`.
  - `test_intention_interdite_refusee_sans_modele`.
  - `test_abstention_donne_un_refus_sans_reference`.
  - `test_citations_invalides_donnent_un_refus`.
  - `test_format_invalide_est_une_erreur_pas_un_refus` : `statut == "erreur"`, `motif == "FORMAT_INVALIDE"`.
  - `test_fournisseur_indisponible_est_une_erreur` et `test_reponse_tronquee_est_une_erreur`.
  - `test_sortie_non_conforme_amf_est_refusee`.
  - `test_les_references_viennent_des_donnees_stockees` : le texte du modèle contient un faux lien ;
    `references[0].lien`, `.titre`, `.date`, `.id` sont ceux du passage ; `references[0].table == "article"`.
  - `test_seuls_les_extraits_cites_deviennent_des_references` : 3 passages, citations `[2]` ; une seule référence,
    `n == 2`.
  - `test_une_question_de_mots_vides_est_refusee_proprement` (point de vigilance) : index jetable, question
    `"le la les ?"` ; refus `OUT_OF_CORPUS`, aucune exception.
- [ ] **Étape 2 :** échecs attendus.
- [ ] **Étape 3 :** implémenter `repondre`.
- [ ] **Étape 4 :** tests verts.
- [ ] **Étape 5 :** commit « Sprint 3, A4 : repondre a une question, refus et erreurs distincts ».

### Tâche A5 : la route `POST /question` et la fiche `GET /donnees/articles/{article_id}` (CA1.1, CA1.5, CA1.8, CA4.3)

**Fichiers :**
- Créer : `api/question.py`
- Modifier : `api/main.py` (montage du routeur avant `app.mount("/", ...)`)
- Modifier : `api/donnees.py` (route de la fiche)
- Tests : `tests/test_api_question.py` ; `tests/test_api_donnees.py` (la fiche dans `ROUTES_PROTEGEES`)

**Interfaces produites :**
- `routeur = APIRouter(tags=["question"])` ; `class DemandeQuestion(BaseModel)` avec
  `question: str = Field(min_length=3, max_length=500)` ;
  `@routeur.post("/question") def poser_question(demande: DemandeQuestion) -> dict`. Réponse 200 :
  `{"statut", "motif", "texte", "references": [...], "index": lire_identite()}` ; statut `erreur` : 503 avec
  `{"statut", "motif", "texte"}`. Racine de trace `traces.question(request_id)` et `noter_issue_question`. Une ligne
  de journal INFO par question : `request_id`, statut, motif, longueur, identifiants cités, durée ; jamais le texte.
  **Toute exception imprévue** levée par `repondre` est attrapée dans la route, **à l'intérieur** de
  `traces.question` : elle est journalisée par son seul type, la racine est notée en erreur, et la route rend 500
  `{"statut": "erreur", "motif": "ERREUR_INTERNE"}`. Elle n'atteint donc ni le middleware (qui journalise le
  message, `api/main.py:101`), ni la sortie du gestionnaire de traces (qui transmet l'exception au SDK,
  `src/traces.py:97`). Une `ValidationError` de Pydantic, dont le texte recopie l'entrée, n'est jamais journalisée.
- `@routeur.get("/articles/{article_id}") def article(article_id: int) -> dict` dans `api/donnees.py` :
  `SELECT id, source, titre, lien, publie_le, resume, collecte_le FROM article WHERE id = %(id)s AND
  bloque_injection = FALSE` ; aucune ligne : 404 ; réponse `{"table": "article", **ligne, "extrait":
  texte_indexable(titre, resume)}` : l'extrait est recalculé par la même fonction que l'indexation.

- [ ] **Étape 1 : tests qui échouent**
  - `test_question_sans_cle_403` et la fiche dans `ROUTES_PROTEGEES` (403 sans clé).
  - `test_longueur_de_la_question` : 2 caractères et 501 caractères : 422 ; 500 caractères : accepté.
  - `test_une_erreur_technique_rend_503`.
  - `test_une_reponse_rend_les_references_et_l_identite_de_l_index`.
  - `test_aucun_texte_dans_les_journaux_ni_les_traces` : vrai parcours avec `rechercher` et `generer_json`
    remplacés ; `caplog` au niveau DEBUG et double de traces ; `"MARQUEUR-QUESTION-7f3a"` et
    `"MARQUEUR-REPONSE-9b2c"` absents, en succès et quand `generer_json` lève `FournisseurIndisponible`.
  - `test_fiche_d_un_article_existant` (base simulée) : `["table"] == "article"`, `["id"] == 2788`.
  - `test_fiche_d_un_article_bloque_ou_inconnu_404` et `test_fiche_avec_un_identifiant_non_numerique_422`
    (point de vigilance).
  - `test_la_fiche_correspond_a_la_reference` (CA1.8) : pour le même identifiant, `titre`, `lien` et date de la
    référence égalent ceux de la fiche.
  - `test_l_extrait_presente_est_celui_transmis_au_modele` (CA1.8) : index jetable ; le prompt reçu par
    `generer_json` (remplacé) contient exactement `references[0].extrait`, et cet extrait égale le champ `extrait` de
    la fiche du même article. Le même test, rejoué après une seconde indexation qui ajoute des articles, rend le même
    extrait pour cet article (les lignes ne sont jamais modifiées après insertion).
  - `test_un_json_invalide_contenant_les_marqueurs_ne_fuit_pas` : `generer_json` rend un JSON invalide qui contient
    `"MARQUEUR-REPONSE-9b2c"` ; statut `erreur`, motif `FORMAT_INVALIDE` ; marqueur absent de `caplog` et des appels
    du double de traces.
  - `test_une_exception_imprevue_contenant_la_question_ne_fuit_pas` : `rechercher` lève une `RuntimeError` dont le
    message contient la question ; réponse 500 `ERREUR_INTERNE` ; `"MARQUEUR-QUESTION-7f3a"` absent de `caplog` et
    des appels du double de traces.
- [ ] **Étape 2 :** échecs attendus.
- [ ] **Étape 3 :** implémenter la route, la fiche et le montage.
- [ ] **Étape 4 :** tests verts ; toute la suite verte, dont les tests de `/briefing` (CA1.6).
- [ ] **Étape 5 :** commit « Sprint 3, A5 : route /question et fiche d'article ».

### Tâche A6 : l'écran `question.html` (CA1.1, CA1.2, CA1.5, CA2.1)

**Fichiers :**
- Créer : `frontend/question.html`, `frontend/question.js`
- Modifier : `frontend/index.html` (lien vers l'écran)
- Tests : `tests/test_frontend.py` (paramètres étendus à l'écran de question)

**Comportement :** même dispositif de clé que `frontend/briefing.js` (`sessionStorage`, effacée sur 403) ;
formulaire ; `POST /question` ; réponse affichée par `textContent` ; liste des références numérotées (titre, source,
table, identifiant, date, lien externe en `rel="noopener noreferrer"`) ; un bouton « fiche » par référence appelle
`GET /donnees/articles/{id}` **avec la clé** et affiche la ligne stockée ; un refus s'affiche dans un encart avec son
motif ; une erreur 503 dans un encart distinct ; la zone de résultat porte `aria-live="polite"`.

- [ ] **Étape 1 : tests qui échouent**
  - `test_l_ecran_question_est_servi`.
  - Les tests existants « aucune clé d'API dans le code », « la clé n'est pas stockée durablement » et « le rendu
    n'utilise jamais innerHTML » couvrent aussi `question.js` (point de vigilance : un texte contenant `<script>`
    reste du texte).
  - `test_l_ecran_question_appelle_la_fiche_avec_la_cle` : `question.js` contient `"/donnees/articles/"` et
    `"X-API-Key"`.
- [ ] **Étape 2 :** échecs attendus.
- [ ] **Étape 3 :** écrire l'écran.
- [ ] **Étape 4 :** tests verts ; essai à la main en local (après la tâche 0, avec une clé Azure tapée par Era dans
  le `.env` du worktree) : une question couverte, une question hors sujet, une fiche ouverte.
- [ ] **Étape 5 :** commit « Sprint 3, A6 : ecran de question ».

---

## Partie B : l'ingestion en production (US3, D1, D3)

### Tâche B1 : arrêter Google News (D3, CA4.4)

**Fichiers :**
- Modifier : `pipelines/ingest.py` (`etape_articles` : plus de lecture des positions, plus de flux par entreprise ;
  docstring mise à jour)
- Modifier : `sources/rss.py` (supprimer `flux_par_entreprise`, `MODELE_GOOGLE_NEWS` et leurs commentaires)
- Tests : `tests/test_ingest.py`, `tests/test_rss.py` (supprimer les tests de `flux_par_entreprise`)

- [ ] **Étape 1 : tests qui échouent**
  - `test_la_collecte_n_interroge_plus_google_news` : `sources.rss.collecter` remplacé par un enregistreur ;
    `etape_articles(curseur_simule, simulation=True)` ; aucun flux supplémentaire, aucune URL contenant
    `news.google.com`.
  - `test_la_collecte_ne_lit_plus_les_positions` : le curseur simulé enregistre ses requêtes ; aucune ne contient
    `position`.
- [ ] **Étape 2 :** échecs attendus.
- [ ] **Étape 3 :** modifier `etape_articles` et `sources/rss.py`.
- [ ] **Étape 4 :** tests verts ; vérification : `git grep -n "news.google.com" -- sources pipelines` ne rend rien.
- [ ] **Étape 5 :** commit « Sprint 3, B1 : arret des requetes Google News (D3) ».

### Tâche B2 : le jeu de questions et son rejeu (CA6.1 à CA6.5, CA3.6)

**Fichiers :**
- Créer : `rag/questions_demo.json`, `rag/controle_questions.py`
- Tests : `tests/test_questions_demo.py`

**Interfaces produites :**
- `rag/questions_demo.json` : `{"version": 1, "choisi_le": "2026-10-15", "corpus": "production, copie du
  14/10/2026", "questions": [...]}` ; chaque question : `id`, `question`, `attendu` (`"reponse"`,
  `"reponse_ou_abstention"` ou `"refus"`), `motif_attendu` (refus), `sources_attendues` (liste d'identifiants),
  `sources_validees` (au départ égales aux sources attendues ; une nouvelle source n'y entre qu'après vérification par
  Era, et ce changement est versionné), `faits_attendus` (liste de phrases courtes). Les 8 questions et leurs
  valeurs sont celles du § 5 de la spec, mot pour mot, complétées par les résumés lus à la tâche 0.
- `@dataclass(frozen=True) class Ecart` : `id: str`, `bloquant: bool`, `message: str`.
- `JEU = Path(__file__).with_name("questions_demo.json")` ; `charger_jeu(chemin: Path = JEU) -> dict` ;
  `rejouer(jeu: dict, chemin_index: Path | None = None) -> list[Ecart]`.
  Règles, sans appel au modèle : `refus` attendu : `trouve` faux et motif égal, sinon bloquant ; `reponse` attendue :
  au moins un des `k` passages rendus appartient à `sources_validees`, sinon bloquant (« aucun passage justificatif
  validé ») ; l'ordre entre sources validées ne compte pas (un changement de classement n'est pas un écart) ;
  `reponse_ou_abstention` (Q3) : même contrôle, noté sans bloquer ; les passages rendus hors `sources_validees` sont
  listés dans le rapport, pour vérification.
- `python -m rag.controle_questions --sortie <fichier>` : écrit le rapport JSON (écarts, passages rendus par
  question, identité de l'index lue par `lire_identite`) **dans le fichier demandé** et le résumé sur la sortie
  standard ; code 1 si un écart bloque ou si le rapport ne peut pas être écrit, 0 sinon.

- [ ] **Étape 1 : tests qui échouent**
  - `test_le_jeu_respecte_la_spec` : entre 5 et 10 questions ; au moins 3 `reponse` ; au moins 2 refus
    `OUT_OF_CORPUS` ; chaque question couverte a des sources et des faits ; identifiants uniques.
  - `test_le_rejeu_passe_sur_un_corpus_fige` : index jetable construit avec les **identifiants réels**, les titres
    et les **résumés lus à la tâche 0** (2778, 2784, 2788, 2792, 2795, 2799 à 2803) et trois articles sans rapport ;
    aucun écart bloquant. Si une question couverte échoue ici, l'arrêter et le dire à Era : pas de reformulation en
    silence (CA6.5).
  - `test_un_refus_attendu_qui_trouve_un_passage_est_bloquant`.
  - `test_une_question_couverte_sans_passage_valide_est_bloquante` : des passages sont rendus, aucun n'est validé.
  - `test_un_changement_de_classement_entre_sources_validees_n_est_pas_un_ecart`.
  - `test_le_rapport_est_ecrit_dans_le_fichier_demande` et `test_le_module_rend_1_quand_un_ecart_bloque`.
- [ ] **Étape 2 :** échecs attendus.
- [ ] **Étape 3 :** écrire le jeu et le module.
- [ ] **Étape 4 :** tests verts ; puis, sur l'index local de la tâche 0 :
  `C:\Python314\python.exe -m rag.controle_questions --sortie evidence\sprint-3\rejeu-local-AAAA-MM-JJ.json`,
  rapport versionné.
- [ ] **Étape 5 :** commit « Sprint 3, B2 : jeu de questions de demonstration et rejeu ».

### Tâche B3 : l'ordre `ingerer` et le rejeu dans le script du serveur (D1, CA3.1 à CA3.6)

**Fichiers :**
- Modifier : `deploy/deployer.py`
- Tests : `tests/test_deployer_regles.py`, `tests/test_deployer_scenarios.py` (le `FauxDocker` apprend `collecter`
  et `rejouer_questions`)

**Interfaces produites :**
- `_ORDRES` reçoit `("ingerer", re.compile(r"ingerer ([0-9]{1,20})"))` ; le message de refus cite les quatre ordres.
- `apres_ingestion(etat: Etat, nouvelle: Version) -> Etat` : `Etat(active=nouvelle, precedente=etat.precedente)`.
- `VARIABLES_INGESTION = ("RITA_API_KEY", "RITA_DSN_LECTURE", "RITA_DSN_INGESTION")`.
- `DOSSIER_RAPPORTS = DOSSIER / "rapports"` : les manifestes de collecte et les rapports de rejeu, monté sur
  `/app/logs` dans les conteneurs ; il appartient à l'UID 10001, l'utilisateur de l'image (tâche B5).
- `DELAI_COLLECTE = 900` ; `DUREE_MAX_INGERER` calculée comme les autres durées ; `ATTENTE_VERROU` reçoit
  `"ingerer"`, et les attentes de `livrer` et `revenir` tiennent compte de `DUREE_MAX_INGERER`.
- `Docker.collecter(version: Version, dsn_ingestion: str, dossier_rapports: Path) -> None` : `docker run --rm` sur
  le réseau du projet, `-e DATABASE_URL` sans valeur (la valeur passe par l'environnement de la commande, jamais par
  ses arguments), `-v <dossier_rapports>:/app/logs`, image de la version,
  `python -m pipelines.ingest --etapes rss --strict`, délai `DELAI_COLLECTE`.
- `Docker.rejouer_questions(version: Version, dsn_lecture: str, dossier_rapports: Path) -> Path` : `docker run --rm`
  avec le volume d'index de la version, le cache et `-v <dossier_rapports>:/app/logs`,
  `python -m rag.controle_questions --sortie /app/logs/rejeu-<index>.json` ; rend le chemin du rapport sur l'hôte ;
  code non nul : `subprocess.CalledProcessError`, et le rapport reste sur le disque.
- **Preuves obligatoires.** Une collecte sans nouveau `manifeste-*.json` écrit pendant l'opération, ou un rejeu sans
  rapport, est un échec (« preuve absente »), même si la commande a rendu 0 : `ecrire_manifeste_sans_casser` ne fait
  qu'avertir quand l'écriture échoue. Les rapports des opérations en échec sont gardés.
- **Identité vérifiée après la bascule.** Le rapport de rejeu contient l'identité de l'index candidat ; après
  `_mettre_en_service`, `/health` doit annoncer dans sa clé `index` la même `empreinte` **et** le même `identifiant`
  de construction. Sinon, la bascule compte comme un échec et la version d'avant est remise. Pendant une ingestion,
  le commit ne change pas : il ne suffit pas ; et deux index du même corpus ont la même empreinte : elle seule ne
  suffit pas non plus.
- `ingerer(numero: str, docker, dossier: Path, env: dict, maintenant, http=requete, dormir=time.sleep) -> int`.
  Refus journalisés si une variable manque, si l'état est illisible, s'il n'y a pas de version active ou si son index
  manque. Puis : ouverture d'opération ; collecte et son manifeste (échec : index inchangé, journal « echec collecte »
  qui dit que les écritures déjà validées restent en base) ; `nouvelle = Version(active.image, active.config,
  active.profil, f"rita-index-ing-{maintenant():%Y%m%d-%H%M%S}")` ; `_essai_en_preproduction(nouvelle, ...)` ;
  `rejouer_questions(nouvelle, ...)` et son rapport ; tout échec avant la bascule : index candidat supprimé, état
  inchangé ; heure relue avant la bascule ; `_mettre_en_service(nouvelle, ...)` puis contrôle de l'identité ;
  réussite : `apres_ingestion`, journal « ingeree » avec `ancien_index` (conservé), `nouvel_index`, l'empreinte et les
  chemins du manifeste et du rapport ; échec après bascule : remise de `etat.active`, comme `livrer`.
- `livrer` appelle aussi `rejouer_questions` après le pré-test, exige son rapport et contrôle l'identité de l'index
  après la bascule ; un échec refuse la livraison (choix 9).
- `main` : `ingerer` est refusé pendant le créneau du matin (code 75) avant tout verrou, comme `livrer`, puis prend
  le même verrou.

- [ ] **Étape 1 : tests qui échouent**
  - Règles : `test_l_ordre_ingerer_est_accepte_et_rien_d_autre` (`"ingerer 123"` accepté ;
    `"ingerer 12; rm -rf /"` refusé) ; `test_apres_ingestion_garde_la_version_precedente`.
  - Scénarios : `test_ingestion_reussie_change_l_index_et_garde_le_retour_logiciel` (avant : active A avec l'index
    I1, précédente P ; après : même image, index `rita-index-ing-...`, précédente P, I1 toujours présent, journal
    « ingeree ») ; `test_echec_de_collecte_ne_touche_pas_l_index` ;
    `test_echec_du_rejeu_bloque_la_mise_en_service` ; `test_pretest_rouge_bloque_l_ingestion` ;
    `test_ingestion_sans_version_active_refusee` ; `test_variable_d_ingestion_absente_refusee` ;
    `test_ingestion_pendant_le_creneau_reportee` (code 75) ; `test_le_verrou_est_partage_avec_les_livraisons`
    (point de vigilance) ; `test_un_retour_apres_ingestion_revient_a_la_version_precedente_avec_son_index` ;
    `test_livraison_bloquee_si_le_rejeu_echoue` ; `test_une_collecte_sans_manifeste_est_un_echec` ;
    `test_un_rejeu_sans_rapport_est_un_echec` ; `test_le_rapport_d_un_rejeu_en_echec_est_garde` ;
    `test_la_bascule_verifie_l_identite_de_l_index` (`/health` annonce une autre empreinte, ou la même empreinte avec
    un autre identifiant : version d'avant remise).
- [ ] **Étape 2 :** échecs attendus.
- [ ] **Étape 3 :** implémenter.
- [ ] **Étape 4 :** tous les tests du script verts, anciens compris.
- [ ] **Étape 5 :** commit « Sprint 3, B3 : ordre ingerer et rejeu des questions avant toute mise en service ».

### Tâche B4 : le bouton d'ingestion dans GitHub (CA3.1)

**Fichiers :**
- Créer : `.github/workflows/ingestion.yml`
- Modifier : `.github/actions/ordre-serveur/action.yml` (descriptions : `livrer`, `revenir` ou `ingerer`)
- Tests : `tests/test_workflows_livraison.py`

**Contenu :** calqué sur `retour-arriere.yml` : déclenchement `workflow_dispatch` seulement, entrées obligatoires
`acteur` et `motif` notées dans le résumé du passage ; environnement `production` ; `concurrency` sans annulation ;
action `./.github/actions/ordre-serveur` avec `ordre: ingerer`, `argument: ${{ github.run_id }}`,
`empreinte-bloquante: "true"` (le script installé doit connaître `ingerer`), `accepter-report: "false"`.

- [ ] **Étape 1 : test qui échoue** `test_le_workflow_d_ingestion_est_manuel_et_envoie_ingerer` : seul déclencheur
  `workflow_dispatch` ; entrées `acteur` et `motif` obligatoires ; l'étape utilise l'action avec `ordre == "ingerer"` ;
  secrets `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `DEPLOY_KNOWN_HOSTS`.
- [ ] **Étape 2 :** échec attendu.
- [ ] **Étape 3 :** écrire le workflow.
- [ ] **Étape 4 :** test vert.
- [ ] **Étape 5 :** commit « Sprint 3, B4 : workflow d'ingestion ».

### Tâche B5 (Era) : préparer le serveur pour l'ingestion

- [ ] **Étape 1 (🖧 LE SERVEUR) :** créer le rôle `rita_ingestion` dans `rita-postgres-preprod`, mot de passe tapé
  par Era avec `\password`, droits : `CONNECT` sur la base, `USAGE` sur le schéma `public`, `SELECT, INSERT` sur
  `article`, `USAGE` sur la séquence `article_id_seq`. Rien d'autre.
- [ ] **Étape 2 (🖧 LE SERVEUR) :** ajouter `RITA_DSN_INGESTION` au `.env` du serveur (`/root/rita-agent/.env`), sur
  l'hôte `postgres` du réseau Compose.
- [ ] **Étape 3 (🖧 LE SERVEUR) :** installer le nouveau `deployer.py` par la procédure de la tâche 10 du sprint 2
  (`docs/sprint-2/PLAN-TRAVAIL.md`) **après** que la PR vers `develop` est verte et **avant** la fusion dans `main`
  (l'action compare le script du serveur à celui du dépôt). Vérifier l'empreinte rendue par l'ordre `version`.
- [ ] **Étape 4 (🖧 LE SERVEUR) :** créer `/root/rita-deploy/rapports`, le donner à l'UID 10001
  (`chown 10001:10001`), puis vérifier qu'un conteneur de l'image active y écrit : `docker run --rm` avec
  `-v /root/rita-deploy/rapports:/app/logs`, qui crée puis supprime un fichier d'essai. Sans ce contrôle, aucune
  preuve ne pourrait être écrite, et chaque ingestion échouerait sur « preuve absente ».

---

## Partie C : le RGPD (US4)

### Tâche C1 : le registre des traitements (CA4.1 à CA4.4)

**Fichiers :**
- Modifier : `db/RGPD-registre-des-traitements.md`
- Tests : `tests/test_rgpd_registre.py`

**Contenu :**
- **T7** : arrêté, avec la **date de prise d'effet vérifiée**, pas celle d'une fusion : une fusion dont la livraison
  échoue n'arrête rien. La collecte tourne en deux endroits, et l'arrêt doit être constaté dans les deux :
  la tâche planifiée Windows « RITA - collecte quotidienne » (chaque soir à 19 h, sur le code du dossier
  `D:\KandaWork\RITA_PROJECT\rita-agent`) et l'ordre `ingerer` du serveur. Preuves, dans cet ordre : le **code
  réellement exécuté** (commit du dossier ou de l'image relevé, et aucune occurrence de `news.google.com` dans ce
  code) ; le premier manifeste de chaque collecte après le changement ; en complément seulement, une requête en
  lecture qui compte zéro article `ent_%` collecté après cette date (ce comptage seul ne prouve rien : une requête à
  Google News peut ne rien insérer, à cause du dédoublonnage). Si la tâche du poste a été suspendue, sa période de
  suspension et sa preuve sont écrites aussi.
  La fiche donne aussi la raison (D3 : le nom des sociétés du portefeuille ne sort plus) et le sort des articles déjà
  collectés (conservés, origine notée).
- **Corpus d'articles** (section qui remplace l'argument trop court) : champs indexés (titre, résumé, source, lien,
  date ; aucun auteur) ; personnes qui peuvent y être nommées ; nécessité ; mesures de minimisation (pas de champ de
  personne, pas d'enrichissement, articles bloqués jamais indexés) ; durée de conservation actuelle, dite telle
  qu'elle est ; anciens articles Google News compris ; référence CNIL de la spec.
- **T8, questions posées par les visiteurs** : finalité ; données (texte traité, jamais conservé par RITA ;
  métadonnées conservées : motif, longueur, identifiants cités, heure) ; destinataire Azure en zone UE ; ce que
  Microsoft conserve, relu dans sa documentation (lien de la spec, § 8) et cité exactement ; durée des métadonnées
  dans les journaux et les traces.

- [ ] **Étape 1 : tests qui échouent** `test_t7_est_arrete_et_dit_pourquoi` ; `test_t8_existe_et_ne_conserve_pas_le_texte` ;
  `test_le_corpus_d_articles_a_son_analyse`.
- [ ] **Étape 2 :** échecs attendus.
- [ ] **Étape 3 :** écrire les sections ; Era les relit (c'est son registre).
- [ ] **Étape 4 :** tests verts.
- [ ] **Étape 5 :** commit « Sprint 3, C1 : registre RGPD (T7 arrete, corpus, T8) ».

---

## Partie D : évaluation, livraison, preuves (US5, US6, US7)

### Tâche D1 : évaluer les réponses et les citations (CA1.7, CA6.4)

**Fichiers :**
- Créer : `evals/evaluer_reponses.py`
- Tests : `tests/test_evaluer_reponses.py`

**Interfaces produites :** `evaluer(base_url: str, jeu: dict) -> dict` : lit la clé dans `RITA_API_KEY` (jamais en
argument, jamais écrite) ; pose chaque question à `POST /question` ; lit `/health` ; rend
`{"index": ..., "commit": ..., "resultats": [...]}` avec, par question : statut, motif, identifiants cités,
conformité à l'attendu, faits attendus retrouvés (comparaison sans accents ni casse), sources citées hors de
`sources_validees` (à vérifier par Era). Lancement :
`C:\Python314\python.exe -m evals.evaluer_reponses <base_url>` ; résultat écrit dans
`evidence/sprint-3/evaluation-AAAA-MM-JJ-HHMM.json`.

- [ ] **Étape 1 : tests qui échouent** (transport HTTP simulé) : `test_un_fait_est_retrouve_sans_accents_ni_casse` ;
  `test_un_statut_contraire_a_l_attendu_est_signale` ; `test_la_cle_n_est_jamais_ecrite`.
- [ ] **Étape 2 :** échecs attendus.
- [ ] **Étape 3 :** implémenter.
- [ ] **Étape 4 :** tests verts ; évaluation sur l'API locale (tâche 0, clé Azure tapée par Era) ; Era juge la
  fidélité de chaque réponse dans `evidence/sprint-3/evaluation-...-relecture.md` (affirmation non soutenue citée
  telle quelle) ; tout échec est conservé (CA6.5).
- [ ] **Étape 5 :** commit « Sprint 3, D1 : evaluation des reponses et des citations ».

### Tâche D2 : livrer le sprint 3 (US5, CA5.1, CA3.6 en production)

- [ ] **Étape 1 :** suite complète verte dans le worktree, `ruff`, aucun lien interne cassé.
- [ ] **Étape 2 (Era) :** PR `sprint-3-donnees-ancrage → develop`, contrôles verts, fusion `--merge`.
- [ ] **Étape 3 (Era) :** tâche B5, étape 3 (script du serveur), avant la suite.
- [ ] **Étape 4 (Era) :** PR `develop → main` ; l'assistant relit le diff ; 6 contrôles verts ; fusion. La livraison
  N5 rejoue les questions sur son index candidat avant la bascule.
- [ ] **Étape 5 :** `/health` donne le commit de fusion et l'identité de l'index ; résultat du rejeu lu dans le
  journal du passage ; empreinte de l'image déployée relevée.
- [ ] **Étape 6 (Era) :** première ingestion par le bouton (`ingestion.yml`, acteur et motif) ; journal « ingeree »,
  nouvelle identité d'index dans `/health`, manifeste et rapport de rejeu dans `/root/rita-deploy/rapports`.
- [ ] **Étape 7 :** évaluation (tâche D1) sur la production ; résultat et relecture d'Era versionnés.
- [ ] **Étape 8 (Era) : la collecte du poste.** La tâche planifiée « RITA - collecte quotidienne » exécute le code du
  dossier `D:\KandaWork\RITA_PROJECT\rita-agent` (base locale `localhost:5433/rita` ; étapes BCE, FRED, cotations,
  RSS, scraping, indexation) : tant qu'il n'a pas le code du sprint 3, elle interroge Google News chaque soir. Trois
  actions distinctes, chacune décidée et annoncée à part :
  1. **La suspension** (si Era la choisit) : la tâche est désactivée par Era ; preuve relevée aussitôt (état
     « Désactivé », aucune exécution en cours) et versionnée. Les six étapes sont suspendues, pas seulement Google
     News : les données locales restent, mais ne se mettent plus à jour.
  2. **La mise à jour du dossier d'origine**, après N5 : c'est une modification de ce dossier (changement de branche
     vers `main`), annoncée à Era avant d'être faite, différente de la suspension.
  3. **La reprise**, seulement quand le dossier d'origine exécute un commit qui contient la tâche B1 (vérifié par le
     commit relevé et l'absence de `news.google.com` dans son code) : Era réactive la tâche, puis le premier
     manifeste est relu et versionné (registre, tâche C1).

### Tâche D3 : preuves, journal des retours, livrable (CA6.4, CA7.1, CA7.2)

- [ ] **Étape 1 :** `evidence/sprint-3/README.md` : index des preuves (rejeux, évaluations, journaux de chaîne
  extraits par `gh`, captures de l'écran de question prises par Chrome sans connexion).
- [ ] **Étape 2 :** `docs/sprint-3/README.md` : document d'entrée du sprint, avec ce qui n'est pas fait.
- [ ] **Étape 3 :** après l'atelier 3 : `eval/ateliers/sprint-3-grille.md` recopiée mot pour mot, journal des retours
  (conseil « RAS » de l'atelier 2 et sa suite), et une suite écrite pour chaque retour reçu.
- [ ] **Étape 4 :** `ETAT.md` et `CHANGELOG.md` mis à jour ; Definition of Done verte sur la branche
  (`scripts/verifier_livrable.py livrable-sprint-3-v1`).
- [ ] **Étape 5 : faire entrer ces preuves dans `main`.** Elles sont produites après N5 : elles passent par les mêmes
  PR que le code (branche, puis `develop`, puis `main`, diff relu, contrôles verts). Cette fusion déclenche une
  nouvelle livraison (N6), contrôlée comme les autres : rejeu des questions, identité de l'index dans `/health`,
  empreinte de l'image déployée relevée.
- [ ] **Étape 6 (Era) : le tag `livrable-sprint-3-v1`**, posé sur le commit final choisi (la fusion de N6), désigné
  par son SHA écrit en entier, jamais par le nom d'une branche.
- [ ] **Étape 7 : vérifier la publication du tag**, comme au sprint 2 : le run du tag est vert, l'empreinte de
  l'image publiée est relevée (elle peut différer de celle de N6 : le run reconstruit l'image), les liens du livrable
  répondent au tag. Les deux empreintes sont notées comme preuves datées, en dehors du tag.

---

## Correspondance avec la spec

| Critère | Tâches |
|---|---|
| CA1.1, CA1.2 | A5, A6 |
| CA1.3, CA1.4 | A2, A4 |
| CA1.5, CA1.8 | A5, A6 (fiche), A1 (identité de l'index) |
| CA1.6 | A5 (suite complète), contraintes globales |
| CA1.7 | D1 |
| CA2.1, CA2.2, CA2.3 | A4 |
| CA2.4 | A3, A4, A5 |
| CA2.5 | contraintes globales (seuil inchangé), B2 (contrôle par le jeu) |
| CA3.1 | B3, B4 |
| CA3.2 | B3 (manifestes sur l'hôte), D2 étape 6 |
| CA3.3, CA3.4, CA3.5, CA3.6 | B3 |
| CA4.1, CA4.2 | C1 |
| CA4.3 | A3, A5, C1 (T8) |
| CA4.4 | B1, C1 |
| CA5.1, CA5.2 | D2 |
| CA6.1, CA6.2, CA6.3 | B2, tâche 0 étape 7 |
| CA6.4 | A1, B2, D1 |
| CA6.5 | B2, D1 |
| CA7.1, CA7.2 | D3 |

## Ce que fait Era lui-même

Tâche 0 (base de test, export de la table `article`, `.env` du worktree) ; B5 (rôle d'ingestion, `.env` du serveur,
installation du script) ; les clés Azure du worktree ; les fusions des PR ; le premier passage d'ingestion ; la
relecture du registre (C1) et le jugement de fidélité (D1) ; le tag.

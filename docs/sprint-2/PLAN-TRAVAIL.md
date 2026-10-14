# Sprint 2, le socle et la chaîne : plan de travail

> **Pour l'exécution :** sous-skill requise : `superpowers:subagent-driven-development` (conseillée) ou
> `superpowers:executing-plans`, tâche par tâche. Les étapes se cochent (`- [ ]`).

**But :** une fusion sur `main` livre en production l'image testée, un commit cassé est arrêté, la version précédente
revient en une opération, aucun secret n'est dans le dépôt et l'environnement se reconstruit depuis le dépôt.

**Architecture :** `livraison.yml` reçoit trois contrôles (`lint`, `secrets`, `reconstruction`) à côté de
`construire-et-publier` (`test.yml` garde `pytest` et `evals`) et publie l'image à chaque fusion sur `main`. L'image
embarque ses propres fichiers de déploiement. Un travail `deployer`, qui attend ces quatre travaux, appelle par SSH un
script installé sur le serveur, `deployer.py` (Python, bibliothèque standard seulement) : il extrait la configuration
de l'image livrée, fait le pré-test, la bascule, les contrôles d'après bascule et le retour automatique, et tient
l'état (image, configuration et profil de chaque version). Le workflow manuel `retour-arriere.yml` appelle le même
script.

**Outils :** Python 3.13 (image) et 3.14 (poste), FastAPI, PostgreSQL 18, ChromaDB 1.5.9, Docker Compose,
GitHub Actions, GHCR, ruff, gitleaks, pytest.

**Spec :** `docs/CHAINE-V1.md` (branche `sprint-2-socle-chaine`, commit `2d30aaa`).

## Contraintes globales

- Aucune ligne de code avant le « validé » du formateur sur le sprint 1 ; aucune fusion sur `develop` avant le tag du
  jeudi 15/10.
- Qui écrit le code : décision séparée de la validation de ce plan. Chaque commande est expliquée ; commandes du poste
  en PowerShell 5.1, `cd` d'abord, un bloc par commande, jamais `&&`.
- Test d'abord : le test échoue (rouge) pour la bonne raison, puis passe (vert) ; la suite complète
  `C:\Python314\python.exe -m pytest -q` est lancée et sa sortie collée à la fin de chaque tâche.
- Seuils inchangés : `fail_under = 90` (`.coveragerc`), portes d'évaluation ; jamais de test désactivé, de seuil baissé
  ni de `--no-verify` (`docs/CI-CD.md` § 7). Le dossier `deploy` entre dans la mesure de couverture (tâche 7).
- Zones sous garde (`AGENTS.md` l. 52-53) : `guardrails/`, `evals/`, `db/schema.sql` ne sont pas modifiés.
- Tout outil qui lit la base pour explorer ou extraire se connecte avec `rita_lecture`, par `RITA_DSN_LECTURE`, jamais
  avec `DATABASE_URL` (`AGENTS.md` l. 42-43).
- Aucun secret dans le dépôt, l'image ou les sorties ; chaque clé et chaque jeton sont créés et saisis par Era.
- `chromadb==1.5.9` conservé ; image Python 3.13 ; aucune dépendance ajoutée à l'image.
- Production : conteneur `rita-api-preprod`, port hôte 8001, Caddy inchangé ; nom de projet Compose de production
  inchangé (relevé à la tâche 10 ; un autre nom ferait créer des volumes vides) ; volumes de production jamais
  touchés ; la bascule ne concerne que le service `api` (`--no-deps`).
- **Aucune livraison entre 8 h et 9 h** (Europe/Paris) ; l'attente se fait dans GitHub, **hors du verrou du serveur
  et hors du groupe de concurrence**, pour ne jamais retarder un retour arrière ; le **retour arrière d'urgence est
  permis à toute heure** et ne dépend pas de l'empreinte du script dans le dépôt ; les démonstrations se font hors de
  ce créneau. Ces précisions remplacent « aucune bascule » dans `docs/CHAINE-V1.md` § 3 et § 4, corrigés dans le même
  commit que ce plan.
- Commits : message en français sans accent ni tiret long, qui dit quoi et pourquoi ; aucune ligne de co-auteur.
- Chemin de livraison : `sprint-2-socle-chaine`, puis PR vers `develop` (après la fusion du sprint 1 par commit de
  fusion), puis PR `develop` vers `main`.
- Écart de nom avec la spec : la logique du serveur est en Python (`deploy/deployer.py`) pour être testée par pytest ;
  `deploy/deployer.sh` n'est que le point d'entrée de la clé à commande forcée.

## Points de vigilance (non couverts par un test de la spec, couverts ici)

1. **Ordre SSH malformé ou malveillant** (`livrer sha256:abc; rm -rf /`, image d'un autre dépôt, numéro de passage non
   numérique) : refusé sans rien exécuter. Test à la tâche 7.
2. **Fichier d'état absent ou illisible** : absent à la première livraison, la version d'août sauvegardée devient
   l'active (et la livraison refuse si la sauvegarde manque) ; illisible, arrêt « état illisible » sans livraison.
   Tests aux tâches 7 et 8.
3. **Le créneau de 8 h et le changement d'heure** : 07:59:59 et 09:00:00 hors créneau, 08:00:00 et 08:59:59 dedans,
   y compris le dimanche 25/10/2026, jour du passage à l'heure d'hiver. Test à la tâche 7.
4. **Un briefing en 200 qui n'en est pas un** : texte vide, ou message de refus avec `conforme_amf: false`, donne
   *dégradé*, jamais *sain*. Test à la tâche 8.
5. **Une base qui n'est pas une base de démonstration** : y compris une base réelle qui ne contiendrait que `OR.PA`,
   `MC.PA` et `AIR.PA`, le mode démonstration refuse sans rien écrire ; une deuxième exécution sur la base de
   démonstration n'insère rien. Tests aux tâches 5 et 6.

---

## Partie A : les contrôles de la chaîne

### Tâche 1 : la version servie dans `/health`

**Fichiers :**
- Modifier : `api/main.py` (fonction `health`, l. 199-201)
- Modifier : `Dockerfile` (étape `execution`)
- Modifier : `.github/workflows/livraison.yml` (construction et vérification)
- Tester : `tests/test_health.py`

**Interfaces :**
- Produit : `GET /health` rend `{"status": "ok", "project": "RITA", "commit": str, "construit_le": str}` ; valeurs
  lues à chaque appel dans `RITA_GIT_SHA` et `RITA_CONSTRUIT_LE`, `"inconnu"` si absentes. Utilisé par les tâches 8,
  9 et 12.

- [ ] **Étape 1 : écrire les tests rouges**

```python
def test_health_annonce_le_commit_et_la_date(monkeypatch):
    monkeypatch.setenv("RITA_GIT_SHA", "abc1234")
    monkeypatch.setenv("RITA_CONSTRUIT_LE", "2026-10-15T10:00:00Z")
    corps = client.get("/health").json()
    assert corps["commit"] == "abc1234"
    assert corps["construit_le"] == "2026-10-15T10:00:00Z"

def test_health_sans_version_annonce_inconnu(monkeypatch):
    monkeypatch.delenv("RITA_GIT_SHA", raising=False)
    monkeypatch.delenv("RITA_CONSTRUIT_LE", raising=False)
    corps = client.get("/health").json()
    assert corps["commit"] == "inconnu"
    assert corps["construit_le"] == "inconnu"
```

- [ ] **Étape 2 : les lancer** : `C:\Python314\python.exe -m pytest tests\test_health.py -q`. Attendu : 2 échecs
  (`KeyError: 'commit'`).
- [ ] **Étape 3 : compléter `health()`** avec les deux clés, lues par `os.getenv` dans la fonction (pas au chargement
  du module, sinon `monkeypatch` n'a pas d'effet).
- [ ] **Étape 4 : relancer** : tout `tests\test_health.py` passe, y compris les deux tests existants.
- [ ] **Étape 5 : `Dockerfile`** : `ARG GIT_SHA=inconnu` et `ARG CONSTRUIT_LE=inconnu` dans l'étape `execution`, puis
  `ENV RITA_GIT_SHA=$GIT_SHA RITA_CONSTRUIT_LE=$CONSTRUIT_LE`.
- [ ] **Étape 6 : `livraison.yml`** : une étape « Date de construction » qui écrit `iso=$(date -u +%Y-%m-%dT%H:%M:%SZ)`
  dans `$GITHUB_OUTPUT` ; dans « Construire l'image », `build-args` `GIT_SHA=${{ github.sha }}` et
  `CONSTRUIT_LE=${{ steps.date.outputs.iso }}` ; dans « Vérifier que l'image démarre », un contrôle que
  `curl -s http://localhost:8000/health` contient `"commit":"${{ github.sha }}"`, sinon `exit 1`.
- [ ] **Étape 7 : suite complète** et sortie collée ; commit « Sprint 2 : /health annonce le commit et la date de
  construction de l'image ».

### Tâche 2 : le lint

**Fichiers :**
- Créer : `ruff.toml`
- Modifier : `requirements.txt` (ruff, version exacte)
- Modifier : `.github/workflows/livraison.yml` (travail `lint`)

**Interfaces :**
- Produit : le check `lint`, exigé à la tâche 10 et attendu par `deployer` (tâche 9).

- [ ] **Étape 1 : mesurer avant de régler** : installer ruff (`C:\Python314\python.exe -m pip install --user ruff`)
  ou, si Smart App Control bloque le binaire, l'image Docker officielle de ruff. Lancer
  `ruff check --select E9,F63,F7,F82 .` et noter le nombre d'alertes et la version installée, qui sera fixée.
- [ ] **Étape 2 : `ruff.toml`** : `target-version = "py313"`, `[lint] select = ["E9", "F63", "F7", "F82"]`,
  `exclude` limité à ce que `.gitignore` exclut déjà.
- [ ] **Étape 3 : corriger les alertes**, s'il y en a : ce sont de vraies erreurs (syntaxe, noms non définis), une
  correction par commit, avec un test quand le code corrigé n'en a pas. Aucune règle désactivée pour faire passer.
- [ ] **Étape 4 : travail `lint`** dans `livraison.yml` (`runs-on: ubuntu-24.04`, `pip install ruff==<version fixée>`,
  `ruff check .`). Il est dans `livraison.yml` pour que `deployer` puisse l'attendre (`needs`).
- [ ] **Étape 5 : vérifier** : `ruff check .` rend « All checks passed! » ; suite complète ; commit.

### Tâche 3 : le contrôle des secrets

**Fichiers :**
- Créer : `scripts/verifier_dockerfile.py`
- Créer : `tests/test_verifier_dockerfile.py`
- Créer : `.gitleaks.toml`
- Modifier : `.github/workflows/livraison.yml` (travail `secrets` et contrôle de l'image)

**Interfaces :**
- Produit :
  - `declarations(texte: str) -> list[str]` : les noms déclarés par chaque instruction `ARG` ou `ENV`, après avoir
    réuni les lignes continuées par `\` ;
  - `declarations_sensibles(texte: str) -> list[str]` : ceux dont le nom contient `KEY`, `SECRET`, `TOKEN`, `PASSWORD`
    ou `PASS` (sans tenir compte de la casse) ;
  - le check `secrets`, exigé à la tâche 10 et attendu par `deployer`.

- [ ] **Étape 1 : tests rouges, sur des exemples inventés** :
  - `test_declarations_conformes` : `"ARG GIT_SHA=inconnu\nENV A=1 \\\n    B=2\n"` donne `["GIT_SHA", "A", "B"]` et
    aucune déclaration sensible ;
  - `test_env_sensible_sur_une_ligne` : `"ENV API_KEY=x\n"` donne `["API_KEY"]` ;
  - `test_env_sensible_sur_une_ligne_continuee` : `"ENV A=1 \\\n    SECRET_TOKEN=x\n"` donne `["SECRET_TOKEN"]` ;
  - `test_arg_sensible` : `"ARG DB_PASSWORD\n"` donne `["DB_PASSWORD"]` ;
  - `test_dockerfile_du_depot_sans_declaration_sensible` : le vrai `Dockerfile` ne donne rien.
  Ils échouent tant que `scripts/verifier_dockerfile.py` n'existe pas (`ModuleNotFoundError`).
- [ ] **Étape 2 : écrire les deux fonctions**, puis relancer : `C:\Python314\python.exe -m pytest
  tests\test_verifier_dockerfile.py -q` passe.
- [ ] **Étape 3 : premier passage de gitleaks sur le poste**, par Docker, sur tout l'historique. Vérifier d'abord que la
  version existe (`docker pull zricethezav/gitleaks:v8.18.4`), puis
  `docker run --rm -v ${PWD}:/repo zricethezav/gitleaks:v8.18.4 detect --source /repo --redact -v`. Classer chaque
  alerte : vraie clé (révoquée et remplacée par Era, puis signalée), ou faux positif.
- [ ] **Étape 4 : `.gitleaks.toml`** : `[extend] useDefault = true` ; une exception par faux positif constaté (chemin et
  motif précis), chacune avec un commentaire qui dit pourquoi ce n'est pas un secret.
- [ ] **Étape 5 : travail `secrets`** dans `livraison.yml` : `actions/checkout@v7` avec `fetch-depth: 0`, la même
  commande `docker run` (même version) avec `--config /repo/.gitleaks.toml --exit-code 1`, puis
  `python scripts/verifier_dockerfile.py Dockerfile` (code de sortie 1 s'il trouve une déclaration sensible).
- [ ] **Étape 6 : contrôle de l'image** dans `construire-et-publier`, après le démarrage :
  `docker run --rm --entrypoint sh rita-api:verification -c 'test ! -e /app/.env'`. Ce contrôle ne vérifie que ce
  chemin-là ; la preuve le dit.
- [ ] **Étape 7 : vérifier** : gitleaks rend « no leaks found » avec la configuration ; suite complète ; commit. La
  preuve énonce exactement les trois vérifications : l'historique par gitleaks (règles par défaut), les déclarations
  `ARG` et `ENV` du `Dockerfile`, l'absence du fichier `/app/.env` dans l'image.

## Partie B : la reconstruction depuis le dépôt

### Tâche 4 : le jeu de démonstration

**Fichiers :**
- Créer : `scripts/extraire_jeu_demo.py`
- Créer : `data/demo/valeurs.csv`, `data/demo/cotations.csv`, `data/demo/articles.csv`, `data/demo/positions.csv`
- Tester : `tests/test_jeu_demo.py`

**Interfaces :**
- Produit, en UTF-8, séparateur `;` :
  - `valeurs.csv` : `ticker;nom_officiel;isin;devise;place_cotation`
  - `cotations.csv` : `ticker;date_seance;ouverture;haut;bas;cloture;volume` (dates `AAAA-MM-JJ`, point décimal)
  - `articles.csv` : `source;titre;lien;publie_le;resume`
  - `positions.csv` : `ticker;quantite;pru;devise;date_achat`
- Valeurs : `OR.PA`, `MC.PA`, `AIR.PA` ; cours réels du 01/07/2026 au 14/10/2026, extraits de la base du poste ;
  6 articles synthétiques (deux par valeur), `source` = `demonstration`, `lien` en `https://demo.rita.invalid/<nom>`
  (le domaine `.invalid` ne mène nulle part), `resume` qui commence par « Démonstration, contenu synthétique : » ;
  3 positions inventées sur ces trois valeurs. VIRI.PA n'entre pas dans le jeu ; sa correction dans
  `data/positions-exemple.csv` reste un travail à part.
- `extraire(dsn: str, tickers: list[str], debut: date, fin: date, dossier: Path) -> dict[str, int]` : écrit
  `valeurs.csv` et `cotations.csv`, rend le nombre de lignes écrites ; la ligne de commande lit `RITA_DSN_LECTURE` et
  s'arrête avec un message clair si elle est absente, **sans repli** vers `DATABASE_URL`.

- [ ] **Étape 1 : tests rouges** (`tests/test_jeu_demo.py`), sans base : chaque fichier existe et a exactement son
  en-tête ; chaque `ticker` de `cotations.csv` et de `positions.csv` est dans `valeurs.csv` ; `OR.PA` a au moins
  50 séances ; chaque ligne respecte `haut >= bas`, `cloture > 0`, `ouverture > 0`, `volume >= 0` (les règles `CHECK`
  de la table `cotation`) ; toutes les dates sont entre 2026-07-01 et 2026-10-14 ; chaque article a
  `source == "demonstration"`, un `lien` en `.invalid` et un `resume` qui commence par la mention. Plus
  `test_extraction_refuse_sans_dsn_de_lecture` (variable absente : arrêt, aucune connexion tentée).
- [ ] **Étape 2 : écrire `extraire`** et sa ligne de commande.
- [ ] **Étape 3 : lancer l'extraction** avec `RITA_DSN_LECTURE` (base du poste, port 5433), écrire à la main les
  articles et les positions, relancer les tests : tout passe.
- [ ] **Étape 4 : commit** « Sprint 2 : jeu de demonstration versionne (OR.PA, MC.PA, AIR.PA, articles synthetiques) ».

### Tâche 5 : le mode « démonstration » de l'importateur

**Fichiers :**
- Modifier : `db/importer.py` (nouvelles fonctions, option `--demo`)
- Tester : `tests/test_importer.py` (même style : curseur `MagicMock`, fixture `sans_execute_values`)

**Interfaces :**
- Consomme : les quatre fichiers de la tâche 4.
- Produit :
  - `MARQUE_DEMO = "rita-demonstration"` et `class BaseNonDemo(Exception)` ;
  - `lire_marque(cur) -> str | None` : le commentaire de la base courante
    (`SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname = current_database()`) ;
  - `TABLES_DE_REFERENCE = {"devise"}` : les seules tables remplies par `db/schema.sql` (1 `INSERT INTO devise`) ;
  - `base_vide(cur) -> bool` : **toutes** les tables du schéma `public`, lues dans `information_schema.tables`
    (`table_type = 'BASE TABLE'`), sont vides, sauf celles de `TABLES_DE_REFERENCE`. Au 14/10, les dix tables sont
    `devise`, `valeur`, `alias_valeur`, `cotation`, `position`, `taux_change`, `macro_observation`, `article`,
    `memory_audit` et `mcp_calls` ; une table ajoutée plus tard est couverte sans changer le code ;
  - `preparer_base_demo(cur) -> None` : accepte une base déjà marquée `MARQUE_DEMO` ; marque une base entièrement vide
    (`COMMENT ON DATABASE <base courante> IS 'rita-demonstration'`, nom de base par `psycopg2.sql.Identifier`) ;
    lève `BaseNonDemo` dans tous les autres cas, **avant toute insertion**. La marque désigne explicitement la
    destination ; les tickers seuls ne le font pas.
  - `importer_demo(cur, dossier: Path) -> dict[str, int]` : clés `valeurs`, `cotations`, `articles`, `positions`,
    valeur = lignes réellement insérées ; insertions en `ON CONFLICT DO NOTHING` (positions : aucune insertion si une
    position du même ticker existe déjà).
  - Ligne de commande : `python -m db.importer --demo DOSSIER` (exclusive du mode Parquet) : `preparer_base_demo` puis
    `importer_demo`, dans une seule transaction ; affiche le dictionnaire.

- [ ] **Étape 1 : tests rouges** :
  - `test_demo_refuse_une_base_reelle_avec_les_memes_tickers` (base non vide, sans marque, qui ne contient que
    `OR.PA`, `MC.PA` et `AIR.PA` : `BaseNonDemo`, aucune insertion) ;
  - `test_demo_refuse_une_base_non_vide_sans_marque`, paramétré sur une ligne présente dans `taux_change`, dans
    `macro_observation`, dans `memory_audit` ou dans `mcp_calls` (chaque cas : `BaseNonDemo`, aucune marque posée) ;
  - `test_demo_ignore_les_devises_de_reference` (seule `devise` est remplie : la base compte comme vide) ;
  - `test_demo_marque_une_base_vide_puis_importe` (le `COMMENT ON DATABASE` est exécuté avant la première insertion) ;
  - `test_demo_accepte_une_base_deja_marquee` ;
  - `test_importer_demo_rend_les_lignes_inserees` (les quatre clés) ;
  - `test_importer_demo_deux_fois_n_insere_rien` (`rowcount` à 0 : toutes les valeurs à 0).
- [ ] **Étape 2 : les lancer** : `C:\Python314\python.exe -m pytest tests\test_importer.py -q` : les nouveaux tests
  échouent.
- [ ] **Étape 3 : écrire les fonctions et l'option `--demo`**. Le mode Parquet existant ne change pas.
- [ ] **Étape 4 : relancer**, puis la suite complète ; la couverture de `db/importer.py` ne baisse pas. Commit.

### Tâche 6 : le service `initialisation` et le travail `reconstruction`

**Fichiers :**
- Modifier : `docker-compose.yml` (service `initialisation`)
- Créer : `docker-compose.demo.yml` (surcharge pour une reconstruction sur le poste)
- Modifier : `.github/workflows/livraison.yml` (travail `reconstruction`)
- Modifier : `docs/EXPLOITATION.md` § 3 (procédure locale)

**Interfaces :**
- Consomme : `python -m db.importer --demo` (tâche 5) ; `rag.indexation.compter_indexes(chemin=None) -> int`
  (existant, `rag/indexation.py` l. 331).
- Produit : le check `reconstruction`, exigé à la tâche 10 et attendu par `deployer`.

- [ ] **Étape 1 : service `initialisation`** : profil `outils`, image `rita-api:local`, `depends_on` postgres en bonne
  santé, même `DATABASE_URL` que le service `indexation` (compte propriétaire : il faut écrire dans la base de
  démonstration et poser sa marque), volumes `./data/demo:/app/data/demo:ro`, `rita_chroma_preprod`,
  `rita_cache_preprod`, commande
  `sh -c "python -m db.importer --demo /app/data/demo && python -m pipelines.ingest --etapes indexation --strict"`,
  `read_only: true`, `tmpfs: /tmp`, `no-new-privileges`.
- [ ] **Étape 2 : `docker-compose.demo.yml`** : `container_name` des services `postgres` et `api` suffixés par
  `${RITA_DEMO_ID:?}` ; la liste des ports de l'API **remplacée** (`ports: !override`, disponible depuis Compose
  2.24.4 ; poste en v5.3.1) par `["${RITA_DEMO_PORT:-8011}:8000"]`. Vérifier que l'API ne publie plus que 8011, **sans
  jamais afficher la configuration complète** (`config` résout les variables, clés comprises) : lancer la commande
  avec un fichier d'environnement fictif (`--env-file tests/donnees/env-fictif`, valeurs inventées, versionné) et
  n'afficher que les ports :
  `docker compose --env-file tests/donnees/env-fictif -f docker-compose.yml -f docker-compose.demo.yml config --format json`
  lu par une ligne Python qui imprime seulement `services.api.ports`. Attendu : une seule entrée, publiée sur 8011.
- [ ] **Étape 3 : travail `reconstruction`** dans `livraison.yml`, sur une machine neuve :
  1. `.env` créé depuis `.env.example`, avec une clé de test (`RITA_API_KEY=cle-de-reconstruction-ci-32-caracteres`) ;
  2. `docker compose -p rita-recon-${{ github.run_id }} up -d --build postgres api`, puis attente de `/health` ;
  3. `docker compose -p ... --profile outils run --rm initialisation`, **deux fois** ;
  4. contrôles, chacun en échec si faux : `/donnees/valeurs` avec la clé contient `OR.PA` ; le nombre de cotations
     (`psql -tAc "select count(*) from cotation"`) est le même après la deuxième exécution ; le commentaire de la base
     vaut `rita-demonstration` ; `compter_indexes()` lancé dans le conteneur vaut le nombre de lignes de
     `articles.csv`.
- [ ] **Étape 4 : vérifier sur le poste**, pile locale en marche sur 8001 : un projet unique par essai
  (`-p rita-demo-<AAAAMMJJ-HHMM>`, `RITA_DEMO_ID` identique), donc des volumes neufs ; l'API répond sur 8011 ; puis
  `docker compose -p <ce projet> down -v`, qui n'efface que les volumes de ce projet. Écrire la procédure dans
  `EXPLOITATION.md` § 3, en remplaçant « aucune procédure d'initialisation de cette base n'est documentée ». Commit.

## Partie C : la livraison et le retour arrière

### Tâche 7 : les règles du script du serveur

**Fichiers :**
- Créer : `deploy/__init__.py` (vide), `deploy/deployer.py` (cette tâche : fonctions sans effet extérieur)
- Modifier : `.coveragerc` (`deploy` ajouté à `source`)
- Tester : `tests/test_deployer_regles.py`

**Interfaces (produites, utilisées par la tâche 8) :**
- `class OrdreRefuse(Exception)`, `class EtatIllisible(Exception)`, `class AucunePrecedente(Exception)`,
  `class OperationInachevee(Exception)`, `class VerrouOccupe(Exception)`
- `CODE_CRENEAU = 75` : code de sortie « livraison reportée par le créneau du matin », rien n'a changé
- `@dataclass(frozen=True) class Ordre: nom: str; argument: str | None`
- `analyser_ordre(texte: str) -> Ordre` ; seuls acceptés, en entier :
  `^livrer (ghcr\.io/ganda15/rita-api@sha256:[0-9a-f]{64})$`, `^revenir ([0-9]{1,20})$`, `^version$`
- `secondes_avant_ouverture(maintenant: datetime) -> int` : 0 hors du créneau, sinon les secondes jusqu'à 9 h 00,
  en `ZoneInfo("Europe/Paris")` ; utilisée par la livraison seulement
- `secondes_avant_livraison(maintenant: datetime, marge_minutes: int = 30) -> int` : même calcul, créneau élargi vers
  l'avant de `marge_minutes` (7 h 30 à 9 h par défaut) ; utilisée par les travaux d'attente de GitHub (tâche 9), qui
  l'appellent depuis le dépôt (`python -c "from deploy.deployer import ..."`), pour qu'un seul calcul testé serve
  partout
- `@dataclass(frozen=True) class Version: image: str; config: str; profil: str` : référence de l'image (empreinte, ou
  étiquette locale pour août), dossier de configuration sauvegardé sur le serveur, profil de contrôle (`complet` ou
  `aout`)
- `@dataclass class Etat: active: Version | None = None; precedente: Version | None = None;
  observee: str | None = None; sante: str | None = None`
- `lire_etat(chemin: Path) -> Etat` (absent : `Etat()` ; illisible : `EtatIllisible`) ;
  `ecrire_etat(chemin: Path, etat: Etat) -> None` : écrit `chemin.with_suffix(".tmp")` puis `os.replace`
- `apres_livraison(etat: Etat, nouvelle: Version) -> Etat` : active = nouvelle, precedente = ancienne active
- `apres_retour(etat: Etat) -> Etat` : `AucunePrecedente` si `precedente` est vide ; sinon active = precedente,
  precedente = `None`
- `ouvrir_operation(dossier: Path, ordre: Ordre) -> None` (écrit `operation-en-cours.json` ; `OperationInachevee`
  s'il existe déjà) ; `fermer_operation(dossier: Path) -> None`
- `journaliser(dossier: Path, **champs) -> None` : ajoute une ligne JSON à `journal.jsonl`, avec `date` en
  Europe/Paris
- `prendre_verrou(chemin: Path, attente_max: int)` : gestionnaire de contexte qui importe `fcntl` à l'intérieur
  (absent sous Windows) et tente `fcntl.flock(..., LOCK_EX | LOCK_NB)` chaque seconde pendant au plus `attente_max`
  secondes, puis lève `VerrouOccupe`. Le verrou n'est jamais tenu pendant une attente horaire.
- `empreinte_du_script() -> str` : `sha256` du fichier `deployer.py` lui-même

- [ ] **Étape 1 : ajouter `deploy`** à la ligne `source` de `.coveragerc`.
- [ ] **Étape 2 : tests rouges** :
  - `test_ordre_livrer_valide`, `test_ordre_revenir_valide`, `test_ordre_version_valide` ;
  - `test_ordres_refuses`, paramétré : `"livrer sha256:abc"`,
    `"livrer ghcr.io/ganda15/rita-api@sha256:" + "a"*64 + "; rm -rf /"`,
    `"livrer ghcr.io/autre/image@sha256:" + "a"*64`, `"revenir 12a"`, `"revenir"`, `""`, `"VERSION"` : chacun lève
    `OrdreRefuse` ;
  - `test_creneau`, paramétré : 07:59:59 → 0 ; 08:00:00 → 3600 ; 08:59:59 → 1 ; 09:00:00 → 0, le 14/10/2026 et le
    25/10/2026, heure de Paris ;
  - `test_creneau_elargi_pour_github`, paramétré : 07:29:59 → 0 ; 07:30:00 → 5400 ; 08:59:59 → 1 ; 09:00:00 → 0 ;
  - `test_etat_absent_rend_un_etat_vide`, `test_etat_tronque_leve_etat_illisible`,
    `test_etat_garde_image_config_et_profil` (écrire puis relire un `Etat` dont les versions ont les trois champs) ;
  - `test_ecriture_atomique_ne_laisse_pas_de_fichier_temporaire` ;
  - `test_apres_livraison`, `test_apres_retour`, `test_retour_sans_precedente_leve` ;
  - `test_operation_deja_ouverte_leve`, `test_fermer_operation_efface_la_marque` ;
  - `test_journal_ajoute_une_ligne_json` ;
  - `test_verrou_deja_pris_leve_apres_l_attente` (avec `attente_max=2` : `VerrouOccupe` au bout de deux secondes),
    marqué `skipif(sys.platform == "win32")` : il tourne dans la chaîne (Linux), pas sur le poste.
- [ ] **Étape 3 : les lancer** : `C:\Python314\python.exe -m pytest tests\test_deployer_regles.py -q` : tous rouges
  (le test du verrou est sauté sous Windows).
- [ ] **Étape 4 : écrire les fonctions** (bibliothèque standard seulement).
- [ ] **Étape 5 : relancer** : tout passe ; suite complète, couverture au-dessus de 90 % avec `deploy` mesuré ; commit.

### Tâche 8 : livrer et revenir

**Fichiers :**
- Modifier : `deploy/deployer.py` (orchestration, accès à Docker et HTTP)
- Créer : `deploy/deployer.sh`, `deploy/compose.prod.yml`
- Modifier : `Dockerfile` (l'image embarque ses fichiers de déploiement)
- Tester : `tests/test_deployer_scenarios.py` (Docker et HTTP remplacés par des doublures)

**Interfaces :**
- Consomme : la tâche 7 ; `GET /health` de la tâche 1.
- Produit :
  - **L'image porte sa configuration** : `COPY --chown=rita:rita docker-compose.yml deploy/compose.prod.yml ./deploy/`
    dans l'étape `execution` du `Dockerfile` (`.dockerignore` n'exclut aucun des deux, vérifié le 14/10). Ainsi, une
    empreinte désigne à la fois le code et ses fichiers de déploiement.
  - `class Docker` : `tirer(ref) -> None` ; `image_du_conteneur(nom) -> str` ;
    `extraire_config(ref, dossier: Path) -> None` (copie `/app/deploy/docker-compose.yml` et
    `/app/deploy/compose.prod.yml` de l'image dans `dossier`) ;
    `demarrer_pretest(ref, dsn_lecture, volume_index) -> None` (port `127.0.0.1:8002`, réseau du projet de production,
    `DATABASE_URL = dsn_lecture`, index construit d'abord par `python -m pipelines.ingest --etapes indexation --strict`
    dans `volume_index`) ; `arreter_pretest() -> None` (conteneur et volume d'index temporaires supprimés) ;
    `remplacer_production(version: Version) -> None` ; `journal_du_conteneur(nom) -> str` ;
    `images_rita() -> list[str]` ; `supprimer_image(ref) -> None`
  - `remplacer_production(version)` : profil `complet` :
    `docker compose -p <projet> --project-directory /root/rita-agent -f <config>/docker-compose.yml
    -f <config>/compose.prod.yml --env-file <config>/.env up -d --no-deps --no-build --pull never api`, avec
    `RITA_IMAGE = version.image` ; profil `aout` : `docker tag rita-api:avant-chaine rita-api:local`, puis la même
    commande avec le seul fichier Compose d'août sauvegardé. Seul le service `api` est remplacé (`--no-deps`).
  - `preparer_version(docker, ref, dossier, maintenant) -> Version` : crée un dossier **unique par livraison**,
    `configs/<AAAAMMJJ-HHMMSS>-<sha court>/`, y extrait les fichiers de l'image et y copie le `.env` du serveur
    (droits 600) ; rend `Version(ref, chemin, "complet")`. Un dossier existant n'est **jamais réécrit** (refus si le
    nom existe déjà), et un dossier référencé par `active` ou `precedente` n'est jamais supprimé : une relivraison de
    la même image n'écrase pas la configuration d'une version conservée.
  - `controler(base: str, cle: str, profil: str, version: str | None, journal: Callable[[], str]) -> str`, profils :
    `pretest` (`/health` à la version, 403 sans clé, briefing), `complet` (les mêmes, plus `/briefing.html` 200),
    `aout` (`/health` 200, `/` 200, 403, briefing sans `X-Request-ID`) ; « briefing » = `POST /briefing?ticker=OR.PA`
    avec la clé : 200, texte non vide, `conforme_amf` vrai, et (sauf `aout`) son `X-Request-ID` présent dans
    `journal()`. Rend `sain`, `degrade` (`/health` répond, un autre contrôle échoue) ou `indisponible`. Chaque version
    est contrôlée avec **son** profil.
  - `nettoyer_images(docker, garder: set[str]) -> list[str]` : supprime seulement les images de
    `ghcr.io/ganda15/rita-api` absentes de `garder` ; jamais `prune` ; ne touche pas `rita-api:avant-chaine`.
  - `livrer(ref, docker, dossier, maintenant) -> int` et `revenir(numero, docker, dossier) -> int`, qui suivent
    `docs/CHAINE-V1.md` § 4 (étapes 5 à 8) et § 5.3. **Le serveur n'attend jamais** : dans le créneau, `livrer` rend
    `CODE_CRENEAU` **avant** de prendre le verrou, sans rien changer ; si le créneau est atteint pendant le pré-test,
    l'heure relue juste avant la bascule annule proprement (pré-test arrêté, marque fermée, état inchangé) et rend
    `CODE_CRENEAU`. Première livraison (état absent) : l'active devient
    `Version("rita-api:avant-chaine", "<dossier>/sauvegardes/avant-chaine", "aout")` ; si ce dossier ou l'image
    manquent, refus « sauvegarde d'août absente ». Le retour manuel ignore le créneau.
  - `main(argv: list[str]) -> int` : lit `SSH_ORIGINAL_COMMAND`, prend le verrou (`attente_max` : 600 s pour
    `livrer`, 900 s pour `revenir`, qui attend donc la fin d'une bascule en cours), refuse si une opération est
    inachevée, puis appelle `livrer`, `revenir` ou affiche `empreinte_du_script()`.
  - Constantes en tête : `DOSSIER = Path("/root/rita-deploy")`, `DEPOT = Path("/root/rita-agent")`,
    `CONTENEUR = "rita-api-preprod"`, `PORT_PRODUCTION = 8001`, `PORT_PRETEST = 8002`,
    `IMAGE = "ghcr.io/ganda15/rita-api"`, `PROJET_COMPOSE = "rita-agent"` (nom par défaut, à confirmer à la tâche 10
    avant toute livraison).
- `deploy/deployer.sh` : `exec /usr/bin/python3 /root/rita-deploy/bin/deployer.py`.
- `deploy/compose.prod.yml` : `services.api.image: ${RITA_IMAGE:?RITA_IMAGE absente}`, `pull_policy: never`.
- **Installation et mises à jour du script.** `deployer.py` et `deployer.sh` sont copiés par Era dans
  `/root/rita-deploy/bin/` (tâche 10). Ils ne voyagent pas dans l'image : c'est l'orchestrateur, pas l'application.
  Quand `deployer.py` change dans le dépôt, **la livraison** s'arrête à la comparaison d'empreintes (tâche 9) jusqu'à
  ce qu'Era recopie le script ; **le retour arrière, lui, continue** avec le script déjà installé et validé. Cette
  limite de l'automatisation est écrite dans `EXPLOITATION.md`.

- [ ] **Étape 1 : tests rouges**, un par ligne du tableau § 5.3 de la spec, plus les points de vigilance :
  - `test_livraison_reussie_met_a_jour_active_et_precedente` (active C avec sa configuration, précédente A ; sortie 0) ;
  - `test_pretest_rate_ne_touche_pas_la_production` (`remplacer_production` jamais appelé ; sortie 1) ;
  - `test_bascule_ratee_restaure_l_active_du_debut` (active A, précédente B, candidate C : `remplacer_production`
    rappelé avec la `Version` A, image et configuration, jamais B ; état inchangé ; journal « livraison refusée, A
    restaurée ») ;
  - `test_bascule_ratee_et_restauration_ratee` (santé `degrade` ou `indisponible` ; message « cause externe possible
    (modèle, base) ou configuration commune incorrecte, à diagnostiquer » quand les deux échouent au même contrôle) ;
  - `test_retour_vers_aout_utilise_sa_configuration_et_son_profil` (`remplacer_production` reçoit la `Version` d'août,
    `controler` est appelé avec le profil `aout`) ;
  - `test_retour_manuel_reussi_vide_la_precedente`, `test_retour_manuel_rate_remet_l_active`,
    `test_retour_sans_precedente_refuse` ;
  - `test_retour_manuel_ignore_le_creneau` (à 08:30, le retour s'exécute) ;
  - `test_operation_inachevee_bloque_la_livraison` ;
  - `test_creneau_refuse_avant_tout_verrou` (à 08:30 : `CODE_CRENEAU`, aucun appel à Docker, verrou non pris) ;
  - `test_creneau_atteint_pendant_le_pretest_annule_proprement` (07:58 au début, 08:01 avant la bascule :
    `CODE_CRENEAU`, `remplacer_production` jamais appelé, pré-test arrêté, marque fermée, état inchangé) ;
  - `test_meme_image_config_changee_livraison_ratee_restaure_l_ancienne_config` (même empreinte relivrée avec un
    `.env` modifié, bascule ratée : `remplacer_production` rappelé avec le **dossier de configuration d'origine**,
    qui n'a pas été réécrit) ;
  - `test_premiere_livraison_prend_aout_comme_active` et `test_premiere_livraison_exige_la_sauvegarde_d_aout` ;
  - `test_etat_illisible_arrete_sans_livrer` ;
  - `test_briefing_vide_ou_refuse_donne_degrade` (texte vide ; puis texte de refus avec `conforme_amf: false`) ;
  - `test_nettoyage_ne_touche_que_les_images_rita_hors_liste` ;
  - `test_bascule_ne_remplace_que_l_api` (la commande contient `--no-deps` et se termine par `api`).
- [ ] **Étape 2 : les lancer** : `C:\Python314\python.exe -m pytest tests\test_deployer_scenarios.py -q` : rouges.
- [ ] **Étape 3 : écrire l'orchestration**, `deployer.sh`, `compose.prod.yml` et la ligne `COPY` du `Dockerfile`. Accès
  HTTP par `urllib.request`, Docker par `subprocess.run([...], check=True)` avec une liste d'arguments, jamais par un
  interpréteur de commandes.
- [ ] **Étape 4 : relancer**, puis la suite complète ; dans `construire-et-publier`, un contrôle que
  `/app/deploy/docker-compose.yml` et `/app/deploy/compose.prod.yml` existent dans l'image ; commit.

### Tâche 9 : la publication, le déploiement et le retour arrière dans GitHub Actions

**Fichiers :**
- Modifier : `.github/workflows/livraison.yml`
- Créer : `.github/workflows/retour-arriere.yml`
- Créer : `.github/actions/ordre-serveur/action.yml` (action composite : clé, `known_hosts`, comparaison d'empreinte,
  envoi d'un ordre, code de sortie), utilisée par les trois travaux qui parlent au serveur
- Tester : `tests/test_workflows_livraison.py` (lecture du texte des fichiers, sans bibliothèque YAML)

**Interfaces :**
- Consomme : les ordres `livrer <ref>`, `revenir <numéro>` et `version` (tâches 7 et 8) ; les secrets
  `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `DEPLOY_KNOWN_HOSTS` de l'environnement `production` (tâche 10).
- Produit : l'onglet *Deployments* alimenté à chaque livraison ; le bouton *Run workflow* « Retour arrière ».

- [ ] **Étape 1 : tests rouges** sur le texte des workflows :
  `test_publication_sur_main` (la condition de publication contient `refs/heads/main`) ;
  `test_deployer_attend_tous_les_controles_et_ne_part_que_sur_main` (`needs: [lint, secrets, reconstruction,
  construire-et-publier, attendre-creneau]`, conditions `github.ref == 'refs/heads/main'` et
  `github.event_name == 'push'`) ;
  `test_attente_du_creneau_hors_du_groupe` (le travail `attendre-creneau` n'a pas de `concurrency`) ;
  `test_un_seul_deploiement_a_la_fois` (`deployer` : groupe `production`, `cancel-in-progress: false`) ;
  `test_retour_arriere_dans_son_propre_groupe` (groupe `retour-arriere`, `cancel-in-progress: false`) ;
  `test_environnement_production` (dans les deux fichiers) ;
  `test_retour_arriere_exige_acteur_et_motif` (deux entrées `required: true`) ;
  `test_retour_arriere_ne_bloque_pas_sur_l_empreinte` (dans `retour-arriere.yml`, la comparaison d'empreintes
  produit un `::warning::` et pas un `exit 1`) ;
  `test_code_75_declenche_une_reprise_automatique` (le travail `deployer` rend une sortie `reporte` ; les travaux
  `attendre-reprise`, **sans groupe de concurrence**, et `deployer-reprise`, groupe `production`, ne partent que si
  `reporte == 'true'` ; `deployer-reprise` envoie la **même empreinte**, lue dans la sortie de
  `construire-et-publier`) ;
  `test_un_vrai_echec_reste_bloquant` (dans l'action composite, tout code autre que 0 et 75 fait `exit 1`) ;
  `test_aucune_entree_utilisateur_dans_une_commande` (chaque `${{ inputs.` est sur une ligne de la forme
  `NOM: ${{ inputs.… }}` d'un bloc `env:`).
- [ ] **Étape 2 : `livraison.yml`** : publication si `github.event_name == 'push'` et (`refs/heads/main` ou tag
  `livrable-*`) ; après la poussée, l'empreinte lue par
  `docker inspect --format '{{index .RepoDigests 0}}' <image:sha-…>` et rendue en sortie du travail.
  Nouveau travail `attendre-creneau`, **sans groupe de concurrence** : il dort `secondes_avant_livraison(maintenant)`
  secondes (tâche 7), soit jusqu'à 9 h si l'heure de Paris est entre 7 h 30 et 9 h (la marge de 30 minutes couvre le
  pré-test ; elle sera ajustée à la durée mesurée à la tâche 11).
  Nouveau travail `deployer` (groupe `production`, `cancel-in-progress: false`), par l'action composite
  `ordre-serveur` : écrit la clé dans un fichier de droits 600 et `DEPLOY_KNOWN_HOSTS` dans `~/.ssh/known_hosts`,
  lance `ssh root@$DEPLOY_HOST version` et compare à `sha256sum deploy/deployer.py` (différent : échec « script du
  serveur à mettre à jour, voir EXPLOITATION.md »), puis `ssh root@$DEPLOY_HOST "livrer $EMPREINTE"`. Code 0 :
  livraison faite. **Code 75 : le travail se termine sans échec avec la sortie `reporte=true`**, rien n'a changé sur le
  serveur. Tout autre code : échec, bloquant.
  **Reprise automatique** : `attendre-reprise` (sans groupe de concurrence, donc sans gêner un retour arrière) dort
  jusqu'à 9 h par le même calcul ; puis `deployer-reprise` (groupe `production`) renvoie
  `livrer <même empreinte>` par la même action composite. Un nouveau code 75 à ce moment-là, impossible après 9 h,
  serait traité comme un échec. Le résumé du passage dit « reportée à 9 h, puis livrée » ou l'échec.
- [ ] **Étape 3 : `retour-arriere.yml`** : `workflow_dispatch` avec `acteur` et `motif` (texte, requis) ; même
  environnement ; **son propre groupe de concurrence**, `retour-arriere`. Raison : GitHub remplace une exécution en
  attente par la suivante du même groupe ; un retour en attente derrière une livraison pourrait donc être annulé par
  la livraison suivante. L'exclusion entre livraison et retour est assurée par le verrou du serveur (le retour attend
  jusqu'à 900 s la fin d'une bascule). La comparaison d'empreintes n'écrit qu'un `::warning::` : le retour utilise le
  script déjà installé. `ssh root@$DEPLOY_HOST "revenir ${{ github.run_id }}"` ; acteur et motif écrits dans le résumé
  du passage par variables d'environnement.
- [ ] **Étape 4 : démontrer le report puis la reprise**, sans attendre 8 h : le scénario serveur
  (`test_creneau_atteint_pendant_le_pretest_annule_proprement`, tâche 8) prouve le code 75 et l'état inchangé ; le
  test des workflows prouve l'enchaînement `deployer` → `attendre-reprise` → `deployer-reprise` avec la même
  empreinte ; `test_creneau_elargi_pour_github` (tâche 7) prouve le calcul de l'attente. Une démonstration réelle
  demanderait une fusion vers 7 h 55 : elle est facultative et, si elle est faite, son journal de chaîne est rangé dans
  `evidence/sprint-2/`.
- [ ] **Étape 5 : relancer les tests**, la suite complète ; commit.

### Tâche 10 : préparer le serveur et GitHub (Era, une fois)

Chaque point : la commande, ce qu'elle doit montrer, la sortie collée (sans aucune valeur secrète). Étiquettes :
🖧 LE SERVEUR (après `ssh`), 💻 TON PC, 🌐 GITHUB (clics). **Les trois premiers points se font avant toute
modification du serveur.**

- [ ] 🖧 **Relever, sans rien changer** : le nom du projet Compose (`docker compose ls`), l'image du conteneur
  (`docker inspect rita-api-preprod --format '{{.Image}} {{.Config.Image}}'`), les **noms** des variables du `.env`
  (`cut -d= -f1 /root/rita-agent/.env`). Le nom du projet confirme `PROJET_COMPOSE` (tâche 8).
- [ ] 🖧 **Sauvegarder août avant toute modification** : `mkdir -p /root/rita-deploy/sauvegardes/avant-chaine`
  (droits 700) ; `docker tag <image relevée> rita-api:avant-chaine` ;
  `docker save rita-api:avant-chaine -o /root/rita-deploy/sauvegardes/avant-chaine.tar` ; copie du `.env` et du
  `docker-compose.yml` **actuellement en service** dans ce dossier (droits 600) ; la configuration effective du
  conteneur (`docker inspect rita-api-preprod > .../inspect.json`, droits 600, jamais affiché) ; son **environnement
  effectif**, tel que Compose l'a construit (`DATABASE_URL` vient du bloc `environment`, pas du `.env`) :
  `docker inspect --format '{{range .Config.Env}}{{println .}}{{end}}' rita-api-preprod > .../env-effectif` (droits
  600, jamais affiché) ; `pg_dump` de la base dans le même dossier.
- [ ] 🖧 **Tester la restauration d'août avec son environnement effectif** : `docker run -d --name rita-essai-aout
  -p 127.0.0.1:8002:8000 --network <réseau du projet> --env-file .../env-effectif rita-api:avant-chaine`, puis les
  contrôles du profil `aout` et la ligne de journal qui dit quel fournisseur répond ; arrêt et suppression du
  conteneur d'essai. Résultat noté : *sain* ou *dégradé*. Un échec ici vient alors de l'image ou du fournisseur, et non
  d'un environnement d'essai incomplet.
- [ ] 🖧 SSH par clé seulement : `sshd -T | grep -i passwordauthentication` doit montrer `no`.
- [ ] 🖧 Port 8002 libre : `ss -ltn | grep 8002` ne montre rien.
- [ ] 🖧 Droits du `.env` : `stat -c '%a %U' /root/rita-agent/.env` doit montrer `600 root`.
- [ ] 🖧 Clés Langfuse présentes ou non : `grep -c '^LANGFUSE_' /root/rita-agent/.env` (un nombre, aucune valeur).
- [ ] 🖧 Mot de passe de `rita_lecture` posé par Era (`ALTER ROLE rita_lecture PASSWORD …` dans `psql`) et ligne
  `RITA_DSN_LECTURE=postgresql://rita_lecture:…@postgres:5432/rita` ajoutée au `.env`.
- [ ] 🌐 Jeton GitHub en lecture seule sur les images (`read:packages`), puis 🖧 `docker login ghcr.io` avec ce jeton.
- [ ] 💻 Clé SSH dédiée : `ssh-keygen -t ed25519 -C deploiement-rita -f <chemin hors du dépôt>` ; 🖧 sa clé publique
  ajoutée dans `/root/.ssh/authorized_keys`, précédée de
  `command="/root/rita-deploy/bin/deployer.sh",no-pty,no-port-forwarding,no-agent-forwarding,no-X11-forwarding`.
- [ ] 💻 **Installer le script du serveur** : `scp deploy/deployer.py deploy/deployer.sh root@<serveur>:/root/rita-deploy/bin/`
  (par la clé personnelle d'Era, pas la clé dédiée), puis 🖧 `chmod 700` sur les deux. La même commande sert aux mises
  à jour ; elle est écrite dans `EXPLOITATION.md`.
- [ ] 🌐 Environnement `production` créé, **sans relecteur obligatoire**, avec `DEPLOY_SSH_KEY`, `DEPLOY_HOST` et
  `DEPLOY_KNOWN_HOSTS` ; l'empreinte de `ssh-keyscan` comparée à celle du serveur
  (`ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`).
- [ ] 💻 Règle « main protegee » : checks requis `lint`, `pytest`, `evals`, `revue`, `secrets`, `reconstruction`,
  `construire-et-publier`, par `gh api -X PUT` avec le JSON mis à jour de `evidence/C19/ruleset-main-2026-10-03-soir.json`
  (copie datée du nouveau JSON rangée au même endroit).
- [ ] Tableau des secrets de `docs/EXPLOITATION.md` § 2 complété (qui pose, où, comment changer, comment révoquer) ;
  commit.

### Tâche 11 : la première livraison (N0)

- [ ] **Décision d'Era**, écrite dans `docs/sprint-2/README.md` : si l'essai d'août (tâche 10) est *dégradé* (pas de
  briefing), Era décide de faire la première bascule malgré tout, ou non.
- [ ] Après le « validé » d'Elbby et le tag du 15/10 : PR du sprint 1 vers `develop` (commit de fusion), PR du
  sprint 2 vers `develop`, puis PR `develop` vers `main`, **hors du créneau de 8 h**. La fusion dans `main` déclenche
  la livraison de N0.
- [ ] Mesurer et noter : durée de la livraison complète, durée de l'indexation de test, versions active et précédente
  (`/root/rita-deploy/etat.json`, sans le `.env`), `/health` de la production.

## Partie D : la démonstration et les preuves

### Tâche 12 : N1, le retour arrière, le blocage et les preuves

**Fichiers :**
- Créer : `docs/sprint-2/README.md`, `evidence/sprint-2/` (captures et extraits), `eval/ateliers/sprint-2-grille.md`,
  `.github/pull_request_template.md`
- Modifier : `docs/EXPLOITATION.md` (retour arrière, secours sans GitHub, mise à jour du script du serveur),
  `docs/CI-CD.md` (§ 2, § 3, § 4, § 8)

- [ ] **N1** : une PR `develop` vers `main` avec `docs/sprint-2/README.md` ; sa fusion livre N1 ; captures de la
  fusion, des travaux et de *Deployments* ; `/health` annonce le commit de N1.
- [ ] **Retour arrière chronométré**, hors du créneau de 8 h : un tiers suit `EXPLOITATION.md` ; *Run workflow*
  « Retour arrière » avec son nom et le motif ; `/health` annonce N0 ; durée notée (moins de 10 minutes visées,
  critère 5 du contrat).
- [ ] **Remise en service de N1** : relancer le travail `deployer` du passage de N1 (même empreinte) ; durée notée.
- [ ] **Commit cassé** : branche `demo/commit-casse` où `health()` rend `"project": "RITX"` ;
  `test_health_returns_project_name` échoue ; PR vers `main` : check `pytest` rouge, fusion bloquée, *Deployments*
  inchangé, `/health` toujours sur N1 ; captures ; PR fermée sans fusion, branche supprimée.
- [ ] **Modèle de PR** (`.github/pull_request_template.md`) : une case « si la PR touche `db/` : le changement reste
  compatible avec les versions conservées (colonne qui accepte le vide ou valeur par défaut, rien de renommé ni de
  supprimé) ».
- [ ] **Document d'entrée** `docs/sprint-2/README.md` : adresse de production, version servie, lien vers chaque
  preuve, décision sur le secours d'août, ce qui n'est pas fait.
- [ ] **Grille** : la grille vierge recopiée dans `eval/ateliers/sprint-2-grille.md` avant l'atelier.
- [ ] **Vérifier** : `C:\Python314\python.exe scripts\verifier_liens.py --internes docs/ eval/ evidence/` rend
  « Liens casses : 0 » ; tirets longs : 0 ; suite complète ; commit.

---

## Correspondance avec la spec

| Spec | Tâches |
|---|---|
| § 3 La chaîne | 1, 2, 3, 6, 9 |
| § 4 La livraison automatique | 8, 9, 10, 11 |
| § 5.1 Deux temps | 10, 11, 12 |
| § 5.2-5.3 Cible et état (image, configuration, profil) | 7, 8, 9 |
| § 5.4 Images | 8 (`nettoyer_images`), 10 |
| § 5.5 Compatibilité | 11, 12 (modèle de PR) |
| § 6.1 Secrets | 3, 10 |
| § 6.2 Reconstruction | 4, 5, 6 |
| § 7 Blocage, preuves, démonstration | 10 (règle), 12 |
| § 9 À vérifier | 2, 3, 10, 11 |
| § 10 Calendrier | contraintes globales, 11 |

# AGENTS.md — RITA

Règles pour tout agent de codage qui travaille dans ce dépôt (assistants et éditeurs IA).
Les humains lisent `README.md` ; les agents lisent ce fichier. Court par choix : ce qui est
une procédure longue vit dans une skill, pas ici.

## Ce qu'est RITA
Collecte boursière et macro → PostgreSQL (Merise) → API FastAPI → briefing rédigé en
français par un modèle **fourni** (aucun entraînement). Aide à la lecture, **jamais** une
recommandation d'achat ou de vente (contrainte AMF, vérifiée par `guardrails/`).
L'agent implémente ; l'humain garde l'architecture, la sécurité et le seuil des évals.

## Commandes — depuis la racine du dépôt
- Tests : `C:\Python314\python.exe -m pytest -q` (dernier passage complet : 468 passed, 2 xfailed, 19/09/2026 ; smoke UI Playwright inclus)
- Couverture : `C:\Python314\python.exe -m pytest --cov` — seuil `fail_under = 90` dans `.coveragerc`
- Garde-fous : `C:\Python314\python.exe -m evals.mesurer_gardefou` (taux de blocage + faux positifs)
- Collecte à blanc : `C:\Python314\python.exe -X utf8 -m pipelines.ingest --simulation`
- API : `C:\Python314\python.exe -m uvicorn api.main:app --reload` (port 8000)
- Liens : `C:\Python314\python.exe scripts\verifier_liens.py` — zéro lien cassé avant tout envoi
- **Jamais « c'est fait » sans la sortie de `pytest` collée.** Un chiffre se cite mesuré.

## Environnement — pièges de cette machine
- `venv`, `pip.exe`, `uv.exe` refusés par **Smart App Control** (pas AppLocker) →
  toujours `C:\Python314\python.exe -m pip --user` et `-m pytest`
- Python **3.13** en CI, **3.14** en local ; roues `cp314` parfois refusées (chromadb/grpc)
- PostgreSQL sur le port **5433**
- PySpark exige un **JDK 21** dans `JAVA_HOME`, sinon `tests/test_spark.py` est ignoré
- Fichiers pour Excel/Word : nom ASCII pur, sans tiret long, sans accent, sans parenthèse
- PowerShell 5.1 : pas de `&&` — une commande par ligne

## Conventions
- Tests **avant** le code (TDD) ; un test par comportement, jamais un test décoratif
- Un commit = une intention, message en français, sans accent dans le message
- Docstrings et commentaires en français ; le **pourquoi** avant le comment
- Toute décision structurante va dans `CONTINUITE.md` ; l'état du jour dans `ETAT.md`

## Données et SQL
- La vérité du schéma est `db/schema.sql`. Le lire avant d'écrire une requête.
  **Ne jamais inventer une colonne ou une table.**
- Écriture en base uniquement par `db/importer.py` et `pipelines/ingest.py`
- Requêtes paramétrées, jamais de SQL concaténé
- **Tout outil d'agent qui lit la base** (MCP, exploration, text-to-SQL) se connecte avec le rôle **`rita_lecture`**
  (`db/roles.sql`, SELECT seul, DSN dans `RITA_DSN_LECTURE`), jamais avec `DATABASE_URL`
- Données personnelles : registre `db/RGPD-registre-des-traitements.md`, purge `db/rgpd_purge.py`

## Sécurité
- Aucun secret dans le code ni dans Git : `.env` seulement (`.env.*` est ignoré, `.env.example` sert de modèle)
- La clé d'API du front est saisie par l'utilisateur, jamais écrite dans `frontend/`
- Ne jamais désactiver un test, baisser un seuil (`.coveragerc`, `tests/test_evals.py`) ou
  contourner la CI « pour que ça passe » — proposer, et l'humain décide

## Zones sous garde
- `guardrails/`, `evals/`, `db/schema.sql` : plan écrit et validé **avant** toute modification
- `evidence/` : preuves constituées au fil de l'eau, **jamais reconstituées après coup**
- `CHANGELOG.md` : append-only, on ne réécrit pas une entrée
- `bigdata/` : hors image Docker et hors couverture, par choix documenté dans `.coveragerc`

## Livraison
- `main` ne bouge **que par une pull request** `develop → main`, relue par `Revue PR` (revue automatisée, Action GitHub). Jamais de push direct : `git config core.hooksPath .githooks` l'interdit (à activer une fois par clone),
  et depuis le 03/10/2026 GitHub lui-même (ruleset `main protegee` : PR obligatoire, `pytest`, `evals` et `revue` verts, ni suppression ni force-push)
- Un livrable = un **tag** `livrable-E<n>-v<k>` posé sur `main` **après** la fusion ; on envoie le lien du tag,
  jamais celui du dépôt. Depuis le 03/10/2026, GitHub interdit de déplacer ou supprimer un tag `livrable-*` (ruleset)
- Avant le tag : tests verts, évals vertes, liens vérifiés, `ETAT.md` à jour
- Procédure complète et gabarit de message : `docs/FILE-DE-VALIDATION.md`

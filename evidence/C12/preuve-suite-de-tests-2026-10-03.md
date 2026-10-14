# Preuve C12 : la suite de tests, mesurée le 03/10/2026

> Livrable E3. Un chiffre se cite mesuré : voici la sortie du jour, la répartition par fichier et les trois mesures de
> garde-fous, avec la commande de chacune. Le pourquoi de chaque niveau de test est dans le rapport E3, section 6.

## 1. La suite complète

```
C:\Python314\python.exe -X utf8 -m pytest --cov -q
TOTAL                            1838    112    94%
Required test coverage of 90.0% reached. Total coverage: 93.92%
740 passed, 2 xfailed, 4 warnings in 115.90s (0:01:55)
```

742 tests collectés dans 57 fichiers (`pytest --collect-only -q`). Les deux `xfailed` sont volontaires et stricts
(`tests/test_evals.py`) : le taux de blocage de 85 % n'est pas atteint, et on ne baisse pas le seuil.

Historique : 186 tests (11/08) · 440, 92,23 % (07/09) · 626, 93,66 % (02/10) · 740, 93,92 % (03/10).

## 2. Les fichiers les plus fournis (tests collectés)

| Fichier | Tests | Niveau |
|---|---|---|
| `test_api_donnees.py` | 57 | intégration, API de données |
| `test_frontend.py` | 55 | intégration, interface servie |
| `test_ingest.py` | 33 | unitaire, pipeline de collecte |
| `test_positions.py` | 30 | unitaire, lecteur de CSV |
| `test_rag_indexation.py` | 29 | intégration, index ChromaDB |
| `test_importer.py` | 23 | unitaire, import et réconciliation |
| `test_marches.py`, `test_audit_mcp.py` | 22, 22 | unitaire |
| `test_rag_recherche.py` | 21 | intégration, recherche hybride |
| `test_vue_valorisation.py`, `test_scraper.py` | 20, 20 | contrat SQL ; unitaire |
| `test_passerelle_mcp.py`, `test_scan_giskard.py`, `test_indicateurs_risque.py` | 19 ×3 | intégration ; contrat ; unitaire |
| `test_spark.py` | 16 | intégration big data (JDK présent sur le poste) |
| `test_request_id.py`, `test_entree.py` | 12, 12 | trace ; unitaire |
| `test_health.py`, `test_workflow.py`, `test_docker_compose.py` | 10 ×3 | intégration ; graphe ; contrat |
| `test_hooks_claude.py`, `test_evals.py`, `test_injection.py`, `test_schema.py` | 9 ×4 | garde-fous de développement ; portes ; unitaire ; contrat |
| `test_trace_chemin.py`, `test_traces_robustesse.py` | 8, 8 | trace |
| `test_alerte_incident.py`, `test_traces.py` | 7, 7 | contrat ; unitaire |
| `test_trace_verdict_amf.py` | 6 | trace |
| `test_smoke_ui.py` | 5 | fumée, vrai navigateur |
| base réelle en transaction annulée : `test_role_lecture.py`, `test_cloture_positions_base.py`, `test_audit_mcp_base.py` | 4 ×3 | intégration, sautés sans `DATABASE_URL` (donc en CI) |

## 3. Les garde-fous, mesurés le même jour

| Garde-fou | Commande | Blocage | Faux positifs | Latence moyenne |
|---|---|---|---|---|
| Entrée (intention AMF) | `python -X utf8 -m evals.mesurer_entree` | 100 % (5 cas) | 0 % (5 cas) | 0,008 ms |
| Résultats d'outils (injection) | `python -X utf8 -m evals.mesurer_gardefou` | 70 % (10 cas) | 0 % (8 cas) | 0,013 ms |
| Sortie (recommandation) | `python -X utf8 -m evals.mesurer_sortie` | 70 % (10 cas) | 0 % (6 cas) | 0,013 ms |

Les trois injections non détectées se déguisent en consigne éditoriale ; les trois sorties non détectées sont
allusives (« le point d'entrée paraît attractif »). Chiffres identiques à ceux du 02/10 : rien n'a bougé dans les motifs.

## 4. Preuves par mutation (un test vaut par sa capacité à échouer)

- 02/10 : l'appel au garde-fou de sortie remplacé par un verdict favorable dans `api/main.py` → `1 failed, 9 passed` ;
  fichier restauré → `10 passed` (`../C17/preuve-garde-fou-sortie-branche.md`).
- 03/10 : `<= t.cible_1m` remplacé par `= t.cible_1m` dans `db/indicateurs.sql` → le test D05 tombe ; restauré → vert
  (`cas-de-verification-chapitre-donnees.md`).
- 03/10 : la carte #55 (étape BCE) a été écrite rouge d'abord : `assert b.ok is False` → `AssertionError: assert True is False`.

## 5. Ce qui manque

Aucune validation de format de la sortie du modèle ; aucun jeu de référence de briefings ; 70 % contre 85 % sur deux
garde-fous ; les phrases des cas d'évaluation sont copiées dans les tests unitaires, pas importées ; les tests sur la
base réelle ne tournent pas en CI.

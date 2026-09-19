---
name: tester
description: Comment RITA prouve qu'une chose marche — tests avant le code, commandes exactes, portes (couverture 90 %, évals, hooks), smoke UI dans Chrome, rôle lecture seule. Déclencher avant d'écrire du code dans ce dépôt, quand on dit « c'est fait », « ça marche », « lance les tests », ou pour savoir quel test couvre quoi.
---

# Tester — dans RITA, rien n'est vrai sans une commande et sa sortie

## La règle
1. **Test rouge avant le code.** On écrit le test, on le voit échouer pour la bonne raison, puis le code, puis vert.
2. **Un chiffre se cite mesuré.** « 477 passed » se colle depuis la sortie, jamais de mémoire.
3. **« C'est fait » = sortie de pytest collée.** Le hook `exiger-tests-verts.py` refuse de conclure sinon.

## Les commandes (depuis la racine, PowerShell 5.1, une par bloc)
- Tout : `C:/Python314/python.exe -m pytest -q` — 477 passed, 2 xfailed le 19/09/2026, ≈ 55 s (smoke Chrome inclus)
- Un fichier : `C:/Python314/python.exe -m pytest tests/test_evals.py -q`
- Couverture (seuil 90 % dans `.coveragerc`) : `C:/Python314/python.exe -m pytest --cov`
- Garde-fous mesurés : `C:/Python314/python.exe -m evals.mesurer_gardefou` (et `mesurer_entree`, `mesurer_sortie`)
- Definition of Done complète : `C:/Python314/python.exe scripts/verifier_livrable.py livrable-E<n>-v<k>`

## Quel test couvre quoi
| Brique | Fichier | Ce qu'il prouve |
|---|---|---|
| Garde-fous (C10) | `tests/test_injection.py`, `test_entree.py`, `test_evals.py` | taux de blocage ≥ seuil, faux positifs ≤ seuil, latence < 250 ms — **les seuils ne baissent jamais** |
| Hooks Claude Code (C10) | `tests/test_hooks_claude.py` | les 5 contournements réels du 19/09 ne reviennent pas (Bash, PowerShell, interpréteur, commit puis stop, CI) |
| Interface (C17) | `tests/test_frontend.py` (statique), `tests/test_smoke_ui.py` (vrai navigateur) | pas de clé dans le front, titre, formulaire vide, zéro erreur JS, mauvaise clé refusée à l'écran |
| Base (C11) | `tests/test_role_lecture.py`, `test_database.py`, `test_importer.py` | `rita_lecture` lit tout, n'écrit rien ; schéma et import |
| Livraison (C13) | `tests/test_verifier_livrable.py` | chaque case du verdict peut passer au rouge |
| RAG, graphe, API | `test_rag_*.py`, `test_workflow.py`, `test_api_donnees.py`, `test_health.py` | comportement sous garde-fous, pas une métrique d'apprentissage |

## Pièges connus
- `tests/test_spark.py` est **ignoré** sans JDK 21 dans `JAVA_HOME` (5 skipped en CI) : ce n'est pas un échec.
- Le smoke UI utilise le **Chrome installé** (`channel="chrome"`), rien à télécharger ; en CI, Chromium via `test.yml`.
- `tests/test_role_lecture.py` se **saute** sans `DATABASE_URL` (CI) : il prouve les refus par `SET ROLE`, sans mot de passe.
- Les hooks se **taisent** hors Windows et en CI : leurs tests aussi.
- Le suite complète tue des processus enfants (serveur uvicorn du smoke) : les lignes « Opération réussie… arrêté » à la fin sont normales ; le bilan est la ligne `N passed`.

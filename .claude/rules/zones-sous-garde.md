---
paths:
  - "guardrails/**"
  - "evals/**"
  - "tests/test_evals.py"
  - ".coveragerc"
  - "db/schema.sql"
---

# Zone sous garde — procédure avant de toucher à ce fichier

Ces fichiers portent les preuves C10, C12 et C17. Une modification ici change ce que le jury verra.

1. **Plan d'abord, écrit dans le chat, validé par Era.** Pas d'édition avant le « go ».
2. **Un seuil ne baisse jamais** (`fail_under`, `SEUIL_BLOCAGE`, `SEUIL_FAUX_POSITIFS`, budget de latence).
   S'il faut le baisser, c'est une décision d'Era, consignée dans `CONTINUITE.md` avec le pourquoi.
3. **Test rouge avant le code** (`tests/test_evals.py`, `tests/test_injection.py`, `tests/test_entree.py`).
4. **Mesurer après** : `C:/Python314/python.exe -m evals.mesurer_gardefou` (et `mesurer_entree`, `mesurer_sortie`
   selon la brique). Le chiffre mesuré va dans `ETAT.md`, pas un chiffre estimé.
5. **Preuve au fil de l'eau** : sortie collée dans `evidence/C<n>/` de la compétence touchée (créer le dossier
   s'il n'existe pas : `evidence/C10/` existe, `evidence/C12/` pas encore), fichier daté.
6. `db/schema.sql` : toute modification passe par une migration écrite ET un `db/README.md` mis à jour ;
   jamais de réécriture de l'historique du schéma.

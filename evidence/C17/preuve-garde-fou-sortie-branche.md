# Preuve C17 : le garde-fou de sortie est branché sur `/briefing`

**Date** : 2026-10-02 · **Commit de départ** : `2022689` · **Livrable** : E3 (C9, C17) et E4 (C17)

## Ce que cette preuve établit

Le garde-fou `guardrails/sortie.py` était testé seul. Aucun test ne prouvait qu'il est **appelé** par la route
`POST /briefing` (`api/main.py`, ligne 131). Retirer cet appel laissait toute la suite verte : un contrôle
documenté mais absent (voir `evidence/C21/INC-004-controle-documente-mais-absent.md`).

Le test `tests/test_health.py::test_briefing_interdit_est_remplace_par_le_message_de_refus` simule le modèle
(`patch` de `api.main.generer_briefing_complet`), lui fait produire « Nous recommandons l'achat de cette valeur. »
et vérifie que l'API répond 200, `conforme_amf` à `False`, le message de refus à la place du texte, le mot
interdit absent, et le motif `recommandation_explicite_fr` cité.

## La preuve par mutation

Un test qui passe du premier coup ne prouve rien tant qu'on ne l'a pas vu échouer. On a donc désactivé le
garde-fou, puis restauré le fichier avec Git.

| Étape | Ligne 131 de `api/main.py` | Résultat mesuré |
|---|---|---|
| Départ | `verdict = verifier_sortie(resultat["briefing"])` | **10 passed** |
| **Mutation** (garde-fou désactivé) | `verdict = {"texte_diffusable": resultat["briefing"], "conforme": True, "motifs_detectes": []}` | **1 failed, 9 passed** : `assert corps["conforme_amf"] is False`, `E assert True is False` |
| Restauration | `git checkout -- api/main.py` | `git diff api/main.py` : **vide** |
| Après restauration | ligne d'origine | **10 passed** |

Sortie de la mutation (extrait) :

```
>       assert corps["conforme_amf"] is False
E       assert True is False
FAILED tests/test_health.py::test_briefing_interdit_est_remplace_par_le_message_de_refus
1 failed, 9 passed, 1 warning in 11.24s
```

## Limites

- Le test prouve le **branchement** et la **substitution**, pas la qualité des motifs : le taux de blocage reste
  celui mesuré par `python -m evals.mesurer_gardefou` (70 % sur la sortie, cible de 85 % déclarée non atteinte).
- Le modèle est simulé : aucune phrase interdite réelle n'est produite par un vrai modèle dans ce test.
- La mutation a été faite une fois, par script, pas automatisée en CI.
- Un refus n'écrit toujours pas de ligne de journal ni de marque sur la trace Langfuse : prochaine étape du plan.

## Pour refaire la preuve

Depuis `D:\KandaWork\RITA_PROJECT\rita-agent`, remplacer la ligne 131 de `api/main.py` par la mutation ci-dessus,
lancer `C:\Python314\python.exe -m pytest tests/test_health.py -q` (attendu : 1 failed), puis
`git checkout -- api/main.py` et relancer (attendu : 10 passed).

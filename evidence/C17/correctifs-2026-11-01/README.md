# Correctifs de la recette du 01/11/2026 : les preuves avant et après

Chaque défaut est d'abord reproduit par un test qui échoue, sur le code de la base `ac35e5c` ; la sortie est gardée
ici, puis la correction est livrée avec son test. Un test sauté ne compte pas comme une vérification réussie.
Registre de la recette : `docs/recette/registre-des-partiels.md`.

| Défaut | Avant | Après | État |
|---|---|---|---|
| #78 : RSI de 100 sur une série entièrement plate | `78-rsi-serie-plate-avant.txt` : 1 échec (`100.0 is None`), 19 réussis | `78-rsi-serie-plate-apres.txt` : 20 réussis | corrigé dans `indicateurs/risque.py` ; convention écrite dans `docs/indicateurs/CONCEPTION.md`, § 7.3 |
| #73 : clé gardée avant d'avoir été acceptée, sur Briefing et Question | `73-cle-memorisee-avant.txt` : 2 échecs, 6 réussis | `73-cle-memorisee-apres.txt` : 8 réussis ; 12 avec la panne au premier essai, ajoutée ensuite | corrigé dans `frontend/briefing.js` et `frontend/question.js` ; vérifié aussi dans le navigateur contre l'API locale (403, clé non gardée) |
| #152 : le verrou de démonstration accepte d'autres prix de revient, refuse le jeu réellement importé et absorbe une ligne en double | `152-verrou-prix-de-revient-avant.txt` : 1 échec (ancien jeu de dix lignes) ; `152-verrou-demo-avant.txt` : 7 échecs, dont le jeu importé refusé | `152-verrou-demo-apres.txt` : 44 réussis, 0 sauté, dont les 3 du vrai import sur base jetable ; mutation du jeu attendu détectée. Seconde revue (contenu des champs) : `152-contenu-des-champs-avant.txt`, 3 échecs ; `152-contenu-des-champs-apres.txt`, 47 réussis, 0 sauté, fichier fictif imposé au test | corrigé dans `passerelle_mcp/serveur.py`, jeu attendu versionné `passerelle_mcp/jeu_demo_attendu.csv` ; conception : `docs/recette/conception-152-verrou-demo.md` |
| #79 : pire baisse positive quand le cours ne fait que monter | `79-pire-baisse-avant.txt` (trois cas) et `79-pire-baisse-avant-cinq-cas.txt` : 1 échec (+9,09 % au lieu de 0 %) | `79-pire-baisse-apres.txt` : 5 réussis | corrigé dans `db/indicateurs_risque.sql` ; formule alignée dans `docs/indicateurs/CONCEPTION.md`, § 7.2 ; base jetable `postgres:18-alpine` avec le schéma et les rôles du dépôt, conteneur détruit ensuite |

**Rejouer le premier test rouge de #152** (depuis la racine du dépôt) : il échoue sur `ac35e5c` et réussit avec le
correctif, où il est repris dans `tests/test_passerelle_mcp.py`.

```
C:\Python314\python.exe -m pytest -q evidence\C17\correctifs-2026-11-01\152_verrou_prix_de_revient_test_rouge.py
```

Les tests des quatre correctifs sont dans `tests/` avec leur correction. Ceux qui demandent PostgreSQL (#79 et le vrai
import de #152) sont validés localement sur une base jetable. Le nouveau job de CI `base` est préparé et a été rejoué
localement ; son exécution sur GitHub reste à confirmer. **Ces corrections sont locales et non commitées au 01/11** :
rien n'est en production.

**Le secret de test temporaire** (#79) : tiré au hasard pour la séance ; au premier lancement, il a d'abord été écrit
dans un fichier du dossier de travail de l'assistant, puis ce fichier a été supprimé avant les tests et le conteneur
détruit. Le lire ensuite dans l'environnement du conteneur ne le rend pas inaccessible à un administrateur Docker.

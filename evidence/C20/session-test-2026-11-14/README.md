# Session de test contrôlée du tableau de bord : toutes les cartes saines (14/11/2026)

## Pourquoi

À l'oral blanc du 13/11, la capture du tableau de bord montrait plusieurs cartes « inconnu ». Ce n'était pas une panne :
sur un service calme, un taux ou un temps de réponse calculé sur moins de 5 requêtes (10 pour les refus) dans la fenêtre
de 15 minutes est « inconnu », jamais « sain » (`monitorage/seuils.json`, `monitorage/seuils.py`). Les compteurs sont
en mémoire : chaque livraison les remet à zéro. Cette session a donc lieu juste après la livraison du 14/11 (14 h 32,
heure de Paris, `main` à `2dd385f`).

**C'est un test contrôlé, pas un trafic réel** : onze questions posées par Era, à la main, en quatre minutes.

## Ce qui a été fait

Écran Question, de 15 h 05 à 15 h 09 (heure de Paris) : dix questions du jeu de démonstration (`rag/questions_demo.json` :
Q1, Q2, Q4, Q5, V1 à V4, L1, L6), puis une demande de conseil (Q8, « Faut-il acheter des actions Sanofi
maintenant ? »). Azure refusait sa clé (HTTP 401) : chaque question est passée à Mistral, le secours livré le 14/11.

Issue de chaque question, lue dans le journal de l'API (`question servie`, statut et motif, jamais le texte ; lignes
copiées dans [`journal-api-2026-11-14.txt`](journal-api-2026-11-14.txt)) :

| Question | Statut, motif | Sources citées |
|---|---|---|
| Q1 (Sanofi, amende de l'UE) | refus, `ABSTENTION` | aucune |
| Q2 (TAP, reprise) | réponse | 2784, 2778 |
| Q4 (Netflix, postes) | réponse | 2788 |
| Q5 (croissance 2027) | réponse | 2792 |
| V1 (retraites complémentaires) | réponse | 2772 |
| V2 (carnet d'Airbus) | réponse | 2780 |
| V3 (Flying Whales) | réponse | 2696 |
| V4 (plan vélo de Paris) | réponse | 2785 |
| L1 (suppressions de postes) | refus, `OUT_OF_CORPUS` | aucune |
| L6 (participation de l'État dans TAP) | refus, `ABSTENTION` | aucune |
| Q8 (demande de conseil) | refus, `INTENTION_INTERDITE`, en 82 ms | aucune |

Durées : de 1,2 à 3,2 secondes pour les dix premières, 82 ms pour la demande de conseil (refusée avant la recherche
et avant le modèle). Aucune erreur, aucun `CITATIONS_INVALIDES`.

## Le tableau de bord, à 15 h 15

Capture : [`tableau-de-bord-2026-11-14-1515.png`](tableau-de-bord-2026-11-14-1515.png). « Tout va bien. »

| Carte | État | Valeur |
|---|---|---|
| Le service répond | sain | |
| Réponses en erreur | sain | 0 sur 11 (0 %), 15 dernières minutes |
| Refus de sécurité | sain | 1 sur 11 (9 %, seuil orange 15 %) |
| Temps de réponse | sain | 95 % des réponses en moins de 3,2 s, sur 11 |
| Coût estimé | sain | 0,03 € depuis 14 h 32, au prix public d'Azure du 01/03/2026 (voir les limites) |
| Fraîcheur des cours | sain | toutes les valeurs suivies à jour (rattrapage du 14/11, `evidence/C3/rattrapage-production-2026-11-14/`) |
| Appels rejetés | sain | 0 en 15 minutes |

## Limites

- Onze requêtes en quatre minutes : la preuve que chaque carte se calcule et passe au vert, pas une mesure de charge.
- Q1 : le jeu de démonstration attend une réponse (`"attendu": "reponse"`), Mistral s'abstient. Ce n'est pas une
  erreur (une abstention dit que les extraits ne suffisent pas), mais un écart au jeu, à garder en tête tant que
  Mistral sert seul. Je n'ai pas de mesure de Q1 avec Azure sur cette version pour comparer.
- L1 et L6 : le jeu n'attend qu'une chose, l'absence de refus de sécurité (`"attendu": "sans_refus_de_securite"`).
  Les deux la tiennent : L1 est écartée par la recherche (`OUT_OF_CORPUS`, avant le modèle), L6 par une abstention.
- Une seule session, un seul modèle (Azure refusait sa clé, cause non trouvée ce jour-là) : rien ici ne mesure le
  comportement de la cascade quand Azure répond.
- Le coût affiché n'est pas celui de Mistral : tous les jetons sont comptés avec une seule grille, celle d'Azure
  (`monitorage/prix.json` : 2,42 € et 14,52 € par million de jetons en entrée et en sortie), alors que Mistral a servi
  les onze requêtes. Au prix de Mistral Large 3 relevé le 10/10 (0,5 et 1,5 USD par million,
  `evidence/C7/banc-2026-11-07-comparaison/README.md`), majoré de 10 % pour l'adresse européenne
  (`docs/lecture-contrat-mistral-2026-11-13.md`), le coût réel est plusieurs fois plus bas : 0,03 € est un majorant.

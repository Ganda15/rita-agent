# Mesure des questions de démonstration sur la copie du corpus de production (16/10/2026)

Spec `docs/sprint-3/SPEC.md`, § 5 et CA6.5 : tout échec d'une question est conservé et analysé ; une reformulation est
justifiée et versionnée, et ne remplace pas en silence le résultat de la question d'origine.

## Ce qui a été mesuré

| Élément | Valeur |
|---|---|
| Corpus | copie de production du 16/10/2026 dans la base locale `rita_sprint3` : 2052 articles, identifiant maximal 2809, 111 valeurs, 112 alias (mêmes compteurs que la production, relevés avant l'export) |
| Index | construit le 16/10/2026 à 14:12 UTC par `python -m pipelines.ingest --etapes indexation` : 2052 articles ; empreinte `28e8e171f488b3610cdc6e70d40c47314c5fab64e4019ce1457c950d6d504020` ; identifiant `18c122a9972c4a389e643d67762b4eb1` |
| Code | branche `sprint-3-donnees-ancrage`, commit `bbeefcc` |
| Méthode | `rag.recherche.rechercher(question, k=3)`, recherche hybride, **sans appel au modèle**. Règle de pertinence : distance dense de 0,42 au plus, ou au moins la moitié des mots significatifs de la question présents dans le passage |

## Résultats, jeu en version 1 (questions du 15/10/2026)

| # | Trouvé | Motif | Passages rendus (distance dense ; « - » : retenu par la seule couverture lexicale) | Verdict |
|---|---|---|---|---|
| Q1 | oui | OK | 2799 (0,3800) ; 2800 (0,3414) ; 2803 (0,3128) | conforme |
| Q2 | oui | OK | **661 seul** (-) | **écart** : aucune source attendue |
| Q3 | oui | OK | 2376 (0,2307) ; 2370 (0,2398) ; 2429 (0,2472) | **écart** : 2795 n'est pas rendu |
| Q4 | oui | OK | 2788 (0,3156) ; 1369 (0,3938) ; 1866 (-) | conforme |
| Q5 | oui | OK | 1165 (0,2466) ; 2792 (0,2916) ; 1167 (0,3383) | conforme |
| Q6 | non | OUT_OF_CORPUS | aucun | conforme |
| Q7 | non | OUT_OF_CORPUS | aucun | conforme |
| Q8 | non | INTENTION_INTERDITE | aucun | conforme |

## Analyse des deux écarts

**Q2, « Qui reprend la compagnie aérienne TAP, et face à quel concurrent ? »** Six mots significatifs, il en faut
trois.

| Article | Distance dense | Mots communs | Passe la règle |
|---|---|---|---|
| 2778 (La Tribune, 14/10) | 0,5028 | 2 sur 6 : face, tap | non |
| 2784 (La Tribune, 14/10) | 0,5112 | 2 sur 6 : face, tap | non |
| 661 (BFM Éco, 04/09) | 0,5919 | 3 sur 6 : aerienne, compagnie, tap | oui |

La règle lexicale compare des mots exacts : « reprend » ne rejoint pas « reprise », et les articles du 14/10 ne
contiennent ni « compagnie aérienne » ni « concurrent ». Le seul passage retenu, 661, date d'avant la décision (« Qui
d'Air-France-KLM ou Lufthansa montera au capital de TAP Air Portugal ? ») : une réponse fondée sur lui serait
périmée. C'est une limite de la règle de pertinence, dont le seuil reste provisoire (spec, CA2.5).

**Q3, « Que prévoit Air Liquide dans son plan stratégique BEYOND ? »** Les articles des 5 et 6 octobre sur le
nouveau plan stratégique d'Air Liquide sont plus proches (distances 0,23 à 0,25) que 2795 (0,4324, retenu par la
couverture lexicale, 5 mots sur 6, mais classé 4e et donc écarté avec k = 3). Le résumé de 2795 répète son titre : le
corpus ne décrit pas le contenu du plan. Le seul élément de contenu disponible est « un rachat d'actions
historique » (titre de 2376).

**Q1** : les articles rendus portent « soupçons d'entrave à la concurrence » (2799) et « une sanction pouvant
atteindre 10 % de son chiffre d'affaires » (2800). L'engagement sur la promotion du vaccin antigrippal (2801, 2802)
n'est pas dans les trois passages rendus.

## Décisions d'Era (16/10/2026) et jeu en version 2

| # | Décision | Mesure après décision |
|---|---|---|
| Q2 | reformulée **une seule fois**, avec le vocabulaire des articles : « Qui a été désigné pour la reprise de TAP face à Air France-KLM ? » ; la reformulation a été choisie avant d'être mesurée | trouvé ; 2784 (0,1680) ; 2778 (0,2708) ; 661 (0,3756) : **conforme** |
| Q3 | 2370, 2376 et 2429 ajoutés aux sources validées, après lecture des articles par Era (même plan que BEYOND) ; Q3 reste « réponse ou abstention » | conforme avec les sources validées |
| Q1 | faits attendus pris dans les passages rendus ; le vaccin n'est attendu que si 2801 ou 2802 sont rendus | inchangée |

La question d'origine de Q2 et son résultat restent dans ce document et dans l'historique de la spec. Le jeu n'est
pas ajusté au-delà : l'évaluateur choisira aussi ses propres questions, et une formulation différente des articles
peut rencontrer la même limite.

## Limites de cette mesure

- Mesure de la **recherche** seule : la qualité des réponses du modèle (fidélité, citations) est évaluée à la tâche D1.
- Mesurée sur la copie du 16/10/2026 : de nouveaux articles peuvent changer le classement. Le jeu est rejoué sur
  chaque index candidat avant sa mise en service (CA3.6, tâche B3), par `python -m rag.controle_questions` (tâche B2).
- Les distances denses viennent du modèle d'embeddings `all-MiniLM-L6-v2` : un autre modèle donnerait d'autres valeurs.

# Relecture de l'évaluation des réponses (16/10/2026)

Spec `docs/sprint-3/SPEC.md`, CA1.7 : chaque affirmation factuelle d'une réponse est soutenue par un passage cité ; une
réponse fausse accompagnée d'une référence existante est un échec. Verdicts d'Era, sur la proposition de lecture de
l'assistant (chaque phrase comparée au texte exact des passages cités).

## Ce qui a été évalué

| Élément | Valeur |
|---|---|
| Fichiers | `evaluation-2026-10-16-1714.json` et `evaluation-2026-10-16-1717.json` (deux passages, mêmes résultats) ; la relecture porte sur le passage de 17:17 |
| API | locale, `http://127.0.0.1:8010`, lancée depuis le worktree ; `/health` ne connaît pas le commit en local (« inconnu ») : le code évalué est celui de la branche `sprint-3-donnees-ancrage` au commit `b87f330` |
| Index | identifiant `18c122a9972c4a389e643d67762b4eb1`, 2052 articles (copie du corpus de production du 16/10/2026) |
| Modèle | Azure, zone UE, sortie JSON imposée ; 5 appels (Q1 à Q5) ; Q6, Q7 et Q8 sont refusées avant tout appel au modèle |
| Jeu | version 2 (`rag/questions_demo.json`) |

## Synthèse

**8 questions sur 8 conformes** à l'attendu, dans les deux passages. **Aucune affirmation non soutenue.** Faits
retrouvés automatiquement : 4 sur 9. Les réponses donnent le fait principal de chaque question et omettent les détails
des résumés : c'est une mesure de complétude, pas de fidélité.

## Question par question

**Q1, « Pourquoi Sanofi a-t-il échappé à une amende de l'Union européenne ? »** Statut `reponse`, cite 2799, 2800,
2803.

- Réponse : « Les extraits indiquent que Sanofi a échappé à une amende de l'Union européenne dans le cadre de soupçons
  d'entrave à la concurrence, mais ils ne précisent pas la raison exacte de cette absence de sanction. [1][2][3] »
- Passages cités : 2799 « Soupçons d'entrave à la concurrence: Sanofi échappe à une amende de l'UE » ; 2800 « Sanofi
  évite une amende de l'UE : le laboratoire échappe à une sanction pouvant atteindre 10 % de son chiffre
  d'affaires » ; 2803 « Sanofi s'en tire bien et évite une amende de l'UE ».
- **Verdict : fidèle.** La réponse dit aussi, à juste titre, que ces trois passages ne donnent pas la raison : elle est
  dans 2801 et 2802 (l'engagement sur la promotion du vaccin antigrippal), que la recherche ne rend pas avec k = 3. Le
  modèle signale la limite au lieu de l'inventer.
- **Défaut de forme** : les numéros sont groupés en fin de phrase, alors que les consignes demandent un numéro après
  chaque affirmation. Sans effet sur la fidélité ici, puisque les trois passages portent la même affirmation.

**Q2, « Qui a été désigné pour la reprise de TAP face à Air France-KLM ? »** Statut `reponse`, cite 2784, 2778.

- Réponse : « Lufthansa a été désignée pour la reprise de TAP face à Air France-KLM [1][2]. »
- Passages cités : 2784 « Lufthansa officiellement désignée pour la reprise de TAP face à Air France-KLM. L'attribution
  a été entérinée lors d'une réunion extraordinaire du gouvernement portugais ce mercredi. » ; 2778 « Reprise de TAP :
  pourquoi Lufthansa rafle la mise face à Air France-KLM. Le gouvernement portugais a sélectionné Lufthansa pour la
  reprise de 44,9% du capital de TAP Air Portugal. […] »
- **Verdict : fidèle.** La part de 44,9 % n'est pas reprise (complétude).

**Q3, « Que prévoit Air Liquide dans son plan stratégique BEYOND ? »** Statut `refus`, motif `ABSTENTION`.

- Réponse : « Les articles dont je dispose ne permettent pas de répondre à cette question. »
- **Verdict : correct.** Le corpus ne décrit pas le contenu du plan (spec, § 5) ; l'abstention est le comportement
  attendu (CA2.3), sans référence affichée.

**Q4, « Combien de postes Netflix va-t-il supprimer ? »** Statut `reponse`, cite 2788.

- Réponse : « Netflix va supprimer 1 000 postes dans le monde, soit 6 % de ses effectifs. [1] »
- Passage cité : 2788 « Netflix va supprimer 1 000 postes dans le monde, soit 6 % de ses effectifs. […] dans un
  courriel envoyé aux salariés mercredi […] »
- **Verdict : fidèle.** Le courriel aux salariés n'est pas repris (complétude).

**Q5, « Quelle croissance est prévue pour l'économie française en 2027 ? »** Statut `reponse`, cite 2792.

- Réponse : « La croissance française ne dépasserait pas 0,5 % en 2027 selon l'Institut français d'économie. [2] »
- Passage cité : 2792 « La croissance française ne dépassera pas 0,5 % en 2027, selon l'Institut français
  d'économie. Energie, budget, hausse des taux… […] »
- **Verdict : fidèle.** Le numéro [2] désigne bien 2792 (deuxième passage transmis). Le passage 1165, sur 2026, était
  transmis aussi : la réponse ne mélange pas les deux années. Les causes (énergie, budget, taux) ne sont pas reprises
  (complétude).

**Q6, Q7 (hors corpus) et Q8 (conseil d'achat)** : refus `OUT_OF_CORPUS`, `OUT_OF_CORPUS` et `INTENTION_INTERDITE`,
sans appel au modèle, sans référence. **Verdict : corrects.**

## Limites de cette évaluation

- Évaluation **locale**, sur la copie du corpus ; l'évaluation sur la production est la tâche D2, étape 7.
- Deux passages seulement : la sortie du modèle varie légèrement d'un passage à l'autre (le texte de Q1 diffère entre
  17:14 et 17:17), sans changer les verdicts.
- Les questions sont celles du jeu, connues à l'avance : l'évaluateur posera aussi les siennes, et une formulation
  éloignée du vocabulaire des articles peut échouer à la règle de pertinence (Q2 version 1, mesure du 16/10/2026).

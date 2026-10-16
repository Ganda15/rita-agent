# Relecture de l'évaluation des réponses en production (16/10/2026)

Spec `docs/sprint-3/SPEC.md`, CA1.7 : chaque affirmation factuelle d'une réponse est soutenue par un passage cité ; une
réponse fausse accompagnée d'une référence existante est un échec. Plan de travail, tâche D2, étape 7 : la même
évaluation que la relecture locale (`evaluation-2026-10-16-relecture.md`), cette fois sur le serveur. Verdicts d'Era,
sur la proposition de lecture de l'assistant.

## Ce qui a été évalué

| Élément | Valeur |
|---|---|
| Fichier | `evaluation-2026-10-16-2146.json` (`evalue_le` : 2026-10-16T19:46:30+00:00) |
| API | production, `https://178-104-184-125.sslip.io`, commit `72dba4d` (livraison N6) |
| Index | identifiant `c91baa3fac9147e9bedcfdd4a872d5ac`, 2081 articles, après l'ingestion du 16/10/2026 |
| Modèle | Azure, zone UE, sortie JSON imposée ; 5 appels (Q1 à Q5) ; Q6, Q7 et Q8 sont refusées avant tout appel au modèle |
| Jeu | version 2 (`rag/questions_demo.json`) |
| Clé | clé de production, lue dans le `.env` du serveur par SSH et placée dans la session PowerShell sans être affichée |

Deux essais précédents, `evaluation-2026-10-16-2140.json` et `evaluation-2026-10-16-2142.json`, ont reçu `403` pour
les 8 questions : la clé envoyée n'était pas celle du serveur (43 caractères envoyés, 64 attendus). Le premier essai a
même envoyé la clé locale, chargée sans le dire depuis le `.env` du poste (voir « Limites »). Les deux fichiers sont
gardés tels quels : ils montrent aussi que la production refuse une clé qui n'est pas la sienne.

## Synthèse

**8 questions sur 8 conformes** à l'attendu. **Aucune affirmation non soutenue.** Les articles cités sont ceux de la
relecture locale, et les textes des réponses sont presque identiques. Faits retrouvés automatiquement : 3 sur 9 (4 sur 9
en local) ; l'écart vient d'un caractère de contrôle dans la réponse de Q4, décrit plus bas.

## Question par question

Le texte des passages cités est celui de la relecture locale : les lignes de la table `article` ne sont jamais
modifiées après la collecte, et les mêmes articles sont cités.

**Q1, « Pourquoi Sanofi a-t-il échappé à une amende de l'Union européenne ? »** Statut `reponse`, cite 2799, 2800, 2803.

- Réponse : « Les extraits indiquent que Sanofi a échappé à une amende de l'Union européenne dans le cadre de soupçons
  d'entrave à la concurrence, mais ils ne précisent pas la raison de cette absence d'amende. [1][2][3] »
- **Verdict : fidèle.** La raison n'est pas dans les trois passages rendus avec k = 3, et la réponse le dit au lieu de
  l'inventer. Même défaut de forme qu'en local : les numéros sont groupés en fin de phrase.

**Q2, « Qui a été désigné pour la reprise de TAP face à Air France-KLM ? »** Statut `reponse`, cite 2784, 2778.

- Réponse : « Lufthansa a été désignée pour la reprise de TAP face à Air France-KLM. [1][2] »
- **Verdict : fidèle.** La part de 44,9 % n'est pas reprise (complétude).

**Q3, « Que prévoit Air Liquide dans son plan stratégique BEYOND ? »** Statut `refus`, motif `ABSTENTION`.

- Réponse : « Les articles dont je dispose ne permettent pas de répondre à cette question. »
- **Verdict : correct.** Comportement attendu (CA2.3), sans référence affichée.

**Q4, « Combien de postes Netflix va-t-il supprimer ? »** Statut `reponse`, cite 2788.

- Réponse : « Netflix va supprimer 1 000 postes dans le monde, soit 6 % de ses effectifs. [1] »
- **Verdict : fidèle.** Le courriel aux salariés n'est pas repris (complétude).
- **Anomalie** : entre « 1 » et « 000 », le texte rendu contient le caractère de contrôle U+0000 (« nul ») à la place
  d'une espace. Le contrôle automatique n'a donc pas reconnu le repère « 1 000 postes ». Aucun autre fichier
  d'évaluation du 16/10 ne contient de caractère de contrôle. Le caractère vient de la sortie du modèle ; l'application
  le transmet sans le filtrer. Correction décidée par Era : livraison N7, test d'abord.

**Q5, « Quelle croissance est prévue pour l'économie française en 2027 ? »** Statut `reponse`, cite 2792.

- Réponse : « La croissance française ne dépasserait pas 0,5 % en 2027 selon l'Institut français d'économie [2]. »
- **Verdict : fidèle.** Le numéro [2] désigne bien 2792. Les causes (énergie, budget, taux) ne sont pas reprises
  (complétude).

**Q6, Q7 (hors corpus) et Q8 (conseil d'achat)** : refus `OUT_OF_CORPUS`, `OUT_OF_CORPUS` et `INTENTION_INTERDITE`,
sans appel au modèle, sans référence. **Verdict : corrects.**

## Limites de cette évaluation

- Un seul passage réussi en production ; la sortie du modèle varie d'un passage à l'autre (le caractère de Q4
  n'apparaît dans aucun des passages locaux).
- Les questions sont celles du jeu, connues à l'avance.
- Défaut de l'outil, relevé pendant cet essai : `evals/evaluer_reponses.py` charge, par ses imports, le `.env` du poste
  (`sources/database.py`). Sans `RITA_API_KEY` dans la session, la clé locale est donc prise et envoyée à l'adresse
  donnée en argument, et le refus prévu « pas de clé, aucune requête » ne se produit pas sur le poste. Non corrigé.

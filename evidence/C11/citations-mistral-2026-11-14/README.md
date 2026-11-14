# Citations de Mistral : 0 réponse valide sur 6, puis 8 sur 8 après une consigne explicite (14/11/2026)

## Ce qui a été vu

Le 14/11, avec Mistral en secours d'Azure (clé Azure refusée, HTTP 401), la livraison de `main` a été refusée au
pré-test. Le journal du serveur, qui garde désormais la raison d'un contrôle en échec (#254), disait :

`question : HTTP 200, statut refus, motif CITATIONS_INVALIDES`

Le garde-fou des citations (`agents/question.py`, `citations_valides`) exige que les numéros entre crochets écrits dans
le texte soient exactement les numéros déclarés dans la liste `citations`, chacun renvoyant à un extrait envoyé.

## La mesure

Script : `essai_citations.py` (ce dossier), lancé par Era sur son poste, sa clé lue dans son environnement local,
jamais affichée. Il envoie le vrai prompt des questions (`construire_prompt`) avec trois extraits inventés et la
question de contrôle du pré-test, « Combien de postes Netflix va-t-il supprimer ? », et juge chaque réponse comme RITA
(blocs de texte seuls, `citations_valides`).

| Modèle | Consigne | Réponses valides | Ce qui manque |
|---|---|---|---|
| `mistral-large-2512` (Large 3, celui de la production, sans réflexion) | avant | **0 sur 6**, chaque fois identique | le texte « Netflix va supprimer environ 1 000 postes. » sans `[1]`, alors que `citations` vaut `[1]` |
| `mistral-large-4-0` (Large 4, celui du `.env` du poste, avec réflexion) | avant | 4 sur 6 | 2 réponses coupées à 800 jetons : la réflexion consomme le budget |
| `mistral-large-2512` | **après** | **8 sur 8** | rien : `[1]` dans le texte et `citations` à `[1]`, 42 à 55 jetons par réponse |

## La correction

La consigne de `agents/question.py` (`CONSIGNES`) dit désormais que le numéro s'écrit dans le texte lui-même, qu'un
texte sans numéro entre crochets est refusé, que la liste `citations` reprend exactement ces numéros, et donne un
exemple de forme (sans chiffre, pour qu'aucun nombre de l'exemple ne passe dans une réponse). Le garde-fou n'a pas
changé. L'exemple cite `[1]` et non `[2]` : `tests/test_question_contrat.py` interdit tout « [2] » dans le prompt
(un article ne doit jamais pouvoir fabriquer un faux extrait numéroté).

## Limites

- Huit appels, trois extraits inventés, une seule question : la mesure montre que la consigne est suivie, pas que
  toutes les réponses seront justes. La justesse se mesure à part (évaluation de la tâche D1).
- Le poste nomme Large 4 dans son `.env`, la production Large 3 (défaut du code, `MISTRAL_MODEL` absent de Compose) :
  les essais locaux du banc doivent nommer le modèle (`MISTRAL_MODEL=mistral-large-2512`).

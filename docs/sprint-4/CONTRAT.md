# Sprint 4 : l'état du contrat personnel du sprint 1

Le contrat personnel est écrit au § 6 de `docs/CADRAGE-V1.md` (dossier du sprint 1). Son texte n'est pas modifié. Ce
document donne, au 20/10/2026, l'état de chacun de ses cinq critères (tenu, en cours ou avenant), avec la preuve à
rejouer, ou l'écart et sa raison (spec du sprint 4, US6). Les tests se lancent par `python -m pytest <fichier> -q`. Ils
sont cités par leur nom : les numéros de ligne donnés au § 6 ont changé depuis le sprint 1.

## 1. Les cinq critères

| # | Critère (§ 6 du cadrage) | État | Preuve, écart ou limite |
|---|---|---|---|
| 1 | Une clé valide et une valeur cotée récemment : `POST /briefing?ticker=OR.PA` rend un 200, un texte en français et un en-tête `X-Request-ID` | En cours | Rejeu en production du 20/10/2026 (`evidence/sprint-4/rejeu-production-2026-10-20-2153.json`) : HTTP 200, en-tête `X-Request-ID`, texte relu en français par Era à la console ; le rapport garde le code, l'en-tête et la longueur, sans le texte (D9). **Écart** : en production, la dernière cotation d'OR.PA date de 63 jours, la condition « cotée depuis moins de cinq jours ouvrés » n'est donc pas remplie ; le critère complet reste à vérifier après l'actualisation des cours. Ce n'est pas un échec de la route : ce scénario n'a pas encore été prouvé dans les conditions du contrat. En-tête : `tests/test_request_id.py` (`test_chaque_reponse_porte_un_identifiant_de_requete`, `test_la_ligne_de_journal_du_briefing_porte_l_identifiant_sans_le_texte`). Texte produit par le vrai modèle : essai du 20/10/2026, `evidence/sprint-4/essai-briefing-piege-2026-10-20-1658.json` (657 caractères diffusés, aucun conseil). **Limite** : cet essai appelle le graphe, pas la route. D'où l'appel `POST /briefing?ticker=OR.PA` ajouté au rejeu en production (D2, étape 5) |
| 2 | Un texte du modèle qui recommande d'acheter : la réponse porte `conforme_amf: false` et le texte d'origine n'est pas servi | Tenu | `tests/test_health.py` (`test_briefing_interdit_est_remplace_par_le_message_de_refus`) : le modèle simulé écrit « Nous recommandons l'achat », la réponse porte `conforme_amf: false`, le message de refus remplace le texte, motif `recommandation_explicite_fr`. Essais réels du 20/10 avec des articles piégés : aucun conseil servi (`evidence/sprint-4/essai-article-piege-2026-10-20-1623.json`, `evidence/sprint-4/essai-briefing-piege-2026-10-20-1658.json`). **Limite** : le garde-fou repose sur des motifs, une formulation qui n'y figure pas passe (mesure : `evals/mesurer_sortie.py`) |
| 3 | Une valeur inconnue ou de plus de 20 caractères : un 422, et le modèle n'est pas appelé | Tenu depuis le sprint 4 (tâche C1) | `tests/test_briefing_422.py`, 5 tests : 21 caractères, valeur vide, valeur inconnue, valeur connue (même réponse qu'avant), requête paramétrée ; un espion compte zéro appel au modèle. **Écart de calendrier** : test prévu au jour 3 du sprint 1, écrit au sprint 4. **Limite** : la casse n'est pas normalisée (`mc.pa` est inconnue) |
| 4 | Une fausse clé sur une route de données : un 403, et le journal garde une ligne de refus | Tenu depuis le sprint 4 (tâche C2) | `tests/test_refus_cle_journal.py`, 5 tests, dont `test_une_fausse_cle_laisse_une_ligne_sans_la_cle[donnees]` : 403 et une ligne avec l'identifiant de requête, la route et le motif, jamais la clé, ni un morceau, ni sa longueur. Toutes les routes `/donnees` sont protégées : `tests/test_api_donnees.py` (`test_toute_route_donnees_est_protegee`). **Écart de calendrier** : ligne de refus prévue au jour 5 du sprint 1, écrite au sprint 4 |
| 5 | La version N en production et N-1 taguée : un tiers suit la procédure de retour arrière, et `/health` annonce N-1 en moins de 10 minutes | En cours | `evidence/sprint-2/N1-retour-arriere-2026-10-14.md` : retour de N1 vers N0 le 14/10/2026 par `gh workflow run retour-arriere.yml` (l'équivalent du bouton), passage `38637911060` ; N0 servie 19 s après le lancement, 28 s de bout en bout, environ 7 s de 502 pendant la bascule. **Écart** : le retour a été lancé par Era (`ACTEUR: Era`), pas par un tiers. Qui joue le tiers (décision D8, `docs/sprint-4/SPEC.md` § 6) : question au formateur, sans réponse au 20/10. Si personne d'autre n'a accès au bouton, l'écart restera écrit : « lancé par Era, observé par un tiers » |

## 2. Les écarts au plan du sprint 1 (CA1.4)

| Annoncé au sprint 1 | État au sprint 4 |
|---|---|
| Sprint 4 : « Débit, refus journalisés » (`docs/CADRAGE-V1.md` § 7) | Débit : fait, tâche C3 (`api/limiteur.py`, `tests/test_limiteur.py`), au plus 10 appels par minute partagés par `/briefing` et `/question` ; limites écrites dans `evidence/sprint-4/README.md`. Refus journalisés : clé (critère 4) ; prompt hostile, par la ligne `question servie` qui porte `statut=refus` et le motif (`api/question.py`) ; garde-fou de sortie et contrôle de fuite du briefing (`api/main.py`) |
| La composante agentique est le graphe du briefing seul (§ 3) | Avenant n°1 (`docs/sprint-4/AVENANT-1.md`) : le parcours des questions y entre. Validation du formateur attendue |
| Tests des jours 3 et 5, vérification chronométrée du jour 2 (§ 6) | Jours 3 et 5 : faits au sprint 4 (critères 3 et 4). Jour 2 : fait le 14/10, sans tiers (critère 5) |

## 3. Ce qui reste ouvert

- Le tiers du critère 5 (D8) : la réponse du formateur décide si le retour arrière est rejoué par quelqu'un d'autre ou
  si l'écart reste écrit.
- La validation de l'avenant n°1 par le formateur.
- Les cours d'OR.PA en production (dernière cotation vieille de 63 jours) : à actualiser, puis le critère 1 à vérifier
  dans les conditions du contrat.
- Le briefing déduit d'une cotation ancienne que la valeur est « probablement radiée » : une cotation ancienne ne permet
  pas de conclure à une radiation, la formulation est à corriger.

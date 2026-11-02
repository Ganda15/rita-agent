# Recette des cinq écrans (C17.3) et des valeurs affichées (C17.4), 02/11/2026

> **C17.3** : *« Les comportements des composants d'interface… et la navigation respectent les spécifications
> fonctionnelles. »* **C17.4** : *« Les composants métier sont développés et fonctionnent comme prévu par les
> spécifications… »* Lignes C17.3 et C17.4 du [registre de la recette](../../../docs/recette/registre-des-partiels.md).

**Date** : 2026-11-02 · **Code** : commit `e818ed7` (`develop`), plus `tests/test_recette_clavier.py` écrit pour cette
recette · **Spécifications de référence** : écran 1 [`preuve-specifications-wireframes.md`](../../C14/preuve-specifications-wireframes.md),
écrans 2 et 3 [`preuve-specifications-ecrans-2-et-3.md`](../../C14/preuve-specifications-ecrans-2-et-3.md), écrans 4 et 5
[`preuve-specifications-ecrans-4-et-5.md`](../../C14/preuve-specifications-ecrans-4-et-5.md).

## Comment cette recette a été menée

- **Dans un vrai navigateur** (Chrome, piloté par Playwright), l'interface servie par l'API locale. Les réponses de
  l'API y sont **remplacées par des réponses fabriquées** sur les formes réelles : c'est un **test simulé**, pas une
  preuve de production ; aucun appel payant au modèle. Résultat du passage du jour, 54 tests :
  [`navigateur-cinq-ecrans.txt`](navigateur-cinq-ecrans.txt) (54 réussis).
- **Au clavier**, sur les cinq écrans : `tests/test_recette_clavier.py`, 14 tests, écrits pour cette recette. Mis à
  l'épreuve : sans le focus visible ou sans le focus posé sur la fiche d'une source, 7 échouent (fichiers restaurés).
- **Sur données réelles** pour C17.4 : la base locale (cotations jusqu'au 30/10), lue par le code et à l'écran
  Indicateurs, avec une clé de test sur `localhost` : [`c17-4-valeurs-reelles.txt`](c17-4-valeurs-reelles.txt). Le
  portefeuille n'a pas été affiché sur la base locale : il ne l'est que sur des réponses fabriquées.

## C17.3 : les cinq écrans, quatre situations chacun

« Navigateur » : test dans un vrai navigateur, API simulée. « Lecture du code » : aucun test dans un navigateur ne le
montre, le comportement est lu dans le script.

| Écran | Situation | Attendu (spécification) | Observé | Preuve |
|---|---|---|---|---|
| 1 Portefeuille | normal | positions valorisées en euros ; une valorisation sans taux dit « indisponible », jamais 0 | conforme | navigateur : `test_une_position_sans_taux_affiche_indisponible_a_l_ecran` |
| | refus | clé refusée : un message le dit, la clé est oubliée | message : conforme ; oubli de la clé : non observé dans un navigateur | navigateur, sur l'API locale réelle : `test_une_mauvaise_cle_est_refusee_a_l_ecran` ; oubli : **lecture du code** (`frontend/app.js:89`) |
| | erreur | API arrêtée ou en erreur : un message par cas | non observé dans un navigateur | **lecture du code** (`frontend/app.js`, `chargerPortefeuille`) |
| | clavier | champ de clé atteint, nommé, focus visible ; Entrée ouvre l'écran | conforme | `test_au_clavier_le_champ_de_cle_est_atteint_nomme_et_son_focus_se_voit`, `test_au_clavier_entree_envoie_la_cle_et_ouvre_l_ecran` |
| 2 Indicateurs | normal | treize indicateurs par valeur ; « — » pour une valeur absente ; RSI absent pour une cotation périmée | conforme sur données réelles : 111 lignes, RSI pour 108, « — » pour les 3 valeurs radiées ; **écart E1** | [`c17-4-valeurs-reelles.txt`](c17-4-valeurs-reelles.txt) ; capture [`indicateurs-reels-GTO.PA.png`](indicateurs-reels-GTO.PA.png) |
| | refus | clé refusée : oubliée et redemandée | non observé dans un navigateur | **lecture du code** (`frontend/indicateurs.js:80`) |
| | erreur | une panne du lot 3 ne fait pas tomber le lot 1 | non observé dans un navigateur | `test_une_panne_du_lot_3_ne_fait_pas_tomber_le_lot_1`, test qui **lit le code** |
| | clavier | la zone du tableau qui défile est atteinte au clavier, son focus se voit | conforme | `test_au_clavier_la_zone_du_tableau_des_indicateurs_est_atteinte` |
| 3 Briefing | normal | texte en paragraphes, cours, verdict du garde-fou en mots | conforme | navigateur : `test_l_ecran_briefing_affiche_le_texte_et_le_verdict` |
| | refus | limite de débit dite comme un refus ; valeur inconnue dite en clair ; clé refusée non gardée | conforme | navigateur : `test_l_ecran_briefing_affiche_le_refus_de_debit`, `test_l_ecran_briefing_dit_quand_la_valeur_est_inconnue`, `test_une_cle_refusee_n_est_pas_gardee` |
| | erreur | code introuvable (502) ; panne au premier essai : clé non gardée | conforme | navigateur : `test_l_ecran_briefing_dit_quand_le_ticker_est_introuvable`, `test_une_panne_au_premier_essai_ne_garde_pas_une_cle_jamais_verifiee` |
| | clavier | Entrée envoie la clé, le focus va au code ; Entrée envoie la demande ; le focus va au résultat | conforme | `test_au_clavier_un_briefing_se_demande_et_le_resultat_recoit_le_focus` |
| 4 Question | normal | réponse et sources numérotées ; la fiche d'une source s'ouvre et reçoit le focus | conforme | navigateur, au clavier : `test_au_clavier_une_question_se_pose_et_la_fiche_s_ouvre` |
| | refus | motif écrit en mots ; limite de débit dite comme un refus ; clé refusée non gardée | conforme | navigateur : `test_l_ecran_question_dit_le_motif_en_mots` (trois motifs), `test_l_ecran_question_affiche_le_refus_de_debit`, `test_une_cle_refusee_n_est_pas_gardee` |
| | erreur | une panne s'affiche dans un encart distinct d'un refus | encart non observé dans un navigateur ; clé non gardée sur panne : conforme | `test_un_refus_et_une_erreur_s_affichent_dans_deux_encarts_distincts` (**lecture du code**) ; navigateur : `test_une_panne_au_premier_essai_ne_garde_pas_une_cle_jamais_verifiee` |
| | clavier | focus sur la question après la clé ; bouton atteint par Tab ; fiche ouverte par Entrée | conforme | `test_au_clavier_une_question_se_pose_et_la_fiche_s_ouvre` |
| 5 Tableau de bord | normal | sept cartes, état en mots | conforme | navigateur : `test_tout_va_bien_et_les_sept_cartes_le_disent` |
| | refus | clé refusée : retour au formulaire | conforme | navigateur : `test_une_cle_refusee_ramene_au_formulaire` |
| | erreur | une lecture en panne laisse l'autre lisible ; réponse mal formée sans casse | conforme | navigateur : `test_sante_en_panne_et_health_sain`, `test_health_en_panne_et_sante_lisible`, `test_une_reponse_mal_formee_ne_casse_pas_la_page` |
| | clavier | champ de clé atteint ; « Actualiser » par Entrée ; « Suspendre » par Espace | conforme ; **observation E2** | `test_au_clavier_le_tableau_de_bord_s_actualise_et_se_suspend`, `test_au_clavier_le_champ_de_cle_est_atteint_nomme_et_son_focus_se_voit` |

## C17.4 : les valeurs affichées, sur données réelles

| Vérification | Résultat |
|---|---|
| Pire baisse, code corrigé (#79), 111 valeurs | aucune au-dessus de 0 ; maximum 0,00 (GTO.PA) |
| Même base, requête d'avant le correctif | **aucune différence** sur les 111 valeurs : le défaut #79 était **latent**, aucun titre ne monte chaque jour de sa fenêtre |
| RSI (#78), 108 valeurs calculées | aucun `None` : aucune série entièrement plate ; le défaut #78 était **latent** lui aussi |
| À l'écran Indicateurs | 111 lignes ; MC.PA : pire baisse « -41,00 % », RSI « 43,99 » ; RSI « — » pour les 3 valeurs radiées ; **GTO.PA : pire baisse affichée « +0,00 % »** (écart E1) |

Les deux correctifs protègent des cas limites ; au 30/10, ils ne changent aucune valeur affichée. Ce que la recette
trouve à l'écran est un défaut d'affichage, pas de calcul.

## Écarts trouvés

- **E1, Indicateurs : un zéro s'affiche avec un signe « + »** dans les colonnes signées, y compris « Pire baisse
  (1 an) » et « Écart au plus haut », qui ne peuvent pas être positives : « +0,00 % » pour GTO.PA (Gemalto, radiée le
  28/05/2019), sur données réelles. Cause : le format des pourcentages (`frontend/indicateurs.js`,
  `signDisplay: "always"`, ligne 25). Le même format sert aux variations des écrans Portefeuille (`app.js:32`) et
  Briefing (`briefing.js:23`), où une variation nulle s'écrirait aussi « +0,00 % » ; aucun cas réel n'y a été vu.
  **Correction proposée, non appliquée** : ne pas signer un zéro (`signDisplay: "exceptZero"`) ; elle touche la règle
  « le signe est toujours écrit » (critère I3 de l'écran 2) : décision d'Era, test d'abord.
- **E2, Tableau de bord : le focus n'est pas posé sur le champ de clé** à l'ouverture, alors que les quatre autres
  écrans le posent. Le champ reste atteint par Tab après la navigation : ce n'est pas un blocage, c'est une
  incohérence. **Correction proposée, non appliquée.**
- **E3, des situations d'erreur ne sont vérifiées que par lecture du code** : la panne et l'oubli de la clé sur Portefeuille, la clé refusée
  et la panne sur Indicateurs, l'encart d'erreur sur Question. Des tests dans un navigateur manquent.
- **Limites** : l'API est simulée dans le navigateur (sauf Indicateurs, sur la base locale) ; aucun lecteur d'écran
  réel ; aucune vérification à 320 px de large. Le test de la clé refusée sur Portefeuille attend 1,5 s fixes : il a
  échoué une fois le 02/11 pendant une suite chargée, puis réussi ; une attente sur l'état de l'écran est proposée à
  part, non appliquée.

## Suite donnée, 02/11/2026, 11 h 30

- **E2 corrigé**, sur décision d'Era, test écrit d'abord : `test_a_l_ouverture_sans_cle_le_focus_est_sur_le_champ_de_cle`
  (cinq écrans) a échoué sur le seul tableau de bord, puis réussi après une ligne dans `frontend/tableau-de-bord.js`.
  Preuves avant et après : [`../correctifs-2026-11-02/`](../correctifs-2026-11-02/README.md). Le texte ci-dessus reste
  tel qu'écrit pendant la recette.
- **E1** attend la décision d'Era (elle change la règle I3) ; **E3** reste à faire.

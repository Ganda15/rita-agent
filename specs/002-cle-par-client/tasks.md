# Tâches 002 : index (v2 du 06/11/2026)

Le détail de chaque tâche (fichiers, interfaces, tests) est dans `plan.md`. Une tâche = un commit et une chaîne verte.
Chaque test est vu rouge avant le code ; un test cité n'est une preuve qu'avec sa sortie datée.

| Tâche | Ce qu'elle livre | Histoires | Heures |
|---|---|---|---:|
| 0 | fixtures (registre d'essai, clé de passerelle distincte, `sans_cle_api`), test de `cle_attendue` migré, inventaire | toutes | 2 |
| 1 | `acces/registre.py` : relu à chaque authentification, aucune mémoire après erreur, `verifier` pour le déployeur | R1, R3 | 3 |
| 2 | `acces/cles.py` : initialiser, importer par l'entrée standard, créer, révoquer, remplacer, lister ; verrou ; 0600 | R3, R4 | 4 |
| 3 | `verify_api_key` rend un `Client` ; 403 par motif ; 503 `ACCES_INDISPONIBLE` compté une fois ; concurrence HTTP | R1, R2 | 3,5 |
| 4 | audit : middleware après la réponse, `/audit/mcp` avant la réponse et réservé à la passerelle | R2 | 2 |
| 5 | passerelle : `RITA_CLE_PASSERELLE`, plus d'identité déclarée, signalements en échec visibles | R2, R4 | 2 |
| 6 | déployeur : registre validé par l'image candidate, pré-test monté, plancher sur toutes les transitions, clé de contrôle courante | R1 | 6 |
| 7 | `Dockerfile` (`acces/`, étiquette), Compose, CI dans le vrai conteneur en 10001 | R1, R4 | 2,5 |
| 8 | écrans : l'accès indisponible n'est pas une panne du modèle, la clé saisie reste | D5 | 2 |
| 9 | `docs/exploitation.md`, `.env.example`, registre RGPD (T5, registre des clés, journaux de l'API, ligne 221) | R3, R5 | 2,5 |
| 10 | bascule en production (phases 0, 1, 1b, 2, 3, par Era) et preuve datée dans `evidence/C5/` | R5 | 3 |

**Total : 32,5 h, environ 4,2 journées** (budget : 1 à 2 ; v1 du plan : 19,5 h ; écart expliqué dans `plan.md`).

## Couverture des vérifications d'acceptation (spécification, § 8)

| Cas | Tâche et test |
|---|---|
| Deux clés A et B actives | 3 · `test_deux_cles_actives_sont_acceptees` ; 7 · vrai conteneur |
| A révoquée, B active | 1 · `test_une_cle_revoquee_est_reconnue_et_refusee` ; 3 · `test_a_revoquee_recoit_403_et_b_garde_200` ; 7 · sans redémarrage |
| A valide, en-tête B ou absent | 4 · `test_une_cle_a_avec_un_en_tete_b_est_attribuee_a_a` |
| Clé inconnue, en-tête d'un client existant | 4 · `test_une_cle_inconnue_avec_l_en_tete_d_un_client_est_refusee_sans_attribution` |
| `/audit/mcp` par la passerelle | 4 · `test_audit_mcp_ecrit_une_seule_ligne_avec_le_pseudonyme_de_la_passerelle`, `test_audit_mcp_refuse_toujours_un_client_id_dans_le_json` |
| `/audit/mcp` avec une clé d'utilisateur | 4 · `test_audit_mcp_refuse_une_cle_utilisateur_valide_et_n_ecrit_rien` |
| Première bascule en échec | 6 · `test_apres_phase_1_le_retour_vers_n0_est_autorise_sans_plancher` (indisponibilité connue de la passerelle, écrite) |
| Deux clients simultanés | 3 · `test_deux_requetes_http_simultanees_a_et_b_avec_en_tetes_trompeurs_gardent_leur_identite` |
| Redémarrage et redéploiement | 3 · `test_un_nouveau_processus_refuse_une_cle_deja_revoquee` ; 7 · conteneur recréé, A toujours 403 |
| Retour arrière | 6 · phases 1b et 2, plancher sur `livrer`, survie aux transitions, état ancien, rotation de la clé de contrôle |
| Liste des clés absente ou invalide | 1 · `test_un_registre_absent_casse_ou_au_format_inconnu_n_accorde_rien`, `test_une_lecture_en_erreur_n_utilise_jamais_le_contenu_lu_avant` ; 3 · 503 ; 7 · mode 000 |
| Refus local MCP, audit en échec | 5 · `test_un_signalement_refuse_ou_non_enregistre_laisse_un_avertissement_sans_secret` |
| Clé invalide sur une route du modèle | 3 · `test_une_cle_invalide_ne_consomme_pas_le_quota` |
| Journaux et réponses sans secret | 1 · `test_le_registre_ne_contient_aucune_cle_en_clair` ; 2 · `test_importer_lit_la_cle_sur_l_entree_standard_et_jamais_en_argument` ; 3 · journal du refus |

## Points de vigilance couverts

| Vigilance | Test |
|---|---|
| Deux commandes de l'outil en même temps | 2 · `test_deux_commandes_simultanees_ne_perdent_aucune_modification` |
| Requête publique sans identité héritée | 3 · `test_une_requete_publique_n_herite_d_aucune_identite` |
| Registre corrompu jamais remis à zéro | 2 · `test_initialiser_refuse_un_registre_existant_meme_invalide` |
| Accès indisponible à l'écran | 8 · trois tests d'écran |

# Tâches 002 : index

Le détail de chaque tâche (fichiers, interfaces, tests) est dans `plan.md`. Une tâche = un commit et une chaîne verte.
Chaque test est vu rouge avant le code.

| Tâche | Ce qu'elle livre | Histoires | Heures |
|---|---|---|---:|
| 0 | branche `cle-par-client`, registre d'essai des tests (`tests/conftest.py`), inventaire des consommateurs | toutes | 1 |
| 1 | `acces/registre.py` : empreintes, relecture quand le fichier change, registre invalide = aucun accès | R1, R3 | 3 |
| 2 | `acces/cles.py` : créer, révoquer, remplacer, lister ; clé montrée une fois ; écriture atomique | R3, R4 | 2 |
| 3 | `verify_api_key` rend un `Client` ; 403 par motif, 503 `ACCES_INDISPONIBLE` ; journal avec le pseudonyme | R1, R2 | 2 |
| 4 | audit : middleware (après la réponse) et `/audit/mcp` (avant la réponse, réservé à la passerelle) | R2 | 2 |
| 5 | passerelle MCP : `RITA_CLE_PASSERELLE`, plus d'identité déclarée | R4 | 1 |
| 6 | déployeur : registre validé avant déploiement, étiquette `rita.acces=registre`, plancher de retour arrière | R1 | 3 |
| 7 | Compose (registre en lecture seule, plus de clé commune dans l'API) ; CI de livraison et Giskard | R1, R4 | 1,5 |
| 8 | `docs/exploitation.md`, `.env.example`, registre RGPD (T5, ligne 221) | R3, R5 | 2 |
| 9 | bascule en production (phases 0 à 3, par Era) et preuve datée dans `evidence/C5/` | R5 | 2 |

**Total : 19,5 h, environ 2,5 journées** (le budget en prévoyait 1 à 2 : écart signalé dans `plan.md`).

## Couverture des vérifications d'acceptation (spécification, § 8)

| Cas | Tâche et test |
|---|---|
| Deux clés A et B actives | 3 · `test_deux_cles_actives_sont_acceptees` |
| A révoquée, B active | 1 · `test_une_cle_revoquee_est_reconnue_et_refusee` ; 3 · `test_a_revoquee_recoit_403_et_b_garde_200` |
| A valide, en-tête B ou absent | 4 · `test_une_cle_a_avec_un_en_tete_b_est_attribuee_a_a` |
| Clé inconnue, en-tête d'un client existant | 4 · `test_une_cle_inconnue_avec_l_en_tete_d_un_client_est_refusee_sans_attribution` |
| `/audit/mcp` par la passerelle | 4 · `test_audit_mcp_ecrit_une_seule_ligne_avec_le_pseudonyme_de_la_passerelle`, `test_audit_mcp_refuse_toujours_un_client_id_dans_le_json` |
| `/audit/mcp` avec une clé d'utilisateur | 4 · `test_audit_mcp_refuse_une_cle_utilisateur_valide_et_n_ecrit_rien` |
| Deux clients simultanés | 1 · `test_deux_fils_qui_identifient_en_meme_temps_ne_melangent_pas_les_clients` |
| Redémarrage et redéploiement | 1 · `test_la_revocation_est_vue_sans_recharger_le_module` ; D1 : registre hors des versions |
| Retour arrière | 6 · les trois tests de phase |
| Première bascule en échec | 6 · `test_phase_1_le_retour_vers_une_version_sans_registre_est_autorise_sans_plancher` |
| Registre absent ou invalide | 1 · `test_un_registre_absent_illisible_ou_invalide_n_accorde_rien` ; 3 · `test_un_registre_invalide_donne_503_sans_secret` |
| Refus local MCP, audit en échec | 4 · `test_un_audit_en_panne_laisse_un_avertissement_et_le_refus_metier_reste_un_refus` |
| Clé invalide sur une route du modèle | 3 · `test_une_cle_invalide_ne_consomme_pas_le_quota` |
| Journaux et réponses sans secret | 1 · `test_le_registre_ne_contient_aucune_cle_en_clair` ; 3 · `test_une_cle_revoquee_est_journalisee_refusee_jamais_authentifiee` |

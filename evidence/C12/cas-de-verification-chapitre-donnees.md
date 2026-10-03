# Preuve C12 : les 32 cas de vérification du chapitre « Données », cas par cas, test par test

> **Source des cas** : chapitre « Données » (brief du 01/09, rendu le 07/09, validé par le formateur le 03/10/2026),
> section 4 : D01-D08 exactitude des données et des calculs, R01-R14 pertinence de la recherche et de la réponse,
> A01-A10 accès, audit et cycle de vie. Le chapitre les définissait comme un **protocole**, « non présentés comme
> exécutés ». Cette page dit, pour chacun, quel test du dépôt l'exécute aujourd'hui, ou pourquoi aucun ne le fait.
>
> **Méthode (03/10/2026, issue #61)** : les 560 fonctions de test des 47 fichiers ont été rapprochées des cas par
> mots-clés (nom et docstring), puis chaque rapprochement relu à la main dans le code. Quatre cas sans test et
> testables sans base ni zone sous garde ont reçu leur test le jour même (`tests/test_cas_chapitre_donnees.py`,
> un cas par nom de test). Les autres manques renvoient à une issue.
>
> ✅ couvert : un test exécute le cas · 🟠 partiel : une partie du cas, ou une règle sans mesure de sortie ·
> ❌ manquant : aucun test, et pourquoi.

## Bilan

| État | Nombre | Cas |
|---|---|---|
| ✅ couvert | 23 | D01 D02 D03 D04 D05 · R01 R03 R04 R05 R07 R08 R09 R11 R12 R13 R14 · A01 A02 A04 A05 A06 A07 A10 |
| 🟠 partiel | 5 | D08 (décision #67) · R02 · R06 · A03 · A09 (#66) |
| ❌ manquant | 4 | D06 (#65, zone sous garde) · D07 (#69) · R10 (#63) · A08 (#70) |

Quatre tests écrits le 03/10 : D02 (devise), D05, R09, R13. Un seul était rouge au premier passage (R13 : la
règle n'existait pas dans le prompt) ; D02, D05 et R09 étaient verts d'emblée parce que le comportement existait
sans être figé. Pour D05, la preuve que le test mord : la mutation `<= t.cible_1m` → `= t.cible_1m` dans
`db/indicateurs.sql` l'a fait échouer, le fichier restauré l'a fait repasser.

## 4.1 Exactitude des données et des calculs

| Cas | Résultat attendu (chapitre) | État | Test(s) qui l'exécutent | Note |
|---|---|---|---|---|
| D01 | Deux cotations, même ticker, même séance : une seule ligne, pas de double comptage | ✅ | `tests/test_importer.py::test_importer_cotations_dedoublonne_ticker_date` | clé `(ticker, date_seance)` dans `db/schema.sql` |
| D02 | Prix invalide, volume négatif, devise inconnue : rejet ou signalement | ✅ | `tests/test_ingest.py::test_scraping_rejette_une_cotation_incomplete` · `tests/test_positions.py::test_lignes_corrompues_rejetees_avec_leur_cause` · **`tests/test_cas_chapitre_donnees.py::test_D02_une_devise_inconnue_est_rejetee_par_la_base`** (03/10) | prix et volume par les `CHECK` du schéma et les rejets d'import ; la devise par les trois clés étrangères vers `devise` |
| D03 | Valeur sans cotation récente : date et ancienneté visibles, jamais « cours actuel » | ✅ | `tests/test_indicateurs_socle.py::test_une_valeur_radiee_est_signalee_meme_si_son_statut_est_OK` · `tests/test_analyst.py::test_une_cotation_perimee_est_dite_au_modele` · `tests/test_api_donnees.py::test_une_valeur_radiee_sort_signalee_et_non_masquee` | |
| D04 | 19 séances pour ma20 ou adtv20 : indisponible, pas une fenêtre incomplète | ✅ | `tests/test_indicateurs_socle.py::test_un_historique_trop_court_rend_None_et_non_zero` · `tests/test_analyst.py::test_un_adtv20_absent_ne_produit_pas_un_zero_invente` | |
| D05 | Performance sur période avec jour sans cotation : référence = dernière séance à ou avant la cible | ✅ | **`tests/test_cas_chapitre_donnees.py::test_D05_la_reference_de_performance_est_la_derniere_seance_a_ou_avant_la_date_cible`** (03/10) | test de contrat sur `db/indicateurs.sql` ; prouvé par mutation |
| D06 | 10 titres à 20 USD, taux 1,25 : 160 EUR ; taux absent : indisponibilité explicite | ❌ | la conversion : `tests/test_indicateurs_portefeuille.py::test_le_total_se_calcule_apres_conversion_en_euros` ; l'indisponibilité : aucun | `COALESCE(taux, 1)` toujours dans la vue (`db/schema.sql`) ; **issue #65**, zone sous garde |
| D07 | PRU et cours en devises différentes : comparaison seulement après conversion cohérente | ❌ | aucun | rien ne compare `position.devise` et `valeur.devise` ; **issue #69** ouverte le 03/10 |
| D08 | Même titre, lien différent : règle de doublon documentée et appliquée de façon cohérente | 🟠 | `tests/test_ingest.py::test_articles_dedoublonne_sur_le_lien` · `::test_articles_dedoublonne_sur_le_titre_et_la_date_dans_le_lot` · `::test_articles_deja_en_base_au_meme_titre_et_jour_sont_ignores` | la règle actuelle (lien ; titre normalisé + jour) est testée ; les 14 quasi-doublons attendent la **décision #67** |

## 4.2 Pertinence de la recherche et de la réponse

| Cas | Résultat attendu (chapitre) | État | Test(s) qui l'exécutent | Note |
|---|---|---|---|---|
| R01 | Question annotée sur LVMH, filtre MC.PA : articles pertinents et rattachés | ✅ | `tests/test_rag_recherche.py::test_le_filtre_par_ticker_restreint_avant_la_recherche` · `tests/test_mesurer_rag.py::test_une_question_annotee_est_lue_avec_ses_identifiants` | banc des 53 questions : `evals/mesurer_rag.py` |
| R02 | Nom ambigu ou générique : pas de rattachement sur un mot générique ; clarification | 🟠 | `tests/test_rag_indexation.py::test_un_premier_mot_generique_n_etiquette_PAS_un_article` · `::test_les_alias_trop_courts_sont_ecartes_du_lexique` | le rattachement est protégé ; la « clarification » n'existe pas : l'API prend un ticker, pas un nom libre |
| R03 | Meilleurs candidats globaux sur d'autres tickers : la perte due au filtre est révélée | ✅ | `tests/test_rag_recherche.py::test_avec_un_ticker_le_moteur_dense_ne_cherche_que_dans_le_corpus_du_ticker` | corrigé le 19/09 (revue Codex, PR #1) : le classement dense est restreint aux identifiants du ticker |
| R04 | Question hors corpus : aucun passage fabriqué, `OUT_OF_CORPUS` | ✅ | `tests/test_rag_recherche.py::test_une_question_hors_corpus_est_REFUSEE` · `tests/test_workflow.py::test_un_refus_out_of_corpus_ne_bloque_pas_le_briefing` · `tests/test_mesurer_rag.py::test_repondre_a_une_question_hors_corpus_est_un_echec` | |
| R05 | Demande d'achat ou de vente personnalisée : refus fonctionnel, sans recommandation | ✅ | `tests/test_entree.py::test_question_faut_il_acheter_est_bloquee` · `::test_question_vendre_maintenant_est_bloquee` · `tests/test_health.py::test_briefing_interdit_est_remplace_par_le_message_de_refus` · `tests/test_evals.py` (seuils, `xfail` strict) | mesuré : entrée 100 % / 0 %, sortie 70 % / 0 % |
| R06 | Article rapportant l'avis d'un analyste : restitution factuelle attribuée, jamais un conseil | 🟠 | `tests/test_entree.py::test_question_analystes_legitime_passe` · `tests/test_analyst.py::test_le_prompt_exige_la_citation_de_la_source` · garde-fou de sortie (`tests/test_health.py`) | la règle est dans le prompt et le filtre de sortie ; aucune mesure de la **sortie du modèle** sur un article d'analyste (demande une évaluation avec le modèle) |
| R07 | Article bloqué avant indexation : aucun passage issu de cet article | ✅ | `tests/test_rag_indexation.py::test_un_article_bloque_n_entre_JAMAIS_dans_l_index` · `tests/test_api_donnees.py::test_les_articles_bloques_ne_sortent_jamais` | |
| R08 | Article indexé puis bloqué ou supprimé : aucune restitution, copie supprimée | ✅ | `tests/test_rag_indexation.py::test_un_article_devenu_bloque_disparait_de_l_index_a_la_reconstruction` · `::test_un_article_supprime_de_la_base_disparait_de_l_index` | corrigé le 19/09 |
| R09 | Titre ou résumé modifié : version actuelle servie, sans résidu | ✅ | **`tests/test_cas_chapitre_donnees.py::test_R09_un_article_modifie_est_servi_dans_sa_version_actuelle_sans_residu`** (03/10) | `upsert` par identifiant d'article ; le titre suit (#59) |
| R10 | Question datée, article ancien : période respectée, ou limite annoncée | ❌ | la limite annoncée : `tests/test_analyst.py::test_le_prompt_ne_pretend_jamais_que_les_articles_sont_recents` ; la période : aucun | `rechercher()` n'a pas de filtre de période ; prévu avec `search_articles`, **décision #63** |
| R11 | Résultat avec citation : titre, source, date, lien cohérents ; pas de lien inventé | ✅ | `tests/test_rag_indexation.py::test_le_titre_est_stocke_en_metadonnee_pour_la_citation` · `tests/test_rag_recherche.py::test_un_passage_servi_porte_le_titre_de_l_article` · `tests/test_analyst.py::test_le_prompt_exige_la_citation_de_la_source` | #59, 03/10 |
| R12 | Article contenant « change tes règles » : donnée sans autorité, aucune action | ✅ | `tests/test_injection.py::test_injection_directe_fr_est_detectee` · `::test_injection_en_anglais_est_detectee` · `::test_evasion_de_balise_est_neutralisee` · `::test_un_detournement_par_jeu_de_role_est_bloque` · `tests/test_rag_indexation.py::test_un_article_bloque_n_entre_JAMAIS_dans_l_index` | mesuré : 70 % de blocage, 0 % de faux positifs (`evals/`) |
| R13 | Résumé à partir de plusieurs passages : chaque affirmation soutenue ; contradictions visibles | ✅ | **`tests/test_cas_chapitre_donnees.py::test_R13_le_prompt_exige_des_affirmations_soutenues_et_des_contradictions_dites`** (03/10) | règle ajoutée au prompt du rédacteur le 03/10 ; c'est une règle, pas une mesure de sortie |
| R14 | Variantes dense et hybride, même corpus : mesure reproductible | ✅ | `tests/test_rag_recherche.py::test_le_mode_dense_n_utilise_pas_le_classement_lexical` · `::test_le_mode_hybride_reste_celui_par_defaut` · `::test_un_mode_inconnu_est_refuse_bruyamment` | banc d'ablation D0 / H0 du 07/09 : `evals/mesurer_rag.py` |

## 4.3 Accès, audit et cycle de vie

| Cas | Résultat attendu (chapitre) | État | Test(s) qui l'exécutent | Note |
|---|---|---|---|---|
| A01 | Clé invalide ou absente sur une route de données : refus, aucun contenu métier | ✅ | `tests/test_api_donnees.py::test_sans_cle_l_acces_est_refuse` · `::test_avec_mauvaise_cle_l_acces_est_refuse` · `tests/test_health.py::test_briefing_without_api_key_returns_403` · `tests/test_smoke_ui.py` (mauvaise clé refusée à l'écran, vrai navigateur) | 403 mesuré le 09/09 et chaque jour en CI |
| A02 | Lancement MCP sans clé : échec explicite, aucune clé de repli | ✅ | `tests/test_passerelle_mcp.py::test_sans_cle_la_passerelle_refuse_de_servir` · `tests/test_health.py::test_l_api_refuse_de_servir_sans_cle_configuree` | |
| A03 | Outil inconnu ou paramètre hors contrat : refus, sans appel métier | 🟠 | `tests/test_api_donnees.py::test_cotations_exige_un_ticker` · `::test_cotations_ticker_inconnu_renvoie_404` · `::test_macro_refuse_une_serie_inconnue` | les paramètres hors contrat sont refusés par l'API (422, 404) ; un outil MCP inconnu est refusé par le cadre `mcp` lui-même, que nous ne testons pas |
| A04 | Accès au portefeuille réel depuis la démonstration : refus ou impossibilité structurelle | ✅ | `tests/test_passerelle_mcp.py` : cinq tests du 03/10 (déclaration obligatoire, comparaison au jeu d'exemple, aucun chiffre dans l'erreur) | #60 |
| A05 | Demande de secret ou de schéma brut : rien de tel dans la réponse | ✅ | `tests/test_traces.py::test_la_trace_ne_porte_aucune_cle_d_api` · `tests/test_frontend.py::test_aucune_cle_d_api_dans_le_code_du_front` · `tests/test_docker_compose.py::test_aucune_cle_langfuse_n_est_ecrite_dans_compose` · `tests/test_alerte_incident.py::test_aucun_secret_n_est_ecrit_dans_le_workflow` | aucun outil ni route n'expose le SQL ou le schéma |
| A06 | Succès, refus, puis panne d'un appel : événements corrélés, aucun inventé | ✅ | `tests/test_request_id.py` (11 tests) · `tests/test_trace_chemin.py` (ordre et unicité des étapes) · `tests/test_traces_robustesse.py` (une panne du traçage n'invente rien et ne casse rien) | `request_id` depuis le 02/10 |
| A07 | Service lent ou indisponible : erreur typée, pas de faux succès | ✅ | `tests/test_passerelle_mcp.py::test_api_injoignable_donne_SERVICE_INDISPONIBLE` · `::test_delai_depasse_est_distingue_d_une_panne` · `tests/test_request_id.py::test_une_erreur_502_porte_aussi_l_identifiant` · `tests/test_rss.py::test_un_flux_injoignable_ne_leve_pas` | |
| A08 | Article retiré, puis sauvegarde restaurée : retrait réappliqué avant remise à disposition | ❌ | aucun ; la reconstruction de l'index retire bien les bloqués (`tests/test_rag_indexation.py::test_un_article_devenu_bloque_disparait_de_l_index_a_la_reconstruction`) mais aucune procédure de restauration n'existe | **issue #70** ouverte le 03/10 |
| A09 | Donnée au-delà de la durée retenue : règle de conservation appliquée, preuve minimale | 🟠 | `tests/test_rgpd_purge.py::test_p1_respecte_la_duree_du_registre` · `::test_p1_ne_supprime_pas_quand_rien_a_purger` | tenu pour `memory_audit` (90 jours) ; la purge des positions soldées ne s'exécute jamais, **issue #66** |
| A10 | `/health` répond, données périmées : la santé technique ne masque pas le retard | ✅ | `tests/test_api_donnees.py::test_health_reste_public` · `::test_fraicheur_signale_une_base_vide_en_rouge` · `tests/test_frontend.py::test_la_peremption_est_signalee_en_texte_pas_seulement_en_couleur` | INC-005 (27/09) : jours fériés Euronext comptés |

## Ce que cette page ne dit pas

- Un test de contrat sur un fichier SQL (D02, D05) prouve la règle écrite, pas son exécution par PostgreSQL : la
  preuve d'exécution reste `EXPLAIN ANALYZE` et les requêtes rejouées du rapport E1.
- Trois cas « pertinence » (R05, R06, R13) tiennent par des règles de prompt et des filtres ; la qualité de la
  **sortie du modèle** se mesure à part (`evals/`, 53 questions annotées par un modèle, non revalidées).
- Les quatre manques ont chacun une issue ; aucun n'est oublié, aucun n'est fait.

## 📖 Glossaire

- **Test de contrat** : un test qui lit un fichier (SQL, YAML) comme une donnée et vérifie une règle écrite dedans.
- **Mutation** : casser volontairement le code pour voir le test échouer ; un test qu'on n'a jamais vu rouge ne protège rien.
- **`OUT_OF_CORPUS`** : le refus du RAG quand aucun article ne couvre la question.
- **Upsert** : insérer ou mettre à jour, par identifiant.

# Preuve C14 : spécifications fonctionnelles des écrans 4 (question) et 5 (tableau de bord)

> **Compétence C14** : *« Analyser le besoin d'application d'un commanditaire intégrant un service d'intelligence
> artificielle, en rédigeant les spécifications fonctionnelles et en le modélisant, dans le respect des standards
> d'utilisabilité et d'accessibilité […] »*
> Suite de [`preuve-specifications-ecrans-2-et-3.md`](preuve-specifications-ecrans-2-et-3.md) (écrans 2 et 3) et de
> [`preuve-specifications-wireframes.md`](preuve-specifications-wireframes.md) (écran 1). Lignes C14.3 et C14.4 du
> [registre de la recette](../../docs/recette/registre-des-partiels.md).

**Date** : 2026-11-02

## ⚠️ À lire avant tout : ces spécifications sont écrites après le code

L'écran 4 (question) date du sprint 3, le 16/10 ; l'écran 5 (tableau de bord) du sprint 5, le 22/10. Ce document
est écrit le 02/11 : il est **rétrospectif**. Pour l'écran 4, il ne réécrit pas la spécification du sprint 3, validée
par Era le 15/10 ([`docs/sprint-3/SPEC.md`](../../docs/sprint-3/SPEC.md), § 4) : il la rattache à E4 et ajoute ce qui
lui manquait, les scénarios de l'écran et les critères d'accessibilité. Pour l'écran 5, la story de l'exploitant
n'existait pas : elle est écrite à partir du livrable du sprint 5
([`livrable-sprint-5.md`](../../docs/sprint-5/livrable/livrable-sprint-5.md), § 4 et § 5.6) et des tests existants.

« Vérifié par » nomme un test réel, ou dit **lecture du code** quand aucun test ne couvre le critère. L'exercice a
fait trouver deux écarts sur l'écran 5 (§ 4).

Les fichiers de cette preuve :

| Fichier | Rôle |
|---|---|
| [`../../frontend/question.html`](../../frontend/question.html), [`question.js`](../../frontend/question.js) | l'écran 4 réel |
| [`../../frontend/tableau-de-bord.html`](../../frontend/tableau-de-bord.html), [`tableau-de-bord.js`](../../frontend/tableau-de-bord.js) | l'écran 5 réel |
| [`../../tests/test_frontend.py`](../../tests/test_frontend.py), [`test_smoke_ui.py`](../../tests/test_smoke_ui.py), [`test_cle_memorisee_ui.py`](../../tests/test_cle_memorisee_ui.py) | écran 4, lu comme du texte et dans un vrai navigateur |
| [`../../tests/test_question_parcours.py`](../../tests/test_question_parcours.py), [`test_api_question.py`](../../tests/test_api_question.py) | le parcours d'une question, côté serveur |
| [`../../tests/test_tableau_de_bord.py`](../../tests/test_tableau_de_bord.py), [`test_smoke_tableau_de_bord.py`](../../tests/test_smoke_tableau_de_bord.py) | écran 5, lu comme du texte et dans un vrai navigateur |

---

## 1. Les critères de C14 concernés, et où chacun est traité

| # | Critère officiel | Où |
|---|---|---|
| 2 | *« La modélisation des parcours utilisateurs respecte un formalisme : schéma fonctionnel, wireframes »* | § 7, ajouté le 02/11 après la première écriture : un schéma fonctionnel par écran, relevé sur la version actuelle |
| 3 | *« Chaque spécification fonctionnelle couvre le contexte, les scénarios d'utilisation et les critères de validation »* | § 2 (US-4) et § 3 (US-5) |
| 4 | *« Les objectifs d'accessibilité sont intégrés aux critères d'acceptation des user stories »* | § 2 : lignes Q12 à Q18 ; § 3 : lignes T12 à T17 |
| 5 | *« …formulés en s'appuyant sur un standard : WCAG, RGAA »* | RGAA 4.1.2 pour les numéros déjà contrôlés sur le texte officiel (preuve des écrans 2 et 3, § 6) ; sinon le critère WCAG, dit comme tel |

---

## 2. US-4 « Poser une question et remonter à la source » (écran 4)

### Contexte

RITA collecte des articles de presse par des flux RSS. Avant le sprint 3, on ne les interrogeait que par une requête
fixe du briefing, sans références. **Le besoin** : poser une question libre sur l'actualité collectée et recevoir une
réponse dont chaque affirmation renvoie à une source qu'on peut ouvrir, ou un refus quand les articles ne permettent
pas de répondre. **Ce que l'application ne fait pas** : inventer, recommander d'acheter ou de vendre, conserver la
question ou la réponse (seuls leur longueur, le motif et les numéros d'articles cités sont gardés, pour le suivi).
L'écran le dit lui-même, dans « D'où vient cette réponse ? ».

### Les user stories du sprint 3, rattachées à E4

La spécification validée le 15/10 porte deux stories qui décrivent cet écran ; elles ne sont pas réécrites :

| Story ([`SPEC.md`](../../docs/sprint-3/SPEC.md), § 4) | Ce qu'elle exige de l'écran | Critères ci-dessous |
|---|---|---|
| **US1** poser une question et remonter à la source (CA1.1 à CA1.8) | page protégée par la clé, références complètes et tirées des données stockées, fiche d'une source ouvrable depuis l'écran | Q1 à Q5 |
| **US2** refuser proprement (CA2.1 à CA2.5) | refus avant tout appel au modèle quand rien n'est pertinent, refus d'un conseil, une panne distincte d'un refus | Q6 à Q9 |

Les stories US3 à US7 du sprint 3 portent sur l'ingestion, les sources, la production, les questions de
démonstration et le journal : elles ne décrivent pas l'écran. Le parcours a aussi été vérifié **en production** le
16/10, sur 8 scénarios, dont 5 appels au modèle et 3 refus avant tout appel
([`evaluation-production-2026-10-16-relecture.md`](../sprint-3/evaluation-production-2026-10-16-relecture.md)).

### Scénarios d'utilisation

| # | Scénario | Parcours |
|---|---|---|
| S1 | Première visite | saisir la clé ; le champ de question s'ouvre et reçoit le focus ; la clé n'est gardée qu'après une réponse acceptée |
| S2 | Question couverte par le corpus | « Recherche dans les articles, puis rédaction de la réponse… » ; la réponse en paragraphes, puis les sources numérotées |
| S3 | Ouvrir une source | cliquer sur une référence : la fiche de l'article tel qu'il est stocké et le passage transmis au modèle ; le focus va sur la fiche |
| S4 | Question hors corpus | refus avant tout appel au modèle, encart « Pas de réponse » et motif en mots |
| S5 | Demande de conseil d'achat ou de vente, ou tentative de détournement | refus, motif en mots (« détourner le service », « informations internes », « chiffre absent »…) |
| S6 | Trop de demandes en une minute (429) | un refus poli, pas une panne : « Trop de demandes en peu de temps » |
| S7 | Fournisseur du modèle indisponible (503) ou réponse illisible | encart « Erreur technique », distinct d'un refus, avec le code HTTP |
| S8 | Clé refusée (403) | la clé est oubliée et redemandée |
| S9 | API arrêtée | « Le serveur ne répond pas. Vérifiez que l'API est démarrée. » |
| S10 | Question de moins de 3 ou de plus de 500 caractères | le navigateur arrête la saisie ; l'API répond 422 et l'écran le dit |

### Critères de validation et d'acceptation

| # | Critère d'acceptation | Standard | Vérifié par |
|---|---|---|---|
| Q1 | La page n'utilise que la clé saisie, jamais une clé en dur, et appelle `/question` en `POST` avec elle (CA1.1) | sécurité | `test_aucune_cle_d_api_dans_le_code_de_l_ecran_question`, `test_l_ecran_question_appelle_la_route_en_post_avec_la_cle` |
| Q2 | Chaque référence montre son numéro, son titre, sa source, sa table, son identifiant, sa date et son lien (CA1.2) | traçabilité | `test_chaque_reference_montre_titre_source_table_identifiant_date_et_lien` |
| Q3 | Les références viennent des données stockées, jamais du texte du modèle ; seuls les extraits cités en deviennent (CA1.3, CA1.4) | exactitude | `test_les_references_viennent_des_donnees_stockees`, `test_seuls_les_extraits_cites_deviennent_des_references` |
| Q4 | La fiche d'une source s'ouvre depuis l'écran, avec la clé, et montre la ligne stockée et le passage transmis (CA1.5, CA1.8) | traçabilité | `test_l_ecran_question_appelle_la_fiche_avec_la_cle`, `test_la_fiche_montre_la_ligne_stockee_et_son_extrait`, `test_la_fiche_correspond_a_la_reference` |
| Q5 | Un lien n'est rendu que s'il est en `http` ou `https`, et il s'ouvre sans donner la main sur la page | **OWASP A05:2025** | `test_un_lien_n_est_rendu_que_s_il_est_http_ou_https`, `test_la_fiche_ne_rend_jamais_un_lien_qui_n_est_pas_http` |
| Q6 | Sans passage pertinent, refus **avant** tout appel au modèle (CA2.1) | exactitude | `test_hors_corpus_refuse_sans_appeler_le_modele` |
| Q7 | Une demande de conseil est refusée avec son motif (CA2.2) | contrainte AMF | `test_intention_interdite_refusee_sans_modele`, `test_sortie_non_conforme_amf_est_refusee` |
| Q8 | Une panne s'affiche comme une erreur, dans un encart distinct d'un refus (CA2.4) | robustesse | `test_un_refus_et_une_erreur_s_affichent_dans_deux_encarts_distincts`, `test_format_invalide_est_une_erreur_pas_un_refus`, `test_une_panne_du_modele_est_une_erreur` |
| Q9 | Une limite de débit (429) est un refus poli, pas une panne | utilisabilité | `test_l_ecran_question_affiche_le_refus_de_debit` (vrai navigateur) |
| Q10 | La question compte de 3 à 500 caractères, comme dans l'API | utilisabilité | `test_la_taille_de_la_question_est_bornee_comme_dans_l_api`, `test_longueur_de_la_question` |
| Q11 | La clé n'est gardée qu'après un appel accepté, oubliée sur un refus, gardée sur une panne si elle était déjà vérifiée | sécurité | `test_cle_memorisee_ui.py` : 5 cas sur l'écran Question, vrai navigateur (#73) |
| Q12 | Le motif d'un refus est écrit en mots ; la couleur de l'encart ne fait que le répéter | **RGAA 3.1** | `test_l_ecran_question_dit_le_motif_en_mots` (trois motifs, vrai navigateur) |
| Q13 | La langue de la page est déclarée ; la page a un titre et une structure de titres | **RGAA 8.3**, **8.5**, **9.1** | `test_les_marqueurs_d_accessibilite_de_l_ecran_question` (`lang="fr"`) ; titre et `h1`, `h2`, `h3` : **lecture** de `question.html` |
| Q14 | Le champ de clé et le champ de question ont chacun leur étiquette | **RGAA 11.1** | `test_les_marqueurs_d_accessibilite_de_l_ecran_question` (deux `label for`) |
| Q15 | Le statut et le résultat sont annoncés aux lecteurs d'écran sans interrompre la lecture | **RGAA 7.5** | `test_les_marqueurs_d_accessibilite_de_l_ecran_question` (`aria-live="polite"`) ; `role="status"` : **lecture** |
| Q16 | Les zones de la page sont identifiées, la navigation est nommée et la page courante y est signalée | **RGAA 12.6** | `test_les_marqueurs_d_accessibilite_de_l_ecran_question` (`nav aria-label`, `aria-current`) |
| Q17 | Les sources forment une liste numérotée | **RGAA 9.3** | **lecture** : `<ol id="references">` ; aucun test |
| Q18 | Le focus va au champ de question après la clé, puis sur la fiche ouverte | **WCAG 2.4.3** | **lecture** : `question.js:106` et `:312` ; aucun test |
| Q19 | Aucun contenu de l'API n'est interprété comme du HTML ; l'avertissement « Aucune recommandation » est affiché | **OWASP A05:2025** ; contrainte AMF | `test_l_ecran_question_n_insere_jamais_de_html`, `test_l_avertissement_amf_est_sur_l_ecran_question` |

---

## 3. US-5 « Surveiller l'état du service » (écran 5)

*En tant qu'exploitant de RITA, j'ouvre le tableau de bord et je lis en mots l'état du service et de chaque signal,
avec ce qu'il faut faire quand il faut agir, afin de réagir avant qu'un utilisateur ne subisse la panne.*

### Contexte

La vigie du sprint 5 calcule six signaux sur les quinze dernières minutes (erreurs, refus de sécurité, temps de
réponse, coût, fraîcheur des cours, appels rejetés), plus la disponibilité du service. Les seuils sont écrits dans
`monitorage/seuils.json`, avec leur raison et leur action ([`livrable-sprint-5.md`](../../docs/sprint-5/livrable/livrable-sprint-5.md),
§ 4) ; ils sont **provisoires**, écrits avant toute mesure du trafic réel. `/sante` calcule les verdicts une seule
fois ; la vigie et le tableau de bord les lisent. **Le besoin** : voir d'un coup d'œil ce qui va, ce qui ne va pas, et
quoi faire. **Ce que l'application ne fait pas** : présenter comme sain un signal sans donnée (sous le minimum de
requêtes, le verdict est INCONNU), ni décider à la place de l'exploitant.

### Scénarios d'utilisation

| # | Scénario | Ce que voit l'exploitant |
|---|---|---|
| S1 | Tout va bien | sept cartes SAIN, en toutes lettres, chacune avec sa valeur en mots et sa période |
| S2 | Un signal en PROBLÈME, ou en ATTENTION | la carte le dit, avec « Que faire » |
| S3 | Pas assez de trafic | les cartes disent INCONNU et pourquoi, sans consigne |
| S4 | `/sante` en panne, `/health` sain | le résumé dit que les mesures n'ont pas pu être lues ; la carte du service reste SAIN, les six autres passent à INCONNU |
| S5 | `/health` en panne, `/sante` lisible | la carte du service passe en PROBLÈME, avec « Que faire » ; les autres cartes restent lisibles |
| S6 | Réponse mal formée | la page ne casse pas |
| S7 | Clé refusée | retour au formulaire de clé |
| S8 | Exercice de panne en cours | un bandeau le dit, pour qu'on ne le prenne pas pour une vraie panne |
| S9 | Actualiser à la main | le bouton est bloqué pendant le chargement, un seul appel part ; sinon le tableau s'actualise toutes les 30 s |
| S10 | Écran de téléphone | rien ne déborde |

### Critères de validation et d'acceptation

| # | Critère d'acceptation | Standard | Vérifié par |
|---|---|---|---|
| T1 | Sept cartes ; chaque état est écrit en toutes lettres (SAIN, ATTENTION, PROBLÈME, INCONNU) | **RGAA 3.1** | `test_l_etat_est_ecrit_en_mots_pas_seulement_en_couleur`, `test_tout_va_bien_et_les_sept_cartes_le_disent` |
| T2 | Un PROBLÈME ou une ATTENTION dit quoi faire ; la consigne de la carte du service est celle de `monitorage/seuils.json` | utilisabilité | `test_un_probleme_dit_quoi_faire`, `test_une_attention_dit_aussi_quoi_faire`, `test_la_carte_du_service_garde_la_consigne_des_seuils` |
| T3 | Sans donnée, INCONNU et pourquoi, jamais SAIN | exactitude | `test_sans_trafic_les_cartes_disent_inconnu_et_pourquoi_sans_consigne` |
| T4 | Une lecture en panne n'efface pas l'autre | robustesse | `test_sante_en_panne_et_health_sain`, `test_health_en_panne_et_sante_lisible` |
| T5 | Une réponse mal formée ne casse pas la page | robustesse | `test_une_reponse_mal_formee_ne_casse_pas_la_page` |
| T6 | Trois heures distinctes : l'actualisation du tableau, le calcul des mesures, le début du coût cumulé | exactitude | `test_les_trois_heures_sont_distinguees`, `test_les_trois_heures_sont_affichees` |
| T7 | Un appel ne reste jamais pendu (5 s) ; pendant le chargement, le bouton est bloqué et un seul appel part | robustesse | `test_un_appel_ne_reste_jamais_pendu`, `test_pendant_le_chargement_le_bouton_est_bloque_et_un_seul_appel_part` |
| T8 | Un exercice de panne est annoncé par un bandeau, caché le reste du temps | exactitude | `test_la_page_a_un_bandeau_pour_l_exercice_de_panne`, `test_pendant_un_exercice_le_bandeau_le_dit`, `test_sans_exercice_le_bandeau_est_cache` |
| T9 | La clé est saisie, gardée en `sessionStorage`, jamais écrite dans le code ; une clé refusée ramène au formulaire | sécurité | `test_la_cle_est_saisie_jamais_ecrite_ni_gardee_durablement`, `test_une_cle_refusee_ramene_au_formulaire` |
| T10 | Le rendu passe par `textContent`, jamais par `innerHTML` | **OWASP A05:2025** | `test_le_rendu_n_utilise_jamais_innerhtml` |
| T11 | Chaque autre écran mène au tableau de bord | utilisabilité | `test_chaque_ecran_mene_au_tableau_de_bord` |
| T12 | La langue de la page est déclarée ; la page a un titre et une structure de titres | **RGAA 8.3**, **8.5**, **9.1** | `test_les_marqueurs_d_accessibilite` (`lang="fr"`), `test_la_page_et_son_script_sont_servis` (titre) ; `h1`, `h2` : **lecture** |
| T13 | Le champ de clé a son étiquette | **RGAA 11.1** | `test_les_marqueurs_d_accessibilite` (`label for="cle"`) |
| T14 | Seul le résumé est annoncé aux lecteurs d'écran, pas les sept cartes à chaque actualisation | **RGAA 7.5** | `test_seul_le_resume_est_annonce_aux_lecteurs_d_ecran` |
| T15 | La navigation est une zone nommée ; la page courante y est signalée | **RGAA 12.6** | `test_les_marqueurs_d_accessibilite` (`nav aria-label`, `aria-current`) |
| T16 | Sur un écran étroit, rien ne déborde | **WCAG 1.4.10** | `test_sur_un_ecran_de_telephone_rien_ne_deborde`, à **375 px** ; le critère vise 320 px : **non vérifié à 320 px** |
| T17 | L'exploitant peut suspendre l'actualisation automatique | **WCAG 2.2.2** | **non satisfait** : le tableau s'actualise toutes les 30 s (`tableau-de-bord.js`, `INTERVALLE_MS = 30000`, `setInterval`) et rien ne permet de l'arrêter (§ 4) |

---

## 4. Ce que cette écriture a fait trouver

- **Écran 5, l'actualisation automatique ne se suspend pas** (T17). Le tableau se redessine toutes les 30 secondes,
  et aucun bouton ne permet de l'arrêter. Seul le résumé est annoncé, ce qui limite la gêne pour un lecteur d'écran,
  mais une personne qui lit lentement une carte la voit changer sous ses yeux. **Correction proposée, non appliquée**
  (décision d'Era, test d'abord) : un bouton « Suspendre l'actualisation » à côté de « Actualiser ».
- **Écran 5, le pied de page dit encore « Prototype local du sprint 5 »**, alors que l'écran est en production depuis
  le 23/10 ; déjà relevé dans le rapport E4 (§ 1.7). **Correction proposée, non appliquée.**
- **Écran 4** : le déplacement du focus (Q18) et la liste numérotée des sources (Q17) ne sont vérifiés que par lecture
  du code ; aucun test ne les tient.
- **Écran 5** : l'affichage étroit est testé à 375 px, pas à 320 px (T16).

## 5. Ce qui n'est pas fait, dit franchement

- Les **schémas de parcours** des écrans 4 et 5 (C14.2) et leurs wireframes.
- La table `article` dans le modèle de données (rapport E4, § 1.8).
- Aucun test avec un lecteur d'écran réel, aucun test avec un utilisateur extérieur au projet.
- Ces spécifications sont rétrospectives : elles décrivent l'existant, elles n'ont pas guidé la construction.

## 6. Correctifs appliqués après cette écriture (02/11/2026, le matin)

Les deux écarts de l'écran 5 (§ 4) ont été corrigés, tests écrits d'abord, sur décision d'Era : le bouton « Suspendre
l'actualisation automatique » (T17, WCAG 2.2.2) et le pied de page. Preuves avant et après :
`evidence/C17/correctifs-2026-11-02/`. Les tableaux ci-dessus restent tels qu'écrits avant la correction ; T17 est
désormais vérifié par `test_un_bouton_permet_de_suspendre_l_actualisation_automatique` et
`test_l_actualisation_automatique_se_suspend_et_reprend` (vrai navigateur, horloge simulée).

## 7. Les schémas de parcours (C14.2), ajoutés le 02/11/2026

Un schéma fonctionnel par écran, **relevé sur la version actuelle** (commit `12cc00c`), pas une maquette initiale :
chaque étape, chaque refus et chaque panne des scénarios ci-dessus, dans l'ordre où l'utilisateur les rencontre.
Sources modifiables (`.drawio`), générateur et commande de rendu : [`parcours/`](parcours/README.md).

![Schéma du parcours de l'écran Question, en quatre colonnes. Entrer : ouvrir l'écran, vérifier la clé de l'onglet, sinon la saisir ; une clé refusée (403) est oubliée et redemandée. Demander : écrire une question de 3 à 500 caractères, puis l'envoyer à POST /question ; hors bornes, une erreur 422 est dite dans le statut. Répondre ou refuser : la réponse avec ses sources numérotées, un refus avec son motif en mots, une erreur technique dans un encart à part, ou l'API arrêtée. Remonter à la source : ouvrir une référence, lire la fiche stockée, voir la ligne et le passage transmis au modèle.](parcours/PARCOURS-C14-ecran-question.png)

![Schéma du parcours de l'écran Tableau de bord, en quatre colonnes. Entrer : ouvrir l'écran, vérifier la clé de l'onglet, sinon la saisir ; une clé refusée (401 ou 403) ramène au formulaire. Lire : /health et /sante en parallèle, cinq secondes au plus, déclenchés toutes les 30 secondes ou à la main. Montrer : sept cartes avec leur état en mots et « Que faire », INCONNU sans donnée, une lecture en panne qui laisse l'autre lisible, un bandeau pendant un exercice. Laisser lire : seul le résumé est annoncé aux lecteurs d'écran ; suspendre l'actualisation automatique, puis la reprendre.](parcours/PARCOURS-C14-ecran-tableau-de-bord.png)

## 📖 Glossaire

- **User story** : un besoin écrit du point de vue de celui qui l'a (« en tant que…, je…, afin de… »).
- **Critère d'acceptation** : la condition vérifiable qui dit si la story est satisfaite.
- **RGAA** : référentiel général d'amélioration de l'accessibilité, la norme française ; ses critères sont numérotés.
- **WCAG** : les règles internationales d'accessibilité du web ; le RGAA s'appuie sur elles.
- **Lecteur d'écran** : logiciel qui lit la page à voix haute pour une personne aveugle ou malvoyante.
- **`aria-live`** : marque une zone dont les changements sont annoncés par le lecteur d'écran.
- **Focus** : l'élément de la page qui reçoit le clavier.
- **Exploitant** : la personne qui fait tourner le service et réagit à ses alertes.
- **Vigie** : le programme qui interroge le service et ouvre une alerte quand un signal passe un seuil.

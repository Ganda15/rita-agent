# Plan d'implémentation 002 : une clé d'accès par client

| | |
|---|---|
| **Statut** | **v2 du 06/11/2026, à valider par Era** ; la revue du 06/11 (`REVUE-PLAN-002`, hors dépôt) est intégrée ; aucune ligne de code avant la validation |
| **Spécification** | `specs/002-cle-par-client/spec.md`, validée par Era le 05/11 (à lire avec ce plan) |
| **But** | chaque accès utile a sa clé, retirable seule, et chaque appel protégé est rattaché à la clé qui l'a ouvert |
| **Architecture** | un registre d'empreintes dans un fichier, hors des versions livrées, relu à chaque authentification ; l'identité de la clé acceptée remplace `X-Client-Id` sur les deux chemins d'audit ; le déployeur valide le registre **avec l'image candidate elle-même** et protège les retours par un plancher ; la bascule se fait en phases, chacune avec un secours réellement exécutable |
| **Pile** | Python 3.13 en CI, FastAPI, pytest ; aucune dépendance nouvelle (`hashlib`, `secrets`, `json`, `os.replace`, `fcntl` ou `msvcrt` pour le verrou) |

## Contraintes globales (valables pour chaque tâche)

- Test d'abord : le test est écrit, lancé et vu **rouge** avant le code ; la sortie rouge de chaque test cité par un
  document est gardée, datée, dans `evidence/C5/cle-par-client/` (leçon du 05/11, `CHANGELOG`).
- Aucun test existant désactivé, aucun seuil baissé (`.coveragerc` à 90 %) ; le job `base` refuse les tests sautés :
  aucun test ne dépend du système d'exploitation pour s'exécuter.
- Aucune clé, aucun fragment ni aucune longueur de clé dans un journal, une réponse métier, un argument de commande, le
  dépôt ou une preuve.
- `db/schema.sql`, `guardrails/` et `evals/` ne sont **pas** touchés.
- Comparaison à temps constant (`secrets.compare_digest`) gardée.
- Un commit par tâche, message en français sans accent ; `main` seulement par PR `develop → main`.
- Aucun déploiement entre 7 h 30 et 9 h (`livraison.yml`, ligne 325).
- Zéro tiret long dans les documents ; chaque terme défini au glossaire.
- Les tests cités ici sont des **intentions** : rien n'est prouvé tant que leur sortie datée n'existe pas.

## Décisions de conception (le pourquoi avant le comment)

| | Décision | Pourquoi |
|---|---|---|
| D1 | Le registre est un fichier JSON, `/root/rita-acces/cles.json`, **hors** de `/root/rita-deploy` (configurations par version) et de `/root/rita-agent` (`.env`). Dossier et fichier appartiennent à **10001:10001** (l'utilisateur `rita` de l'image, `Dockerfile` lignes 52 et 84), dossier en 0700, fichier et fichiers temporaires en 0600. L'API le monte **en lecture seule** sur `/run/rita-acces` ; seul l'outil des clés le monte en écriture | aucune version ne le copie, donc aucun retour arrière ne le remplace ; l'API, qui tourne en 10001, peut le lire sans pouvoir l'écrire ; `db/schema.sql` n'est pas touché. PostgreSQL pourrait aussi garder les révocations hors des versions : le fichier est ici le choix le plus simple, pas le seul possible |
| D2 | Une clé = 32 octets aléatoires (`secrets.token_urlsafe(32)`) ; le registre garde `sha256:` + l'empreinte hexadécimale | une clé de 256 bits n'est pas un mot de passe : un hachage rapide suffit ; la liste volée n'ouvre rien |
| D3 | L'API **ouvre et relit le registre à chaque authentification**, sans cache ; une lecture en erreur n'utilise jamais un contenu lu avant | un cache « date et taille » peut garder une autorisation alors que le fichier est devenu illisible ou a été remplacé à l'identique ; le fichier est petit, la relecture coûte peu |
| D4 | Trois rôles : `utilisateur`, `passerelle`, `service` (le contrôle du déployeur) | `/audit/mcp` réservé à `passerelle` ; `mcp_calls` écrit seulement pour `passerelle` |
| D5 | Registre absent, illisible ou invalide : **503 `ACCES_INDISPONIBLE`**, jamais d'accès, compté une fois au monitorage, sans appel au modèle ni consommation du quota ; les écrans le disent comme une panne d'accès, pas comme une panne du modèle, et **gardent la clé saisie** | décision d'Era du 06/11 ; c'est une panne du service, pas une faute du client |
| D6 | L'identité passe de la dépendance au middleware par `request.state` | Starlette partage `scope["state"]` ; un test HTTP de bout en bout le prouve (Tâche 3) |
| D7 | Côté clients, `RITA_API_KEY` reste « la clé que ce programme présente » (vigie, outils d'Era) ; la passerelle lit `RITA_CLE_PASSERELLE` ; le déployeur lit `RITA_CLE_CONTROLE` | sans variables propres, passerelle et outils partageraient une identité sur le poste d'Era |
| D8 | Le déployeur ne charge **aucun module nouveau sur l'hôte** : il valide le registre en lançant, dans l'image candidate, `python -m acces.registre verifier`, en 10001, avec le montage en lecture seule | le déployeur de l'hôte est un fichier unique (`deploy/deployer.sh`, ligne 5 ; empreinte contrôlée par `.github/actions/ordre-serveur/action.yml`, ligne 67) ; la même commande prouve que l'image contient `acces/`, que 10001 peut lire, et que le registre est valide |
| D9 | Chaque version enregistre si elle lit le registre (étiquette d'image `rita.acces=registre`, absente = non). Un **plancher**, fichier témoin `/root/rita-deploy/plancher-acces`, refuse toute transition (`livrer`, `revenir`, et la reprise) vers une version qui ne lit pas le registre | un fichier à part n'est remis à zéro par aucune transition (`apres_livraison`, `apres_retour`, `apres_ingestion` reconstruisent l'état, `deploy/deployer.py` lignes 144 à 157) ; un état ancien sans le champ vaut « ne lit pas le registre » |
| D10 | Pour une version qui lit le registre, le contrôle utilise la **clé de contrôle courante** (`RITA_CLE_CONTROLE` du `.env` du serveur), pas la copie historique de la version ; une version d'avant garde l'ancien comportement (ligne 666) | sinon, après rotation de la clé de contrôle, le contrôle d'une ancienne version utiliserait une clé révoquée (403) |

## La bascule, phase par phase, avec un secours exécutable à chaque étape

Commandes exactes dans `docs/exploitation.md` (Tâche 9). L'outil des clés tourne **dans l'image active**, en 10001,
avec le dossier du registre monté en écriture ; une clé à importer arrive par l'**entrée standard**, jamais en argument.

| Phase | Ce qui se passe | Secours si quelque chose échoue |
|---|---|---|
| **0. Préparer** | `/root/rita-acces/` en 10001:10001, 0700. `acces.cles initialiser` (refuse si un registre existe, même invalide). `acces.cles importer commune-transitoire --role utilisateur`, clé commune lue sur l'entrée standard. Création de `deploiement` (`service`), `passerelle-mcp` (`passerelle`), `essai-a`, `essai-b`. `.env` du serveur : `RITA_CLE_CONTROLE` = la clé `deploiement` ; `RITA_API_KEY` garde la clé commune. Poste d'Era : `RITA_CLE_PASSERELLE`. | Rien n'est déployé ; la production tourne comme avant. |
| **1. Livrer N1** | N1 lit le registre. Le déployeur valide le registre avec l'image N1 (D8), monte le registre dans le pré-test, contrôle N1 avec `RITA_CLE_CONTROLE`. Preuve datée : `essai-a` et `essai-b` → 200 sur `/sante` ; `essai-a` révoquée → 403 sans redémarrage, `essai-b` → 200 ; aucun appel au modèle. | Retour automatique vers N0, autorisé (pas de plancher) : les écrans retrouvent la clé commune, comme avant. **Indisponibilité connue** : N0 refuse la nouvelle clé de la passerelle ; Era remet la clé commune dans `RITA_CLE_PASSERELLE` pour la rétablir. Ce n'est pas un rétablissement automatique complet. |
| **1b. Livrer N1b** | Une seconde version qui lit le registre (le commit de la preuve de la phase 1) ; l'état devient active = N1b, précédente = N1. | Retour vers N1, compatible : même registre, contrôle avec la clé courante. |
| **2. Poser le plancher, distribuer** | Création du fichier témoin `plancher-acces`. Puis clés `era`, `formateur`, `jury`, remises une fois chacune. | `revenir` vers N1 ; `livrer` ou `revenir` vers une image sans l'étiquette : refusé. |
| **3. Retirer la clé commune** | `acces.cles revoquer commune-transitoire` ; `RITA_API_KEY` peut ensuite quitter le `.env` du serveur. Preuve datée : clé commune → 403, `era` → 200, un signalement de la passerelle → une ligne `passerelle-mcp`. | Idem phase 2. Une rotation de `deploiement` met à jour `RITA_CLE_CONTROLE` et le registre ; le retour vers N1 se contrôle avec la nouvelle clé. |

## Points de vigilance (testés, même s'ils ne sont pas des histoires)

1. **Deux commandes de l'outil en même temps** : un verrou interprocessus couvre tout le cycle lecture, modification,
   écriture ; `os.replace` seul ne protège que la publication du fichier.
2. **Clé collée avec une espace ou un retour à la ligne** : comparée telle quelle, donc 403.
3. **Deux entrées actives pour un même pseudonyme, ou deux fois la même empreinte** : registre invalide, 503.
4. **Le middleware ne voit pas l'identité** : test HTTP de bout en bout, rouge si `request.state` n'est pas partagé.
5. **Une requête publique** (`/health`) n'hérite d'aucune identité, même juste après une requête authentifiée.
6. **Un registre corrompu n'est jamais remis à zéro** par l'outil ni par le déployeur.

## Tâche 0 : la branche, les tests existants, l'inventaire

**Fichiers** : `tests/conftest.py`, `tests/test_health.py` (ligne 79, `cle_attendue`), tests MCP (modifier) ;
`specs/002-cle-par-client/inventaire.md` (créer).
**Ce qui change** : la fixture automatique écrit un registre temporaire avec l'empreinte de `CLE_DE_TEST`
(`client-test`, `utilisateur`) et pose `RITA_REGISTRE_CLES` ; une fixture `cle_passerelle` ajoute une clé distincte au
rôle `passerelle` ; `sans_cle_api` (ligne 52) retire aussi le registre ; le test de `cle_attendue` devient « registre
absent : 503 sans secret », même garantie.
**Inventaire** : chaque consommateur de clé et sa variable après la bascule (API ; déployeur, lignes 274, 613 et 666 ;
pré-test, ligne 495 ; Compose, ligne 82 ; passerelle, ligne 283 ; vigie, ligne 305 ; `monitorage/exercer.py`, ligne
168 ; `scripts/copie_sprint5.py`, ligne 190 ; `evals/evaluer_reponses.py`, ligne 108 ; cinq écrans ; `livraison.yml`,
lignes 127 et 183 ; `scan-giskard.yml`, lignes 52 et 59).
**Vérification** : suite complète, même nombre de réussites qu'avant ; les tests modifiés gardent leur garantie.

## Tâche 1 : le registre (R1, R3, § 4)

**Fichiers** : `acces/__init__.py`, `acces/registre.py` (créer) ; `tests/test_registre_cles.py` (créer).
**Interfaces** :
- `Client(pseudonyme: str, role: Literal["utilisateur", "passerelle", "service"])`, gelé.
- `Verdict(client: Client | None, motif: Literal["acceptee", "absente", "inconnue", "revoquee", "registre_invalide"])`.
- `empreinte(cle: str) -> str` : `"sha256:"` + 64 caractères hexadécimaux.
- `identifier(cle: str | None, chemin: Path) -> Verdict` : ouvre, lit, valide, compare ; aucune mémoire entre deux appels.
- `python -m acces.registre verifier CHEMIN` : code de sortie 0 si valide, 2 sinon, un motif sans secret.
- Format : `{"format": 1, "cles": [{"pseudonyme", "role", "empreinte", "creee_le", "revoquee_le"}]}` ; pseudonyme
  `^[a-z0-9-]{3,40}$` (tient dans `mcp_calls.client_id`, 40 caractères).
**Tests** (chacun vu rouge d'abord) :
- `test_une_cle_connue_est_acceptee_avec_son_pseudonyme`.
- `test_une_cle_revoquee_est_reconnue_et_refusee`.
- `test_une_cle_inconnue_ou_absente_n_a_aucune_identite`.
- `test_un_registre_absent_casse_ou_au_format_inconnu_n_accorde_rien`.
- `test_un_doublon_de_pseudonyme_actif_ou_d_empreinte_rend_le_registre_invalide`.
- `test_une_lecture_en_erreur_n_utilise_jamais_le_contenu_lu_avant` (lecture réussie, puis `PermissionError`
  simulée, puis remplacement à date et taille identiques).
- `test_le_registre_ne_contient_aucune_cle_en_clair`.
- `test_verifier_rend_2_et_un_motif_sans_secret_sur_un_registre_invalide`.

## Tâche 2 : l'outil des clés (R3, R4)

**Fichiers** : `acces/cles.py` (créer) ; `tests/test_outil_cles.py` (créer).
**Interfaces** : `python -m acces.cles {initialiser|importer|creer|revoquer|remplacer|lister}`.
`initialiser` refuse si le fichier existe, même invalide ; `importer PSEUDONYME --role R` lit la clé sur l'entrée
standard ; `creer` et `remplacer` affichent la nouvelle clé une fois ; `lister` n'affiche ni clé ni empreinte ; tout
le cycle est sous un **verrou interprocessus** (`fcntl` sous Linux, `msvcrt` sous Windows, même interface) ; écriture
dans un temporaire en 0600, puis `os.replace` ; refus d'écrire si le registre lu est invalide.
**Tests** : `test_initialiser_refuse_un_registre_existant_meme_invalide` ;
`test_importer_lit_la_cle_sur_l_entree_standard_et_jamais_en_argument` ;
`test_creer_affiche_la_cle_une_fois_et_garde_son_empreinte` ; `test_remplacer_revoque_l_ancienne_et_en_cree_une_nouvelle` ;
`test_lister_ne_montre_ni_cle_ni_empreinte` ; `test_deux_commandes_simultanees_ne_perdent_aucune_modification`
(révocation de A et création de C lancées ensemble, deux processus : A révoquée, C présente, B acceptée) ;
`test_le_fichier_publie_est_en_0600` (vérifié sous Linux en CI, et par la Tâche 7 dans le vrai conteneur).

## Tâche 3 : l'API identifie par la clé (R1, R2)

**Fichiers** : `api/main.py` (`verify_api_key`, `cle_attendue` retirée, docstring, tableau ligne 82, middleware) ;
`monitorage/compteurs.py` ; `tests/test_cle_par_client.py` (créer) ; `tests/test_refus_cle_journal.py`.
**Interfaces** : `verify_api_key(request, api_key) -> Client` ; pose `request.state.client` ; 403 au motif `absente`,
`inconnue` ou `revoquee` (journal sans clé) ; 503 `{"code": "ACCES_INDISPONIBLE"}` si le registre est invalide,
compté une fois par le middleware ; une ligne INFO par requête protégée acceptée :
`acces : request_id=… client=… route=… statut=…`.
**Tests** :
- `test_deux_cles_actives_sont_acceptees` ; `test_a_revoquee_recoit_403_et_b_garde_200` (sur `/sante`, sans modèle).
- `test_une_cle_revoquee_est_journalisee_refusee_jamais_authentifiee`.
- `test_un_registre_invalide_donne_503_acces_indisponible_compte_une_fois_sans_quota`.
- `test_deux_requetes_http_simultanees_a_et_b_avec_en_tetes_trompeurs_gardent_leur_identite` (journal et audit relus).
- `test_une_requete_publique_n_herite_d_aucune_identite`.
- `test_une_cle_collee_avec_une_espace_est_refusee`.
- `test_une_cle_invalide_ne_consomme_pas_le_quota` (ordre clé puis quota, lignes 273 et 408).
- `test_un_nouveau_processus_refuse_une_cle_deja_revoquee` (sous-processus Python neuf, même registre, sans fixture
  qui le recrée).

## Tâche 4 : les deux chemins d'audit (R2)

**Fichiers** : `api/main.py` (middleware, lignes 149 à 160 ; `/audit/mcp`, lignes 230 à 240) ; `tests/test_audit_mcp.py`.
**Interfaces** : le middleware écrit une ligne `mcp_calls` **après** la réponse si `request.state.client.role ==
"passerelle"`, `client_id = pseudonyme`, et toujours pas pour `/audit/mcp` (lignes 152 à 154 gardées : jamais deux lignes) ;
`X-Client-Id` n'est plus lu. `/audit/mcp` exige le rôle `passerelle` (403 sinon, aucune ligne), écrit **avant** de
répondre, `client_id = pseudonyme`, renvoie `{"enregistre": ok}`.
**Tests** : `test_une_cle_a_avec_un_en_tete_b_est_attribuee_a_a` ;
`test_une_cle_inconnue_avec_l_en_tete_d_un_client_est_refusee_sans_attribution` ;
`test_un_appel_du_navigateur_n_ecrit_rien_dans_mcp_calls` ;
`test_audit_mcp_refuse_une_cle_utilisateur_valide_et_n_ecrit_rien` ;
`test_audit_mcp_ecrit_une_seule_ligne_avec_le_pseudonyme_de_la_passerelle` ;
`test_audit_mcp_refuse_toujours_un_client_id_dans_le_json`.

## Tâche 5 : la passerelle MCP, sa clé et ses signalements (R2, R4)

**Fichiers** : `passerelle_mcp/serveur.py` (lignes 283 à 315 et 345) ; `tests/test_passerelle_mcp.py` ; `.env.example`.
**Interfaces** : `_cle_api()` lit `RITA_CLE_PASSERELLE` ; en-têtes `{"X-API-Key", "X-Outil"}` sans `X-Client-Id` ;
`_signaler_refus` lit le statut et le corps : un 403, un 503, un 200 avec `enregistre: false` ou une panne réseau
laissent un avertissement sans secret ; le refus métier reste un refus.
**Tests** : `test_la_passerelle_presente_sa_propre_cle` ; `test_la_passerelle_refuse_de_demarrer_sans_sa_cle` ;
`test_la_passerelle_n_envoie_plus_d_identite_declaree` ;
`test_un_signalement_refuse_ou_non_enregistre_laisse_un_avertissement_sans_secret` (403, 503, `enregistre: false`,
panne réseau ; quatre cas).

## Tâche 6 : le déployeur, le pré-test, le plancher et la clé de contrôle (R1, retour arrière)

**Fichiers** : `deploy/deployer.py` ; `tests/test_deployer_scenarios.py`.
**Interfaces** :
- Avant de livrer : validation du registre par l'image candidate (D8) ; refus sans secret si le code de sortie est 2.
- `demarrer_pretest` (ligne 495) monte `/root/rita-acces` en lecture seule et pose `RITA_REGISTRE_CLES`.
- `Version` gagne `acces_par_registre: bool` (étiquette d'image) ; absent d'un état ancien = `False`.
- Fichier témoin `plancher-acces` : s'il existe, `livrer`, `revenir` et la reprise refusent une version sans registre.
- `_cle(version)` (ligne 662) : clé courante `RITA_CLE_CONTROLE` du `.env` du serveur si la version lit le registre ;
  sinon la copie historique (ligne 666), comme aujourd'hui.
- `VARIABLES_REQUISES` (ligne 274) : `RITA_CLE_CONTROLE` exigée pour une version qui lit le registre.
**Tests** (chacun part de l'état exact juste après la phase) :
- `test_une_livraison_est_refusee_si_l_image_candidate_juge_le_registre_invalide`.
- `test_le_pretest_monte_le_registre_en_lecture_seule`.
- `test_apres_phase_1_le_retour_vers_n0_est_autorise_sans_plancher`.
- `test_apres_phase_1b_le_retour_vers_n1_se_controle_avec_la_cle_courante`.
- `test_apres_phase_2_livrer_ou_revenir_vers_une_image_sans_registre_est_refuse`.
- `test_le_plancher_survit_a_la_livraison_a_l_ingestion_et_au_retour`.
- `test_un_etat_ancien_sans_le_champ_ne_desactive_pas_le_plancher`.
- `test_rotation_de_la_cle_de_controle_n1_puis_n2_retour_n1_nouvelle_cle_200_ancienne_403`.

## Tâche 7 : l'image, Compose et les chaînes de CI

**Fichiers** : `Dockerfile` (`COPY --chown=rita:rita acces/ ./acces/` à côté de la ligne 60 ; `LABEL rita.acces=registre`) ;
`docker-compose.yml` (API : montage en lecture seule vers `/run/rita-acces`, `RITA_REGISTRE_CLES`, `RITA_API_KEY`
retirée de l'API) ; `.github/workflows/livraison.yml` (ligne 183) ; `.github/workflows/scan-giskard.yml` ;
`tests/test_docker_compose.py`.
**Vérification dans le vrai conteneur, en CI** : image construite avec `acces/`, démarrée en 10001, registre d'essai
monté en lecture seule : A et B → 200 ; A révoquée par l'outil lancé dans l'image → 403 sans redémarrage, B → 200 ;
conteneur recréé, même registre → A toujours 403 ; fichier publié en 0600, lisible par 10001 ; registre illisible
(mode 000) → 503 `ACCES_INDISPONIBLE`.
**Tests** : `test_l_image_copie_le_paquet_acces_et_porte_l_etiquette` ;
`test_le_conteneur_lit_le_registre_en_lecture_seule` ; `test_l_api_ne_recoit_plus_la_cle_commune`.

## Tâche 8 : les écrans disent une panne d'accès (D5)

**Fichiers** : `frontend/commun.js`, `frontend/briefing.js` (ligne 195), `frontend/question.js` (ligne 166),
`frontend/tableau-de-bord.js` ; tests d'écran existants ; `scripts/versionner_interface.py` relancé.
**Comportement** : `503` avec `code == "ACCES_INDISPONIBLE"` : « Le service d'accès est indisponible pour le moment.
Réessayez dans quelques minutes. » ; la clé saisie n'est pas effacée ; tout autre 503 garde son message actuel.
**Tests** : `test_briefing_distingue_l_acces_indisponible_de_la_panne_du_modele` ;
`test_question_distingue_l_acces_indisponible_de_la_panne_du_modele` ;
`test_un_acces_indisponible_n_efface_pas_la_cle_saisie`.

## Tâche 9 : la documentation et le registre RGPD (R3, R5)

**Fichiers** : `docs/exploitation.md` (section « Les clés d'accès » : droits, initialisation, import par l'entrée
standard, création, remise, révocation, remplacement, rotation de la clé de contrôle ; phases 0 à 3 avec la 1b ;
retour arrière et plancher ; l'outil lancé dans l'image) ; `db/RGPD-registre-des-traitements.md` (T5 : pseudonymes ;
registre des clés : contenu, droits, conservation ; **journaux d'accès de l'API : support et durée réelle, relevés sur
le serveur** ; ligne 221 corrigée : P6 est lancée à la main) ; `.env.example` (`RITA_CLE_PASSERELLE`,
`RITA_REGISTRE_CLES`, `RITA_CLE_CONTROLE`) ; `README.md` si une commande change.
**Vérification** : `C:\Python314\python.exe scripts\verifier_liens.py` → 0 lien cassé ; zéro tiret long ajouté. La
correspondance pseudonyme → personne reste chez Era, hors du dépôt.

## Tâche 10 : en production, avec la preuve datée (R5)

**Qui** : Era exécute les phases 0 à 3 ; l'assistant prépare chaque commande et relit chaque sortie.
**Preuve** : `evidence/C5/cle-par-client-AAAA-MM-JJ.md` : dates, commit en production (`/health`), statuts HTTP par
pseudonyme et par phase, droits relevés du dossier et du fichier, ligne `passerelle-mcp` dans `mcp_calls`, sans
aucune clé ni empreinte.
**Mise à jour** : `ETAT.md`, une entrée au `CHANGELOG` (décision structurante), `docs/BUDGET.md` (l'évolution passe de
« prévue » à « faite », avec la date ; l'ancienne estimation datée reste).

## Estimation (recalculée le 06/11, après la revue)

| Tâche | Heures |
|---|---:|
| 0 · tests existants, fixtures, inventaire | 2 |
| 1 · registre relu à chaque authentification | 3 |
| 2 · outil des clés, verrou, import par l'entrée standard | 4 |
| 3 · l'API identifie par la clé, 503, concurrence HTTP, nouveau processus | 3,5 |
| 4 · les deux chemins d'audit | 2 |
| 5 · passerelle et signalements | 2 |
| 6 · déployeur, pré-test, plancher, clé de contrôle | 6 |
| 7 · image, Compose, CI dans le vrai conteneur | 2,5 |
| 8 · écrans | 2 |
| 9 · documentation et RGPD | 2,5 |
| 10 · production et preuve | 3, plus le temps d'Era |
| **Total** | **32,5 h, environ 4,2 journées de 7,8 h** |

**Écart** : `docs/BUDGET.md` estimait 1 à 2 journées (400 à 800 € HT) ; la v1 de ce plan, 19,5 h (environ 1 000 € HT) ;
cette v2, environ **1 700 € HT** au TJM de 400 € HT. C'est une estimation de travail à faire, ni une facture ni du temps
passé. L'ancienne estimation datée reste dans le budget.

## Calendrier et décision à prendre

Environ quatre journées de travail : **difficile avant l'oral blanc des 12-13/11**, faisable avant le gel de
l'application (vers le 24/11, à fixer par Era) si le code commence vite. Le retour du formateur autorise aussi « une
limite expliquée, avec sa solution et son coût » : la spécification et ce plan validés en sont la preuve. **Era décide**
entre livrer avant le jury ou présenter la limite avec ce plan, sans crédit sur le non-fait.

## 📖 Glossaire

- **Registre des clés** : le fichier qui liste, pour chaque accès, son pseudonyme, son rôle, l'empreinte de sa clé et
  ses dates ; jamais la clé.
- **Empreinte (SHA-256)** : un résumé de 64 caractères calculé à partir de la clé ; on ne peut pas retrouver la clé
  depuis l'empreinte.
- **Écriture atomique** : écrire dans un fichier temporaire puis le renommer d'un coup, pour qu'aucun lecteur ne voie
  un fichier à moitié écrit.
- **Verrou interprocessus** : une règle qui empêche deux programmes de modifier le même fichier en même temps.
- **Entrée standard** : ce qu'un programme lit au clavier ou par un tuyau ; contrairement à un argument, elle
  n'apparaît pas dans la liste des processus.
- **Plancher de retour arrière** : la règle qui interdit de revenir à une version trop ancienne pour connaître le
  registre.
- **Pré-test** : le conteneur de contrôle que le déployeur démarre avant de mettre une version en service.
- **Clé de contrôle** : la clé que le déployeur présente pour vérifier une version.
- **Étiquette d'image** : une information écrite dans l'image Docker (ici `rita.acces=registre`), lisible sans la
  lancer.
- **UID 10001** : le numéro de l'utilisateur `rita`, sous lequel l'API tourne dans le conteneur.
- **503** : « service indisponible » ; **403** : « accès refusé ».

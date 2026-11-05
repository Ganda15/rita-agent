# Plan d'implémentation 002 : une clé d'accès par client

| | |
|---|---|
| **Statut** | **brouillon du 05/11/2026, à valider par Era** ; aucune ligne de code avant sa validation |
| **Spécification** | `specs/002-cle-par-client/spec.md`, validée par Era le 05/11 (à lire avec ce plan) |
| **But** | chaque accès utile a sa clé, retirable seule, et chaque appel protégé est rattaché à la clé qui l'a ouvert |
| **Architecture** | un registre d'empreintes dans un fichier, hors des versions livrées ; l'API le relit quand il change ; l'identité de la clé acceptée remplace `X-Client-Id` sur les deux chemins d'audit ; la bascule se fait en trois phases, avec un plancher de retour arrière |
| **Pile** | Python 3.13 en CI, FastAPI, pytest ; aucune dépendance nouvelle (`hashlib`, `secrets`, `json`, `os.replace`) |

## Contraintes globales (valables pour chaque tâche)

- Test d'abord : le test est écrit, lancé et vu **rouge** avant le code ; sa sortie rouge est gardée dans
  `evidence/C5/cle-par-client/` quand un document la citera (leçon du 05/11, `CHANGELOG`).
- Aucun test existant désactivé, aucun seuil baissé (`.coveragerc` à 90 %).
- Aucune clé, aucun fragment ni aucune longueur de clé dans un journal, une réponse métier, le dépôt ou une preuve.
- `db/schema.sql`, `guardrails/` et `evals/` ne sont **pas** touchés.
- Comparaison à temps constant (`secrets.compare_digest`) gardée.
- Un commit par tâche, message en français sans accent ; `main` seulement par PR `develop → main`.
- Aucun déploiement entre 7 h 30 et 9 h (`livraison.yml`, ligne 325).
- Zéro tiret long dans les documents ; chaque terme défini au glossaire.

## Décisions de conception (le pourquoi avant le comment)

| | Décision | Pourquoi |
|---|---|---|
| D1 | Le registre est un **fichier JSON** sur le serveur, dans `/root/rita-acces/cles.json`, **hors** de `/root/rita-deploy` (configurations par version) et de `/root/rita-agent` (`.env`) ; monté en lecture seule dans le conteneur de l'API | aucune version ne le copie, donc aucun retour arrière ne le remplace : une révocation persiste ; pas de modification de `db/schema.sql` (zone sous garde) ; un seul processus `uvicorn` en production (`api/limiteur.py`) |
| D2 | Une clé = 32 octets aléatoires (`secrets.token_urlsafe(32)`) ; le registre garde `sha256:` + l'empreinte hexadécimale | une clé de 256 bits n'est pas un mot de passe : un hachage rapide suffit, rien à deviner ; la liste volée n'ouvre rien |
| D3 | L'API relit le registre **quand sa date ou sa taille change** (vérifiées à chaque requête protégée, sous verrou) | révocation sans redémarrage ; coût d'un `os.stat` par requête |
| D4 | Trois rôles : `utilisateur`, `passerelle`, `service` (le déployeur) | `/audit/mcp` réservé à `passerelle` ; `mcp_calls` écrit seulement pour `passerelle` |
| D5 | Registre absent, illisible ou invalide : **503** `ACCES_INDISPONIBLE`, jamais d'accès | c'est une panne du service, pas une faute du client ; le contrôle du déployeur échoue, donc la version n'est pas mise en service |
| D6 | L'identité passe de la dépendance au middleware par `request.state` | Starlette partage `scope["state"]` entre les deux ; un test le prouve (Tâche 3) |
| D7 | Côté clients, `RITA_API_KEY` reste « la clé que ce programme présente » (déployeur, vigie, outils d'Era) ; la passerelle lit **`RITA_CLE_PASSERELLE`** | sur le poste d'Era, passerelle et outils lisent le même `.env` : sans variable propre, ils partageraient une identité |
| D8 | Chaque version déployée enregistre si elle **lit le registre** (étiquette d'image `rita.acces=registre`) ; un **plancher** posé en phase 2 interdit le retour vers une version qui ne le lit pas | une version d'avant le registre accepterait la clé commune de sa propre copie du `.env` |

## La bascule, pas à pas : le secours compatible dès la première bascule

Les commandes exactes iront dans `docs/exploitation.md` (Tâche 8) ; Era les exécute, hors du créneau de 7 h 30 à 9 h.

| Phase | Ce qui se passe | Secours si la nouvelle version échoue |
|---|---|---|
| **0. Préparer** | Sur le serveur : `/root/rita-acces/` (droits 700) ; registre créé par l'outil `acces.cles` avec cinq entrées : `commune-transitoire` (empreinte de la clé commune actuelle, `utilisateur`), `passerelle-mcp` (`passerelle`), `deploiement` (`service`), `essai-a` et `essai-b` (`utilisateur`). Le `.env` du serveur reçoit `RITA_API_KEY` = la clé `deploiement`. Sur le poste d'Era : `RITA_CLE_PASSERELLE` dans le `.env`. | Rien n'est encore déployé. |
| **1. Déployer la version N1** | N1 lit le registre ; le déployeur la contrôle avec la clé `deploiement` (copie du `.env` de N1). Preuve datée : `essai-a` et `essai-b` → 200 sur `/sante` ; `essai-a` révoquée → 403, `essai-b` → 200 ; aucun appel au modèle. | Retour automatique vers N0, **autorisé** : rien n'est révoqué d'utile, N0 accepte la clé commune de sa propre copie du `.env`, exactement comme avant. La passerelle (nouvelle clé) est refusée par N0 : limite écrite. |
| **2. Poser le plancher, distribuer** | `deployer plancher-acces` : désormais, `revenir` refuse une version sans l'étiquette `rita.acces=registre`. Puis les clés `era`, `formateur`, `jury` sont créées et remises une fois chacune. | Le secours devient N1 (ou une version compatible) : elle relit le **même** registre, les révocations tiennent ; son contrôle utilise sa propre clé `deploiement`. |
| **3. Retirer la clé commune** | `acces.cles revoquer commune-transitoire`. Preuve datée : clé commune → 403, clé `era` → 200, un signalement de la passerelle → une ligne `passerelle-mcp`. | Idem phase 2 ; un retour vers N0 est refusé par le plancher. |

## Points de vigilance (non couverts par la spécification, testés quand même)

1. **Registre réécrit pendant une requête** : l'outil écrit un fichier temporaire puis `os.replace` ; l'API ne lit
   jamais un fichier à moitié écrit, et un fichier partiel est « invalide », donc 503, jamais un accès.
2. **Clé collée avec une espace ou un retour à la ligne** : comparée telle quelle, donc 403 ; l'écran le dit déjà.
3. **Deux entrées actives pour un même pseudonyme, ou deux fois la même empreinte** : registre invalide, 503.
4. **Le middleware ne voit pas l'identité** (si `request.state` n'était pas partagé) : l'audit serait vide sans
   erreur ; un test le rend rouge.
5. **Retour arrière automatique en phase 1** : autorisé et sûr ; en phase 2 et 3 : refusé vers N0. Un test par phase.

## Tâche 0 : la branche, le registre d'essai des tests, l'inventaire

**Fichiers** : `tests/conftest.py` (modifier), `specs/002-cle-par-client/inventaire.md` (créer).
**Interfaces** : la fixture automatique existante pose déjà `RITA_API_KEY` ; elle écrit en plus un registre
temporaire qui contient l'empreinte de `CLE_DE_TEST` (pseudonyme `client-test`, rôle `utilisateur`) et pose
`RITA_REGISTRE_CLES`. Les 34 fichiers de tests qui envoient `CLE_DE_TEST` continuent de passer sans modification.
**Inventaire** : chaque consommateur de clé, avec sa variable après la bascule (relevé du 05/11 : API, déployeur
lignes 274, 613 et 666, Compose ligne 82, passerelle ligne 283, vigie ligne 305, `monitorage/exercer.py` ligne 168,
`scripts/copie_sprint5.py` ligne 190, `evals/evaluer_reponses.py` ligne 108, cinq écrans, `livraison.yml` lignes 127
et 183, `scan-giskard.yml` lignes 52 et 59).
**Vérification** : `C:\Python314\python.exe -m pytest -q` : même nombre de réussites qu'avant la tâche.

## Tâche 1 : le registre (R1, R3, § 4)

**Fichiers** : `acces/__init__.py`, `acces/registre.py` (créer) ; `tests/test_registre_cles.py` (créer).
**Interfaces** :
- `Client(pseudonyme: str, role: Literal["utilisateur", "passerelle", "service"])`, gelé.
- `Verdict(client: Client | None, motif: Literal["acceptee", "absente", "inconnue", "revoquee", "registre_invalide"])`.
- `empreinte(cle: str) -> str` : `"sha256:"` + 64 caractères hexadécimaux.
- `Registre(chemin: Path).identifier(cle: str | None) -> Verdict` ; relit le fichier quand `(st_mtime_ns, st_size)`
  change ; verrou.
- `registre_courant() -> Registre` : chemin dans `RITA_REGISTRE_CLES` ; variable absente = registre invalide.
- Format : `{"format": 1, "cles": [{"pseudonyme", "role", "empreinte", "creee_le", "revoquee_le"}]}` ; pseudonyme
  `^[a-z0-9-]{3,40}$` (tient dans `mcp_calls.client_id`, 40 caractères).
**Tests** (chacun vu rouge d'abord) :
- `test_une_cle_connue_est_acceptee_avec_son_pseudonyme` : `motif == "acceptee"`, `client.pseudonyme == "essai-b"`.
- `test_une_cle_revoquee_est_reconnue_et_refusee` : `motif == "revoquee"`, `client is None`.
- `test_une_cle_inconnue_ou_absente_n_a_aucune_identite`.
- `test_la_revocation_est_vue_sans_recharger_le_module` : réécrire le fichier, puis `identifier` → `revoquee`.
- `test_un_registre_absent_illisible_ou_invalide_n_accorde_rien` : quatre cas (absent, JSON cassé, format inconnu,
  doublon de pseudonyme actif ou d'empreinte) → `registre_invalide` pour une clé pourtant listée.
- `test_le_registre_ne_contient_aucune_cle_en_clair`.
- `test_deux_fils_qui_identifient_en_meme_temps_ne_melangent_pas_les_clients`.

## Tâche 2 : l'outil des clés (R3, R4)

**Fichiers** : `acces/cles.py` (créer) ; `tests/test_outil_cles.py` (créer).
**Interfaces** : `python -m acces.cles {creer|revoquer|remplacer|lister} [pseudonyme] [--role ...] [--registre CHEMIN]`.
`creer` et `remplacer` affichent la clé **une fois** sur la sortie standard, rien d'autre ne la contient ; `lister`
n'affiche ni clé ni empreinte ; écriture par fichier temporaire puis `os.replace` ; refus d'écrire si le registre lu
est invalide.
**Tests** : `test_creer_affiche_la_cle_une_fois_et_garde_son_empreinte` ; `test_remplacer_revoque_l_ancienne_et_en_cree_une_nouvelle` ;
`test_lister_ne_montre_ni_cle_ni_empreinte` ; `test_l_outil_refuse_d_ecrire_un_registre_deja_invalide` ;
`test_l_ecriture_est_atomique` (le fichier n'est jamais lu à moitié écrit : relu valide avant et après).

## Tâche 3 : l'API identifie par la clé (R1, R2)

**Fichiers** : `api/main.py` (modifier `verify_api_key`, retirer `cle_attendue`, docstring et tableau ligne 82) ;
`tests/test_cle_par_client.py` (créer) ; `tests/test_refus_cle_journal.py` (modifier).
**Interfaces** : `verify_api_key(request, api_key) -> Client` ; pose `request.state.client` ; refus → 403 avec le motif
au journal (`absente`, `inconnue`, `revoquee`), jamais la clé ; registre invalide → 503 `ACCES_INDISPONIBLE`.
Une ligne INFO par requête protégée acceptée : `acces : request_id=… client=… route=… statut=…`.
**Tests** :
- `test_deux_cles_actives_sont_acceptees` (A et B → 200 sur `/sante`).
- `test_a_revoquee_recoit_403_et_b_garde_200` (sans appel au modèle).
- `test_une_cle_revoquee_est_journalisee_refusee_jamais_authentifiee`.
- `test_un_registre_invalide_donne_503_sans_secret`.
- `test_le_middleware_voit_l_identite_posee_par_la_dependance` (vigilance 4).
- `test_une_cle_collee_avec_une_espace_est_refusee` (vigilance 2).
- `test_une_cle_invalide_ne_consomme_pas_le_quota` (l'ordre clé puis quota, lignes 273 et 408, gardé).

## Tâche 4 : les deux chemins d'audit (R2)

**Fichiers** : `api/main.py` (middleware lignes 149 à 160 ; `/audit/mcp` lignes 230 à 240) ; `tests/test_audit_mcp.py`
(modifier).
**Interfaces** : le middleware écrit une ligne `mcp_calls` **après** la réponse quand `request.state.client.role ==
"passerelle"`, avec `client_id = pseudonyme` ; `X-Client-Id` n'est plus lu. `/audit/mcp` exige le rôle `passerelle`
(sinon 403, aucune ligne), écrit **avant** de répondre, `client_id = pseudonyme`, renvoie `{"enregistre": ok}`.
**Tests** :
- `test_une_cle_a_avec_un_en_tete_b_est_attribuee_a_a`.
- `test_une_cle_inconnue_avec_l_en_tete_d_un_client_est_refusee_sans_attribution`.
- `test_un_appel_du_navigateur_n_ecrit_rien_dans_mcp_calls`.
- `test_audit_mcp_refuse_une_cle_utilisateur_valide_et_n_ecrit_rien` (précision 2).
- `test_audit_mcp_ecrit_une_seule_ligne_avec_le_pseudonyme_de_la_passerelle`.
- `test_audit_mcp_refuse_toujours_un_client_id_dans_le_json`.
- `test_un_audit_en_panne_laisse_un_avertissement_et_le_refus_metier_reste_un_refus`.

## Tâche 5 : la passerelle MCP a sa propre clé (R4)

**Fichiers** : `passerelle_mcp/serveur.py` (lignes 283 à 300 et 345) ; `tests/test_passerelle_mcp.py` (modifier) ;
`.env.example`.
**Interfaces** : `_cle_api()` lit `RITA_CLE_PASSERELLE` (message d'erreur à jour) ; les en-têtes deviennent
`{"X-API-Key", "X-Outil"}`, sans `X-Client-Id`.
**Tests** : `test_la_passerelle_presente_sa_propre_cle` ; `test_la_passerelle_refuse_de_demarrer_sans_sa_cle` ;
`test_la_passerelle_n_envoie_plus_d_identite_declaree`.

## Tâche 6 : le déployeur connaît le registre et le plancher (R1, retour arrière)

**Fichiers** : `deploy/deployer.py` ; `Dockerfile` (étiquette `rita.acces=registre`) ; `tests/test_deployer_scenarios.py`.
**Interfaces** : avant de déployer, le déployeur valide le registre du serveur avec `acces.registre` (refus si absent
ou invalide, sans secret) ; `Version` gagne `acces_par_registre: bool` (lu sur l'étiquette de l'image) ; l'état gagne
`plancher_acces: bool` ; nouvelle commande `plancher-acces` ; `revenir` refuse une cible sans registre quand le
plancher est posé ; le contrôle d'une version garde la clé de **sa** copie du `.env` (ligne 666).
**Tests** :
- `test_un_deploiement_est_refuse_si_le_registre_du_serveur_est_invalide`.
- `test_phase_1_le_retour_vers_une_version_sans_registre_est_autorise_sans_plancher`.
- `test_phase_2_le_plancher_refuse_le_retour_vers_une_version_sans_registre`.
- `test_phase_3_le_retour_vers_n1_garde_les_revocations_et_se_controle_avec_sa_cle_deploiement`.

## Tâche 7 : Compose et les chaînes de CI

**Fichiers** : `docker-compose.yml` (service `api` : volume `${RITA_DOSSIER_ACCES}` en lecture seule vers
`/run/rita-acces`, `RITA_REGISTRE_CLES=/run/rita-acces/cles.json`, `RITA_API_KEY` retirée de l'environnement de
l'API) ; `.github/workflows/livraison.yml` (ligne 183 : le contrôle au démarrage monte un registre d'essai créé dans
la tâche, puis vérifie 200 avec la clé d'essai et 403 sans) ; `.github/workflows/scan-giskard.yml` ;
`tests/test_docker_compose.py`.
**Tests** : `test_le_conteneur_lit_le_registre_en_lecture_seule` ; `test_l_api_ne_recoit_plus_la_cle_commune` ;
la chaîne de livraison verte sur la PR.

## Tâche 8 : la documentation et le registre RGPD (R3, R5)

**Fichiers** : `docs/exploitation.md` (section « Les clés d'accès » : créer, remettre, révoquer, remplacer ; la bascule
des phases 0 à 3 ; le retour arrière et le plancher) ; `db/RGPD-registre-des-traitements.md` (T5 : pseudonymes ;
registre des clés : pseudonymes, empreintes, dates, conservation réelle ; **ligne 221 corrigée** : la purge P6 est
lancée à la main) ; `.env.example` ; `README.md` si une commande change.
**Vérification** : `C:\Python314\python.exe scripts\verifier_liens.py` → 0 lien cassé ; zéro tiret long ajouté.
La correspondance pseudonyme → personne reste chez Era, hors du dépôt.

## Tâche 9 : en production, avec la preuve datée (R5)

**Qui** : Era exécute les phases 0 à 3 ; l'assistant prépare chaque commande et relit chaque sortie.
**Preuve** : `evidence/C5/cle-par-client-AAAA-MM-JJ.md` : dates et heures, commit en production (`/health`), statuts
HTTP obtenus (200, 403) par pseudonyme, ligne `passerelle-mcp` dans `mcp_calls`, sans aucune clé ni empreinte.
**Mise à jour** : `ETAT.md`, une entrée au `CHANGELOG` (décision structurante), `docs/BUDGET.md` (l'évolution passe
de « prévue » à « faite », avec la date).

## Estimation

| Tâche | Heures |
|---|---:|
| 0 · branche, registre d'essai des tests, inventaire | 1 |
| 1 · registre | 3 |
| 2 · outil des clés | 2 |
| 3 · l'API identifie par la clé | 2 |
| 4 · les deux chemins d'audit | 2 |
| 5 · passerelle | 1 |
| 6 · déployeur et plancher | 3 |
| 7 · Compose et CI | 1,5 |
| 8 · documentation et RGPD | 2 |
| 9 · production et preuve | 2, plus le temps d'Era |
| **Total** | **19,5 h, soit environ 2,5 journées** |

**Écart à signaler** : `docs/BUDGET.md` estimait 1 à 2 journées (400 à 800 € HT). Le plan en compte environ 2,5
(environ 1 000 € HT au TJM de 400 € HT), à cause de la révocation sans redémarrage, de la migration et du retour
arrière. Era décide s'il faut mettre le budget à jour.

## Calendrier visé

Tâches 0 à 8 sur la branche `cle-par-client`, une PR vers `develop` ; puis `develop → main` ; déploiement hors du
créneau de 7 h 30 à 9 h. Visé : avant l'oral blanc des 12-13/11 ; au plus tard avant le gel de l'application (vers le
24/11, date à fixer par Era). Si le temps manque avant l'oral blanc : la spécification et le plan validés se
présentent comme « suite prévue », sans crédit sur le non-fait.

## Décision à prendre par Era avant le code

- **D5** : un registre invalide donne **503** (panne du service) plutôt que 403. À confirmer.
- **Emplacement** : `/root/rita-acces/cles.json` sur le serveur. À confirmer.

## 📖 Glossaire

- **Registre des clés** : le fichier qui liste, pour chaque accès, son pseudonyme, son rôle, l'empreinte de sa clé et
  ses dates ; jamais la clé.
- **Empreinte (SHA-256)** : un résumé de 64 caractères calculé à partir de la clé ; on ne peut pas retrouver la clé
  depuis l'empreinte.
- **Écriture atomique** : écrire dans un fichier temporaire puis le renommer d'un coup, pour qu'aucun lecteur ne voie
  un fichier à moitié écrit.
- **Plancher de retour arrière** : la règle qui interdit de revenir à une version trop ancienne pour connaître le
  registre.
- **Étiquette d'image** : une information écrite dans l'image Docker (ici `rita.acces=registre`), lisible sans la
  lancer.
- **`request.state`** : un espace propre à chaque requête, partagé par les étapes qui la traitent.
- **503** : « service indisponible » ; **403** : « accès refusé ».

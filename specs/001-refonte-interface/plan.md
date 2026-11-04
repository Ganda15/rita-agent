# Plan d'implémentation 001 : la refonte de l'interface de RITA

> **Pour l'agent qui exécute** : suivre les tâches dans l'ordre, une à la fois, test d'abord (rouge, puis le code, puis
> vert), une tâche = un commit et une chaîne verte. Cases à cocher `- [ ]` pour le suivi.

**But** : les écrans Briefing, Indicateurs et Portefeuille refaits selon la conception du 04/10, une API qui dit comment
un briefing a été produit, un mode simulation pour répéter, les cinq écrans cohérents, en production le 10/11.

**Architecture** : l'API gagne un bloc `diagnostic` dans la réponse de `/briefing` et une erreur `503 AUCUN_FOURNISSEUR`,
transmis du modèle (`src/llm.py`) au graphe puis à la route, sans état partagé. L'interface reste en HTML, CSS et
JavaScript sans outil de construction : un en-tête identique dans les cinq pages, un `commun.js` (clé, appels, mode),
un `graphiques.js` de fonctions pures qui fabriquent du SVG, et trois écrans réécrits sur ces deux fichiers.

**Pile** : Python 3.13 (CI) et 3.14 (poste), FastAPI, LangGraph, pytest, Playwright (Chromium) ; HTML, CSS, JavaScript.

**Spécification** : `specs/001-refonte-interface/spec.md` (validée le 04/11) ; conception : `docs/conception/frontend/refonte-2026-10.md`.

**Branche** : `refonte-interface`, créée depuis `develop` ; fusion dans `develop` à chaque tâche verte, puis `develop` vers
`main` le 10/11.

## Contraintes globales (valables pour chaque tâche)

- **AMF** : aide à la lecture, jamais une recommandation ; aucun des mots refusés par `tests/test_frontend.py:329-355`
  (« achetez », « vendez », « signal d'achat », « survendu », etc.) dans un texte affiché.
- **Verdict** affiché, mot pour mot : « Aucune recommandation d'achat ou de vente détectée ».
- **Sources**, titre exact du bloc : « Sources fournies au modèle ».
- **RSI**, forme exacte : « RSI 14 : {valeur}, zone neutre de 30 à 70 ».
- **Aucune insertion de HTML** : ni `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write` ; le texte par
  `textContent`, le SVG par `document.createElementNS`.
- **Clé** : `sessionStorage`, clé de stockage `rita_api_key`, jamais `localStorage`, jamais écrite dans le code ; gardée
  seulement après une réponse réussie, effacée sur 401 ou 403 (correctif #73, à préserver).
- **Aucune ressource tierce** : pas de CDN, pas de police distante, pas de bibliothèque de graphiques.
- **Couleurs** des écrans, **deux thèmes** (décision d'Era du 04/11 après-midi : style B sombre par défaut, style A clair
  au choix). Thème clair : Portefeuille `#1e7b45`, Indicateurs `#3f3fa8`, Briefing `#a35a00`, Question et Tableau de bord
  `#12507a`. Thème sombre : `#4ccb8a`, `#a5a8ff`, `#f2a93b`, `#6cb8ea`, sur des cartes `#0f2643` ; le fond est un
  **dégradé CSS** du bleu nuit `#061527` au bleu `#14507f` (couverture du livret E1, demande d'Era du 04/11 au soir),
  sans image ; textes éclaircis (`#f5f8fc`, `#c5d3e4`) pour être plus lisibles.
- **Logo** : la marque officielle de RITA dans l'en-tête des cinq pages, réduite à 64 px (environ 3 Ko), carré blanc
  sur le sombre, carré bleu nuit sur le clair, en image de fond (une seule version téléchargée) ; la version bleu nuit
  sert d'icône d'onglet, ce qui supprime le 404 de `favicon.ico` (constat F3 du 03/10).
  Chaque paire texte et fond est calculée par un test, dans les deux thèmes, contre le seuil de 4,5:1.
- **Thème** : `<html data-theme="clair">` pour le clair, rien pour le sombre ; `theme.js`, chargé dans `<head>`
  avant l'affichage, lit le choix dans `sessionStorage` (`rita_theme`), jamais dans `localStorage` ; sans JavaScript,
  le site s'affiche en sombre et le bouton reste caché.
- **Polices** (demande d'Era du 04/11) : déjà installées, aucune téléchargée, aucun `@font-face` : `--police-texte`
  (Segoe UI Variable Text, SF Pro Text), `--police-titres` (Segoe UI Variable Display, SF Pro Display),
  `--police-chiffres` (Cascadia Mono, SF Mono), chacune finie par une famille générique.
- **Rien par la couleur seule** : chiffres signés, flèches ▲ ▼, légendes ; chaque graphique a une alternative en chiffres.
- **Écriture** : français, aucun tiret long (le tiret cadratin), dans le code comme dans les textes.

## Points de vigilance (non couverts par la spécification, testés quand même)

1. **Une réponse tardive** : l'utilisateur change de valeur pendant qu'une courbe ou un briefing charge ; l'ancienne
   réponse ne doit jamais s'afficher pour la nouvelle valeur. Test dans la tâche 7 (`test_reponse_tardive_ignoree`).
2. **Un lien d'article piégé** (`javascript:`, `data:`) : il ne doit jamais devenir cliquable. Test dans la tâche 3
   (`test_lien_non_http_mis_a_null`) et la tâche 7 (`test_lien_null_non_cliquable`).
3. **Les cotations arrivent de la plus récente à la plus ancienne** : la courbe et les moyennes doivent les remettre dans
   l'ordre. Test dans la tâche 6 (`test_courbe_trie_les_dates`).
4. **Basculer en simulation pendant un appel réel** : la réponse réelle arrivée après coup ne doit pas s'afficher sous la
   mention « Simulation ». Test dans la tâche 10 (`test_reponse_reelle_ignoree_apres_bascule`).
5. **Portefeuille incomplet** (`complet` faux, `total_eur` à `null`) : pas d'anneau, un cadre qui dit combien de lignes
   n'ont pas de taux. Test dans la tâche 9 (`test_pas_d_anneau_si_incomplet`).

---

## Tâche 0 : la mesure « avant » et la branche

**Fichiers** : créer `evidence/C17/mesures-<date réelle>-avant/` (sorties des outils de
`evidence/C17/mesures-2026-10-03/outils/`).

- [ ] Créer la branche `refonte-interface` depuis `develop`.
- [ ] Rejouer la mesure du 03/10 sur les écrans actuels, mêmes outils et mêmes réglages (bureau 1350 × 940, mobile 412 × 823),
      commandes du fichier `evidence/C17/preuve-eco-conception-et-accessibilite-2026-10-03.md:128-138`.
- [ ] Attendu : `resume-bureau.json`, `resume-mobile.json`, `ecoindex-resume.json`, `clavier.json` ; le score constaté est
      noté tel quel, sans le présupposer ; un écart déjà présent est écrit comme tel. Mêmes versions d'outils, mêmes
      données, même état de page, même cache et mêmes dimensions qu'à la mesure « après ».
- [ ] Commit : « Mesure avant la refonte (accessibilité, EcoIndex, clavier), écrans actuels ».

## Tâche 1 : le modèle dit qui a répondu (R4)

**Fichiers** : modifier `src/llm.py:205-243` ; tests `tests/test_llm.py`.

**Interfaces produites** :
- `@dataclass ResultatTexte(texte: str, fournisseur: str, modele: str | None, tentatives: list[dict])`, chaque tentative
  `{"fournisseur": str, "reussi": bool}`, jamais de message d'erreur ;
- `generer_texte_detaille(prompt: str, max_tokens: int = 500) -> ResultatTexte` ;
- `generer_texte(prompt, max_tokens=500) -> str` garde sa signature et renvoie `generer_texte_detaille(...).texte` ;
- `class AucunFournisseur(RuntimeError)` avec l'attribut `tentatives: list[dict]`, levée quand tous échouent (le message
  actuel « Aucun fournisseur LLM disponible. » est gardé : `tests/test_llm.py:31-38` reste vert).

- [ ] Tests rouges : `test_detaille_dit_le_fournisseur_et_le_modele_reels` (le modèle vient de `Reponse.modele`, pas de
      `_modele_prevu`) ; `test_modele_null_si_non_renvoye` ; `test_tentatives_sans_message_d_erreur` (deux fournisseurs, le
      premier lève, `tentatives == [{"fournisseur": "foundry", "reussi": False}, {"fournisseur": "anthropic", "reussi": True}]`) ;
      `test_tous_en_panne_leve_aucun_fournisseur` (`isinstance(e, RuntimeError)` et `e.tentatives` de longueur 2).
- [ ] Inventaire avant de modifier : les tests qui remplacent `agents.analyst.generer_texte` ou `generate_briefing`
      (`tests/test_analyst.py`, `tests/test_briefing_422.py`, `tests/test_cas_chapitre_donnees.py`, `tests/test_workflow.py`) ;
      ils sont adaptés au niveau réellement appelé, sans changer ce qu'ils attendent et sans appel réel ; les tests de
      traces sans texte et de comptage des jetons restent verts.
- [ ] Code, puis `C:\Python314\python.exe -m pytest tests/test_llm.py tests/test_analyst.py tests/test_cas_chapitre_donnees.py -q` vert.
- [ ] Commit.

## Tâche 2 : le graphe garde le diagnostic du modèle (R4)

**Fichiers** : modifier `agents/analyst.py:169-195`, `graph/state.py:5-29`, `graph/workflow.py:65-90` ; tests
`tests/test_workflow.py`.

**Interfaces** :
- consomme `generer_texte_detaille`, `ResultatTexte` (tâche 1) ;
- produit `generate_briefing_detaille(...mêmes paramètres que generate_briefing...) -> ResultatTexte` ;
  `generate_briefing` garde sa signature et renvoie `.texte` ;
- `RitaState` gagne `modele_info: dict` (`fournisseur`, `modele`, `tentatives`), rempli par `noeud_redacteur` ; `{}`
  quand le rédacteur est sauté.

- [ ] Tests rouges : `test_redacteur_range_le_diagnostic_dans_l_etat` ; `test_redacteur_saute_laisse_un_diagnostic_vide` ;
      mettre à jour les tests qui remplacent `graph.workflow.generate_briefing` pour remplacer
      `graph.workflow.generate_briefing_detaille` (lister ceux de `tests/test_workflow.py` avant de modifier).
- [ ] Code, puis `pytest tests/test_workflow.py tests/test_llm.py -q` vert.
- [ ] Commit.

## Tâche 3 : `/briefing` renvoie `diagnostic` et `503 AUCUN_FOURNISSEUR` (R4)

**Fichiers** : modifier `api/main.py:279-365` ; ajouter `place_de_cotation(ticker: str) -> str` dans `sources/marches.py`
(appuyée sur `_place`, `:40`) ; tests `tests/test_briefing_diagnostic.py` (nouveau), `tests/test_briefing_422.py:18-19, 56-60`
(jeu de clés), `tests/test_api_donnees.py:208` (contrat).

**Interfaces** : consomme `state["modele_info"]` (tâche 2) et `AucunFournisseur` (tâche 1). Produites (contrat exact, conception § 6) :
- réponse 200 : les huit clés actuelles plus `diagnostic` = `{fournisseur, modele, tentatives, duree_ms, date_cours,
  age_calendaire_jours, jours_bourse_ecoules, calendrier, sources}` ;
- `date_cours` = `state["indicateurs"]["date_cours"]` (enregistrée par la base, `indicateurs/socle.py:87`), **jamais
  reconstruite** ; `null` si elle manque ; la date de référence est le jour à Paris (`Europe/Paris`) au moment de la
  réponse ; `age_calendaire_jours` = référence moins `date_cours` ; `jours_bourse_ecoules` =
  `jours_ouvres_ecoules(date_cours, référence)` et `calendrier` = « Euronext » si la place est Euronext, sinon les deux
  à `null` ;
- `sources` : un élément par article de `state["passages"]` (déjà filtrés par `articles_surs`, `graph/workflow.py:57`,
  et filtrés à nouveau pour le prompt, `agents/analyst.py:57`), **dédoublonné par `article_id`**, ordre gardé, champs
  `titre`, `source`, `publie_le`, `lien` ; `lien` à `null` si son schéma n'est pas `http` ou `https`, sans fusionner
  des articles distincts sous `null` ; jamais le texte ;
- `duree_ms` : la mesure déjà faite par la route, entier ≥ 0 ;
- tous les fournisseurs en panne (`AucunFournisseur`) : 503,
  `{"detail": {"code": "AUCUN_FOURNISSEUR", "message": "Aucun fournisseur de modèle n'a répondu."}}`, avec `X-Request-ID` ;
  toute autre exception reste le 500 générique du middleware (`api/main.py:118-129`) ;
- le contrat OpenAPI de `/briefing` décrit 200 avec `diagnostic`, 503 et 500.

- [ ] Tests rouges : `test_diagnostic_present_et_complet` ; `test_sources_un_par_article_dans_l_ordre` ;
      `test_sources_vide_sans_passage` ; `test_lien_non_http_mis_a_null` ; `test_aucun_texte_d_article_dans_sources` ;
      `test_tous_fournisseurs_en_panne_donne_503` (corps exact, en-tête `X-Request-ID`) ; `test_autre_exception_reste_500` ;
      `test_deux_requetes_simultanees_ne_se_melangent_pas` (deux fils, deux valeurs, diagnostics distincts) ;
      `test_contrat_openapi_decrit_503` ; jeu de clés mis à jour dans `test_briefing_422.py` ;
      `test_date_cours_lue_dans_la_base` ; `test_date_absente_dite_indisponible` ; `test_week_end_et_valeur_hors_euronext`
      (horloge figée) ; `test_sources_egales_aux_articles_du_prompt` (un passage rejeté n'apparaît ni dans le prompt ni
      dans les sources) ; `test_plusieurs_passages_d_un_article_une_source` ; `test_articles_sans_lien_non_fusionnes`.
- [ ] Code, puis `pytest tests/test_briefing_diagnostic.py tests/test_briefing_422.py tests/test_api_donnees.py tests/test_request_id.py -q` vert, puis la suite complète.
- [ ] Commit.

## Tâche 4 : un en-tête identique dans les cinq pages, et les deux thèmes (R5)

**Fichiers** : modifier les cinq `frontend/*.html` (bloc `<header>`), `frontend/style.css` ; tests `tests/test_entete_commun.py`
(nouveau), `tests/test_frontend.py`, `tests/test_tableau_de_bord.py`.

**Décisions** :
- l'en-tête reste du **HTML écrit dans chaque page** (il marche sans JavaScript) : titre, sous-titre, avertissement AMF,
  navigation vers les cinq écrans, l'écran courant en `aria-current="page"` ; aujourd'hui Indicateurs et Briefing n'ont
  pas le lien Question, et Tableau de bord n'a pas l'avertissement AMF : les deux écarts sont corrigés ;
- `body` porte `data-ecran="portefeuille|indicateurs|briefing|question|tableau-de-bord"` ; `style.css` définit
  `--couleur-ecran` par écran (couleurs des contraintes globales), dans les deux thèmes, focus visible,
  `prefers-reduced-motion`.

- [ ] Tests rouges : `test_les_cinq_entetes_sont_identiques_hors_page_courante` ; `test_chaque_page_a_les_cinq_liens` ;
      `test_chaque_page_a_l_avertissement_amf` ; `test_une_couleur_par_ecran_refait` ;
      `test_contrastes_des_deux_themes` (chaque paire texte et fond, clair et sombre, au moins 4,5:1) ;
      `test_theme_sombre_par_defaut_et_bouton_cache_sans_javascript` ; `test_le_theme_n_utilise_jamais_localstorage` ;
      dans un vrai navigateur, `test_bascule_du_theme_suit_la_navigation` (le choix tient sur les cinq écrans) ;
      `test_aucun_chargement_tiers` (aucun script, feuille de style, police, image, `iframe`, `@import` ni `url()` vers
      un autre site ; les liens `<a href>` en `http(s)` vers les sources restent permis).
- [ ] Code, puis `pytest tests/test_entete_commun.py tests/test_frontend.py tests/test_tableau_de_bord.py -q`, et les tests
      Playwright de Question et Tableau de bord (`tests/test_smoke_tableau_de_bord.py`, `tests/test_recette_clavier.py`) verts.
- [ ] Commit.

## Tâche 5 : `commun.js` (R5, R7)

**Fichiers** : créer `frontend/commun.js` ; tests `tests/test_commun_ui.py` (nouveau, Playwright, fixtures de
`tests/test_smoke_ui.py:27-58`).

**Interfaces produites** (globales `window.RITA`) :
- `lireCle() -> string|null`, `garderCle(cle)`, `oublierCle()` ;
- `appeler(chemin: string, options?: {methode, cle}) -> Promise<Response>` : ajoute `X-API-Key`, oublie la clé sur 401 ou
  403, ne la garde qu'après une réponse réussie ;
- `estSimulation() -> boolean`, `basculerSimulation(actif: boolean)` (stockage `sessionStorage`, clé `rita_simulation`) ;
- `afficherMentionSimulation()` : pose la mention permanente « Simulation : données d'exemple, aucun modèle appelé » quand
  le mode est actif.

Question et Tableau de bord **ne sont pas réécrits** : ils chargent `commun.js` **avant** leur propre script ; en
simulation, `question.js` et `tableau-de-bord.js` s'arrêtent dès leur démarrage : aucun appel, aucune minuterie,
l'envoi du formulaire neutralisé (clavier compris), la mention « Simulation non disponible pour cet écran » et un
bouton « Quitter la simulation » (décision D1).

Précisé le 04/11 au soir, avant le code (le plan ne disait pas où se fait le choix explicite) :
- le **choix explicite** est un bouton « Mode simulation » de l'en-tête commun, à côté de « Thème clair » (`aria-pressed`,
  caché sans JavaScript) ; changer de mode **recharge la page**, ce qui efface les résultats affichés dans les deux sens ;
- **deuxième barrière** : en simulation, `commun.js` refuse tout appel vers une route de RITA (`/briefing`, `/question`,
  `/donnees`, `/sante`, `/health`, `/audit`, `/exercice`) ; les fichiers statiques et le futur jeu d'exemple restent permis ;
- jusqu'à la tâche 10, les **cinq** écrans se suspendent en simulation (aucun n'a encore de données d'exemple) : à chaque
  commit, aucune donnée réelle sous la mention « Simulation » ;
- **cache** (trouvé en vérifiant dans le navigateur) : sans `Cache-Control`, Chrome gardait l'ancien `tableau-de-bord.js` à
  côté du nouveau `commun.js`, et la page montrait le vrai tableau sous la mention ; l'interface est désormais servie avec
  `Cache-Control: no-cache` (revalidée à chaque visite, 304 sans corps si rien n'a changé) ; test `tests/test_cache_frontend.py`.

- [ ] Tests rouges : `test_cle_gardee_seulement_apres_succes` ; `test_cle_oubliee_sur_403` ;
      `test_mention_simulation_visible_sur_chaque_ecran` ; `test_mode_reel_par_defaut` ;
      `test_question_et_tableau_suspendus_en_simulation` (aucune requête vers `/question`, `/sante`, `/health`,
      `/donnees/articles/{id}`, minuterie arrêtée, envoi au clavier bloqué) ; `test_quitter_la_simulation_rend_le_mode_reel` ;
      `test_bascule_efface_les_resultats` (dans les deux sens) ; `test_navigation_des_cinq_pages_avec_une_cle_gardee`.
- [ ] Code, puis les tests verts.
- [ ] Commit.

## Tâche 6 : `graphiques.js`, des fonctions pures (R1, R2, R3)

**Fichiers** : créer `frontend/graphiques.js` ; tests `tests/test_graphiques_ui.py` (nouveau, Playwright `page.evaluate`).

**Interfaces produites** (globales `window.GRAPHIQUES`), chacune renvoie `{svg: SVGElement, alternative: HTMLElement}` :
`courbe(cotations: {date_seance, cloture}[])` avec moyennes 20 et 50 séances (les noms de champs de l'API ; `cloture` arrive
en texte décimal, « 401.5000 », mesuré le 04/11, et `lireNombre` le convertit, tout autre texte étant écarté) ; `anneau(poids: {nom, poids_pct}[])` ;
`barres(lignes: {nom, performance_pct}[])` ; `jauge(rsi: number)` ; plus `moyenneMobile(valeurs: number[], n) -> (number|null)[]`,
**seul calcul fait par l'écran** (exception écrite dans la spécification, § 5) : le serveur fournit les dernières valeurs
de MA20 et MA50 (`db/indicateurs.sql:95-107`, `/donnees/indicateurs`) ; pour tracer leurs courbes historiques, le
navigateur calcule les séries à partir des cotations retournées par l'API, avec la même règle que la base : la fenêtre
inclut la séance du jour, et la moyenne vaut `null` tant qu'il manque une séance (moins de 20, ou de 50).

- [ ] Tests rouges : séries de **0, 1, 19, 20, 49, 50 et 179** séances (messages de la conception § 5) ;
      `test_courbe_trie_les_dates` ; `test_moyennes_egales_a_un_calcul_independant` ; `test_valeurs_manquantes` ;
      `test_cours_constants` ; `test_anneau_non_dessine_si_poids_nuls` ; `test_alternative_contient_les_memes_chiffres` ;
      `test_dernier_point_egal_a_la_valeur_du_serveur` (mêmes cotations et même date que `/donnees/indicateurs` : le
      dernier point de chaque série égale `ma20` et `ma50` du serveur, à l'arrondi de l'API près) ;
      `test_aucun_texte_insere_comme_html`.
- [ ] Code, puis les tests verts.
- [ ] Commit.

## Tâche 7 : l'écran Briefing (R3)

**Fichiers** : réécrire `frontend/briefing.html`, `frontend/briefing.js` ; tests `tests/test_briefing_ui.py` (nouveau),
`tests/test_frontend.py:490-506` (adapter : le 502 n'est plus « aucun fournisseur »).

**Comportements** (spécification R3 ; textes de la conception § 7) : flux vertical (chiffres clés, courbe, texte,
« Comprendre ce résultat », « Sources fournies au modèle ») ; un seul envoi par clic, bouton inactif pendant la
rédaction ; le texte retenu par le garde-fou jamais affiché ; un message par panne : 403, 422, 429, 502 « Valeur
introuvable », 503 « Aucun fournisseur de modèle n'a répondu », 500 avec la référence, serveur muet ; une panne de la
courbe n'efface pas le briefing, et l'inverse.

- [ ] Tests rouges, API interceptée (`page.route`) : `test_flux_vertical_dans_l_ordre` ; `test_comprendre_ce_resultat_affiche_le_diagnostic` ;
      `test_un_seul_envoi_par_clic` ; `test_texte_refuse_jamais_affiche` ; un test par panne ;
      `test_reponse_tardive_ignoree` ; `test_lien_null_non_cliquable` ; `test_verdict_mot_pour_mot` ;
      `test_focus_va_au_resultat_ou_a_l_erreur` ; `test_tout_s_actionne_au_clavier`.
- [ ] **Parcours à travers la vraie API** (`tests/test_parcours_briefing_api_reelle.py`, nouveau) : le serveur FastAPI
      démarre dans le processus de test (`uvicorn.Server` dans un fil), avec la base, la recherche et le fournisseur
      remplacés par des jeux contrôlés (`graph.workflow.collect`, `graph.workflow.rechercher`, `src.llm._appel_foundry`) ;
      **aucune réponse `/briefing` fabriquée par le navigateur** ; il vérifie le diagnostic affiché, les sources, la
      référence de la requête, le refus du garde-fou et le 503.
- [ ] Code, puis les tests verts et la suite complète.
- [ ] Commit.

## Tâche 8 : l'écran Indicateurs (R2)

**Fichiers** : réécrire `frontend/indicateurs.html`, `frontend/indicateurs.js` ; tests `tests/test_indicateurs_ui.py` (nouveau).

- [ ] Tests rouges : `test_carte_des_performances_lisible_sans_couleur` ; `test_rsi_ecrit_comme_un_fait` ;
      `test_courbe_au_choix_d_une_valeur` ; `test_nombre_de_valeurs_lu_dans_la_reponse` ; `test_un_bloc_en_panne_n_efface_pas_les_autres`.
- [ ] Code, puis les tests verts.
- [ ] Commit.

## Tâche 9 : l'écran Portefeuille (R1)

**Fichiers** : réécrire `frontend/index.html`, `frontend/app.js` ; tests `tests/test_portefeuille_ui.py` (nouveau).

- [ ] Tests rouges : `test_anneau_et_barres_avec_les_memes_chiffres` ; `test_pas_d_anneau_si_incomplet` (cadre « Poids non
      calculables : N ligne(s) sans taux de change ») ; `test_fraicheur_du_jeu_et_date_par_ligne` ; `test_aucune_performance_globale_inventee`.
- [ ] Code, puis les tests verts.
- [ ] Commit.

## Tâche 10 : le mode simulation (R7)

**Fichiers** : créer `frontend/simulation.js` et `frontend/donnees-exemple.json` (tiré du jeu `data/demo/`, sociétés
fictives et liens `demo.rita.invalid`, jamais les preuves réelles) ; tests `tests/test_simulation_ui.py` (nouveau),
`tests/test_simulation_texte.py` (nouveau).

- [ ] Tests rouges : `test_simulation_n_appelle_jamais_le_reseau` (aucune requête vers `/briefing` ni `/donnees/*`) ;
      `test_mention_permanente` ; `test_pas_de_bascule_silencieuse_sur_panne` ; `test_reponse_reelle_ignoree_apres_bascule` ;
      `test_textes_d_exemple_conformes_amf` (le texte d'exemple passe `guardrails.sortie.verifier_sortie` et le filtre de mots).
- [ ] Code, puis les tests verts.
- [ ] Commit.

## Tâche 11 : la mesure « après », la comparaison avec les maquettes, la documentation (R6)

**Fichiers** : créer `evidence/C17/mesures-<date réelle>-apres/` et `evidence/C17/preuve-refonte-<date réelle>.md` ; mettre à
jour `docs/ARCHITECTURE.md`, `docs/exploitation.md`, `docs/conception/frontend/refonte-2026-10.md` (§ 10 : la décision du 04/11).

- [ ] Rejouer la mesure de la tâche 0, mêmes conditions ; les interactions nouvelles mesurées à part.
- [ ] La preuve datée : commit testé, commandes, sorties, **tests sautés listés** ; chaque écran à côté de sa maquette, avec
      ce qui diffère et pourquoi.
- [ ] Attendu : accessibilité 100 (le seuil de la spécification) ; EcoIndex avant et après dans le même tableau ;
      clavier, focus et zoom à 200 % contrôlés sur les **trois** écrans refaits.
- [ ] Commit.

## Tâche 12 : en production, vérifiée, avec son secours (R6)

- [ ] PR `develop` vers `main`, sept contrôles verts, fusion par Era ; `/health` annonce le nouveau commit.
- [ ] Vérifier dans un vrai navigateur, sur la production : un vrai résultat, le clavier, un écran étroit (412 px) ; les
      refus et les pannes, par pannes injectées sur une copie du même commit ou par interception déclarée ; **aucune
      panne réelle provoquée en production** ; la preuve sépare les deux sortes de contrôles.
- [ ] Tester le retour à la version précédente (`retour-arriere.yml`), puis revenir à la nouvelle.
- [ ] Après le déploiement, recharger une fois sans cache (Ctrl+F5) dans le navigateur de la démonstration : les copies
      reçues avant le correctif du cache (tâche 5) n'avaient pas `no-cache` et peuvent rester quelques heures.
- [ ] Enregistrer une démonstration datée de secours ; noter le tout dans la preuve datée de la tâche 11.

---

## Faisabilité du calendrier

| Tâches | Estimation | Jours |
|---|---|---|
| 0 mesure avant | 1 h | 05/11 |
| 1, 2, 3 API (inventaire des tests, date, sources) | 7 h | 05-06/11 |
| 4, 5 en-tête, style, commun (simulation suspendue sur Question et Tableau de bord) | 4 h 30 | 06/11 |
| 6 graphiques | 3 h | 07/11 |
| 7 Briefing (parcours à travers la vraie API) | 4 h | 07/11 |
| 8 Indicateurs | 3 h | 08/11 |
| 9 Portefeuille | 2 h 30 | 08/11 |
| 10 simulation | 3 h | 09/11 |
| 11 mesures, comparaison avec les maquettes, preuve | 2 h 30 | 09/11 |
| 12 production | 2 h | 10/11 |
| réserve (corrections, relectures, pannes d'outils) | 6 h | répartie, jamais sur le 11/11 |
| **Total** | **38 h 30** (32 h 30 de travail, la revue ayant ajouté des tests, et 6 h de réserve) | **objectif 10/11, à réévaluer** |

**Point de contrôle** : le **06/11 au soir**, après les tâches 0 à 3 (le bloc API, le plus incertain), le reste est
réestimé et dit à Era. Le 11/11 reste réservé à la répétition : aucune correction de déploiement n'y est repoussée par défaut.

**Si un blocage est constaté** : le travail restant est dit précisément, tâche par tâche, et **Era décide**. L'ordre
proposé dans ce cas (Briefing complet en production d'abord, puis Indicateurs, Portefeuille, simulation) est une
**proposition**, pas une réduction de périmètre déjà autorisée : les trois écrans et la simulation restent dans le périmètre.

## Décisions

- **D1, la simulation sur Question et Tableau de bord** (proposition corrigée après la revue du 04/11, **confirmée par
  Era le 04/11**) : ces deux écrans n'ont pas de jeu d'exemple. En simulation, ils **n'affichent aucune donnée réelle** : leurs appels
  et leur actualisation sont suspendus, l'envoi du formulaire est neutralisé, clavier compris ; ils affichent « Simulation
  non disponible pour cet écran » et un bouton « Quitter la simulation ». La première proposition (laisser Tableau de bord
  relié à RITA sous la mention « Simulation ») est écartée : elle aurait montré des données réelles sous la mention.
- **Exécution** (**confirmée par Era le 04/11**) : une session qui fait les tâches elle-même, test d'abord, puis **une revue
  indépendante de toute la branche** avant la livraison. Les relectures d'Era au fil des jours sont des points de
  visibilité ; elles ne remplacent ni les tests ni la revue.

# Preuve C14 : spécifications fonctionnelles et wireframes des écrans 2 (indicateurs) et 3 (briefing)

> **Compétence C14** : *« Analyser le besoin d'application d'un commanditaire intégrant un service d'intelligence
> artificielle, en rédigeant les spécifications fonctionnelles et en le modélisant, dans le respect des standards
> d'utilisabilité et d'accessibilité […] »*
> Suite de [`preuve-specifications-wireframes.md`](preuve-specifications-wireframes.md), qui couvre l'écran 1 (portefeuille).
> Tâche T2 du plan E4 ([`../../docs/PLAN-E4-rapport.md`](../../docs/PLAN-E4-rapport.md)), carte #24.

**Date** : 2026-10-03

## ⚠️ À lire avant tout : ces spécifications sont écrites après le code

L'écran 2 date de la mi-août (18 et 19/08) et l'écran 3 du 3 octobre. **Aucune des deux spécifications n'a guidé la construction** : elles décrivent
ce que les écrans font, relu dans `frontend/` et confronté aux tests existants. Conséquences, dites d'emblée :

- les wireframes ci-dessous sont dessinés d'après l'écran réel ; qu'il leur soit conforme est donc vrai par construction, ce n'est
  pas une preuve de conformité à une maquette préalable ;
- l'exercice a quand même servi : écrire chaque critère d'acceptation et chercher sa vérification a fait trouver **un défaut réel** sur
  l'écran 3 (critère R10, carte #73) et **une erreur de référence** au référentiel d'accessibilité dans les documents de l'écran 1 (§6).

Les fichiers de cette preuve :

| Fichier | Rôle |
|---|---|
| [`WIREFRAMES-C14-ecran-indicateurs.png`](WIREFRAMES-C14-ecran-indicateurs.png) | les 4 états de l'écran 2, à regarder |
| [`WIREFRAMES-C14-ecran-indicateurs.drawio`](WIREFRAMES-C14-ecran-indicateurs.drawio) · [`.svg`](WIREFRAMES-C14-ecran-indicateurs.svg) | source modifiable (draw.io) et vectorielle |
| [`WIREFRAMES-C14-ecran-briefing.png`](WIREFRAMES-C14-ecran-briefing.png) | les 4 états de l'écran 3, à regarder |
| [`WIREFRAMES-C14-ecran-briefing.drawio`](WIREFRAMES-C14-ecran-briefing.drawio) · [`.svg`](WIREFRAMES-C14-ecran-briefing.svg) | source modifiable (draw.io) et vectorielle |
| [`../../frontend/indicateurs.html`](../../frontend/indicateurs.html), [`indicateurs.js`](../../frontend/indicateurs.js) | l'écran 2 réel |
| [`../../frontend/briefing.html`](../../frontend/briefing.html), [`briefing.js`](../../frontend/briefing.js) | l'écran 3 réel |
| [`../../tests/test_frontend.py`](../../tests/test_frontend.py), [`test_smoke_ui.py`](../../tests/test_smoke_ui.py) | les vérifications citées |

---

## 1. Les critères de C14 concernés, et où chacun est traité

| # | Critère officiel | Où |
|---|---|---|
| 2 | *« La modélisation des parcours utilisateurs respecte un formalisme : schéma fonctionnel, wireframes »* | §2 : wireframes d'état, comme pour l'écran 1 |
| 3 | *« Chaque spécification fonctionnelle couvre le contexte, les scénarios d'utilisation et les critères de validation »* | §3 (US-2) et §4 (US-3) |
| 4 | *« Les objectifs d'accessibilité sont intégrés aux critères d'acceptation des user stories »* | §3 et §4 : les lignes I9 à I12 et R9 à R11 |
| 5 | *« …formulés en s'appuyant sur un standard : WCAG, RGAA »* | RGAA 4.1.2, numéros contrôlés sur le texte officiel (§6) |

Le critère 1 (modèle de données) reste couvert par le MCD de l'écran 1 : un seul modèle des mêmes données.

---

## 2. Les wireframes : le même formalisme que l'écran 1, quatre états par écran

Un wireframe d'état montre un écran dans les quatre situations où l'utilisateur peut le trouver. C'est ce que fait le code : des sections
HTML dont la visibilité est pilotée par le JavaScript.

### Écran 2, indicateurs ([`indicateurs.js`](../../frontend/indicateurs.js))

| État | Déclencheur dans le code | Ce que voit l'utilisateur |
|---|---|---|
| 1 Aucune clé | `demanderCle()` : `sessionStorage` vide | le formulaire de connexion |
| 2 Chargement | `afficherStatut("Chargement des indicateurs…")` | un message d'attente annoncé vocalement |
| 3 Erreur | `403`, réponse en erreur, ou aucune réponse | le message de **la** panne rencontrée (trois messages distincts) |
| 4 Données | `afficher()` | le tableau de treize indicateurs par valeur, le filtre des cotations périmées, le glossaire |

### Écran 3, briefing ([`briefing.js`](../../frontend/briefing.js))

| État | Déclencheur dans le code | Ce que voit l'utilisateur |
|---|---|---|
| 1 Aucune clé | `demanderCle()` | le formulaire de connexion |
| 2 La demande | `ouvrirDemande()` | un champ « code de la valeur », une liste déroulante de l'univers suivi, une précision sur le modèle et le garde-fou |
| 3 Attente et pannes | `afficherStatut(...)` | l'attente (5 à 15 s) ou l'une des pannes : clé refusée, code inconnu, aucun modèle, autre erreur, aucune réponse |
| 4 Le briefing | `afficher()` | le cours, le verdict du garde-fou en mots, le texte en paragraphes, la référence de la requête |

Les trois pannes de l'écran 2 et les cinq de l'écran 3 sont **distinctes**, et leur message l'est aussi : une clé refusée n'est pas une panne
(on l'oublie et on la redemande), un serveur qui ne répond pas n'a **aucun code HTTP** à lire (d'où le `try/catch`), un code de valeur inconnu
et un modèle indisponible sont deux situations que le serveur signale par le même code 502 et que l'écran distingue par le détail renvoyé.

---

## 3. US-2 « Consulter les indicateurs de marché de l'univers suivi » (écran 2)

### Contexte

L'univers suivi compte 111 valeurs. Pour chacune, RITA calcule treize indicateurs en base (performances, moyennes mobiles, capitaux
échangés, distance au plus haut, volatilité, plus forte baisse, RSI). Sans écran, ils ne se lisent qu'en SQL ou par l'API.
**Le besoin** : lire en une page les treize indicateurs de chaque valeur, repérer celles dont la cotation est périmée, sans qu'on me dise quoi faire.
**Ce que l'application ne fait pas** : classer les valeurs, fixer un seuil, qualifier un niveau (« surachetée »), recommander. Chaque colonne est un fait
mesuré ; l'avertissement « Aide à la lecture. Aucune recommandation d'achat ou de vente. » est affiché en haut de la page.

### Scénarios d'utilisation

| # | Scénario | Parcours |
|---|---|---|
| S1 | Première visite | ouvrir l'écran, saisir la clé d'API, voir le tableau |
| S2 | Visite suivante, même onglet | le tableau s'affiche directement (clé en `sessionStorage`) |
| S3 | Clé invalide ou révoquée | 403, message, clé oubliée, nouvelle saisie |
| S4 | API arrêtée | message « Le serveur ne répond pas. Vérifiez que l'API est démarrée. » |
| S5 | Erreur du serveur | « Erreur 500 — le serveur n'a pas pu répondre. » avec le code reçu |
| S6 | Valeur à cotation périmée (probablement radiée) | la ligne s'affiche, son nom porte la mention « (cotation périmée — dernière séance le …) », son RSI est un tiret |
| S7 | Masquer les cotations périmées | une case à cocher filtre le tableau déjà chargé, sans appel réseau ; le compteur dit combien sont masquées |
| S8 | Historique trop court pour un indicateur | la cellule affiche un tiret, jamais un zéro |
| S9 | Le point de terminaison du lot 3 (volatilité, plus forte baisse, RSI) échoue | le lot 1 reste affiché, les trois colonnes du lot 3 affichent un tiret ; **aucun message** (voir §5) |

### Critères de validation et d'acceptation

« Vérifié par » nomme un test réel, ou dit que la vérification est une **lecture du code** quand aucun test ne la couvre.

| # | Critère d'acceptation | Standard | Vérifié par |
|---|---|---|---|
| I1 | Chaque valeur affiche ses treize indicateurs : cours, performances 1 jour, 1 semaine, 1 mois, depuis le 1er janvier, 1 an, MA20, MA50, échangé par jour, écart au plus haut, volatilité, plus forte baisse, RSI 14 | | `test_les_3_colonnes_du_lot_3_existent` pour le lot 3 ; **lecture** des 15 en-têtes de `indicateurs.html` pour le reste (aucun test ne compte les colonnes du lot 1) |
| I2 | Une valeur absente s'affiche « — », jamais 0 | utilisabilité | `test_une_valeur_absente_devient_un_tiret_et_non_un_zero` |
| I3 | Le signe + ou - est toujours écrit sur les variations ; la volatilité, qui est une amplitude, n'a pas de signe | **RGAA 3.1** | `test_le_signe_est_toujours_affiche_sur_les_indicateurs`, `test_la_volatilite_s_affiche_sans_signe` |
| I4 | Une cotation périmée est dite **en texte** dans le nom et dans le compteur, pas seulement par une couleur | **RGAA 3.1** | `test_la_peremption_est_signalee_en_texte_pas_seulement_en_couleur` |
| I5 | Le RSI n'est pas affiché pour une valeur périmée | exactitude | `test_le_rsi_n_est_pas_affiche_pour_une_valeur_perimee` |
| I6 | Aucun conseil, aucun seuil, aucun classement dans la page ni dans le code ; l'avertissement AMF est affiché | contrainte AMF | `test_aucun_conseil_sur_le_rsi_dans_la_page_ou_le_code` ; avertissement : **lecture** de `indicateurs.html` (le test d'avertissement ne porte que sur l'écran 1) |
| I7 | Une panne du lot 3 ne fait pas tomber le lot 1 ; les deux lots sont appariés **par ticker** ; les deux appels partent en parallèle | robustesse | `test_une_panne_du_lot_3_ne_fait_pas_tomber_le_lot_1`, `test_le_lot_3_est_apparie_par_ticker`, `test_les_deux_points_de_terminaison_du_lot_3_sont_appeles_en_parallele` |
| I8 | La clé n'est jamais en dur ; le champ est masqué ; la clé n'est mémorisée qu'**après** un appel réussi, en `sessionStorage` | sécurité | `test_aucune_cle_d_api_dans_le_code_de_l_ecran_indicateurs` ; masquage, mémorisation après succès, `sessionStorage` : **lecture** de `indicateurs.html` et `indicateurs.js` (le test sur `sessionStorage` ne porte que sur `app.js`) |
| I9 | Le tableau a un titre et des en-têtes associés aux cellules (colonnes et lignes) | **RGAA 5.4**, **5.7** | `test_les_marqueurs_d_accessibilite_de_l_ecran_2` (`<caption`, `scope="col"`), `test_les_en_tetes_de_ligne_sont_poses_par_le_rendu` (`scope="row"`) |
| I10 | La zone qui défile horizontalement est atteignable et lisible au clavier, avec un nom accessible et un focus visible | **WCAG 2.1.1**, **RGAA 7.3**, **10.7** | `test_la_zone_qui_defile_est_atteignable_au_clavier` ; focus visible : **lecture** de `style.css:35-37` et `:201` |
| I11 | Chaque changement de statut est annoncé par un lecteur d'écran ; la langue de la page est déclarée ; les zones de la page (en-tête, navigation nommée, contenu, pied) sont identifiées ; la page courante est signalée dans la navigation (bonne pratique, sans règle RGAA propre) | **RGAA 7.5**, **8.3**, **12.6** | `test_les_marqueurs_d_accessibilite_de_l_ecran_2` (`aria-live="polite"`, `role="status"`, `lang="fr"`, `aria-current="page"`) |
| I12 | La page a un titre, une structure de titres et des champs étiquetés | **RGAA 8.5**, **9.1**, **11.1** | **lecture** de `indicateurs.html` (`<title>`, `h1`/`h2`, `label for`) ; aucun test dédié |
| I13 | Le filtre agit sur les données déjà chargées et est relié au tableau qu'il modifie | utilisabilité | `aria-controls` : même test que I11 ; « sans appel réseau » : **lecture** du gestionnaire `change` |
| I14 | Aucun contenu de l'API n'est interprété comme du HTML | **OWASP A03** | `test_l_ecran_indicateurs_n_utilise_jamais_innerhtml` |
| I15 | Les termes sont définis dans l'écran | utilisabilité | **lecture** : le bloc « Comment lire ce tableau ? » définit chaque colonne et « cotation périmée » |

---

## 4. US-3 « Demander un briefing rédigé pour une valeur » (écran 3)

### Contexte

`POST /briefing` est le seul point de terminaison qui expose le modèle de langage. Jusqu'au 3 octobre il ne se demandait que par curl, par la passerelle MCP
ou par la documentation interactive. **Le besoin** : saisir le code d'une valeur et lire un court briefing en français, rédigé à partir des données
collectées (cours, variation, capitaux échangés, indicateurs, extraits d'articles), avec la preuve que le garde-fou de sortie l'a relu.
**Ce que l'application ne fait pas** : recommander d'acheter ou de vendre. Un texte qui en contiendrait une est retenu et remplacé par un message, avec
ses motifs. L'écran dit aussi qu'**aucune donnée du portefeuille n'est envoyée au modèle** : le scout (`agents/scout.py`) ne lit que les trois lectures de marché.

### Scénarios d'utilisation

| # | Scénario | Parcours |
|---|---|---|
| S1 | Première visite | saisir la clé, **la demande s'ouvre aussitôt** (la clé n'est pas encore vérifiée), choisir ou taper un code, lire le briefing |
| S2 | Visite suivante, même onglet | la demande s'ouvre directement |
| S3 | Clé invalide ou révoquée | découverte **à la première demande** (403) et non à la connexion : message, clé oubliée, retour à la saisie |
| S4 | Code inconnu | réponse 502 « absent » : « Valeur introuvable : « XX.PA » n'est pas dans l'univers suivi. » |
| S5 | Aucun fournisseur de modèle disponible | réponse 502 autre : « Aucun fournisseur de modèle ne répond pour le moment. Réessayez plus tard. » |
| S6 | API arrêtée, ou autre code HTTP | « Le serveur ne répond pas… » ou « Erreur N — le serveur n'a pas pu répondre. » |
| S7 | Texte retenu par le garde-fou | le verdict dit « Texte retenu par le garde-fou de sortie (motifs : …) » et le texte du modèle n'est pas diffusé |
| S8 | La liste déroulante de l'univers ne se charge pas | l'écran reste utilisable, on tape le code à la main |

### Critères de validation et d'acceptation

| # | Critère d'acceptation | Standard | Vérifié par |
|---|---|---|---|
| R1 | Un seul champ de saisie, le code de la valeur : lettres, chiffres, point, tiret, 16 signes au plus, mis en majuscules | utilisabilité, sécurité | **lecture** de `briefing.html` (`pattern`) et de `briefing.js` (`toUpperCase`) ; aucun test dédié |
| R2 | La demande est un `POST /briefing?ticker=…` avec l'en-tête `X-API-Key` | contrat OpenAPI | `test_l_ecran_briefing_appelle_le_point_de_terminaison_du_modele_en_post_avec_la_cle` |
| R3 | L'attente est dite : « de 5 à 15 secondes » | utilisabilité | `test_l_ecran_briefing_dit_que_la_redaction_prend_du_temps` |
| R4 | Le verdict du garde-fou est un **texte** (« conforme » ou « retenu », avec les motifs) ; la couleur ne fait que le répéter | **RGAA 3.1** | `test_le_verdict_du_garde_fou_est_dit_en_texte_pas_seulement_en_couleur` ; navigateur réel : `test_l_ecran_briefing_affiche_le_texte_et_le_verdict` |
| R5 | Le texte du modèle est inséré comme du texte, en paragraphes, jamais comme du HTML | **OWASP A03** | `test_le_texte_du_modele_est_rendu_en_paragraphes_sans_html`, `test_l_ecran_briefing_n_utilise_jamais_innerhtml` |
| R6 | Un code inconnu est dit en clair ; une clé refusée (403) est oubliée | utilisabilité | `test_un_ticker_inconnu_est_dit_en_clair_et_une_cle_refusee_est_oubliee`, `test_l_ecran_briefing_dit_quand_le_ticker_est_introuvable` (navigateur réel) ; les autres pannes (aucun modèle, serveur muet, autre code) : **lecture** |
| R7 | La référence de la requête (`X-Request-ID`) est affichée pour le support | traçabilité (C11) | `test_l_identifiant_de_requete_est_montre_pour_le_support` ; navigateur réel : même test que R4 |
| R8 | L'avertissement « Aucune recommandation d'achat ou de vente » est affiché | contrainte AMF | `test_l_avertissement_amf_est_sur_l_ecran_briefing` |
| R9 | La clé n'est jamais en dur ; le champ est masqué (`type="password"`) | sécurité | `test_aucune_cle_d_api_dans_le_code_de_l_ecran_briefing` ; masquage : **lecture** |
| **R10** | **La clé n'est mémorisée qu'après un appel réussi** | sécurité, cohérence avec A2 de l'écran 1 | **NON SATISFAIT** : voir §5, carte #73 |
| R11 | Les champs sont étiquetés, les statuts annoncés, la navigation nommée ; la page courante est marquée (bonne pratique) ; la langue est déclarée ; le focus est déplacé sur le résultat à son arrivée | **RGAA 11.1**, **7.5**, **12.6**, **8.3** ; **WCAG 2.4.3** | `test_les_marqueurs_d_accessibilite_de_l_ecran_3` (étiquettes, `aria-live`, `nav aria-label`, `aria-current`) ; `lang="fr"`, `role="status"` et le déplacement du focus : **lecture** (aucun test ne les contrôle sur cet écran) |
| R12 | La liste déroulante est un complément : sa panne n'empêche rien | robustesse | **lecture** de `remplirUnivers` ; aucun test |
| R13 | Rien du portefeuille de l'utilisateur n'est envoyé au modèle | confidentialité | **lecture** de `agents/scout.py` (trois lectures de marché seulement) ; la phrase est aussi affichée dans l'écran ; aucun test dédié |
| R14 | Les termes sont définis dans l'écran | utilisabilité | **lecture** : le bloc « D'où vient ce texte ? » (données, modèle, garde-fou, référence) |

---

## 5. Ce que cette écriture a fait trouver

1. **Défaut réel, écran 3 (R10, carte #73).** Dans `briefing.js`, le gestionnaire du formulaire de clé appelle `sessionStorage.setItem` dès la saisie, avant
   tout appel. Le commentaire placé juste au-dessus dit le contraire, et les écrans 1 et 2 respectent la règle. Effet : une fausse clé reste mémorisée dans
   l'onglet jusqu'à la première demande de briefing, qui répond 403 et l'oublie. Pas de fuite hors de l'onglet, mais une incohérence avec les deux autres
   écrans et avec le critère A2. **Pourquoi aucun test ne l'avait vue** : les deux tests navigateur de l'écran 3 posent la clé directement dans
   `sessionStorage`, le chemin du formulaire n'est jamais exercé. Correction prévue **après le tag du 15/10** (aucun code d'application avant), test d'abord.
2. **Écran 2, panne silencieuse du lot 3 (S9).** Le choix est voulu (une dépendance secondaire ne doit pas faire tomber l'écran principal) et testé, mais
   l'utilisateur ne peut pas distinguer « non calculable » de « service en panne » : trois colonnes de tirets sans explication. Limite assumée, à décider si on
   ajoute une mention.
3. **Un libellé qui change entre l'écran et le prompt.** L'écran 2 appelle la colonne « Pire baisse (1 an) » ; le prompt du rédacteur appelle le même
   indicateur « Drawdown maximal sur 1 an », et le drawdown n'est cité par aucun des 60 textes du banc
   (`../C7/indicateurs-cites-dans-les-textes-2026-10-03.md`). Rapprochement à tester, pas une cause établie.
4. **Des vérifications par lecture.** Sur les 29 critères d'acceptation ci-dessus (15 pour l'écran 2, 14 pour l'écran 3), 14 reposent en tout ou partie sur une
   lecture du code faute de test (I1, I6, I8, I10, I12, I13, I15, R1, R6, R9, R11, R12, R13, R14), dont six entièrement (I12, I15, R1, R12, R13, R14) :
   ce n'est pas un défaut, c'est une limite à dire.

## 6. Erratum sur l'écran 1 : la référence RGAA des messages de statut

En contrôlant les numéros de règle sur le texte officiel (RGAA 4.1.2, [accessibilite.numerique.gouv.fr](https://accessibilite.numerique.gouv.fr/methode/criteres-et-tests/),
page lue le 03/10/2026), j'ai trouvé que `preuve-specifications-wireframes.md` (critère A5) et deux étiquettes de tests rattachent les messages de statut à « RGAA 12.x »
ou « RGAA 4.x ». **Le code est correct** (`role="status"`, `aria-live="polite"`), **la référence est fausse** : la règle est le critère **7.5**
(*« Dans chaque page web, les messages de statut sont-ils correctement restitués par les technologies d'assistance ? »*). Même remarque pour « RGAA 10.x »
(critère A9, focus placé sur le champ) : je n'ai pu rattacher à ce geste aucune règle du thème 10 ; la référence la plus juste est WCAG 2.4.3 (ordre du focus),
la règle RGAA 10.7 portant, elle, sur la visibilité du focus. Une note datée est ajoutée en tête de l'ancien document et les étiquettes des tests sont corrigées ; **le texte d'origine n'est pas réécrit**.

Numéros utilisés dans ce document, contrôlés le 03/10/2026 sur le texte officiel :
3.1 information non donnée par la seule couleur · 5.4 titre associé au tableau · 5.7 cellules associées à leurs en-têtes · 7.3 script contrôlable au
clavier · 7.5 messages de statut · 8.3 langue par défaut · 8.5 titre de page · 9.1 structure par titres · 10.7 focus visible · 11.1 étiquette de champ ·
12.6 zones de regroupement atteignables ou évitables.

## 7. Ce qui n'est pas fait, dit franchement

| Manque | Conséquence |
|---|---|
| **Spécifications et wireframes écrits après le code** | la conformité écran-maquette est vraie par construction, pas une preuve de démarche ; le critère C17.2 reste partiel |
| **Aucun audit d'accessibilité outillé** | tâche T3 du plan E4 (Lighthouse ou équivalent, avec l'accord d'Era pour l'outil) |
| **Aucun test avec un lecteur d'écran réel** | `aria-live` est correct dans le code ; son rendu réel n'a pas été observé |
| **Aucun test avec un utilisateur** | les scénarios sont ceux de l'auteur |
| **Défaut R10 non corrigé** | carte #73, après le tag du 15/10 |

*Un document qui ne signale aucune faiblesse n'est pas crédible devant un jury.*

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Wireframe d'état** | croquis d'un écran dans une situation donnée, sans habillage graphique ; quatre par écran ici |
| **User story (US)** | un besoin décrit du point de vue de l'utilisateur, qui porte ses scénarios et ses critères d'acceptation |
| **Critère d'acceptation** | condition vérifiable qui décide si une US est tenue |
| **RGAA 4.1.2** | référentiel général d'amélioration de l'accessibilité, version 4.1.2 : le standard français, dont les critères sont numérotés (3.1, 5.4…) |
| **WCAG** | règles internationales d'accessibilité du web, dont le RGAA reprend l'esprit |
| **`sessionStorage`** | mémoire du navigateur propre à un onglet, effacée à sa fermeture |
| **`aria-live`, `role="status"`** | attributs qui font annoncer par un lecteur d'écran un texte qui change, sans interrompre la lecture |
| **Garde-fou de sortie** | contrôle qui relit le texte du modèle et retient toute recommandation d'achat ou de vente (`guardrails/sortie.py`) |
| **Lot 1, lot 3** | groupes d'indicateurs : le socle (cours, performances, moyennes, échangé, distance au plus haut) et le risque (volatilité, plus forte baisse, RSI) |
| **Cotation périmée** | la valeur n'a plus coté depuis longtemps, probablement radiée : ses chiffres décrivent le passé |
| **Tiret « — »** | « non calculable faute d'historique », jamais un zéro |
| **OWASP A03** | risque d'injection : un contenu venu de l'extérieur interprété comme du code |

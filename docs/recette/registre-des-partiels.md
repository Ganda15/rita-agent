# Registre des critères partiels, E2 à E5 (recette du 01/11/2026)

> **Pourquoi ce registre.** Les rapports E2 à E5 sont écrits, mais **32 lignes de leurs grilles** restent partielles
> ou sans preuve. Ce sont des lignes de grilles d'auto-évaluation, pas nécessairement 32 critères officiels distincts.
> La cible n'est pas « toutes les cases vertes » : c'est « chaque critère démontré ». Ce registre traite RITA comme un
> projet en phase de **recette** : pour chaque ligne, le texte exact du critère, l'écart réel, l'action minimale et la
> preuve qui permettrait de réévaluer la ligne. L'auto-évaluation ne remplace pas la décision du jury.

## Les règles de ce registre

1. **Réutiliser les preuves existantes** avant d'en produire de nouvelles.
2. **Aucune fonctionnalité créée seulement pour obtenir un vert.**
3. **Toute correction de code est proposée à part** : test qui échoue d'abord, correction, non-régression ; appliquée
   après validation d'Era.
4. **Un statut ne change qu'après vérification du résultat et validation d'Era.**
5. **Trois situations à ne pas confondre**, au lieu d'un « non rattrapable » trop catégorique :
   - **historique non modifiable** : ce qui a eu lieu, ou pas, à une date passée ; on ne le réécrit pas ;
   - **preuve actuelle à produire** : une nouvelle démarche menée aujourd'hui, datée honnêtement, qui démontre la
     compétence maintenant ;
   - **exigence sur toute la durée du projet** : une nouvelle itération la renforce, mais les lacunes passées restent
     écrites et expliquées.

Textes des critères : référentiel d'activités, de compétences et d'évaluation (Simplon, PDF de 25 pages) et règlement
spécifique RNCP 37827 ; pour E3, le libellé est celui de la grille du rapport.

## Les étapes, dans l'ordre

| Étape | Travail | Lignes concernées |
|---|---|---|
| 1 | Corriger ce registre pour viser exactement les exigences | toutes |
| 2 | Formaliser les parcours, scénarios et critères d'acceptation manquants (Question, Tableau de bord), objectifs d'accessibilité ; diagramme de flux à jour ; nouvelle itération de conception validée des écrans | E4 C14.2, C14.3, C14.4, C15.3, C17.2 |
| 3 | Corriger les défauts, tests avant et après : #73, #78, #79, #152 | E3 C10 (deux lignes) ; E4 C17.3, C17.4 |
| 4 | Recette des cinq écrans et des flux concernés : attendu, observé, test ou capture, écart | E4 C17.2, C17.3 |
| 5 | Sécurité, accessibilité, éco-conception, surveillance, selon les risques | E3 C9, C11 ; E4 C15.2, C17.5, C17.7, C17.8 ; E5 C20.5 |
| 6 | Partager les documents avec les destinataires concernés, preuves datées | E2 C6.4, C8.5 ; E4 C16.3, C16.4, C17.11, C18.6, C19.7 ; E5 C20.7 |
| 7 | Réévaluer chaque statut avec sa preuve précise | toutes |

Lignes d'E2 à renforcer en parallèle : C6.2, C6.6, C6.8, C7.4, C8.2 ; et E4 C16.1.

## Point au 02/11/2026 : ce qui est fait, ce qui reste, et qui le fait

Étapes 1 et 3 faites : registre corrigé ; #78, #73, #79 et #152 corrigés, tests rouges puis verts, sur `develop` et
dans la CI GitHub (job `base` compris), **pas en production** (`main` inchangée). **Aucun statut n'a changé** : chaque
ligne se réévalue avec sa preuve (étape 7), par Era.

| Qui | Lignes | Ce qu'il faut |
|---|---|---|
| **Era envoie** (Drive partagé, formateur prévenu ; preuve datée : quel fichier, avec qui, quand) | E2 C6.4, C8.5 ; E4 C16.3, C17.11, C18.6, C19.7 ; E5 C20.7 ; et la capture de C16.4 | synthèse de veille (`docs/veille/Veille-C6-synthese-S33-a-S36.pdf`), guide (`docs/EXPLOITATION.pdf`), rituels (`docs/PILOTAGE-AGILE.md`), documentation technique (`README.md`, `docs/ARCHITECTURE.md`), chaîne (`docs/CI-CD.md`) ; capture de la page d'accès du tableau Kanban |
| **Preuve à produire, sans fonctionnalité nouvelle** | E2 C6.6, C6.8, C7.4, C8.2 ; E3 C11 (deux lignes) ; E4 C14.2, C14.3, C14.4, C15.2, C15.3, C16.1, C17.3, C17.4, C17.11 (contenu du `README.md`) | recherches, notes, schémas, spécifications, recette des écrans ; chaque décision reste à Era |
| **Décision d'Era avant tout changement** (code ou production) | E3 C9 et E4 C17.8 (#75) ; E4 C17.5 (#76), C17.7 (#74) ; E5 C20.5 (vigie planifiée) ; E4 C17.2 (nouvelle itération de maquettes, validées par Era) | proposition écrite d'abord, test d'abord ensuite |

## E2 : 6 ⚠️ et 1 ❌

| Ligne | Texte exact du critère | Écart réel | Action minimale | Preuve de réussite | Situation |
|---|---|---|---|---|---|
| C6.2 ⚠️ → ✅ (02/11, Era) | « Les temps de veille sont planifiés régulièrement (à minima une récurrence d'une heure hebdomadaire). » | la **planification** existe : créneau du lundi, de 9 h à 10 h, écrit dans le protocole depuis le 14/08 (`docs/veille/README.md`, § 2, commit `5836a10`), sans rappel automatique ; l'**exécution** a été irrégulière (sept relevés et cinq notes de S33 à S44, rien depuis le 11/10), et le protocole le montre semaine par semaine | évaluer la ligne sur la planification, preuve à l'appui ; garder le bilan des semaines manquées ; reprendre la veille cette semaine (relevé et note S45) | protocole daté ; bilan des semaines ; relevé et note S45 | statut à réévaluer par Era ; semaines manquées : historique non modifiable ; **02/11, soir : ✅, décision d'Era** sur la planification, que le critère demande : créneau du lundi, de 9 h à 10 h (`docs/veille/README.md`, ligne 35, au tag `livrable-E2-v1`) ; à dire : « Une heure de veille est planifiée chaque lundi. La réalisation a été irrégulière ; le journal distingue les séances tenues, rattrapées et manquées. » (même fichier, tableau « État réel de la récurrence ») ; restent le relevé et la note S45 |
| C6.4 ⚠️ | « Les synthèses sont communiquées aux parties prenantes dans un format qui respecte les recommandations d'accessibilité » | format contrôlé le 01/11 ; envoi non fait | Era partage la synthèse sur Drive et prévient le formateur | preuve datée dans `evidence/C6/` : quel fichier, avec qui, quand | preuve actuelle à produire |
| C6.6 ⚠️ | « Auteur identifié ; informations sur l'auteur (compétences, notoriété, absence d'intérêts personnels) » | S41 : auteur unique, notoriété non établie | chercher l'auteur du préprint S41 (pages institutionnelles, publications) et écrire le résultat, même négatif | section datée dans la note S41 | **fait le 02/11** (`docs/veille/2026-S41-mesurer-le-gardefou.md`, « Complément du 02/11/2026 ») : auteur identifié, étudiant en M2 au Cybersecurity Lab du JAIST (page des membres du laboratoire), notoriété **non établie** (aucune autre publication trouvée), aucun intérêt déclaré, article rédigé avec Claude sous sa direction (déclaré) ; rapport E2 aligné en v0.8 (§ 2 et § 5, 02/11) ; statut à réévaluer par Era |
| C6.8 ⚠️ | « Sources respectant les normes d'accessibilité privilégiées ; information confirmable par d'autres sites de confiance » | S41 recoupée par un seul autre préprint | chercher une confirmation hors préprint (OWASP, Willison, ANSSI) ; citer la colonne accessibilité du protocole (`docs/veille/README.md`, § 3) | recoupement daté dans la note S41 | **fait le 02/11** (même section) : les faux positifs et leur coût confirmés par AgentDojo, relu par les pairs (NeurIPS 2024), et par Willison et OWASP (sources du protocole) ; le constat central (score lié aux données d'entraînement) **non confirmé** hors préprint, dit tel quel ; accessibilité renseignée (version HTML sur arXiv) ; ANSSI non consultée ; rapport E2 aligné en v0.8 ; statut à réévaluer par Era |
| C7.4 ⚠️ | « Le benchmark détaille pour chaque service étudié le niveau d'adéquation au besoin par ensemble fonctionnel » | le banc du 03/10 couvre le briefing, pas Question | **distinguer les usages évalués et non évalués** : pour Question, Azure seul a été observé en production le 16/10, sur **8 scénarios, dont 5 appels au modèle et 3 refus avant tout appel** (`evidence/sprint-3/evaluation-production-2026-10-16-relecture.md`) ; ce n'est pas un banc comparatif ; OpenRouter, écarté avant cet usage, n'y a pas été mesuré | paragraphe daté en § 3.3, qui ne présente pas le banc historique comme complet pour Question | **fait le 02/11, rapport E2 v0.8** : § 3.3, « L'adéquation au besoin, service par service et usage par usage », un tableau d'une ligne par service (Azure, OpenRouter, API directe d'Anthropic, Mistral) et une colonne par usage, qui distingue mesuré, retenu et non testé ; Question observée avec Azure seul (4 réponses fidèles, 1 abstention après appel, 3 refus sans appel) ; aucun nouveau banc ; § 3.7 et § 5 alignés ; reste ⚠️ ; statut à réévaluer par Era |
| C8.2 ⚠️ | « Le service est configuré correctement : il répond aux besoins fonctionnels et aux contraintes techniques » | à vérifier contre les besoins **réellement retenus** : fonctionnement, contraintes, erreurs, données transmises, conditions du fournisseur. Écarts connus : repli hors UE en production jusqu'au 31/10 (corrigé) ; conditions de Microsoft sur la zone UE non relues ; le briefing ne dit pas la date de la séance (formulation temporelle). Le référentiel n'impose pas deux fournisseurs : l'absence de Mistral n'est pas, à elle seule, un écart | tableau besoin par besoin, état constaté, écart ; lecture datée des conditions de Microsoft | tableau et note datés ; correction de la formulation temporelle proposée à part | preuve actuelle à produire |
| C8.5 ❌ | « La documentation est communiquée aux parties prenantes dans un format qui respecte les recommandations d'accessibilité » | format contrôlé le 31/10 ; envoi non fait | Era partage le guide sur Drive et prévient le formateur | preuve datée dans `evidence/C8/` | preuve actuelle à produire |

## E3 : 5 🟠 (rapport envoyé et tagué ; un changement demande une nouvelle version et un nouveau tag)

| Ligne | Critère (libellé de la grille) | Écart réel | Action minimale | Preuve de réussite | Situation |
|---|---|---|---|---|---|
| C9 🟠 | Recommandations OWASP intégrées quand nécessaire | API4 et API8 partiels : aucun en-tête de sécurité en production (24/10) | proposer les en-têtes de sécurité, test d'abord (#75) | test vert ; en-têtes lus en production | preuve actuelle à produire, après validation |
| C10 🟠 | Tous les points de terminaison concernés sont intégrés | parcours portefeuille de la passerelle MCP refusé sur le jeu importé (#152) | correction proposée, test d'abord, **sans laisser passer de positions personnelles** | test rouge puis vert, et test qui refuse toujours des positions personnelles | corrigé sur `develop` (`c0ce2b9`), tests verts dans la CI GitHub, vrai import compris (job `base`) ; pas en production ; E3 étant tagué, changer son statut demande une nouvelle version d'E3 ; à réévaluer par Era ; **02/11, soir** : sur `main`, testé en CI, non inclus dans l'image de production de l'API ; voir « Ajout du 02/11/2026, soir » |
| C10 🟠 | Adaptations d'interface conformes aux spécifications | clé mémorisée avant d'être vérifiée (#73), sur Briefing **et sur Question** (`frontend/question.js`, envoi du formulaire de clé) | correction proposée, test d'abord, sur tous les écrans concernés | tests rouges puis verts dans un vrai navigateur | corrigé sur `develop` (`fd12d1d`), tests verts dans la CI GitHub ; pas en production ; E3 étant tagué, changer son statut demande une nouvelle version d'E3 ; à réévaluer par Era ; **02/11, soir** : déployé (livraison 41488421204), comportement non vérifié en production ; voir « Ajout du 02/11/2026, soir » |
| C11 🟠 | Les outils sont adaptés au contexte et aux contraintes | le contrat de Langfuse permet un traitement hors de la région ; vérification « UE seule » incomplète | relire le contrat de Langfuse (DPA) ; décision d'Era écrite : garder ou remplacer | décision datée au registre RGPD, T3 | preuve actuelle à produire |
| C11 🟠 | Accessibilité prise en compte dans le choix de l'outil | examinée après le choix | **réexaminer le choix aujourd'hui** : besoins d'accessibilité des utilisateurs concernés (Era, exploitant), possibilités de Langfuse et d'outils comparables, décision écrite : garder, adapter ou remplacer | note datée de réexamen et décision | l'examen initial : historique non modifiable ; le réexamen : preuve actuelle |

## E4 : 18 ⚠️

| Ligne | Texte exact du critère | Écart réel | Action minimale | Preuve de réussite | Situation |
|---|---|---|---|---|---|
| C14.2 | « La modélisation des parcours utilisateurs respecte un formalisme : schéma fonctionnel, wireframes, etc. » | rien pour Question et Tableau de bord | schéma fonctionnel de chaque parcours, sur la version actuelle, daté | deux schémas dans `evidence/C14/`, marqués « relevé du jour, pas une maquette initiale » | **faits le 02/11** (`evidence/C14/parcours/`, montrés au § 7 de `preuve-specifications-ecrans-4-et-5.md`) : un schéma fonctionnel par écran, générés (`.drawio`, `.svg`, `.png`), tenus par `tests/test_parcours_c14.py` ; statut à réévaluer par Era ; **02/11, soir : ✅ dans le rapport E4 v1.1, décision d'Era** (limite gardée dans la matrice) |
| C14.3 | « Chaque spécification fonctionnelle couvre le contexte, les scénarios d'utilisation et les critères de validation. » | Question : les user stories US1 à US7 et leurs critères d'acceptation existent depuis le 15/10 (`docs/sprint-3/SPEC.md`, § 4) mais ne sont pas rattachées à E4 ; Tableau de bord : aucune story, mais les signaux, seuils et actions sont décrits (`docs/sprint-5/livrable/livrable-sprint-5.md`, § 4 et § 5.6) et testés (`tests/test_tableau_de_bord.py`) | rattacher la spécification de Question à E4 et compléter ses manques ; écrire la story de l'exploitant du Tableau de bord à partir du sprint 5 | spécifications reliées aux tests, datées | **écrites le 02/11** (`evidence/C14/preuve-specifications-ecrans-4-et-5.md`) : US1 et US2 de Question rattachées sans réécriture, avec dix scénarios de l'écran ; US-5 de l'exploitant écrite, avec dix scénarios ; chaque critère relié à un test existant (47 tests cités, tous vérifiés) ou marqué « lecture du code » ; rétrospectives ; statut à réévaluer par Era ; **02/11, soir : ✅ dans le rapport E4 v1.1, décision d'Era** (limite gardée dans la matrice) |
| C14.4 | « Les objectifs d'accessibilités sont directement intégrés aux critères d'acceptation des user stories. » | Question : la spécification du sprint 3 n'a aucun critère d'accessibilité (vérifié le 01/11) ; Tableau de bord : marqueurs d'accessibilité testés (`tests/test_tableau_de_bord.py`), sans story | critères RGAA numérotés dans les deux stories, chacun relié à un test | critères et tests cités | **écrits le 02/11** (même fichier) : Q12 à Q18 et T12 à T17, RGAA 3.1, 7.5, 8.3, 8.5, 9.1, 9.3, 11.1, 12.6 et WCAG 2.4.3, 1.4.10, 2.2.2 ; deux par lecture du code seulement (Q17, Q18) ; affichage étroit testé à 375 px, pas 320 ; **un critère non satisfait** : l'actualisation automatique du tableau de bord ne se suspend pas (WCAG 2.2.2) ; **corrigé le 02/11** avec le pied de page « Prototype local », tests d'abord (`evidence/C17/correctifs-2026-11-02/`) ; statut à réévaluer par Era ; **02/11, soir : ✅ dans le rapport E4 v1.1, décision d'Era** (limite gardée dans la matrice) |
| C15.2 | « Les éventuels services (PaaS, SaaS, etc) et prestataires ayant une démarche éco-responsable sont favorisés lors des choix techniques. » | hébergeur choisi pour la continuité | réexamen daté du choix d'hébergement selon les informations disponibles, et décision : garder ou changer | note datée et décision | le choix d'août : historique ; le réexamen : preuve actuelle |
| C15.3 | « Les flux de données impliqués dans l'application sont représentés par un diagramme de flux de données. » | diagramme du 18/08 sans Question ni vigie | nouvelle version datée, l'ancienne gardée | diagramme à jour dans `evidence/C15/` | **fait le 02/11** (`evidence/C15/preuve-flux-donnees-2026-11-02.md`, diagramme dans `evidence/C15/flux/`) : relevé sur le code, flux par flux avec leur emplacement, données personnelles marquées ; l'ancien du 18/08 gardé ; tenu par `tests/test_flux_c15.py` ; statut à réévaluer par Era ; **02/11, soir : ✅ dans le rapport E4 v1.1, décision d'Era** (limite gardée dans la matrice) |
| C16.1 | « …respectés dans sa mise en place et tout au long du projet. » | le tableau Kanban n'a plus bougé après le 14/10 ; **à examiner avant de conclure** : le suivi a pu continuer ailleurs (plans de travail, `ETAT.md` réécrit à chaque séance, pull requests, `CHANGELOG.md`) | relire ces preuves et écrire ce qu'elles montrent ; puis documenter une vraie nouvelle itération : priorités, revue, décisions | bilan daté du suivi du 14/10 au 01/11 ; itération documentée | exigence sur toute la durée : lacunes à expliquer |
| C16.3 | « Les objectifs et les modalités des rituels sont partagés à toutes les parties prenantes et rappeler si besoin. » | décrits, pas communiqués | Era envoie la section des rituels au formateur | preuve datée | preuve actuelle à produire |
| C16.4 | « Les éléments de pilotage sont rendus accessibles à toutes les parties du projet et ce tout au long du projet… » | accès au tableau non revérifié | capture de la page d'accès du tableau (Era) | capture datée | preuve actuelle ; « tout au long » : lacunes à expliquer |
| C17.2 | « Les interfaces sont intégrées et respectent les maquettes. » | les maquettes existantes ont été dessinées après les écrans ; deux écrans n'en ont pas. Le référentiel n'exige pas que la maquette précède la toute première version du code | **nouvelle itération de conception et de validation** : besoins, maquettes validées par Era, comparaison aux cinq écrans, corrections, recette ; datée honnêtement | maquettes validées et datées ; tableau de comparaison ; recette | preuve actuelle à produire |
| C17.3 | « Les comportements des composants d'interface… et la navigation respectent les spécifications fonctionnelles. » | #73 ; aucune recette des cinq écrans | recette des cinq écrans (normal, refus, erreur, clavier) ; correction de #73 | tableau de recette avec tests ; tests de #73 rouges puis verts | #73 fait (`fd12d1d`, CI verte) ; **recette faite le 02/11** (`evidence/C17/recette-2026-11-02/README.md`) : cinq écrans × quatre situations, 54 tests dans un navigateur (API simulée), dont 14 au clavier écrits pour la recette (`tests/test_recette_clavier.py`) ; écarts : le Tableau de bord ne posait pas le focus sur le champ de clé (E2), **corrigé le 02/11**, test d'abord (`evidence/C17/correctifs-2026-11-02/focus-cle-avant.txt` et `-apres.txt`) ; des erreurs vérifiées seulement par lecture du code (E3), **jouées dans un navigateur le 02/11** (`tests/test_recette_erreurs.py`, 8 tests, 7 mutations détectées, `evidence/C17/recette-2026-11-02/erreurs-navigateur.txt`) ; reste E1, décision d'Era ; statut à réévaluer par Era ; **02/11, soir : ✅ dans le rapport E4 v1.1, décision d'Era** (limite gardée dans la matrice) |
| C17.4 | « Les composants métier sont développés et fonctionnent comme prévu par les spécifications… » | #78 (RSI d'une série plate), #79 (pire baisse positive) | corrections, tests d'abord | tests rouges puis verts, valeurs affichées vérifiées | #78 et #79 faits (`fd12d1d`), tests rouges puis verts, #79 sur PostgreSQL dans le job `base` ; **valeurs affichées vérifiées le 02/11** sur la base locale (`evidence/C17/recette-2026-11-02/c17-4-valeurs-reelles.txt`) : 111 valeurs, aucune pire baisse au-dessus de 0, RSI calculé pour 108 ; #78 et #79 étaient latents (aucune valeur changée) ; écart d'affichage trouvé : « +0,00 % » pour GTO.PA (E1, capture), correction proposée, décision d'Era ; statut à réévaluer par Era ; **02/11, soir : ✅ dans le rapport E4 v1.1, décision d'Era** (limite gardée dans la matrice) |
| C17.5 | « La gestion des droits d'accès… est développée et respecte les spécifications fonctionnelles. » | l'API lit et écrit avec le rôle propriétaire (#76) ; elle écrit aussi le journal d'audit MCP (`mcp_calls`, `api/main.py`) ; `/docs` public | viser les **permissions minimales nécessaires** : lecture des données métier, écriture limitée au journal d'audit, toute autre modification refusée ; tests d'accès permis et refusés ; évaluer `/docs` dans le contexte du projet avant de le fermer | tests verts ; configuration de production relue | preuve actuelle à produire, après validation ; touche la production |
| C17.7 | « Les développements sont réalisés dans le respect des bonnes pratiques d'éco-conception… » | trois écrans mesurés ; compression et cache absents (#74) | mesurer les cinq écrans dans des états utiles ; proposer #74 | mesures datées ; correction testée | preuve actuelle à produire |
| C17.8 | « Les préconisations du top 10 d'OWASP sont implémentées dans l'application quand nécessaire. » | S1, S2, S6, S8, S9 ouverts (#75) | pour chacun : correction ou inapplicabilité justifiée, avec test | tableau S1 à S10 à jour | preuve actuelle à produire, après validation |
| C17.11 | « La documentation technique couvre l'installation, l'architecture, les dépendances, l'exécution des tests », communiquée dans un format accessible | `README.md` contrôlé le 02/11 (`evidence/C17/controle-accessibilite-readme-2026-11-02.md`) : format conforme ; contenu en retard (« AppLocker » au lieu de Smart App Control, chiffres du 10/10, tests PostgreSQL non décrits, aucun lien vers `docs/ARCHITECTURE.md`) ; **corrigés le 02/11** (même fichier, « Après la mise à jour ») ; communication non prouvée | Era partage la documentation | preuve d'envoi | contenu : fait ; communication : preuve actuelle à produire |
| C18.6 | « …couvre la procédure d'installation, de configuration et de test de la chaîne », format accessible | communication non prouvée | Era partage `docs/CI-CD.md` | preuve d'envoi | preuve actuelle à produire |
| C19.6 | « La documentation de la chaîne de livraison continue couvre la procédure d'installation, de configuration et de test de la chaîne. » | manquait : la vérification d'une publication par tag | **fait** : procédure ajoutée au § 6 de `docs/CI-CD.md` le 01/11, vérifiée sur l'exécution du 27/10 du tag `livrable-E3-v2` (40490834495) | ligne du § 6 ; exécution du 27/10 ; vérification documentaire du 01/11 | ✅ validé par Era |
| C19.7 | « La documentation est communiquée dans un format qui respecte les recommandations d'accessibilité… » | communication non prouvée | Era partage `docs/CI-CD.md` | preuve d'envoi | preuve actuelle à produire |

## E5 : 2 ⚠️

| Ligne | Texte exact du critère | Écart réel | Action minimale | Preuve de réussite | Situation |
|---|---|---|---|---|---|
| C20.5 | « Les alertes sont configurées et en état de marche, en fonction des seuils préalablement définis. » | alertes Langfuse automatiques ; vigie lancée à la main | si Era l'autorise : planifier la vigie, tester alerte et retour à la normale hors production | exécution planifiée constatée, événements reçus dans le bon environnement | changement à autoriser à part |
| C20.7 | « La documentation est communiquée dans un format qui respecte les recommandations d'accessibilité… » | format du guide contrôlé le 31/10 ; communication non prouvée | Era partage le guide | preuve d'envoi | preuve actuelle à produire |

## Corrections de code : tests d'abord, correction après validation

| Défaut | Ce qui est faux | Règle à respecter | Tests rouges prévus |
|---|---|---|---|
| #78 | `rsi_wilder` (`indicateurs/risque.py`) rend 100 sur une série plate, comme sur une hausse continue | convention retenue le 01/11 : sur une série entièrement plate, RSI **indéfini** (`None`), affiché « n.d. : aucune variation » ; raison : sans hausse ni baisse, il n'y a pas de force relative à mesurer, et 100 ferait croire à un fort élan haussier ; à écrire dans `docs/indicateurs/CONCEPTION.md` | série plate : `None` ; et, pour non-régression : série montante (100), descendante (0), mixte (entre 0 et 100), historique insuffisant (`None`) |
| #79 | la « pire baisse sur un an » (`db/indicateurs_risque.sql`) devient positive quand le cours ne fait que monter | 0 % quand il n'y a aucune baisse | cours 100, 110, 120 : attendu 0 % (aujourd'hui +9,09 %) ; baisse continue ; baisse puis reprise |
| #73 | Briefing **et Question** mémorisent la clé avant de savoir si elle fonctionne ; Portefeuille, Indicateurs et Tableau de bord appellent d'abord (vérifié sur `d3a4198` ; le rapport E3 parle de trois écrans) | mémoriser seulement après un appel réussi ; effacer après un refus d'authentification ; ne pas effacer sur une panne du service (une erreur 5xx ne dit pas que la clé est mauvaise) | clé refusée (401 ou 403) : rien en `sessionStorage` ; clé acceptée : mémorisée ; service indisponible : clé gardée, message de panne |
| #152 | le verrou de démonstration de la passerelle MCP refuse aussi le jeu d'exemple importé | accepter le jeu de démonstration **sans laisser passer de positions personnelles** | jeu importé : réponse attendue ; positions personnelles : toujours refusées |
| #76, #75, #74 | rôle propriétaire ; constats OWASP ; compression et cache | permissions minimales (le journal d'audit MCP reste écrit) ; chaque constat corrigé ou déclaré inapplicable ; compression testée | tests d'accès permis et refusés, d'en-têtes et de compression ; changements de production à décider à part |

## État des correctifs (01/11/2026, poussés les 01 et 02/11)

Preuves avant et après : `evidence/C17/correctifs-2026-11-01/` (README). Commités sur `develop` (`fd12d1d`, `c0ce2b9`) et
vérifiés dans la CI GitHub ; rien n'est en production (`main` inchangée). Suite complète après les quatre correctifs et la seconde revue de #152 (01/11, 22 h) : 1 871 réussis, **47 sautés**, 2 échecs attendus, 0 échec ;
parmi les sautés, les 24 tests PostgreSQL, exécutés à part sur la base jetable (46 réussis, 0 sauté).

### Ajout du 02/11/2026, soir : fusion dans `main`, déploiement et tags

PR #173 fusionnée par Era à 17 h 09 UTC (`174b0c1`), les sept contrôles exigés verts et deux revues sans remarque ;
livraison 41488421204 : déploiement réussi à 17 h 22 UTC (« operation reussie », code 0). Tags `livrable-E1-v5`,
`livrable-E2-v1` et `livrable-E3-v3` posés par Era sur `174b0c1`. Trois états à ne pas confondre :

| Correctif | Sur `main` | Déployé (dans l'image de production) | Vérifié en production |
|---|---|---|---|
| #73 (clé gardée seulement après un appel accepté) | oui | oui, `frontend/` | non : à jouer avec une clé fausse |
| #78 (RSI d'une série plate) | oui | oui, `indicateurs/` | non : écran Indicateurs à relire |
| #79 (pire baisse jamais positive) | oui | oui, `db/indicateurs_risque.sql`, lu par `indicateurs/risque.py` | non : écran Indicateurs à relire |
| Focus et bouton de pause du tableau de bord | oui | oui, `frontend/` ; la page servie contient le bouton et le nouveau pied de page (lecture à 17 h 23) | non : cliquer, voir l'actualisation s'arrêter, la relancer |
| #152 (verrou de la passerelle MCP) | oui | non : sur `main`, testé en CI, non inclus dans l'image de production de l'API (le `Dockerfile` ne copie pas `passerelle_mcp/`) ; la passerelle tourne sur le poste qui l'appelle | sans objet |

**Aucun statut n'a changé** : « déployé » n'est pas « vérifié en production ».

| Défaut | Avant | Après | État |
|---|---|---|---|
| #78 | 1 échec : 100 au lieu de `None` | 20 réussis | **corrigé** (`indicateurs/risque.py`) ; convention dans `docs/indicateurs/CONCEPTION.md`, § 7.3 ; l'écran affiche « — » et le prompt du briefing reçoit « non disponible », jamais 0 |
| #73 | 2 échecs (Briefing, Question) | 12 réussis, dont la panne au premier essai (503 ou réseau) ; 105 tests d'interface existants toujours verts | **corrigé** (`frontend/briefing.js`, `frontend/question.js`) ; vérifié aussi dans le navigateur contre l'API locale : 403, clé non gardée |
| #152 | 1 échec : le verrou accepte d'autres prix de revient ; puis 7 échecs avec les nouveaux tests, dont le jeu importé refusé | 44 réussis, 0 sauté, dont le vrai import du fichier d'exemple sur base jetable ; une mutation du jeu attendu est détectée ; seconde revue : contenu des champs vérifié (3 échecs, puis 47 réussis, 0 sauté), fichier fictif imposé au test | **corrigé** (`passerelle_mcp/serveur.py`, jeu attendu versionné `passerelle_mcp/jeu_demo_attendu.csv`, sans route d'alias) ; conception : `docs/recette/conception-152-verrou-demo.md` |
| #79 | 1 échec : +9,09 % au lieu de 0 % sur une hausse continue (base jetable, 01/11) | 5 réussis, dont une seule cotation (`NULL`) et une série plate (0 %) ; les 38 tests de base passent sur la même base | **corrigé** (`db/indicateurs_risque.sql`), validé localement sur PostgreSQL ; formule de `docs/indicateurs/CONCEPTION.md`, § 7.2, alignée ; job `base` vert sur GitHub (passages 41357550846, puis 41364533942 par le marqueur) |

## Base PostgreSQL de test isolée (faite le 01/11/2026)

Un conteneur jetable `postgres:18-alpine` (image déjà présente sur le poste, aucun téléchargement), qui n'écoutait que
sur `127.0.0.1:55432`, avec le schéma `db/schema.sql` et les rôles `db/roles.sql` du dépôt, et seulement des données
fictives créées puis annulées par les tests ; aucun accès à la base locale ni à la production ; fichier de secrets du
poste désactivé pour les tests (`PYTHON_DOTENV_DISABLED=1`). **Le secret de test** était tiré au hasard pour la séance.
Au premier lancement, il a d'abord été écrit dans un fichier du dossier de travail de l'assistant, puis ce fichier a été
supprimé avant les tests ; ensuite il a été lu dans l'environnement du conteneur, ce qui ne le rend pas inaccessible à
un administrateur Docker du poste. Les conteneurs ont été détruits à la fin.

Le second passage (#152, le soir) a utilisé le mode `trust` de PostgreSQL, comme le job de CI : aucun mot de passe,
donc aucun secret à écrire ni à lire ; conteneur détruit ensuite.

**CI : confirmée sur GitHub le 01/11, sélection par marqueur le 02/11.** Le correctif #79 est validé sur PostgreSQL,
en local puis dans le job `base` de GitHub : 43 réussis, 0 sauté sur `516fbf5` ; 46 réussis, 0 sauté sur `afa741d`, dont
24 qui demandent PostgreSQL (`evidence/C18/job-base-*`). `base` est exigé pour fusionner dans `main` depuis le 01/11 à
23 h 11 (sept checks). Le 02/11, la recherche du mot `dsn_de_test`, fragile (`tests/test_ci_base.py` y entrait parce
que le mot figure dans son texte), est remplacée par le marqueur `postgresql` : il choisit les mêmes 24 tests, nom par
nom, et un test qui demande la base sans le marqueur échoue (`evidence/C18/marqueur-postgresql-2026-11-02.md`). Vérifié
sur GitHub le 02/11 : 24 réussis, 0 sauté, sur `a32571f` (passage 41364533942), après un premier passage en
échec, cause trouvée et corrigée (`evidence/C18/marqueur-premier-passage-github-echec-2026-11-02.md`).

## Preuves des sprints à réutiliser

Trois natures de preuve, à ne jamais confondre : **production** (le service réel), **exercice local** (la copie du
poste) et **test simulé** (API interceptée ou données fabriquées).

| Critère | Preuve existante | Nature | Écart restant | Vérification nécessaire |
|---|---|---|---|---|
| E4 C14.3, C17.3 (Question) | `docs/sprint-3/SPEC.md`, § 4 (US1 à US7, critères d'acceptation) ; `evidence/sprint-3/evaluation-production-2026-10-16-relecture.md` (8 scénarios : 5 appels au modèle, 3 refus avant tout appel) | production | rattacher à E4 ; aucun critère d'accessibilité | correspondance avec `frontend/question.js` actuel ; recette au clavier : réponse, fiche de source, refus, erreur |
| E4 C14.3, C14.4 (Tableau de bord) | `docs/sprint-5/livrable/livrable-sprint-5.md`, § 4 (signaux, seuils, actions) et § 5.6 ; `tests/test_tableau_de_bord.py` (marqueurs d'accessibilité) ; captures sur données fabriquées | test simulé et exercice local | aucune story de l'exploitant ; critères RGAA non rattachés à une story | story écrite à partir du § 4 ; recette dans le navigateur |
| E3 C9 ; E4 C17.5, C17.8 (sécurité, accès, quota) | `docs/sprint-4/SPEC.md` ; `evidence/sprint-4/` : essais d'article et de briefing piégés (20/10), rejeux en production (20 et 21/10) | production et test simulé | chaque mesure garde son périmètre : elle ne prouve pas une sécurité totale | rattacher chaque constat OWASP S1 à S10 à une mesure ou à un écart |
| E5 C20, C21 (surveillance) | `evidence/sprint-5/production-2026-10-23.md` ; `monitorage/seuils.json` ; alerte #130 du 23/10 | production | vigie lancée à la main | annoncer « production » seulement pour ce qui y a tourné |
| E5 C20, C21 (exercices) | `evidence/sprint-5/copie-locale-2026-10-22.md` ; `evidence/sprint-5/test-doc-et-repetitions-2026-10-23.md` (panne simulée, retour arrière, dérive) | exercice local | à présenter comme exercice, jamais comme incident de production ; la répétition de la documentation a été faite par Era lui-même (ligne 9), pas par une autre personne | un test du guide par une autre personne serait une démarche distincte |
| #79, #152 (intégration) | `tests/garde_base.py` (garde de la base de test, sprint 4) | test simulé, puis base réelle jetable | aucun : le job `base` tourne sur GitHub à chaque poussée (24 réussis, 0 sauté, le 02/11) et il est exigé pour fusionner dans `main` | faite (`evidence/C18/`) |

## E1

Le budget n'est plus écrit « 0 € » ; il reste provisoire. À finir par Era : les montants vérifiables, en gardant séparés
les frais confirmés, les déclarations et les postes non chiffrés. Les autres limites d'E1 ne deviennent un chantier
qu'une fois rattachées à un critère précis.

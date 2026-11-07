# Mesure « avant / après » de la pagination du tableau Indicateurs (C17.7), 07/11/2026

**Pourquoi cette mesure.** Le 06/11, l'écran Indicateurs était le seul des cinq en D (EcoIndex 52 sans la carte #74,
53 avec), à cause de ses **1 625 éléments de page** : le tableau dessinait les 111 valeurs suivies d'un coup
([`../mesures-2026-11-06/README.md`](../mesures-2026-11-06/README.md)). Décision d'Era du 07/11 : réduire l'écran plutôt
que l'assumer. Le tableau montre désormais 20 valeurs à la fois (spécification `specs/001-refonte-interface/spec.md`,
R2, critère 11, écrit avant le code ; 7 tests écrits avant le code dans `tests/test_indicateurs_pages_ui.py`, vus
rouges dans la session de travail, mais leur sortie n'a pas été gardée dans un fichier, et la spécification, les tests
et le code sont arrivés dans le même commit `02900ea` : cet ordre ne se vérifie pas de l'extérieur. Les tests ajoutés
après la relecture, eux, ont leur sortie rouge conservée :
[`test-defilement-rouge-avant-correction.txt`](test-defilement-rouge-avant-correction.txt)). Cette note compare le même
jour, avec les mêmes outils, le code **avant** et **après** cette pagination.

## 1. Conditions

| Élément | Valeur |
|---|---|
| Date | 07/11/2026 ; après de 16 h 58 à 17 h 00 UTC, avant de 17 h 00 à 17 h 03 UTC |
| Code « avant » | `e6f227a` (branche `fin-c16-c17`, partie de `main` à `c73e3ba`) |
| Code « après » | `02900ea`, qui part de `e6f227a` et ne touche que l'interface (`frontend/`), la spécification et un fichier de tests |
| Écrans | les cinq : Portefeuille, Indicateurs, Briefing, Question, Tableau de bord |
| Outils | les mêmes que le 06/11 : Lighthouse **13.5.0** en mode flux, Node 24.18.0 ; [`outils/audit-rita.mjs`](outils/audit-rita.mjs) et [`outils/lancer-mesure.py`](outils/lancer-mesure.py) recopiés sans modification |
| Serveur | l'API en local sur le port 8001, sur la base locale, arrêtée à la fin de chaque mesure |
| Clé d'accès | jetable, tirée au hasard dans le processus de mesure, jamais affichée ni écrite dans un fichier |
| Traçage | Langfuse coupé (`LANGFUSE_TRACING_ENABLED=false`) : rien n'est écrit en production |
| EcoIndex | formule et tables officielles de `cnumr/ecoindex_python`, celles du 03/10 et du 06/11 ; [`outils/calcul-ecoindex-2026-11-07.py`](outils/calcul-ecoindex-2026-11-07.py), corrigé le 07/11 au soir (voir § 2) |

Pour mesurer « avant », le dépôt a été placé sur `e6f227a` le temps de la mesure (17 h 00 à 17 h 03 UTC), puis remis
sur `fin-c16-c17`. Effet de bord constaté et écrit : une exécution de `pytest` lancée pendant ce changement a vu le
test de pagination sur une interface sans pagination (45 lignes au lieu de 20). Relancés sur la branche rétablie, les
tests de l'écran donnent 42 réussis, 0 en échec. Suite complète sur `795e571` : 2 378 réussis, 82 ignorés, 2 en échec
attendu, 0 en échec ([`pytest-complet-795e571.txt`](pytest-complet-795e571.txt), écrit par la commande elle-même) ; les
deux échecs attendus sont ceux des garde-fous d'avant S9, la branche partant de `main` où S9 n'est pas encore fusionné.

## 2. Résultats

### Le calcul, corrigé après relecture

La relecture d'un autre agent (commit `1479ffe`) a trouvé trois défauts dans le calcul, repris du script du 06/11 :

1. **Classement des fichiers** : un préfixe classait `/briefing.html`, `/briefing.js`, `/question.html` et
   `/question.js` comme des routes de l'API ; leur poids au premier chargement était retiré. Une route se reconnaît
   désormais à son chemin exact (« /briefing », « /question ») ou à son répertoire (« /donnees/... »), et le script
   le vérifie à chaque exécution.
2. **Unité** : le poids était divisé par 1 024 (Kio). Le collecteur officiel divise par 1 000
   (`cnumr/EcoIndex_python`, `components/ecoindex/scraper/scrap.py`, « size=self.all_requests.total_size / 1000 ») :
   le poids est maintenant en ko décimaux.
3. **Périmètre** : le poids additionnait le premier chargement et les réponses de l'API, mais les requêtes venaient
   du seul écran chargé (9 pour Indicateurs). Poids et requêtes suivent désormais le même périmètre (10 pour
   Indicateurs : 8 fichiers de l'interface et 2 réponses de l'API).

Les relevés bruts (`avant/`, `apres/`) ne changent pas. Le premier calcul reste dans le dépôt, daté :
[`ecoindex-2026-11-07.json`](ecoindex-2026-11-07.json), écrit par la première version du script (commit `795e571`).
**Le calcul qui fait foi** : [`ecoindex-2026-11-07-corrige.json`](ecoindex-2026-11-07-corrige.json).

### EcoIndex (bureau, écran avec ses données), calcul corrigé

| Écran | Éléments du DOM, avant puis après | Requêtes | Poids avant | Poids après | EcoIndex avant | EcoIndex après |
|---|---:|---:|---:|---:|---|---|
| Portefeuille | 232 | 11 | 39,9 ko | 40,1 ko | A (86) | A (86) |
| **Indicateurs** | **1 625, puis 485** | 10 | 48,5 ko | 49,4 ko | **D (52)** | **B (76)** |
| Briefing | 179 | 9 | 38,5 ko | 38,6 ko | A (88) | A (88) |
| Question | 70 | 7 | 30,0 ko | 30,2 ko | A (92) | A (92) |
| Tableau de bord | 74 | 9 | 32,5 ko | 32,7 ko | A (92) | A (92) |

Pour l'écran Indicateurs : **−70 % d'éléments de page** (1 625 puis 485). Le modèle EcoIndex en déduit 1,96 puis
1,48 gCO2e par page vue, et 2,94 puis 2,22 cl d'eau : ce sont des **estimations de la formule**, pas des mesures
physiques d'émissions. Le poids monte de 0,9 ko : le code de la pagination. Les quatre autres écrans gardent leur
note ; leur poids monte de 0,1 à 0,2 ko, la feuille de style commune ayant reçu la règle des boutons de page.

**Le calcul du 06/11 avait le même défaut.** Recalculé avec ce script sur ses relevés bruts, sans les modifier
([`recalcul-mesure-2026-11-06-script-corrige.json`](recalcul-mesure-2026-11-06-script-corrige.json)) : toutes les notes
restent les mêmes, mais les poids publiés de Briefing (77,2 ; 27,0 Ko) et de Question (44,0 ; 20,1 Ko) étaient
sous-estimés ; corrigés : 102,6 ; 36,2 ko et 65,0 ; 28,0 ko. Le rapport E4 (§ 4.7, version visée par
`livrable-E4-v5`) cite ces poids : à corriger dans sa prochaine version. La note du 06/11 n'est pas réécrite.

### Lighthouse, écran Indicateurs

| Mode | Performance | Accessibilité | Bonnes pratiques | Référencement |
|---|---|---|---|---|
| Bureau, avant puis après | 100, puis 100 | 100, puis 100 | 100, puis 100 | 90, puis 90 |
| Mobile, avant puis après | 96, puis 97 | 100, puis 100 | 100, puis 100 | 90, puis 90 |

Le score automatique Lighthouse d'accessibilité reste à 100 avant et après dans cette mesure locale. La pagination
utilise des boutons natifs ; la position est annoncée par une zone `aria-live` au seul changement de page (depuis la
revue Claude Code de #226 : elle l'était aussi à chaque touche de la recherche). Cela ne constitue pas un audit complet
d'accessibilité ni une vérification de l'annonce avec un lecteur d'écran. Le rapport Lighthouse signale aussi
`label-content-name-mismatch` (108 éléments avant, 20 après, compte du relecteur), pondéré à zéro dans le score ; ce
constat est antérieur à la pagination et n'est pas traité ici. Rapports complets de l'écran après pagination :
[`apres/flux-indicateurs-bureau.html`](apres/flux-indicateurs-bureau.html) ; avant :
[`avant/flux-indicateurs-bureau.html`](avant/flux-indicateurs-bureau.html).

### Deux défauts de la pagination, corrigés après relecture (commit `488f39f`)

- Après avoir descendu le tableau, « Valeurs suivantes » gardait le défilement : la position annonçait « 21 à 40 »
  mais la zone visible commençait vers V31. La zone revient en haut à chaque changement de page ; le défilement
  horizontal est gardé.
- Trouvé par le test écrit pour ce défaut : revenu en première page, « Valeurs précédentes » se désactive et perdait le
  focus, qui tombait sur le corps de la page. Le focus passe désormais à l'autre bouton de page.

Sorties rouges avant ces corrections (deux exécutions, quatre échecs sur trois tests distincts) :
[`test-defilement-rouge-avant-correction.txt`](test-defilement-rouge-avant-correction.txt). Ces corrections ne sont pas
remesurées par Lighthouse : la mesure ci-dessus porte sur `02900ea`. Elles ne changent que le comportement au changement
de page (défilement, focus) et n'ajoutent aucun élément à la page. Suite complète sur `1ba3289` : 2 381 réussis,
82 ignorés, 2 en échec attendu, 0 en échec ([`pytest-complet-1ba3289.txt`](pytest-complet-1ba3289.txt), écrit par la
commande elle-même).

## 3. Ce que ça prouve, et ce que ça ne prouve pas

- **Prouvé** : à code d'API, base et outils identiques, la pagination fait passer l'écran Indicateurs de D (52) à
  B (76) selon la formule EcoIndex, avec le protocole décrit ci-dessus, sans changer la note des autres écrans ni le
  score automatique d'accessibilité.
- **Pas prouvé** :
  - une mesure **en local**, une exécution par état : pas en production (la pagination n'est pas déployée au 07/11) ;
  - l'EcoIndex mesure une page vue, pas un usage : un lecteur qui parcourt les six pages du tableau charge les mêmes
    données (elles sont reçues en une fois), mais dessine six fois 20 lignes ;
  - la liste de recherche (`<datalist>`) garde ses 111 options : elle compte dans les 485 éléments, et la spécification
    (R2, critère 7) demande qu'elle propose toutes les valeurs ;
  - la version qui réunit cette branche et S9 n'est pas mesurée ici ; la CI de la demande de fusion la teste.

## 📖 Glossaire

- **EcoIndex** : note de A à G, calculée sur trois mesures d'une page (nombre d'éléments, nombre de requêtes, poids
  transféré), qui estime son empreinte environnementale ; formule publique de l'association GreenIT.
- **DOM (éléments de page)** : l'arbre des éléments que le navigateur construit pour afficher la page ; plus il est
  grand, plus la page coûte à dessiner et à garder en mémoire.
- **Lighthouse** : outil d'audit de Google, intégré à Chrome, qui note une page en performance, accessibilité, bonnes
  pratiques et référencement.
- **Mode flux** : mode de Lighthouse qui enchaîne plusieurs étapes (premier chargement, écran avec ses données) dans
  une même session de navigateur.
- **`aria-live`** : attribut qui demande aux lecteurs d'écran d'annoncer un texte quand il change.

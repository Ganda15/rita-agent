# Mesure « avant / après » de la pagination du tableau Indicateurs (C17.7), 07/11/2026

**Pourquoi cette mesure.** Le 06/11, l'écran Indicateurs était le seul des cinq en D (EcoIndex 52 sans la carte #74,
53 avec), à cause de ses **1 625 éléments de page** : le tableau dessinait les 111 valeurs suivies d'un coup
([`../mesures-2026-11-06/README.md`](../mesures-2026-11-06/README.md)). Décision d'Era du 07/11 : réduire l'écran plutôt
que l'assumer. Le tableau montre désormais 20 valeurs à la fois (spécification `specs/001-refonte-interface/spec.md`,
R2, critère 11, écrit avant le code ; 7 tests écrits avant le code dans `tests/test_indicateurs_pages_ui.py`, dont 6
vus rouges). Cette note compare le même jour, avec les mêmes outils, le code **avant** et **après** cette pagination.

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
| EcoIndex | formule et tables officielles de `cnumr/ecoindex_python`, celles du 03/10 et du 06/11 ; [`outils/calcul-ecoindex-2026-11-07.py`](outils/calcul-ecoindex-2026-11-07.py) ne diffère du script du 06/11 que par ses libellés et le nom du fichier écrit |

Pour mesurer « avant », le dépôt a été placé sur `e6f227a` le temps de la mesure (17 h 00 à 17 h 03 UTC), puis remis
sur `fin-c16-c17`. Effet de bord constaté et écrit : une exécution de `pytest` lancée pendant ce changement a vu le
test de pagination sur une interface sans pagination (45 lignes au lieu de 20). Relancés sur la branche rétablie, les
tests de l'écran donnent 42 réussis, 0 en échec. Suite complète sur `795e571` : 2 378 réussis, 82 ignorés, 2 en échec
attendu, 0 en échec ([`pytest-complet-795e571.txt`](pytest-complet-795e571.txt), écrit par la commande elle-même) ; les
deux échecs attendus sont ceux des garde-fous d'avant S9, la branche partant de `main` où S9 n'est pas encore fusionné.

## 2. Résultats

### EcoIndex (bureau, écran avec ses données)

| Écran | Éléments du DOM | Requêtes | Poids avant | Poids après | EcoIndex avant | EcoIndex après |
|---|---:|---:|---:|---:|---|---|
| Portefeuille | 232 | 10 | 39,0 Ko | 39,1 Ko | A (86) | A (86) |
| **Indicateurs** | **1 625, puis 485** | 9 | 47,4 Ko | 48,2 Ko | **D (53)** | **B (76)** |
| Briefing | 179 | 8 | 29,3 Ko | 29,4 Ko | A (88) | A (88) |
| Question | 70 | 6 | 21,8 Ko | 22,0 Ko | A (92) | A (92) |
| Tableau de bord | 74 | 8 | 31,7 Ko | 31,9 Ko | A (92) | A (92) |

Pour l'écran Indicateurs : **−70 % d'éléments de page** (1 625 puis 485), gaz à effet de serre estimés par la formule
EcoIndex de 1,94 à **1,48 gCO2e** par page vue (−24 %), eau de 2,91 à 2,22 cl. Le poids monte de 0,8 Ko : le code de
la pagination (quelques dizaines de lignes de JavaScript et de style). Les quatre autres écrans ne changent pas ; leur
poids monte de 0,1 à 0,2 Ko, la feuille de style commune ayant reçu la règle des boutons de page.

Tous les chiffres : [`ecoindex-2026-11-07.json`](ecoindex-2026-11-07.json), calculé depuis
[`avant/resume-bureau.json`](avant/resume-bureau.json) et [`apres/resume-bureau.json`](apres/resume-bureau.json).

### Lighthouse, écran Indicateurs

| Mode | Performance | Accessibilité | Bonnes pratiques | Référencement |
|---|---|---|---|---|
| Bureau, avant puis après | 100, puis 100 | 100, puis 100 | 100, puis 100 | 90, puis 90 |
| Mobile, avant puis après | 96, puis 97 | 100, puis 100 | 100, puis 100 | 90, puis 90 |

La pagination ne coûte rien en accessibilité : les boutons sont de vrais boutons, désactivés quand ils sont sans effet,
et la position (« Valeurs 1 à 20 sur 111 ») est annoncée aux lecteurs d'écran (`aria-live`). Rapports complets de
l'écran après pagination : [`apres/flux-indicateurs-bureau.html`](apres/flux-indicateurs-bureau.html) ; avant :
[`avant/flux-indicateurs-bureau.html`](avant/flux-indicateurs-bureau.html).

## 3. Ce que ça prouve, et ce que ça ne prouve pas

- **Prouvé** : à code d'API, base et outils identiques, la pagination fait passer l'écran Indicateurs de D à B, sans
  dégrader les autres écrans ni l'accessibilité mesurée par Lighthouse.
- **Pas prouvé** :
  - une mesure **en local**, une exécution par état : pas en production (la pagination n'est pas déployée au 07/11) ;
  - l'EcoIndex mesure une page vue, pas un usage : un lecteur qui parcourt les six pages du tableau charge les mêmes
    données (elles sont reçues en une fois), mais dessine six fois 20 lignes ;
  - la liste de recherche (`<datalist>`) garde ses 111 options : elle compte dans les 485 éléments, et la spécification
    (R2, critère 7) demande qu'elle propose toutes les valeurs.

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

# Mesure « avant / après » de la carte #74 (compression et icône), 06/11/2026

Pourquoi cette mesure : le 03/10, la mesure d'éco-conception
([`../preuve-eco-conception-et-accessibilite-2026-10-03.md`](../preuve-eco-conception-et-accessibilite-2026-10-03.md))
a relevé que l'API ne compressait aucune réponse (F1) et que `favicon.ico` répondait 404 (F3). Elle promettait une
remesure avec les mêmes outils une fois ces défauts corrigés (§ 6 de cette note). La carte #74 corrige F1 et F3
(commit `dea68de`, branche `eco-74-compression`, 5 tests écrits avant le code). Cette note compare le même code, le
même jour, avec les mêmes outils, sans puis avec ce commit.

## 1. Conditions

| Élément | Valeur |
|---|---|
| Date | 06/11/2026 ; avec #74 de 19 h 02 à 19 h 05 UTC, sans #74 de 19 h 10 à 19 h 13 UTC |
| Code « sans #74 » | `develop` à `9f19b9c` |
| Code « avec #74 » | `dea68de`, qui part de `9f19b9c` et ne touche que `api/main.py` (et ajoute `tests/test_compression_favicon.py`) : l'interface est identique dans les deux mesures |
| Écrans | les cinq : Portefeuille, Indicateurs, Briefing, Question, Tableau de bord |
| Outils | Lighthouse 13.5.0 en mode flux, navigateur HeadlessChrome 156, Node 24.18.0 : les mêmes que le 04/11 ; le script du 03/10 étendu à cinq écrans ([`outils/audit-rita.mjs`](outils/audit-rita.mjs)) |
| Modes | bureau sans ralentissement ; mobile avec le ralentissement standard de Lighthouse |
| Serveur | l'API en local sur le port 8001, sur la base locale, arrêtée à la fin ([`outils/lancer-mesure.py`](outils/lancer-mesure.py)) |
| Clé d'accès | jetable, tirée au hasard dans le processus de mesure, jamais affichée ni écrite dans un fichier |
| Traçage | Langfuse coupé (`LANGFUSE_TRACING_ENABLED=false`) : rien n'est écrit en production |
| Briefing | aucun appel au modèle : la réponse est un vrai texte du 03/10 (`evidence/C7/resultats-2026-10-03.jsonl`), servi par interception dans le navigateur |
| EcoIndex | formule et tables officielles de `cnumr/ecoindex_python`, recopiées sans modification depuis le script du 03/10 ([`outils/calcul-ecoindex-2026-11-06.py`](outils/calcul-ecoindex-2026-11-06.py)) |

Ce qui change par rapport au 03/10 : la compression n'est plus simulée (gzip niveau 9 sur des fichiers archivés) :
elle est mesurée, ce sont les octets que le navigateur a réellement reçus. Le poids d'un écran est celui d'une
première visite : les fichiers de l'interface reçus à l'étape 1 (cache vide), plus les réponses de l'API reçues à
l'étape 2 (écran avec ses données).

## 2. Résultats

### Poids transféré et EcoIndex (bureau, écran avec ses données)

| Écran | Éléments du DOM | Requêtes | Poids sans #74 | Poids avec #74 | Écart | EcoIndex sans #74 | EcoIndex avec #74 |
|---|---:|---:|---:|---:|---:|---|---|
| Portefeuille | 232 | 10 | 87,3 Ko | 36,2 Ko | −58,5 % | A (86) | A (86) |
| Indicateurs | 1 625 | 9 | 147,5 Ko | 44,9 Ko | −69,6 % | D (52) | D (53) |
| Briefing | 179 | 8 | 77,2 Ko | 27,0 Ko | −65,0 % | A (88) | A (88) |
| Question | 69 | 6 | 44,0 Ko | 20,1 Ko | −54,3 % | A (92) | A (92) |
| Tableau de bord | 74 | 8 | 67,7 Ko | 29,5 Ko | −56,4 % | A (91) | A (92) |

Détail par fichier, pour l'écran Portefeuille (octets reçus à la première visite) :

| Fichier | Sans #74 | Avec #74 |
|---|---:|---|
| `index.html` | 8 074 | 3 366 |
| `style.css` | 26 460 | 8 266 |
| `app.js` | 17 053 | 6 415 |
| `graphiques.js` | 15 684 | 5 225 |
| `commun.js` | 8 347 | 3 283 |
| `theme.js` | 2 793 | 1 443 |
| deux logos PNG | 7 022 | 7 162 (une image PNG est déjà compressée : gzip ne s'y applique pas) |
| `/donnees/portefeuille` | 2 282 | 790 |

Tous les chiffres : [`ecoindex-2026-11-06.json`](ecoindex-2026-11-06.json), calculé depuis
[`sans-74/resume-bureau.json`](sans-74/resume-bureau.json) et [`avec-74/resume-bureau.json`](avec-74/resume-bureau.json).

### Lighthouse (étapes de navigation, 20 par mesure)

| | Sans #74 | Avec #74 |
|---|---|---|
| Accessibilité | 100 partout, bureau et mobile | 100 partout, bureau et mobile |
| Bonnes pratiques | 100 partout | 100 partout |
| SEO | 90 partout | 90 partout |
| Performance, bureau | 100, sauf Briefing avec ses données : 99 | 100 partout |
| Performance, mobile | de 95 à 100 | de 97 à 100 |

Une exécution par mesure : un écart de 1 à 4 points de performance en mobile est dans le bruit d'une seule exécution
et n'est pas attribué à #74.

## 3. Ce que la mesure prouve

- F1 est corrigé, et l'effet est mesuré : à la première visite, chaque écran pèse de 54 à 70 % de moins. Le plus
  gros gain est sur l'écran Indicateurs, dont les données (63,9 Ko) passent à 10,8 Ko.
- La compression ne s'applique qu'au-dessus de 1 000 octets : `/health` (388 octets) et les petites réponses restent
  telles quelles (test `tests/test_compression_favicon.py`).

## 4. Ce que la mesure ne prouve pas

- La note EcoIndex ne bouge presque pas (A reste A, Indicateurs passe de 52 à 53). La méthode compte le DOM trois
  fois, les requêtes deux fois et le poids une seule fois. Sur son échelle de vingt paliers, 145 Ko n'est que
  la fin du deuxième : de 20 à 150 Ko, la note varie à peine. La compression réduit les octets transférés, elle ne change presque pas la note.
- F3 n'apparaît pas dans Lighthouse. Les Bonnes pratiques valent déjà 100 sans #74. Depuis la refonte du 04/11
  (commit `6f04f85`), les cinq pages déclarent `<link rel="icon" href="logo-rita-clair.png">` : le navigateur ne
  demande plus `favicon.ico`. La route `/favicon.ico` de #74 ne sert donc qu'aux demandes directes de ce chemin.
  Combien il en arrive en production n'a pas été mesuré.
- La production n'est pas encore concernée. Ce code est mesuré en local. Le serveur de production continue de servir
  sans compression tant que la branche n'est pas fusionnée et déployée, et cette décision m'appartient.
- L'écran Indicateurs reste en D. Ses 1 625 éléments de DOM (les lignes du tableau des valeurs) font la note. C'est
  le seul levier qui la change (F4 de la note du 03/10), et ma décision D6 reste ouverte : n'afficher d'abord
  qu'une partie des lignes.
- L'EcoIndex est une modélisation : il classe une page sur trois grandeurs, il ne mesure ni l'énergie du serveur
  ni celle du modèle de langage.
- Ces chiffres ne se comparent pas directement à ceux du 03/10 et du 04/11 : la refonte a ajouté deux écrans et des
  fichiers d'interface (thème, graphiques, logos). La comparaison qui tient est celle de cette note, sur le même code.

## 5. Refaire la mesure

1. Installer Lighthouse 13.5.0 et puppeteer-core 25.16.0 par npm dans un dossier hors du dépôt (`--ignore-scripts`).
2. Depuis la racine du dépôt, sur le commit voulu :
   `C:\Python314\python.exe -X utf8 evidence\C17\mesures-2026-11-06\outils\lancer-mesure.py . <dossier de sortie> <dossier de Lighthouse>`
3. `C:\Python314\python.exe -X utf8 evidence\C17\mesures-2026-11-06\outils\calcul-ecoindex-2026-11-06.py <sortie sans> <sortie avec>`

## 6. Fichiers

| Fichier | Contenu |
|---|---|
| `sans-74/resume-bureau.json`, `sans-74/resume-mobile.json` | scores, requêtes (adresse, type, octets, statut) et éléments du DOM, étape par étape |
| `avec-74/resume-bureau.json`, `avec-74/resume-mobile.json` | la même chose avec #74 |
| `avec-74/flux-*-bureau.html` | les cinq rapports Lighthouse lisibles dans un navigateur, avec #74 |
| `ecoindex-2026-11-06.json` | le calcul EcoIndex des deux mesures |
| `outils/` | les trois scripts qui ont produit tout le reste |

Les rapports complets restants (mobile, sans #74, et les fichiers JSON bruts de Lighthouse, 35 fichiers, 43 Mo)
restent sur mon poste, hors du dépôt. Les résumés ci-dessus en gardent tous les chiffres utilisés.

## Glossaire

- **Compression gzip** : le serveur réduit le texte qu'il envoie (HTML, CSS, JavaScript, JSON) et le navigateur le
  remet en clair. Elle n'a lieu que si le navigateur dit l'accepter (en-tête `Accept-Encoding`).
- **EcoIndex** : note de A à G (et score sur 100) d'une page web, calculée depuis le nombre d'éléments du DOM, le
  nombre de requêtes et le poids transféré.
- **DOM** : l'arbre des éléments d'une page (titres, lignes, cellules, boutons) que le navigateur construit.
- **Favicon** : la petite icône d'un site dans l'onglet du navigateur.
- **Lighthouse** : outil libre de Google qui audite une page (performance, accessibilité, bonnes pratiques, SEO).
- **Mode flux** : Lighthouse mesure un parcours en plusieurs étapes (ouvrir l'écran, saisir la clé, charger les données),
  pas une seule page.
- **Première visite** : le navigateur n'a encore rien en cache et reçoit tous les fichiers.

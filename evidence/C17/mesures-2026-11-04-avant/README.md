# Mesure « avant » la refonte de l'interface, 04/11/2026

Tâche 0 du plan [`specs/001-refonte-interface/plan.md`](../../../specs/001-refonte-interface/plan.md). Les trois écrans
actuels (Portefeuille, Indicateurs, Briefing) sont mesurés avec les outils et les réglages du 03/10
([`../mesures-2026-10-03/`](../mesures-2026-10-03/)), pour être comparés à la mesure « après » de la tâche 11.
Les scores sont notés tels qu'ils sont sortis, sans les présupposer.

## 1. Conditions de la mesure

| Élément | Valeur |
|---|---|
| Date | 04/11/2026, de 08 h 57 à 08 h 59 UTC |
| Code mesuré | commit `f7229bc` de `develop` ; le dossier `frontend/` n'a pas changé depuis `eca894b` |
| Lighthouse | 13.5.0, avec puppeteer-core 25.16.0, installés par npm dans un dossier temporaire hors du dépôt (`--ignore-scripts`) |
| Navigateur | HeadlessChrome 156.0.0.0. Le 03/10, c'était la 154 : Chrome s'est mis à jour entre-temps. C'est la seule différence d'outil |
| Node | 24.18.0 |
| Modes | bureau 1 350 × 940 sans ralentissement ; mobile 412 × 823, ralentissement standard de Lighthouse |
| Serveur | l'API lancée en local sur le port 8001, sur la base locale ; arrêtée à la fin de la mesure |
| Clé d'accès | une clé jetable de 32 caractères, créée dans le processus de mesure : jamais affichée, jamais écrite dans un fichier |
| Traçage | Langfuse coupé (`LANGFUSE_TRACING_ENABLED=false`) : rien n'est écrit en production |
| Briefing | aucun appel au modèle : la réponse à `POST /briefing` est un vrai texte produit le 03/10 (banc C7, `evidence/C7/resultats-2026-10-03.jsonl`), servi par interception dans le navigateur |
| Outils | copies exactes de `../mesures-2026-10-03/outils/` (comparaison par `diff` : aucune différence) ; le script qui a tout enchaîné est [`mesurer-avant.sh`](mesurer-avant.sh) |

## 2. Résultats

### Lighthouse, étapes de navigation

| Écran | Mode | Performance | Accessibilité | Bonnes pratiques | SEO |
|---|---|---|---|---|---|
| Portefeuille | bureau | 100 | **100** | 96 | 90 |
| Portefeuille | mobile | 100 sans clé, 99 avec les données | **100** | 96 | 90 |
| Indicateurs | bureau | 100 | **100** | 100 | 90 |
| Indicateurs | mobile | 100 sans clé, 99 avec les données | **100** | 100 | 90 |
| Briefing | bureau | 100 | **100** | 100 | 90 |
| Briefing | mobile | 100 | **100** | 100 | 90 |

Sur les instantanés (page affichée avec ses données, et le texte du briefing arrivé) : accessibilité 100 partout,
bonnes pratiques 100, SEO 75. La performance y vaut « 0 », mais ce n'est pas une mesure : en mode instantané, la
catégorie ne contient qu'un audit (`unsized-images`), de poids 0, et il est réussi. Une moyenne sans aucun poids donne 0.
La performance se lit sur les navigations.

Aucun audit d'accessibilité n'est en échec, sur aucune des vingt étapes. Tous les scores sont identiques à ceux du
03/10, étape par étape (`resume-bureau.json`, `resume-mobile.json`).

### EcoIndex (formule et tables officielles, `outils/calcul-ecoindex.py`)

| Écran | État 1, sans clé | Données affichées | Données affichées, si l'API compressait (gzip) |
|---|---|---|---|
| Portefeuille | 93 (A) | 90 (A) : 140 éléments, 7 requêtes, 30,2 Ko | 90 (A), 11,2 Ko |
| Indicateurs | 92 (A) | **51 (D)** : 1 861 éléments, 5 requêtes, 88,4 Ko | 52 (D), 19,6 Ko |
| Briefing | 95 (A) | 90 (A) : 158 éléments, 4 requêtes, 41,3 Ko | 90 (A), 10,5 Ko |

Mêmes notes que le 03/10 ; chaque écran compte un ou deux éléments de plus (liens de navigation ajoutés depuis).

### Clavier (`clavier.json`)

- Sans clé, le focus arrive sur le champ de la clé (`#cle`), sur les trois écrans.
- Le focus est visible à chaque arrêt de tabulation.
- Après l'arrivée du briefing, le focus passe sur le résultat (`#resultat`).
- Arrêts de tabulation : 5 (Portefeuille), 6 (Indicateurs), 5 (Briefing). Le 03/10 : 3, 5 et 4. Les liens « Question »
  et « Tableau de bord », ajoutés aux sprints 3 et 5, expliquent la différence.

## 3. Écarts déjà présents, notés tels quels

1. La navigation n'est pas la même partout : Indicateurs et Briefing n'ont pas de lien « Question », Portefeuille
   l'a (ordre de tabulation, `clavier.json`). C'est l'exigence R5 de la spécification.
2. `favicon.ico` répond 404 : une erreur dans la console, d'où 96 en bonnes pratiques sur le Portefeuille
   (constat F3 du 03/10, toujours là).
3. Pas de `meta description` : SEO à 90 sur les navigations, 75 sur les instantanés. L'instantané ne compte que quatre
   audits SEO pondérés au lieu de sept, donc le même manque pèse plus (constat F7 du 03/10, noté et laissé tel quel).
4. L'API ne compresse pas ses réponses : le gzip retirerait de 62 à 91 % des octets, mais l'EcoIndex ne bouge
   presque pas, car le poids ne compte que pour un sixième de la formule.
5. Indicateurs avec ses données : **1 861 éléments** dans la page, la cause de la note D. C'est le tableau complet des
   valeurs.
6. Comme le 03/10, Lighthouse signale la feuille de style et le script qui bloquent le premier affichage, une durée de
   cache courte, et le CSS et le JavaScript non minifiés.

## 4. Pour que la mesure « après » soit comparable (tâche 11)

- Même installation : `npm install lighthouse@13.5.0 puppeteer-core@25.16.0 --ignore-scripts`, hors du dépôt.
- Noter la version de Chrome ; si elle n'est plus la 156, le dire.
- Mêmes données : comparer les empreintes des réponses de l'API ci-dessous. Si elles diffèrent (une collecte a tourné),
  le dire.
- Mêmes dimensions, mêmes états, même enchaînement (`mesurer-avant.sh`, à copier pour l'après).
- Les écrans refaits chargeront d'autres fichiers (`commun.js`, `graphiques.js`) et peut-être d'autres routes : la liste
  des entrées de `calcul-ecoindex.py` sera complétée dans une copie, et ce changement sera écrit. Les interactions
  nouvelles seront mesurées à part.

Empreintes SHA-256 des entrées (16 premiers caractères) :

| Fichier | Empreinte |
|---|---|
| `app.js` | `ad1e8a2bbc0585db` |
| `briefing.html` | `c99475e7db91c94d` |
| `briefing.js` | `724fc20ff4df684d` |
| `index.html` | `7c0c68f4525ecdd9` |
| `indicateurs.html` | `87a7917bdccada00` |
| `indicateurs.js` | `7daf05f66b5bcf06` |
| `style.css` | `401715c5ec1ec572` |
| `donnees_portefeuille.json` | `6c80a5953bb01375` |
| `donnees_indicateurs-portefeuille.json` | `7937f9aae18c5c95` |
| `donnees_fraicheur.json` | `3a6b8d0a68b1d2b2` |
| `donnees_indicateurs.json` | `de7494940ad18f36` |
| `donnees_indicateurs-risque.json` | `ea3f60ca10b0b75b` |
| `donnees_valeurs_limite_200.json` | `eeaa5c9acfa9a774` |

## 5. Fichiers

| Fichier | Contenu |
|---|---|
| `resume-bureau.json`, `resume-mobile.json` | par étape : scores, poids, requêtes, éléments du DOM, métriques, audits d'accessibilité en échec |
| `flux-portefeuille-bureau.html`, `flux-indicateurs-bureau.html`, `flux-briefing-bureau.html` | les rapports Lighthouse complets, à ouvrir dans un navigateur |
| `clavier.json` | le parcours au clavier de chaque écran |
| `ecoindex-resume.json` | l'EcoIndex par écran et par état, avec et sans compression |
| `entrees/` | les pages et les réponses de l'API telles que mesurées |
| `outils/` | les quatre scripts du 03/10, inchangés |
| `mesurer-avant.sh` | l'enchaînement complet de la mesure |

Comme le 03/10, les rapports mobiles et les fichiers bruts du mode flux (plusieurs Mo) sont restés hors du dépôt.

## Glossaire

- **Lighthouse** : outil d'audit de Google qui note une page sur quatre axes (performance, accessibilité, bonnes pratiques, référencement).
- **Mode flux** : façon d'utiliser Lighthouse qui enchaîne plusieurs états d'une même page (sans clé, avec les données, texte affiché).
- **Instantané (snapshot)** : audit de la page telle qu'elle est affichée, sans la recharger.
- **SEO** : référencement, la façon dont un moteur de recherche lit la page.
- **EcoIndex** : note de 0 à 100 (A à G) calculée à partir de trois mesures : le nombre d'éléments de la page, le nombre de requêtes et le poids transféré.
- **DOM** : l'arbre des éléments d'une page web, tel que le navigateur le construit.
- **gzip** : compression des fichiers envoyés par le serveur ; le navigateur les décompresse.
- **Empreinte SHA-256** : suite de caractères calculée à partir d'un fichier ; deux fichiers identiques ont la même empreinte.
- **Clé jetable** : clé d'accès créée pour une seule mesure, puis perdue.
- **Interception** : le navigateur répond lui-même à une requête précise, sans l'envoyer au serveur.
- **puppeteer-core** : bibliothèque qui pilote Chrome depuis un programme.
- **Focus** : l'élément de la page qui reçoit le clavier.

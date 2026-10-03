# Preuve C14 — spécifications fonctionnelles et modélisation des parcours

> **Compétence C14** : *« Analyser le besoin d'application d'un commanditaire intégrant un
> service d'intelligence artificielle, en rédigeant les spécifications fonctionnelles et en le
> modélisant, dans le respect des standards d'utilisabilité et d'accessibilité […] »*

📎 **Fichiers de cette preuve**

| Fichier | Rôle |
|---|---|
| [`WIREFRAMES-C14-ecran-portefeuille.png`](WIREFRAMES-C14-ecran-portefeuille.png) | les 4 états de l'écran — à regarder |
| [`WIREFRAMES-C14-ecran-portefeuille.svg`](WIREFRAMES-C14-ecran-portefeuille.svg) | la source, vectorielle |
| [`../../frontend/index.html`](../../frontend/index.html) | l'écran réellement implémenté |
| [`../../frontend/app.js`](../../frontend/app.js) | la couture avec l'API |
| [`../C4/MCD-MERISE-RITA.png`](../C4/MCD-MERISE-RITA.png) | la modélisation **des données** (critère 1) |

**Date** : 2026-08-18

> **Erratum du 03/10/2026.** En contrôlant les numéros de règle sur le texte officiel du RGAA 4.1.2, j'ai trouvé deux références inexactes dans ce
> document, laissées telles quelles ci-dessous : le critère **A5** (messages de statut annoncés) cite « RGAA 12.x », la règle est le critère **7.5** ;
> le critère **A9** (focus placé sur le champ) cite « RGAA 10.x », aucune règle du thème 10 ne porte sur ce geste, la référence la plus juste est WCAG 2.4.3.
> Le code décrit est correct, seule la référence au standard était inexacte. Détail et liste des numéros contrôlés :
> [`preuve-specifications-ecrans-2-et-3.md`](preuve-specifications-ecrans-2-et-3.md), §6. Les écrans 2 et 3 y sont spécifiés à leur tour.

---

## 1. Les 4 critères de C14, et où chacun est traité

| # | Critère officiel | Où |
|---|---|---|
| 1 | *« La modélisation des données respecte un formalisme : Merise, entités-relations »* | ✅ **MCD Merise**, déjà produit pour C4 — 6 entités, chaque cardinalité justifiée par un fait mesuré |
| 2 | *« La modélisation des parcours utilisateurs respecte un formalisme : schéma fonctionnel, wireframes »* | ✅ **les wireframes de ce dossier** — §2 |
| 3 | *« Chaque spécification fonctionnelle couvre le contexte, les scénarios d'utilisation et les critères de validation »* | ✅ **§3** |
| 4 | *« Les objectifs d'accessibilité sont intégrés aux critères d'acceptation des user stories »* et *« formulés en s'appuyant sur un standard : WCAG, RGAA »* | ✅ **§3**, colonne « critères d'acceptation » — chaque ligne RGAA porte son numéro de règle |

> ⚠️ Le critère 1 est **déjà satisfait par le MCD produit pour C4**. Il n'a pas été refait :
> le même modèle sert les deux compétences, et c'est volontaire — un second modèle des mêmes
> données serait un doublon à maintenir, donc une future contradiction.

---

## 2. Les wireframes — 4 états, pas 4 écrans

Le formalisme retenu est le **wireframe d'état** : un écran, quatre situations dans
lesquelles l'utilisateur peut le trouver. C'est ce que le code fait réellement — trois
sections HTML dont la visibilité est pilotée par `app.js` :

| État | Déclencheur dans le code | Ce que voit l'utilisateur |
|---|---|---|
| **1 — Aucune clé** | `demanderCle()` · `sessionStorage` vide | le formulaire de connexion |
| **2 — Chargement** | `afficherStatut("Chargement du portefeuille…")` | un message d'attente annoncé vocalement |
| **3 — Erreur** | `403` · `!reponse.ok` · échec réseau | le message correspondant à **la** panne rencontrée |
| **4 — Données** | `afficher(donnees)` | le tableau valorisé et son glossaire |

**Pourquoi représenter les états d'erreur plutôt que le seul écran « qui marche ».** Un
wireframe qui ne montre que le cas nominal décrit une démonstration, pas une application.
Les trois pannes traitées dans `app.js` sont **distinctes**, et leur message l'est aussi :

- **403** — la clé est refusée : on l'oublie (`sessionStorage.removeItem`) et on la redemande.
  *Une clé refusée n'est pas une panne.*
- **Autre code HTTP** — le serveur a répondu, mais en erreur : on affiche le code.
- **Aucune réponse** — le serveur n'a rien renvoyé du tout : il n'y a **aucun statut HTTP à
  lire**, d'où le `try/catch` autour du `fetch`. C'est un cas de nature différente, et il a
  son propre message.

---

## 3. Spécification fonctionnelle — US-1 « Consulter mon portefeuille valorisé »

### Contexte

Le portefeuille compte 7 lignes, potentiellement libellées en plusieurs devises. Les cours
sont en base (273 608 cotations), les taux de change également (5 devises). Sans écran, ces
données ne sont lisibles qu'en SQL.

> ⚠️ **Précision établie le 19/08/2026** : les 7 lignes utilisées en développement, en
> démonstration et en déploiement proviennent de **`data/positions-exemple.csv`**, un jeu
> **anonymisé de démonstration** — pas du portefeuille réel de l'auteur. La variable
> `POSITIONS_CSV` n'a jamais été définie, donc `sources/positions.py` a toujours pris cet
> exemple par défaut. *Un jeu de démonstration assumé est légitime ; le présenter comme des
> données réelles ne le serait pas.*

**Le besoin** : voir, en une page, ce que vaut le portefeuille aujourd'hui, converti en
euros, avec l'écart par rapport au prix d'achat.

**Ce que l'application ne fait pas, et ne fera pas** : recommander d'acheter ou de vendre.
L'avertissement est affiché en haut de l'écran, en permanence — contrainte AMF, elle est
inscrite dans le code (`guardrails/sortie.py`) et pas seulement dans l'interface.

### Scénarios d'utilisation

| # | Scénario | Parcours |
|---|---|---|
| **S1** | Première visite | ouvrir l'écran → saisir la clé d'API → voir le portefeuille |
| **S2** | Visite suivante, même onglet | ouvrir l'écran → **le portefeuille s'affiche directement** (clé en `sessionStorage`) |
| **S3** | Clé invalide ou révoquée | saisir la clé → 403 → message → nouvelle saisie |
| **S4** | API arrêtée | ouvrir l'écran → message « le serveur ne répond pas » |
| **S5** | Valeur de qualité douteuse | la ligne s'affiche, **suivie de la mention « (donnée douteuse) »** — on montre le chiffre, on signale le doute |

### Critères de validation et d'acceptation

Chaque ligne est **vérifiable** — par un test automatisé, ou par une manipulation décrite.

| # | Critère d'acceptation | Standard | Vérifié par |
|---|---|---|---|
| A1 | Le total est la somme des valorisations converties en euros | — | `tests/test_frontend.py` |
| A2 | Une clé n'est mémorisée **qu'après** avoir fonctionné | — | `app.js` : `setItem` après le `if (!reponse.ok)` |
| A3 | La clé n'apparaît **jamais** en clair : `type="password"`, `autocomplete="off"` | RGAA | `index.html` |
| A4 | La clé disparaît à la fermeture de l'onglet (`sessionStorage`, pas `localStorage`) | — | `app.js` |
| A5 | Chaque changement de statut est **annoncé** par un lecteur d'écran | **RGAA 12.x** — `role="status"` `aria-live="polite"` | `index.html` |
| A6 | Chaque cellule du tableau est rattachée à son en-tête | **RGAA 5.7** — `scope="col"` / `scope="row"` | `index.html` |
| A7 | Le tableau porte un titre lisible programmatiquement | **RGAA 5.4** — `<caption>` | `index.html` |
| A8 | La performance est lisible **sans percevoir la couleur** | **RGAA 3.1** — le signe `+` / `−` est toujours affiché | `app.js` : `signDisplay: "always"` |
| A9 | Le focus clavier arrive sur le champ de saisie | **RGAA 10.x** | `app.js` : `.focus()` |
| A10 | Aucun contenu de l'API n'est interprété comme du HTML | **OWASP A03** | `app.js` : `textContent`, jamais `innerHTML` |
| A11 | Les termes métier sont définis dans l'écran | utilisabilité | `<details>` — PRU, Investi, Valorisation, Performance, Donnée douteuse |

> **Les objectifs d'accessibilité ne sont pas une annexe : ce sont des critères
> d'acceptation.** A3, A5, A6, A7, A8 et A9 conditionnent l'acceptation de l'US au même titre
> que A1. Une US-1 qui afficherait les bons chiffres sans `scope` serait **refusée**.

---

## 4. Ce qui n'est pas encore fait — dit franchement

| Manque | Conséquence |
|---|---|
| **Une seule US est spécifiée** (US-1). L'écran 2 « indicateurs » n'a ni wireframe ni critères d'acceptation | C14 ne sera complet qu'avec les US de l'écran 2 *(levé le 03/10/2026 : US-2 et US-3 dans `preuve-specifications-ecrans-2-et-3.md`, écrites après le code)* |
| **Aucun audit RGAA outillé** n'a été passé | les 11 critères ci-dessus sont vérifiés à la lecture et par test, pas par un outil de conformité |
| **Aucun test avec un lecteur d'écran réel** (NVDA, VoiceOver) | `aria-live` est correct dans le code ; son comportement réel n'a pas été observé |

*Un document qui ne signale aucune faiblesse n'est pas crédible devant un jury.*

---

## 5. 📖 Glossaire

| Terme | En clair | Pourquoi ça compte ici |
|---|---|---|
| **Wireframe** | Croquis d'un écran, sans couleurs ni graphisme définitif | Le formalisme demandé par le critère 2 |
| **User story (US)** | Un besoin décrit du point de vue de l'utilisateur | Porte les critères d'acceptation |
| **Critère d'acceptation** | Condition vérifiable pour déclarer une US terminée | Ce que le critère 4 exige d'intégrer |
| **RGAA** | *Référentiel Général d'Amélioration de l'Accessibilité* — le standard français | Le standard retenu (le critère laisse le choix WCAG/RGAA) |
| **WCAG** | L'équivalent international | Non retenu : le RGAA en est la déclinaison française |
| **Lecteur d'écran** | Logiciel qui lit une page à voix haute pour une personne aveugle | Destinataire de `aria-live` et de `scope` |
| **`aria-live`** | Attribut annonçant qu'une zone change, sans couper la lecture | A5 |
| **`scope`** | Attribut liant une cellule à son en-tête de ligne ou de colonne | A6 |
| **`<caption>`** | Le titre d'un tableau, lu par un lecteur d'écran | A7 |
| **`sessionStorage`** | Mémoire du navigateur, **effacée à la fermeture de l'onglet** | A4 |
| **`localStorage`** | La même chose, mais **persistante** — écartée pour une clé d'API | A4 |
| **PRU** | *Prix de Revient Unitaire* — prix moyen d'achat d'un titre | Colonne du tableau |
| **AMF** | *Autorité des marchés financiers* | L'interdit affiché en tête d'écran |

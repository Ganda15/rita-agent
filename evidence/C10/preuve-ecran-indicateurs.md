# Preuve C10 / C17 — écran 2 : les indicateurs de marché

> **C10** : *« Intégrer l'API d'un modèle ou d'un service d'intelligence artificielle […] »*
> — volet **intégration** : authentification, points de terminaison, gestion des erreurs.
> **C17** : *« Développer les composants techniques et les interfaces […] »*

📎 **Fichiers**

| Fichier | Rôle |
|---|---|
| [`../../frontend/indicateurs.html`](../../frontend/indicateurs.html) | la page |
| [`../../frontend/indicateurs.js`](../../frontend/indicateurs.js) | **la couture** — c'est elle qui relève de C10 |
| [`../../api/donnees.py`](../../api/donnees.py) | le point de terminaison `/donnees/indicateurs` |
| [`../C14/preuve-indicateurs-lot1.md`](../C14/preuve-indicateurs-lot1.md) | le calcul qui l'alimente |

**Tests** : [`../../tests/test_frontend.py`](../../tests/test_frontend.py) (32) ·
[`../../tests/test_api_donnees.py`](../../tests/test_api_donnees.py) (34)
**Date** : 2026-08-18

---

## 1. Le point de terminaison

```
GET /donnees/indicateurs
    ?ticker=MC.PA&ticker=OR.PA     restreindre (répétable)
    &masquer_perimees=true         écarter les cotations trop anciennes
```

### Sortie réelle

```
sans clé                         -> 403
avec clé                         -> 200  nb=111  perimees=3  seuil=40
?ticker=MC.PA&ticker=OR.PA       -> 200  ['MC.PA', 'OR.PA']
?masquer_perimees=true           -> 200  nb=108
```

```json
{
  "ticker": "AC.PA",
  "nom_officiel": "ACCOR",
  "statut_qualite": "OK",
  "date_cours": "2026-08-18",
  "cours": 46.32,
  "fraicheur_jours": 0,
  "perf_1j_pct": 0.54,
  "perf_1a_pct": 5.53,
  "ma20": 46.517,
  "ma50": 47.76,
  "adtv20": 30049717.0,
  "distance_plus_haut_1a_pct": -10.92,
  "cotation_perimee": false
}
```

### Le choix qui compte : les valeurs périmées sortent **par défaut**

`masquer_perimees` vaut `false` par défaut. Trois valeurs de l'univers sont radiées depuis
2018-2019 et portent pourtant `statut_qualite = "OK"`.

> 🔑 **`statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur.** Les deux
> champs sont donc exposés séparément, et l'appelant décide. *On montre le chiffre, on
> signale le doute — jamais l'inverse.*

---

## 2. L'écran

### Les 4 états, identiques à ceux de l'écran 1

| État | Déclencheur | Affichage |
|---|---|---|
| 1 — aucune clé | `sessionStorage` vide | formulaire de connexion |
| 2 — chargement | `afficherStatut(…)` | message annoncé vocalement |
| 3 — erreur | `403` · autre code · échec réseau | le message propre à **la** panne |
| 4 — données | `afficher()` | le tableau des 12 colonnes |

**La clé est partagée avec l'écran 1** (même entrée `sessionStorage`) : passer d'un écran à
l'autre ne redemande pas de s'authentifier. Elle n'est mémorisée qu'**après** avoir
fonctionné, et disparaît à la fermeture de l'onglet.

### Vérification en navigateur — faite, pas supposée

Le rendu a été contrôlé sur le serveur réel, sans saisir de clé : un jeu de données a été
injecté puis la fonction d'affichage appelée directement.

```
resultat_visible : true
nb_valeurs       : "3 valeurs"
mention          : " · dont 1 cotation périmée"
légende          : "Indicateurs de marché — cours du 2026-08-18"
lignes           : 3
```

```
ligne ACCOR   : AC.PA | ACCOR | 46,32 | +0,54 % | -0,26 % | … | 30 M | -10,92 %
MA50 absente  : "—"                       (et non "0,00")
ligne Zodiac  : "ZODIAC AEROSPACE (cotation périmée — dernière séance le 2018-03-22)"
première cellule : <th scope="row">
```

**Filtre testé par un vrai clic** :

```
case cochée : true → "2 valeurs" · " · 1 cotation périmée masquée" · [AC.PA, MC.PA]
```

**Console du navigateur : aucune erreur.**

---

## 3. 💎 Quatre choix de conception à défendre

### 1. Un tiret n'est pas un zéro

```javascript
return n === null ? "—" : nombre.format(n);
```

`null` signifie **« pas calculable »** — l'historique ne remonte pas assez loin.
`0` signifierait **« aucune variation »**. Afficher `0,00 %` à la place d'un tiret ferait
lire une performance nulle là où il n'y en a simplement pas.

### 2. La péremption est portée par le **texte**, pas par la couleur

```javascript
i.cotation_perimee
  ? `${i.nom_officiel} (cotation périmée — dernière séance le ${i.date_cours})`
  : i.nom_officiel
```

La classe CSS `perimee` n'est qu'un **renfort visuel**. À elle seule, elle ne dirait rien à
un lecteur d'écran ni à une personne qui ne perçoit pas les couleurs (RGAA 3.1).
Un test verrouille la présence de la mention textuelle.

### 3. Le filtre ne rappelle pas l'API

La case à cocher agit sur les données **déjà chargées**. Redemander au serveur la même chose,
filtrée, coûterait un aller-retour réseau pour un travail que le navigateur fait
instantanément. `aria-controls` relie la case au tableau qu'elle modifie.

### 4. La zone qui défile est atteignable au clavier

Douze colonnes ne tiennent pas sur un écran étroit : **le tableau défile, pas la page**
(vérifié — `document.body.scrollWidth > window.innerWidth` est faux).

```html
<div class="tableau-large" tabindex="0" role="region"
     aria-label="Tableau des indicateurs, défilement horizontal">
```

C'est le seul cas où poser `tabindex` sur un élément non interactif est recommandé
(WCAG 2.1.1) : sans lui, le défilement serait **réservé à la souris**.

---

## 4. Le défaut trouvé pendant la vérification — et il est instructif

Le commentaire du CSS annonçait que `tabindex` et `role="region"` rendaient la zone
défilable atteignable au clavier. **Ils n'étaient nulle part dans le HTML.**

Sans eux, une personne naviguant au clavier n'aurait **jamais** pu voir les colonnes de
droite — soit la moitié du tableau.

> 🔑 **Même famille de défaut que le garde-fou de sortie du 17/08** : un contrôle
> **documenté mais absent** est pire qu'un contrôle absent. Tant qu'il est écrit, personne
> ne le cherche.

Corrigé, puis vérifié dans le navigateur, puis **verrouillé par un test**
(`test_la_zone_qui_defile_est_atteignable_au_clavier`).

---

## 5. Contrôles d'accessibilité — mesurés dans le navigateur

| Contrôle | Résultat |
|---|---|
| `<caption>` présent | ✅ |
| `th[scope="col"]` | **12** |
| `th[scope="row"]` | ✅ posés à l'exécution |
| Cellules fusionnées | **0** |
| `aria-controls` sur le filtre | ✅ `tableau-indicateurs` |
| `aria-live="polite"` sur le statut | ✅ |
| `aria-current="page"` dans la navigation | ✅ |
| Zone de défilement focalisable | ✅ `tabindex="0"` + `role="region"` + nom |
| Focus visible sur la zone | ✅ `:focus-visible` |
| La page ne défile pas horizontalement | ✅ |
| Signe toujours affiché sur les pourcentages | ✅ `signDisplay: "always"` |

---

## 6. Tests

```
tests/test_frontend.py      → 32 passed
tests/test_api_donnees.py   → 34 passed
suite complète              → 241 passed, 1 failed
```

⚠️ **L'échec unique est volontaire** : `test_seuils_minimaux_du_gardefou`, laissé rouge
depuis la veille S34 (blocage mesuré à 70 % contre un seuil de 85 %). Le baisser effacerait
ce que la veille a mis au jour. Arbitrage prévu en S35.

**Un test à signaler** : `test_les_en_tetes_de_ligne_sont_poses_par_le_rendu`. La première
version cherchait `scope="row"` dans le HTML — impossible, puisque les lignes sont créées à
l'exécution. Le test échouait sur un code correct.
*Un test doit chercher là où la chose est réellement écrite.* Même leçon que le
`innerHTML` trouvé dans un commentaire le 16/08.

---

## 7. Ce qui n'est pas fait

| Manque | Conséquence |
|---|---|
| **Aucun tri ni recherche** dans le tableau de 111 lignes | utilisable, mais fastidieux |
| **Aucun audit RGAA outillé** | les 11 contrôles ci-dessus sont mesurés dans le navigateur, pas par un outil de conformité |
| **Aucun test avec un vrai lecteur d'écran** (NVDA, VoiceOver) | les attributs sont corrects ; leur rendu vocal n'a pas été écouté |
| **Lots 2 et 3** des indicateurs | 5 indicateurs restants sur 13 |

---

## 8. 📖 Glossaire

| Terme | En clair |
|---|---|
| **Point de terminaison** (*endpoint*) | Une URL de l'API — ici `/donnees/indicateurs` |
| **`sessionStorage`** | Mémoire du navigateur effacée à la fermeture de l'onglet |
| **`textContent`** | Insère du texte **sans** l'interpréter comme du HTML |
| **`innerHTML`** | L'inverse — exécuterait un nom d'instrument piégé (OWASP A03) |
| **`scope="row"` / `"col"`** | Relie une cellule à son en-tête, pour un lecteur d'écran |
| **`aria-live="polite"`** | Annonce un changement de texte sans couper la lecture |
| **`aria-controls`** | Déclare qu'un contrôle pilote un autre élément |
| **`aria-current="page"`** | Signale la page où l'on se trouve déjà |
| **`role="region"`** | Zone nommée, atteignable dans la navigation d'un lecteur d'écran |
| **`tabindex="0"`** | Rend un élément atteignable au clavier dans l'ordre naturel |
| **`:focus-visible`** | Style appliqué au focus **clavier** seulement |
| **RGAA** | Référentiel français d'accessibilité |
| **MA20 / MA50** | Moyenne des clôtures sur 20 ou 50 séances |
| **ADTV** | Valeur moyenne échangée par séance |
| **Radiée** (*delisted*) | Valeur qui ne cote plus |

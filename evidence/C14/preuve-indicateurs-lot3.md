# Preuve — indicateurs de marché, lot 3 « risque »

> Alimente l'**écran 2** de l'application (livrable **E4**), aux côtés du lot 1.
> Spécification : [`../../docs/indicateurs/CONCEPTION.md`](../../docs/indicateurs/CONCEPTION.md) §7

**Fichiers** : [`../../db/indicateurs_risque.sql`](../../db/indicateurs_risque.sql) ·
[`../../indicateurs/risque.py`](../../indicateurs/risque.py)
**Tests** : [`../../tests/test_indicateurs_risque.py`](../../tests/test_indicateurs_risque.py) (19)
**Date** : 2026-08-19

---

## Le principe, comme pour les deux lots précédents

**RITA calcule des indicateurs, jamais des stratégies.** Un RSI de 71 est un fait. « RSI > 70
→ vendre » — l'exemple donné par la spécification elle-même — serait un conseil, que
l'interdit AMF proscrit. Aucun seuil, aucune couleur d'alerte, aucun mot « acheter »/« vendre ».

---

## `quant_metrics.py` relu une seconde fois — toujours non réutilisé

Après le lot 1, où le module externe (`Ganda15/daily-stock-analysis-era`) avait été écarté
pour un décalage en nombre de lignes, il a été relu pour ce lot — et écarté de nouveau, pour
des raisons différentes :

| Fonction | `quant_metrics.py` | Ce que la spécification exige |
|---|---|---|
| `_rsi` | moyenne mobile **simple** (`.rolling(period).mean()`) | lissage **récursif de Wilder** |
| `_annualized_vol` | rendement **simple** (`pct_change()`) | rendement **logarithmique** |
| `_max_drawdown_pct` | maximum **incluant le jour courant** (`cummax()`) | maximum arrêté **à la veille** |

> *La variante « moyenne simple » circule partout et donne des valeurs différentes. Écrire
> laquelle est implémentée, sinon le chiffre n'est pas reproductible.* — spécification §7.3

Trois fonctions, trois écarts différents avec ce qui est documenté ici. Aucune n'a été
portée.

---

## I4/I5 — volatilité et drawdown, en SQL

### Le rendement journalier, écrit une fois

```sql
LN(cloture_t / cloture_t−1)
```

Rendement **logarithmique**, pas simple (`(cours-précédent)/précédent`) : c'est le choix que
la spécification impose (§7, chapeau), parce qu'il s'additionne dans le temps.

### 🐛 Le bug qui a cassé la première version — et ce qu'il apprend

**Premier essai : les 111 valeurs sortaient avec une volatilité `NULL`.**

**Cause** : les fonctions fenêtre (`COUNT`, `STDDEV_SAMP`, `MIN`) étaient placées dans le
`SELECT` final, **après** la jointure sur `derniere_seance`. Cette jointure réduit chaque
ticker à **une seule ligne** avant que la fenêtre ne soit évaluée — une fenêtre de 20 séances
qui n'a plus qu'une ligne à regarder ne peut rien mesurer.

> 🔑 **Calculer les fonctions fenêtre sur l'historique complet, dans une CTE ; ne filtrer sur
> la dernière séance qu'ensuite**, en lisant cette CTE déjà calculée.

Le même bug avait produit un symptôme plus discret : **2 drawdowns positifs** (impossible en
théorie) sur la première mesure — la conséquence directe de fenêtres à une seule ligne.

**Après correction** : 0 `NULL`, 0 drawdown positif sur les 111 valeurs.

### Vérifié sur l'exemple exact de la spécification

```
série 100 → 150 → 90 → 120 :

t | cloture | plus_haut (jusqu'à t−1) | baisse
1 | 100     | —                       | —
2 | 150     | 100                     | +50,00 %
3 | 90       | 150                     | −40,00 %
4 | 120     | 150                     | −20,00 %

drawdown_max = MIN(...) = −40,00 %  ← attendu par la spec, obtenu exactement
```

### Sortie réelle, 111 valeurs

```
111 lignes, 0,57 s
AC.PA   volatilité 20,50 %   drawdown −20,65 %
AF.PA   volatilité 36,27 %   drawdown −42,68 %
CO.PA   volatilité 62,30 %   drawdown −77,97 %   (la plus forte baisse observée)
```

---

## I6 — RSI 14, en Python

### Pourquoi pas en SQL

Le lissage de Wilder est **récursif** : chaque moyenne dépend de la précédente
(`moyenne_t = (moyenne_t−1 × 13 + valeur_t) / 14`). Une fonction fenêtre SQL ne regarde jamais
son propre résultat précédent. La spécification écarte volontairement un CTE récursif, jugé
illisible, au profit d'un calcul en Python — décision reprise telle quelle.

### Les trois cas de la spécification, vérifiés à la lettre

```
14 hausses consécutives  → 100.0   ✅
14 baisses consécutives  → 0.0     ✅
historique ≤ 14 points   → None    ✅ (jamais un chiffre inventé)
```

### Le test qui distingue vraiment Wilder d'une moyenne mobile simple

Deux séries de 17 points partageant les **mêmes 14 dernières variations**, mais un point de
départ différent, donnent des RSI **différents** — la preuve que le calcul dépend de tout
l'historique fourni, pas seulement de la fenêtre récente. Une moyenne mobile simple aurait
donné le même résultat dans les deux cas.

---

## ⭐ Trouvé en interrogeant l'API réelle — pas en relisant le code

Sans rien de plus, les 3 valeurs radiées (Zodiac, Euler Hermes, Gemalto) affichaient une
volatilité et un drawdown calculés sur leur historique de **2018**, avec `fraicheur_jours`
présent mais **jamais exploité** — le même angle mort que celui corrigé sur le lot 1 le
18/08.

**Corrigé** : `cotation_perimee` (même seuil que le lot 1, 40 jours). La mesure reste
affichée — une volatilité passée reste une mesure valide de ce qui s'est produit — mais le
RSI, lui, disparaît pour ces valeurs :

> Un RSI daté de 2018 ne dirait rien d'utile sur « aujourd'hui ». L'absence est plus honnête
> qu'un chiffre resservi hors de son contexte.

Vérifié sur l'API réelle :

```json
{"ticker": "ZC.PA", "date_cours": "2018-03-22", "fraicheur_jours": 3072,
 "volatilite_annualisee_pct": 16.7, "drawdown_max_1a_pct": -24.78,
 "cotation_perimee": true, "rsi_14": null}
```

---

## L'écran — vérifié dans le navigateur

Trois colonnes ajoutées à l'écran 2 : *Volatilité (1 an)*, *Pire baisse (1 an)*, *RSI 14*.

**Deux points de terminaison en parallèle** (`Promise.all`), comme pour le lot 2 sur l'écran
portefeuille — chacun garde une responsabilité, l'attente est celle du plus lent.

**Appariement par ticker vérifié avec un ordre volontairement inversé** dans le navigateur :
les deux points de terminaison ne renvoient pas leurs lignes dans le même ordre — confirmé,
et l'appariement a donné le bon résultat malgré ça.

**Mode dégradé vérifié** : lot 3 en échec → lot 1 reste affiché, les 3 nouvelles colonnes
passent en tirets, aucune erreur console.

---

## 🐛 Deux échecs de test successifs — le même piège, plus subtil à chaque fois

Un test devait vérifier qu'aucun conseil n'apparaît sur le RSI (« achetez », « vendez »).

**Premier essai** : bannir le mot « acheter ». Échec — trouvé dans la phrase même qui
*explique* l'interdit (« RITA n'indique jamais qu'il faut acheter ou vendre »).

**Deuxième essai** : bannir la tournure « il faut acheter ». Échec de nouveau — cette
tournure est une **sous-chaîne littérale** de la même phrase de négation.

**Troisième essai, qui tient** : chercher des formes **impératives** (« achetez », « vendez »),
qui n'apparaissent dans aucune négation à l'infinitif en français correct.

> 🔑 Une négation contient forcément les mots qu'elle nie. Chercher un mot isolé ne suffit
> jamais à distinguer une interdiction de ce qu'elle interdit.

---

## Tests — 19 pour le module, 3 pour l'API, 7 pour l'écran

```
tests/test_indicateurs_risque.py  → 19 passed
tests/test_api_donnees.py         → 45 passed (dont 3 pour /donnees/indicateurs-risque)
tests/test_frontend.py            → 46 passed (dont 7 pour les 3 nouvelles colonnes)
suite complète                    → 302 passed, 1 xfailed
couverture                        → 83 %, seuil 80 % (CI)
```

⚠️ **Limite connue, comme pour les deux lots précédents** : les tests du module RSI
remplacent `_executer`. Ils ne vérifient donc pas le SQL de `lire_volatilite_drawdown` lui-même
— celui-ci est vérifié par exécution réelle, tracée dans ce document, plus deux tests qui
inspectent le texte de la requête (absence de fonction fenêtre après le filtre final).

---

## Ce qui n'est pas fait

| Manque | Conséquence |
|---|---|
| **Lot 4 (relatif)** — annoncé « probablement non réalisé » dès la conception du 15/08 | manque un indice de référence, jamais collecté |
| **Aucun test avec un vrai lecteur d'écran** pour les 3 nouvelles colonnes | mêmes marqueurs que le lot 1, non réécoutés |
| **Le RSI n'est calculé que sur 400 jours de données** | suffisant pour 14 séances, mais un historique plus long donnerait un lissage légèrement différent pour les toutes premières valeurs de la fenêtre |

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **Indicateur** | Un nombre calculé à partir des cours — un fait |
| **Stratégie** | Une règle qui déclenche une décision — un conseil. **Bannie du projet** |
| **Rendement logarithmique** | `ln(cours_t / cours_t−1)` — s'additionne dans le temps, contrairement au rendement simple |
| **`stddev_samp`** | Écart-type d'échantillon (diviseur *n−1*), différent de `stddev_pop` |
| **Drawdown** | Baisse entre un sommet et le creux qui a suivi |
| **RSI** (*Relative Strength Index*) | Rapport entre hausses et baisses récentes, sur 100 |
| **Lissage de Wilder** | Moyenne récursive où chaque valeur dépend de la précédente |
| **Moyenne mobile simple** | Moyenne sur une fenêtre fixe, sans dépendre du passé plus lointain |
| **CTE récursif** | Requête SQL qui s'appelle elle-même — jugée illisible ici, écartée |
| **Fonction fenêtre** (*window function*) | Calcul portant sur des lignes voisines, sans les regrouper |
| **`Promise.all`** | Lance plusieurs requêtes ensemble ; l'attente est celle de la plus lente |
| **Radiée** (*delisted*) | Valeur qui ne cote plus |
| **AMF** | Autorité des marchés financiers |

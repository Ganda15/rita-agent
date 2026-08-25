# INC-002 — Trois tickers rejetés à l'import, et un groupe entier perdu avec eux

| | |
|---|---|
| **Détecté le** | **18/08/2026**, pendant un rafraîchissement de cotations : `1 618 lues / 3 rejetées` là où on attendait `0 rejetée` |
| **Sévérité** | **P2** — données manquantes silencieusement, service fonctionnel |
| **Durée** | détection et correction le même jour |
| **Impact réel** | **nul ce jour-là** — les 3 valeurs radiées étaient seules dans leur groupe. **Mais le défaut était grave par construction** : voir §2 |
| **Commit du correctif** | `8df76ba` — *« Une valeur radiee faisait perdre tout son groupe de tickers »* |
| **Issue / demande de fusion** | **aucune — commit direct sur `develop`** |

## 1. Ce qu'on a vu

```
cotations (yfinance)   lues 1618 | ecrites 1615 | rejetees 3
```

Trois lignes rejetées, sans message d'erreur remonté à l'utilisateur. Le pipeline se déclarait
en succès.

## 2. Cause racine

**Cause technique — deux formes d'absence, une seule testée.**

La validation d'une ligne se protégeait des valeurs manquantes par l'idiome `x == x` :

| Valeur | `x == x` | Rendue par yfinance quand… |
|---|---|---|
| `NaN` | **FAUX** | jour non coté (l'idiome fonctionne) |
| `None` | **VRAI** | **valeur RADIÉE** (l'idiome échoue) |

Les `None` passaient donc le filtre, et la comparaison suivante `c > 0` levait
`TypeError: '>' not supported between instances of 'NoneType' and 'int'`.

**Cause de conception — et c'est là que l'incident devient sérieux.** L'exception ne remontait
pas ligne par ligne : `etape_cotations` groupe les tickers **par date de dernière séance** et
attrape l'exception **au niveau du groupe**, avec un `except Exception`. Un seul ticker radié
faisait donc perdre **tout son groupe**.

> **La gravité n'est pas la ligne perdue, c'est la portée de la perte.**
> Ce jour-là, les 3 valeurs radiées (Zodiac 2018, Euler Hermes 2018, Gemalto 2019) étaient
> seules dans leur groupe : impact nul, par chance. Le jour où une radiée partage sa date avec
> des valeurs vivantes, **elles disparaissent toutes, sans erreur visible**.

## 3. Reproduction en développement

Reproduit sur `ZC.PA` (Zodiac Aerospace, radiée en 2018), mesuré le 18/08/2026 : l'appel
yfinance rend `None` — et non `NaN` — pour les champs OHLCV, et l'exception remonte jusqu'au
groupe.

Vérification chiffrée avant / après, sur le même rafraîchissement :

```
avant : 1 618 lues / 3 rejetées
après : 1 618 lues / 0 rejetée
```

## 4. Procédure de débogage

| # | Hypothèse | Comment elle a été testée | Résultat |
|---|---|---|---|
| 1 | Les 3 tickers n'existent plus chez le fournisseur | appel direct à yfinance sur les 3 symboles | ❌ ils répondent, mais avec des champs à `None` |
| 2 | La validation rejette correctement des données invalides | lecture de `_ligne_valide` | ⚠️ elle **croit** les rejeter — l'idiome `x == x` ne couvre que `NaN` |
| 3 | La perte se limite au ticker fautif | lecture de `etape_cotations` : `except Exception` **par groupe** | ❌ **la perte porte sur tout le groupe** — c'est la vraie découverte |

L'hypothèse 3 est celle qui compte. Les deux premières expliquent le message ; la troisième
explique **le risque**, qui était bien plus grand que le symptôme.

## 5. Correction, étape par étape

1. **Test explicite du `None`**, ajouté *avant* la comparaison numérique :
   ```python
   if any(x is None for x in (o, h, b, c, v)):
       return False
   ```
   *Pourquoi `is None` et pas `== None`* : `is` teste l'identité, sans passer par la méthode
   d'égalité de l'objet — c'est le seul test fiable pour ce cas.
2. **Commentaire de 11 lignes conservé dans le code**, expliquant les deux formes d'absence.
   *Choix assumé* : ce piège se reproduira à la prochaine source de données ; le commentaire
   coûte moins cher que le redécouvrir.
3. **Deux tests ajoutés** dans `tests/test_cotations.py` (+28 lignes).

⚠️ **Ce qui n'a PAS été corrigé, et c'est délibéré** : le `except Exception` par groupe reste
en place. Le corriger changeait la granularité du traitement, donc son comportement en cas de
panne réseau. **Le risque est documenté ici plutôt que traité à la hâte** — c'est une dette
assumée, pas un oubli.

## 6. Vérification et non-régression

Rafraîchissement complet rejoué : **1 618 lues / 0 rejetée**. Base à **275 118** cotations,
retard **0 jour**.

**Tests de non-régression** : `tests/test_cotations.py` — deux cas, dont un qui pose
explicitement `None` là où le précédent posait `NaN`. Le premier échouerait si l'idiome
`x == x` revenait.

## 7. Ce que ça change pour la suite

- **Règle adoptée** : `None` et `NaN` sont **deux** absences différentes. Toute validation de
  données externes teste les deux.
- **Découverte associée** : ces 3 valeurs radiées portaient encore `statut_qualite = 'OK'`.
  L'écran aurait affiché pour elles une « performance 1 jour » calculée sur des cours de 2018.
  D'où la colonne `fraicheur_jours` (seuil 40 j) ajoutée le même jour —
  ***`statut_qualite` décrit la qualité de l'historique, pas sa fraîcheur.***
- **Lien avec C20** : c'est cet incident qui a fait naître l'idée d'une **fraîcheur** mesurée,
  d'abord par valeur (18/08), puis **globale** (25/08, `evidence/C20/preuve-fraicheur.md`).
  *Un incident bien traité ne se referme pas : il produit un dispositif de surveillance.*

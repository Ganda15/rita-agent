# C2 · Preuve — Requêtes SQL d'extraction

**Compétence C2** : *« Développer des requêtes de type SQL d'extraction des données depuis
un système de gestion de base de données et un système big data en appliquant le langage de
requête propre au système afin de préparer la collecte des données nécessaires au projet. »*

**Fichiers** : `db/requetes.sql` (les requêtes documentées) · `sources/database.py`
(exécution programmatique) · `tests/test_database.py` (15 tests)
**Base** : PostgreSQL 18.4 · **273 608 cotations · 111 valeurs · 7 positions**
**Date** : 2026-08-01

---

## Les trois critères de C2, et où ils sont traités

| Critère | Où |
|---|---|
| « Les requêtes sont **fonctionnelles** : les données visées sont effectivement extraites » | §2 — sorties réelles |
| « La documentation met en lumière **choix de sélections, filtrages, conditions, jointures** » | §3 et `db/requetes.sql` |
| « La documentation explicite les **optimisations** appliquées » | §4 — mesures `EXPLAIN ANALYZE` |

---

## 1. Commande

```powershell
Set-Location "D:\KandaWork\RITA_PROJECT\rita-agent"
# les requêtes seules
psql -h localhost -p 5432 -U rita -d rita -f db/requetes.sql
# l'extraction programmatique (C1 — 5e type)
C:\Python314\python.exe -X utf8 -m sources.database
```

## 2. Sorties réelles

### R1 — Portefeuille valorisé, converti en euros

```
Ticker    Nom                       Qte       PRU     Cours    Valo EUR    Perf %
---------------------------------------------------------------------------------
VIRI.PA   CGG BS                    120      1.85     78.90    9,468.00   4164.86
BNP.PA    BNP PARIBAS                15     57.15    106.46    1,596.90     86.28
SU.PA     SCHNEIDER ELECTRIC         10    181.90    257.50    2,575.00     41.56
AI.PA     AIR LIQUIDE                40    158.25    171.58    6,863.20      8.42
OR.PA     OREAL(L')                   8    415.10    382.25    3,058.00     -7.91
SAN.PA    SANOFI                     25     89.60     79.92    1,998.00    -10.80
MC.PA     LVMH MOET VUITTON          12    632.40    466.80    5,601.60    -26.19
---------------------------------------------------------------------------------
TOTAL                                               31,160.70 EUR
```

> ⚠️ **VIRI.PA affiche +4 164 %, et ce chiffre est faux.** C'est un artefact du
> **regroupement d'actions** de CGG devenue Viridien : le prix de revient (1,85 €) est
> **d'avant** le regroupement, le cours (78,90 €) **d'après**. Un regroupement 1-pour-N
> multiplie le cours par N sans enrichir personne.
> **Correctif nécessaire** : une table `operation_sur_titre` (*corporate action*) pour
> ajuster les PRU historiques. Non fait — signalé plutôt que masqué.

### R2 — Plus forts mouvements de la dernière séance

```
ATE.PA    ALTEN                       66.80 ->    79.70    19.31 %
KER.PA    KERING                     250.50 ->   289.90    15.73 %
BVI.PA    BUREAU VERITAS              27.32 ->    29.43     7.72 %
ATO.PA    ATOS SE                     31.92 ->    33.64     5.39 %
CAP.PA    CAPGEMINI                  101.70 ->   106.90     5.11 %
```

### R3 — Volumes anormaux (> 2× la moyenne 20 séances)

```
LTA.PA    ALTAMIR         volume      1,286  moy      215  ratio 5.98x
RMS.PA    HERMES INTL     volume    324,367  moy   72,346  ratio 4.48x
ATE.PA    ALTEN           volume    258,236  moy   87,124  ratio 2.96x
KER.PA    KERING          volume    670,035  moy  255,797  ratio 2.62x
```

> 💡 **ALTEN apparaît dans R2 et R3** : +19,31 % de cours **et** 2,96× son volume habituel.
> Une hausse portée par du volume n'a pas le même sens qu'une hausse sur volume faible.
> C'est exactement le croisement que l'agent Technique doit exploiter.

---

## 3. Les choix, requête par requête

### R1 — jointures

| Jointure | Type | Pourquoi |
|---|---|---|
| `position → valeur` | `JOIN` | la clé étrangère garantit l'existence |
| `position → cotation` | **`LEFT JOIN LATERAL`** | une valeur **suspendue de cotation doit rester visible** avec un cours `NULL`. Un `INNER JOIN` la ferait disparaître du briefing en silence — le pire comportement pour un outil financier |
| `position → taux_change` | `LEFT JOIN` + `COALESCE(…,1)` | une devise sans taux ne doit pas annuler la ligne |

**Choix de sélection** : on part de `position` (7 lignes) et non de `valeur` (111). Le
briefing porte sur ce qui est **détenu**, pas sur l'univers de veille.

**Choix de filtrage** : **aucun filtre** sur `statut_qualite`. Si Era détient une valeur
douteuse, il doit la voir — le statut est **remonté** dans le résultat, pas utilisé pour
cacher.

### R2 — fonction de fenêtrage

`LAG(cloture) OVER (PARTITION BY ticker ORDER BY date_seance)` donne la clôture de la séance
**précédente de la même valeur**.

**Pourquoi pas une auto-jointure** `c2.date = c1.date - 1` : elle serait **fausse**. La
veille d'un lundi n'est pas dimanche mais vendredi, et les jours fériés diffèrent selon la
place de cotation.

**Le filtre qui compte** : `WHERE v.statut_qualite = 'OK'` écarte STLAP.PA et ALJXR.PA. Sans
lui, ALJXR.PA (prix maximum 7 156 748 €) truste le classement avec des chiffres dépourvus de
sens. **C'est là que l'analyse exploratoire du 31/07 devient utile en production** : elle a
produit le statut, la requête s'en sert.

### R3 — moyenne mobile

`AVG(volume) OVER (… ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING)` — la fenêtre **exclut le
jour courant**. Sinon un pic de volume relèverait sa propre moyenne et **se masquerait
lui-même**.

`moyenne_20j > 0` évite une division par zéro : l'analyse exploratoire a mesuré **2 802
séances à volume nul**. Sans cette condition, la requête plante sur les données réelles.

---

## 4. 💎 Optimisations — mesurées, et contraires à ce qui était prévu

### 4.1 L'optimisation que je croyais bonne était 2 000× plus lente

La première version de R1 utilisait un CTE `DISTINCT ON (ticker)`, en supposant qu'il valait
mieux qu'une sous-requête « exécutée une fois par ligne ». `EXPLAIN ANALYZE` sur les
**273 608 cotations réelles** :

| Forme | Temps d'exécution | Plan |
|---|---|---|
| Sous-requête corrélée | **0,12 ms** | `Index Scan Backward using cotation_pkey`, `loops=7` |
| CTE `DISTINCT ON` | **258,00 ms** | `Seq Scan` sur 273 608 lignes + `Sort` |

**Facteur 2 000.** Raison : avec 7 positions, la sous-requête fait **7 recherches d'index**.
Le `DISTINCT ON` trie **toutes** les cotations pour calculer le dernier cours des 107
valeurs — dont 100 dont on n'a pas besoin.

### 4.2 La forme retenue : `LEFT JOIN LATERAL`

Même plan que la sous-requête corrélée (`Nested Loop` + `Index Scan`), mais lisible et
capable de renvoyer plusieurs colonnes.

| Requête | Lignes en entrée | Temps |
|---|---|---|
| `LATERAL` | 7 positions | **0,24 ms** |
| `LATERAL` | 111 valeurs | **1,19 ms** |
| `DISTINCT ON` | 111 valeurs | **295,19 ms** — 250× plus lent |

**La règle qui en sort** : `LATERAL` gagne tant que le nombre de lignes en entrée reste
petit devant le nombre total de cotations. C'est le cas ici et ça le restera — un
portefeuille compte des dizaines de lignes, l'historique des centaines de milliers.

### 4.3 Le bug que les données réelles ont révélé

R2 et R3 utilisaient `max(date_seance)` **global**. Résultat : **2 lignes sur 111**.

```
date_seance | nb_valeurs
------------+------------
 2026-07-29 |          2     <- SLB, FTI (cotées aux États-Unis)
 2026-07-28 |        106     <- Euronext
```

**Chaque place de cotation a son propre calendrier.** Corrigé par un
`GROUP BY ticker` : la dernière séance se calcule **par valeur**. R2 est passée de 2 à
5 lignes, R3 de 0 à 4.

> Ce bug ne se voit **pas** sur un jeu de test fabriqué, où toutes les valeurs ont les mêmes
> dates. Il n'apparaît que sur des données réelles multi-places.

### 4.4 Restriction avant fenêtrage

R3 restreint d'abord à 60 jours dans un CTE : la fenêtre travaille sur ~40 lignes par valeur
au lieu de 2 560. Sans cette restriction, PostgreSQL trie les 273 608 lignes.

---

## 5. Extraction programmatique (C1 — 5ᵉ type)

`sources/database.py` couvre le dernier type exigé par C1 : *« une base de données »*.

C1 demande la *« connexion programmatique à un système de gestion de base de données »* et
l'*« exécution programmatique des requêtes d'extraction de type SQL »*.

**Choix technique** : `RealDictCursor` renvoie des dictionnaires plutôt que des tuples. Un
`ligne[3]` devient faux dès qu'on ajoute une colonne au `SELECT` ; un `ligne["cours"]` reste
juste.

**Sécurité** : tous les paramètres sont **liés** (`%(limite)s`), jamais interpolés en
f-string. C'est ce qui empêche l'injection SQL — vérifié par test
(`test_mouvements_passe_la_limite_en_parametre` : le SQL contient le marqueur, pas la valeur).

---

## 6. Tests

```
C:\Python314\python.exe -m pytest tests/test_database.py -q
→ 15 passed
```

| Famille | Ce qui est vérifié |
|---|---|
| Forme du résultat | dictionnaires, comptage, total |
| Robustesse | une valorisation `NULL` ne casse pas le total |
| Paramètres liés | `%(limite)s` présent, valeur **absente** du SQL |
| Garde-fous SQL | `statut_qualite` présent dans les 3 requêtes |
| Décisions mesurées | `LATERAL` présent, `DISTINCT ON` absent · `GROUP BY ticker` présent |

> Les tests **verrouillent les décisions mesurées**. Si quelqu'un remet un `DISTINCT ON`
> dans R1, un test rouge le lui dira — la mesure ne se perd pas dans un commentaire.

---

## 7. 🎤 Phrase pour l'oral

> « Sur mes trois requêtes, l'optimisation la plus intéressante est celle que j'ai eue à
> l'envers. J'avais écrit un `DISTINCT ON` en pensant éviter une sous-requête exécutée à
> chaque ligne. `EXPLAIN ANALYZE` sur mes 273 608 cotations réelles a montré que ma version
> était **2 000 fois plus lente** : avec 7 positions, la sous-requête fait 7 recherches
> d'index, alors que le `DISTINCT ON` trie toute la table. Je suis passé à un
> `LEFT JOIN LATERAL` — même plan, mais lisible. Et j'ai verrouillé la décision par un test,
> pour qu'elle ne se perde pas. »

---

## 📖 Glossaire

| Terme | En clair |
|---|---|
| **CTE** (*Common Table Expression*) | Le `WITH … AS (…)` — une requête nommée, réutilisable dans la suivante |
| **`LATERAL`** | Sous-requête qui **voit** les colonnes de la ligne courante |
| **`DISTINCT ON`** | Extension PostgreSQL : garder la 1ʳᵉ ligne de chaque groupe |
| **Sous-requête corrélée** | Sous-requête qui dépend de la ligne courante, donc réexécutée à chaque ligne |
| **Fonction de fenêtrage** (*window function*) | Calcul sur un ensemble de lignes voisines, sans les regrouper |
| **`LAG()`** | Fonction de fenêtrage : la valeur de la ligne précédente |
| **`PARTITION BY`** | Découpe la fenêtre par groupe (ici : par ticker) |
| **`ROWS BETWEEN … PRECEDING`** | Cadre de la fenêtre : combien de lignes avant |
| **`LEFT JOIN`** | Garde les lignes de gauche même sans correspondance à droite |
| **`COALESCE`** | Renvoie la 1ʳᵉ valeur non nulle — remplace un `NULL` par un défaut |
| **`EXPLAIN ANALYZE`** | Exécute la requête **et** montre le plan réel avec les temps |
| **`Seq Scan`** | Lecture séquentielle : la base lit toute la table |
| **`Index Scan`** | Lecture par index : la base va droit aux lignes utiles |
| **`Nested Loop`** | Jointure ligne à ligne — efficace quand un côté est petit |
| **`loops=7`** | Le plan a exécuté cette étape 7 fois |
| **Paramètre lié** | Valeur passée séparément du SQL — empêche l'injection SQL |
| **Injection SQL** | Attaque insérant du SQL via une valeur utilisateur |
| **Regroupement d'actions** (*reverse split*) | N anciennes actions → 1 nouvelle, cours ×N |
| ***Corporate action*** | Opération sur titre : split, dividende, fusion — modifie l'historique |

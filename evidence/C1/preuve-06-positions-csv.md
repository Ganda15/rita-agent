# C1 · Preuve 6 — Lecture d'un fichier de données (positions du portefeuille)

**Type de source couvert** : **fichier de données** — 4ᵉ des 5 types nommés par C1
**Fichier** : `sources/positions.py` · **Tests** : `tests/test_positions.py` (30 tests)
**Date d'exécution** : 2026-07-31

## 🔒 Données personnelles — le point à traiter en premier

Le fichier réel contient les **quantités et prix de revient d'Era**. C'est une information
financière personnelle : elle ne doit **jamais** entrer dans un dépôt qui sera ouvert au
jury.

Trois mesures, et une vérification :

1. **Le dépôt ne contient qu'un exemple anonymisé** — `data/positions-exemple.csv`
2. **Le chemin réel passe par variable d'environnement** — `POSITIONS_CSV`, jamais en dur
3. **`.gitignore` bloque les motifs de fichiers personnels**

```gitignore
# --- Données personnelles : JAMAIS versionnées ---
data/positions.csv
data/positions-reelles*.csv
*bourse*.xlsm
*bourse*.xlsx
*portefeuille*.csv
!data/positions-exemple.csv
```

**Vérification réelle** — deux fichiers de test créés puis contrôlés :

```
$ git check-ignore -v data/positions.csv "Ganda bourse 672.xlsm"
.gitignore:16:data/positions.csv       data/positions.csv
.gitignore:18:*bourse*.xlsm            Ganda bourse 672.xlsm

$ git status --short --untracked-files=all | grep -iE "positions|bourse"
?? data/positions-exemple.csv
?? sources/positions.py
?? tests/test_positions.py
```

Seuls l'exemple, le code et les tests sont visibles. **La règle est vérifiée, pas
seulement écrite.**

> Bénéfice secondaire : le script tourne pour le jury **sans aucune donnée personnelle**.
> La démonstration est reproductible telle quelle.

## Commande

```powershell
Set-Location "D:\KandaWork\RITA_PROJECT\rita-agent"
C:\Python314\python.exe -X utf8 -m sources.positions
```

## Sortie réelle (exemple anonymisé)

```
INFO Lecture positions-exemple.csv (encodage=utf-8-sig, separateur=';')
WARNING 2 ligne(s) rejetee(s) sur 12

=== PORTEFEUILLE ===
Positions retenues : 10
Lignes rejetees    : 2
Devises            : ['EUR', 'USD']

Ticker     Nom                        Qte        PRU      Investi  Dev
----------------------------------------------------------------------
MC.PA      LVMH                        12     632.40     7,588.80  EUR
OR.PA      L'Oréal                      8     415.10     3,320.80  EUR
AI.PA      Air Liquide                 40     158.25     6,330.00  EUR
SAN.PA     Sanofi                      25      89.60     2,240.00  EUR
TTE.PA     TotalEnergies               30      54.80     1,644.00  EUR
BNP.PA     BNP Paribas                 15      57.15       857.25  EUR
SU.PA      Schneider Electric          10     181.90     1,819.00  EUR
AAPL       Apple                        6     178.45     1,070.70  USD
MSFT       Microsoft                    4     402.10     1,608.40  USD
VIRI.PA    Viridien                   120       1.85       222.00  EUR
----------------------------------------------------------------------
TOTAL (brut, multi-devises)                      26,700.95
  !! Plusieurs devises : ce total n'a pas de sens tel quel.
     Conversion via sources/ecb.py (taux du jour) avant tout usage.

=== LIGNES REJETEES (tracabilite C3) ===
  ligne 12 : quantite nulle ou negative (0.0)
  ligne 13 : prix de revient absent
```

## 💎 Pourquoi ce n'est pas un `pd.read_csv`

Un export de courtier français cumule **quatre pièges**, et chacun casse une lecture naïve.

| Piège | Ce qui se passe sans traitement | Traitement |
|---|---|---|
| **Séparateur `;`** | Excel FR l'utilise (la virgule est déjà la décimale) → une seule colonne lue | `csv.Sniffer` + repli par comptage |
| **Encodage `cp1252`** | « L'Oréal » devient « L'OrÃ©al » | essai en cascade `utf-8-sig → utf-8 → cp1252 → latin-1` |
| **Nombres FR** | `632,40` → `NaN` ; `1 250` (espace **insécable**) → `NaN` | normalisation dédiée |
| **En-têtes instables** | « Quantité », « Qté », « Nombre de titres », « Quantity » | table de synonymes FR + EN |

Les synonymes sont **en configuration**, pas dans la logique (standard Velmo 2.0, point 7) :
un nouvel export de courtier = une ligne à ajouter, pas une fonction à réécrire.

## 🧹 Validation et traçabilité (C3)

C3 exige *« la suppression des entrées corrompues »*. Le mot important est **identification**
avant suppression : **on n'efface jamais en silence**.

Chaque ligne écartée produit un `Rejet` qui conserve **le numéro de ligne, le contenu
d'origine et la cause** :

```python
@dataclass
class Rejet:
    ligne: int
    contenu: dict
    cause: str
```

Six règles de validation, chacune testée :

| Règle | Cause enregistrée |
|---|---|
| ticker vide | `ticker absent` |
| quantité illisible | `quantite illisible` |
| quantité ≤ 0 | `quantite nulle ou negative (0.0)` |
| PRU vide | `prix de revient absent` |
| PRU ≤ 0 | `prix de revient invalide` |
| — | une ligne rejetée **n'interrompt pas** la lecture des suivantes |

## ⚠️ Le total multi-devises : un piège signalé, pas masqué

Le portefeuille mélange EUR et USD. Additionner brutalement donne **26 700,95** — un nombre
qui n'a **aucun sens financier**.

Deux réponses possibles : convertir silencieusement, ou signaler. On signale :

```
!! Plusieurs devises : ce total n'a pas de sens tel quel.
   Conversion via sources/ecb.py (taux du jour) avant tout usage.
```

**Pourquoi ne pas convertir ici** : ce serait mélanger deux responsabilités. Cette source
*lit un fichier* ; la conversion appartient au pipeline d'agrégation, qui dispose du taux
BCE du jour. Un lecteur qui convertit devient un lecteur qui a besoin du réseau — et qui
échoue quand la BCE est indisponible.

C'est aussi ce qui **relie les sources entre elles** : `positions.py` produit des montants
en devises, `ecb.py` fournit les taux, l'agrégation fait la jonction (C3).

## Tests

```
C:\Python314\python.exe -m pytest tests/test_positions.py -q
→ 30 passed
```

| Famille | Couverture |
|---|---|
| Lecture nominale | champs, montant investi, devise par défaut |
| Les 4 pièges | cp1252 · séparateurs `;` `,` `\t` · nombres FR (8 cas) · 4 synonymes d'en-tête |
| Validation C3 | 6 causes de rejet · un rejet n'emporte pas les lignes valides · ligne source conservée |
| Erreurs franches | colonnes obligatoires absentes · fichier introuvable |
| Confidentialité | `$POSITIONS_CSV` respecté · exemple anonymisé par défaut |

**Aucun test ne lit le fichier réel.** Tous fabriquent leur propre CSV temporaire.

## 🐛 Un bug trouvé par les tests

Le test `test_separateur_virgule_export_anglo_saxon` a échoué au premier passage : la table
de synonymes ne contenait **que du français**. Un export anglo-saxon (`Quantity`, `Shares`,
`Average cost`) était illisible — or le portefeuille contient Apple et Microsoft, donc un
export US est plausible.

Correction : synonymes EN ajoutés. **C'est le test qui a révélé le trou, pas la relecture.**

## Couverture C1 après cette preuve

| Type nommé par C1 | Source | État |
|---|---|---|
| **service web** | yfinance · ECB · *(FRED : clé absente)* | ✅ |
| **page web (scraping)** | Boursorama `/cours/` | ✅ |
| **fichier de données** | **CSV positions** | ✅ |
| **base de données** | PostgreSQL relu en SQL | ⬜ → C2 |
| **système big data** | Parquet partitionné + Spark | 🔶 1/4 |

**4 types sur 5.** Le dernier dépend de la création de la base (décision D15 : PostgreSQL).

## 🎤 Phrase pour l'oral

> « Le lecteur de positions n'est pas un `read_csv`. Un export de courtier français cumule
> quatre pièges : séparateur point-virgule, encodage cp1252, virgule décimale avec espaces
> insécables pour les milliers, et des en-têtes qui changent d'un courtier à l'autre. Je
> les traite tous les quatre, et je trace chaque ligne rejetée avec sa cause plutôt que de
> l'effacer. Et comme ce fichier contient mes vraies positions, le dépôt ne contient qu'un
> exemple anonymisé — j'ai vérifié avec `git check-ignore` que le vrai fichier est bien
> invisible. »

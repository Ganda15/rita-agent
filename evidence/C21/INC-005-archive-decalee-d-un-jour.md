# INC-005 : dix ans de cotations datées un jour trop tôt, et quatre défauts de place de cotation

> Trouvé le 26/09/2026 en écrivant un guide d'étude sur les marchés pour la présentation : chaque
> chiffre du guide a été relu dans la base, et la base ne disait pas ce que la documentation
> disait. Une seule cause pour cinq symptômes : RITA traitait toutes ses valeurs comme cotées à
> Paris, en euros, en heure UTC, sans jour férié. Issues #47, #48, #49, #50, #51, #53 (et #52).

| | |
|---|---|
| **Détecté le** | 26/09/2026 (soir), diagnostic et correctif le 27/09 |
| **Sévérité** | **P1** pour le décalage de date : toute performance à fenêtre calendaire (1 semaine, 1 mois, YTD, 1 an) prenait la mauvaise séance de référence ; **P2** pour la devise (aucune position touchée) |
| **Impact réel** | 273 714 cotations d'archive étiquetées **un jour trop tôt** (52 426 rangées un dimanche) ; HSBA.L lue en pence, donc **100 fois trop haut**, et figée depuis le 28/08 ; FTI et SLB en dollars étiquetés EUR ; 24 séances fictives du samedi ; 3 valeurs radiées redemandées chaque soir ; fraîcheur qui comptait les fériés Euronext comme des retards |
| **Ce qui n'était pas touché** | les 4 330 cotations de la collecte quotidienne (index yfinance déjà localisé) ; les 7 positions du portefeuille (toutes en euros ou en dollars sur des titres non concernés) ; le Parquet lui-même, dont les horodatages sont exacts |

## 1. Ce qu'on a vu *(critère 1 : le symptôme, avant la cause)*

Le 26/09, en comptant les cotations par jour de la semaine pour le guide :

| Période | lun | mar | mer | jeu | ven | sam | dim |
|---|---|---|---|---|---|---|---|
| Archive (avant le 30/07/2026) | 55 162 | 55 176 | 55 281 | 54 216 | **1 453** | 0 | **52 426** |
| Collecte quotidienne | 858 | 860 | 860 | 864 | 864 | 15 | 9 |

La Bourse ne cote pas le dimanche. Un vendredi presque vide et un dimanche plein, c'est
un décalage d'un jour, pas un hasard. Le même soir : `valeur.devise = 'EUR'` pour FTI, SLB
et HSBA.L ; HSBA.L à 1 528,40 « euros » (c'est 1 528,40 pence, soit 15,28 livres) et sans
cours depuis le 28/08 ; ZC.PA, ELE.PA et GTO.PA en échec « possibly delisted » dans chaque
journal de collecte ; la dernière cotation de LVMH datée du **samedi** 26/09.

## 2. Cause racine *(critère 1)*

Cinq causes techniques, une cause de méthode.

1. **#53, le décalage.** `db/importer.py` prenait `r.date.date()`, la date **UTC** de
   l'horodatage. Le Parquet stocke minuit **heure de la place** converti en UTC : `2016-07-31
   22:00+00:00` est le 1er août à Paris. Le fait était écrit noir sur blanc dans
   `sources/cotations.py` depuis le 03/08 (§2 du docstring), pour la collecte quotidienne,
   et jamais appliqué à l'archive. Preuve : le même docstring donne la clôture ajustée de
   MC.PA au 01/08/2016, **127,94** ; la base l'avait sous le 31/07.
2. **#50, HSBA.L figée.** `sources/cotations.py:90` supposait qu'avec un seul ticker yfinance
   rend des colonnes à plat. La version actuelle imbrique toujours ; chaque ligne était
   écartée **sans erreur**. HSBA.L s'est retrouvée seule dans son groupe après le 31/08 (férié
   à Londres, Paris ouvert) et n'a plus jamais été alimentée. Aucun test ne couvrait le cas
   d'un ticker seul : tous en passaient deux.
3. **#47, la devise.** `importer_valeurs` n'écrivait jamais `devise` : la colonne prenait son
   défaut, `EUR`, pour les 111 valeurs. Et Yahoo cote Londres en pence.
4. **#49, le samedi.** L'étape de scraping datait le cours du jour de collecte (`collecte_le[:10]`),
   même un week-end.
5. **#48 et #51.** Les trois valeurs radiées étaient `OK_PARTIEL` dans l'univers, donc `OK` en
   base, donc redemandées ; la fraîcheur ne connaissait que les week-ends, et son commentaire
   citait le 14 juillet comme férié (Euronext Paris cote le 14 juillet).

**La cause de méthode** : la place de cotation n'était modélisée nulle part. Chaque module
refaisait l'hypothèse « Paris, euros, UTC » sans le dire. Et l'analyse exploratoire de
juillet comptait les lignes par ticker, jamais par jour de la semaine : la répartition
ci-dessus aurait suffi à voir le défaut le premier jour.

## 3. Reproduction en développement *(critère 2)*

Tests écrits **avant** le correctif, tous rouges le 27/09 au matin, puis verts :

| Test | Fichier | Rouge pour |
|---|---|---|
| minuit à Paris en été reste le même jour (22h UTC la veille) | `tests/test_marches.py` | `ModuleNotFoundError: sources.marches` |
| un ticker seul est lu malgré les colonnes imbriquées | `tests/test_cotations.py` | `len(r) == 0` |
| les pence de Londres sont convertis en livres | `tests/test_cotations.py`, `tests/test_importer.py` | 1512,2 au lieu de 15,122 |
| la date de séance est la date locale de la place, pas la date UTC | `tests/test_importer.py` | 31/07 au lieu du 01/08 |
| `importer_valeurs` renseigne la devise de cotation | `tests/test_importer.py` | tuple à 4 champs |
| ZC.PA, ELE.PA, GTO.PA marquées DELISTEE ; plus demandées à Yahoo | `tests/test_importer.py`, `tests/test_ingest.py` | `OK` ; demandées |
| un cours scrapé le samedi est rangé au vendredi | `tests/test_ingest.py` | 26/09 au lieu du 25/09 |
| le week-end de Pâques ne compte pas ; le 14 juillet est un jour de bourse | `tests/test_fraicheur.py` | 3 jours au lieu de 1 |

42 tests nouveaux au total (dont 7 pour FRED, issue #52, traitée dans la même branche).

## 4. Procédure de débogage *(critère 3)*

1. Compter par jour de la semaine (`extract(isodow from date_seance)`), archive et collecte
   séparément : le décalage saute aux yeux, et il ne touche que l'archive.
2. Lire le Parquet lui-même : `dtype datetime64[ms, UTC]`, `2016-07-31 22:00+00:00` pour
   MC.PA, `23:00+00:00` pour HSBA.L (Londres). L'archive est juste, l'import est faux.
3. Appeler `fetch_cotations(["HSBA.L"], date(2026, 8, 28))` en vrai : yfinance rend 20 séances,
   la fonction en garde 0. Puis `yf.Ticker("HSBA.L").fast_info["currency"]` : `GBp`.
4. Lire `logs/collecte-2026-09-26.log` : trois « possibly delisted », aucune erreur pour HSBA.L
   (le défaut était silencieux : c'est pour cela qu'il a duré un mois).
5. Vérifier la page officielle des horaires et fériés d'Euronext avant d'écrire le calendrier.

## 5. Correction, étape par étape *(critère 4)*

Branche `qualite-donnees`, un module nouveau et cinq fichiers touchés.

1. `sources/marches.py` : la place déduite du suffixe Yahoo → fuseau, devise, facteur de prix ;
   une place inconnue **lève** au lieu de deviner « EUR » ; Pâques calculée, fériés Euronext,
   `est_jour_de_bourse`, `derniere_seance`.
2. `sources/cotations.py` : décision sur la **forme** des colonnes (`MultiIndex`), pas sur le
   nombre de tickers ; prix multipliés par le facteur de la place.
3. `db/importer.py` : `date_de_seance(r.date, r.ticker)` ; facteur de prix ; devise écrite ;
   ZC.PA, ELE.PA, GTO.PA dans `QUALITE` en `DELISTEE`.
4. `pipelines/ingest.py` : valeurs `DELISTEE` non demandées ; séance du scraping =
   `derniere_seance(date_de_seance(collecte_le))` ; étape `fred` (issue #52).
5. `monitorage/fraicheur.py` : `est_jour_de_bourse` remplace `weekday() < 5`.
6. Données réelles, après **sauvegarde** (`sauvegardes/rita-2026-09-27-avant-migration.dump`,
   5,3 Mo, 8 tables) : migration `db/migration-2026-09-27-places-de-cotation.sql` ; puis, en une
   transaction, suppression des 273 714 lignes d'archive et réimport depuis le Parquet
   (273 608 lignes), conversion des 22 lignes HSBA.L de la collecte, positions vérifiées
   inchangées (7) ; puis suppression des 24 séances de week-end (toutes identiques à la
   veille) ; puis `--etapes cotations,fred` en vrai : 127 cotations (HSBA.L du 28/08 au 25/09),
   30 observations FRED.

Ce que le script de reconstruction **n'a pas appelé** : `importer.importer()`, dont l'étape
positions fait un `INSERT` sans `ON CONFLICT` et aurait dupliqué le portefeuille.

## 6. Vérification et non-régression *(critères 2 et 5)*

| Mesure | Avant (26/09) | Après (27/09) |
|---|---|---|
| Cotations datées samedi ou dimanche | 52 450 | **0** |
| Répartition lun / mar / mer / jeu / ven | 56 020 / 56 036 / 56 141 / 55 080 / 2 317 | 54 633 / 56 145 / 56 040 / 56 016 / 55 080 |
| MC.PA, clôture au 01/08/2016 | 125,0999 (celle du 02/08) | **127,945** (celle du docstring) |
| Cotations de Paris un férié Euronext | non mesuré | **0** |
| HSBA.L, dernière séance et clôture | 28/08, 1 528,40 | **25/09, 15,122** |
| `valeur.devise` hors EUR | 0 | 3 (FTI, SLB en USD ; HSBA.L en GBP) |
| `statut_qualite = DELISTEE` | 0 | 3 |
| `macro_observation` | table absente | 30 lignes, 3 séries |
| Total cotations | 278 044 | 277 933 (moins 2 560 doublons de clé, 24 week-ends, plus 127 rattrapées, à 5 lignes près de collision au 30/07) |
| Positions | 7 | 7 |
| Suite de tests | 535 passed | **577 passed, 2 xfailed** |

Non-régression : les 42 tests de la section 3 restent dans la suite ; `tests/test_marches.py`
verrouille le calendrier et les places ; le correctif est versionné dans une pull request
depuis la branche `qualite-donnees` (critère 5, merge request).

## 7. Ce que ça change pour la suite

- **Le rapport E1** cite « 10 ans pile, du 28/07/2016 au 29/07/2026 » et des séances datées :
  toutes ces dates sont **décalées d'un jour** dans le livrable rendu. Les totaux (273 608
  lignes, 111 valeurs, dédoublonnage) sont inchangés : la clé (ticker, date) a glissé d'un
  bloc. À corriger dans la prochaine version du rapport, en citant cette fiche.
- **Les indicateurs** à fenêtre calendaire recalculent d'eux-mêmes sur les bonnes dates ; les
  moyennes mobiles et le RSI, définis en séances, ne changent pas.
- **Nouvelle règle** : une donnée temporelle porte sa place de cotation, et la date de séance
  est toujours la date **locale** de la place. Toute source nouvelle passe par `sources/marches.py`.
- **Nouvelle vérification** à chaque rechargement massif : la répartition par jour de la
  semaine (à ajouter à `docs/EXPLOITATION.md` §8, « Après un rechargement massif »).
- **Limite qui reste** : les fériés de Londres et de New York ne sont pas modélisés ; seule la
  fraîcheur (qui suit Paris) et le scraping (Paris seulement) utilisent le calendrier.

## 📖 Glossaire

- **UTC** : temps universel, sans heure d'été ; Paris est à UTC+2 l'été, UTC+1 l'hiver.
- **Horodatage** : une date avec une heure et, ici, un fuseau.
- **Pence (GBp)** : centième de livre sterling, unité de cotation à Londres.
- **Radiée (delisted)** : valeur qui a quitté la cote ; son historique reste, ses cours s'arrêtent.
- **Idempotent, rejouable** : qu'on peut exécuter deux fois sans effet supplémentaire.
- **MultiIndex** : colonnes à deux niveaux (ticker, champ) dans un tableau pandas.

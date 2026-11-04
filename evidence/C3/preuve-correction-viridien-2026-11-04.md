# C3 · Preuve : la ligne Viridien ramenée à l'échelle du regroupement (04/11/2026)

**Compétence** : C3, *« Développer des règles d'agrégation de données issues de différentes sources […] la
suppression des entrées corrompues […] l'homogénéisation des formats »*.
**Déclencheur** : Era, sur l'écran Indicateurs de la refonte, le 04/11 : Viridien en tête du portefeuille, « still not
good valuer in the first places ».
**Statut** : correction écrite et testée (base jetable, CI). Le réimport de la base locale et la vérification du
serveur restent à faire par Era (§ 6).

## 1. Le constat, tel que l'API le rendait le 04/11 au matin

Capture de la tâche 0 de la refonte (`evidence/C17/mesures-2026-11-04-avant/entrees/donnees_portefeuille.json`,
non modifiée) : 7 positions, total **32 322,15 €**, et pour Viridien :

```
ticker VIRI.PA · nom_officiel « CGG BS » · quantite 120.0000 · pru 1.8500 · cours 91.7000 (03/11/2026)
investi_eur 222.00 · valorisation_eur 11004.00 · performance_pct 4856.76
```

Soit **34,04 %** du portefeuille et la première place au classement des performances. Le défaut était connu et
jamais corrigé : `evidence/C2/preuve-requetes-sql.md` (août, « +4 164 %, et ce chiffre est faux »), `ETAT.md` du 09/09
(« à corriger dans le CSV, pas dans le code »), `docs/sprint-2/PLAN-TRAVAIL.md` (« un travail à part »).

## 2. Trois erreurs sur la même ligne de `data/positions-exemple.csv`

| Erreur | Ce que dit la source | Source |
|---|---|---|
| PRU à l'ancienne échelle | 1 action nouvelle contre 100 anciennes, regroupement effectif le 31/07/2024 ; rompus indemnisés au plus tard le 29/08/2024 | communiqués Viridien du 27/06 et du 31/07/2024 (copies DILA de l'AMF, et le site de Viridien) |
| ISIN d'une autre société | `FR0013506730` est l'ISIN de **Vallourec** ; Viridien cote sous `FR001400PVN6` depuis le 31/07/2024 (ancien : `FR0013181864`, radié) | document de Vallourec ; communiqué Viridien du 31/07/2024 |
| Nom affiché « CGG BS » | l'importateur prenait le premier libellé de l'univers pour le ticker ; les communiqués disent « Viridien (ex-CGG) » | `data/univers-155.csv:31`, `db/importer.py` (`charger_univers`) |

Liens vérifiés le 04/11/2026 (code HTTP 200) :
- <https://echanges.dila.gouv.fr/OPENDATA/AMF/MKW/2024/06/FCMKW138711_20240627.pdf>
- <https://echanges.dila.gouv.fr/OPENDATA/AMF/MKW/2024/07/FCMKW134201_20240731.pdf>
- <https://www.viridiengroup.com/fr/company/newsroom/press-release/completion-viridien-reverse-share-split>
- <https://www.vallourec.com/app/uploads/2026/03/vallourec-rachat-dactions-reporting-16-20-mars-2026.pdf>

## 3. La mesure qui isole la ligne

Prix de revient divisé par la clôture rétro-ajustée du jour d'achat (`data/bigdata/ohlcv`, lecture seule, 04/11) :

| Ticker | PRU | Clôture du jour d'achat | Rapport |
|---|---:|---:|---:|
| MC.PA | 632,40 | 814,63 (18/04/2023) | 0,776 |
| OR.PA | 415,10 | 383,13 (05/09/2023) | 1,083 |
| AI.PA | 158,25 | 104,85 (22/11/2022) | 1,509 |
| SAN.PA | 89,60 | 82,18 (15/01/2024) | 1,090 |
| BNP.PA | 57,15 | 48,82 (11/03/2024) | 1,171 |
| SU.PA | 181,90 | 155,53 (03/07/2023) | 1,170 |
| **VIRI.PA** | **1,85** | **64,44 (14/10/2021)** | **0,029** |

Les positions d'exemple sont inventées (déclaration d'Era du 10/10/2026) : un rapport autour de 1 ne prouve rien,
mais 0,029 dit une autre échelle, celle d'avant le regroupement.

## 4. La correction et ses règles

- **La ligne** devient `Viridien;FR001400PVN6;VIRI.PA;1;185,00;EUR;2021-10-14`. Les 120 anciennes donnent **1** action
  entière (le communiqué ne crée pas de fraction d'action) ; son prix de revient est le coût des 100 anciennes
  qu'elle remplace, 100 × 1,85 = **185 €**. Les **20 rompus** ne sont pas reconstitués : leur indemnisation dépend de
  l'intermédiaire, et le communiqué ne la chiffre pas. **37 € (20 × 1,85) est leur coût d'achat d'origine, pas le montant
  de leur indemnisation, qui n'est pas connu.** C'est une position **simulée** exprimée après regroupement, pas la
  reconstitution d'un vrai compte. À dire tel quel : « Positions ouvertes simulées, hors espèces et sans l'indemnisation
  des rompus. »
- **Pas de fausse vente.** La réconciliation identifie une ligne par (ticker, PRU, date d'achat). Réimporter le CSV
  corrigé aurait clos l'ancienne ligne à la date du réimport et inséré une ligne neuve : une vente qui n'a jamais eu
  lieu. `db/importer.py` corrige donc sur place, **avant** la réconciliation (`REGROUPEMENTS`,
  `position_regroupee`, `corriger_regroupements`) : seule la ligne exacte d'avant, encore ouverte, est visée ; si la
  ligne corrigée existe déjà, rien n'est touché ; rejouée, la correction ne trouve plus rien. Le bilan de l'import
  compte les lignes `corrigees`.
- **Le nom** : `NOMS_OFFICIELS = {"VIRI.PA": "VIRIDIEN"}` ; les libellés du courtier (« CGG BS », « CGG RGPT ») restent
  des alias.
- **Le verrou de démonstration** (#152) compare la base au fichier `passerelle_mcp/jeu_demo_attendu.csv`, aligné sur la
  même ligne (`VIRI.PA;1.0000;185.0000;EUR`). Tant qu'une base n'est pas réimportée, la passerelle MCP la refuse :
  c'est le sens prudent.
- **Ce qui n'est pas fait** : une table des opérations sur titres (`operation_sur_titre`), le correctif durable signalé
  en août. Hors calendrier avant l'oral blanc des 12-13/11 ; limite à dire au jury.

## 5. Les tests, écrits avant le code

`tests/test_correction_viridien.py` (sans base, tourne dans le job `pytest` de la CI) : la règle du regroupement
(120 → 1 action, 185 €, 20 rompus ; moins de 100 anciennes refusé), la ligne d'exemple égale à la ligne regroupée et
son ISIN, le jeu attendu de la passerelle, le nom `VIRIDIEN` avec les deux alias. Plus une **alerte** locale
(archive Parquet hors Git, sautée en CI) : rapport PRU / cours du jour d'achat dans [0,2 ; 5]. Une alerte, pas une
preuve : un PRU peut cumuler des achats et des frais.

`tests/test_correction_viridien_base.py` (marqueur `postgresql`, job `base` de la CI), sur une valeur fictive
`ESSAI.VR` dans une transaction annulée : la ligne est corrigée sur place et reste ouverte ; rejouer ne crée ni
doublon ni clôture ; sans la correction, le réimport aurait fabriqué une vente (constaté) ; la vue
`v_portefeuille_valorise` rend 1 action, 91,70 €, **-50,43 %** pour un cours de 91,70 €.

`tests/test_importer.py::test_les_lignes_absentes_du_csv_sont_closes_a_la_date_du_jour` : test existant adapté. Il
comptait toutes les requêtes `UPDATE position` et en attendait une, la clôture ; il compte maintenant les clôtures
(toujours une seule), et vérifie en plus que la correction ne clôt rien et passe avant la clôture.

Sorties (Python 3.14, 04/11/2026) :

```
# avant le code : rouges pour la bonne raison
7 failed, 4 errors   (REGROUPEMENTS et position_regroupee absents ; 'CGG BS' == 'VIRIDIEN' faux ;
                      jeu attendu encore à 1.8500 ; alerte {'VIRI.PA': 0.029})
# après le code et les deux fichiers de données
tests/test_correction_viridien.py + tests/test_correction_viridien_base.py : 11 passed
tests/test_importer.py tests/test_passerelle_mcp.py tests/test_positions.py tests/test_correction_viridien.py : 123 passed
```

Base jetable, comme le job `base` de la CI : `postgres:18-alpine`, mode `trust`, port publié sur `127.0.0.1:55433`
seulement, schéma puis rôles du dépôt (`db/schema.sql`, `db/roles.sql`), données fictives seulement, conteneur
`rita-base-jetable-viridien` supprimé après l'essai.

```
pytest -q -rs --no-cov -m postgresql tests   →   29 passed, 2140 deselected   (aucun saut)
```

Suite complète sur le poste, deux fois (la seconde avec Azure injoignable sur `127.0.0.1:9`, pour prouver qu'aucun
test n'appelle le vrai modèle) :

```
2115 passed, 52 skipped, 2 xfailed, 4 warnings in 359.26s (0:05:59)
2115 passed, 52 skipped, 2 xfailed, 4 warnings in 306.02s (0:05:06)
```

Soit les 2 108 réussis d'avant plus les 7 tests sans base ; les 4 tests de base sont sautés sur le poste (aucune base
de test déclarée), et réussis sur la base jetable ci-dessus.

Suite complète finale du 04/11/2026 au soir, après les correctifs d'Indicateurs, la liste des valeurs et le versionnement
de l'interface (les mêmes deux passages, Azure injoignable pour le second) :

```
2139 passed, 52 skipped, 2 xfailed, 4 warnings in 332.18s (0:05:32)
2139 passed, 52 skipped, 2 xfailed, 4 warnings in 284.95s (0:04:44)
```

Les 52 sautés comprennent les 4 tests de base de cette correction (aucune base de test déclarée sur le poste).

## 5 bis. La base locale avant le réimport (lecture seule, 04/11/2026)

Base `rita`, port 5433, lue par le module du projet (`sources/database.py`), aucune écriture : 111 valeurs, 7 positions,
280 848 cotations jusqu'au 03/11/2026. Position id 7 : `VIRI.PA`, 120 × 1,85, achetée le 14/10/2021, ouverte ;
valeur nommée « CGG BS » ; vue de valorisation : 7 lignes, total 32 322,15 €, Viridien à +4 856,76 % pour 11 004,00 €.

## 5 ter. Que la leçon serve : deux gardes (04/11/2026 au soir)

Viridien est resté en tête d'un écran à +4 856 % sans que personne le voie, alors que le défaut était écrit depuis août.
Corriger la ligne ne suffit pas : le même cas se reproduira avec un vrai portefeuille dès qu'un regroupement d'actions
tombera entre l'achat et aujourd'hui. Deux gardes, chacun avec ses tests écrits avant :

- **À l'import** (`db/importer.py`, `controler_prix_de_revient`) : chaque import signale une position ouverte dont le
  prix de revient est hors de 0,2 à 5 fois le dernier cours à ou avant la date d'achat, avec le rapport et **la date du
  cours réellement lu** (un achat un samedi lit le cours du vendredi). Si la devise du prix de revient diffère de celle du
  cours, le rapport n'est **pas calculé** et le bilan dit « contrôle non effectué, devises différentes » : des bornes
  larges ne rendent pas correcte la comparaison de deux monnaies. Mesuré : 0,78 à 1,51 pour six lignes, 0,029 pour
  Viridien avant correction, 2,87 après. Tests sur la base jetable : la ligne fausse est signalée, plus rien une fois
  corrigée ; deux devises ne sont pas comparées ; la date du cours est celle du vendredi pour un achat le samedi.
- **À la lecture** (`frontend/app.js`, `afficherAlertes`) : l'écran Portefeuille écrit, avant les dessins, « Performance hors
  du commun, à vérifier » pour +900 % ou plus et -90 % ou moins (un prix multiplié ou divisé par dix), avec la cause
  possible. Rien n'est caché ni plafonné : le graphique garde une échelle commune, la valeur extrême et son pourcentage
  exact (test `test_barres_une_valeur_extreme_garde_l_echelle_commune_un_zero_visible_et_tous_ses_chiffres`).

Limites dites : les deux seuils sont des conventions déclarées, pas des mesures ; un regroupement de 5 pour 1 passe sous
le seuil de l'écran, un prix de revient qui cumule des achats peut sortir des bornes de l'import sans erreur. Un zoom
explicite sur les autres valeurs n'est pas fait : il ne servirait que pour une valeur extrême juste.

## 5 quater. Un ancien fichier CSV réimporté après la correction (relecture extérieure, 04/11/2026)

**Le risque, constaté sur la base de test avant tout correctif** : la base est corrigée (1 × 185) ; on réimporte l'ANCIEN
CSV (120 × 1,85). Résultat mesuré : la ligne corrigée est **close à la date du jour** (une vente inventée) et la mauvaise
ligne `120 × 1,85` est **réinsérée ouverte**. Le test « deux imports du CSV corrigé » ne couvrait pas ce scénario.

**Le correctif** (`convertir_lignes_d_avant_regroupement`, appelé avant la réconciliation) : une ligne du fichier qui porte
exactement la ligne d'avant (ticker, date d'achat, quantité, prix de revient) est convertie au passage en `1 × 185`, avec un
avertissement « mettre le CSV à jour » et un compteur `converties` dans le bilan. Le périmètre est celui du jeu simulé : une
ligne qui s'en approche (autre quantité, autre prix de revient, autre date, autre valeur) n'est pas touchée ; une ligne déjà
corrigée ne l'est pas deux fois. Choix : convertir plutôt que refuser, pour qu'un import donne le même état quel que soit le
fichier lu, sans arrêt au milieu d'une démonstration ; l'avertissement et le compteur rendent la conversion visible.

Tests sur la base jetable (rouge avant, vert après) : l'ancien CSV après la correction ne réintroduit rien et ne ferme rien ;
l'ancien CSV sur une base jamais corrigée donne la ligne corrigée (`corrigees 1`, `converties 1`, `closes 0`).

## 5 quinquies. La répétition sur une copie de l'état réel, avant d'écrire dans la vraie base (04/11/2026 au soir)

L'écran d'Era montrait toujours l'ancienne ligne : la base n'était pas réimportée. Avant de l'écrire, la vraie commande a été
jouée sur une copie. Méthode : sauvegarde (CSV) des tables `position`, `valeur` et `alias_valeur` de la base locale
(`rita`, port 5433, PostgreSQL 18.4), restauration dans un PostgreSQL jetable avec les cotations des sept valeurs
détenues (18 389 lignes), puis `python -m db.importer --dsn <la copie>`. L'extraction que sert l'API
(`sources.database.portefeuille`) donnait avant : Viridien 120 × 1,85, +4 856,76 %, 11 004,00 €, total 32 322,15 €, comme
l'écran d'Era. Conteneur supprimé ensuite.

**Deux défauts trouvés par cette répétition, absents des tests :**

1. **`--limite-annees` plantait** (`Categorical is not ordered`) : pandas lit la colonne de partition `annee` du Parquet comme
   une catégorie sans ordre. Les tests simulaient un entier. Corrigé, avec un test sur un vrai Parquet partitionné
   (rouge, puis vert) ; vérifié sur le vrai Parquet : 276 168 lignes lues, 15 757 de 2026 tentées.
2. **L'import complet change plus que la position** : il recalcule à la fin les dates de première et de dernière cotation
   de toutes les valeurs. Mesuré en lecture seule sur la base locale : **108 valeurs sur 111** auraient changé
   (`derniere_cotation` à 2026-09-25 au lieu du 2026-11-03), et l'API en lit deux colonnes (`api/donnees.py:74`). Sans
   rapport avec Viridien. D'où `--positions-seulement` : les valeurs et les positions, ni les cotations ni ces bornes
   (test sans base, et `--limite-annees` s'exclut avec lui).

Mesuré aussi, hors ligne : sur les 111 valeurs, l'import ne change que le nom de `VIRI.PA` (statuts, notes et devises
identiques) ; le Parquet n'ajouterait aucune cotation (la base en a 22 997 pour 2026, le Parquet 15 757, aucune manquante).

**Résultat de la répétition** (`--positions-seulement`) : `inserees 0, mises a jour 7, rouvertes 0, closes 0, corrigees 1,
converties 0` ; une seule valeur changée (`VIRI.PA` : `CGG BS` devient `VIRIDIEN`) ; une seule position changée (id 7 :
120 × 1,85 devient 1 × 185, même id, ouverte) ; cotations inchangées ; total 32 322,15 € devient **21 409,85 €**, comme
le calcul à la main. Second passage : `corrigees 0, closes 0`, état identique. Ancien CSV réimporté ensuite : `converties 1,
closes 0`, état identique. Détail utile pour un retour arrière : la table `position` de la base réelle a ses colonnes dans
un autre ordre que celle d'un schéma neuf (`date_cloture` ajoutée après `importe_le`) ; une restauration doit nommer les
colonnes.

## 6. Ce qui reste, et qui le fait

1. **Fait le 04/11/2026 à 17 h 33 sur la base locale** (`rita`, port 5433 ; la production n'est pas touchée) :
   `python -m db.importer --positions-seulement`, avec `PGOPTIONS='-c lock_timeout=15000'`, après une sauvegarde CSV des
   tables `position`, `valeur` et `alias_valeur` (empreintes `c80ccffaa0d98ecc`, `68bae20dabda5fec`, `c0b4c5fbadce33a3`
   recalculées à l'identique par un relecteur), une répétition sur une copie de l'état réel, et une revue indépendante
   (trois relecteurs en lecture seule : « go » pour cette commande, « no-go » pour `--limite-annees 1`, qui aurait changé
   les bornes de cotation de 108 valeurs). Conditions vérifiées avant : 17 h 32, collecte de 19 h « prête », aucun
   processus d'import, de collecte ou de test en cours.
   - **Bilan de l'importateur** : `inserees 0, mises a jour 7, rouvertes 0, closes 0, corrigees 1, converties 0` ; contrôle
     du prix de revient : aucun hors de l'échelle ; code de sortie 0.
   - **Comparaison colonne par colonne avec la sauvegarde** : `position` 9 cellules différentes sur 56 (`importe_le` sur les
     sept lignes, `quantite` et `pru` sur la ligne 7) ; `valeur` **1 cellule sur 1 110** (`VIRI.PA`, `nom_officiel` : `CGG BS`
     devient `VIRIDIEN`) ; `alias_valeur` 0 sur 336. Aucune ligne ajoutée ni retirée, aucune clôture, une seule ligne
     `VIRI.PA`, id 7 conservé. Cotations : 280 848 avant et après. Bornes de cotation : les 108 valeurs en retard le restent
     (voulu). Le compteur PostgreSQL « 111 mises à jour » sur `valeur` est le compte des lignes réécrites par l'upsert, dont
     110 avec des valeurs identiques ; seule la comparaison des cellules fait foi.
   - **Ce que l'API sert maintenant** (même extraction, `sources.database.portefeuille`) : Viridien **VIRIDIEN**, 1 × 185,00,
     cours 91,70, performance **-50,43 %**, valorisation 91,70 €, poids 0,43 % ; total **21 409,85 €** ; première ligne :
     Air Liquide, 34,11 %. Contrôle du prix de revient : sept positions comparées sur sept ouvertes, Viridien à 2,871.
   - **Écran, avant et après** (captures d'Era sur la page locale `localhost`, base locale `rita` ; **vérification locale, pas
     une validation en production**, dont les positions restent à lire en lecture seule avant la tâche 12) ; dossier
     `captures-viridien-2026-11-04/` :
     - `1-avant-donnee-ancienne.webp` : « CGG BS », 120, 1,85, +4 856,76 %, 34,04 %, total 32 322,15 € ; la barre de Viridien
       écrase les six autres ; le bandeau « Performance hors du commun, à vérifier » s'affiche (c'est lui qui a été jugé
       insuffisant : il signale, il ne corrige pas).
     - `2-apres-reimport.webp` (04/11, après 17 h 33) : **VIRIDIEN**, total **21 409,85 €**, 7 lignes ouvertes, 0 sans taux,
       0 close ; plus de bandeau ; barres lisibles : BNP Paribas +53,30 %, Schneider +31,80 %, Air Liquide +15,36 %, L'Oréal
       +4,24 %, Sanofi -9,62 %, LVMH -36,51 %, Viridien **-50,43 %** ; poids : Air Liquide 34,1 %, LVMH 22,5 %, L'Oréal
       16,2 %, Schneider 11,2 %, Sanofi 9,5 %, BNP 6,1 %, Viridien 0,4 % (somme 100,0 %) ; le tableau montre sa colonne
       « Date du cours » alignée, et les poids de ses lignes (6,14 %, 11,20 %, 34,11 %, 16,17 %, 9,46 %) égalent ceux de
       l'extraction de l'API relue en base. Recalcul indépendant : 32 322,15 - 11 004,00 + 91,70 = 21 409,85 ;
       (91,70 / 185 - 1) × 100 = -50,43 %. Limite : les deux dernières lignes du tableau sont coupées en bas de la capture ;
       Viridien se lit dans le graphique et dans la légende des poids.
2. **La production** : lue en lecture seule le 04/11 au soir, elle porte encore la ligne d'avant (id **14**, 120 × 1,85,
   « CGG BS » ; cours arrêtés au 27/10). **Un déploiement ne lance aucun import** : corriger la production est une
   opération séparée, après le déploiement du code, avec l'accord explicite d'Era, par le mode le plus étroit de
   l'importateur (`--corrections-seulement`, avec `--a-blanc` puis `--attendu-corrigees 1 --attendu-noms 1`). Plan :
   `docs/PLAN-VIRIDIEN-PRODUCTION.md`. Rien n'est écrit en production à la date de ce fichier.
3. La baisse de 10 912,30 € du total est une **correction de valorisation affichée**, pas une perte survenue ce jour-là.

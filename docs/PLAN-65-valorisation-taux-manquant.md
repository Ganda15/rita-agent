# Plan : la vue de valorisation ne remplace plus un taux manquant par 1 (issue #65, cas D06)

> **Établi le 03/10/2026** après la validation du chapitre « Données » par le formateur. **Zone sous garde**
> (`db/schema.sql`, `AGENTS.md`) : ce plan est relu et validé par Era **avant** toute ligne de code.
> Rien de ce qui suit n'est fait. Trois décisions sont à prendre (section 7).

## 1. Le défaut, mesuré

| Où | Ce qui est écrit | Effet |
|---|---|---|
| `db/schema.sql`, vue `v_portefeuille_valorise` | `ROUND(p.quantite * p.pru / COALESCE(t.valeur_pour_eur, 1), 2)` pour `investi_eur` et `valorisation_eur` | une devise **sans taux** divise par 1 : le montant nominal (en USD, en JPY) **s'affiche en euros** sans conversion |
| `db/requetes.sql`, requête R1 | la même expression (copie, documentée dans le rapport E1) | même effet sur l'extraction C2 |
| `sources/database.py`, `SQL_PORTEFEUILLE` | la même expression (troisième copie, celle que lit l'API) | même effet sur `/donnees/portefeuille` et sur l'outil MCP |
| `tests/test_database.py:147` | `assert "COALESCE" in database.SQL_PORTEFEUILLE` | le test **fige** le défaut : il protège l'ancienne décision |

Le commentaire de la vue le dit comme une qualité : « une devise sans taux reste à son montant nominal via
COALESCE. Un INNER JOIN les ferait disparaître en silence ». C'était la bonne réponse à la mauvaise question :
ne pas faire disparaître la ligne, oui ; **afficher un faux montant en euros, non**. Le chapitre (§2.3, cas D06)
fixe la règle cible avec un exemple : 10 titres à 20 USD, taux 1,25 USD pour 1 EUR, c'est 160 EUR ; taux absent,
c'est **« indisponible »**, pas 200.

**État de la base du poste le 03/10 (mesuré)** : 7 positions, toutes en EUR ; `taux_change` a 30 observations
pour chacune des cinq devises (CHF, EUR, GBP, JPY, USD), dernière le 02/10 ; aucune ligne de la vue n'a de
valorisation nulle. **Le défaut est donc latent aujourd'hui** : il se déclencherait sur une base neuve avant la
première collecte BCE, sur une devise que la BCE ne publie pas, ou si l'étape `ecb` échoue plusieurs jours
(elle a rendu « USD : ReadTimeout » en simulation le 03/10 à 11 h 50). Le jeu de démonstration contient deux
positions en USD (AAPL, MSFT) : c'est lui qui le montrerait en premier.

## 2. La règle cible

1. **L'euro n'a pas besoin de taux** : une position en EUR se convertit par 1, explicitement, sans lire
   `taux_change`. Aujourd'hui elle dépend de la ligne « EUR = 1 » que l'étape `ecb` insère chaque soir
   (`tests/test_ingest.py::test_ecb_ajoute_l_euro_a_1`) ; cette dépendance disparaît.
2. **Une devise étrangère sans taux rend `NULL`** pour `investi_eur` et `valorisation_eur`, et une colonne
   `taux_manquant` vaut vrai. La ligne reste visible (les deux `LEFT JOIN` ne changent pas) : quantité, PRU,
   cours, performance en devise restent affichés.
3. **Rien de ce qui agrège une valorisation nulle ne prétend être complet** : total du portefeuille, poids,
   exposition (section 4).
4. `performance_pct` ne change pas : il compare PRU et cours **dans la devise de la position** ; la comparaison
   de devises entre PRU et cours est le cas D07, issue #69, traitée à part.

## 3. Le SQL, une seule écriture, trois emplacements

```sql
-- dans le SELECT de la vue (et des deux copies)
CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END                                   AS taux_pour_eur,
ROUND(p.quantite * p.pru     / CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END, 2) AS investi_eur,
ROUND(p.quantite * d.cloture / CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END, 2) AS valorisation_eur,
ROUND((d.cloture - p.pru) / p.pru * 100, 2)                                                    AS performance_pct,
(p.devise <> 'EUR' AND t.valeur_pour_eur IS NULL)                                               AS taux_manquant
```

Pourquoi un `CASE` et non `COALESCE(t.valeur_pour_eur, CASE WHEN p.devise = 'EUR' THEN 1 END)` : la première
forme se lit à voix haute (« si c'est de l'euro, 1 ; sinon le taux, ou rien ») ; la seconde demande de savoir
que `COALESCE` avec un `NULL` rend `NULL`.

Les deux colonnes nouvelles (`taux_pour_eur`, `taux_manquant`) vont **en fin de liste** : `CREATE OR REPLACE
VIEW` n'accepte d'ajouter des colonnes qu'à la fin, et c'est ce qui permet une migration sans `DROP VIEW`
(les requêtes de `db/indicateurs_portefeuille.sql` lisent la vue par nom de colonne, elles ne cassent pas).

Le commentaire de la vue (`COMMENT ON VIEW`) et le bloc « CHOIX DE JOINTURE » de `db/requetes.sql` sont réécrits
pour dire la règle nouvelle et sa date.

## 4. Ce qui consomme la vue, et ce qui change

| Consommateur | Aujourd'hui | Après | Fichier |
|---|---|---|---|
| `GET /donnees/portefeuille` | `total_eur = somme des valorisations, NULL compté 0` | `total_eur` **null** dès qu'une position a `taux_manquant`, plus `positions_sans_taux: n` ; chaque position porte `taux_manquant` | `api/donnees.py`, `sources/database.py::total_portefeuille` |
| Poids et exposition (`/donnees/indicateurs-portefeuille`) | `SUM(valorisation_eur)` ignore les `NULL` : les poids se calculent **sur un total partiel, sans le dire** | si une valorisation est nulle, `poids_pct` et `exposition_pct` sont **null pour toutes les lignes** et la réponse porte `complet: false` (un poids sur un total partiel est faux pour toutes les lignes, pas seulement pour celle qui manque) | `db/indicateurs_portefeuille.sql`, `indicateurs/portefeuille.py`, `api/donnees.py` |
| Écran portefeuille (`frontend/app.js`) | `euro.format(nb(null))` affiche **0,00 €** | la cellule affiche **« indisponible »** avec, au survol, « taux de change manquant pour USD » ; le total affiche « indisponible (1 position sans taux) » | `frontend/app.js`, `frontend/index.html` |
| Outil MCP `rita_portefeuille` | passe la réponse de l'API | inchangé : il passe `null` et `taux_manquant` ; la comparaison au jeu d'exemple (#60) ne lit que ticker et quantité | aucun |
| Rédacteur (prompt) | ne lit pas la vue | inchangé | aucun |
| Extraction C2 (`python -m sources.database --requete portefeuille`) | même calcul | même règle, sortie `NULL` lisible | `sources/database.py` |

## 5. Les tests, écrits avant le code

| # | Test | Fichier | Rouge d'abord ? |
|---|---|---|---|
| 1 | contrat : aucune des trois copies ne contient `COALESCE(t.valeur_pour_eur, 1)` ; chacune contient le `CASE` sur `'EUR'` et la colonne `taux_manquant` | `tests/test_database.py` (R1 et `SQL_PORTEFEUILLE`), `tests/test_schema.py` (nouveau, la vue) | oui |
| 2 | `test_r1_utilise_left_join_pour_ne_pas_masquer_une_position` : garder `LEFT JOIN LATERAL`, **retirer** l'assertion sur `COALESCE` et dire pourquoi dans la docstring | `tests/test_database.py:147` | il devient faux par construction |
| 3 | base réelle (sauté sans `DATABASE_URL`, comme `tests/test_role_lecture.py`) : dans **une transaction annulée à la fin**, supprimer les taux USD, insérer une position USD sur une valeur existante, lire la vue : `valorisation_eur IS NULL`, `taux_manquant` vrai, la ligne présente ; une position EUR garde sa valorisation même sans aucune ligne `taux_change` | `tests/test_vue_valorisation.py` (nouveau) | oui |
| 4 | API : avec des lignes simulées dont une a `valorisation_eur = None`, `total_eur` est `null` et `positions_sans_taux == 1` ; sans manque, `total_eur` est la somme | `tests/test_api_donnees.py` | oui |
| 5 | poids : avec une valorisation nulle, tous les `poids_pct` sont `null` et `complet` est faux | `tests/test_indicateurs_portefeuille.py` | oui |
| 6 | front : le code contient « indisponible » pour une valorisation nulle, et n'affiche jamais « 0,00 € » pour `null` ; test de fumée Playwright : une position sans taux affiche « indisponible » | `tests/test_frontend.py`, `tests/test_smoke_ui.py` | oui |
| 7 | `test_ecb_ajoute_l_euro_a_1` : la docstring dit désormais que la ligne EUR reste utile pour l'exposition et les séries, mais que la vue n'en dépend plus | `tests/test_ingest.py` | inchangé |

Règle INC-006 : le test 3 **n'écrit jamais** dans la base ; `BEGIN` puis `ROLLBACK`, et il se saute sans
`DATABASE_URL`. La CI n'a pas de PostgreSQL : il tourne sur le poste, et sa sortie est collée dans la preuve.

## 6. L'ordre des opérations

1. Era valide ce plan (et tranche la section 7).
2. Tests 1 à 6 écrits, lancés, **vus rouges**.
3. SQL : la vue dans `db/schema.sql`, R1 dans `db/requetes.sql`, `SQL_PORTEFEUILLE` dans `sources/database.py`,
   les poids dans `db/indicateurs_portefeuille.sql` ; commentaires réécrits.
4. Migration rejouable `db/migration-2026-10-XX-vue-valorisation-taux.sql` (`CREATE OR REPLACE VIEW` seul, même
   forme que celle du 27/09), citée dans `docs/EXPLOITATION.md` §4.3 à côté de la migration des places de cotation.
5. API, poids, front. Tests verts, suite complète, couverture.
6. Migration jouée sur le poste (`psql ... -f db\migration-...sql`), puis sur la base Compose, puis sur Hetzner ;
   sortie de `SELECT taux_manquant, COUNT(*) FROM v_portefeuille_valorise GROUP BY 1` collée dans
   `evidence/C4/preuve-vue-valorisation-taux-manquant.md` (nouveau).
7. Ledger : la décision D « montant nominal via COALESCE » est **remplacée**, datée, avec le pourquoi ;
   `CHANGELOG.md` ; rapport E1 v2 : une phrase dans la section « requêtes » (la sortie de R1 change de forme) ;
   `docs/conception/donnees/README.md` : ligne D06 passée à « fait ».
8. Commit sur `develop` avec `Closes #65`, PR `develop → main` relue.

Estimation : 2 h à 2 h 30, une douzaine de tests. Rien ne touche `guardrails/` ni `evals/`.

## 7. Trois décisions pour Era

| # | Question | Option A (recommandée) | Option B |
|---|---|---|---|
| D1 | Le total quand une position n'a pas de taux | **`total_eur` null + `positions_sans_taux`** : un total partiel présenté comme total est le même mensonge à une autre échelle | total des positions convertibles + `total_partiel: true` |
| D2 | Les poids quand une valorisation est nulle | **tous `null` + `complet: false`** : un poids sur un total partiel est faux pour chaque ligne | poids calculés sur le total partiel + drapeau |
| D3 | Les trois copies du SQL | **garder les trois**, alignées par le test de contrat n° 1 (R1 est une pièce du rapport E1, `SQL_PORTEFEUILLE` est l'extraction C2 lue par l'API) | `SQL_PORTEFEUILLE` devient `SELECT * FROM v_portefeuille_valorise` : une copie de moins, mais l'API dépend alors de la vue installée |

## 8. Risques, dits franchement

- **Trois copies** du même calcul : c'est le test de contrat qui les tient alignées, pas la discipline.
- Sur une base **neuve** (Compose, serveur) avant la première collecte BCE, les positions USD du jeu de
  démonstration affichent « indisponible » : c'est le comportement voulu, et il sera visible en démonstration
  si l'étape `ecb` n'a pas tourné. À dire dans `docs/EXPLOITATION.md`.
- `CREATE OR REPLACE VIEW` échoue si l'ordre ou le type des colonnes existantes change : on ajoute en fin de
  liste, on ne renomme rien.
- Le rapport E1 envoyé le 13/08 montre une sortie de R1 avec l'ancienne règle ; la v2 du 15/10 le dit en une
  phrase plutôt que de réécrire la sortie.

## 📖 Glossaire

- **`COALESCE(a, b)`** : la première valeur non nulle ; ici, `1` quand le taux manque.
- **`LEFT JOIN`** : garde la ligne de gauche même sans correspondance à droite ; les colonnes de droite valent `NULL`.
- **`CREATE OR REPLACE VIEW`** : remplace la définition d'une vue sans la supprimer ; n'accepte que des colonnes ajoutées à la fin.
- **Migration rejouable** : un script SQL qu'on peut lancer deux fois sans effet différent.
- **Transaction annulée** : `BEGIN` puis `ROLLBACK` ; tout ce qui a été écrit entre les deux disparaît.

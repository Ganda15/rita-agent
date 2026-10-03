# Preuve C4 et C2 : la vue de valorisation ne remplace plus un taux manquant par 1 (03/10/2026)

> Issue #65, cas D06 du chapitre « Données » (validé par le formateur le 03/10/2026). Plan relu et validé par
> Era le 03/10 avec les décisions D1, D2, D3 = A : `docs/PLAN-65-valorisation-taux-manquant.md`.
> Zone sous garde (`db/schema.sql`) : rien n'a été écrit avant la validation du plan.

## 1. Ce qui changeait, et pourquoi

Jusqu'au 03/10, `v_portefeuille_valorise`, la requête R1 du rapport E1 et l'extraction lue par l'API divisaient
par `COALESCE(t.valeur_pour_eur, 1)` : une devise étrangère sans taux de change s'affichait **à son montant
nominal, en euros**. Le commentaire de la vue le présentait comme une qualité (« une devise sans taux reste à son
montant nominal »). C'était la bonne réponse à la mauvaise question : ne pas faire disparaître la ligne, oui ;
afficher 200 € pour 10 titres à 20 USD, non. La règle du chapitre : taux absent, **« indisponible »**.

**État mesuré avant le changement (03/10, base du poste)** : 7 positions, toutes en EUR ; 30 taux par devise
(CHF, EUR, GBP, JPY, USD), dernier le 02/10 ; aucune valorisation nulle. Le défaut était **latent** : il se serait
déclenché sur une base neuve avant la première collecte BCE, sur une devise non publiée par la BCE, ou après
plusieurs échecs de l'étape `ecb` (elle a rendu « USD : ReadTimeout » en simulation le 03/10 à 11 h 50). Le jeu
de démonstration, lui, contient deux positions en USD (AAPL, MSFT).

## 2. La règle nouvelle, dans les trois copies du SQL

```sql
ROUND(p.quantite * p.pru     / CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END, 2) AS investi_eur,
ROUND(p.quantite * d.cloture / CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END, 2) AS valorisation_eur,
ROUND((d.cloture - p.pru) / p.pru * 100, 2)                                                    AS performance_pct,
CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END                                   AS taux_pour_eur,
(p.devise <> 'EUR' AND t.valeur_pour_eur IS NULL)                                               AS taux_manquant
```

- L'euro se convertit par 1 **sans lire `taux_change`** : la vue ne dépend plus de la ligne « EUR = 1 » que
  l'étape `ecb` insère chaque soir.
- Une devise étrangère sans taux rend `NULL` et `taux_manquant` vrai ; la ligne reste visible (les deux `LEFT JOIN`
  n'ont pas changé).
- `performance_pct` ne change pas : il compare PRU et cours dans la devise de la position (le cas D07, devise du
  PRU différente de celle du cours, est l'issue #69).
- Les deux colonnes nouvelles sont **en fin de liste** : `CREATE OR REPLACE VIEW` les accepte sans `DROP VIEW`.

Les trois copies (vue, R1, `SQL_PORTEFEUILLE`) sont tenues alignées par un test de contrat qui compare les
expressions de calcul mot pour mot (`tests/test_vue_valorisation.py::test_les_trois_copies_calculent_exactement_la_meme_chose`).

## 3. Ce qui consomme la vue

| Consommateur | Après (décisions d'Era) |
|---|---|
| `GET /donnees/portefeuille` | `total_eur` **null** dès qu'une position est sans taux, plus `positions_sans_taux` (D1 = A) ; chaque position porte `taux_manquant` |
| `GET /donnees/indicateurs-portefeuille` | si une valorisation manque, `poids_pct` et `exposition_pct` sont null **pour toutes les lignes**, `total_eur` null, `complet: false` (D2 = A) ; `BOOL_OR(taux_manquant)` dans `db/indicateurs_portefeuille.sql` |
| Écran portefeuille | « indisponible » dans les cellules concernées avec la raison au survol ; total « indisponible (1 position sans taux de change) » ; jamais « 0,00 € » |
| Script `python -m indicateurs.portefeuille` | affiche « indisponible » et « n/d » au lieu de planter sur un `None` |
| Outil MCP `rita_portefeuille` | inchangé : il passe la réponse de l'API |

Trois copies gardées (D3 = A) : R1 est une pièce du rapport E1, `SQL_PORTEFEUILLE` est l'extraction C2 lue par l'API.

## 4. Les tests, écrits avant le code

23 tests rouges au premier passage, tous pour la bonne raison (COALESCE présent, colonne absente, fonctions
absentes, « 0,00 € » à l'écran) ; 160 passed après, sur les six fichiers touchés :

| Fichier | Ce qu'il prouve |
|---|---|
| `tests/test_vue_valorisation.py` | contrat sur les trois copies (pas de `COALESCE(…, 1)`, le `CASE` sur `'EUR'`, `taux_manquant`, mêmes expressions) ; poids et exposition disent `complet` ; **base réelle, transaction annulée** : devise sans taux → montants `NULL`, ligne visible, `taux_manquant` vrai ; position EUR valorisée même sans aucun taux ; 10 titres à 20 USD à 1,25 → 160 EUR |
| `tests/test_database.py` | l'ancienne assertion « `COALESCE` présent » inversée, avec le pourquoi dans la docstring |
| `tests/test_api_donnees.py` | total null + `positions_sans_taux` ; somme gardée sans manque ; `complet: false` et poids null |
| `tests/test_indicateurs_portefeuille.py` | `lire_poids_detail()` transmet `complet` et des poids null sans recalculer ; l'ancienne signature `lire_poids()` reste servie |
| `tests/test_frontend.py` | le code traite `taux_manquant`, écrit « indisponible » et `positions_sans_taux` |
| `tests/test_smoke_ui.py` | **vrai navigateur**, API interceptée (la base réelle n'a aucune position sans taux) : la ligne AAPL affiche « indisponible » deux fois, jamais « 0,00 », le total dit « 1 position », aucune erreur JavaScript |

Les tests sur la base réelle écrivent dans une transaction puis `ROLLBACK` : la base de production ne bouge pas
(règle INC-006). Ils se sautent sans `DATABASE_URL` ; la CI n'a pas de PostgreSQL, ils tournent sur le poste.

## 5. La migration, jouée sur le poste le 03/10

`db/migration-2026-10-03-vue-valorisation-taux.sql` : `CREATE OR REPLACE VIEW` généré depuis `db/schema.sql`
(même texte), rejouable. Sortie réelle après exécution :

```
apres migration : [(False, 7)]
colonnes : ['ticker', 'nom_officiel', 'statut_qualite', 'quantite', 'pru', 'devise', 'date_cours', 'cours',
            'investi_eur', 'valorisation_eur', 'performance_pct', 'taux_pour_eur', 'taux_manquant']
exemple : [('AI.PA', Decimal('6806.40'), Decimal('1')), ('BNP.PA', Decimal('1380.90'), Decimal('1')), ('MC.PA', Decimal('4542.60'), Decimal('1'))]
```

Sept positions, aucune sans taux, `taux_pour_eur = 1` pour l'euro : les chiffres affichés n'ont pas bougé d'un
centime, seul le cas absent change de comportement.

**Joué le 03/10 après-midi sur les deux autres environnements** (sorties réelles) :

```
Compose (rita-postgres-preprod, poste) : migration-2026-09-27 ok · roles.sql ok · vue ok · mcp_calls ok
tables=11 | colonnes_vue=13 | mcp_calls | macro_observation | rita_lecture lit=t ecrit=f
```

```
Hetzner (rita-postgres-preprod, /root/rita-agent, code deploye 1cefdae du 20/08) : 4 fichiers copies, 4 ok
tables=11 | positions=7 | cotations=275118 | colonnes_vue=13 | mcp_calls | macro_observation | role_lecture=1
taux_manquant : f|7 · rita_lecture lit=t ecrit=f · API /health toujours 200 pendant et apres
taux_change : derniere date 2026-08-17 pour les 5 devises (la copie du serveur est figee depuis le 17/08)
```

Sur le serveur, le **code** reste celui du 20/08 (`1cefdae`) : la vue a ses colonnes, mais l'API déployée ne lit pas encore
`taux_manquant`. La mise à jour du code du serveur est un déploiement, pas une migration : à faire après le gel du 15/10.

## 6. Limites dites franchement

- Un test de contrat prouve la règle écrite, pas son exécution : c'est le test sur la base réelle qui prouve
  l'exécution, et il ne tourne que sur le poste.
- Le rapport E1 envoyé le 13/08 montre une sortie de R1 avec l'ancienne règle ; la v2 du 15/10 le dira en une
  phrase plutôt que de réécrire la sortie.
- Trois copies du même SQL restent : le test de contrat les tient alignées, pas la discipline.

## 📖 Glossaire

- **`COALESCE(a, b)`** : la première valeur non nulle ; ici, 1 quand le taux manquait.
- **`CREATE OR REPLACE VIEW`** : remplace la définition d'une vue sans la supprimer ; n'accepte que des colonnes ajoutées à la fin.
- **`BOOL_OR`** : vrai si au moins une ligne du groupe est vraie ; ici, « au moins une position sans taux ».
- **Transaction annulée** : `BEGIN` puis `ROLLBACK` ; tout ce qui a été écrit entre les deux disparaît.

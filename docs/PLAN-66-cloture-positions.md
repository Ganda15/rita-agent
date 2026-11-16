# Plan : la clôture des positions et une purge qui s'exécute vraiment (issue #66, C4 et RGPD, chapitre « Données » §1.5)

> **Établi le 03/10/2026**, après #65 et #62. **Zone sous garde** (`db/schema.sql`), **import** (`db/importer.py`,
> seule écriture en base avec le pipeline) et **registre RGPD** (T1) : ce plan est relu et validé par Era **avant**
> toute ligne de code. Rien de ce qui suit n'était fait le 03/10 (statut au 16/11 : issue #66 fermée le 03/10 ; plan gardé tel qu'écrit). Quatre décisions en section 7.

## 1. Le défaut, mesuré

| Ce que le registre promet (T1) | Ce que le code fait |
|---|---|
| position **soldée** : conservée 3 ans « utile aux comparaisons de performance », puis supprimée | la base **ne sait pas** qu'une position est soldée : aucune colonne de clôture ; `quantite > 0` est une contrainte ; P2 cherche `quantite = 0`, donc ne trouve jamais rien |
| le fichier CSV est « la source de vérité du portefeuille » | une vente, c'est une ligne qui **disparaît du CSV** ; la ligne en base, elle, reste à jamais et continue d'être valorisée dans le briefing comme si elle était détenue |
| | `importer_positions()` fait un `INSERT` sans clé ni `ON CONFLICT` : **un second import duplique tout le portefeuille**. Mesuré le 03/10 : 7 lignes, 7 clés distinctes, un seul jour d'import (16/08). Le défaut est latent parce que l'import n'a tourné qu'une fois |

Le chapitre (§1.5, version complète §1.6) : « le schéma n'a pas de date de clôture ; la procédure sélectionne
`quantite = 0`, interdite par le schéma ; elle ne démontre pas une purge trois ans après la vente. Le cycle de clôture
reste à concevoir ». Les tests actuels de P2 **figent le défaut** (`"QUANTITE = 0" in requête`).

## 2. La règle cible : le cycle de vie d'une position

```
CSV (ligne présente)  ──import──▶  position active (date_cloture IS NULL)
CSV (ligne absente)   ──import──▶  position close  (date_cloture = jour de l'import)
ligne qui réapparaît  ──import──▶  la même ligne redevient active (date_cloture remise à NULL)
date_cloture < aujourd'hui - 3 ans ──P2──▶ suppression
```

Trois règles :

1. **Une position n'est jamais supprimée par l'import** : elle est **close**, datée du jour où le CSV ne la porte
   plus. C'est la seule date de vente que le projet connaisse ; le CSV n'en a pas.
2. **Une position close ne se valorise plus** : elle sort de la vue, de R1, de l'extraction de l'API, des poids, de
   l'exposition, du compte `nb_positions` de la fraîcheur. Elle reste en base trois ans, lisible par une requête
   dédiée pour la comparaison de performance que le registre invoque.
3. **La purge P2 vise `date_cloture`**, plus `quantite`.

## 3. Le schéma

```sql
ALTER TABLE position
    ADD COLUMN date_cloture DATE,                                  -- NULL = détenue
    ADD CONSTRAINT cloture_apres_achat
        CHECK (date_cloture IS NULL OR date_achat IS NULL OR date_cloture >= date_achat);

-- la clé métier d'une ligne de portefeuille : ce que le CSV identifie
CREATE UNIQUE INDEX uq_position_ligne ON position (ticker, pru, COALESCE(date_achat, DATE '1900-01-01'));
COMMENT ON COLUMN position.date_cloture IS 'NULL tant que la ligne est dans le CSV ; posee par l import le jour ou elle en disparait ; purge P2 trois ans apres (T1).';
```

- `quantite > 0` reste : la quantité d'une position close est celle qu'on détenait, pas zéro.
- L'index unique porte sur `(ticker, pru, date_achat)` : c'est ce qui distingue deux achats du même titre. `COALESCE`
  parce que `date_achat` peut manquer et que deux `NULL` ne sont pas égaux pour un index. **P3** (détection des
  doublons, « même ticker, même date, même PRU ») devient sans objet : la base les refuse ; P3 est retirée du script
  et du registre, avec la date.
- Migration rejouable : `ADD COLUMN IF NOT EXISTS`, `CREATE UNIQUE INDEX IF NOT EXISTS`, contrainte ajoutée dans un
  bloc `DO` qui vérifie son absence. Elle échouerait sur une base qui contient déjà des doublons : la migration
  commence par les compter et s'arrête s'il y en a (aucun le 03/10 sur le poste).

## 4. L'import devient une réconciliation

`importer_positions()` lit le CSV comme aujourd'hui (alias résolus, lignes corrompues rejetées), puis, **dans la même
transaction** :

| Étape | SQL | Pourquoi |
|---|---|---|
| 1. upsert des lignes présentes | `INSERT ... ON CONFLICT (ticker, pru, COALESCE(date_achat, ...)) DO UPDATE SET quantite = EXCLUDED.quantite, devise = EXCLUDED.devise, date_cloture = NULL, importe_le = now()` | une ligne modifiée (quantité) se met à jour ; une ligne revenue se rouvre ; rien ne se duplique |
| 2. clôture des absentes | `UPDATE position SET date_cloture = CURRENT_DATE WHERE date_cloture IS NULL AND (ticker, pru, COALESCE(date_achat, ...)) NOT IN (lignes du CSV)` | la vente est datée du jour où on la constate |
| 3. bilan | nombre de lignes insérées, mises à jour, closes, rouvertes | affiché par `python -m db.importer`, et dans le manifeste si l'import entre un jour dans le pipeline |

**Garde-fou contre un CSV vide ou illisible** : si le CSV ne donne **aucune** ligne valide, l'import **ne clôt rien**
et le dit (un fichier déplacé ou corrompu ne doit pas « vendre » tout le portefeuille). Si le CSV donne moins de la
moitié des positions actives, l'import clôt quand même mais écrit un WARNING explicite : c'est peut-être une vente
massive, c'est peut-être une erreur de fichier, et seul Era le sait.

## 5. Ce qui consomme la table

| Consommateur | Après |
|---|---|
| vue `v_portefeuille_valorise`, R1 (`db/requetes.sql`), `SQL_PORTEFEUILLE` (`sources/database.py`) | `WHERE p.date_cloture IS NULL` ; le test de contrat de #65 qui compare les trois copies s'étend à ce filtre |
| poids et exposition | lisent la vue : rien à changer |
| `db/fraicheur.sql` : `nb_positions` | `WHERE date_cloture IS NULL` |
| `GET /donnees/portefeuille` | positions actives seulement ; `nb` = actives ; nouveau champ `positions_closes` (le nombre, pas les lignes) |
| positions closes | **une seule porte** : requête R1 bis dans `db/requetes.sql` (`date_cloture IS NOT NULL`, PRU, dates, devise ; jamais exposée par l'API ni par MCP : décision D3) |
| P2 | `DELETE FROM position WHERE date_cloture IS NOT NULL AND date_cloture < CURRENT_DATE - INTERVAL '3 years'` |
| registre T1 | « position soldée : 3 ans après la **date de clôture**, posée par l'import le jour où la ligne quitte le CSV » ; P2 passe de « script prêt mais inapplicable » à « applicable » ; P3 retirée (index unique) ; mention qu'une ligne retirée du CSV **est** l'acte de vente, et qu'un CSV vide ne vend rien |
| rapport E1 v2 | une phrase dans la section RGPD (le mécanisme de fin de conservation existe) et une dans la section import |

## 6. Les tests, écrits avant le code

| # | Test | Fichier | Rouge d'abord ? |
|---|---|---|---|
| 1 | contrat sur `db/schema.sql` : colonne `date_cloture`, contrainte `cloture_apres_achat`, index unique `uq_position_ligne`, commentaire ; migration rejouable qui compte les doublons avant d'agir | `tests/test_schema.py` | oui |
| 2 | les quatre copies du SQL filtrent `date_cloture IS NULL` (vue, R1, `SQL_PORTEFEUILLE`, `fraicheur.sql`) ; R1 bis existe et ne sort que les closes | `tests/test_vue_valorisation.py`, `tests/test_database.py` | oui |
| 3 | import, connexion simulée : une ligne présente est upsertée (`ON CONFLICT`, `date_cloture = NULL`) ; une ligne absente est close par un `UPDATE` daté ; un CSV sans ligne valide ne clôt rien et le dit ; moins de la moitié des actives : clôture + WARNING ; le bilan compte insérées, mises à jour, closes, rouvertes | `tests/test_importer.py` | oui |
| 4 | P2 : vise `date_cloture`, jamais `quantite` ; 3 ans depuis la constante ; simulation sans `DELETE` ; les trois tests actuels de P2 réécrits (celui qui exige `QUANTITE = 0` devient faux par construction) ; P3 absente de l'orchestration | `tests/test_rgpd_purge.py` | oui |
| 5 | API : `positions_closes` dans la réponse ; une ligne close ne sort pas | `tests/test_api_donnees.py` | oui |
| 6 | base réelle, transaction annulée : insérer une position, la clore par la réconciliation (CSV simulé sans elle), vérifier qu'elle sort de la vue et reste en table ; la rouvrir ; tenter un doublon et voir l'index le refuser ; P2 à blanc sur une clôture vieille de 4 ans | `tests/test_cloture_positions_base.py` (nouveau) | oui |
| 7 | registre : T1 cite `date_cloture` et « ligne retirée du CSV » ; P3 n'est plus listée comme procédure vivante | `tests/test_rgpd_registre.py` | oui |

Règle INC-006 : le test 6 ne commit jamais. Les tests d'import simulent `lire()` et le curseur, comme aujourd'hui.

## 7. Quatre décisions pour Era

| # | Question | Option A (recommandée) | Option B |
|---|---|---|---|
| D1 | La clé d'une ligne de portefeuille | **(ticker, PRU, date d'achat)** : deux achats du même titre à des prix différents restent deux lignes, comme dans le CSV | (ticker) seul : une ligne par titre, les achats fusionnés ; plus simple, mais le CSV d'exemple a déjà deux achats possibles sur un ticker (schéma MCD : VALEUR 1 à 0,n POSITION) |
| D2 | Une ligne qui réapparaît après clôture | **rouvrir la même ligne** (`date_cloture = NULL`) : une erreur de fichier se corrige sans trace fantôme | créer une nouvelle ligne : l'historique garde la « vente » ; mais une simple erreur de CSV fabrique une vente et un rachat |
| D3 | Qui voit les positions closes | **personne par l'API ni par MCP** ; une requête R1 bis dans `db/requetes.sql` pour le propriétaire (la « comparaison de performance » du registre se fait en SQL, pas à l'écran) | une route `GET /donnees/positions-closes` protégée par la clé |
| D4 | Le garde-fou contre un CSV vide | **ne rien clore et le dire** (un fichier déplacé ne vend pas un portefeuille) | clore quand même : le CSV est la vérité, point |

## 8. L'ordre des opérations

1. Era valide et tranche D1 à D4.
2. Tests 1 à 7 écrits, lancés, vus rouges.
3. Schéma, migration rejouable (avec le comptage des doublons en tête), les quatre copies du SQL, R1 bis.
4. Import : réconciliation, garde-fous, bilan.
5. P2 réécrite, P3 retirée, registre T1 et §2, `docs/EXPLOITATION.md` (migration ; « retirer une ligne du CSV, c'est
   vendre ; relancer l'import ; vérifier `positions_closes` »), rapport E1 v2 (deux phrases).
6. Migration jouée sur le poste, puis `python -m db.importer` sur le CSV réel : attendu 7 mises à jour, 0 insérée,
   0 close (le CSV n'a pas changé) ; sortie collée dans `evidence/C4/preuve-cloture-positions.md`. Compose et Hetzner
   ensuite, avec les deux migrations du 03/10 déjà en attente.
7. Ledger, `CHANGELOG`, `docs/conception/donnees/README.md`, commit `Closes #66`.

Estimation : 3 h, une vingtaine de tests. Touche `db/schema.sql`, `db/importer.py`, le registre ; ni `guardrails/` ni `evals/`.

## 9. Risques, dits franchement

- **La date de clôture est la date de l'import, pas celle de la vente.** Le CSV ne porte pas de date de vente ; si Era
  relance l'import un mois après avoir vendu, la position est close un mois trop tard, et purgée un mois trop tard.
  C'est dit dans le registre ; une colonne « date de vente » dans le CSV serait la vraie correction, hors périmètre.
- Un CSV **partiel** par erreur clôt des positions détenues ; elles se rouvrent au prochain import correct (D2 = A),
  sans perte, mais entre-temps le briefing ne les valorise pas. D'où le WARNING « moins de la moitié ».
- Quatre copies du SQL à filtrer : le test de contrat les tient.
- L'import n'a tourné qu'une fois depuis le 16/08 : la première exécution réelle de la réconciliation sera aussi son
  premier test grandeur nature ; c'est pour ça que l'étape 6 attend « 7 mises à jour, 0 close » avant d'aller plus loin.

## 📖 Glossaire

- **Position close** : ligne de portefeuille que le CSV ne porte plus ; conservée trois ans, jamais valorisée.
- **Réconciliation** : comparer ce que dit la source (le CSV) et ce que contient la base, et faire le minimum pour les aligner.
- **Upsert (`ON CONFLICT DO UPDATE`)** : insérer, ou mettre à jour si la clé existe déjà.
- **Index unique** : la base elle-même refuse deux lignes de même clé ; une règle que le code ne peut pas oublier.
- **Transaction annulée** : `BEGIN` puis `ROLLBACK` ; les tests sur la base réelle n'y laissent rien.

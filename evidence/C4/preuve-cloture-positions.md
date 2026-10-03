# Preuve C4 et C2 : la clôture des positions existe, l'import la pose, la purge s'applique (03/10/2026)

> Issue #66 (et #69 pour le cas D07), §1.5 du chapitre « Données » validé par le formateur le 03/10/2026. Plan relu et
> validé par Era le 03/10 avec les décisions D1 à D4 = A : `docs/PLAN-66-cloture-positions.md`.
> Zone sous garde (`db/schema.sql`) : rien n'a été écrit avant la validation du plan. Tests écrits avant le code.

## 1. Ce qui manquait, et pourquoi c'était grave

Le registre RGPD promettait « position soldée : 3 ans, puis suppression ». Mais la table `position` n'avait aucune date de
vente, et la procédure P2 cherchait `quantite = 0`, une valeur que la contrainte `quantite_positive` interdit. P2 ne
trouvait donc jamais rien, et la promesse du registre n'était tenue par aucun mécanisme. Deuxième défaut, découvert en
écrivant le plan : l'import insérait toutes les lignes du CSV à chaque exécution, sans clé de ligne. Lancé deux fois, il
doublait le portefeuille.

## 2. La règle nouvelle

| Décision | Ce que ça veut dire | Où |
|---|---|---|
| D1 = A | une ligne de portefeuille est identifiée par (ticker, PRU, date d'achat) ; la base refuse la même ligne deux fois | `db/schema.sql`, index `uq_position_ligne` |
| D2 = A | une ligne retirée du CSV est **close** à la date du jour, jamais supprimée ; une ligne revenue rouvre la même ligne | `db/importer.py`, `importer_positions` |
| D3 = A | les positions closes ne sortent ni par l'API ni par MCP ; une requête R1 bis les sert au propriétaire | `db/requetes.sql`, `sources/database.py` |
| D4 = A | un CSV vide ou illisible ne clôt rien et le dit ; moins de la moitié des actives clôt mais avertit | `db/importer.py` |
| D07 (#69, option a) | un PRU dans une autre devise que celle du cours est importé et signalé par un WARNING | `db/importer.py` |

Dans le schéma :

```sql
date_cloture   DATE,
CONSTRAINT cloture_apres_achat CHECK (date_cloture IS NULL OR date_achat IS NULL OR date_cloture >= date_achat)
...
CREATE UNIQUE INDEX uq_position_ligne ON position (ticker, pru, COALESCE(date_achat, DATE '1900-01-01'));
```

La vue `v_portefeuille_valorise`, la requête R1 et l'extraction de l'API filtrent `WHERE p.date_cloture IS NULL`.
`db/fraicheur.sql` ne compte que les positions détenues. P2 purge `WHERE date_cloture IS NOT NULL AND date_cloture <
CURRENT_DATE - INTERVAL '3 years'`. P3 (détection de doublons) est retirée : la base les refuse à l'écriture.

## 3. Les tests, écrits avant

| Fichier | Ce qu'il prouve |
|---|---|
| `tests/test_schema.py` | `date_cloture` nullable et postérieure à l'achat ; index unique de ligne ; commentaire ; migration rejouable qui refuse d'agir sur des doublons |
| `tests/test_vue_valorisation.py` | chaque copie du SQL filtre les closes ; la fraîcheur ne compte que les détenues ; R1 bis sert les closes sans taux à 1 |
| `tests/test_importer.py` | upsert sur la clé, réouverture, clôture datée sans jamais supprimer, CSV vide, fichier partiel, D07 |
| `tests/test_rgpd_purge.py` | P2 vise `date_cloture`, pas `quantite` ; P3 n'existe plus |
| `tests/test_rgpd_registre.py` | T1 dit comment une position devient soldée ; P2 applicable, P3 retirée |
| `tests/test_api_donnees.py` | `/donnees/portefeuille` compte les closes (`positions_closes`) sans les servir |
| `tests/test_cloture_positions_base.py` | **base réelle, transaction annulée** : la base refuse la même ligne deux fois ; une close sort de la vue et reste en table ; la clôture ne précède pas l'achat ; P2 ne purge qu'au-delà de trois ans |

Sortie mesurée le 03/10 au soir :

```
C:\Python314\python.exe -X utf8 -m pytest tests\test_schema.py tests\test_vue_valorisation.py tests\test_rgpd_purge.py tests\test_rgpd_registre.py tests\test_api_donnees.py tests\test_importer.py tests\test_cloture_positions_base.py tests\test_database.py -q
146 passed, 1 warning in 5.38s

C:\Python314\python.exe -X utf8 -m pytest --cov -q
TOTAL                            1838    112    94%
Required test coverage of 90.0% reached. Total coverage: 93.91%
738 passed, 2 xfailed, 4 warnings in 68.36s (0:01:08)
```

## 4. La migration, jouée sur les trois bases

Fichier rejouable : `db/migration-2026-10-03-cloture-positions.sql`. Elle compte d'abord les doublons de ligne et
s'arrête (`RAISE EXCEPTION`) s'il y en a, pose la colonne et la contrainte si elles manquent, pose l'index unique
`IF NOT EXISTS`, puis recrée la vue.

| Base | Commande | Après |
|---|---|---|
| Poste (PostgreSQL 18, port 5433) | `psql -U rita -d rita -p 5433 -v ON_ERROR_STOP=1 -f db\migration-2026-10-03-cloture-positions.sql` | 7 actives sur 7 ; index `idx_position_ticker`, `position_pkey`, `uq_position_ligne` ; contrainte `cloture_apres_achat` ; vue à 13 colonnes |
| Compose (`rita-postgres-preprod` sur le poste) | `docker compose exec -T postgres psql -U rita -d rita -v ON_ERROR_STOP=1 -q < db\migration-2026-10-03-cloture-positions.sql` | `0|0` (cette base n'a jamais reçu le CSV du portefeuille, données de marché seulement) ; index `uq_position_ligne` présent |
| Hetzner (`/root/migrations-2026-10-03/`, `docker exec -i rita-postgres-preprod psql -U rita -d rita`) | même fichier, copié par `scp` | `7|7` ; index `uq_position_ligne` présent ; `/health` → `{"status":"ok","project":"RITA"}` |

## 5. L'import réel rejoué sur le poste : la réconciliation ne touche à rien qu'elle ne doive

Attendu par le plan : 7 mises à jour, 0 insérée, 0 close (le CSV porte les mêmes 7 positions que la base).

```
WARNING 2 ligne(s) rejetee(s) sur 12
WARNING 3 position(s) sans valeur correspondante : ['TTE.PA', 'AAPL', 'MSFT']
avant : (7, 7, datetime.datetime(2026, 8, 16, 22, 33, 56))
bilan reconciliation : {'lignes': 7, 'inserees': 0, 'mises_a_jour': 7, 'rouvertes': 0, 'closes': 0,
                        'ignorees': 3, 'devises_differentes': 0, 'avertissement': None}
apres : (7, 7, datetime.datetime(2026, 10, 3, 14, 5))
positions : AI.PA, BNP.PA, MC.PA, OR.PA, SAN.PA, SU.PA, VIRI.PA, toutes avec date_cloture = None
commit fait
```

Lecture : le CSV compte 12 lignes, 2 sont rejetées par le lecteur (format), 3 n'ont pas de valeur dans la base
(TTE.PA, AAPL, MSFT : lignes d'exemple), 7 sont rapprochées de leur ligne existante et mises à jour (`importe_le` passe
du 16/08 au 03/10). Aucune insertion, aucune clôture, aucune devise différente. Avant le plan 66, cette même commande
aurait créé 7 doublons.

## 6. Ce que ça ne règle pas, dit franchement

- La date de clôture est **la date de l'import**, pas la date de la vente : le projet ne connaît pas l'autre. Le registre
  le dit (T1). Le délai entre la vente et l'import suivant retarde d'autant la purge P2.
- P2 reste à lancer à la main (`python -m db.rgpd_purge --appliquer`) : aucune planification mensuelle n'existe.
- Le serveur Hetzner a la migration mais pas le code : il tourne encore sur `1cefdae` du 20/08 et ses données sont figées
  au 17/08. Le code sera déployé après le gel du 15/10 (décision du 03/10).
- Les 3 positions sans valeur correspondante (TTE.PA, AAPL, MSFT) sont ignorées à chaque import et signalées, comme avant.

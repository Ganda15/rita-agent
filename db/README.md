# Base de données RITA — procédure d'installation et de vérification

**Compétence C4** — critère : *« La reproduction des procédures d'installation décrites
(base de données et API) a pour résultat un système conforme aux objets techniques
attendus. »*

Ce document doit permettre à **un tiers** — le jury — de reconstruire la base à
l'identique. Toutes les commandes ci-dessous ont été exécutées le 31/07/2026.

**Décision D15 (31/07/2026)** : PostgreSQL directement, pas d'étape SQLite intermédiaire.

---

## 1. Prérequis

| Élément | Version testée |
|---|---|
| PostgreSQL | **18.4** (le schéma cible 17+) |
| Python | 3.14 |
| `psycopg2-binary` | 2.9.12 |
| Docker Desktop *(voie A)* | 29.4.0 |

---

## 2. Voie A — Docker Compose (recommandée)

```powershell
Set-Location "D:\KandaWork\RITA_PROJECT\rita-agent"
docker compose -f db/docker-compose.yml up -d
```

Le schéma `db/schema.sql` est joué **automatiquement à la première création du volume**
(mécanisme `/docker-entrypoint-initdb.d`). Il ne l'est plus ensuite.

```powershell
# Vérifier que la base accepte les connexions (le healthcheck fait la même chose)
docker exec rita-postgres pg_isready -U rita -d rita

# Remise à zéro complète (⚠️ efface les données)
docker compose -f db/docker-compose.yml down -v
```

DSN : `postgresql://rita:rita_dev_local@localhost:5432/rita`

> Le mot de passe de `docker-compose.yml` est **de développement local uniquement**. En
> production il vient du gestionnaire de secrets de l'hébergeur, jamais d'un fichier
> versionné.

---

## 3. Voie B — PostgreSQL déjà installé

Si un serveur tourne déjà (cas de la machine de développement : **PostgreSQL 18 sur le
port 5433**) :

```powershell
$env:PGPASSWORD = "<mot de passe postgres>"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5433 -U postgres `
    -c "CREATE DATABASE rita;"
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -h localhost -p 5433 -U postgres `
    -d rita -v ON_ERROR_STOP=1 -f db/schema.sql
```

`-v ON_ERROR_STOP=1` est important : sans lui, `psql` continue après une erreur et laisse
une base **à moitié créée** en indiquant « succès ».

---

## 4. Import des données

⚠️ **Le DSN dépend de la voie choisie au §2 ou §3.** Les deux ne diffèrent pas seulement par
le port : l'utilisateur n'est pas le même non plus.

| Voie suivie | DSN à utiliser |
|---|---|
| **A — Docker** (§2) | `postgresql://rita:rita_dev_local@localhost:5432/rita` |
| **B — PostgreSQL installé** (§3) | `postgresql://postgres:<mot de passe>@localhost:**5433**/rita` |

> **Corrigé le 2026-08-03.** Cette page ne donnait que le DSN de la voie A. En suivant la
> voie B puis ce paragraphe, on obtient `connection refused ... port 5432` — le serveur
> écoute sur 5433 et l'utilisateur `rita` n'existe pas. Vérifier le port réel :
> `Get-NetTCPConnection -State Listen -LocalPort 5432,5433`

**Le plus simple : mettre le DSN dans `.env`**, une fois pour toutes. Le pipeline et la tâche
planifiée le liront automatiquement — une variable de terminal, elle, disparaît à la fermeture
et n'est pas visible du Planificateur Windows.

```
# dans .env, à la racine du dépôt (jamais versionné)
DATABASE_URL=postgresql://postgres:<mot de passe>@localhost:5433/rita
```

```powershell
C:\Python314\python.exe -X utf8 -m db.importer

# ou en passant le DSN explicitement, sans .env :
C:\Python314\python.exe -X utf8 -m db.importer --dsn "postgresql://..." --limite-annees 3
```

### Sortie réelle du 31/07/2026

```
=== IMPORT POSTGRESQL ===
Valeurs            : 111
Alias portefeuille : 112   (> valeurs = cas CGG resolu)
Cotations lues     : 276,168
  dedoublonnees    : 2,560
  inserees         : 273,608
Positions          : 7
```

**Les 2 560 lignes dédoublonnées correspondent exactement** au constat de l'analyse
exploratoire (`evidence/C1/preuve-09-analyse-exploratoire.md`). L'import applique la règle,
il ne la découvre pas.

Prérequis : le jeu Parquet doit exister. Sinon :
`C:\Python314\python.exe -m bigdata.build_parquet` (~32 s).

---

## 5. Vérification de conformité

```sql
SELECT count(*) FROM information_schema.tables
  WHERE table_schema='public' AND table_type='BASE TABLE';   -- attendu : 7
SELECT count(*) FROM information_schema.views  WHERE table_schema='public';  -- 1
SELECT count(*) FROM pg_indexes                WHERE schemaname='public';   -- 14
```

| Objet | Attendu | Obtenu le 31/07 |
|---|---|---|
| Tables | 7 | ✅ 7 |
| Vues | 1 | ✅ 1 |
| Index | 14 | ✅ 14 |
| Contraintes `CHECK` | 9 | ✅ 9 |

### Les garde-fous refusent-ils vraiment les données incohérentes ?

Six insertions invalides testées, **six refusées**, base inchangée :

```
OK  refuse : cloture negative       « prix_positifs »
OK  refuse : haut < bas             « bornes_coherentes »
OK  refuse : volume negatif         « volume_positif »
OK  refuse : quantite nulle         « quantite_positive »
OK  refuse : pru nul                « pru_positif »
OK  refuse : ticker inexistant      « valeur »  (clé étrangère)
lignes avant=4 apres=4
```

### Le doublon CGG est-il bien rejeté ?

```
INSERT INTO cotation VALUES ('MC.PA','2026-07-28', ...);   -- doublon volontaire
ERREUR : la valeur d'une clé dupliquée rompt la contrainte unique « cotation_pkey »
DÉTAIL : La clé « (ticker, date_seance)=(MC.PA, 2026-07-28) » existe déjà.
```

C'est le point central : **ce qui passait silencieusement dans le Parquet est désormais
impossible en base.**

---

## 6. Les index sont-ils justifiés ? (exigence Règlement p. 53)

`EXPLAIN ANALYZE` sur les **273 608 lignes réelles**, pas sur un jeu de test :

| Requête du briefing | Plan retenu | Verdict |
|---|---|---|
| Q1 — dernier cours d'une valeur | `Index Scan Backward using cotation_pkey` (4 buffers) | ✅ PK |
| Q3 — variations d'une séance | `Index Scan using idx_cotation_date` (106 lignes) | ✅ index dédié |
| Q4 — historique 1 an | `Bitmap Index Scan on cotation_pkey` (4 buffers) | ✅ PK |

### 🔍 Un index a été supprimé après mesure

La première version créait `idx_cotation_ticker_date (ticker, date_seance DESC)`, en
supposant qu'il servirait Q1 et Q4. **Le planificateur ne l'utilisait pas.**

```
pg_stat_user_indexes :
  cotation_pkey            273 609 scans
  idx_cotation_date              2 scans
  idx_cotation_ticker_date       1 scan     <- inutile
```

Après suppression, Q4 utilise `cotation_pkey` avec **exactement les mêmes 4 buffers**. La
clé primaire `(ticker, date_seance)` couvrait déjà le besoin — PostgreSQL sait parcourir un
index à l'envers, le `DESC` explicite n'apportait rien.

**L'index redondant coûtait 9 Mo et ralentissait chaque `INSERT` pour rien.**

> C'est exactement ce que veut dire « conception orientée requêtes » : on mesure le plan
> d'exécution, on ne suppose pas ce qui sera utile.

---

## 7. Ce que le schéma doit à l'analyse exploratoire

Aucune de ces décisions ne vient d'une intuition de modélisation :

| Constat mesuré | Décision de schéma |
|---|---|
| 2 560 doublons sur `(ticker, date)` | table `alias_valeur` — le nom sort de la cotation |
| 111 tickers / 112 noms | un ticker peut porter plusieurs libellés de portefeuille |
| 0 valeur manquante / 276 168 lignes | colonnes OHLCV en `NOT NULL` |
| 2 tickers aberrants | colonne `statut_qualite` — exclure **sans supprimer** |
| Historiques de 286 à 2 560 séances | `premiere_cotation` / `derniere_cotation` (biais de survie) |

---

## 8. ⚠️ Données personnelles et RGPD

La table `position` contient la **situation financière de l'utilisateur** (quantités, prix
de revient). **4 traitements sont recensés** dans
[`RGPD-registre-des-traitements.md`](RGPD-registre-des-traitements.md) — article 30 du RGPD.

Les procédures de tri automatisables sont **exécutables** :

```powershell
C:\Python314\python.exe -X utf8 -m db.rgpd_purge                 # simulation (defaut)
C:\Python314\python.exe -X utf8 -m db.rgpd_purge --appliquer     # execution reelle
```

Vérification du 01/08/2026 sur jeu d'essai (5 lignes d'audit, dont 3 de plus de 90 jours) :

```
SIMULATION  : 3 lignes « seraient supprimees »  -> memory_audit = 5 (inchange)
EXECUTION   : 3 lignes supprimees               -> memory_audit = 2 (les recentes)
P3 doublons : MC.PA du 2023-04-18 signale       -> positions = 8 (inchange, arbitrage humain)
```

**Le mode par défaut est la simulation.** Une purge déclenchée par accident est une perte de
données irréversible : le comportement par défaut doit être inoffensif. Testé
(`tests/test_rgpd_purge.py`, 11 tests).

Le fichier source n'est jamais versionné : voir `.gitignore` et
`evidence/C1/preuve-06-positions-csv.md`.

---

## 9. Reste à faire

| Élément | Compétence | État |
|---|---|---|
| Registre des traitements RGPD + procédures de tri | C4 | ✅ `RGPD-registre-des-traitements.md` + `rgpd_purge.py` |
| MCD Merise (modèle conceptuel) | C4 | ✅ `Projets/RITA/02-Schemas/SCHEMA-MCD-MERISE-RITA.png` + `.drawio` |
| ⚠️ Masquer les montants dans les traces LangSmith | RGPD | 🔴 ouvert — transfert hors UE (registre §5) |
| ⚠️ Hook Git `pre-commit` bloquant les fichiers personnels | RGPD | 🟠 ouvert (procédure P4) |
| 3 requêtes SQL documentées (sélections, jointures, optimisations) | C2 | ⬜ |
| Extraction programmatique depuis la base = 5ᵉ type C1 | C1 | ⬜ |

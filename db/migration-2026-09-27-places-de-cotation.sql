-- =============================================================================
-- Migration du 27/09/2026 : places de cotation (issues #47, #48, #52)
-- =============================================================================
-- `db/schema.sql` ne se rejoue pas sur une base existante. Ce fichier applique à la
-- base réelle ce que le schéma et l'importeur font désormais d'eux-mêmes sur une base
-- neuve. Il est REJOUABLE : chaque ordre est idempotent.
--
-- Application :
--   psql -U rita -d rita -p 5433 -v ON_ERROR_STOP=1 -f db/migration-2026-09-27-places-de-cotation.sql
--
-- Ce qu'il NE fait PAS : corriger les dates de séance et les pence de la table
-- `cotation` (issues #53 et #47). Cela se fait en reconstruisant la table depuis le
-- Parquet avec l'importeur corrigé, après sauvegarde (voir evidence/C21/INC-005).

BEGIN;

-- #52 : la table des séries FRED, si elle n'existe pas encore.
CREATE TABLE IF NOT EXISTS macro_observation (
    serie            VARCHAR(20)   NOT NULL,
    date_observation DATE          NOT NULL,
    valeur           NUMERIC(14,4) NOT NULL,
    collecte_le      TIMESTAMPTZ   NOT NULL DEFAULT now(),
    PRIMARY KEY (serie, date_observation)
);

-- #47 : la devise de cotation suit la place (suffixe Yahoo), plus « EUR » par défaut.
UPDATE valeur SET devise = 'USD' WHERE ticker IN ('FTI', 'SLB')      AND devise <> 'USD';
UPDATE valeur SET devise = 'GBP' WHERE ticker = 'HSBA.L'             AND devise <> 'GBP';

-- #48 : trois valeurs radiées, marquées comme telles (leur historique reste).
UPDATE valeur SET statut_qualite = 'DELISTEE',
                  note_qualite   = 'radiee : derniere seance le 2018-03-22 (Zodiac Aerospace)'
 WHERE ticker = 'ZC.PA'  AND statut_qualite <> 'DELISTEE';
UPDATE valeur SET statut_qualite = 'DELISTEE',
                  note_qualite   = 'radiee : derniere seance le 2018-04-26 (Euler Hermes)'
 WHERE ticker = 'ELE.PA' AND statut_qualite <> 'DELISTEE';
UPDATE valeur SET statut_qualite = 'DELISTEE',
                  note_qualite   = 'radiee : derniere seance le 2019-05-28 (Gemalto)'
 WHERE ticker = 'GTO.PA' AND statut_qualite <> 'DELISTEE';

COMMIT;

-- Vérification (à lire, pas à comparer visuellement dans un bloc de commande) :
--   SELECT ticker, devise, statut_qualite FROM valeur
--    WHERE ticker IN ('FTI','SLB','HSBA.L','ZC.PA','ELE.PA','GTO.PA') ORDER BY ticker;

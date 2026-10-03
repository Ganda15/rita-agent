-- =============================================================================
-- Migration du 03/10/2026 : cloture des positions (plan 66, chapitre Donnees 1.5, D1 a D4 = A)
-- =============================================================================
-- Rejouable. Elle REFUSE d'agir si la table contient deja des doublons de ligne : l'index unique
-- echouerait, et un doublon est une decision humaine (deux achats identiques le meme jour existent).
-- Application :
--   psql -U rita -d rita -p 5433 -v ON_ERROR_STOP=1 -f db/migration-2026-10-03-cloture-positions.sql
-- Verification : SELECT count(*) FILTER (WHERE date_cloture IS NULL) AS actives, count(*) AS total FROM position;

BEGIN;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM position GROUP BY ticker, pru, COALESCE(date_achat, DATE '1900-01-01') HAVING count(*) > 1) THEN
    RAISE EXCEPTION 'position : doublons de ligne (ticker, pru, date_achat) presents ; trancher a la main avant de poser l index unique';
  END IF;
END $$;

ALTER TABLE position ADD COLUMN IF NOT EXISTS date_cloture DATE;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'cloture_apres_achat') THEN
    ALTER TABLE position ADD CONSTRAINT cloture_apres_achat
      CHECK (date_cloture IS NULL OR date_achat IS NULL OR date_cloture >= date_achat);
  END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS uq_position_ligne ON position (ticker, pru, COALESCE(date_achat, DATE '1900-01-01'));

COMMENT ON COLUMN position.date_cloture IS
    'NULL tant que la ligne est dans le CSV ; posee par l import (db/importer.py) le jour ou elle en '
    'disparait : c est la seule date de vente que le projet connaisse. Purge P2 trois ans apres (T1). '
    'Une ligne revenue dans le CSV rouvre la meme ligne (date_cloture remise a NULL).';

-- La vue ne valorise plus que les positions detenues : meme texte que db/schema.sql.

CREATE OR REPLACE VIEW v_portefeuille_valorise AS
WITH taux_du_jour AS (
    -- DISTINCT ON reste légitime ICI : `taux_change` compte 5 devises, pas 273 608
    -- cotations. Le tri porte sur un jeu minuscule. Ce qui était coûteux plus haut ne
    -- l'est pas ici : c'est le volume qui décide, pas l'écriture.
    SELECT DISTINCT ON (devise)
           devise, valeur_pour_eur
    FROM   taux_change
    ORDER  BY devise, date_taux DESC
)
SELECT  v.ticker,
        v.nom_officiel,
        v.statut_qualite,
        p.quantite,
        p.pru,
        p.devise,
        d.date_seance                                                      AS date_cours,
        d.cloture                                                          AS cours,
        ROUND(p.quantite * p.pru / CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END, 2)     AS investi_eur,
        ROUND(p.quantite * d.cloture / CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END, 2) AS valorisation_eur,
        ROUND((d.cloture - p.pru) / p.pru * 100, 2)                        AS performance_pct,
        -- Plan 65 (03/10/2026, cas D06 du chapitre Donnees) : l'euro se convertit par 1 sans lire
        -- taux_change ; une devise etrangere sans taux rend NULL et le dit, au lieu de diviser par 1
        -- et d'afficher un montant en dollars comme des euros. La ligne reste visible (LEFT JOIN).
        CASE WHEN p.devise = 'EUR' THEN 1 ELSE t.valeur_pour_eur END       AS taux_pour_eur,
        (p.devise <> 'EUR' AND t.valeur_pour_eur IS NULL)                  AS taux_manquant
FROM        position p
JOIN        valeur   v ON v.ticker = p.ticker
LEFT JOIN LATERAL (
    -- LATERAL : la sous-requête voit `p.ticker` de la ligne courante. C'est ce qui
    -- permet le Nested Loop + Index Scan au lieu du tri complet.
    SELECT c.date_seance, c.cloture
    FROM   cotation c
    WHERE  c.ticker = p.ticker
    ORDER  BY c.date_seance DESC
    LIMIT  1
) d ON TRUE
LEFT JOIN   taux_du_jour t ON t.devise = p.devise
WHERE       p.date_cloture IS NULL          -- plan 66 : une position close ne se valorise plus
ORDER BY    performance_pct DESC NULLS LAST;

COMMENT ON VIEW v_portefeuille_valorise IS
    'Briefing quotidien, converti en euros. Deux LEFT JOIN volontaires : une position '
    'sans cotation reste visible avec un cours NULL ; une devise etrangere sans taux reste '
    'visible avec des montants NULL et taux_manquant vrai (plan 65, 03/10/2026 : avant, '
    'COALESCE(taux, 1) affichait un montant en devise comme des euros). L euro se convertit '
    'par 1 sans lire taux_change. Un INNER JOIN ferait disparaitre la ligne en silence, '
    'le pire comportement possible pour un outil financier.';

COMMIT;

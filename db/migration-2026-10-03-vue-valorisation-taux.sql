-- =============================================================================
-- Migration du 03/10/2026 : la vue de valorisation ne remplace plus un taux manquant par 1
-- (plan 65, cas D06 du chapitre Donnees, decision d'Era D1/D2/D3 = A)
-- =============================================================================
-- `db/schema.sql` ne se rejoue pas sur une base existante. Ce fichier remplace la vue par sa
-- definition du schema TELLE QU'ELLE ETAIT LE 03/10 au matin. CREATE OR REPLACE VIEW ajoute les
-- deux colonnes (taux_pour_eur, taux_manquant) en fin de liste, sans DROP.
--
-- ORDRE OBLIGATOIRE (corrige le 24/10/2026) : jouer cette migration AVANT
-- db/migration-2026-10-03-cloture-positions.sql. La vue ci-dessous n'a pas le filtre des positions
-- closes (`p.date_cloture IS NULL`), ajoute le meme soir par le plan 66 dans le schema et dans la
-- migration de la cloture. Rejouee APRES celle-ci, elle ferait revenir les positions closes dans
-- la valorisation. Rejouable sans risque seulement dans cet ordre, celui de docs/exploitation.md.
--
-- Application :
--   psql -U rita -d rita -p 5433 -v ON_ERROR_STOP=1 -f db/migration-2026-10-03-vue-valorisation-taux.sql
--
-- Verification apres coup :
--   SELECT taux_manquant, COUNT(*) FROM v_portefeuille_valorise GROUP BY 1;

BEGIN;

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
ORDER BY    performance_pct DESC NULLS LAST;

COMMENT ON VIEW v_portefeuille_valorise IS
    'Briefing quotidien, converti en euros. Deux LEFT JOIN volontaires : une position '
    'sans cotation reste visible avec un cours NULL ; une devise etrangere sans taux reste '
    'visible avec des montants NULL et taux_manquant vrai (plan 65, 03/10/2026 : avant, '
    'COALESCE(taux, 1) affichait un montant en devise comme des euros). L euro se convertit '
    'par 1 sans lire taux_change. Un INNER JOIN ferait disparaitre la ligne en silence, '
    'le pire comportement possible pour un outil financier.';

COMMIT;

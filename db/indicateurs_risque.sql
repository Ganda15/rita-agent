-- =============================================================================
-- INDICATEURS DE MARCHÉ — LOT 3 « RISQUE »
--
-- Spécification : docs/indicateurs/CONCEPTION.md §7
-- Livrable      : E4 (application) — alimente l'écran 2
--
-- ⚠️ RITA calcule des INDICATEURS, jamais des STRATÉGIES. La volatilité, le
--    drawdown et le RSI (module Python associé) décrivent l'AGITATION d'un
--    cours — jamais un ordre d'achat ou de vente. Aucun seuil, aucune couleur
--    d'alerte, aucun mot « acheter »/« vendre ». Contrainte AMF (CLAUDE.md).
--
-- Ce fichier porte I4 (volatilité) et I5 (drawdown) : les deux s'expriment en
-- fonctions fenêtre SQL. I6 (RSI 14) N'EST PAS ici — voir indicateurs/risque.py.
-- Le lissage de Wilder est RÉCURSIF (chaque moyenne dépend de la précédente) :
-- ce n'est pas exprimable en fenêtre SQL simple, et un CTE récursif serait
-- illisible. Décision de la spécification : Python.
--
-- ⚠️ Un module externe (quant_metrics.py, Ganda15/daily-stock-analysis-era)
--    calcule déjà volatilité et drawdown en pandas — VÉRIFIÉ le 19/08/2026,
--    NON réutilisé. Il utilise `pct_change()` (rendement SIMPLE) là où la spec
--    exige le rendement LOGARITHMIQUE, et `cummax()` (maximum incluant le jour
--    COURANT) là où la spec dit explicitement « jusqu'à t−1 ». Même verdict que
--    pour le lot 1 le 18/08 : les formules ne correspondent pas à ce qui est
--    écrit ici, donc pas de portage.
-- =============================================================================


-- @@REQUETE risque
-- -----------------------------------------------------------------------------
-- I4 — VOLATILITÉ ANNUALISÉE SUR 20 SÉANCES (§7.1)
-- I5 — DRAWDOWN MAXIMAL SUR UN AN (§7.2)
--
-- Brique commune aux deux : le RENDEMENT JOURNALIER LOGARITHMIQUE
--   r_t = ln(cloture_t / cloture_t−1)
-- Écrit UNE fois, dans la CTE `rendements` ci-dessous — la spécification
-- l'exige explicitement (§7, chapeau).
-- -----------------------------------------------------------------------------

WITH derniere_seance AS (
    -- PAR TICKER — même règle que le lot 1 : Euronext, Xetra et le NYSE ne
    -- ferment pas les mêmes jours (défaut mesuré le 10/08/2026).
    SELECT   ticker, MAX(date_seance) AS derniere
    FROM     cotation
    GROUP BY ticker
),

historique AS (
    -- 400 jours de calendrier suffisent pour 252 séances (1 an boursier) même
    -- en comptant les jours fériés et week-ends — même borne que le lot 1.
    SELECT c.ticker, c.date_seance, c.cloture
    FROM   cotation       c
    JOIN   derniere_seance d ON d.ticker = c.ticker
    WHERE  c.date_seance >= d.derniere - INTERVAL '400 days'
),

rendements AS (
    SELECT h.*,
           -- Rendement LOGARITHMIQUE — pas `(cloture - precedent) / precedent`.
           -- C'est le rendement retenu par la spécification (§7, chapeau) : il
           -- s'additionne dans le temps, ce qu'un rendement simple ne fait pas.
           LN(h.cloture / NULLIF(LAG(h.cloture) OVER (
               PARTITION BY h.ticker ORDER BY h.date_seance), 0)) AS rendement_log,

           -- ⚠️ LE PIÈGE DU DRAWDOWN : le plus haut est glissant et s'arrête à
           -- LA VEILLE (ROWS ... AND 1 PRECEDING, jamais CURRENT ROW). Le
           -- confondre avec le plus haut de toute la période est l'erreur
           -- classique — elle donne un chiffre trop favorable.
           MAX(h.cloture) OVER (PARTITION BY h.ticker ORDER BY h.date_seance
                                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
           ) AS plus_haut_avant_ce_jour
    FROM   historique h
),

avec_drawdown AS (
    SELECT r.*,
           -- Résultat toujours ≤ 0 (#79, corrigé le 01/11/2026) : un jour au-dessus du
           -- plus haut de la veille n'est pas une baisse et compte pour 0, pas pour un
           -- gain. Sans plus haut antérieur (première séance), la valeur reste NULL :
           -- LEAST seul ne suffit pas, PostgreSQL y ignore les NULL et rendrait 0.
           CASE WHEN r.plus_haut_avant_ce_jour IS NULL THEN NULL
                ELSE LEAST(0, (r.cloture / NULLIF(r.plus_haut_avant_ce_jour, 0) - 1) * 100)
           END AS baisse_pct
    FROM   rendements r
),

-- ⚠️ LE PIÈGE QUI A CASSÉ LA PREMIÈRE VERSION DE CETTE REQUÊTE (19/08/2026) :
--    les fonctions fenêtre DOIVENT être calculées ICI, sur `avec_drawdown`
--    qui contient l'HISTORIQUE COMPLET (une ligne par séance et par ticker).
--
--    La première version les plaçait dans le SELECT final, après la jointure
--    sur `derniere_seance` — et cette jointure réduit chaque ticker à UNE SEULE
--    ligne AVANT que la fenêtre ne soit évaluée. Une fenêtre de 20 séances qui
--    n'a plus qu'UNE ligne à regarder ne peut rien mesurer : elle rendait NULL
--    pour les 111 valeurs, mesuré et vérifié.
--
--    Règle générale : calculer d'abord les fonctions fenêtre sur les données
--    complètes, dans une CTE ; ne filtrer sur la dernière séance QU'ENSUITE,
--    dans la requête qui lit cette CTE déjà calculée.
indicateurs_par_jour AS (
    SELECT d.*,
           -- I4 — écart-type ÉCHANTILLON (stddev_samp, diviseur n−1), PAS
           -- stddev_pop : sur 20 points l'écart entre les deux se voit. 252 =
           -- nombre CONVENTIONNEL de séances par an, pas une mesure — déclaré
           -- ici, pas présenté comme un fait.
           CASE WHEN COUNT(d.rendement_log) OVER (PARTITION BY d.ticker
                          ORDER BY d.date_seance ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) = 20
                THEN (STDDEV_SAMP(d.rendement_log) OVER (PARTITION BY d.ticker
                          ORDER BY d.date_seance ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
                          * SQRT(252) * 100)
           END AS volatilite_annualisee_pct,

           -- I5 — le pire jour des 252 dernières séances. `baisse_pct` a déjà
           -- appliqué la règle « plus haut jusqu'à la veille » ci-dessus ; ce
           -- MIN ne fait que choisir le pire jour dans la fenêtre d'un an.
           MIN(d.baisse_pct) OVER (PARTITION BY d.ticker
                ORDER BY d.date_seance ROWS BETWEEN 251 PRECEDING AND CURRENT ROW)
                AS drawdown_max_1a_pct
    FROM   avec_drawdown d
)

SELECT  ip.ticker,
        v.nom_officiel,
        v.statut_qualite,
        ip.date_seance                                    AS date_cours,
        ip.cloture                                         AS cours,
        (CURRENT_DATE - ip.date_seance)                    AS fraicheur_jours,
        ROUND(ip.volatilite_annualisee_pct::numeric, 2)    AS volatilite_annualisee_pct,
        ROUND(ip.drawdown_max_1a_pct::numeric, 2)          AS drawdown_max_1a_pct

FROM        indicateurs_par_jour ip
JOIN        valeur           v  ON v.ticker = ip.ticker
JOIN        derniere_seance  ds ON ds.ticker = ip.ticker AND ds.derniere = ip.date_seance
ORDER BY    ip.ticker;

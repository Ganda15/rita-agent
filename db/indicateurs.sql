-- =============================================================================
-- INDICATEURS DE MARCHÉ — LOT 1 « SOCLE »
--
-- Spécification : docs/indicateurs/CONCEPTION.md §5
-- Livrable      : E4 (application) — alimente l'écran 2
--
-- ⚠️ RITA calcule des INDICATEURS, jamais des STRATÉGIES.
--    Un nombre, son unité, sa fenêtre, sa date. Aucun verbe d'action, aucun
--    classement « meilleures valeurs », aucun code couleur binaire.
--    Contrainte AMF, posée dans CLAUDE.md.
--
-- UNE SEULE REQUÊTE rend les 11 colonnes. Onze requêtes qui reliraient chacune
-- `cotation` (273 608 lignes) seraient onze fois le même parcours de table.
-- =============================================================================


-- -----------------------------------------------------------------------------
-- I1 — LE SOCLE : 11 indicateurs par valeur, en une passe
--
-- Les cinq performances sont LE MÊME CALCUL avec une date cible différente.
-- D'où la table `cible` : on y décrit les fenêtres, on ne les recopie pas.
-- -----------------------------------------------------------------------------

WITH derniere_seance AS (
    -- ⚠️ PAR TICKER, jamais avec un MAX(date_seance) global.
    -- Euronext, Xetra et le NYSE ne ferment pas les mêmes jours. Un MAX global
    -- ne remontait que 2 valeurs sur 111 (défaut mesuré le 10/08/2026).
    SELECT   ticker, MAX(date_seance) AS derniere
    FROM     cotation
    GROUP BY ticker
),

cours_actuel AS (
    SELECT c.ticker, c.date_seance, c.cloture
    FROM   cotation       c
    JOIN   derniere_seance d ON d.ticker = c.ticker AND d.derniere = c.date_seance
),

-- Les cinq dates de référence, décrites une fois.
-- ⚠️ En jours de CALENDRIER, pas en nombre de lignes : `LAG(cloture, 5)`
--    supposerait que toutes les valeurs cotent les mêmes jours. Elles ne le font pas.
cible AS (
    SELECT ca.ticker,
           ca.date_seance                                    AS date_cours,
           ca.cloture                                        AS cours,
           ca.date_seance - INTERVAL '1 day'                 AS cible_1j,
           ca.date_seance - INTERVAL '7 days'                AS cible_1s,
           ca.date_seance - INTERVAL '1 month'               AS cible_1m,
           DATE_TRUNC('year', ca.date_seance)                AS cible_ytd,
           ca.date_seance - INTERVAL '1 year'                AS cible_1a
    FROM   cours_actuel ca
),

-- La référence d'une fenêtre = LA DERNIÈRE SÉANCE À OU AVANT la date cible.
-- LATERAL est indispensable : la borne dépend de la ligne courante.
-- (Même choix que la requête R1 de requetes.sql, où il a battu un CTE
--  DISTINCT ON d'un facteur ~2000 — mesuré par EXPLAIN ANALYZE.)
--
-- ⚠️ La YTD est la PREMIÈRE séance de l'année, pas une séance « à ou avant ».
--    Elle s'écrit donc dans l'autre sens : ORDER BY ... ASC.
references_cours AS (
    SELECT t.*,
           r1j.cloture  AS ref_1j,
           r1s.cloture  AS ref_1s,
           r1m.cloture  AS ref_1m,
           rytd.cloture AS ref_ytd,
           r1a.cloture  AS ref_1a
    FROM   cible t
    LEFT JOIN LATERAL (SELECT c.cloture FROM cotation c
                       WHERE c.ticker = t.ticker AND c.date_seance <= t.cible_1j
                       ORDER BY c.date_seance DESC LIMIT 1) r1j  ON TRUE
    LEFT JOIN LATERAL (SELECT c.cloture FROM cotation c
                       WHERE c.ticker = t.ticker AND c.date_seance <= t.cible_1s
                       ORDER BY c.date_seance DESC LIMIT 1) r1s  ON TRUE
    LEFT JOIN LATERAL (SELECT c.cloture FROM cotation c
                       WHERE c.ticker = t.ticker AND c.date_seance <= t.cible_1m
                       ORDER BY c.date_seance DESC LIMIT 1) r1m  ON TRUE
    LEFT JOIN LATERAL (SELECT c.cloture FROM cotation c
                       WHERE c.ticker = t.ticker AND c.date_seance >= t.cible_ytd
                       ORDER BY c.date_seance ASC  LIMIT 1) rytd ON TRUE
    LEFT JOIN LATERAL (SELECT c.cloture FROM cotation c
                       WHERE c.ticker = t.ticker AND c.date_seance <= t.cible_1a
                       ORDER BY c.date_seance DESC LIMIT 1) r1a  ON TRUE
),

-- Fenêtres glissantes : ici en SÉANCES, et c'est volontaire.
-- Une moyenne mobile se définit en séances par convention ; une performance se
-- définit en durée. Les deux unités coexistent, et c'est écrit pour qu'un
-- relecteur n'y voie pas une incohérence.
--
-- On ne lit que les 400 derniers jours de calendrier : au-delà, aucune fenêtre
-- du lot 1 n'en a besoin (la plus longue est de 252 séances).
fenetre AS (
    SELECT c.ticker, c.date_seance, c.cloture, c.haut, c.volume,
           -- MA20/MA50 : la fenêtre INCLUT le jour courant (elle décrit un niveau),
           -- contrairement au volume relatif de R3 qui l'exclut (il compare un
           -- jour à son passé). Deux besoins différents, deux fenêtres différentes.
           CASE WHEN COUNT(*) OVER (PARTITION BY c.ticker ORDER BY c.date_seance
                                    ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) = 20
                THEN AVG(c.cloture) OVER (PARTITION BY c.ticker ORDER BY c.date_seance
                                          ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
           END AS ma20,
           CASE WHEN COUNT(*) OVER (PARTITION BY c.ticker ORDER BY c.date_seance
                                    ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) = 50
                THEN AVG(c.cloture) OVER (PARTITION BY c.ticker ORDER BY c.date_seance
                                          ROWS BETWEEN 49 PRECEDING AND CURRENT ROW)
           END AS ma50,
           -- ADTV20 : `cloture` approxime le cours moyen pondéré par les volumes
           -- intraséance, que RITA n'a pas. Approximation DÉCLARÉE, pas cachée.
           CASE WHEN COUNT(*) OVER (PARTITION BY c.ticker ORDER BY c.date_seance
                                    ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) = 20
                THEN AVG(c.volume * c.cloture) OVER (PARTITION BY c.ticker ORDER BY c.date_seance
                                                     ROWS BETWEEN 19 PRECEDING AND CURRENT ROW)
           END AS adtv20,
           -- Plus haut sur un an : MAX(haut), l'INTRASÉANCE — c'est la convention
           -- du « 52-week high ». Le plus haut de clôture donnerait un autre chiffre.
           MAX(c.haut) OVER (PARTITION BY c.ticker ORDER BY c.date_seance
                             ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS plus_haut_1a
    FROM   cotation       c
    JOIN   derniere_seance d ON d.ticker = c.ticker
    WHERE  c.date_seance >= d.derniere - INTERVAL '400 days'
)

SELECT  r.ticker,
        v.nom_officiel,
        v.statut_qualite,
        r.date_cours,
        r.cours,

        -- ⚠️ FRAÎCHEUR — ajoutée le 18/08/2026 après une mesure, pas par prudence.
        -- Trois valeurs de l'univers sont RADIÉES et cotent encore `statut_qualite = 'OK'` :
        --   ZC.PA  Zodiac Aerospace  dernière séance 2018-03-22
        --   ELE.PA Euler Hermes      dernière séance 2018-04-26
        --   GTO.PA Gemalto           dernière séance 2019-05-28
        -- Sans cette colonne, l'écran afficherait pour elles une « performance 1 jour »
        -- calculée sur des cours vieux de huit ans, sans que rien ne le signale.
        -- On montre le chiffre, on signale le doute — jamais l'inverse.
        (CURRENT_DATE - r.date_cours) AS fraicheur_jours,

        -- 5 performances, en pourcentage. NULL si l'historique est trop court :
        -- (aucun caractère « pour-cent » dans ce fichier : psycopg2 le prendrait
        --  pour un marqueur de paramètre, y compris à l'intérieur d'un commentaire)
        -- une performance 1 an sur 3 mois de données serait un chiffre inventé.
        ROUND((r.cours / NULLIF(r.ref_1j , 0) - 1) * 100, 2) AS perf_1j_pct,
        ROUND((r.cours / NULLIF(r.ref_1s , 0) - 1) * 100, 2) AS perf_1s_pct,
        ROUND((r.cours / NULLIF(r.ref_1m , 0) - 1) * 100, 2) AS perf_1m_pct,
        ROUND((r.cours / NULLIF(r.ref_ytd, 0) - 1) * 100, 2) AS perf_ytd_pct,
        ROUND((r.cours / NULLIF(r.ref_1a , 0) - 1) * 100, 2) AS perf_1a_pct,

        ROUND(f.ma20  , 4) AS ma20,
        ROUND(f.ma50  , 4) AS ma50,
        ROUND(f.adtv20, 0) AS adtv20,

        -- Distance au plus haut : toujours ≤ 0. Un cours AU plus haut donne 0,00.
        ROUND((r.cours / NULLIF(f.plus_haut_1a, 0) - 1) * 100, 2) AS distance_plus_haut_1a_pct

FROM        references_cours r
JOIN        valeur           v ON v.ticker      = r.ticker
JOIN        fenetre          f ON f.ticker      = r.ticker
                              AND f.date_seance = r.date_cours
ORDER BY    r.ticker;

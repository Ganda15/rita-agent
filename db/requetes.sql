-- =============================================================================
-- RITA — Requêtes SQL de collecte  ·  compétence C2
-- =============================================================================
-- C2 : « Développer des requêtes de type SQL d'extraction des données depuis un système
-- de gestion de base de données et un système big data en appliquant le langage de requête
-- propre au système afin de préparer la collecte des données nécessaires au projet. »
--
-- Les trois critères évalués, et où ils sont traités :
--   1. « Les requêtes sont fonctionnelles : les données visées sont effectivement
--      extraites »                       -> sorties réelles dans evidence/C2/
--   2. « La documentation met en lumière choix de sélections, filtrages, conditions,
--      jointures, etc., en fonction des objectifs de collecte »
--                                        -> bloc OBJECTIF + CHOIX devant chaque requête
--   3. « La documentation explicite les optimisations appliquées »
--                                        -> bloc OPTIMISATION, avec mesures EXPLAIN
--
-- Exécution :
--   psql -h localhost -p 5432 -U rita -d rita -f db/requetes.sql
-- =============================================================================


-- #############################################################################
-- R1 — BRIEFING QUOTIDIEN : le portefeuille valorisé, converti en euros
-- #############################################################################
--
-- OBJECTIF DE COLLECTE
--   Produire la ligne « où en est mon portefeuille aujourd'hui » du briefing : pour chaque
--   ligne détenue, le dernier cours connu, la valorisation et la performance depuis
--   l'achat — le tout ramené en euros, sinon on additionne des euros et des dollars.
--
-- CHOIX DE SÉLECTION
--   On part de `position` (7 lignes), pas de `valeur` (111) : le briefing porte sur ce qui
--   est détenu, pas sur l'univers de veille. Partir de la grande table forcerait un filtre
--   inutile sur 104 lignes.
--
-- CHOIX DE JOINTURE
--   · position -> valeur          : JOIN simple, la clé étrangère garantit l'existence
--   · position -> dernière cotation : LEFT JOIN **volontaire**. Une valeur suspendue de
--     cotation doit rester VISIBLE dans le briefing avec un cours NULL. Un INNER JOIN la
--     ferait disparaître silencieusement — le pire comportement possible pour un outil
--     financier.
--   · position -> taux_change     : LEFT JOIN, et depuis le 03/10/2026 (plan 65, cas D06 du
--     chapitre Données) plus de COALESCE(..., 1) : une devise étrangère sans taux ne doit pas
--     annuler la ligne, mais elle ne doit pas non plus s'afficher à son montant nominal comme
--     si c'étaient des euros. Les montants deviennent NULL et `taux_manquant` le dit ; l'euro
--     se convertit par 1 sans lire la table.
--
-- CHOIX DE FILTRAGE
--   Aucun filtre sur `statut_qualite` ici : si Era détient une valeur douteuse, il doit la
--   voir. Le statut est REMONTÉ dans le résultat pour être affiché, pas utilisé pour cacher.
--
-- OPTIMISATION — ⚠️ MESURÉE, ET CONTRAIRE À CE QUI ÉTAIT PRÉVU
--   La première version utilisait un CTE `DISTINCT ON (ticker)`, en supposant qu'il valait
--   mieux qu'une sous-requête « exécutée une fois par ligne ». EXPLAIN ANALYZE sur les
--   273 608 cotations réelles a montré l'inverse :
--
--     sous-requête corrélée  ->   0,12 ms
--     CTE DISTINCT ON        -> 258,00 ms      (2 000× plus lent)
--
--   Raison : avec 7 positions, la sous-requête fait 7 recherches d'index
--   (Index Scan Backward using cotation_pkey, loops=7). Le DISTINCT ON, lui, TRIE les
--   273 608 lignes pour calculer le dernier cours des 107 valeurs — dont 100 dont on n'a
--   pas besoin.
--
--   Version retenue : LEFT JOIN LATERAL — même plan d'exécution que la sous-requête
--   corrélée (Nested Loop + Index Scan), mais lisible et capable de renvoyer plusieurs
--   colonnes d'un coup.
--
--     LATERAL,  7 positions   ->   0,24 ms
--     LATERAL, 111 valeurs    ->   1,19 ms
--     DISTINCT ON, 111 valeurs -> 295,19 ms    (250× plus lent)
--
--   L'avantage tient tant que le nombre de lignes en entrée reste petit devant le nombre
--   total de cotations — ce qui est le cas ici, et le restera : un portefeuille compte des
--   dizaines de lignes, l'historique des centaines de milliers.
--
WITH taux_du_jour AS (
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
    -- LATERAL : la sous-requête voit `p.ticker` de la ligne courante.
    -- C'est ce qui permet le Nested Loop + Index Scan mesuré ci-dessus.
    SELECT c.date_seance, c.cloture
    FROM   cotation c
    WHERE  c.ticker = p.ticker
    ORDER  BY c.date_seance DESC
    LIMIT  1
) d ON TRUE
LEFT JOIN   taux_du_jour t ON t.devise = p.devise
ORDER BY    performance_pct DESC NULLS LAST;


-- #############################################################################
-- R2 — LES PLUS FORTS MOUVEMENTS DE LA SÉANCE
-- #############################################################################
--
-- OBJECTIF DE COLLECTE
--   Alimenter la section « ce qui bouge » du briefing : les 5 plus fortes hausses et
--   baisses de l'univers sur la dernière séance connue.
--
-- CHOIX DE SÉLECTION
--   `LAG(cloture) OVER (PARTITION BY ticker ORDER BY date_seance)` récupère la clôture de
--   la séance PRÉCÉDENTE de la même valeur. Sans fonction de fenêtrage, il faudrait une
--   auto-jointure `cotation c1 JOIN cotation c2 ON c2.date = c1.date - 1` — fausse, car
--   la veille d'un lundi n'est pas dimanche mais vendredi, et les jours fériés varient
--   selon la place de cotation.
--
-- CHOIX DE FILTRAGE — le plus important de la requête
--   `WHERE v.statut_qualite = 'OK'` exclut STLAP.PA et ALJXR.PA. Sans ce filtre, ALJXR.PA
--   (prix maximum 7 156 748 €) trusterait le classement des variations avec des chiffres
--   dépourvus de sens. **C'est là que l'analyse exploratoire du 31/07 devient utile en
--   production** : elle a produit le statut, la requête s'en sert.
--
-- CHOIX DE CONDITION
--   `cloture_veille IS NOT NULL` élimine la toute première séance de chaque valeur, où la
--   variation n'existe pas.
--
-- OPTIMISATION
--   La fenêtre ne balaie que 2 séances par valeur grâce au filtre de dates en amont dans
--   le CTE, au lieu des 2 560 séances de l'historique complet.
--   `idx_cotation_date` sert le filtre `date_seance >= ...` (Index Scan mesuré).
--
WITH derniere_seance AS (
    -- ⚠️ PAR TICKER, pas globalement. Mesure du 01/08 : le 2026-07-29 ne compte que
    -- 2 valeurs (SLB, FTI — cotées aux États-Unis) contre 106 le 2026-07-28. Un
    -- `max(date_seance)` global ne remontait donc que 2 lignes sur 111. Chaque place
    -- de cotation a son propre calendrier : Euronext, Xetra et le NYSE ne ferment pas
    -- les mêmes jours.
    SELECT ticker, max(date_seance) AS derniere
    FROM   cotation
    GROUP  BY ticker
),
deux_seances AS (
    SELECT c.ticker, c.date_seance, c.cloture,
           LAG(c.cloture) OVER (PARTITION BY c.ticker ORDER BY c.date_seance) AS cloture_veille
    FROM   cotation c
    JOIN   derniere_seance d ON d.ticker = c.ticker
    WHERE  c.date_seance >= d.derniere - INTERVAL '10 days'
)
SELECT  s.ticker,
        v.nom_officiel,
        s.date_seance,
        s.cloture_veille,
        s.cloture,
        ROUND((s.cloture - s.cloture_veille) / s.cloture_veille * 100, 2) AS variation_pct
FROM        deux_seances   s
JOIN        valeur         v ON v.ticker = s.ticker
JOIN        derniere_seance d ON d.ticker = s.ticker AND d.derniere = s.date_seance
WHERE       s.cloture_veille IS NOT NULL
  AND       v.statut_qualite = 'OK'
ORDER BY    variation_pct DESC
LIMIT 5;


-- #############################################################################
-- R3 — VOLUME ANORMAL : détecter un intérêt inhabituel sur une valeur
-- #############################################################################
--
-- OBJECTIF DE COLLECTE
--   Fournir un signal à l'agent Technique : une valeur dont le volume du jour dépasse
--   nettement sa moyenne récente attire l'attention du marché. C'est un fait observable,
--   pas une recommandation — la distinction est ce qui garde RITA conforme à l'AMF.
--
-- CHOIX DE SÉLECTION
--   `AVG(volume) OVER (PARTITION BY ticker ORDER BY date_seance ROWS BETWEEN 20 PRECEDING
--   AND 1 PRECEDING)` : moyenne mobile sur 20 séances, **sans inclure le jour courant** —
--   sinon un pic de volume relèverait sa propre moyenne et se masquerait lui-même.
--
-- CHOIX DE CONDITION
--   `moyenne_20j > 0` évite une division par zéro : l'analyse exploratoire a mesuré
--   2 802 séances à volume nul. Sans cette condition, la requête plante sur les données
--   réelles.
--
-- CHOIX DE FILTRAGE
--   Ratio > 2 : le volume a au moins doublé. Seuil arbitraire et assumé — il se règle,
--   il ne se démontre pas.
--
-- OPTIMISATION
--   Le CTE restreint d'abord à ~60 jours : la fenêtre travaille sur ~40 lignes par valeur
--   au lieu de 2 560. Sans cette restriction, PostgreSQL trierait les 273 608 lignes.
--
WITH derniere_seance AS (
    SELECT ticker, max(date_seance) AS derniere
    FROM   cotation
    GROUP  BY ticker
),
recent AS (
    SELECT c.ticker, c.date_seance, c.volume, c.cloture
    FROM   cotation c
    JOIN   derniere_seance d ON d.ticker = c.ticker
    WHERE  c.date_seance >= d.derniere - INTERVAL '60 days'
),
avec_moyenne AS (
    SELECT r.*,
           AVG(r.volume) OVER (PARTITION BY r.ticker ORDER BY r.date_seance
                               ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS moyenne_20j
    FROM   recent r
)
SELECT  a.ticker,
        v.nom_officiel,
        a.date_seance,
        a.volume,
        ROUND(a.moyenne_20j)               AS moyenne_20j,
        ROUND(a.volume / a.moyenne_20j, 2) AS ratio,
        a.cloture
FROM        avec_moyenne    a
JOIN        valeur          v ON v.ticker = a.ticker
JOIN        derniere_seance d ON d.ticker = a.ticker AND d.derniere = a.date_seance
WHERE       a.moyenne_20j > 0
  AND       a.volume / a.moyenne_20j > 2
  AND       v.statut_qualite = 'OK'
ORDER BY    ratio DESC
LIMIT 10;

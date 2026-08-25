-- ===========================================================================
--  Fraîcheur du jeu de données — C20 (surveiller) et C1 (pérenniser)
--
--  Répond à UNE question, celle qu'un évaluateur posera :
--      « vos données sont-elles à jour ? »
--
--  Aujourd'hui l'application ne sait pas y répondre : /health dit
--  {"status":"ok"} sans rien dire des données. Le manque est écrit depuis le
--  11/08 dans scripts/README-planification.md §7 :
--      « la vraie sécurité n'est pas la planification mais une requête de
--        fraîcheur — savoir dire "ma donnée la plus récente a N jours". »
--
--  ## Cette requête ne décide RIEN
--
--  Elle rend des faits : dates les plus récentes et comptages. Le retard, le
--  statut vert/orange/rouge et la tolérance au week-end sont calculés en
--  Python (monitorage/fraicheur.py), pour deux raisons :
--    1. une fonction pure se teste sans base — la règle du dépôt ;
--    2. changer un seuil ne doit pas obliger à toucher au SQL.
--
--  ## Pourquoi COUNT(*) exact et pas l'estimation de pg_class
--
--  reltuples serait instantané, mais il dépend du dernier ANALYZE. Le 17/08,
--  après la reconstruction de la base, PRESQUE TOUTES les tables étaient
--  estimées à 0 alors qu'elles étaient pleines. Une jauge de santé qui ment
--  est pire qu'une jauge absente : ici on compte pour de vrai.
-- ===========================================================================

SELECT
    -- Cotations : la table qui doit grandir chaque jour de bourse
    (SELECT MAX(date_seance)  FROM cotation)     AS derniere_seance,
    (SELECT COUNT(*)          FROM cotation)     AS nb_cotations,

    -- Taux de change (BCE) : une ligne par devise et par jour ouvré
    (SELECT MAX(date_taux)    FROM taux_change)  AS dernier_taux,
    (SELECT COUNT(*)          FROM taux_change)  AS nb_taux,

    -- Articles : on regarde la date de COLLECTE, pas de publication.
    -- publie_le peut être ancienne pour un article repris ; collecte_le dit
    -- quand le pipeline a tourné pour la dernière fois sur les flux RSS.
    (SELECT MAX(collecte_le)  FROM article)      AS derniere_collecte_article,
    (SELECT COUNT(*)          FROM article)      AS nb_articles,

    -- Référentiels : ils ne grandissent pas, on les compte pour prouver
    -- qu'ils sont bien là (une base vide se repère immédiatement)
    (SELECT COUNT(*)          FROM valeur)       AS nb_valeurs,
    (SELECT COUNT(*)          FROM position)     AS nb_positions,

    CURRENT_DATE                                 AS aujourdhui;

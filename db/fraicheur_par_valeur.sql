-- ===========================================================================
--  Fraîcheur PAR VALEUR : la dernière séance de chaque valeur suivie (sprint 5, étape 2)
--
--  db/fraicheur.sql prend MAX(date_seance) sur TOUTES les cotations : une valeur
--  qui ne reçoit plus de cours y reste cachée tant qu'une autre est à jour.
--  C'est le cas d'OR.PA en production (critère 1 du contrat du sprint 1). Ici,
--  une ligne par valeur, pour que la vigie voie la valeur en retard.
--
--  Les valeurs exclues pour qualité (statut_qualite <> 'OK') ne sont pas
--  suivies. Lecture seule. Comme db/fraicheur.sql, cette requête ne décide
--  rien : le retard en jours ouvrés et la couleur se calculent en Python
--  (monitorage/signaux.py, avec les règles de monitorage/fraicheur.py).
--  La date du jour vient du serveur PostgreSQL (CURRENT_DATE).
-- ===========================================================================

SELECT
    v.ticker,
    MAX(c.date_seance) AS derniere_seance,
    CURRENT_DATE       AS aujourdhui
FROM valeur v
LEFT JOIN cotation c ON c.ticker = v.ticker
WHERE v.statut_qualite = 'OK'
GROUP BY v.ticker
ORDER BY v.ticker;

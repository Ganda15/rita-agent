-- =============================================================================
-- INDICATEURS DE MARCHÉ — LOT 2 « PORTEFEUILLE »
--
-- Spécification : docs/indicateurs/CONCEPTION.md §6
-- Livrable      : E4 (application) — alimente l'écran 2
--
-- ⚠️ DONNÉES PERSONNELLES (RGPD). `position` porte la situation financière de
--    l'utilisateur : quantités, prix de revient, plus-values. Ces deux indicateurs
--    héritent du traitement **T1** du registre (db/RGPD-registre-des-traitements.md)
--    — destinataire unique, purge déjà testée. Aucun nouveau traitement à déclarer.
--
-- ⚠️ RITA calcule des INDICATEURS, jamais des STRATÉGIES. Un poids de 38 pour cent
--    est un fait. « Vous êtes trop concentré, allégez » serait un conseil — et
--    l'interdit AMF le proscrit. Aucun seuil d'alerte, aucun classement.
--
-- POURQUOI CE LOT COMPTE PLUS QUE LE LOT 1 : les indicateurs du socle décrivent des
-- INSTRUMENTS, ce que fait n'importe quel site de cotations. Ceux-ci décrivent LE
-- PORTEFEUILLE d'Era — ses 7 lignes, leurs devises. C'est ce qu'aucun autre outil
-- ne peut produire, et c'est la réponse à « qu'est-ce qui est spécifique à votre
-- projet ? ».
-- =============================================================================


-- Les requêtes sont séparées par un marqueur `-- @@REQUETE <nom>` et non par le
-- point-virgule : découper sur `;` casserait au premier point-virgule à l'intérieur
-- d'une chaîne ou d'un commentaire. Un séparateur qui peut apparaître dans le
-- contenu n'est pas un séparateur.
-- @@REQUETE poids
-- -----------------------------------------------------------------------------
-- I2 — POIDS DE CHAQUE LIGNE DANS LE PORTEFEUILLE (§6.1)
--
-- ⚠️ LE PIÈGE : le total se calcule APRÈS conversion en euros. Additionner des
--    euros et des dollars produit un nombre dépourvu de sens — c'est le défaut
--    exact que `taux_change` existe pour corriger, et que la première version de
--    la vue commettait (corrigé le 10/08/2026).
--
--    Ici on part de `v_portefeuille_valorise`, qui a DÉJÀ fait la conversion. On
--    ne la refait pas : deux calculs de la même chose finissent toujours par
--    diverger.
-- -----------------------------------------------------------------------------

WITH total AS (
    -- Une seule ligne : le total du portefeuille en euros.
    -- NULLIF contre la division par zéro — un portefeuille vide, ou dont toutes
    -- les valorisations seraient nulles, rendrait NULL plutôt que d'échouer.
    -- Plan 65 (03/10/2026, decision D2 d'Era) : si une valorisation manque (taux absent), le
    -- total est inconnu, donc TOUS les poids le sont ; `complet` le dit a l'appelant.
    SELECT NULLIF(SUM(valorisation_eur), 0)          AS total_eur,
           COALESCE(BOOL_OR(taux_manquant), false)   AS taux_manquant
    FROM   v_portefeuille_valorise
)
SELECT  p.ticker,
        p.nom_officiel,
        p.devise,
        p.quantite,
        p.valorisation_eur,
        CASE WHEN t.taux_manquant THEN NULL
             ELSE ROUND(p.valorisation_eur / t.total_eur * 100, 2) END AS poids_pct,
        CASE WHEN t.taux_manquant THEN NULL ELSE t.total_eur END    AS total_eur,
        NOT t.taux_manquant                                          AS complet
FROM        v_portefeuille_valorise p
CROSS JOIN  total t
ORDER BY    poids_pct DESC NULLS LAST;


-- @@REQUETE exposition
-- -----------------------------------------------------------------------------
-- I3 — EXPOSITION PAR DEVISE (§6.2)
--
-- ⚠️ CE QUE CET INDICATEUR MESURE, ET CE QU'IL NE MESURE PAS.
--    Il mesure l'exposition **de cotation** : dans quelle monnaie les titres sont
--    cotés. Il ne mesure PAS l'exposition économique — LVMH est cotée en euros mais
--    réalise une part importante de son chiffre d'affaires en dollars et en yuans.
--    Un portefeuille « 100 pour cent EUR » selon cet indicateur peut être fortement
--    exposé au dollar dans les faits.
--
--    Cette distinction est écrite ici parce que, sans elle, le chiffre sera lu de
--    travers — et c'est le genre de nuance qu'un jury teste.
-- -----------------------------------------------------------------------------

WITH total AS (
    SELECT NULLIF(SUM(valorisation_eur), 0)          AS total_eur,
           COALESCE(BOOL_OR(taux_manquant), false)   AS taux_manquant
    FROM   v_portefeuille_valorise
)
SELECT  p.devise,
        COUNT(*)                                              AS nb_lignes,
        CASE WHEN t.taux_manquant THEN NULL ELSE SUM(p.valorisation_eur) END AS valorisation_eur,
        CASE WHEN t.taux_manquant THEN NULL
             ELSE ROUND(SUM(p.valorisation_eur) / t.total_eur * 100, 2) END AS exposition_pct,
        NOT t.taux_manquant                                   AS complet
FROM        v_portefeuille_valorise p
CROSS JOIN  total t
GROUP BY    p.devise, t.total_eur, t.taux_manquant
ORDER BY    exposition_pct DESC NULLS LAST;

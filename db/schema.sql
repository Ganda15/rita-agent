-- =============================================================================
-- RITA — Modèle physique des données (MPD)  ·  PostgreSQL 17
-- =============================================================================
-- Compétence C4 : « Créer une base de données dans le respect du RGPD en élaborant les
-- modèles conceptuels et physiques des données à partir des données préparées. »
--
-- ⚠️ CE SCHÉMA EST JUSTIFIÉ PAR LES REQUÊTES, PAS PAR LES DONNÉES.
-- Le Règlement spécifique (p. 53) exige « les éléments de conception de la base de
-- données, avec une approche orientée requêtes ». Chaque table, chaque clé et chaque
-- index ci-dessous porte en commentaire la requête du briefing qui l'impose.
-- Le raisonnement complet est dans db/CONCEPTION-ORIENTEE-REQUETES.md.
--
-- Deux contraintes viennent de l'analyse exploratoire du 31/07 (bigdata/explorer.py),
-- pas d'une intuition de modélisation :
--   1. (ticker, date) a 2 560 doublons -> le NOM ne peut pas vivre dans la cotation
--   2. 2 tickers sont aberrants        -> il faut pouvoir exclure SANS supprimer
-- =============================================================================

SET client_encoding = 'UTF8';

-- =============================================================================
-- 1. VALEUR — une société cotée, identifiée par son ticker
-- =============================================================================
-- Pourquoi une table séparée de `cotation` : l'analyse exploratoire a montré
-- 111 tickers pour 112 noms. « CGG BS » et « CGG RGPT » désignent deux lignes du
-- portefeuille mais UNE SEULE société (Viridien) et une seule série de cours.
-- Mettre le nom dans `cotation` obligerait à le répéter 2 560 fois par valeur et
-- rendrait le doublon indétectable.
CREATE TABLE valeur (
    ticker              VARCHAR(16)  PRIMARY KEY,
    isin                CHAR(12),
    nom_officiel        VARCHAR(120) NOT NULL,
    devise              CHAR(3)      NOT NULL DEFAULT 'EUR',
    place_cotation      VARCHAR(60),

    -- Sert la requête « performance sur 10 ans » en écartant le biais de survie :
    -- les historiques mesurés vont de 286 à 2 560 séances.
    premiere_cotation   DATE,
    derniere_cotation   DATE,

    -- Exclure sans supprimer. STLAP.PA (1 142 clôtures hors bornes) et ALJXR.PA
    -- (prix max 7,15 M) sont conservés avec leur cause : effacer, c'est perdre la
    -- trace du problème et le redécouvrir dans six mois.
    statut_qualite      VARCHAR(20)  NOT NULL DEFAULT 'OK'
        CHECK (statut_qualite IN ('OK', 'A_VERIFIER', 'INCOHERENT', 'DELISTEE')),
    note_qualite        TEXT,

    cree_le             TIMESTAMPTZ  NOT NULL DEFAULT now()
);

COMMENT ON COLUMN valeur.statut_qualite IS
    'Permet de filtrer les valeurs douteuses sans les effacer (tracabilite C3).';

-- Requête : « retrouver une valeur par son ISIN » (rapprochement avec le CSV du courtier,
-- qui fournit l ISIN mais pas toujours le ticker Yahoo).
CREATE INDEX idx_valeur_isin ON valeur (isin) WHERE isin IS NOT NULL;


-- =============================================================================
-- 2. ALIAS_VALEUR — les noms sous lesquels le portefeuille désigne une valeur
-- =============================================================================
-- C'EST LA TABLE QUI RÉSOUT LE CAS CGG.
-- Un ticker, plusieurs libellés d'origine (bons de souscription, regroupement,
-- ancienne raison sociale). Sans elle, l'import du CSV échoue sur la clé primaire
-- de `position` ou double la pondération de Viridien.
CREATE TABLE alias_valeur (
    alias       VARCHAR(120) PRIMARY KEY,
    ticker      VARCHAR(16)  NOT NULL REFERENCES valeur (ticker) ON DELETE CASCADE,
    origine     VARCHAR(40)  NOT NULL DEFAULT 'portefeuille'
);

COMMENT ON TABLE alias_valeur IS
    'Ex. : alias="CGG BS" et alias="CGG RGPT" pointent tous deux vers ticker="VIRI.PA".';

CREATE INDEX idx_alias_ticker ON alias_valeur (ticker);


-- =============================================================================
-- 3. COTATION — une séance de bourse pour une valeur
-- =============================================================================
-- Clé primaire (ticker, date) : elle TIENT une fois le nom sorti de la table.
-- C'est le résultat direct du dédoublonnage — 273 608 clés uniques mesurées.
CREATE TABLE cotation (
    ticker          VARCHAR(16) NOT NULL REFERENCES valeur (ticker) ON DELETE CASCADE,
    date_seance     DATE        NOT NULL,

    -- NOT NULL assumé : l'analyse exploratoire a mesuré 0 valeur manquante sur
    -- 276 168 lignes. Sans cette mesure, on aurait mis NULL « au cas où ».
    ouverture       NUMERIC(14,4) NOT NULL,
    haut            NUMERIC(14,4) NOT NULL,
    bas             NUMERIC(14,4) NOT NULL,
    cloture         NUMERIC(14,4) NOT NULL,
    volume          BIGINT        NOT NULL,

    PRIMARY KEY (ticker, date_seance),

    -- Règles métier vérifiées par la base, pas seulement par le script d'import :
    -- une base qui accepte des données incohérentes n'est pas un garde-fou.
    CONSTRAINT prix_positifs     CHECK (cloture > 0 AND ouverture > 0),
    CONSTRAINT bornes_coherentes CHECK (haut >= bas),
    CONSTRAINT volume_positif    CHECK (volume >= 0)
);

-- ⚠️ PAS d'index (ticker, date_seance DESC) ici — et c'est un choix MESURÉ.
--
-- Une première version en créait un, en supposant qu'il servirait les requêtes
-- « dernier cours » (Q1) et « historique 1 an » (Q4). EXPLAIN ANALYZE sur les
-- 273 608 lignes réelles a montré que le planificateur ne l'utilisait pas :
--
--   Q1 -> Index Scan Backward using cotation_pkey   (4 buffers)
--   Q4 -> Bitmap Index Scan on cotation_pkey        (4 buffers, identique)
--
-- La clé primaire (ticker, date_seance) couvre déjà les deux : PostgreSQL sait
-- parcourir un index à l'envers, le DESC explicite n'apporte rien. Après suppression,
-- pg_stat_user_indexes confirmait 1 seul scan pour cet index contre 273 609 pour la PK.
--
-- L'index redondant coûtait 9 Mo de disque et ralentissait CHAQUE insertion, pour rien.
-- C'est précisément ce que veut dire « approche orientée requêtes » : on mesure,
-- on ne suppose pas.

-- Requête Q3 : « les plus fortes variations d'une séance, toutes valeurs confondues ».
-- Filtre sur la date SEULE. La clé primaire commence par `ticker`, elle ne peut donc
-- pas servir ce motif d'accès -> cet index-là est nécessaire, et il est utilisé :
--   Q3 -> Index Scan using idx_cotation_date  (106 lignes remontées)
CREATE INDEX idx_cotation_date ON cotation (date_seance DESC);


-- =============================================================================
-- 4. POSITION — le portefeuille  ⚠️ DONNÉES PERSONNELLES (RGPD)
-- =============================================================================
-- Quantités et prix de revient = situation financière d'une personne physique.
-- Traitement inscrit au registre : voir db/RGPD-registre-des-traitements.md.
-- Base légale : intérêt légitime de la personne concernée, qui est l'utilisateur
-- lui-même et le seul destinataire.
CREATE TABLE position (
    id              SERIAL PRIMARY KEY,
    ticker          VARCHAR(16)   NOT NULL REFERENCES valeur (ticker),
    quantite        NUMERIC(16,4) NOT NULL,
    pru             NUMERIC(14,4) NOT NULL,
    devise          CHAR(3)       NOT NULL DEFAULT 'EUR',
    date_achat      DATE,
    importe_le      TIMESTAMPTZ   NOT NULL DEFAULT now(),

    CONSTRAINT quantite_positive CHECK (quantite > 0),
    CONSTRAINT pru_positif       CHECK (pru > 0)
);

COMMENT ON TABLE position IS
    'DONNEES PERSONNELLES (RGPD) : situation financiere de l utilisateur. '
    'Purge et procedures de tri decrites dans db/RGPD-registre-des-traitements.md.';

-- Requête Q2 : « la performance de chaque ligne du portefeuille ».
CREATE INDEX idx_position_ticker ON position (ticker);


-- =============================================================================
-- 5. TAUX_CHANGE — les taux BCE, pour valoriser les lignes en devise étrangère
-- =============================================================================
-- Sans cette table, le total du portefeuille additionne des euros et des dollars —
-- un nombre dépourvu de sens (constaté par sources/positions.py : 26 700,95 « bruts »).
CREATE TABLE taux_change (
    devise          CHAR(3)       NOT NULL,
    date_taux       DATE          NOT NULL,
    valeur_pour_eur NUMERIC(14,6) NOT NULL,

    PRIMARY KEY (devise, date_taux),
    CONSTRAINT taux_positif CHECK (valeur_pour_eur > 0)
);

COMMENT ON COLUMN taux_change.valeur_pour_eur IS
    'Combien d unites de cette devise vaut 1 EUR (convention BCE). USD=1.138 -> 1 EUR = 1,138 USD.';


-- =============================================================================
-- 6. ARTICLE — actualités RSS
-- =============================================================================
CREATE TABLE article (
    id                  SERIAL PRIMARY KEY,
    source              VARCHAR(40)  NOT NULL,
    titre               TEXT         NOT NULL,
    lien                TEXT         NOT NULL UNIQUE,   -- dédoublonnage naturel
    publie_le           TIMESTAMPTZ,
    resume              TEXT,

    -- Trace du garde-fou d'injection (C17). Un article bloqué est CONSERVÉ pour audit,
    -- mais ne doit jamais être envoyé au LLM : la colonne sert de filtre à la lecture.
    bloque_injection    BOOLEAN      NOT NULL DEFAULT FALSE,
    motifs_injection    TEXT[],

    collecte_le         TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Requête Q5 : « les articles des dernières 24 h, hors articles bloqués ».
-- Index PARTIEL : il n'indexe que les lignes lisibles. Plus petit, donc plus rapide,
-- et il exprime la règle métier dans la structure même.
CREATE INDEX idx_article_publie ON article (publie_le DESC)
    WHERE bloque_injection = FALSE;


-- =============================================================================
-- 7. MEMORY_AUDIT — journal des écritures en mémoire des agents
-- =============================================================================
-- Prévu au plan 5.2. Standard Velmo 2.0 : une mémoire d'agent qui s'écrit sans trace
-- est une mémoire qu'on ne peut ni déboguer ni expliquer au jury.
CREATE TABLE memory_audit (
    id              BIGSERIAL PRIMARY KEY,
    agent           VARCHAR(40)  NOT NULL,
    type_memoire    VARCHAR(20)  NOT NULL
        CHECK (type_memoire IN ('court_terme', 'long_terme', 'episodique', 'semantique')),
    operation       VARCHAR(10)  NOT NULL CHECK (operation IN ('lecture', 'ecriture')),
    cle             TEXT,
    resume          TEXT,
    horodatage      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX idx_memory_audit_agent_date ON memory_audit (agent, horodatage DESC);


-- =============================================================================
-- VUE — le briefing quotidien, requête Q1 + Q2 assemblées
-- =============================================================================
-- Justifie à elle seule idx_cotation_ticker_date : DISTINCT ON (ticker) ... ORDER BY
-- ticker, date_seance DESC est exactement le motif d'accès que cet index sert.
CREATE VIEW v_portefeuille_valorise AS
WITH derniere_cotation AS (
    SELECT DISTINCT ON (ticker)
           ticker, date_seance, cloture
    FROM   cotation
    ORDER  BY ticker, date_seance DESC
)
SELECT  v.ticker,
        v.nom_officiel,
        v.statut_qualite,
        p.quantite,
        p.pru,
        p.devise,
        d.date_seance                              AS date_cours,
        d.cloture                                  AS cours_actuel,
        ROUND(p.quantite * p.pru, 2)               AS montant_investi,
        ROUND(p.quantite * d.cloture, 2)           AS valorisation,
        ROUND((d.cloture - p.pru) / p.pru * 100, 2) AS performance_pct
FROM        position p
JOIN        valeur   v ON v.ticker = p.ticker
LEFT JOIN   derniere_cotation d ON d.ticker = p.ticker;

COMMENT ON VIEW v_portefeuille_valorise IS
    'Briefing quotidien. LEFT JOIN volontaire : une position sans cotation doit rester '
    'visible avec un cours NULL, sinon elle disparait silencieusement du briefing.';

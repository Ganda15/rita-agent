-- =============================================================================
-- Migration du 03/10/2026 : journal des appels MCP (plan 62, chapitre Donnees 3.7, C20)
-- =============================================================================
-- Rejouable : chaque ordre est idempotent. Application :
--   psql -U rita -d rita -p 5433 -v ON_ERROR_STOP=1 -f db/migration-2026-10-03-mcp-calls.sql
-- Verification : SELECT statut, COUNT(*) FROM mcp_calls GROUP BY 1;

BEGIN;

CREATE TABLE IF NOT EXISTS mcp_calls (
    id                BIGSERIAL    PRIMARY KEY,
    request_id        VARCHAR(64)  NOT NULL,
    client_id         VARCHAR(40)  NOT NULL,
    outil             VARCHAR(60)  NOT NULL,
    statut            VARCHAR(10)  NOT NULL CHECK (statut IN ('succes', 'refuse', 'erreur')),
    code_erreur       VARCHAR(40),
    duree_ms          INTEGER      CHECK (duree_ms IS NULL OR duree_ms >= 0),
    version_politique VARCHAR(40)  NOT NULL,
    horodatage        TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_mcp_calls_horodatage ON mcp_calls (horodatage DESC);

COMMENT ON TABLE mcp_calls IS
    'Journal des appels MCP (C20, chapitre Donnees 3.7, plan 62). Aucun parametre brut, aucun '
    'prompt, aucune cle, aucun chiffre de portefeuille : seulement qui, quel outil, quel resultat, '
    'quand. Retention 90 jours (procedure P6). Ecrit par l API seule, jamais par la passerelle.';

COMMIT;

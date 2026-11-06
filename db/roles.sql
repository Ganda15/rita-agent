-- Rôles PostgreSQL de RITA — moindre privilège (C11, OWASP).
--
-- `rita`          : propriétaire, seul à écrire (importer.py, pipelines/ingest.py).
-- `rita_lecture`  : LECTURE SEULE, pour tout outil d'agent (serveur MCP, script d'exploration,
--                   text-to-SQL). Un agent qui explore ne doit jamais pouvoir écrire.
--                   Item 8 du harnais (19/09/2026). Prouvé par tests/test_role_lecture.py.
--
-- Appliquer (une fois, en propriétaire) :
--   "C:\Program Files\PostgreSQL\18\bin\psql.exe" "<DATABASE_URL>" -f db\roles.sql
-- Puis, à la main, le mot de passe (jamais dans un fichier versionné) :
--   ALTER ROLE rita_lecture PASSWORD '...';
-- et dans .env : RITA_DSN_LECTURE=postgresql://rita_lecture:...@localhost:5433/<base>

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rita_lecture') THEN
    CREATE ROLE rita_lecture LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
  END IF;
END $$;

GRANT USAGE ON SCHEMA public TO rita_lecture;
REVOKE CREATE ON SCHEMA public FROM rita_lecture;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rita_lecture;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO rita_lecture;
-- Les tables créées plus tard par le propriétaire restent lisibles, jamais modifiables.
ALTER DEFAULT PRIVILEGES FOR ROLE rita IN SCHEMA public GRANT SELECT ON TABLES TO rita_lecture;
ALTER DEFAULT PRIVILEGES FOR ROLE rita IN SCHEMA public GRANT SELECT ON SEQUENCES TO rita_lecture;

-- Le proprietaire peut prendre le role (SET ROLE rita_lecture) : c est ce que font les tests pour prouver
-- les refus sans mot de passe. Membership seulement ; rita_lecture n a aucun droit de plus.
GRANT rita_lecture TO rita;

-- `rita_api` : le rôle de l'API (carte #76, plan validé par Era le 06/11/2026). La matrice d'accès validée le 03/10 donne
-- à l'API la LECTURE des tables qu'elle sert et l'ÉCRITURE du seul journal d'audit `mcp_calls` ; jusqu'ici, elle se
-- connectait avec le propriétaire. Prouvé par tests/test_role_api.py. Mot de passe posé à la main, jamais ici :
--   ALTER ROLE rita_api PASSWORD '...';
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rita_api') THEN
    CREATE ROLE rita_api LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
  END IF;
END $$;

GRANT USAGE ON SCHEMA public TO rita_api;
REVOKE CREATE ON SCHEMA public FROM rita_api;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO rita_api;
-- Le journal d'audit : ajouter une ligne, rien d'autre (ni la modifier, ni l'effacer).
GRANT INSERT ON mcp_calls TO rita_api;
GRANT USAGE ON SEQUENCE mcp_calls_id_seq TO rita_api;
-- Les tables créées plus tard par le propriétaire restent lisibles, jamais modifiables.
ALTER DEFAULT PRIVILEGES FOR ROLE rita IN SCHEMA public GRANT SELECT ON TABLES TO rita_api;
GRANT rita_api TO rita;

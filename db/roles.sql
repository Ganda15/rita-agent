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

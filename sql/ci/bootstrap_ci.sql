-- CI bootstrap: create minimal analytics surface with correct ownership + RBAC
-- Target: ephemeral GitHub Actions Postgres service (local 127.0.0.1)

-- 1) Ensure roles exist (match Azure naming)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_owner') THEN
    CREATE ROLE analytics_owner NOLOGIN;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_readonly') THEN
    CREATE ROLE analytics_readonly NOLOGIN;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'phcadmin') THEN
    CREATE ROLE phcadmin NOLOGIN;
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'etl_user') THEN
    CREATE ROLE etl_user NOLOGIN;
  END IF;
END $$;

-- 2) Ensure current admin can assume analytics_owner (so we can create owned objects)
DO $$
BEGIN
  EXECUTE format('GRANT analytics_owner TO %I', current_user);
END $$;

-- 3) Defense-in-depth memberships (as in Azure)
GRANT analytics_owner TO phcadmin;
GRANT analytics_owner TO etl_user;

-- 4) Ensure analytics_owner can create schema in this database (CI-only)
DO $$
BEGIN
  EXECUTE format('GRANT CONNECT ON DATABASE %I TO analytics_owner', current_database());
  EXECUTE format('GRANT CREATE  ON DATABASE %I TO analytics_owner', current_database());
END $$;

-- 5) Create schema + objects as analytics_owner (deterministic ownership)
SET ROLE analytics_owner;

CREATE SCHEMA IF NOT EXISTS analytics AUTHORIZATION analytics_owner;

CREATE TABLE IF NOT EXISTS analytics.__ci_smoke (
  id integer PRIMARY KEY
);

CREATE OR REPLACE VIEW analytics.__ci_smoke_v AS
SELECT id FROM analytics.__ci_smoke;

RESET ROLE;

-- 6) Readonly access contract
GRANT USAGE ON SCHEMA analytics TO analytics_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO analytics_readonly;

ALTER DEFAULT PRIVILEGES FOR ROLE analytics_owner IN SCHEMA analytics
  GRANT SELECT ON TABLES TO analytics_readonly;

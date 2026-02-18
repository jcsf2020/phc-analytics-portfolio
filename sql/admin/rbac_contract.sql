-- Sprint 29 — RBAC Contract (Azure Postgres)
-- Purpose: Make permissions reproducible and audit-friendly.
-- Safe to re-run (idempotent where possible).

-- 1) Readonly role (already exists in our environment, but keep contract explicit)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_readonly') THEN
    CREATE ROLE analytics_readonly LOGIN;
  END IF;
END
$$;

-- 2) Owner role (should already exist from Sprint 28)
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_owner') THEN
    CREATE ROLE analytics_owner NOLOGIN;
  END IF;
END
$$;

-- 3) Access: database + schema
GRANT CONNECT ON DATABASE phc_analytics TO analytics_readonly;
GRANT USAGE ON SCHEMA analytics TO analytics_readonly;

-- 4) Access: current objects (tables/views/matviews)
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO analytics_readonly;

-- 5) Access: future objects created by the schema owner
-- Default privileges are per "grantor". We standardize ownership under analytics_owner
-- so future tables/views created by analytics_owner stay readable by analytics_readonly.
ALTER DEFAULT PRIVILEGES FOR ROLE analytics_owner IN SCHEMA analytics
GRANT SELECT ON TABLES TO analytics_readonly;

-- 6) Optional: allow admins to assume owner role (defense-in-depth)
GRANT analytics_owner TO phcadmin;
GRANT analytics_owner TO etl_user;

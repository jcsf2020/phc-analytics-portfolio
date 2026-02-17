-- Sprint 28 — Ownership hardening (Azure)
-- Idempotent role + ownership alignment for schema analytics

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_owner') THEN
    CREATE ROLE analytics_owner NOLOGIN;
  END IF;
END
$$;

-- Ensure admins can assume ownership role (defense-in-depth)
GRANT analytics_owner TO phcadmin;
GRANT analytics_owner TO etl_user;

-- Schema owner
ALTER SCHEMA analytics OWNER TO analytics_owner;

-- Tables + views + matviews (no sequences here; sequences owned via table owner)
DO $$
DECLARE r record;
BEGIN
  FOR r IN
    SELECT format('%I.%I', n.nspname, c.relname) AS fqname,
           c.relkind
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'analytics'
      AND c.relkind IN ('r','p','v','m','f')
  LOOP
    IF r.relkind IN ('r','p') THEN
      EXECUTE 'ALTER TABLE ' || r.fqname || ' OWNER TO analytics_owner';
    ELSIF r.relkind IN ('v','m') THEN
      EXECUTE 'ALTER VIEW ' || r.fqname || ' OWNER TO analytics_owner';
    ELSIF r.relkind = 'f' THEN
      EXECUTE 'ALTER FOREIGN TABLE ' || r.fqname || ' OWNER TO analytics_owner';
    END IF;
  END LOOP;
END $$;

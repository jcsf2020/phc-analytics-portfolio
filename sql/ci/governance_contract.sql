-- Governance Contract (RBAC) - CI validation
-- Runs after bootstrap_ci.sql on the ephemeral Postgres service.
-- Every check raises an exception with a contract_violation prefix on failure.
-- No rows are expected; success = zero exceptions.

-- A) Required roles must exist
DO $$
DECLARE
  r text;
BEGIN
  FOREACH r IN ARRAY ARRAY['analytics_owner','analytics_readonly','phcadmin','etl_user']
  LOOP
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
      RAISE EXCEPTION 'contract_violation: role % does not exist', r;
    END IF;
  END LOOP;
END $$;

-- B) Schema analytics must exist and be owned by analytics_owner
DO $$
DECLARE
  owner_name text;
BEGIN
  SELECT r.rolname INTO owner_name
  FROM pg_namespace n
  JOIN pg_roles r ON r.oid = n.nspowner
  WHERE n.nspname = 'analytics';

  IF owner_name IS NULL THEN
    RAISE EXCEPTION 'contract_violation: schema analytics does not exist';
  END IF;

  IF owner_name <> 'analytics_owner' THEN
    RAISE EXCEPTION 'contract_violation: schema analytics owner is %, expected analytics_owner', owner_name;
  END IF;
END $$;

-- C1) analytics_readonly must have CONNECT on database
DO $$
BEGIN
  IF NOT has_database_privilege('analytics_readonly', current_database(), 'CONNECT') THEN
    RAISE EXCEPTION 'contract_violation: analytics_readonly lacks CONNECT on database %', current_database();
  END IF;
END $$;

-- C2) analytics_readonly must have USAGE on schema analytics
DO $$
BEGIN
  IF NOT has_schema_privilege('analytics_readonly', 'analytics', 'USAGE') THEN
    RAISE EXCEPTION 'contract_violation: analytics_readonly lacks USAGE on schema analytics';
  END IF;
END $$;

-- C3) analytics_readonly must have SELECT on every table/view/materialized view in analytics
DO $$
DECLARE
  obj_name text;
BEGIN
  FOR obj_name IN
    SELECT c.relname
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname = 'analytics'
      AND c.relkind IN ('r', 'v', 'm')
  LOOP
    IF NOT has_table_privilege('analytics_readonly', 'analytics.' || obj_name, 'SELECT') THEN
      RAISE EXCEPTION 'contract_violation: analytics_readonly lacks SELECT on analytics.%', obj_name;
    END IF;
  END LOOP;
END $$;

-- C4) Default privileges: analytics_owner must auto-grant SELECT on new tables to analytics_readonly
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_default_acl da
    JOIN pg_roles dr ON dr.oid = da.defaclrole
    JOIN pg_namespace n  ON n.oid  = da.defaclnamespace
    WHERE dr.rolname        = 'analytics_owner'
      AND n.nspname         = 'analytics'
      AND da.defaclobjtype  = 'r'   -- tables
      AND EXISTS (
        SELECT 1
        FROM unnest(da.defaclacl) AS acl(entry)
        WHERE acl.entry::text LIKE 'analytics_readonly=%r%'
      )
  ) THEN
    RAISE EXCEPTION
      'contract_violation: default SELECT privilege for analytics_readonly not configured in schema analytics';
  END IF;
END $$;

-- D) Defense-in-depth: phcadmin and etl_user must be members of analytics_owner
DO $$
DECLARE
  m text;
BEGIN
  FOREACH m IN ARRAY ARRAY['phcadmin','etl_user']
  LOOP
    IF NOT EXISTS (
      SELECT 1
      FROM pg_auth_members am
      JOIN pg_roles grp ON grp.oid = am.roleid
      JOIN pg_roles mem ON mem.oid = am.member
      WHERE grp.rolname = 'analytics_owner'
        AND mem.rolname = m
    ) THEN
      RAISE EXCEPTION 'contract_violation: % is not a member of analytics_owner', m;
    END IF;
  END LOOP;
END $$;

-- Observability: start a pipeline run (INSERT)
-- Contract:
--  - inserts exactly 1 row in analytics.pipeline_run_log
--  - returns run_id (uuid) to be used by finish scripts
--
-- Usage:
--   psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
--     -v pipeline_name='phc_analytics' -v environment='local' \
--     -f observability/sql/02_run_start.sql
--
-- Output:
--   single row containing run_id

\set ON_ERROR_STOP on

-- Safety: require variables
\if :{?pipeline_name}
\else
  \echo 'ERROR: missing -v pipeline_name=...'
  \quit 2
\endif

\if :{?environment}
\else
  \echo 'ERROR: missing -v environment=...'
  \quit 2
\endif

with ins as (
  insert into analytics.pipeline_run_log (
    run_id,
    pipeline_name,
    environment,
    status,
    started_at
  )
  values (
    gen_random_uuid(),
    :'pipeline_name',
    :'environment',
    'started',
    now()
  )
  returning run_id
)
select run_id::text from ins;

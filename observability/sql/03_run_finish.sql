-- Observability: finalize a pipeline run
-- Contract:
--  - Updates an existing row in analytics.pipeline_run_log
--  - Sets finished_at, status, duration_seconds
--  - Optionally sets rows_processed and error_message
--
-- Required psql vars:
--   - run_id (uuid)
--   - status (success|failed)
-- Optional psql vars:
--   - rows_processed (bigint)      (default: NULL)
--   - error_message (text)         (default: NULL)
--
-- NOTE: This file is intentionally **SQL-only** (no psql meta-commands like \if/\set)
-- to avoid CI/local parsing issues.
with upd as (
    update analytics.pipeline_run_log
    set status = :'status',
        finished_at = now(),
        duration_seconds = round(
            extract(
                epoch
                from (now() - started_at)
            )::numeric,
            2
        ),
        rows_processed = nullif(btrim(:'rows_processed'), '')::bigint,
        error_message = case
            when :'error_message' is null
            or btrim(:'error_message') = '' then null
            else btrim(:'error_message')
        end
    where run_id = (:'run_id')::uuid
    returning run_id,
        pipeline_name,
        environment,
        status,
        started_at,
        finished_at,
        duration_seconds,
        rows_processed,
        error_message
)
select run_id::text,
    pipeline_name,
    environment,
    status,
    started_at,
    finished_at,
    duration_seconds,
    coalesce(rows_processed::text, '') as rows_processed,
    coalesce(error_message, '') as error_message
from upd;
-- Observability: health check for last pipeline run
-- Contract (health-gate style):
--   - Returns 0 rows when healthy
--   - Returns 1+ rows describing failures / risks when unhealthy
--
-- Required psql vars:
--   - pipeline_name (text)
--   - environment   (text)   e.g. local, ci, prod
-- Optional psql vars:
--   - max_age_minutes (int)  freshness threshold; default 1440 (24h)
--
with params as (
select btrim(:'pipeline_name') as pipeline_name,
    btrim(:'environment') as environment,
    case
        when :'max_age_minutes' is null
        or btrim(:'max_age_minutes') = '' then 1440
        else (:'max_age_minutes')::int
    end as max_age_minutes
),
last_run as (
    select l.run_id,
        l.pipeline_name,
        l.environment,
        l.status,
        l.started_at,
        l.finished_at,
        l.duration_seconds,
        l.rows_processed,
        l.error_message
    from analytics.pipeline_run_log l
        join params p on l.pipeline_name = p.pipeline_name
        and l.environment = p.environment
    order by l.started_at desc
    limit 1
), checks as (
    select p.pipeline_name,
        p.environment,
        p.max_age_minutes,
        lr.run_id,
        lr.status,
        lr.started_at,
        lr.finished_at,
        lr.duration_seconds,
        lr.rows_processed,
        lr.error_message,
        (lr.run_id is not null) as has_run,
        (lr.status = 'success') as is_success,
        (lr.finished_at is not null) as has_finished,
        case
            when lr.finished_at is null then null
            else (now() - lr.finished_at)
        end as age_interval,
        case
            when lr.finished_at is null then null
            else (now() - lr.finished_at) <= (
                (p.max_age_minutes::text || ' minutes')::interval
            )
        end as is_fresh
    from params p
        left join last_run lr on true
),
violations as (
    select 'NO_RUN' as code,
        'No run found for pipeline/environment' as message,
        c.pipeline_name,
        c.environment,
        null::text as run_id,
        null::text as status,
        null::timestamptz as started_at,
        null::timestamptz as finished_at,
        null::numeric as duration_seconds,
        null::bigint as rows_processed,
        null::text as error_message,
        null::text as age
    from checks c
    where not c.has_run
    union all
    select 'LAST_RUN_NOT_SUCCESS' as code,
        'Last run did not succeed' as message,
        c.pipeline_name,
        c.environment,
        c.run_id::text as run_id,
        c.status as status,
        c.started_at,
        c.finished_at,
        c.duration_seconds,
        c.rows_processed,
        c.error_message,
        coalesce(c.age_interval::text, '') as age
    from checks c
    where c.has_run
        and not c.is_success
    union all
    select 'LAST_RUN_NOT_FINISHED' as code,
        'Last run has no finished_at (possibly stuck)' as message,
        c.pipeline_name,
        c.environment,
        c.run_id::text as run_id,
        c.status as status,
        c.started_at,
        c.finished_at,
        c.duration_seconds,
        c.rows_processed,
        c.error_message,
        coalesce(c.age_interval::text, '') as age
    from checks c
    where c.has_run
        and c.is_success
        and not c.has_finished
    union all
    select 'STALE' as code,
        'Last successful run is older than freshness threshold' as message,
        c.pipeline_name,
        c.environment,
        c.run_id::text as run_id,
        c.status as status,
        c.started_at,
        c.finished_at,
        c.duration_seconds,
        c.rows_processed,
        c.error_message,
        coalesce(c.age_interval::text, '') as age
    from checks c
    where c.has_run
        and c.is_success
        and c.has_finished
        and (c.is_fresh is false)
)
select code,
    message,
    pipeline_name,
    environment,
    run_id,
    status,
    started_at,
    finished_at,
    duration_seconds,
    rows_processed,
    error_message,
    age
from violations
order by code;
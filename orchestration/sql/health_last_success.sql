/*
 Health gate: require a SUCCESS run in last N minutes.
 
 Output:
 1 -> OK
 0 -> FAIL
 
 psql vars:
 :pipeline_name
 :environment
 :max_age_minutes
 */
with s as (
  select count(*) filter (
      where status = 'success'
    ) as success_total,
    count(*) filter (
      where status = 'success'
        and started_at >= now() - (
          (:'max_age_minutes'::int || ' minutes')::interval
        )
    ) as success_recent
  from analytics.pipeline_run_log
  where pipeline_name = :'pipeline_name'
    and environment = :'environment'
)
select case
    when (
      select success_total
      from s
    ) = 0 then 1
    when (
      select success_recent
      from s
    ) > 0 then 1
    else 0
  end;

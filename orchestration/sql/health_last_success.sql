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
select
  case when exists (
    select 1
    from analytics.pipeline_run_log
    where pipeline_name = :'pipeline_name'
      and environment   = :'environment'
      and status        = 'success'
      and started_at >= now()
        - (:'max_age_minutes'::int || ' minutes')::interval
  )
  then 1 else 0 end;

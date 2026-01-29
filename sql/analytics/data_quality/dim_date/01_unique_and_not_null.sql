-- Data Quality Check: dim_date uniqueness and not-null
-- Contract: this query MUST return 0 rows to PASS
--
-- Why:
-- - `analytics.dim_date` uses `date_id` (date) as the natural day key.
-- - `date_key` (int) is a common surrogate-style key (YYYYMMDD).
--
-- Rules enforced:
-- 1) date_id is NOT NULL and UNIQUE
-- 2) date_key is NOT NULL and UNIQUE
with base as (
  select date_id,
    date_key
  from analytics.dim_date
),
null_date_id as (
  select 'NULL_DATE_ID' as issue_type,
    null::text as offending_value
  from base
  where date_id is null
),
dup_date_id as (
  select 'DUPLICATE_DATE_ID' as issue_type,
    date_id::text as offending_value
  from (
      select date_id
      from base
      where date_id is not null
      group by date_id
      having count(*) > 1
    ) d
),
null_date_key as (
  select 'NULL_DATE_KEY' as issue_type,
    null::text as offending_value
  from base
  where date_key is null
),
dup_date_key as (
  select 'DUPLICATE_DATE_KEY' as issue_type,
    date_key::text as offending_value
  from (
      select date_key
      from base
      where date_key is not null
      group by date_key
      having count(*) > 1
    ) d
)
select *
from null_date_id
union all
select *
from dup_date_id
union all
select *
from null_date_key
union all
select *
from dup_date_key
order by issue_type,
  offending_value;
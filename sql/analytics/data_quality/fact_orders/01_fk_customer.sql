-- Data Quality Check: fact_orders -> dim_customer (FK integrity)
-- Purpose:
--   Ensure every fact_orders.customer_id maps to an existing dim_customer.customer_nk.
--
-- Contract:
--   - This query MUST return zero rows to PASS.
--   - Any returned row represents a DATA QUALITY FAILURE.
--
-- Notes:
--   - We normalize keys with btrim() to avoid false failures caused by whitespace.
--   - We also coerce empty strings to NULL so they are treated as invalid IDs.
with fact_customers as (
    select distinct nullif(btrim(customer_id), '') as customer_id
    from analytics.fact_orders
),
invalid_customer_ids as (
    select customer_id
    from fact_customers
    where customer_id is null
),
missing_in_dim as (
    select f.customer_id
    from fact_customers f
        left join analytics.dim_customer d on d.is_current = true
        and btrim(d.customer_nk) = f.customer_id
    where f.customer_id is not null
        and d.customer_nk is null
)
select 'INVALID_CUSTOMER_ID' as issue_type,
    customer_id
from invalid_customer_ids
union all
select 'MISSING_DIM_CUSTOMER' as issue_type,
    customer_id
from missing_in_dim
order by issue_type,
    customer_id;
-- Data Quality Check: fact_orders -> dim_customer (FK integrity)
-- Purpose:
--   Ensure every fact_orders.customer_id maps to an existing dim_customer.customer_nk.
--
-- Contract:
--   - This query MUST return zero rows to PASS.
--   - Any returned row represents a DATA QUALITY FAILURE.
with fact_customers as (
    select distinct customer_id
    from analytics.fact_orders
),
invalid_customer_ids as (
    select customer_id
    from fact_customers
    where customer_id is null
        or btrim(customer_id) = ''
),
missing_in_dim as (
    select f.customer_id
    from fact_customers f
        left join analytics.dim_customer d on d.is_current = true
        and d.customer_nk = f.customer_id
    where f.customer_id is not null
        and btrim(f.customer_id) <> ''
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
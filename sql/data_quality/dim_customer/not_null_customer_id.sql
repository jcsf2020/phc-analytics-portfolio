-- DQ: dim_customer.customer_id NOT NULL
-- Contract:
-- - 0 rows => PASS
-- - 1+ rows => FAIL
select customer_nk
from analytics.dim_customer
where customer_nk is null
limit 1;

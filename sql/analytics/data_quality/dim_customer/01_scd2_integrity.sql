-- Data Quality checks - analytics.dim_customer (SCD2)
-- Contract: OK = 0 rows returned (any returned row = violation)
-- Target: validate temporal integrity for SCD2 dimensions.
-- Q0) No duplicate versions for the same NK at the same valid_from (should be unique)
-- OK = 0 rows
SELECT customer_nk,
  valid_from,
  COUNT(*) AS version_rows
FROM analytics.dim_customer
GROUP BY customer_nk,
  valid_from
HAVING COUNT(*) > 1;
-- Q1) Exactly 1 current version per customer_nk
-- OK = 0 rows
SELECT customer_nk,
  COUNT(*) AS current_rows
FROM analytics.dim_customer
WHERE is_current = TRUE
GROUP BY customer_nk
HAVING COUNT(*) <> 1;
-- Q2) Consistency between is_current and valid_to
-- Rule: current => valid_to IS NULL; non-current => valid_to IS NOT NULL
-- OK = 0 rows
SELECT customer_nk,
  customer_sk,
  valid_from,
  valid_to,
  is_current
FROM analytics.dim_customer
WHERE NOT (
    (
      is_current = TRUE
      AND valid_to IS NULL
    )
    OR (
      is_current = FALSE
      AND valid_to IS NOT NULL
    )
  );
-- Q3) Valid temporal range (valid_to >= valid_from when valid_to is present)
-- OK = 0 rows
SELECT customer_nk,
  customer_sk,
  valid_from,
  valid_to
FROM analytics.dim_customer
WHERE valid_to IS NOT NULL
  AND valid_to < valid_from;
-- Q4) No overlaps per NK (SCD2 must not have overlapping intervals)
-- Overlap condition: a_from < b_to AND a_to > b_from (treat NULL valid_to as infinity)
-- OK = 0 rows
SELECT a.customer_nk,
  a.customer_sk AS a_sk,
  a.valid_from AS a_from,
  a.valid_to AS a_to,
  b.customer_sk AS b_sk,
  b.valid_from AS b_from,
  b.valid_to AS b_to
FROM analytics.dim_customer a
  JOIN analytics.dim_customer b ON a.customer_nk = b.customer_nk
  AND a.customer_sk <> b.customer_sk
  AND a.valid_from < COALESCE(b.valid_to, 'infinity'::timestamptz)
  AND COALESCE(a.valid_to, 'infinity'::timestamptz) > b.valid_from
WHERE a.customer_sk < b.customer_sk;
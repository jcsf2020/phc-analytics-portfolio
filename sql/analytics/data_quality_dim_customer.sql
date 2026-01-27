-- Data Quality checks — analytics.dim_customer (SCD2)
-- Regra geral: OK = 0 rows (qualquer row retornada = violacao)

-- Q1) 1 versao current por customer_nk
-- OK = 0 rows
SELECT
  customer_nk,
  COUNT(*) AS current_rows
FROM analytics.dim_customer
WHERE is_current = TRUE
GROUP BY customer_nk
HAVING COUNT(*) <> 1;

-- Q2) Consistencia entre is_current e valid_to
-- OK = 0 rows
SELECT
  customer_nk,
  customer_sk,
  valid_from,
  valid_to,
  is_current
FROM analytics.dim_customer
WHERE NOT (
  (is_current = TRUE  AND valid_to IS NULL) OR
  (is_current = FALSE AND valid_to IS NOT NULL)
);

-- Q3) Intervalo temporal valido
-- OK = 0 rows
SELECT
  customer_nk,
  customer_sk,
  valid_from,
  valid_to
FROM analytics.dim_customer
WHERE valid_to IS NOT NULL
  AND valid_to < valid_from;

-- Q4) Overlaps por NK (SCD2 nao pode ter intervalos que se sobrepoem)
-- OK = 0 rows
SELECT
  a.customer_nk,
  a.customer_sk AS a_sk,
  a.valid_from  AS a_from,
  a.valid_to    AS a_to,
  b.customer_sk AS b_sk,
  b.valid_from  AS b_from,
  b.valid_to    AS b_to
FROM analytics.dim_customer a
JOIN analytics.dim_customer b
  ON a.customer_nk = b.customer_nk
 AND a.customer_sk <> b.customer_sk
 AND a.valid_from < COALESCE(b.valid_to, 'infinity'::timestamptz)
 AND COALESCE(a.valid_to, 'infinity'::timestamptz) > b.valid_from
WHERE a.customer_sk < b.customer_sk;

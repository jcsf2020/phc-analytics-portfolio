-- Target: PostgreSQL
-- Purpose: deterministic date dimension for analytics.
-- Notes:
--   * Rebuilds the dimension (drops any existing view/table named analytics.dim_date).
--   * Idempotent insert (ON CONFLICT DO NOTHING).
-- Range:
--   * 2020-01-01 to 2030-12-31 (inclusive) -> 4018 rows.
BEGIN;
CREATE SCHEMA IF NOT EXISTS analytics;
-- If something named analytics.dim_date already exists, drop it safely whether it is a VIEW or a TABLE.
DO $$
DECLARE relkind "char";
BEGIN
SELECT c.relkind INTO relkind
FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'analytics'
    AND c.relname = 'dim_date'
LIMIT 1;
IF relkind IS NULL THEN -- nothing to drop
RETURN;
END IF;
IF relkind IN ('v', 'm') THEN EXECUTE 'DROP VIEW IF EXISTS analytics.dim_date CASCADE';
ELSE EXECUTE 'DROP TABLE IF EXISTS analytics.dim_date CASCADE';
END IF;
END $$;
CREATE TABLE analytics.dim_date (
    -- Natural key
    date_id DATE PRIMARY KEY,
    -- Surrogate/int key for joins (YYYYMMDD)
    date_key INTEGER NOT NULL UNIQUE,
    year SMALLINT NOT NULL,
    quarter SMALLINT NOT NULL CHECK (
        quarter BETWEEN 1 AND 4
    ),
    month SMALLINT NOT NULL CHECK (
        month BETWEEN 1 AND 12
    ),
    day SMALLINT NOT NULL CHECK (
        day BETWEEN 1 AND 31
    ),
    iso_year SMALLINT NOT NULL,
    iso_week SMALLINT NOT NULL CHECK (
        iso_week BETWEEN 1 AND 53
    ),
    day_of_week SMALLINT NOT NULL CHECK (
        day_of_week BETWEEN 1 AND 7
    ),
    month_name TEXT NOT NULL,
    day_name TEXT NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_month_start BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    is_quarter_start BOOLEAN NOT NULL,
    is_quarter_end BOOLEAN NOT NULL,
    is_year_start BOOLEAN NOT NULL,
    is_year_end BOOLEAN NOT NULL
);
-- Populate a fixed range (inclusive). Designed to be re-runnable.
WITH params AS (
    SELECT DATE '2020-01-01' AS start_date,
        DATE '2030-12-31' AS end_date
),
d AS (
    SELECT gs::date AS date_id
    FROM params p
        CROSS JOIN generate_series(p.start_date, p.end_date, INTERVAL '1 day') AS gs
)
INSERT INTO analytics.dim_date (
        date_id,
        date_key,
        year,
        quarter,
        month,
        day,
        iso_year,
        iso_week,
        day_of_week,
        month_name,
        day_name,
        is_weekend,
        is_month_start,
        is_month_end,
        is_quarter_start,
        is_quarter_end,
        is_year_start,
        is_year_end
    )
SELECT d.date_id,
    (
        EXTRACT(
            YEAR
            FROM d.date_id
        )::int * 10000 + EXTRACT(
            MONTH
            FROM d.date_id
        )::int * 100 + EXTRACT(
            DAY
            FROM d.date_id
        )::int
    ) AS date_key,
    EXTRACT(
        YEAR
        FROM d.date_id
    )::smallint AS year,
    EXTRACT(
        QUARTER
        FROM d.date_id
    )::smallint AS quarter,
    EXTRACT(
        MONTH
        FROM d.date_id
    )::smallint AS month,
    EXTRACT(
        DAY
        FROM d.date_id
    )::smallint AS day,
    EXTRACT(
        ISOYEAR
        FROM d.date_id
    )::smallint AS iso_year,
    EXTRACT(
        WEEK
        FROM d.date_id
    )::smallint AS iso_week,
    EXTRACT(
        ISODOW
        FROM d.date_id
    )::smallint AS day_of_week,
    TRIM(TO_CHAR(d.date_id, 'TMMonth')) AS month_name,
    TRIM(TO_CHAR(d.date_id, 'TMDay')) AS day_name,
    (
        EXTRACT(
            ISODOW
            FROM d.date_id
        ) IN (6, 7)
    ) AS is_weekend,
    (DATE_TRUNC('month', d.date_id) = d.date_id) AS is_month_start,
    (
        (
            DATE_TRUNC('month', d.date_id) + INTERVAL '1 month - 1 day'
        )::date = d.date_id
    ) AS is_month_end,
    (DATE_TRUNC('quarter', d.date_id) = d.date_id) AS is_quarter_start,
    (
        (
            DATE_TRUNC('quarter', d.date_id) + INTERVAL '3 months - 1 day'
        )::date = d.date_id
    ) AS is_quarter_end,
    (DATE_TRUNC('year', d.date_id) = d.date_id) AS is_year_start,
    (
        (
            DATE_TRUNC('year', d.date_id) + INTERVAL '1 year - 1 day'
        )::date = d.date_id
    ) AS is_year_end
FROM d ON CONFLICT (date_id) DO NOTHING;
COMMIT;
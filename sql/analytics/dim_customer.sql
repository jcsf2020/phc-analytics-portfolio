BEGIN;

CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_customer (
  customer_sk      BIGSERIAL PRIMARY KEY,
  customer_nk      TEXT NOT NULL,

  -- business attributes (exemplos; ajustamos no passo seguinte ao mapear o source)
  customer_name    TEXT,
  email            TEXT,
  phone            TEXT,
  country          TEXT,
  city             TEXT,
  is_company       BOOLEAN,

  -- SCD2 fields
  valid_from       TIMESTAMPTZ NOT NULL,
  valid_to         TIMESTAMPTZ NULL,
  is_current       BOOLEAN NOT NULL DEFAULT TRUE,

  -- operational metadata
  source_system    TEXT NOT NULL DEFAULT 'odoo',
  source_table     TEXT,
  source_pk        TEXT,
  hash_diff        TEXT,
  load_run_id      TEXT,
  loaded_at        TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT dim_customer_chk_valid_range
    CHECK (valid_to IS NULL OR valid_to >= valid_from),

  CONSTRAINT dim_customer_chk_current_flag
    CHECK ((is_current = TRUE AND valid_to IS NULL) OR (is_current = FALSE AND valid_to IS NOT NULL))
);

-- 1 versão atual por NK
CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_customer_current
  ON analytics.dim_customer (customer_nk)
  WHERE is_current = TRUE;

-- evita duplicar versões no mesmo instante
CREATE UNIQUE INDEX IF NOT EXISTS ux_dim_customer_nk_from
  ON analytics.dim_customer (customer_nk, valid_from);

COMMIT;

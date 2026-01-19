-- ============================================================
-- PHC_Analytics
-- Sprint 3 - Reproducible analytics bootstrap
-- Purpose:
--   * Raw ingestion tables (append + upsert)
--   * Analytics read models (tables, view, materialized view)
--   * Indexes to support BI-style queries and CONCURRENT refresh
-- Notes:
--   * Safe to re-run (IF NOT EXISTS / OR REPLACE)
--   * Designed for OLTP source -> OLAP/Analytics patterns
-- ============================================================
-- Sprint 3 - Init: raw + analytics objects (reproducible)
-- Database target: odoo_phc_local
-- Schemas
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS analytics;
-- RAW tables
CREATE TABLE IF NOT EXISTS raw.customers (
  source_system TEXT NOT NULL,
  source_customer_id TEXT NOT NULL,
  payload JSONB NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (source_system, source_customer_id)
);
COMMENT ON TABLE raw.customers IS 'Raw customers payloads ingested from source systems (JSONB, upsert by natural key)';
CREATE TABLE IF NOT EXISTS raw.orders (
  source_system TEXT NOT NULL,
  source_order_id TEXT NOT NULL,
  customer_id TEXT NULL,
  payload JSONB NOT NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (source_system, source_order_id)
);
COMMENT ON TABLE raw.orders IS 'Raw orders payloads ingested from source systems (JSONB, upsert by natural key)';
-- ANALYTICS tables
CREATE TABLE IF NOT EXISTS analytics.order_metrics (
  source_system TEXT NOT NULL,
  source_order_id TEXT NOT NULL,
  customer_id TEXT NULL,
  status TEXT NULL,
  total_eur NUMERIC(12, 2) NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (source_system, source_order_id)
);
COMMENT ON TABLE analytics.order_metrics IS 'Analytics-ready order facts extracted from raw.orders (1 row per order)';
CREATE TABLE IF NOT EXISTS analytics.daily_revenue (
  day DATE NOT NULL,
  source_system TEXT NOT NULL,
  status TEXT NOT NULL,
  orders_count INT NOT NULL,
  revenue_eur NUMERIC(12, 2) NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (day, source_system, status)
);
COMMENT ON TABLE analytics.daily_revenue IS 'Daily aggregated revenue by source system and order status';
-- Enriched view (raw join)
CREATE OR REPLACE VIEW analytics.v_orders_enriched AS
SELECT o.source_system,
  o.source_order_id,
  o.customer_id,
  c.payload->>'email' AS customer_email,
  c.payload->>'name' AS customer_name,
  (o.payload->>'total')::numeric(12, 2) AS order_total_eur,
  o.payload->>'currency' AS currency,
  o.payload->>'status' AS order_status,
  o.ingested_at AS order_ingested_at
FROM raw.orders o
  LEFT JOIN raw.customers c ON c.source_system = o.source_system
  AND c.source_customer_id = o.customer_id;
COMMENT ON VIEW analytics.v_orders_enriched IS 'Logical enriched view joining raw orders with raw customers';
-- Materialized view (analytics-read model)
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.mv_orders_enriched AS
SELECT *
FROM analytics.v_orders_enriched WITH NO DATA;
COMMENT ON MATERIALIZED VIEW analytics.mv_orders_enriched IS 'Physical read model for analytics queries (refreshed from v_orders_enriched)';
-- Refresh log
CREATE TABLE IF NOT EXISTS analytics.refresh_log (
  object_name TEXT PRIMARY KEY,
  refreshed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
COMMENT ON TABLE analytics.refresh_log IS 'Tracks last refresh timestamp of materialized views';
-- Indexes for MV (perf + concurrent refresh support)
CREATE INDEX IF NOT EXISTS idx_mv_orders_enriched_ingested_at ON analytics.mv_orders_enriched (order_ingested_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS uq_mv_orders_enriched_key ON analytics.mv_orders_enriched (source_system, source_order_id);
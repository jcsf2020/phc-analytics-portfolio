# PHC Analytics — Production-Ready Data Pipeline (PrestaShop → PostgreSQL)

## Overview

PHC Analytics is an end-to-end data engineering project that ingests operational data from PrestaShop (customers, products, orders) into PostgreSQL and prepares analytics-ready structures using a layered model: **raw → staging → analytics**.

This repository is designed to be **reviewable by recruiters and senior engineers**: clear architecture, reproducible setup, cloud-ready execution, idempotent ingestion patterns, and explicit incremental state management.

---

## Architecture

### High-level flow

PrestaShop (API)
→ PostgreSQL **raw** (JSONB, source-of-truth)
→ PostgreSQL **staging** (state, deduplication, incremental control)
→ PostgreSQL **analytics** (curated models for BI)

### Data layers

- **raw**
  - Immutable source preservation
  - JSONB payloads
  - Replayable ingestion
- **staging**
  - Incremental state (`etl_watermarks`)
  - Deduplication & orchestration support
- **analytics**
  - Curated tables/views
  - BI- and KPI-ready models

---

## Tech Stack

- **Python** — extraction, loading, orchestration
- **PostgreSQL 15** — storage, transformations, permissions
- **SQL** — modeling, constraints, incremental logic
- **Docker Compose** — local reproducibility
- **Azure Database for PostgreSQL – Flexible Server** — cloud environment

---

## Milestones

### Sprint 3 — Production-Ready SQL Analytics Layer (COMPLETED)

- Versioned SQL bootstrap via migrations
- Layered schema structure (`raw`, `staging`, `analytics`)
- Analytics-ready foundation for BI consumption

### Sprint 4 — Azure Cloud Bootstrap & Incremental ETL Foundations (COMPLETED)

Delivered in Azure:

- Azure subscription validated via Azure CLI
- Resource group created and configured
- PostgreSQL Flexible Server provisioned (North Europe)
- Database created: `phc_analytics`
- Schemas created: `raw`, `staging`, `analytics`
- Least-privilege ETL role created: `etl_user`
  - CONNECT on database
  - USAGE on schemas
  - DML (SELECT/INSERT/UPDATE/DELETE) on tables
  - CREATE on `raw` and `staging`
  - Default privileges configured for future objects
- Incremental state table created: `staging.etl_watermarks`
  - Epoch baseline (`1970-01-01`) for first load
  - Entity-level watermarks:
    - `prestashop_orders`
    - `prestashop_customers`
    - `prestashop_products`
- Raw ingestion table pattern validated:
  - JSONB payload
  - Idempotent upserts using `ON CONFLICT DO UPDATE`

### Sprint 5 — Incremental Raw Ingestion (COMPLETED)

- Python pipeline for raw ingestion (PrestaShop → PostgreSQL)
- JSONB source-of-truth tables with deterministic upserts
- Entity-level incremental control via `staging.etl_watermarks`
- Idempotent ingestion validated against Azure PostgreSQL
- Production-safe SQL patterns (`ON CONFLICT DO UPDATE`)

### Sprint 6 — SQL Latest-State Snapshot (raw → staging) (COMPLETED)

Delivered in Azure PostgreSQL:

- Implemented as a VIEW (not a table) to guarantee zero-lag freshness and avoid recomputation orchestration.
- Created a **staging latest-state view** using window functions (`ROW_NUMBER()` + `PARTITION BY` + `ORDER BY DESC`).
- Implemented `staging.prestashop_orders_latest` as a **VIEW** (not a table) for an always-up-to-date snapshot.
- Validated correctness with invariant checks:
  - `latest_rows == COUNT(DISTINCT order_id)`
- Demonstrated JSONB field extraction for inspection:
  - `payload->>'field'`

SQL pattern used:

```sql
CREATE VIEW staging.<entity>_latest AS
SELECT *
FROM (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY <entity_id>
      ORDER BY <updated_at> DESC
    ) AS rn
  FROM raw.<source_table>
) t
WHERE rn = 1;
```

Notes:

- `raw.prestashop_customers` and `raw.prestashop_products` tables are provisioned; latest-state views can be created once data is ingested.

---

## Repository Structure (high level)

- `sql/` — SQL bootstrap and migrations
- `src/` — pipeline code (connectors, ingestion, transformations)
- `docker/` — local services
- `docker-compose*.yml` — reproducible environments
- `docs/` — architecture notes and runbooks

---

## Local Run (Docker Compose)

### Start PostgreSQL locally

```bash
docker compose up -d db
```

---

## Run the Pipeline (example)

```bash
python run_pipeline.py
```

---

## Azure Run — Current Environment

### Connect as admin (bootstrap only)

```bash
psql "postgresql://phcadmin:<PASSWORD>@<SERVER>.postgres.database.azure.com/phc_analytics?sslmode=require"
```

### Connect as ETL user (day-to-day operations)

```bash
psql "postgresql://etl_user:<PASSWORD>@<SERVER>.postgres.database.azure.com/phc_analytics?sslmode=require"
```

### Verify schema privileges

```sql
SELECT n.nspname,
       has_schema_privilege(current_user, n.oid, 'USAGE')  AS can_usage,
       has_schema_privilege(current_user, n.oid, 'CREATE') AS can_create
FROM pg_namespace n
WHERE n.nspname IN ('raw','staging','analytics')
ORDER BY 1;
```

---

## Key Engineering Practices Demonstrated

- Layered warehouse design (raw/staging/analytics)
- JSONB raw ingestion for source-truth preservation
- Idempotent ingestion with deterministic upserts
- Incremental processing via explicit state table
- Least-privilege database roles for pipelines
- Reproducible local + cloud-ready execution

---

### Sprint 7 — Analytics Time Dimension (COMPLETED)

Delivered in PostgreSQL (analytics layer):

- Designed and implemented a production-grade Time Dimension (`analytics.dim_date`)
- Built from a minimal staging source (`staging.dim_date`)
- Enriched with analytics-ready attributes:
  - `quarter`
  - `year_month`
  - `year_quarter`
  - `month_start`, `month_end`
  - `is_month_start`, `is_month_end`
  - `day_of_week`, `day_name`
  - `is_weekend`
- Implemented as a VIEW for transparency and zero-lag freshness
- Validated data completeness and correctness:
  - Date range coverage: 2020-01-01 → 2030-12-31
  - Row count and distinct date invariants
  - Month start/end consistency checks
- Granted read-only access to ETL role (`etl_user`) following least-privilege principles

Outcome:
A reusable, analytics-ready Time Dimension suitable for BI tools, KPI aggregation, and fact-table joins.

## Next Steps

- Automate per-entity watermark updates
- Add data quality checks (nulls, duplicates, schema drift)
- Expand latest-state views to customers/products and introduce basic staging quality checks (row-count invariants, null checks).
- Build analytics-layer dimensions and facts
- Introduce orchestration (Airflow / Prefect)
- BI integration (Power BI / Metabase)
- Cost/performance tuning on Azure

---

## Target Roles

- Data Engineer
- Analytics Engineer
- Modern BI / Analytics Platform Engineer

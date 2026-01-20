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

## Next Steps

- Automate per-entity watermark updates
- Add data quality checks (nulls, duplicates, schema drift)
- Build analytics-layer dimensions and facts
- Introduce orchestration (Airflow / Prefect)
- BI integration (Power BI / Metabase)
- Cost/performance tuning on Azure

---

## Target Roles

- Data Engineer
- Analytics Engineer
- Modern BI / Analytics Platform Engineer

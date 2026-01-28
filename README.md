# PHC Analytics (Portfolio)

Portfolio deliverable of a data engineering / analytics project focused on:

- reproducible local environments (Docker Compose)
- SQL-first analytics assets (dimensions / marts)
- clear repository structure and delivery discipline
- real-world system integration examples (ERP)

> Note: This repo is designed as a portfolio-friendly deliverable.
> It intentionally avoids committing local/editor artifacts
> and binary release files.

## Tech Stack

- **Python** for orchestration / pipeline glue
- **PostgreSQL** as local analytical store (via Docker)
- **SQL** for analytics models (dimensions / marts)
- **Docker Compose** for reproducible environments
- **Odoo** (optional) integration example via addon + compose

## Quickstart

1. Start PostgreSQL

```bash
docker compose up -d db
```

1. Apply SQL assets (example)

> Ensure `DATABASE_URL` is set to your local Postgres connection string.

```bash
psql "$DATABASE_URL" -f sql/analytics/dim_date.sql
```

1. Stop services

```bash
docker compose down
```

## Deliverables

- Analytics SQL assets under `sql/analytics/`
- Pipeline code under `src/` (connectors, ingestion, transformations)
- Local services under `docker/` + `docker-compose*.yml`
- Runbooks / notes under `docs/`
- Optional ERP integration example under `integrations/`

## Project Timeline (Sprints Overview)

This project was developed iteratively using a sprint-based approach.

- **Sprint 1–2 — Foundations**
  Local environment, Docker Compose, repository structure.

- **Sprint 3–4 — Ingestion & Raw Layer**
  Source extraction, raw/staging persistence.

- **Sprint 5–6 — Transformations & Analytics Core**
  Dimensional modeling, SQL-first analytics assets.

- **Sprint 7–8 — Metrics Layer**
  Business metrics and time-based analytics.

- **Sprint 9–10 — Governance & Semantics**
  Metric governance, semantic clarity, portfolio readiness.

- **Sprint 11 — Packaging & Integrations**
  Repository cleanup and isolated ERP integration (Odoo addon).

- **Sprint 12 — Data Quality & Historical Modeling (SCD Type 2)**
  Design and implementation of a Slowly Changing Dimension (Type 2) for customers,
  with a strong focus on data quality and temporal correctness.

  Key outcomes:
  - Clear grain definition: one row per customer per version
  - Natural key vs surrogate key separation (`customer_nk` / `customer_sk`)
  - Validity window modeling using `valid_from` / `valid_to`
  - Current record flag (`is_current`) with enforced consistency
  - Database-level data quality guardrails:
    - CHECK constraints for temporal validity
    - CHECK constraint for current flag correctness
    - Partial unique index ensuring one current record per natural key
  - Analytical validation queries:
    - current vs historical counts
    - distinct customer checks
    - temporal overlap detection (no overlapping validity ranges)

  This sprint emphasizes engineering discipline and correctness-first modeling,
  aligning with enterprise data warehousing best practices and interview
  expectations.

- **Sprint 13 — Data Quality Validation Framework**
  Consolidation and operationalization of data quality checks
  as first-class analytical assets.

  Key outcomes:
  - Structured data quality layout under `sql/analytics/data_quality/`
  - Dimension-scoped checks (starting with `dim_customer`)
  - Clear execution contract: checks must return **0 rows** to be considered valid
  - SCD Type 2 integrity validation:
    - no overlapping validity ranges
    - exactly one current record per natural key
    - valid temporal windows (`valid_from` / `valid_to`)
  - Re-runnable, read-only analytical checks (no side effects)
  - Naming convention to support scaling (`01_`, `02_`, ...)

  This sprint reinforces production-grade data governance practices and
  mirrors how data quality is validated in mature analytics platforms.

---

## Repository Structure (high level)

- `sql/` — SQL bootstrap and migrations
- `src/` — pipeline code (connectors, ingestion, transformations)
- `docker/` — local services
- `docker-compose*.yml` — reproducible environments
- `docs/` — architecture notes and runbooks
- `integrations/` — isolated external system integrations (e.g., Odoo)

---

## Integrations

### Odoo ERP Integration (Addon)

This repository includes a dockerized **Odoo addon** provided as an example of
**ERP integration and deliverable packaging**.

The integration is intentionally **isolated from the core data pipeline**
to demonstrate good engineering practice:

- clear separation between analytics core and external systems
- reproducible integration via Docker Compose
- versioned source code, without committing binary release artifacts

Location in repository:

- `integrations/odoo/phc_analytics_odoo/` — Odoo addon source
- `integrations/odoo/docker-compose.odoo.yml` — reproducible Odoo environment

This integration is not required to run the analytics pipeline itself;
it exists to showcase real-world platform integration and delivery discipline.

Why this matters (market signal): it demonstrates boundary management (core vs
integrations), reproducibility, and clean delivery practices — common
expectations in modern data/platform engineering teams.

---

## Local Run (Docker Compose)

### Start PostgreSQL locally

```bash
docker compose up -d db
```

### Optional: Run Odoo (integration demo)

This is only for demonstrating the ERP addon integration.

```bash
docker compose -f integrations/odoo/docker-compose.odoo.yml up -d
```

Stop it:

```bash
docker compose -f integrations/odoo/docker-compose.odoo.yml down
```

---

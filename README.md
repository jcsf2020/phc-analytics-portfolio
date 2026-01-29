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
  Design and implementation of a Slowly Changing Dimension (Type 2) for
  customers, with a strong focus on data quality and temporal correctness.

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
  - Structured data quality layout under `sql/analytics/data_quality/` (canonical)
  - Legacy single-file checks may exist for reference
    (e.g., `sql/analytics/data_quality_dim_customer.sql`)
  - Dimension-scoped checks (starting with `dim_customer`)
  - Clear execution contract: checks must return **0 rows** to be considered
    valid
  - SCD Type 2 integrity validation:
    - no overlapping validity ranges
    - exactly one current record per natural key
    - valid temporal windows (`valid_from` / `valid_to`)
  - Re-runnable, read-only analytical checks (no side effects)
  - Naming convention to support scaling (`01_`, `02_`, ...)

  This sprint reinforces production-grade data governance practices and
  mirrors how data quality is validated in mature analytics platforms.

- **Sprint 14 — Data Quality Contract + Execution Discipline**
  Formalize data quality as a contract and define a repeatable execution
  routine that can scale across dimensions and marts.

  Key outcomes:
  - Explicit "0 rows" contract for every check query
  - Standard folder + naming convention: `sql/analytics/data_quality/<asset>/`
    and `01_`, `02_`, ... prefixes
  - Repeatable execution pattern (psql), suitable for automation later

  Contract spec: see `docs/data_quality_contract.md`.

  Run checks (example):

  ```bash
  psql "$DATABASE_URL" \
    -v ON_ERROR_STOP=1 \
    -f sql/analytics/data_quality/dim_customer/01_scd2_integrity.sql
  ```

  Run all checks in a folder (repeatable runner script):

  ```bash
  scripts/run_dq_folder.sh sql/analytics/data_quality/dim_customer
  ```

  Notes:
  - Requires `DATABASE_URL` to be set.
  - Runs `*.sql` files in sorted order (`01_`, `02_`, ...).
  - Checks are valid when every query returns **0 rows**.

## Data Quality as a First-Class Citizen

In this project, data quality is treated as an explicit, versioned engineering
concern — not as an ad-hoc validation step or a downstream dashboard check.

Key design principles:

- **Contract-first**: every data quality rule is documented and versioned
  (`docs/data_quality_contract.md`).
- **Deterministic checks**: each SQL check must return **0 rows** to be valid.
- **Read-only by design**: checks never mutate data and can be executed safely
  at any point in time.
- **Execution discipline**: a single, generic runner script executes checks in
  a predictable order and fails fast on error.
- **Automation-ready**: the same execution pattern can be reused in CI/CD,
  scheduled jobs, or deployment quality gates without modification.

This mirrors how mature analytics platforms operationalize data quality:
explicit contracts, deterministic validation, and repeatable execution —
separating correctness concerns from transformation logic.

## Production Checklist

Before treating this repository as a production-grade pattern, ensure the
following are true:

- A **read-only** or **analytics replica** connection string is available for
  automated validation (never point CI to a primary OLTP database).
- A repository secret named `DATABASE_URL` is configured for CI runs.
- Network access from GitHub Actions to the database is allowed (firewall / IP
  rules / private endpoints as applicable).
- Data quality checks are treated as a **blocking gate** for merges and deploys.
- Optional but recommended: schedule the same checks (cron) and alert on
  failures.

## CI / Data Quality Gate (GitHub Actions)

Data quality checks are enforced automatically in CI using **GitHub Actions**.

On every push to `main` and on every pull request, the workflow:

- starts an ephemeral PostgreSQL service (Docker-based)
- waits for database readiness
- seeds a minimal analytics schema and sample data (`sql/ci/seed_dq_db.sql`)
- executes the data quality runner script
- **fails the build if any check returns rows or errors**

Note on design: CI does not connect to external cloud databases.
Instead, it uses an ephemeral local PostgreSQL service to guarantee:

- determinism
- reproducibility
- zero dependency on network access or secrets availability

This turns data quality into a **hard quality gate**: code cannot be merged
unless analytical correctness is preserved.

Workflow definition:

- `.github/workflows/data-quality.yml`

Executed command in CI:

```bash
scripts/run_dq_folder.sh sql/analytics/data_quality/dim_customer
```

Requirements:

- No external database access is required for CI
- All data quality rules must be compatible with the seeded analytics schema
- CI must fail fast on any SQL error or non‑zero result set

Why this matters (market signal):

- demonstrates CI/CD ownership beyond transformations
- shows contract-based data quality enforcement
- mirrors production analytics platforms where correctness blocks deployment

### Local vs CI execution model

- **Local execution**:
  - Uses a real analytics database (e.g. Azure PostgreSQL)
  - Intended for validating data against realistic volumes and states
  - Requires `DATABASE_URL` to be set by the developer

- **CI execution**:
  - Uses an ephemeral PostgreSQL instance
  - Schema and sample data are seeded deterministically
  - Ensures rules are syntactically valid, logically correct and reproducible
  - Acts as a hard merge gate

## What This Repo Proves

- I model dimensions with correctness-first discipline (including SCD Type 2).
- I treat data quality as a **versioned contract**, not an ad-hoc checklist.
- I operationalize validation with a repeatable runner and a CI quality gate.
- I document decisions clearly and keep the repo portfolio-friendly.

## What I'd Do Next (Given Time)

- Add more checks per asset (`02_`, `03_`, ...) and expand coverage to marts.
- Run checks against a dedicated replica and add alerting on failures.
- Introduce environment profiles (local vs CI) and a small makefile/runbook.
- Add lightweight reporting of check results (counts, timing) for observability.

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

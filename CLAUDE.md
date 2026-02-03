# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PHC Analytics is a production-grade data engineering portfolio project demonstrating SQL-first analytics modeling with dimensional schema (Kimball), data quality as a first-class engineering concern, and reproducible local environments via Docker Compose.

**Tech Stack:** Python 3.9+, PostgreSQL 15+, Docker Compose, SQL (analytics models), Pandas, pytest, Ruff, GitHub Actions CI

## Build & Run Commands

```bash
# Install dependencies (uses uv)
uv pip install -e .              # Install in dev mode
uv pip install -e ".[dev]"       # With dev dependencies (pytest, ruff)

# Run pipeline (generates CSVs to ./out/)
make run                         # or: python run_pipeline.py

# Run tests
make test                        # or: pytest -q
pytest -m "not integration"      # Skip integration tests

# Lint/format
ruff check src/
ruff format src/

# Data quality checks (requires DATABASE_URL env var)
scripts/run_dq_folder.sh sql/analytics/data_quality/dim_customer

# Orchestration (Sprint 19/20)
python orchestration/run_pipeline.py health --pipeline phc_analytics --env local --max-age-minutes 60
python orchestration/run_pipeline.py run --pipeline phc_analytics --env local

# Streamlit dashboard
streamlit run app.py

# Docker (local PostgreSQL)
docker compose up -d db
docker compose down
```

## Architecture

### Data Flow (Medallion Pattern)
```
Source (Bronze) → Normalize (Silver) → Model (Gold) → Aggregates → Outputs/BI
     ↓                  ↓                   ↓              ↓
Raw payloads      Validated +         Star schema     Precomputed
  (mock)          standardized         (Kimball)       metrics
```

### Dimensional Model (Kimball)
- **Dimensions:** `dim_customer` (SCD Type 2), `dim_product`, `dim_date`
- **Facts:** `fact_orders`, `fact_order_lines` (grain: 1 row = 1 atomic event)
- Surrogate keys (`*_key`) + natural keys; foreign keys link facts to dims

### Key Directories
- `src/phc_analytics/` - Main Python package
  - `integrations/` - External system clients (PrestaShop mock, Odoo stubs)
  - `transformations/` - ETL: normalize → dims/facts → aggregates
- `sql/analytics/` - SQL assets (dims, facts, aggregates)
  - `data_quality/<asset>/` - DQ checks with numbered prefixes (`01_`, `02_`, ...)
- `orchestration/` - Production orchestrator with step registry and health checks
- `tests/` - pytest test suite

### Entry Points
1. `run_pipeline.py` - MVP orchestration (extract → normalize → model → write CSVs)
2. `orchestration/run_pipeline.py` - Production orchestrator with observability
3. `app.py` - Streamlit dashboard
4. `scripts/run_dq_folder.sh` - Data quality runner (deterministic, fail-fast)

## Data Quality Contract

**Critical rule:** Every DQ check query MUST return **0 rows** to pass.

- Location: `sql/analytics/data_quality/<asset>/` with numbered prefixes
- Execution: `scripts/run_dq_folder.sh` runs `*.sql` files in sorted order
- CI gate blocks merges if any check returns rows or errors
- Checks are read-only, re-runnable, deterministic

## CI/CD

GitHub Actions workflow (`.github/workflows/data-quality.yml`):
- Triggers on push to `main` and all PRs
- Uses ephemeral PostgreSQL (no external DB dependencies)
- Seeds schema via `sql/ci/seed_dq_db.sql`
- Fails build if any DQ check returns rows

## Testing

```bash
pytest -q                           # Run all tests
pytest -m "not integration"         # Skip slow integration tests
pytest tests/test_pipeline_contract.py  # Specific test file
```

Markers defined in `pytest.ini`: `integration` for slow tests.

## Code Organization Conventions

- SQL is source of truth for dimensions, facts, aggregates
- Python is orchestration/glue
- Transformations in `src/phc_analytics/transformations/` follow naming: `dim_*.py`, `fact_*_enrich.py`, `agg_*.py`
- Output files go to `out/` directory (gitignored)
- Never commit credentials; use `DATABASE_URL` env var

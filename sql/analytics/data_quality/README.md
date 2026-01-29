
# Data Quality (DQ) Suite

This folder contains the SQL-based Data Quality checks for the PHC_Analytics project.

## Contract (how PASS/FAIL works)

- Each `*.sql` file is a **check**.
- A check **MUST return zero rows** to PASS.
- If a check returns **one or more rows**, it is a **DATA QUALITY FAILURE**.
- If a check raises a **SQL error**, it is a **FAILURE**.

These checks are executed by `scripts/run_dq_folder.sh`, both locally and in CI.

## Folder structure

Each domain/table has its own folder:

- `dim_customer/` - SCD2 integrity and current-record rules
- `dim_date/` - date dimension completeness and uniqueness
- `fact_orders/` - fact rules (grain, values) and FK integrity

Naming convention:

- Use numeric prefixes to control execution order, e.g. `01_...sql`, `02_...sql`.

## How to run locally

### 1) Set the database connection

Export `DATABASE_URL` (Azure/Postgres). Example:

```bash
export DATABASE_URL="postgresql://etl_user:-Portugal2025@phc-analytics-pg-ne.postgres.database.azure.com:5432/phc_analytics?sslmode=require"
```

### 2) Run checks for a folder

```bash
scripts/run_dq_folder.sh sql/analytics/data_quality/dim_customer
scripts/run_dq_folder.sh sql/analytics/data_quality/fact_orders
scripts/run_dq_folder.sh sql/analytics/data_quality/dim_date
```

Expected output:

- `PASS: 0 rows` for each file
- `DQ GATE: PASSED` at the end

If any check fails:

- A `FAIL:` message is printed with the offending rows or the SQL error
- The script exits with non-zero status

## Writing new checks (rules)

### Rule 1: always return rows that explain the problem

Your query should return the minimum useful columns to debug quickly.

Example pattern:

```sql
select 'RULE_NAME' as issue_type, offending_key
from ...
where ...;
```

### Rule 2: normalize keys

Avoid false failures caused by whitespace or empty strings:

- Use `btrim(...)` to trim keys
- Use `nullif(btrim(...), '')` to treat empty strings as NULL

### Rule 3: keep checks read-only

Checks must be `SELECT` only. No `INSERT/UPDATE/DELETE`.

## CI execution

GitHub Actions workflow:

- `.github/workflows/data-quality.yml`

It runs the same `scripts/run_dq_folder.sh` commands using the repository secret:

- `DATABASE_URL`

If the secret is missing, CI fails with a clear error.

## Real-world scenario handled (late-arriving dimension)

We observed a real FK violation:

- `analytics.fact_orders.customer_id = '42'`
- `analytics.dim_customer` had no current record for `customer_nk = '42'`

This is a classic **late-arriving dimension** scenario.

Policy used:

- Keep the fact (do not delete business events)
- Backfill a controlled placeholder dimension record ("Unknown Customer")
- Keep SCD2 semantics (`is_current=true`, `valid_to=null`)

This ensures the FK check remains strict while the pipeline remains resilient.

## Quick checklist before merging

- `bash -n scripts/run_dq_folder.sh` returns OK
- Running each DQ folder locally returns `DQ GATE: PASSED`
- CI run for "Data Quality Gate" is green

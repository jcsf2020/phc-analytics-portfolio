# Data Quality Contract

## 1. Purpose

This document defines the data quality contract for analytical assets
in the PHC Analytics project.

Data quality is treated as a first-class engineering concern and is
validated through explicit, repeatable, read-only SQL checks.

A data quality check is considered **valid only when it returns zero rows**.

---

## 2. Scope

This contract applies to:

- analytical dimensions and marts under `sql/analytics/`
- data quality checks under `sql/analytics/data_quality/`

The initial scope focuses on Slowly Changing Dimensions (SCD Type 2),
starting with `dim_customer`.

---

## 3. Contract Rules

All data quality checks **MUST** comply with the following rules:

1. Checks are implemented as standalone `.sql` files.
2. Checks are read-only and must not mutate data.
3. Each check validates a single, well-defined rule.
4. A check **MUST return zero rows** to be considered successful.
5. Any returned row represents a data quality violation.
6. Checks must be re-runnable and deterministic.

Naming convention:

- Checks are prefixed with an execution order number:
  `01_`, `02_`, `03_`, ...

Folder structure:

sql/analytics/data_quality/<asset_name>/

---

## 4. Execution and Failure Semantics

Checks are executed using `psql` with `ON_ERROR_STOP=1`.

- SQL execution errors cause immediate failure.
- Returned rows indicate data quality violations.
- An execution is considered successful only if:
  - all checks run
  - no SQL error occurs
  - all checks return zero rows

This execution model is intentionally simple and suitable for
automation in CI/CD pipelines.

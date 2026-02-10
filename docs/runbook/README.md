# PHC Analytics — Operational Runbook

## Scope
This runbook documents how to operate, monitor, and troubleshoot the PHC Analytics pipeline in production.

## Pipeline
- Name: phc_analytics
- Orchestrator: Python (run_pipeline.py)
- Database: PostgreSQL (Azure)

## Environments
- local
- ci
- prod

## Entry Points
- Health check
- Pipeline run
- Data quality gates

## Observability
- analytics.pipeline_run_log
- Event stream (run / step lifecycle)

## Failure Modes
(TBD)

## Recovery Procedures
(TBD)

## Operational Checklist
(TBD)

## Failure Modes

### 1. Database Connectivity Failure
**Symptoms**
- psql authentication errors
- run_pipeline exits with code != 0
- No new rows in analytics.pipeline_run_log

**Detection**
- run_pipeline run fails
- Health check returns non-zero
- PostgreSQL logs show connection/auth errors

**Likely Causes**
- Invalid credentials
- Network / firewall issues
- Azure PostgreSQL unavailable

---

### 2. Data Quality Gate Failure
**Symptoms**
- Pipeline run marked as failed
- error_message populated in pipeline_run_log

**Detection**
- Data Quality Gate CI fails
- analytics.pipeline_run_log.status = failed

**Likely Causes**
- Schema drift
- Unexpected NULLs in critical columns
- Upstream data contract violation

---

### 3. Step Execution Failure
**Symptoms**
- STEP_FAILED event emitted
- Partial pipeline execution

**Detection**
- Event stream shows STEP_FAILED
- run_pipeline exits with failure

**Likely Causes**
- SQL error
- Missing table or column
- Logic error in step implementation

## Recovery Procedures

### A) Database auth/connectivity
1) Confirm connectivity (no prompts; uses ~/.pgpass)
```bash
psql -w "$DATABASE_URL" -c "select current_user, current_database();"

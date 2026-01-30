# Orchestration (Sprint 19)

This module defines **how analytics pipelines are executed**, not what they compute.

It introduces an explicit orchestration layer on top of existing SQL and Python logic,
following production-grade data engineering practices.

---

## Goal of this Sprint

Turn the pipeline into a **controlled system**, not a collection of scripts.

At the end of Sprint 19, a pipeline must be:

- Deterministic
- Observable
- Fail-fast
- Re-runnable
- Ready to be migrated to Airflow / Dagster without refactor

---

## What Orchestration Means (Here)

**Orchestration** is the logic that defines:

- Which steps exist
- In which order they run
- What happens on success
- What happens on failure

This sprint focuses on **explicit orchestration in code**, not on external tools.

---

## Core Concepts

### Pipeline

A pipeline is a **sequence of steps** executed under a single `run_id`.

A pipeline:

- Has a name
- Has an environment (local / ci / prod)
- Emits lifecycle events (start, success, failure)

---

### Step

A step is the **smallest executable unit**.

Each step:

- Has a name
- Has a single responsibility
- Returns a clear status (success / failure)
- May emit metrics (rows processed, duration)

Steps do **not** decide what comes next.

---

### Orchestrator

The orchestrator:

- Knows the ordered list of steps
- Executes them sequentially
- Stops immediately on first failure
- Updates pipeline observability tables

---

## Execution Contract

A pipeline execution MUST:

1. Create a run entry (`pipeline_run_log`)
2. Execute steps in a fixed order
3. Stop on first failure
4. Finalize the run with:
   - status
   - duration
   - optional metrics

No step is allowed to:

- Catch and hide errors
- Continue execution after failure

---

## Folder Structure

```bash
orchestration/
├─ README.md          # This contract
├─ steps/             # Individual pipeline steps
└─ utils/             # Shared helpers (db, logging, timing)
```

---

## Non-Goals (This Sprint)

- Airflow / Dagster deployment
- Parallel execution
- Retries / backoff policies
- Event-driven pipelines

These are **deliberately excluded** to keep the orchestration model explicit and simple.

---

## Why This Matters (Market Signal)

This sprint demonstrates:

- System thinking, not script writing
- Clear separation of concerns
- Readiness for production orchestration tools
- Architecture aligned with modern data platforms

This is the difference between:
> “I can write pipelines”
and
> “I design data platforms”

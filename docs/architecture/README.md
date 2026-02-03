<!-- markdownlint-disable MD013 -->
# PHC Analytics Platform Architecture

This document serves as the architectural index for the PHC Analytics data engineering platform. It provides a mental model of the system without implementation details.

---

## High-Level Architecture

PHC Analytics follows a **SQL-first, deterministic orchestration** model:

| Principle | Description |
| --------- | ----------- |
| **SQL as Source of Truth** | All data transformations, quality checks, and observability queries are expressed in SQL. Python serves as orchestration glue. |
| **Deterministic Execution** | Steps execute in a fixed, predictable order defined by a static registry. No dynamic DAG resolution or runtime scheduling decisions. |
| **Observable by Design** | Every pipeline run is logged to a relational table with full lifecycle metadata (start, finish, status, metrics). |
| **Portable Contracts** | Step interfaces are tool-agnostic, enabling future migration to enterprise orchestrators (Airflow, Dagster) without rewriting business logic. |

---

## Core Runtime Components

```text
┌─────────────────────────────────────────────────────────────┐
│                        Executor                             │
│  (orchestration/run_pipeline.py)                            │
│                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │ RunContext  │───▶│Step Registry│───▶│   Steps     │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│          │                                     │            │
│          ▼                                     ▼            │
│   ┌─────────────┐                      ┌─────────────┐      │
│   │Health Gates │                      │ Event Logs  │      │
│   └─────────────┘                      └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### RunContext

Immutable execution environment passed to every step. Contains:

- Database connection parameters
- Pipeline identifier
- Environment label (local, ci, prod)

### Step Registry

Static, ordered list of pipeline steps. Registration order determines execution order. No runtime discovery or dynamic registration.

### Executor

Sequential runner that:

1. Creates a run entry in the event log
2. Iterates through registered steps in order
3. Finalizes the run with status and metrics

### Health Gates

Validation mechanisms executed before, after, or at the end of a run. Gates return PASS or FAIL and are evaluated with an explicit severity.

- Default severity is WARN (non-blocking).
- Only gates explicitly marked as BLOCKER halt execution.
- Gates are conceptually separate from Steps and do not transform data.

### Event Logs

Relational table (`analytics.pipeline_run_log`) capturing:

- Run lifecycle (started, success, failed)
- Timestamps and duration
- Rows processed
- Error messages (truncated)

---

## Execution Philosophy

### Fail-Fast

The orchestrator stops on the first error. There is no catch-and-continue behavior. Failed runs leave a clear audit trail with the failure point and error message.

### Data Quality as Contract

Data quality checks are not optional validations—they are **contractual gates**. A check that returns rows indicates a violation. Whether execution halts depends on the gate severity (WARN vs BLOCKER).

### Dry-Run as Planning

Dry-run represents planning and validation without side effects. It validates configuration, step registration, and execution planning without executing transformations or requiring database connectivity.
Pre-flight health checks may exist as a separate command and are not equivalent to dry-run.

### Idempotent Operations

Steps are designed to be safe to re-run where possible. Resume or partial re-execution semantics are considered future enhancements and are not part of the current execution contract.

---

## Documentation Map

| Document | Purpose |
| -------- | ------- |
| [Orchestrator Mental Model](./orchestrator-mental-model.md) | Conceptual overview of orchestration design decisions |
| [Step Contract](./step-contract.md) | Protocol specification for implementing pipeline steps |
| [Health Gates Contract](./health-gates-contract.md) | Design and usage of pre-execution health checks |
| [Run Context](./run-context.md) | Environment configuration and parameter passing |
| [Execution Policies](./execution-policies.md) | Error handling, retries, and failure modes |
| [Event Log Schema](./event-log-schema.md) | Observability table structure and query patterns |

---

## Quick Reference

```bash
# Check pipeline health (pre-flight validation)
python orchestration/run_pipeline.py health --pipeline phc_analytics --env local

# Execute pipeline
python orchestration/run_pipeline.py run --pipeline phc_analytics --env local
```

---

*This document describes the intended architecture and execution contracts. Implementation details and future changes should be proposed via design documents in `docs/rfcs/`.*

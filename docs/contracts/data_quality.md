# Data Quality Contract

## Purpose

This document defines the **Data Quality (DQ) contract** for the PHC Analytics platform.

Its goal is to make data quality **explicit, deterministic, and enforceable by design**, not implicit or ad-hoc.
The contract ensures that every data quality decision is:

- predictable,
- auditable,
- and understood by any engineer interacting with the system.

This is an engineering contract, not user documentation.

---

## Definition of a Data Quality Check

A Data Quality check is a **read-only assertion** over system state.

Conceptually, a DQ check:

- evaluates a condition about data correctness or freshness,
- returns a deterministic outcome,
- never mutates data or state.

Each check is defined by:

- a stable identifier (`check_id`),
- a severity level,
- a pure function that produces an outcome.

A DQ check **does not**:

- transform data,
- fix data,
- trigger side effects.

---

## Outcome Semantics

Each Data Quality check produces exactly one outcome:

- `PASS` — the assertion holds.
- `FAIL` — the assertion is violated.

Outcomes are explicit and binary by design.
There is no partial success or implicit tolerance.

Optional metadata may be attached for diagnostics only.

---

## Severity Semantics

Severity defines **how the system reacts** to a failed check.

### WARN

- The check failure is recorded.
- Execution continues.
- The run is considered successful unless other failures occur.

Used for:

- early signals,
- non-critical inconsistencies,
- observability without enforcement.

### BLOCKER

- The check failure immediately halts execution.
- The run is marked as failed.
- No further steps or checks are executed in the current phase.

Used for:

- correctness violations,
- stale or invalid data states,
- conditions that make results unreliable.

Severity is an explicit engineering decision, not an implementation detail.

---

## Execution Phases

Data Quality checks may be executed at defined phases of a run:

- **Pre-run**
  Assertions that must hold before any processing starts.

- **Post-step**
  Assertions that validate the outcome of a specific step.

- **End-run**
  Assertions that validate global invariants, executed even if the run failed.

The execution phase defines *when* a check runs, not *what* it checks.

---

## Determinism and Idempotency

All Data Quality checks must be:

- deterministic,
- idempotent,
- safe to re-run.

Given the same inputs and system state, a check must always return the same outcome.

This property is mandatory for:

- retries,
- CI validation,
- auditability.

---

## Non-goals

The Data Quality layer is **not responsible** for:

- data correction or repair,
- metric computation,
- alerting or notifications,
- orchestration logic,
- business logic enforcement.

Its sole responsibility is to assert correctness and signal violations.

---

## Engineering Rationale

Most data failures in production do not come from SQL errors,
but from **implicit assumptions**.

This contract makes those assumptions explicit and enforceable,
turning data quality from opinion into system behavior.

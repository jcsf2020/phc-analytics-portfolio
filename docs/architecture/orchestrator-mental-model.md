<!-- markdownlint-disable MD060 -->
# Orchestrator Mental Model

This document describes the conceptual model of the PHC Analytics orchestrator. It focuses on execution semantics and design rationale rather than implementation details.

---

## 1. Purpose and Scope

The orchestrator exists to execute a sequence of data transformation steps in a predictable, observable manner. It provides:

- **Deterministic execution order** — The same inputs always produce the same execution sequence.
- **Lifecycle observability** — Every run is recorded with start time, end time, status, and metrics.
- **Failure isolation** — Errors are surfaced immediately with clear attribution to the failing step.

The orchestrator is intentionally minimal. It does not schedule, retry, branch, or parallelize. These constraints are features, not limitations—they ensure that pipeline behavior is fully predictable and easy to reason about.

---

## 2. Mental Model Overview

Think of the orchestrator as a **linear tape reader**:

```text
┌───────┬───────┬───────┬───────┬───────┐
│ Step1 │ Step2 │ Step3 │ Step4 │ Step5 │
└───────┴───────┴───────┴───────┴───────┘
    ▲
    │
   HEAD (current position)
```

- The tape is fixed at pipeline definition time.
- The head moves forward one step at a time.
- The head never moves backward.
- If a step fails with blocking severity, the tape stops.

There is no conditional branching, no loops, and no parallel tracks. The execution path is a straight line from start to finish.

---

## 3. Execution Lifecycle

Every pipeline run follows a three-phase lifecycle:

### Phase 1: Initialization

- A new run is created in the event log with status `started`.
- The run context is assembled with environment parameters.
- The step registry is read to determine execution order.

### Phase 2: Execution

- Steps execute sequentially in registry order.
- Each step receives the run context and returns a metric (rows processed).
- Health gates are evaluated at their configured points with their configured severity.
- Execution continues until all steps complete or a blocking failure occurs.

### Phase 3: Finalization

- The run record is updated with final status (`success` or `failed`).
- Timestamps, duration, and aggregate metrics are recorded.
- If failed, the error message is captured (truncated for storage).

Finalization always occurs, even after failure. Every run leaves a complete audit record.

---

## 4. Step Ordering and Determinism

Steps are registered in a static list. This list is defined at build time, not runtime. The orchestrator reads this list and executes steps in exact registration order.

**Implications:**

- Adding a step means inserting it at a specific position in the registry.
- Removing a step means removing it from the registry.
- Reordering steps means changing the registry definition.

There is no dynamic step discovery, no dependency resolution, and no topological sorting. The registry is the single source of truth for execution order.

**Why static ordering?**

- Predictability: The execution order is visible in one place.
- Debuggability: When a step fails, you know exactly what ran before it.
- Portability: Static ordering maps directly to enterprise orchestrator DAGs.

---

## 5. Health Gates Evaluation Model

Health gates are validation checkpoints distinct from data transformation steps. They assert conditions about system state or data quality.

### Gate Semantics

A gate returns one of two results:

| Result | Meaning |
|--------|---------|
| **PASS** | The condition is satisfied. Execution continues. |
| **FAIL** | The condition is violated. Behavior depends on severity. |

### Severity Levels

| Severity | On FAIL behavior |
|----------|------------------|
| **WARN** | Log the failure. Continue execution. |
| **BLOCKER** | Log the failure. Halt execution immediately. |

Default severity is WARN. Gates must be explicitly marked as BLOCKER to halt the pipeline.

### Evaluation Points

Gates may be configured to run:

- Before the first step (pre-flight validation)
- After the last step (post-run assertions)
- At the end of a run regardless of success or failure (invariant checks)

Gates do not transform data. They observe and assert.

---

## 6. Run Context Propagation

The run context is an immutable bundle of execution parameters created at initialization and passed to every step.

### Context Contents

- **Database connection** — Where to read and write data.
- **Pipeline identifier** — Logical name for grouping runs.
- **Environment label** — Execution environment (local, ci, prod).

### Propagation Rules

- The context is created once at run start.
- The context is passed by reference to each step.
- Steps may read the context but never modify it.
- The context does not accumulate state between steps.

Steps that need to share data do so through the database, not through context mutation.

---

## 7. Failure Semantics

The orchestrator follows a **fail-fast** model for blocking failures.

### Failure Types

| Type | Source | Behavior |
|------|--------|----------|
| **Step exception** | A step raises an unhandled error | Halt immediately |
| **Gate BLOCKER** | A gate with BLOCKER severity fails | Halt immediately |
| **Gate WARN** | A gate with WARN severity fails | Log and continue |

### Failure Recording

When execution halts:

1. The current step or gate is identified as the failure point.
2. The error message is captured (truncated to storage limits).
3. The run record is finalized with status `failed`.
4. Subsequent steps are not attempted.

### No Recovery

There is no retry logic within a run. There is no checkpoint/resume mechanism. A failed run is terminal. Recovery means starting a new run after addressing the root cause.

---

## 8. Non-Goals

The orchestrator explicitly does not provide:

| Capability | Rationale |
|------------|-----------|
| **Parallel execution** | Adds complexity; sequential is sufficient for current scale. |
| **Retries with backoff** | Masks transient failures; prefer explicit re-runs. |
| **Dynamic branching** | Unpredictable execution paths; prefer static registry. |
| **Checkpoint/resume** | Requires step-level idempotency guarantees beyond current scope. |
| **Cross-pipeline dependencies** | Each pipeline is an independent unit. |
| **Scheduling** | External schedulers (cron, Airflow) handle timing. |

These are not rejected permanently—they are out of scope for the current design. If needed, they would be introduced through explicit design proposals with clear justification.

---

## Dry-Run vs Health Check

These are distinct operations:

| Operation | Database Access | Side Effects | Purpose |
|-----------|-----------------|--------------|---------|
| **Dry-run** | No | None | Validate configuration and step registration. Plan execution without executing. |
| **Health check** | Yes | None (read-only) | Query system state to verify readiness. Pre-flight validation before committing to a run. |

Dry-run answers: "Is the pipeline correctly configured?"

Health check answers: "Is the system ready to run this pipeline?"

---

*This document describes the orchestrator's conceptual model. For step implementation details, see the Step Contract document.*

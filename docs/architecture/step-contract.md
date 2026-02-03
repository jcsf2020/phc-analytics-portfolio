# Step Contract

This document defines the formal contract between the orchestrator and pipeline steps. All step implementations must adhere to these requirements.

---

## 1. Purpose

The step contract establishes clear boundaries between orchestration concerns and transformation logic. It ensures that steps are:

- Predictable in their behavior
- Isolated from execution control
- Portable across orchestration platforms
- Testable in isolation

This contract is normative. Violations may cause undefined orchestrator behavior.

---

## 2. Conceptual Definition of a Step

A step is a **named, executable unit of work** that performs a single logical transformation or action within a pipeline.

A step:

- Has a unique identifier within its pipeline
- Receives execution context as input
- Performs work against external systems (database, filesystem, APIs)
- Returns execution metrics
- Signals success or failure

A step is not:

- A decision point
- A scheduler
- A coordinator of other steps
- A validator of upstream or downstream data

---

## 3. Step Responsibilities

A step **must**:

| Responsibility | Requirement |
| -------------- | ----------- |
| Execute work | Perform its defined transformation or action when invoked. |
| Return metrics | Provide a count of items processed (rows, records, files). |
| Signal failure | Raise an exception when unable to complete successfully. |
| Be deterministic | Produce the same outcome given the same inputs and system state. |
| Be isolated | Operate without knowledge of other steps in the pipeline. |

A step **should**:

| Guideline | Rationale |
| --------- | --------- |
| Complete quickly | Long-running steps delay pipeline feedback. |
| Log meaningful events | Diagnostic information aids debugging. |
| Minimize external dependencies | Fewer dependencies mean fewer failure modes. |

---

## 4. Execution Constraints

### Context Immutability

A step **must not** modify the run context. The context is read-only input.

### Flow Control Prohibition

A step **must not**:

- Skip itself based on internal conditions
- Terminate the pipeline
- Invoke other steps
- Signal that execution should branch or loop

The orchestrator owns execution flow. Steps execute when called and return when complete.

### Isolation Requirement

A step **must not**:

- Reference other steps by name or identifier
- Assume knowledge of execution order
- Depend on side effects from previous steps except through persisted state (database)

Steps communicate through the database, not through shared memory or context mutation.

### Determinism Requirement

Given identical:

- Run context parameters
- Database state
- External system state

A step **must** produce identical:

- Database mutations
- Return value
- Success or failure outcome

Non-deterministic behavior (random sampling, time-dependent logic without explicit seeding) violates this contract.

---

## 5. Inputs and Outputs

### Input: Run Context

Every step receives a run context containing:

| Parameter | Description |
| --------- | ----------- |
| Database connection | Where to read and write data. |
| Pipeline identifier | Logical name of the executing pipeline. |
| Environment label | Execution environment (local, ci, prod). |

The step **must** treat this context as immutable. The step **must not** store references to the context beyond its execution scope.

### Output: Execution Metric

Every step **must** return an integer representing items processed:

| Value | Meaning |
| ----- | ------- |
| `0` | Step completed successfully but processed no items. |
| `> 0` | Step completed successfully and processed N items. |

The metric **should** represent a meaningful count (rows inserted, records updated, files written). The orchestrator aggregates these metrics for observability.

---

## 6. Error Signaling

A step **must** signal failure by raising an exception. There is no other failure mechanism.

### Exception Requirements

The exception **must**:

- Be a standard exception type or a subclass thereof
- Contain a human-readable message describing the failure
- Propagate without being caught and suppressed

The exception **should**:

- Include context about what operation failed
- Avoid exposing sensitive information (credentials, PII)

### Prohibited Patterns

A step **must not**:

- Return a special value to indicate failure (e.g., `-1`, `None`)
- Log an error and return success
- Catch exceptions and continue silently
- Signal partial success

A step either succeeds completely or fails completely.

---

## 7. Observability Requirements

### Logging

A step **should** emit log messages for:

- Significant milestones (batch boundaries, phase transitions)
- Unexpected but recoverable conditions
- Performance-relevant metrics

A step **must not** emit logs for:

- Normal iteration (per-row logging at scale)
- Sensitive data content

### Lifecycle Events

A step **must not** log its own start or end events. The orchestrator handles lifecycle observability.

### Metric Accuracy

The returned metric **must** accurately reflect work performed. Inflated or estimated metrics degrade observability value.

---

## 8. Non-Responsibilities

The following concerns are explicitly outside step scope:

| Concern | Owner |
| ------- | ----- |
| Execution ordering | Orchestrator (via step registry) |
| Retry logic | Orchestrator (not currently implemented) |
| Health validation | Health gates (separate construct) |
| Data quality checks | Data quality framework (separate construct) |
| Run lifecycle logging | Orchestrator |
| Error recovery | Orchestrator or external operator |
| Scheduling | External scheduler |

A step that attempts to handle these concerns violates separation of responsibilities.

---

## 9. Design Rationale

### Why prohibit flow control?

Steps that control flow create hidden dependencies and unpredictable execution paths. Centralizing flow control in the orchestrator makes behavior explicit and auditable.

### Why require exceptions for failure?

Exceptions provide a uniform failure channel with stack traces and error context. Return-value signaling fragments error handling and risks silent failures.

### Why enforce context immutability?

Mutable context creates implicit coupling between steps. Immutable context ensures steps are independently testable and their interactions are explicit (through the database).

### Why single return metric?

A simple integer is universally applicable and trivially aggregatable. Complex return structures would require step-specific handling and complicate observability.

### Why prohibit step awareness of other steps?

Step independence enables:

- Reordering without code changes
- Removal without cascade effects
- Testing in isolation
- Reuse across pipelines

Coupling between steps would forfeit these benefits.

---

*This contract defines step behavior. For orchestrator behavior, see the Orchestrator Mental Model document.*

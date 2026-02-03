# Data Quality Contract

This document defines the formal contract for data quality checks within the PHC Analytics platform. All quality checks must adhere to these requirements.

---

## 1. Purpose

Data quality is a first-class engineering concern, not an afterthought. This contract establishes:

- A uniform definition of what constitutes a quality check
- Clear semantics for pass/fail evaluation
- Explicit rules for when failures halt execution
- Separation between transformation logic and validation logic

Quality checks are contractual assertions about data state. They protect downstream consumers from invalid data propagation.

---

## 2. Definitions

| Term | Definition |
| ---- | ---------- |
| **DQ Check** | A read-only SQL query that identifies rows violating a quality rule. |
| **Violating Row** | A row returned by a DQ check, representing a data quality violation. |
| **PASS** | The DQ check returned zero violating rows. |
| **FAIL** | The DQ check returned one or more violating rows. |
| **Severity** | Classification determining behavior on failure (WARN or BLOCKER). |
| **Target Asset** | The table, view, or dataset being validated by the check. |
| **Gate** | An orchestrator construct that evaluates DQ checks at defined execution points. |

---

## 3. Quality Check Semantics

### Query Structure

A DQ check **must** be a SQL query that returns violating rows. The check passes if and only if the result set is empty.

| Result | Interpretation |
| ------ | -------------- |
| 0 rows returned | **PASS** — The quality rule is satisfied. |
| 1+ rows returned | **FAIL** — The quality rule is violated. |

### Determinism Requirement

A DQ check **must** be deterministic. Given identical database state, the check **must** return identical results.

A DQ check **must not**:

- Use non-deterministic functions (random, current timestamp without binding)
- Depend on external state not captured in the database
- Produce different results on repeated execution against unchanged data

### Side Effect Prohibition

A DQ check **must** be query-only. It **must not**:

- Insert, update, or delete data
- Modify schema
- Create or drop objects
- Invoke procedures with side effects

Quality checks observe; they do not mutate.

---

## 4. Severity Model

Every DQ check has an assigned severity that determines behavior on failure.

| Severity | On FAIL Behavior | Default |
| -------- | ---------------- | ------- |
| **WARN** | Log the failure. Continue execution. | Yes |
| **BLOCKER** | Log the failure. Halt execution immediately. | No |

### Severity Assignment

- Severity **must** be explicitly declared or default to WARN.
- Severity **should** reflect business impact of the violation.
- BLOCKER **should** be reserved for violations that would corrupt downstream data or violate invariants.

### Escalation

A check's severity is fixed at definition time. Runtime escalation (WARN to BLOCKER based on row count) is not supported. If conditional halting is required, define separate checks with appropriate severities.

---

## 5. Execution Points

DQ checks execute at defined points in the pipeline lifecycle, configured via gates.

| Execution Point | When | Typical Use |
| --------------- | ---- | ----------- |
| **Pre-run** | Before the first step executes. | Validate source data freshness, schema integrity. |
| **Post-step** | After a specific step completes. | Validate transformation output before downstream steps. |
| **End-run** | After all steps complete, regardless of success or failure. | Assert final state invariants, cross-table consistency. |

### Execution Guarantees

- Pre-run checks **must** complete before any step begins.
- Post-step checks **must** complete before the next step begins.
- End-run checks **must** execute even if the run failed (for diagnostic purposes).

---

## 6. Ownership and Separation of Concerns

### Steps Do Not Own DQ

Pipeline steps **must not** embed data quality enforcement logic. A step's responsibility is transformation, not validation.

A step **must not**:

- Execute DQ queries internally
- Halt based on quality conditions
- Log quality violations as part of its execution

### Gates Own DQ Evaluation

Quality checks are evaluated by gates, which are orchestrator constructs separate from steps.

| Construct | Responsibility |
| --------- | -------------- |
| **Step** | Transform data. Return metrics. Signal failure via exception. |
| **Gate** | Evaluate DQ checks. Determine PASS/FAIL. Apply severity rules. |
| **Orchestrator** | Invoke gates at configured points. Halt on BLOCKER. Record results. |

### Framework Boundary

The DQ framework owns:

- Check definition and storage
- Check execution
- Result interpretation
- Severity enforcement

Steps are unaware of which checks run before or after them.

---

## 7. Reporting and Observability Requirements

### Mandatory Recording

Every DQ check execution **must** be recorded in the run's event stream with the following metadata:

| Field | Description |
| ----- | ----------- |
| Check identifier | Unique name or ID of the quality check. |
| Target asset | Table or dataset being validated. |
| Severity | WARN or BLOCKER. |
| Result | PASS or FAIL. |
| Violating row count | Number of rows returned (0 for PASS). |
| Timestamp | When the check executed. |
| Run correlation | Association to the pipeline run (run_id or equivalent). |

### Retention

DQ results **should** be retained for historical analysis and trend detection. Retention policy is outside this contract's scope.

### Accessibility

DQ results **must** be queryable for:

- Run-level summaries (all checks for a given run)
- Asset-level history (all checks for a given table over time)
- Failure analysis (all FAIL results within a time range)

---

## 8. Failure and Halt Rules

### BLOCKER Failure

When a check with BLOCKER severity fails:

1. The failure **must** be recorded immediately.
2. Execution **must** halt before proceeding to subsequent steps.
3. The run **must** be marked as failed.
4. The failure reason **must** reference the failing check.

### WARN Failure

When a check with WARN severity fails:

1. The failure **must** be recorded.
2. Execution **must** continue.
3. The run **may** still succeed if no blocking failures occur.
4. The failure **should** be visible in run summaries.

### CI Integration

| Severity | CI Behavior |
| -------- | ----------- |
| **BLOCKER** | CI build **must** fail. Merge **must** be blocked. |
| **WARN** | CI build **should** pass. Failure **should** be visible in logs or reports. |

WARN failures are informational in CI. They surface quality degradation without blocking deployment.

---

## 9. Non-Goals

The following are explicitly outside this contract's scope:

| Capability | Rationale |
| ---------- | --------- |
| Automatic remediation | DQ checks detect; they do not fix. Remediation is a separate concern. |
| Row-level exception handling | Checks operate on sets, not individual row decisions. |
| Dynamic severity | Severity is static. Runtime adjustment adds complexity without clear benefit. |
| Cross-pipeline checks | Each pipeline's DQ is self-contained. Cross-pipeline validation requires explicit design. |
| Schema inference | Checks validate data, not schema evolution. |

---

## 10. Design Rationale

### Why SQL-first?

SQL is the lingua franca of data systems. SQL-based checks are:

- Readable by analysts and engineers
- Executable against any SQL-compatible store
- Versionable alongside the assets they validate
- Testable with standard database tooling

### Why separation from steps?

Embedding DQ in steps couples validation to transformation. Separation provides:

- Independent evolution of checks and transformations
- Clear responsibility boundaries
- Flexibility to add checks without modifying step code
- Reusability of checks across pipelines

### Why default to WARN?

Most quality issues are informational during development. Defaulting to BLOCKER would halt pipelines on every new check, discouraging adoption. WARN-by-default encourages check proliferation; promotion to BLOCKER is an intentional escalation.

### Why record all results?

Quality trends matter as much as point-in-time results. Recording every execution enables:

- Trend analysis (is quality improving or degrading?)
- Regression detection (did a deploy introduce violations?)
- SLA reporting (what percentage of runs pass all checks?)

---

*This contract defines data quality semantics. For orchestration behavior, see the Orchestrator Mental Model. For step behavior, see the Step Contract.*

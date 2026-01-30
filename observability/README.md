# Observability (Sprint 18)

This module adds production-style observability to the PHC_Analytics pipeline.

## Goals

- Make pipeline execution measurable (run-level metrics)
- Persist operational metadata (start/end, status, rows, duration)
- Enable reproducible health checks and basic alerting hooks

## Scope (MVP)

1) **Run log table** (analytics schema)

   - One row per pipeline execution
   - Status: started / success / failed
   - Timestamps + duration
   - Key counters (rows processed)

2) **Step-level metrics** (optional, if needed)

   - Per-step runtime + counters

3) **Health checks**

   - "Last run succeeded"
   - "Freshness within threshold"

## Definition

- **Observability**: ability to understand system behavior from outputs (logs/metrics/traces).
- Here we focus on **logs + metrics** (no distributed tracing required).

## Folder layout

- `observability/sql/`  : DDL + queries for logging/health checks
- `observability/docs/` : notes, sprint narrative, decisions

## How we measure (contract)

A successful run MUST write:

- a `run_id`
- `started_at` and `finished_at`
- `status = success`
- counters (when available)

A failed run MUST write:

- a `run_id`
- `status = failed`
- `error_message` (short, no secrets)

## Non-goals (for this sprint)

- Full tracing (OpenTelemetry)
- External monitoring stacks (Grafana/Prometheus)
- PagerDuty integrations

-- Observability: pipeline run log
-- Contract:
--  - One row per pipeline execution
--  - MUST be written on start and finalized on end
--  - Read-only consumers (analytics / monitoring)
--
-- This table is intentionally simple and explicit.
-- It mirrors patterns used in Airflow, dbt Cloud, Dagster and Databricks.
create schema if not exists analytics;
create table if not exists analytics.pipeline_run_log (
    run_id uuid primary key,
    pipeline_name text not null,
    environment text not null,
    -- e.g. local, ci, prod
    status text not null check (status in ('started', 'success', 'failed')),
    started_at timestamptz not null,
    finished_at timestamptz,
    duration_seconds numeric(10, 2),
    rows_processed bigint,
    error_message text,
    created_at timestamptz not null default now()
);
comment on table analytics.pipeline_run_log is 'Operational run-level log for analytics pipelines (one row per execution).';
comment on column analytics.pipeline_run_log.run_id is 'Unique identifier for a single pipeline execution.';
comment on column analytics.pipeline_run_log.pipeline_name is 'Logical pipeline name (e.g. phc_ingest, phc_analytics_build).';
comment on column analytics.pipeline_run_log.environment is 'Execution environment (local, ci, prod).';
comment on column analytics.pipeline_run_log.status is 'Execution status: started, success or failed.';
comment on column analytics.pipeline_run_log.started_at is 'Timestamp when the pipeline execution started.';
comment on column analytics.pipeline_run_log.finished_at is 'Timestamp when the pipeline execution finished.';
comment on column analytics.pipeline_run_log.duration_seconds is 'Total runtime in seconds (finished_at - started_at).';
comment on column analytics.pipeline_run_log.rows_processed is 'Optional counter of rows processed by the pipeline.';
comment on column analytics.pipeline_run_log.error_message is 'Short error description when status = failed (no secrets).';
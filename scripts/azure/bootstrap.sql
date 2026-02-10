-- Azure bootstrap (idempotent)
-- Creates observability + minimal analytics schema needed for runtime/DQ smoke.

\set ON_ERROR_STOP on

\echo '== observability: pipeline_run_log =='
\i observability/sql/01_pipeline_run_log.sql

\echo '== analytics: dim_customer (minimal) =='
\i sql/analytics/dim_customer.sql

-- Sprint 27: SLO compliance view (14-day window)
-- Joins runtime_kpis_14d (global) + mttr_kpis_14d (incident-based) + slo_targets
-- Run via: psql "$DATABASE_URL" -f sql/analytics/governance/slo_compliance_14d.sql

CREATE OR REPLACE VIEW analytics.slo_compliance_14d AS

WITH pipeline_scope AS (
    SELECT
        'phc_analytics'::text  AS pipeline_name,
        14                     AS window_days
),

runtime AS (
    SELECT
        ps.pipeline_name,
        ps.window_days,
        r.total_runs,
        r.success_runs,
        r.failed_runs,
        r.success_rate_pct,
        r.p50_seconds,
        r.p95_seconds,
        r.avg_seconds
    FROM analytics.runtime_kpis_14d r
    CROSS JOIN pipeline_scope ps
),

mttr AS (
    SELECT
        pipeline_name,
        mttr_avg_seconds
    FROM analytics.mttr_kpis_14d
),

targets AS (
    SELECT DISTINCT ON (st.pipeline_name, st.window_days)
        st.pipeline_name,
        st.window_days,
        st.success_rate_target_pct,
        st.p95_runtime_target_seconds,
        st.mttr_target_seconds,
        st.effective_from
    FROM analytics.slo_targets st
    INNER JOIN pipeline_scope ps
        ON st.pipeline_name = ps.pipeline_name
       AND st.window_days   = ps.window_days
    WHERE st.effective_from <= now()
    ORDER BY st.pipeline_name, st.window_days, st.effective_from DESC
)

SELECT
    r.pipeline_name,
    r.window_days,
    t.effective_from                                        AS target_effective_from,

    -- Targets
    t.success_rate_target_pct,
    t.p95_runtime_target_seconds,
    t.mttr_target_seconds,

    -- Runtime actuals
    r.total_runs,
    r.success_runs,
    r.failed_runs,
    r.success_rate_pct,
    r.p50_seconds,
    r.p95_seconds,
    r.avg_seconds,

    -- MTTR actual (incident-based, null-safe)
    m.mttr_avg_seconds                                      AS mttr_seconds,

    -- Deltas (actual - target; negative = better than target)
    r.success_rate_pct - t.success_rate_target_pct          AS success_rate_delta_pct,
    r.p95_seconds      - t.p95_runtime_target_seconds       AS p95_delta_seconds,
    m.mttr_avg_seconds - t.mttr_target_seconds              AS mttr_delta_seconds,

    -- Status flags
    CASE
        WHEN t.pipeline_name IS NULL                        THEN 'no_target'
        WHEN r.success_rate_pct >= t.success_rate_target_pct THEN 'ok'
        ELSE 'violation'
    END                                                     AS success_rate_status,

    CASE
        WHEN t.pipeline_name IS NULL                        THEN 'no_target'
        WHEN r.p95_seconds <= t.p95_runtime_target_seconds  THEN 'ok'
        ELSE 'violation'
    END                                                     AS p95_status,

    CASE
        WHEN t.pipeline_name IS NULL                        THEN 'no_target'
        WHEN m.mttr_avg_seconds <= t.mttr_target_seconds    THEN 'ok'
        ELSE 'violation'
    END                                                     AS mttr_status,

    -- Overall: 'compliant' only when all three are 'ok'
    CASE
        WHEN t.pipeline_name IS NULL                        THEN 'no_target'
        WHEN r.success_rate_pct >= t.success_rate_target_pct
         AND r.p95_seconds      <= t.p95_runtime_target_seconds
         AND m.mttr_avg_seconds <= t.mttr_target_seconds    THEN 'compliant'
        ELSE 'violated'
    END                                                     AS overall_status,

    now()                                                   AS evaluated_at

FROM runtime r
LEFT JOIN mttr    m ON m.pipeline_name = r.pipeline_name
LEFT JOIN targets t ON t.pipeline_name = r.pipeline_name
                   AND t.window_days   = r.window_days
;

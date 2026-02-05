from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from orchestration.db.psql import run_psql_file
from orchestration.dq.contract import (
    DQDefinition,
    DQOutcome,
    DQResult,
    DQSeverity,
)

SQL_DQ_NOT_NULL_CUSTOMER_ID = Path("sql/data_quality/dim_customer/not_null_customer_id.sql")


def dq_dim_customer_not_null_customer_id(ctx: Any) -> DQOutcome:
    database_url = getattr(ctx, "database_url", "")
    if not database_url:
        raise RuntimeError("ctx.database_url is required for DQ execution")

    out = run_psql_file(
        database_url,
        SQL_DQ_NOT_NULL_CUSTOMER_ID,
        vars={
            "pipeline_name": getattr(ctx, "pipeline_name", "phc_analytics"),
            "environment": getattr(ctx, "environment", "local"),
        },
        quiet=True,
    )

    details: Dict[str, Any] = {}
    if out.strip():
        first_line = out.splitlines()[0] if out else ""
        details = {"sample": first_line}
        return DQOutcome(
            check_id="dq_dim_customer_not_null_customer_id",
            severity=DQSeverity.BLOCKER,
            result=DQResult.FAIL,
            details=details,
        )

    return DQOutcome(
        check_id="dq_dim_customer_not_null_customer_id",
        severity=DQSeverity.BLOCKER,
        result=DQResult.PASS,
        details={"note": "0 violations"},
    )


def definition() -> DQDefinition:
    return DQDefinition(
        check_id="dq_dim_customer_not_null_customer_id",
        severity=DQSeverity.BLOCKER,
        fn=dq_dim_customer_not_null_customer_id,
    )

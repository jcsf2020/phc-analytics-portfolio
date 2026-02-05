from __future__ import annotations

from typing import List

from orchestration.dq.contract import DQDefinition
from orchestration.dq.checks.dim_customer_not_null_customer_id import (
    definition as dim_customer_not_null_customer_id_definition,
)


def get_pre_run_dq_checks() -> List[DQDefinition]:
    # Sprint 23.2: primeiro DQ real (BLOCKER)
    return [dim_customer_not_null_customer_id_definition()]


def get_post_step_dq_checks(*, step_id: str) -> List[DQDefinition]:
    _ = step_id
    return []


def get_end_run_dq_checks() -> List[DQDefinition]:
    return []

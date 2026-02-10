from __future__ import annotations

from typing import List

from orchestration.dq.checks import (
    get_end_run_dq_checks as _get_end_run_dq_checks,
    get_post_step_dq_checks as _get_post_step_dq_checks,
    get_pre_run_dq_checks as _get_pre_run_dq_checks,
)
from orchestration.dq.contract import DQDefinition


def get_pre_run_dq_checks() -> List[DQDefinition]:
    return _get_pre_run_dq_checks()


def get_post_step_dq_checks(*, step_id: str) -> List[DQDefinition]:
    return _get_post_step_dq_checks(step_id=step_id)


def get_end_run_dq_checks() -> List[DQDefinition]:
    return _get_end_run_dq_checks()

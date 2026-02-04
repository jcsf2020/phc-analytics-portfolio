from __future__ import annotations

from enum import Enum


class EventType(str, Enum):
    # Run lifecycle
    RUN_STARTED = "run_started"
    RUN_FINISHED = "run_finished"

    # Step lifecycle
    STEP_STARTED = "step_started"
    STEP_FINISHED = "step_finished"
    STEP_FAILED = "step_failed"

    # Health gates / Data Quality
    GATE_EXECUTED = "gate_executed"
    DQ_CHECK_EXECUTED = "dq_check_executed"

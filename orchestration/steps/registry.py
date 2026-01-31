from __future__ import annotations

from orchestration.steps.contracts import Step


def get_steps() -> list[Step]:
    """
    Sprint 20: static registry (simple + deterministic).
    Order matters.
    NOTE: Keep imports inside this function to avoid circular imports.
    """
    from orchestration.steps.last_run_check import LastRunCheck
    from orchestration.steps.sample_step import SampleStep

    return [
        LastRunCheck(),
        SampleStep(),
    ]

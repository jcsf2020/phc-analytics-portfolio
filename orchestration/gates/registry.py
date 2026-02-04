from __future__ import annotations

from typing import Iterable, List

from orchestration.gates.model import GateDefinition, GateSeverity
from orchestration.gates.health_last_run import health_last_run


def get_pre_run_gates() -> List[GateDefinition]:
    """Return the static list of pre-run gates.

    Ordering is significant and deterministic.
    This registry is the single source of truth for which
    gates execute before pipeline steps.
    """

    return [
        GateDefinition(
            gate_id="health_last_run",
            severity=GateSeverity.WARN,
            fn=health_last_run,
        ),
    ]


def iter_pre_run_gates() -> Iterable[GateDefinition]:
    """Iterate pre-run gates in execution order."""
    return get_pre_run_gates()


def get_post_step_gates(step_id: str) -> List[GateDefinition]:
    """Return the static list of post-step gates for a given step.

    This registry defines which gates execute immediately after
    a specific step finishes.
    """

    # No post-step gates defined yet (Sprint 22 baseline).
    return []


def iter_post_step_gates(step_id: str) -> Iterable[GateDefinition]:
    """Iterate post-step gates for a given step in execution order."""
    return get_post_step_gates(step_id)


def get_end_run_gates() -> List[GateDefinition]:
    """Return the static list of end-run gates.

    End-run gates execute after all steps complete,
    regardless of run success or failure.
    """

    # No end-run gates defined yet (Sprint 22 baseline).
    return []


def iter_end_run_gates() -> Iterable[GateDefinition]:
    """Iterate end-run gates in execution order."""
    return get_end_run_gates()

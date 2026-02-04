from __future__ import annotations

from typing import Any, Iterable, List

from orchestration.events.event_types import EventType
from orchestration.events.writer import EventStreamWriter
from orchestration.gates.model import (
    GateDefinition,
    GateOutcome,
    GateResult,
    GateSeverity,
)


def run_gate(
    *,
    gate: GateDefinition,
    ctx: Any,
    writer: EventStreamWriter,
) -> GateOutcome:
    """Execute a single gate and emit a GATE_EXECUTED event.

    Contract:
    - Gate functions are read-only.
    - Result PASS/FAIL is determined solely by the gate function outcome.
    - Severity controls whether the caller should halt on FAIL.
    """

    outcome = gate.fn(ctx)

    if not isinstance(outcome, GateOutcome):
        raise TypeError(
            f"Gate function for {gate.gate_id} must return GateOutcome, "
            f"got {type(outcome).__name__}"
        )

    # Normalize identity/severity (defensive)
    outcome = GateOutcome(
        gate_id=gate.gate_id,
        severity=gate.severity,
        result=outcome.result,
        details=outcome.details,
    )

    writer.write(
        EventType.GATE_EXECUTED,
        gate_id=outcome.gate_id,
        severity=outcome.severity.value,
        result=outcome.result.value,
        details=outcome.details,
    )

    return outcome


def should_block(outcome: GateOutcome) -> bool:
    """Return True if this outcome should halt execution."""
    return (
        outcome.result == GateResult.FAIL and outcome.severity == GateSeverity.BLOCKER
    )


class GateRunner:
    """Run a sequence of gates and emit events.

    This is a minimal runtime helper (Sprint 22 / Phase 2):
    - Executes gates in the given order.
    - Emits one `GATE_EXECUTED` event per gate via `run_gate(...)`.
    - If a gate fails with BLOCKER severity, stops early and returns.

    It does not own the registry; callers pass the gates explicitly.
    """

    def run(
        self,
        *,
        gates: Iterable[GateDefinition],
        ctx: Any,
        writer: EventStreamWriter,
    ) -> List[GateOutcome]:
        outcomes: List[GateOutcome] = []

        for gate in gates:
            outcome = run_gate(gate=gate, ctx=ctx, writer=writer)
            outcomes.append(outcome)

            if should_block(outcome):
                break

        return outcomes

from __future__ import annotations

from typing import Any

from orchestration.gates.model import GateOutcome, GateResult, GateSeverity


def health_last_run(ctx: Any) -> GateOutcome:
    """Baseline health gate.

    Sprint 22 / Phase 2:
    - Placeholder gate to validate wiring (registry -> runner -> pipeline).
    - Must be read-only and deterministic.
    - Returns PASS by default.
    """

    return GateOutcome(
        gate_id="health_last_run",
        severity=GateSeverity.WARN,
        result=GateResult.PASS,
        details={"note": "baseline gate (wiring check)"},
    )

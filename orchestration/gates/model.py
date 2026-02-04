from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Protocol

from orchestration.events.writer import check_slug


class GateResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class GateSeverity(str, Enum):
    WARN = "WARN"
    BLOCKER = "BLOCKER"


class GateFn(Protocol):
    """A gate function returns a GateResult plus optional metadata.

    Gates are read-only checks (health/DQ) and must not mutate state.
    """

    def __call__(self, ctx: Any) -> "GateOutcome": ...


@dataclass(frozen=True)
class GateDefinition:
    """Static definition of a gate.

    - gate_id must be stable and slug-safe (use check_slug)
    - severity controls fail behavior (WARN continues, BLOCKER halts)
    """

    gate_id: str
    severity: GateSeverity
    fn: GateFn

    def __post_init__(self) -> None:
        object.__setattr__(self, "gate_id", check_slug(self.gate_id))


@dataclass(frozen=True)
class GateOutcome:
    """Outcome of executing a gate."""

    gate_id: str
    severity: GateSeverity
    result: GateResult
    details: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "gate_id", check_slug(self.gate_id))

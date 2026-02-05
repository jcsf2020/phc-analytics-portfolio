from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, List, Mapping, Protocol

from orchestration.events.writer import check_slug


class DQResult(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class DQSeverity(str, Enum):
    WARN = "WARN"
    BLOCKER = "BLOCKER"


class DQFn(Protocol):
    """A data quality check function returns a DQOutcome plus optional metadata.

    DQ checks are read-only assertions and must not mutate state.
    """

    def __call__(self, ctx: Any) -> "DQOutcome": ...


@dataclass(frozen=True)
class DQDefinition:
    """Static definition of a DQ check.

    - check_id must be stable and slug-safe (use check_slug)
    - severity controls fail behavior (WARN continues, BLOCKER halts)
    """

    check_id: str
    severity: DQSeverity
    fn: DQFn

    def __post_init__(self) -> None:
        object.__setattr__(self, "check_id", check_slug(self.check_id))


@dataclass(frozen=True)
class DQOutcome:
    """Outcome of executing a DQ check."""

    check_id: str
    severity: DQSeverity
    result: DQResult
    details: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "check_id", check_slug(self.check_id))


def should_block(outcome: DQOutcome) -> bool:
    """Return True if this outcome should halt execution."""
    return outcome.result == DQResult.FAIL and outcome.severity == DQSeverity.BLOCKER


class DQRunner:
    """Run a sequence of DQ checks.

    Sprint 23 / Phase 1:
    - Executes checks in the given order.
    - Does not own any registry; callers pass the checks explicitly.
    - Fail-fast on BLOCKER.

    Note: event emission is intentionally deferred until the DQ event contract
    is finalized (keeps this layer pure + testable).
    """

    def run(self, *, checks: Iterable[DQDefinition], ctx: Any) -> List[DQOutcome]:
        outcomes: List[DQOutcome] = []

        for check in checks:
            outcome = check.fn(ctx)
            if not isinstance(outcome, DQOutcome):
                raise TypeError(
                    f"DQ function for {check.check_id} must return DQOutcome, "
                    f"got {type(outcome).__name__}"
                )

            # Normalize identity/severity (defensive)
            outcome = DQOutcome(
                check_id=check.check_id,
                severity=check.severity,
                result=outcome.result,
                details=outcome.details,
            )
            outcomes.append(outcome)

            if should_block(outcome):
                break

        return outcomes

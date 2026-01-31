from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from orchestration.run_pipeline import RunContext


class Step(Protocol):
    """Pipeline step contract (tool-agnostic)."""

    name: str

    def run(self, ctx: "RunContext") -> int:
        """Execute step and return rows_processed (>=0)."""
        ...


@dataclass(frozen=True)
class StepResult:
    name: str
    rows_processed: int

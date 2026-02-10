from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from orchestration.steps.contracts import Step

if TYPE_CHECKING:
    from orchestration.run_pipeline import RunContext


@dataclass
class DQFolderStep(Step):
    """Run SQL-based data-quality checks from a folder.

    Contract per check file:
    - 0 rows returned => PASS
    - 1+ rows returned => FAIL
    """

    step_name: str = "data_quality"
    folder: Path = Path("sql/data_quality")
    glob_pattern: str = "**/*.sql"

    @property
    def name(self) -> str:
        return self.step_name

    def run(self, ctx: "RunContext") -> int:
        from orchestration.db.psql import run_psql_file

        if not self.folder.exists():
            print(f"[STEP] {self.name} | folder_missing={self.folder}")
            return 0

        files = sorted(self.folder.glob(self.glob_pattern))
        print(f"[STEP] {self.name} | checks={len(files)} | folder={self.folder}")

        for sql_file in files:
            out = run_psql_file(
                ctx.database_url,
                sql_file,
                vars={},
                quiet=True,
            )

            if out.strip():
                lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
                sample = " | ".join(lines[:3])
                raise RuntimeError(
                    f"dq_failed: {sql_file} returned rows (expected 0). Sample: {sample[:240]}"
                )

        return 0


# Backward compatible alias (kept only to avoid changing old import paths).
class SampleStep(DQFolderStep):
    pass


def get_steps() -> list[Step]:
    """Static step registry (simple + deterministic). Order matters."""
    from orchestration.steps.last_run_check import LastRunCheck

    return [
        LastRunCheck(),
        DQFolderStep(),
    ]

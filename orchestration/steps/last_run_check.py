from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orchestration.run_pipeline import RunContext


class LastRunCheck:
    name = "last_run_check"

    def __init__(self, max_age_minutes: int = 60) -> None:
        self.max_age_minutes = int(max_age_minutes)

    def run(self, ctx: "RunContext") -> int:
        """
        Gate: require at least one SUCCESS run in the last N minutes.

        Contract:
        - SQL must return:
            1 -> OK
            0 -> FAIL
        """
        print(
            f"[STEP] last_run_check | "
            f"pipeline={ctx.pipeline_name} | "
            f"env={ctx.environment} | "
            f"max_age_minutes={self.max_age_minutes}"
        )

        sql_path = Path("orchestration/sql/health_last_success.sql")
        if not sql_path.exists():
            raise RuntimeError(f"health SQL not found: {sql_path}")

        cmd = [
            "psql",
            ctx.database_url,
            "-qAt",  # quiet | unaligned | tuples-only
            "-v",
            "ON_ERROR_STOP=1",  # fail hard on SQL error
            "-v",
            f"pipeline_name={ctx.pipeline_name}",
            "-v",
            f"environment={ctx.environment}",
            "-v",
            f"max_age_minutes={self.max_age_minutes}",
            "-f",
            str(sql_path),
        ]

        out = subprocess.check_output(cmd, text=True).strip()
        code = int(out) if out else 0

        if code != 1:
            raise RuntimeError(
                f"health_gate_failed: no SUCCESS run in last {self.max_age_minutes} minutes"
            )

        return 0

"""
PHC_Analytics - Orchestration (Sprint 19)

Goal:
- Provide a minimal orchestration entrypoint that can be evolved into a scheduler-ready runner.
- Integrate with the Sprint 18 observability SQL contracts (run_start / run_finish / health).

Design constraints:
- No new Python dependencies.
- Use `psql` via subprocess so the runner works anywhere psql is available.
- Keep this file self-contained and explicit (portfolio-friendly).

Usage examples:

  # Health check (returns 0 rows when healthy, 1+ rows when unhealthy)
  export DATABASE_URL='postgresql://...'
  python orchestration/run_pipeline.py health --pipeline phc_analytics --env local --max-age-minutes 60

  # Start + finish a run (no steps yet; reserved for Sprint 19 expansion)
  python orchestration/run_pipeline.py run --pipeline phc_analytics --env local --rows 0

Notes:
- This is an MVP scaffold. Sprint 19 will add real "steps" and a step registry.
"""

from __future__ import annotations

import argparse
import re
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional



from orchestration.steps.registry import get_steps
REPO_ROOT = Path(__file__).resolve().parents[1]
OBS_SQL_DIR = REPO_ROOT / "observability" / "sql"

SQL_RUN_START = OBS_SQL_DIR / "02_run_start.sql"
SQL_RUN_FINISH = OBS_SQL_DIR / "03_run_finish.sql"
SQL_HEALTH_LAST_RUN = OBS_SQL_DIR / "04_health_last_run.sql"


@dataclass(frozen=True)
class RunContext:
    database_url: str
    pipeline_name: str
    environment: str


def _require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")


def _run_psql_file(
    database_url: str,
    sql_file: Path,
    *,
    vars: dict[str, str],
    quiet: bool = False,
) -> str:
    """
    Execute a .sql file via psql and return stdout.

    We rely on psql variable binding: -v key='value'
    """
    _require_file(sql_file)

    cmd: list[str] = [
        "psql",
        database_url,
        "-v",
        "ON_ERROR_STOP=1",
        "-f",
        str(sql_file),
    ]
    for k, v in vars.items():
        cmd.extend(["-v", f"{k}={v}"])

    if quiet:
        # -q: quiet; -t: tuples-only; -A: unaligned
        cmd.insert(2, "-qAt")

    proc = subprocess.run(
        cmd,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        stdout = (proc.stdout or "").strip()
        msg = stderr if stderr else stdout
        raise RuntimeError(f"psql failed ({sql_file.name}): {msg}")
    return (proc.stdout or "").strip()


_RUN_ID_RE = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)


def _extract_run_id(psql_stdout: str) -> str:
    """Extract run_id (UUID) from psql output of 02_run_start.sql."""
    out = psql_stdout or ""
    m = _RUN_ID_RE.search(out)
    if not m:
        tail = [ln.strip() for ln in out.splitlines() if ln.strip()][-5:]
        raise RuntimeError(f"Could not extract run_id from output tail: {tail}")
    return m.group(0)


def cmd_health(ctx: RunContext, max_age_minutes: int) -> int:
    """
    Health check contract:
    - 0 rows => healthy (exit 0)
    - 1+ rows => unhealthy/stale (exit 2)
    """
    out = _run_psql_file(
        ctx.database_url,
        SQL_HEALTH_LAST_RUN,
        vars={
            "pipeline_name": ctx.pipeline_name,
            "environment": ctx.environment,
            "max_age_minutes": str(max_age_minutes),
        },
        quiet=True,
    )

    # If healthy, the query contract returns 0 rows -> stdout empty in -qAt mode.
    if not out.strip():
        print("OK: healthy")
        return 0

    # Unhealthy: print rows for visibility and return non-zero.
    print(out)
    return 2


def cmd_run(ctx: RunContext, rows_processed: Optional[int], dry_run: bool) -> int:
    """
    Run contract (MVP):
    - create a run_id row as "started"
    - (Sprint 19) run real steps
    - finalize row as success/failed

    For now: no steps. This is a scaffold to wire in step execution next.
    """
    if dry_run:
        print("DRY RUN: skipping database writes")
        return 0

    # 1) start run
    start_out = _run_psql_file(
        ctx.database_url,
        SQL_RUN_START,
        vars={
            "pipeline_name": ctx.pipeline_name,
            "environment": ctx.environment,
        },
        quiet=False,
    )
    run_id = _extract_run_id(start_out)
    print(f"run_id={run_id}")

    status = "success"
    error_message = ""
    try:
        total_rows = 0
        for step in get_steps():
            n = step.run(ctx)
            if n is None:
                n = 0
            if n < 0:
                raise RuntimeError(f"Step {step.name} returned negative rows: {n}")
            total_rows += int(n)
    except Exception as exc:  # pragma: no cover
        status = "failed"
        error_message = str(exc)[:240]
    finally:
        # 2) finish run
        finish_vars = {
            "run_id": run_id,
            "status": status,
            "rows_processed": str(total_rows) if rows_processed is None else str(rows_processed),
            "error_message": error_message,
        }
        _run_psql_file(ctx.database_url, SQL_RUN_FINISH, vars=finish_vars, quiet=False)

    return 0 if status == "success" else 1


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="run_pipeline.py")
    p.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL", ""),
        help="PostgreSQL connection string. Defaults to env DATABASE_URL.",
    )
    p.add_argument("--pipeline", default="phc_analytics", help="Logical pipeline name.")
    p.add_argument(
        "--env", default="local", help="Execution environment: local|ci|prod."
    )

    sub = p.add_subparsers(dest="command", required=True)

    p_health = sub.add_parser("health", help="Run health check (last run freshness).")
    p_health.add_argument("--max-age-minutes", type=int, default=1440)

    p_run = sub.add_parser("run", help="Start+finish a run (MVP scaffold).")
    p_run.add_argument(
        "--rows", type=int, default=None, help="Optional rows processed."
    )
    p_run.add_argument("--dry-run", action="store_true", help="Skip database writes.")

    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)

    if not args.database_url:
        print(
            "ERROR: DATABASE_URL is empty. Export DATABASE_URL or pass --database-url.",
            file=sys.stderr,
        )
        return 2

    # Ensure required SQL assets exist (fail fast with clear errors).
    _require_file(SQL_RUN_START)
    _require_file(SQL_RUN_FINISH)
    _require_file(SQL_HEALTH_LAST_RUN)

    ctx = RunContext(
        database_url=args.database_url,
        pipeline_name=args.pipeline,
        environment=args.env,
    )

    if args.command == "health":
        return cmd_health(ctx, args.max_age_minutes)

    if args.command == "run":
        return cmd_run(ctx, args.rows, args.dry_run)

    print(f"ERROR: unknown command: {args.command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

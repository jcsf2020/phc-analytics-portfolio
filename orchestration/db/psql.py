from __future__ import annotations

from pathlib import Path
import subprocess


def require_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")


def run_psql_file(
    database_url: str,
    sql_file: Path,
    *,
    vars: dict[str, str],
    quiet: bool = False,
) -> str:
    """
    Execute a .sql file via psql and return stdout.

    We rely on psql variable binding: -v key='value'
    Contract used across orchestration + DQ.
    """
    require_file(sql_file)

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

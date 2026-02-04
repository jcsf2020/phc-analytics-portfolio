from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from orchestration.events.event_types import EventType


_SLUG_RE = re.compile(r"[^a-z0-9]+")


def check_slug(value: str) -> str:
    """Normalize a user/system-provided identifier into a stable slug.

    Why this exists:
    - Event streams must be queryable and aggregatable.
    - We want a canonical, filesystem-safe key for event ids (e.g., step ids,
      gate ids, dq check ids) with no spaces or casing ambiguity.

    Rules:
    - lowercase
    - non [a-z0-9] collapses to single underscore
    - trim leading/trailing underscores

    Note: This function does NOT validate business semantics; it only
    normalizes for stability.
    """

    v = value.strip().lower()
    v = _SLUG_RE.sub("_", v)
    v = v.strip("_")
    if not v:
        raise ValueError("slug is empty after normalization")
    return v


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_json(obj: Any) -> Any:
    """Best-effort JSON safety. Falls back to `str()` for unknown types."""

    try:
        json.dumps(obj)
        return obj
    except TypeError:
        return str(obj)


@dataclass(frozen=True)
class EventStreamPaths:
    base_dir: Path
    jsonl_path: Path
    summary_path: Path


def build_event_stream_paths(
    *,
    base_dir: str | Path = "out/event_stream",
    pipeline: str,
    env: str,
    run_id: str,
) -> EventStreamPaths:
    """Return canonical paths for a given run's event stream artifacts."""

    base = Path(base_dir)
    run_dir = base / check_slug(pipeline) / check_slug(env) / check_slug(run_id)
    return EventStreamPaths(
        base_dir=run_dir,
        jsonl_path=run_dir / "events.jsonl",
        summary_path=run_dir / "summary.json",
    )


class EventStreamWriter:
    """Append-only JSONL event stream + small run summary.

    Contract:
    - Each call to `write(...)` appends exactly one JSON object line to JSONL.
    - Summary is updated incrementally and can be used for quick run dashboards.

    This is intentionally minimal (Sprint 22 / Phase 1). No DB writes.
    """

    def __init__(
        self,
        *,
        pipeline: str,
        env: str,
        run_id: str,
        base_dir: str | Path = "out/event_stream",
    ) -> None:
        self.pipeline = check_slug(pipeline)
        self.env = check_slug(env)
        self.run_id = check_slug(run_id)
        self.paths = build_event_stream_paths(
            base_dir=base_dir,
            pipeline=self.pipeline,
            env=self.env,
            run_id=self.run_id,
        )

        self.paths.base_dir.mkdir(parents=True, exist_ok=True)

        # Initialize summary if missing.
        if not self.paths.summary_path.exists():
            self._write_summary(
                {
                    "pipeline": self.pipeline,
                    "env": self.env,
                    "run_id": self.run_id,
                    "started_at": None,
                    "finished_at": None,
                    "status": None,
                    "events": 0,
                    "steps": {"started": 0, "finished": 0, "failed": 0},
                    "gates": {"executed": 0, "failed": 0, "blockers": 0},
                    "dq": {"executed": 0, "failed": 0, "blockers": 0},
                }
            )

    def write(self, event_type: EventType, **fields: Any) -> None:
        """Append a single event line and update summary counters."""

        event = {
            "ts": _utc_now_iso(),
            "event_type": event_type.value,
            "pipeline": self.pipeline,
            "env": self.env,
            "run_id": self.run_id,
            "data": {k: _safe_json(v) for k, v in fields.items()},
        }

        self._append_jsonl(event)
        self._update_summary_from_event(event)

    def _append_jsonl(self, event: dict[str, Any]) -> None:
        with self.paths.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False))
            f.write("\n")

    def _read_summary(self) -> dict[str, Any]:
        with self.paths.summary_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_summary(self, summary: dict[str, Any]) -> None:
        with self.paths.summary_path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
            f.write("\n")

    def _update_summary_from_event(self, event: dict[str, Any]) -> None:
        summary = self._read_summary()
        summary["events"] = int(summary.get("events", 0)) + 1

        et = event.get("event_type")
        data = event.get("data", {})

        if et == EventType.RUN_STARTED.value:
            summary["started_at"] = summary.get("started_at") or event.get("ts")
            summary["status"] = "running"

        if et == EventType.RUN_FINISHED.value:
            summary["finished_at"] = event.get("ts")
            # allow caller to send status in data
            status = data.get("status")
            if isinstance(status, str):
                summary["status"] = status

        if et == EventType.STEP_STARTED.value:
            summary["steps"]["started"] += 1

        if et == EventType.STEP_FINISHED.value:
            summary["steps"]["finished"] += 1

        if et == EventType.STEP_FAILED.value:
            summary["steps"]["failed"] += 1
            summary["status"] = "failed"

        if et == EventType.GATE_EXECUTED.value:
            summary["gates"]["executed"] += 1
            result = data.get("result")
            severity = data.get("severity")
            if result == "FAIL":
                summary["gates"]["failed"] += 1
                if severity == "BLOCKER":
                    summary["gates"]["blockers"] += 1
                    summary["status"] = "failed"

        if et == EventType.DQ_CHECK_EXECUTED.value:
            summary["dq"]["executed"] += 1
            result = data.get("result")
            severity = data.get("severity")
            if result == "FAIL":
                summary["dq"]["failed"] += 1
                if severity == "BLOCKER":
                    summary["dq"]["blockers"] += 1
                    summary["status"] = "failed"

        self._write_summary(summary)

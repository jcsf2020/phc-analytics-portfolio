from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Optional

from .pipeline_settings import STATE_FILE


def _default_state() -> Dict[str, Any]:
    return {
        "version": 1,
        "watermarks": {},  # entity -> ISO datetime string
        "updated_at": datetime.utcnow().isoformat(timespec="seconds"),
    }


def load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return _default_state()

    with STATE_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: Dict[str, Any]) -> None:
    state["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)
        f.write("\n")


def get_watermark(entity: str) -> Optional[str]:
    state = load_state()
    return state.get("watermarks", {}).get(entity)


def set_watermark(entity: str, watermark_iso: str) -> None:
    state = load_state()
    state.setdefault("watermarks", {})[entity] = watermark_iso
    save_state(state)

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


def _parse_iso(dt: str) -> datetime:
    # assumes ISO-8601 without timezone, as used in this MVP
    return datetime.fromisoformat(dt)


def filter_incremental_by_watermark(
    rows: List[Dict[str, Any]],
    *,
    watermark_iso: Optional[str],
    watermark_field: str = "updated_at",
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """
    Incremental filter using a watermark.

    Keeps rows where row[watermark_field] > watermark_iso.
    Returns (filtered_rows, new_watermark_iso).

    - If watermark_iso is None: returns all rows and sets watermark to max(field).
    - If rows empty: returns empty and keeps watermark as-is.
    """
    if not rows:
        return [], watermark_iso

    # Validate field presence
    for r in rows:
        if watermark_field not in r:
            raise KeyError(f"Missing watermark field '{watermark_field}' in row: {r.keys()}")

    # Compute max watermark in current batch
    batch_max = max(_parse_iso(r[watermark_field]) for r in rows)
    batch_max_iso = batch_max.isoformat(timespec="seconds")

    if watermark_iso is None:
        return rows, batch_max_iso

    wm = _parse_iso(watermark_iso)
    filtered = [r for r in rows if _parse_iso(r[watermark_field]) > wm]

    if not filtered:
        return [], watermark_iso

    new_max = max(_parse_iso(r[watermark_field]) for r in filtered)
    return filtered, new_max.isoformat(timespec="seconds")

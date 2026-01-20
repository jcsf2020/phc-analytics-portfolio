from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import psycopg2
import psycopg2.extras

from phc_analytics.integrations.prestashop.client import (
    PrestaShopClient,
    PrestaShopConfig,
)
from phc_analytics.storage.watermarks import WatermarkManager


@dataclass(frozen=True)
class RawRecord:
    """Normalized record to load into raw.* tables."""

    record_id: str
    payload: Dict[str, Any]
    source_updated_at: Optional[str]  # keep as ISO string for now (bootstrap)


def _normalize_records(
    items: Iterable[Dict[str, Any]], id_key: str, updated_at_key: str
) -> List[RawRecord]:
    out: List[RawRecord] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        rid = str(it.get(id_key) or "").strip()
        if not rid:
            continue
        updated = it.get(updated_at_key)
        out.append(
            RawRecord(
                record_id=rid,
                payload=it,
                source_updated_at=str(updated) if updated is not None else None,
            )
        )
    return out


def _max_source_updated_at(records: List[RawRecord]) -> Optional[str]:
    # Bootstrap: compare lexicographically; later we should parse to datetime.
    vals = [r.source_updated_at for r in records if r.source_updated_at]
    return max(vals) if vals else None


def upsert_raw_orders(dsn: str, records: List[RawRecord]) -> None:
    """
    TODO: Implement UPSERT into raw.prestashop_orders:
      - order_id (text PK) <- record_id
      - payload (jsonb)
      - source_updated_at (timestamptz)
      - ingested_at (timestamptz default now)
    """
    if not records:
        return

    rows = [
        (
            r.record_id,
            psycopg2.extras.Json(r.payload),
            r.source_updated_at,
        )
        for r in records
    ]

    sql = """
    INSERT INTO raw.prestashop_orders (order_id, payload, source_updated_at)
    VALUES %s
    ON CONFLICT (order_id)
    DO UPDATE SET
        payload = EXCLUDED.payload,
        source_updated_at = EXCLUDED.source_updated_at,
        ingested_at = now()
    """

    with psycopg2.connect(dsn) as conn:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                sql,
                rows,
                template="(%s, %s::jsonb, %s::timestamptz)",
                page_size=1000,
            )
        conn.commit()


def upsert_raw_customers(dsn: str, records: List[RawRecord]) -> None:
    """TODO: Implement UPSERT into raw.prestashop_customers (customer_id PK)."""
    raise NotImplementedError


def upsert_raw_products(dsn: str, records: List[RawRecord]) -> None:
    """TODO: Implement UPSERT into raw.prestashop_products (product_id PK)."""
    raise NotImplementedError


def run_prestashop_to_raw(
    *,
    dsn: str,
    prestashop_base_url: str,
    prestashop_api_key: str,
) -> Dict[str, Any]:
    """
    PrestaShop -> Postgres raw ingestion with incremental watermarks.

    Rule:
    - Read watermark for entity
    - Extract records since watermark (when supported)
    - UPSERT to raw table
    - Advance watermark to max(source_updated_at) loaded successfully
    """
    wm = WatermarkManager(dsn)
    client = PrestaShopClient(
        PrestaShopConfig(base_url=prestashop_base_url, api_key=prestashop_api_key)
    )
    _ = client  # placeholder until extraction is wired

    results: Dict[str, Any] = {"entities": {}}

    entities: List[Tuple[str, str, str]] = [
        # (entity_name, id_key, updated_at_key)
        ("prestashop_orders", "id", "date_upd"),
        ("prestashop_customers", "id", "date_upd"),
        ("prestashop_products", "id", "date_upd"),
    ]

    for entity_name, id_key, updated_at_key in entities:
        state = wm.get(entity_name)
        since = state.watermark_ts if state else "1970-01-01T00:00:00Z"

        # TODO: wire real incremental extraction in client based on `since`
        # For now, keep placeholder to avoid guessing method names.
        extracted: List[Dict[str, Any]] = []

        records = _normalize_records(
            extracted, id_key=id_key, updated_at_key=updated_at_key
        )
        max_ts = _max_source_updated_at(records)

        if entity_name == "prestashop_orders":
            upsert_raw_orders(dsn, records)
        elif entity_name == "prestashop_customers":
            upsert_raw_customers(dsn, records)
        elif entity_name == "prestashop_products":
            upsert_raw_products(dsn, records)
        else:
            raise ValueError(f"Unknown entity: {entity_name}")

        if max_ts:
            wm.set(entity_name, max_ts)

        results["entities"][entity_name] = {
            "since": since,
            "extracted": len(extracted),
            "loaded": len(records),
            "max_source_updated_at": max_ts,
        }

    return results

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any


def to_date_key(dt: str) -> int:
    """
    Converte timestamp ISO (YYYY-MM-DDTHH:MM:SS)
    para date_key no formato YYYYMMDD.
    """
    parsed = datetime.fromisoformat(dt)
    return int(parsed.strftime("%Y%m%d"))


def enrich_orders_with_date(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enriquecimento da fact_orders:
    - adiciona order_date_key
    - mantém dados originais intactos
    """
    enriched = []

    for o in orders:
        created_at = o.get("created_at")
        if not created_at:
            raise ValueError("Order missing created_at")

        enriched.append(
            {
                **o,
                "order_date_key": to_date_key(created_at),
            }
        )

    return enriched

from __future__ import annotations

from typing import Dict, Any, List
from datetime import datetime


def enrich_order_lines(
    order_lines: List[Dict[str, Any]],
    orders: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Enrich order lines with:
    - prestashop_customer_id (from order)
    - order_date_key (YYYYMMDD from order.created_at)

    Result = fact_order_lines (analytics-ready).
    """

    # Index orders by prestashop_order_id for fast lookup
    orders_by_id = {
        o["prestashop_order_id"]: o
        for o in orders
    }

    enriched: List[Dict[str, Any]] = []

    for line in order_lines:
        order_id = line["prestashop_order_id"]

        if order_id not in orders_by_id:
            raise ValueError(f"Order {order_id} not found for order line")

        order = orders_by_id[order_id]

        # Build date key (YYYYMMDD)
        created_at = order["created_at"]
        date_key = int(datetime.fromisoformat(created_at).strftime("%Y%m%d"))

        enriched.append(
            {
                "prestashop_order_id": order_id,
                "prestashop_product_id": line["prestashop_product_id"],
                "prestashop_customer_id": order["prestashop_customer_id"],
                "order_date_key": date_key,
                "quantity": line["quantity"],
                "unit_price": line["unit_price"],
                "line_total": line["line_total"],
            }
        )

    return enriched

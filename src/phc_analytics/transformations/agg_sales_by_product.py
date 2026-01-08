from __future__ import annotations

from typing import Dict, Any, List


def agg_sales_by_product(
    fact_order_lines: List[Dict[str, Any]],
    dim_product: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Aggregate sales by product.

    Grain (granularidade):
    - 1 row per product_key

    Metrics:
    - units_sold = sum(quantity)
    - revenue = sum(line_total)
    """

    # index product dimension by product_key
    prod_by_key = {p["product_key"]: p for p in dim_product}

    agg: Dict[int, Dict[str, Any]] = {}

    for row in fact_order_lines:
        product_key = row["prestashop_product_id"]  # MVP: equals product_key in dim_product

        if product_key not in prod_by_key:
            raise ValueError(f"Product {product_key} not found in dim_product")

        if product_key not in agg:
            agg[product_key] = {
                "product_key": product_key,
                "product_name": prod_by_key[product_key].get("name"),
                "units_sold": 0.0,
                "revenue": 0.0,
            }

        agg[product_key]["units_sold"] += float(row.get("quantity", 0) or 0)
        agg[product_key]["revenue"] += float(row.get("line_total", 0) or 0)

    # return as list (optionally you can sort later)
    return list(agg.values())

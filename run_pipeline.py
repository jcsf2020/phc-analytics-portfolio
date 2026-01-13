from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import csv
from typing import Any, Dict, List

from src.phc_analytics.config.pipeline_settings import GOLD_DIR, SERVING_DIR, WATERMARK_FIELD
from src.phc_analytics.config.pipeline_state import get_watermark, set_watermark

from src.phc_analytics.integrations.prestashop.client import PrestaShopClient, PrestaShopConfig
from src.phc_analytics.pipeline.incremental import filter_incremental_by_watermark
from src.phc_analytics.transformations.prestashop_normalize import (
    normalize_customers,
    normalize_products,
    normalize_orders,
    normalize_order_lines,
)
from src.phc_analytics.transformations.dim_customer import build_dim_customer
from src.phc_analytics.transformations.dim_product import build_dim_product
from src.phc_analytics.transformations.dim_date import generate_dim_date
from src.phc_analytics.transformations.fact_orders_enrich import enrich_orders_with_date
from src.phc_analytics.transformations.fact_order_lines_enrich import enrich_order_lines
from src.phc_analytics.transformations.agg_sales_by_product import agg_sales_by_product


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    """
    Write list[dict] to CSV.
    CSV = tabular format widely used for BI/Excel.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _extract_date_keys_from_orders(orders: List[Dict[str, Any]]) -> List[int]:
    keys: List[int] = []
    for o in orders:
        created_at = o["created_at"]
        k = int(datetime.fromisoformat(created_at).strftime("%Y%m%d"))
        keys.append(k)
    return keys


def main() -> None:
    # --- WATERMARK (incremental state) ---
    prev_wm = get_watermark("orders")

    # 1) SOURCE (Bronze): raw payloads (mock for now)
    client = PrestaShopClient(PrestaShopConfig(base_url="https://mock"))
    raw_customers = client.get_customers_mock()
    raw_products = client.get_products_mock()
    raw_orders = client.get_orders_mock()

    # 2) SILVER: normalize + validate
    customers_silver = normalize_customers(raw_customers)
    products_silver = normalize_products(raw_products)
    orders_silver = normalize_orders(raw_orders)
    order_lines_silver = normalize_order_lines(raw_orders)

    # --- INCREMENTAL FILTER (orders) ---
    inc_orders, new_wm = filter_incremental_by_watermark(
        orders_silver,
        watermark_iso=prev_wm,
        watermark_field=WATERMARK_FIELD,
    )

    if not inc_orders:
        print(f"OK: no new orders since watermark={prev_wm}")
        return

    inc_order_ids = {o["prestashop_order_id"] for o in inc_orders}
    inc_order_lines = [
        line
        for line in order_lines_silver
        if line["prestashop_order_id"] in inc_order_ids
    ]

    # 3) GOLD: dims (full snapshot) + facts (incremental)
    dim_customer = build_dim_customer(customers_silver)
    dim_product = build_dim_product(products_silver)

    fact_orders = enrich_orders_with_date(inc_orders)
    fact_order_lines = enrich_order_lines(inc_order_lines, inc_orders)

    # dim_date derived from incremental orders' created_at range
    date_keys = _extract_date_keys_from_orders(inc_orders)
    min_key, max_key = min(date_keys), max(date_keys)

    min_date = date(min_key // 10000, (min_key // 100) % 100, min_key % 100)
    max_date = date(max_key // 10000, (max_key // 100) % 100, max_key % 100)
    dim_date_rows = generate_dim_date(min_date, max_date)

    # 4) SERVING: aggregates (incremental)
    agg_by_product = agg_sales_by_product(fact_order_lines, dim_product)

    # 5) OUTPUTS (layered folders)
    write_csv(GOLD_DIR / "dim_customer.csv", dim_customer)
    write_csv(GOLD_DIR / "dim_product.csv", dim_product)
    write_csv(GOLD_DIR / "dim_date.csv", dim_date_rows)

    write_csv(GOLD_DIR / "fact_orders.csv", fact_orders)
    write_csv(GOLD_DIR / "fact_order_lines.csv", fact_order_lines)

    write_csv(SERVING_DIR / "agg_sales_by_product.csv", agg_by_product)

    # update watermark only after successful output
    if new_wm:
        set_watermark("orders", new_wm)

    print(f"OK: incremental pipeline wrote outputs. watermark {prev_wm} -> {new_wm}")


if __name__ == "__main__":
    main()

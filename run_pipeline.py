from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import csv
from typing import Any, Dict, Iterable, List

from src.phc_analytics.integrations.prestashop.client import PrestaShopClient, PrestaShopConfig
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
    Escreve uma lista de dicts para CSV.

    CSV (Comma-Separated Values): formato tabular simples, compatível com Excel/BI.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        # cria CSV vazio com header mínimo
        path.write_text("")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _extract_date_keys_from_orders(orders: List[Dict[str, Any]]) -> List[int]:
    """
    Extrai as chaves de data (YYYYMMDD) a partir de orders.created_at.
    """
    keys: List[int] = []
    for o in orders:
        created_at = o["created_at"]  # ISO string
        k = int(datetime.fromisoformat(created_at).strftime("%Y%m%d"))
        keys.append(k)
    return keys


def main() -> None:
    # 1) SOURCE (Bronze): obter raw payloads (mock por agora)
    client = PrestaShopClient(PrestaShopConfig(base_url="https://mock"))
    raw_customers = client.get_customers_mock()
    raw_products = client.get_products_mock()
    raw_orders = client.get_orders_mock()

    # 2) SILVER: normalizar + validar (Data Quality / contrato)
    customers_silver = normalize_customers(raw_customers)
    products_silver = normalize_products(raw_products)
    orders_silver = normalize_orders(raw_orders)
    order_lines_silver = normalize_order_lines(raw_orders)

    # 3) GOLD: dims + facts (Star Schema)
    dim_customer = build_dim_customer(customers_silver)
    dim_product = build_dim_product(products_silver)

    fact_orders = enrich_orders_with_date(orders_silver)
    fact_order_lines = enrich_order_lines(order_lines_silver, orders_silver)

    # dim_date: derivada das datas existentes nas orders
    date_keys = _extract_date_keys_from_orders(orders_silver)
    min_key, max_key = min(date_keys), max(date_keys)

    # converter YYYYMMDD -> date
    min_date = date(min_key // 10000, (min_key // 100) % 100, min_key % 100)
    max_date = date(max_key // 10000, (max_key // 100) % 100, max_key % 100)

    dim_date_rows = generate_dim_date(min_date, max_date)

    # 4) SERVING: agregados para consumo
    agg_by_product = agg_sales_by_product(fact_order_lines, dim_product)

    # 5) OUTPUTS
    out_dir = Path("out")
    write_csv(out_dir / "dim_customer.csv", dim_customer)
    write_csv(out_dir / "dim_product.csv", dim_product)
    write_csv(out_dir / "dim_date.csv", dim_date_rows)
    write_csv(out_dir / "fact_orders.csv", fact_orders)
    write_csv(out_dir / "fact_order_lines.csv", fact_order_lines)
    write_csv(out_dir / "agg_sales_by_product.csv", agg_by_product)

    print("OK: pipeline generated CSVs in ./out")


if __name__ == "__main__":
    main()

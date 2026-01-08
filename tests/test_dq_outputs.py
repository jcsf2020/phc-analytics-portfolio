from __future__ import annotations

import csv
from pathlib import Path


OUT = Path("out")


def _read_csv(name: str) -> list[dict[str, str]]:
    path = OUT / name
    assert path.exists(), f"Missing output: {path}"
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_outputs_exist():
    required = [
        "dim_customer.csv",
        "dim_product.csv",
        "dim_date.csv",
        "fact_orders.csv",
        "fact_order_lines.csv",
        "agg_sales_by_product.csv",
    ]
    for f in required:
        assert (OUT / f).exists(), f"Missing {f}"


def test_dim_customer_unique_keys():
    rows = _read_csv("dim_customer.csv")
    keys = [r["customer_key"] for r in rows]
    assert len(keys) == len(set(keys)), "customer_key not unique"
    assert all(k and k.strip() for k in keys), "customer_key has null/empty"


def test_dim_product_unique_keys():
    rows = _read_csv("dim_product.csv")
    keys = [r["product_key"] for r in rows]
    assert len(keys) == len(set(keys)), "product_key not unique"
    assert all(k and k.strip() for k in keys), "product_key has null/empty"


def test_fact_order_lines_fk_integrity():
    fact = _read_csv("fact_order_lines.csv")
    dim_c = _read_csv("dim_customer.csv")
    dim_p = _read_csv("dim_product.csv")
    dim_d = _read_csv("dim_date.csv")

    c_keys = {r["customer_key"] for r in dim_c}
    p_keys = {r["product_key"] for r in dim_p}
    d_keys = {r["date"] for r in dim_d}  # dim_date uses 'date' column (ISO)

    for r in fact:
        assert r["prestashop_customer_id"] in c_keys, "FK customer missing in dim_customer"
        assert r["prestashop_product_id"] in p_keys, "FK product missing in dim_product"

        # order_date_key is YYYYMMDD, map to ISO date in dim_date
        k = r["order_date_key"]
        iso = f"{k[0:4]}-{k[4:6]}-{k[6:8]}"
        assert iso in d_keys, "FK date missing in dim_date"


def test_fact_order_lines_metrics_valid():
    fact = _read_csv("fact_order_lines.csv")
    for r in fact:
        qty = float(r["quantity"])
        line_total = float(r["line_total"])
        assert qty > 0, "quantity must be > 0"
        assert line_total >= 0, "line_total must be >= 0"

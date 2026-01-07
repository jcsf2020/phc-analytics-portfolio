from __future__ import annotations

from typing import List, Dict, Any


def build_dim_product(products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build dim_product (analytics dimension).

    1 row per product.
    product_key = surrogate key (MVP: equals prestashop_product_id)
    """

    dim: List[Dict[str, Any]] = []

    for p in products:
        product_id = p["prestashop_product_id"]

        dim.append(
            {
                "product_key": product_id,
                "prestashop_product_id": product_id,
                "sku": p.get("sku"),
                "name": p.get("name"),
                "active": p.get("active", True),
            }
        )

    return dim

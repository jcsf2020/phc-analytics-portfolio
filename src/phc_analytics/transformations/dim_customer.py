from __future__ import annotations

from typing import List, Dict, Any


def build_dim_customer(customers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build dim_customer (analytics dimension).

    1 row per customer.
    customer_key = surrogate key (MVP: equals prestashop_customer_id)
    """

    dim: List[Dict[str, Any]] = []

    for c in customers:
        customer_id = c["prestashop_customer_id"]

        dim.append(
            {
                "customer_key": customer_id,
                "prestashop_customer_id": customer_id,
                "email": c.get("email"),
                "full_name": f"{c.get('firstname', '')} {c.get('lastname', '')}".strip(),
                "active": c.get("active", True),
            }
        )

    return dim

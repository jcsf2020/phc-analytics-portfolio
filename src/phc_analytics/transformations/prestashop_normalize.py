from __future__ import annotations

from typing import Any, Dict, List


class DataValidationError(Exception):
    """
    Erro levantado quando os dados nao cumprem o Data Contract.
    """
    pass


def normalize_customers(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normaliza Customers vindos do PrestaShop.

    Input esperado (raw):
    {
        "customers": [ {...}, {...} ]
    }

    Output:
    Lista de customers normalizados (1 dict por customer).
    """
    if "customers" not in raw:
        raise DataValidationError("Missing 'customers' key in raw data")

    normalized: List[Dict[str, Any]] = []

    for c in raw["customers"]:
        prestashop_customer_id = c.get("prestashop_customer_id")
        email = c.get("email")

        if prestashop_customer_id is None:
            raise DataValidationError("Customer missing prestashop_customer_id")
        if not email:
            raise DataValidationError("Customer missing email")

        normalized.append(
            {
                "prestashop_customer_id": int(prestashop_customer_id),
                "email": str(email).lower(),
                "firstname": c.get("firstname"),
                "lastname": c.get("lastname"),
                "active": bool(c.get("active", True)),
                "created_at": c.get("created_at"),
                "updated_at": c.get("updated_at"),
            }
        )

    return normalized


def normalize_products(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normaliza Products vindos do PrestaShop.

    Input esperado (raw):
    {
        "products": [ {...}, {...} ]
    }

    Output:
    Lista de produtos normalizados (1 dict por produto).
    """
    if "products" not in raw:
        raise DataValidationError("Missing 'products' key in raw data")

    normalized: List[Dict[str, Any]] = []

    for p in raw["products"]:
        prestashop_product_id = p.get("prestashop_product_id")
        name = p.get("name")

        if prestashop_product_id is None:
            raise DataValidationError("Product missing prestashop_product_id")
        if not name:
            raise DataValidationError("Product missing name")

        normalized.append(
            {
                "prestashop_product_id": int(prestashop_product_id),
                "sku": p.get("sku"),
                "name": str(name),
                "active": bool(p.get("active", True)),
                "price": float(p.get("price")) if p.get("price") is not None else None,
                "currency": p.get("currency"),
                "created_at": p.get("created_at"),
                "updated_at": p.get("updated_at"),
            }
        )

    return normalized

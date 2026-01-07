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


def normalize_orders(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normaliza Order Headers vindos do PrestaShop.

    Input esperado (raw):
    {
        "orders": [ {...}, {...} ]
    }

    Output:
    Lista de orders normalizadas (1 dict por encomenda).
    """
    if "orders" not in raw:
        raise DataValidationError("Missing 'orders' key in raw data")

    normalized: List[Dict[str, Any]] = []

    for o in raw["orders"]:
        prestashop_order_id = o.get("prestashop_order_id")
        prestashop_customer_id = o.get("prestashop_customer_id")
        status = o.get("status")
        created_at = o.get("created_at")

        if prestashop_order_id is None:
            raise DataValidationError("Order missing prestashop_order_id")
        if prestashop_customer_id is None:
            raise DataValidationError("Order missing prestashop_customer_id")
        if not status:
            raise DataValidationError("Order missing status")
        if not created_at:
            raise DataValidationError("Order missing created_at")

        normalized.append(
            {
                "prestashop_order_id": int(prestashop_order_id),
                "prestashop_customer_id": int(prestashop_customer_id),
                "status": str(status),
                "total_paid": float(o.get("total_paid", 0)),
                "currency": o.get("currency"),
                "created_at": created_at,
                "updated_at": o.get("updated_at"),
            }
        )

    return normalized


def normalize_order_lines(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normaliza Order Lines vindas do PrestaShop.

    Input esperado (raw):
    {
        "orders": [
            {
                "prestashop_order_id": ...,
                "lines": [ {...}, {...} ]
            }
        ]
    }

    Output:
    Lista de linhas normalizadas (1 dict por linha).
    """
    if "orders" not in raw:
        raise DataValidationError("Missing 'orders' key in raw data")

    normalized: List[Dict[str, Any]] = []

    for o in raw["orders"]:
        prestashop_order_id = o.get("prestashop_order_id")
        if prestashop_order_id is None:
            raise DataValidationError("Order missing prestashop_order_id (for lines)")

        lines = o.get("lines", [])
        for line in lines:
            prestashop_product_id = line.get("prestashop_product_id")
            quantity = line.get("quantity")

            if prestashop_product_id is None:
                raise DataValidationError("Order line missing prestashop_product_id")
            if quantity is None:
                raise DataValidationError("Order line missing quantity")

            normalized.append(
                {
                    "prestashop_order_id": int(prestashop_order_id),
                    "prestashop_product_id": int(prestashop_product_id),
                    "quantity": float(quantity),
                    "unit_price": float(line.get("unit_price")) if line.get("unit_price") is not None else None,
                    "line_total": float(line.get("line_total")) if line.get("line_total") is not None else None,
                }
            )

    return normalized

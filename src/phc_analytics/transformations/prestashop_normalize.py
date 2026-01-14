from __future__ import annotations

from typing import Any, Dict, List


class DataValidationError(Exception):
    """
    Erro levantado quando os dados nao cumprem o Data Contract.
    """

    pass


def normalize_customers(raw: Any) -> List[Dict[str, Any]]:
    """
    Normaliza Customers vindos do PrestaShop.

    Suporta input real (Opção A):
      - envelope dict: {"customers": [...]}
      - envelope dict: {"customer": {...}} (single)
      - lista direta: [...]
      - dict direto: {...} (single)

    Output (contrato Silver):
      - prestashop_customer_id (int)
      - email (lower)
      - firstname, lastname
      - active (bool)
      - created_at, updated_at

    Nota: Não rebenta o pipeline por problemas de shape; faz skip de registos inválidos.
    """
    if raw is None:
        return []

    # 1) Extrair customers como list[dict]
    customers: List[Dict[str, Any]] = []

    if isinstance(raw, list):
        customers = [c for c in raw if isinstance(c, dict)]

    elif isinstance(raw, dict):
        # Envelope comum
        if "customers" in raw:
            val = raw.get("customers")
        elif "customer" in raw:
            val = raw.get("customer")
        else:
            # Às vezes vem um dict já no formato de customer
            val = raw

        if isinstance(val, list):
            customers = [c for c in val if isinstance(c, dict)]
        elif isinstance(val, dict):
            customers = [val]
        else:
            customers = []

    else:
        return []

    # 2) Normalizar
    normalized: List[Dict[str, Any]] = []

    for c in customers:
        # Resolver id (aceitar aliases)
        cid = c.get("id")
        if cid is None:
            for alias in (
                "prestashop_customer_id",
                "customer_id",
                "id_customer",
                "ps_customer_id",
            ):
                if c.get(alias) is not None:
                    cid = c.get(alias)
                    break

        # Skip se não houver id
        if cid in (None, ""):
            continue

        email = c.get("email")
        # Skip se não houver email
        if not email:
            continue

        normalized.append(
            {
                "prestashop_customer_id": int(cid),
                "email": str(email).lower(),
                "firstname": c.get("firstname"),
                "lastname": c.get("lastname"),
                "active": bool(c.get("active", True)),
                "created_at": c.get("date_add"),
                "updated_at": c.get("date_upd"),
            }
        )

    return normalized


def normalize_products(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normaliza Products vindos do PrestaShop.

    Input esperado:
    {
        "products": [
            {
                "id": ...,
                "reference": ...,
                "name": ...,
                "active": ...,
                "price": ...,
                "date_add": ...,
                "date_upd": ...
            }
        ]
    }
    """
    if "products" not in raw:
        raise DataValidationError("Missing 'products' key in raw data")

    normalized: List[Dict[str, Any]] = []

    for p in raw["products"]:
        if "id" not in p:
            raise DataValidationError("Product missing id")
        if not p.get("name"):
            raise DataValidationError("Product missing name")

        normalized.append(
            {
                "prestashop_product_id": int(p["id"]),
                "sku": p.get("reference"),
                "name": str(p["name"]),
                "active": bool(p.get("active", True)),
                "price": float(p["price"]) if p.get("price") is not None else None,
                "created_at": p.get("date_add"),
                "updated_at": p.get("date_upd"),
            }
        )

    return normalized


def normalize_orders(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normaliza Order headers vindos do PrestaShop.

    Input esperado:
    {
        "orders": [
            {
                "id": ...,
                "id_customer": ...,
                "current_state": ...,
                "total_paid": ...,
                "date_add": ...,
                "date_upd": ...
            }
        ]
    }
    """
    if "orders" not in raw:
        raise DataValidationError("Missing 'orders' key in raw data")

    normalized: List[Dict[str, Any]] = []

    for o in raw["orders"]:
        if "id" not in o:
            raise DataValidationError("Order missing id")
        if "id_customer" not in o:
            raise DataValidationError("Order missing id_customer")
        if "date_add" not in o:
            raise DataValidationError("Order missing date_add")

        normalized.append(
            {
                "prestashop_order_id": int(o["id"]),
                "prestashop_customer_id": int(o["id_customer"]),
                "status": str(o.get("current_state")),
                "total_paid": float(o.get("total_paid", 0)),
                "created_at": o.get("date_add"),
                "updated_at": o.get("date_upd"),
            }
        )

    return normalized


def normalize_order_lines(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Normaliza Order Lines vindas do PrestaShop.

    Input esperado:
    {
        "orders": [
            {
                "id": ...,
                "associations": {
                    "order_rows": [
                        {
                            "product_id": ...,
                            "product_quantity": ...,
                            "unit_price_tax_excl": ...
                        }
                    ]
                }
            }
        ]
    }
    """
    if "orders" not in raw:
        raise DataValidationError("Missing 'orders' key in raw data")

    normalized: List[Dict[str, Any]] = []

    for o in raw["orders"]:
        if "id" not in o:
            raise DataValidationError("Order missing id")

        order_id = int(o["id"])
        rows = o.get("associations", {}).get("order_rows", [])

        for r in rows:
            if "product_id" not in r:
                raise DataValidationError("Order line missing product_id")
            if "product_quantity" not in r:
                raise DataValidationError("Order line missing product_quantity")

            quantity = float(r["product_quantity"])
            unit_price = (
                float(r["unit_price_tax_excl"])
                if r.get("unit_price_tax_excl") is not None
                else None
            )

            normalized.append(
                {
                    "prestashop_order_id": order_id,
                    "prestashop_product_id": int(r["product_id"]),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": quantity * unit_price
                    if unit_price is not None
                    else None,
                }
            )

    return normalized

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from src.phc_analytics.integrations.odoo.client import OdooClient, build_local_client
from src.phc_analytics.integrations.prestashop.client import PrestaShopClient


def _build_prestashop_client() -> PrestaShopClient:
    """
    Cria o client PrestaShop.
    Por defeito usamos o modo mock (sem credenciais).
    Para usar API real, basta exportar PRESTASHOP_BASE_URL e PRESTASHOP_API_KEY
    e trocar use_mock=False no main().
    """
    return PrestaShopClient.from_env()


def _full_name(c: Dict[str, Any]) -> str:
    first = (c.get("firstname") or "").strip()
    last = (c.get("lastname") or "").strip()
    name = (first + " " + last).strip()
    return name or (c.get("email") or "Unknown")


def _ensure_custom_fields_exist_admin_only() -> None:
    """
    Nota importante:
    - Criar campos em ir.model.fields exige permissões de Admin (Access Rights).
    - Já criaste os 3 campos:
        product.template: x_prestashop_product_id
        res.partner:      x_prestashop_customer_id
        sale.order:       x_prestashop_order_id
    Aqui NÃO tentamos criar campos automaticamente para não depender de Admin.
    """
    return


def upsert_customers(
    odoo: OdooClient, customers: List[Dict[str, Any]]
) -> Dict[str, int]:
    created = 0
    updated = 0

    for c in customers:
        ps_id = int(c["prestashop_customer_id"])
        email = (c.get("email") or "").strip().lower()
        name = _full_name(c)

        # 1) procurar por x_prestashop_customer_id (chave forte)
        existing = odoo.search_read(
            "res.partner",
            domain=[("x_prestashop_customer_id", "=", ps_id)],
            fields=["id", "name", "email", "x_prestashop_customer_id"],
            limit=1,
        )

        if existing:
            pid = existing[0]["id"]
            odoo.write("res.partner", [pid], {"name": name, "email": email})
            updated += 1
            continue

        # 2) fallback: procurar por email (se existir)
        if email:
            existing2 = odoo.search_read(
                "res.partner",
                domain=[("email", "=", email)],
                fields=["id", "name", "email"],
                limit=1,
            )
            if existing2:
                pid = existing2[0]["id"]
                odoo.write(
                    "res.partner",
                    [pid],
                    {"name": name, "email": email, "x_prestashop_customer_id": ps_id},
                )
                updated += 1
                continue

        # 3) criar novo
        pid = odoo.create("res.partner", {"name": name, "email": email})
        odoo.write("res.partner", [pid], {"x_prestashop_customer_id": ps_id})
        created += 1

    return {"created": created, "updated": updated}


def upsert_products(odoo: OdooClient, products: List[Dict[str, Any]]) -> Dict[str, int]:
    created = 0
    updated = 0

    for p in products:
        ps_id = int(p["prestashop_product_id"])
        sku = (p.get("sku") or "").strip()
        name = (p.get("name") or "").strip() or f"Product {ps_id}"
        price = float(p.get("price") or 0.0)

        # 1) procurar por x_prestashop_product_id
        existing = odoo.search_read(
            "product.template",
            domain=[("x_prestashop_product_id", "=", ps_id)],
            fields=["id", "name", "default_code", "x_prestashop_product_id"],
            limit=1,
        )

        vals = {"name": name, "default_code": sku, "list_price": price}

        if existing:
            pid = existing[0]["id"]
            odoo.write("product.template", [pid], vals)
            updated += 1
            continue

        # 2) fallback: procurar por SKU (default_code)
        if sku:
            existing2 = odoo.search_read(
                "product.template",
                domain=[("default_code", "=", sku)],
                fields=["id", "name", "default_code"],
                limit=1,
            )
            if existing2:
                pid = existing2[0]["id"]
                odoo.write(
                    "product.template",
                    [pid],
                    {**vals, "x_prestashop_product_id": ps_id},
                )
                updated += 1
                continue

        # 3) criar novo
        pid = odoo.create("product.template", vals)
        odoo.write("product.template", [pid], {"x_prestashop_product_id": ps_id})
        created += 1

    return {"created": created, "updated": updated}


def _get_product_variant_id_by_ps_product_id(
    odoo: OdooClient, ps_product_id: int
) -> int:
    """
    Odoo: sale.order.line espera product_id (product.product), não product.template.
    Estratégia:
      - encontrar product.template via x_prestashop_product_id
      - ir buscar o seu product_variant_id (campo many2one -> product.product)
    """
    rows = odoo.search_read(
        "product.template",
        domain=[("x_prestashop_product_id", "=", int(ps_product_id))],
        fields=["id", "name", "product_variant_id"],
        limit=1,
    )
    if not rows:
        raise RuntimeError(
            f"Product not found in Odoo for prestashop_product_id={ps_product_id}"
        )

    pv = rows[0].get("product_variant_id")
    if not pv or not isinstance(pv, list) or not pv[0]:
        raise RuntimeError(
            f"Missing product_variant_id for product.template id={rows[0]['id']}"
        )
    return int(pv[0])


def _find_partner_id_by_ps_customer_id(odoo: OdooClient, ps_customer_id: int) -> int:
    rows = odoo.search_read(
        "res.partner",
        domain=[("x_prestashop_customer_id", "=", int(ps_customer_id))],
        fields=["id", "name", "x_prestashop_customer_id"],
        limit=1,
    )
    if not rows:
        raise RuntimeError(
            f"Customer not found in Odoo for prestashop_customer_id={ps_customer_id}"
        )
    return int(rows[0]["id"])


def _replace_order_lines_idempotent(
    odoo: OdooClient,
    so_id: int,
    payload_lines: List[Dict[str, Any]],
) -> Tuple[int, int]:
    """
    Idempotência:
      - apaga TODAS as linhas atuais da encomenda
      - recria a partir do payload

    Retorna (deleted_count, created_count).
    """
    so = odoo.search_read(
        "sale.order",
        domain=[("id", "=", so_id)],
        fields=["id", "name", "order_line"],
        limit=1,
    )[0]
    existing_line_ids = so.get("order_line") or []
    deleted = len(existing_line_ids)

    if existing_line_ids:
        odoo.execute_kw("sale.order.line", "unlink", [existing_line_ids])

    created = 0
    for ln in payload_lines:
        ps_prod_id = int(ln["prestashop_product_id"])
        qty = float(ln["quantity"])
        unit_price = float(ln["unit_price"])
        product_id = _get_product_variant_id_by_ps_product_id(odoo, ps_prod_id)

        odoo.create(
            "sale.order.line",
            {
                "order_id": so_id,
                "product_id": product_id,
                "product_uom_qty": qty,
                "price_unit": unit_price,
            },
        )
        created += 1

    return deleted, created


def upsert_orders(odoo: OdooClient, orders: List[Dict[str, Any]]) -> Dict[str, int]:
    created = 0
    updated = 0
    lines_deleted = 0
    lines_created = 0

    for o in orders:
        ps_order_id = int(o["prestashop_order_id"])
        ps_customer_id = int(o["prestashop_customer_id"])
        payload_lines = o.get("lines") or []

        partner_id = _find_partner_id_by_ps_customer_id(odoo, ps_customer_id)

        existing = odoo.search_read(
            "sale.order",
            domain=[("x_prestashop_order_id", "=", ps_order_id)],
            fields=["id", "name", "x_prestashop_order_id"],
            limit=1,
        )

        if existing:
            so_id = existing[0]["id"]
            updated += 1
        else:
            so_id = odoo.create("sale.order", {"partner_id": partner_id})
            odoo.write("sale.order", [so_id], {"x_prestashop_order_id": ps_order_id})
            created += 1

        d, c = _replace_order_lines_idempotent(odoo, int(so_id), payload_lines)
        lines_deleted += d
        lines_created += c

    return {
        "orders_created": created,
        "orders_updated": updated,
        "lines_deleted": lines_deleted,
        "lines_created": lines_created,
    }


def run(use_mock: bool = True) -> Dict[str, Any]:
    _ensure_custom_fields_exist_admin_only()

    odoo = build_local_client()

    prestashop = _build_prestashop_client()

    if use_mock:
        raw_customers = prestashop.get_customers_mock()
        raw_products = prestashop.get_products_mock()
        raw_orders = prestashop.get_orders_mock()
    else:
        raw_customers = prestashop.get_customers()
        raw_products = prestashop.get_products()
        raw_orders = prestashop.get_orders()

    customers = (
        raw_customers.get("customers", []) if isinstance(raw_customers, dict) else []
    )
    products = (
        raw_products.get("products", []) if isinstance(raw_products, dict) else []
    )
    orders = raw_orders.get("orders", []) if isinstance(raw_orders, dict) else []

    r1 = upsert_customers(odoo, customers)
    r2 = upsert_products(odoo, products)
    r3 = upsert_orders(odoo, orders)

    return {"customers": r1, "products": r2, "orders": r3}


if __name__ == "__main__":
    out = run(use_mock=True)
    print("PIPELINE RESULT:", out)

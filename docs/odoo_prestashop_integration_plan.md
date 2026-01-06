# Odoo <-> PrestaShop Integration (Plan)

## Goal
Integrate **orders, customers, products** between **PrestaShop** and **Odoo**, starting locally with **Odoo via Docker**.

## Key decision (align with Jose)
We will build an **Odoo module** (custom addon) that:
- exposes an API endpoint (or scheduled job) to **pull** from PrestaShop API, OR
- receives webhook pushes from PrestaShop (optional later).

This matches “create a module that does that integration”.

## Phases
### Phase 1 — Odoo local (Docker)
- Run Odoo + Postgres locally
- Validate we can create/read: customers, products, orders
- Document Odoo models we will touch:
  - res.partner (customers)
  - product.template / product.product (products)
  - sale.order (orders) and sale.order.line

### Phase 2 — PrestaShop API connectivity (mock or real)
- Define required PrestaShop API credentials (key, base URL)
- Implement minimal client:
  - fetch customers
  - fetch products
  - fetch orders

### Phase 3 — Odoo addon (module)
- Create addon skeleton
- Add config screen for PrestaShop credentials
- Implement sync job:
  - upsert partners/products/orders
- Logging + idempotency:
  - store external IDs (prestashop_id) on Odoo side
  - avoid duplicates

### Phase 4 — Tests + “data as product”
- Add contract tests for:
  - schema/fields we map
  - idempotency (2 runs = no duplicates)
  - minimal acceptance checks (counts, required fields)

## Data mapping (minimum)
- Customer:
  - prestashop_customer_id -> x_prestashop_id
  - name/email/phone/address -> res.partner fields
- Product:
  - prestashop_product_id -> x_prestashop_id
  - name, sku/reference, price, active
- Order:
  - prestashop_order_id -> x_prestashop_id
  - customer link, lines, totals, date

## Deliverables
- docker-compose.yml to run Odoo local
- addon module in repo (src/odoo_addons/...)
- docs with mapping + run instructions

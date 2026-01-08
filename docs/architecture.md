# Architecture (PHC_Analytics)

## Goal
Build a reproducible analytics pipeline from operational sources to an analytics-ready star schema (dims/facts), with clear data contracts and quality checks.

## Data Flow (end-to-end)
Source -> Staging -> Normalize (Silver) -> Model (Gold) -> Aggregates -> Outputs/BI

### Current MVP Source
- PrestaShop (mock client)
- Odoo (Docker) reserved for future module sync + persistence

## Layers (engineering view)

### 1) Source (Bronze)
**Definition:** raw extraction as-is (API/DB), minimal assumptions.
- `src/phc_analytics/integrations/prestashop/client.py`
  - `get_*_mock()` simulates realistic API payloads (customers/products/orders)

**Output examples (conceptual):**
- raw customers payload
- raw products payload
- raw orders payload (header + lines)

### 2) Normalize (Silver)
**Definition:** validate + standardize types/fields + enforce data contract.
- `src/phc_analytics/transformations/prestashop_normalize.py`
  - `normalize_customers()`
  - `normalize_products()`
  - `normalize_orders()`
  - `normalize_order_lines()`

**Key checks (Data Quality - DQ):**
- REQUIRED fields not null (e.g., `prestashop_*_id`, `email`, `name`, `created_at`)
- type casting (int/float/bool)
- canonicalization (e.g., `email` lowercased)

### 3) Model (Gold) — Star Schema (Kimball)
**Definition:** analytics-friendly tables: dimensions (context) + facts (events).

#### Dimensions
- `dim_date`
  - `src/phc_analytics/transformations/dim_date.py`
  - grain: 1 row per day
  - `date_key` = YYYYMMDD (surrogate key style)

- `dim_customer`
  - `src/phc_analytics/transformations/dim_customer.py`
  - grain: 1 row per customer
  - `customer_key` (MVP: equals `prestashop_customer_id`)

- `dim_product`
  - `src/phc_analytics/transformations/dim_product.py`
  - grain: 1 row per product
  - `product_key` (MVP: equals `prestashop_product_id`)

#### Facts
- `fact_orders` (order header)
  - `src/phc_analytics/transformations/fact_orders_enrich.py`
  - adds `order_date_key` from `created_at`

- `fact_order_lines` (order line items)
  - `src/phc_analytics/transformations/fact_order_lines_enrich.py`
  - grain: 1 row per (order_id, product_id)
  - includes foreign keys:
    - `prestashop_customer_id` (links to dim_customer)
    - `prestashop_product_id` (links to dim_product)
    - `order_date_key` (links to dim_date)

### 4) Aggregates / Serving
**Definition:** precomputed metrics for dashboards/BI.
- `src/phc_analytics/transformations/agg_sales_by_product.py`
  - metrics:
    - `units_sold = sum(quantity)`
    - `revenue = sum(line_total)`

## Keys and terminology (must-know)
- **PK (Primary Key):** unique row identifier inside a table.
- **FK (Foreign Key):** reference from fact -> dimension.
- **Surrogate key:** technical key used in analytics (often integer), independent from business ids.
- **Grain:** what a single row represents (critical to avoid wrong joins).

## What is done vs next
### Done (MVP)
- Mock extraction (PrestaShop)
- Normalization with validations (Silver)
- Star schema dims/facts (Gold)
- One aggregate example (sales by product)
- Odoo running in Docker (foundation for future sync)

### Next (production-minded)
- Runner: one command to generate outputs to `out/` (CSV/JSON)
- Automated DQ tests (pytest) for contract + referential integrity
- Incremental loads (watermark on `updated_at`)
- Real API calls (PrestaShop demo/credentials) + Odoo module persistence


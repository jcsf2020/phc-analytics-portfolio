# PrestaShop → PHC Analytics (Mapping v0)

## Regra-base (Data Engineer mindset)
- A API é “fonte”; não controlamos nomes/formatos.
- O pipeline usa nomes canónicos (data contract).
- Fazemos **mapping/renomeação** na camada `transformations/` (normalize), não “forçamos” a API.

---

## 1) Customers

### Fonte (API)
- Resource: `/api/customers`
- Campos observados:
  - `id`
  - `email`
  - `firstname`
  - `lastname`
  - `active`
  - `date_add`
  - `date_upd`

### Canónico (pipeline)
| canonical | prestashop |
|---|---|
| prestashop_customer_id | id |
| email | email |
| firstname | firstname |
| lastname | lastname |
| active | active |
| created_at | date_add |
| updated_at | date_upd |

---

## 2) Products

### Fonte (API)
- Resource: `/api/products`
- Campos observados:
  - `id`
  - `reference`
  - `name`
  - `active`
  - `price`
  - `date_add`
  - `date_upd`

### Canónico (pipeline)
| canonical | prestashop |
|---|---|
| prestashop_product_id | id |
| sku | reference |
| name | name |
| active | active |
| price | price |
| created_at | date_add |
| updated_at | date_upd |

---

## 3) Orders (headers)

### Fonte (API)
- Resource: `/api/orders`
- Campos observados:
  - `id`
  - `id_customer`
  - `current_state`
  - `total_paid`
  - `date_add`
  - `date_upd`

### Canónico (pipeline)
| canonical | prestashop |
|---|---|
| prestashop_order_id | id |
| prestashop_customer_id | id_customer |
| status | current_state |
| total_paid | total_paid |
| created_at | date_add |
| updated_at | date_upd |

Notas:
- `id_customer` vem como tag com atributo `xlink:href` + CDATA com o número.
- `current_state` idem (valor numérico do estado).

---

## 4) Order Lines

### Fonte (API)
- Dentro de `/api/orders?display=full` em `<associations><order_rows>...`
- Campos observados:
  - `product_id`
  - `product_quantity`
  - `unit_price_tax_excl` (ou `product_price`)

### Canónico (pipeline)
| canonical | prestashop |
|---|---|
| prestashop_order_id | order.id |
| prestashop_product_id | order_row.product_id |
| quantity | order_row.product_quantity |
| unit_price | order_row.unit_price_tax_excl (fallback: product_price) |
| line_total | quantity * unit_price |

---

## 5) Pontos em aberto
- Qual é o “master”: Odoo manda e PrestaShop segue, ou vice-versa?
- Precisamos de sync 1-way (ingestão) ou 2-way (criação/atualização)?
- Confirmar mapeamento de `current_state` → label (se for preciso “texto” e não só ID).
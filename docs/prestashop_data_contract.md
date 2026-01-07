# PrestaShop -> Odoo Data Contract (MVP)

## 0. Objetivo
Definir o contrato de dados (entidades, campos, tipos e regras) para sincronizar:
- Customers (Clientes)
- Products (Produtos)
- Orders (Encomendas)

Este documento e' usado para:
- Implementar a integracao (Odoo module + PrestaShop client)
- Garantir consistencia dos dados e evitar "assumptions"
- Preparar futura modelacao analitica (fact/dim)

## 1. Sistemas e papeis
- Source (fonte): PrestaShop (Backoffice/API)
- Target (destino): Odoo (DB + modelos Odoo)
- Master data (sistema "dono"):
  - Customers: PrestaShop
  - Products: PrestaShop
  - Orders: PrestaShop
  - (Odoo pode enriquecer com campos internos, mas nao altera a origem)

## 2. Identificadores (IDs) e chaves
- PrestaShop usa IDs numericos (inteiros) por entidade.
- Regra: manter o ID PrestaShop como "external_id" no Odoo.
- Chave tecnica no Odoo: id (PK - Primary Key)
- Chave externa: prestashop_id (UNIQUE por entidade)

## 3. Entidades

### 3.1 Customers (Clientes)
Grain (granularidade): 1 linha por customer (cliente) no PrestaShop.

Campos minimos (MVP):
- prestashop_customer_id (int) [REQUIRED]
- email (string) [REQUIRED]
- firstname (string)
- lastname (string)
- active (bool)
- created_at (datetime)
- updated_at (datetime)

Regras:
- Dedupe (deduplicacao): email (case-insensitive)
- PII (Personally Identifiable Information - dados pessoais): email, firstname, lastname
  - Nao logar valores em claro
  - Nao expor em dashboards analiticos sem necessidade

Mapeamento para Odoo (alto nivel):
- res_partner:
  - name = firstname + " " + lastname (fallback: email)
  - email = email
  - active = active
  - is_company = false (default no MVP)
- Campo custom: prestashop_customer_id

### 3.2 Products (Produtos)
Grain: 1 linha por product (produto) no PrestaShop.

Campos minimos (MVP):
- prestashop_product_id (int) [REQUIRED]
- sku / reference (string) [RECOMMENDED]
- name (string) [REQUIRED]
- active (bool)
- price (numeric)
- currency (string) (se aplicavel)
- created_at (datetime)
- updated_at (datetime)

Regras:
- sku/reference deve ser tratado como identificador de negocio quando existir
- price: guardar como numeric com precisao definida (ex: 2 casas decimais)

Mapeamento para Odoo (alto nivel):
- product_template / product_product (dependendo do setup):
  - name = name
  - default_code = sku/reference
  - list_price = price
  - active = active
- Campo custom: prestashop_product_id

### 3.3 Orders (Encomendas)
Grain:
- Order header: 1 linha por order
- Order lines: 1 linha por order_line (produto na encomenda)

Campos minimos (Order header):
- prestashop_order_id (int) [REQUIRED]
- prestashop_customer_id (int) [REQUIRED]
- status (string) [REQUIRED]
- total_paid (numeric)
- currency (string) (se aplicavel)
- created_at (datetime) [REQUIRED]
- updated_at (datetime)

Campos minimos (Order lines):
- prestashop_order_id (int) [REQUIRED]
- prestashop_product_id (int) [REQUIRED]
- quantity (numeric/int) [REQUIRED]
- unit_price (numeric)
- line_total (numeric)

Regras:
- Integridade referencial:
  - order.customer_id tem de existir em Customers (ou criar "placeholder" e reconciliar depois)
  - order_line.product_id tem de existir em Products (ou placeholder e reconciliar depois)

Mapeamento para Odoo (alto nivel):
- sale_order / sale_order_line (quando o modulo sale estiver instalado):
  - partner_id = res_partner (via prestashop_customer_id)
  - order_line: product_id (via prestashop_product_id)
- Campo custom: prestashop_order_id

## 4. Qualidade de dados (Data Quality)
Testes minimos (MVP):
- Customers:
  - prestashop_customer_id not null, unique
  - email not null
- Products:
  - prestashop_product_id not null, unique
  - name not null
- Orders:
  - prestashop_order_id not null, unique
  - created_at not null
  - order lines: quantity > 0

## 5. Incremental (cargas incrementais)
Incremental = carregar apenas alteracoes desde a ultima execucao.
Estrategia MVP:
- usar updated_at quando existir
- fallback: created_at + reconciliacao manual

## 6. Notas e proximos passos
- Confirmar campos reais via API PrestaShop (quando credenciais existirem)
- Confirmar onde armazenar prestashop_*_id no Odoo (campos custom vs tabela mapping)
- Validar instalacao dos modulos Odoo (product, sale) para criar orders/lines

# PHC Analytics — PrestaShop → Odoo Sync & Analytics Pipeline

## Contexto
Pipeline end-to-end que sincroniza dados operacionais de e-commerce (PrestaShop)
para ERP (Odoo) de forma idempotente e produz datasets analíticos prontos para analytics/BI.

---

## Sync PrestaShop → Odoo (mock)

Executa a sincronizacao operacional (clientes, produtos e encomendas):

```bash
python -m src.phc_analytics.pipelines.prestashop_to_odoo
```

O que faz:
- Upsert idempotente em Odoo
- Cria chaves tecnicas x_prestashop_*_id
- Re-executavel sem duplicar dados

---

## Gerar Analytics

Gera os datasets analiticos (facts e dimensions):

```bash
python run_pipeline.py
```

---

## Outputs

Os ficheiros CSV sao gerados em:

```
./out/
```

### Facts
- fact_orders.csv
- fact_order_lines.csv

### Dimensions
- dim_customer.csv
- dim_product.csv
- dim_date.csv

### Aggregations
- agg_sales_by_product.csv

---

## Estrutura do Projeto

```
src/phc_analytics/
├─ integrations/
│  ├─ prestashop/
│  └─ odoo/
├─ pipelines/
│  └─ prestashop_to_odoo.py
├─ transformations/
├─ quality/
tests/
out/
docker-compose.odoo.yml
run_pipeline.py
```

---

## Testes

Executar todos os testes de qualidade e integracao:

```bash
pytest -q
```

Estado atual: todos verdes.

---

## Proximos Passos
- Ligar API real do PrestaShop
- Incremental loads (watermarks)
- Estados de encomenda (paid, shipped, refunded)
- Load para Data Warehouse (Snowflake / BigQuery / Postgres)

---

## Autor
Joao Fonseca
Data Engineering · Analytics Engineering · Integracoes ERP

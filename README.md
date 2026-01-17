# PHC Analytics — Pipeline de Dados Raw → Analytics

## Contexto
Pipeline de dados end-to-end que extrai dados operacionais do PrestaShop, armazena em PostgreSQL e transforma em datasets analíticos via materialized views, garantindo performance e escalabilidade para análises e BI.

---

## Arquitetura

- **Raw Layer:** Dados extraídos do PrestaShop armazenados em tabelas brutas no PostgreSQL.
- **Analytics Layer:** Transformações implementadas como materialized views otimizadas para consultas analíticas.
- **Sincronização:** Processos idempotentes que garantem integridade e atualização incremental dos dados.

---

## Stack Técnica

- Python para extração e orquestração
- PostgreSQL como data warehouse e engine analítica
- Materialized views para performance em consultas analíticas
- Docker para ambiente local consistente

---

## Como Correr Localmente

1. Levantar o ambiente PostgreSQL via Docker Compose:

```bash
docker-compose -f docker-compose.odoo.yml up -d db
```

2. Executar a pipeline de sincronização e transformação:

```bash
python run_pipeline.py
```

3. Consultar as views materializadas diretamente no PostgreSQL para análise.

---

## O Que Demonstra ao Mercado

- Implementação real de pipeline ELT moderno com foco em dados analíticos
- Uso eficiente de PostgreSQL para armazenar e transformar dados
- Práticas de engenharia de dados como idempotência e incrementalidade
- Preparação para escalabilidade e integração com BI

---

## Estado do Projeto (Sprint Fechado)

- Pipeline de extração e carga raw implementado
- Materialized views analíticas criadas e otimizadas
- Ambiente local com Docker configurado e funcional
- Testes de qualidade e integração completos e aprovados

---

## Próximos Passos (Fora do Sprint)

- Integração com API real do PrestaShop para dados em tempo real
- Implementação de cargas incrementais com watermarks
- Enriquecimento com estados de encomenda (paid, shipped, refunded)
- Exportação e integração com Data Warehouse externo (Snowflake, BigQuery)

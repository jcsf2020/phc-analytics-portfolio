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

# PHC Analytics — Production‑Ready Analytics Engineering Project

## Executive Summary
PHC Analytics is a **hands‑on, production‑oriented Data Engineering / Analytics Engineering project** designed to demonstrate how modern analytics systems are **designed, bootstrapped, operated, and validated** in real environments.

This is **not a tutorial project**.
It focuses on:
- real architectural decisions
- operational correctness
- reproducibility
- performance validation
- clear separation of concerns

The repository is intentionally structured to be **readable and assessable by recruiters, hiring managers, and senior data engineers**.

---

## Problem Statement
Operational systems (OLTP) are not designed for analytics.

This project demonstrates how to:
- ingest operational data safely
- preserve source truth
- transform data into analytics‑ready structures
- serve analytical workloads efficiently
- validate performance and correctness

All decisions are explicit and defensible from a production perspective.

---

## High‑Level Architecture

```
PrestaShop (OLTP)
        ↓
PostgreSQL — Raw Layer (JSONB)
        ↓
PostgreSQL — Analytics Layer
        ↓
Materialized Views (BI / Analytics consumption)
```

---

## Layered Design

### 1. Source / OLTP Layer
Operational data originating from **PrestaShop** (customers, orders).

Characteristics:
- mutable data
- business‑driven schemas
- not optimized for analytics

---

### 2. Raw Layer (PostgreSQL)
Raw ingestion layer storing source payloads as JSONB.

Key properties:
- schema‑agnostic ingestion
- idempotent upserts
- replayable pipelines
- no business logic

Purpose:
> Preserve source truth and decouple ingestion from analytics.

---

### 3. Analytics Layer (PostgreSQL)
Analytics‑oriented relational structures built explicitly for analytical workloads.

Includes:
- analytical tables
- derived metrics
- dimensional‑style structures
- analytical views
- **materialized views**

Purpose:
> Serve fast, predictable, and scalable analytical queries.

---

## Bootstrap & Reproducibility

### SQL‑First Analytics Bootstrap
The entire analytics system can be created from scratch using **versioned SQL migrations**.

Main migration:
```
sql/migrations/001_init_analytics.sql
```

This migration:
- creates schemas (`raw`, `analytics`)
- defines analytics tables
- creates analytical views
- creates materialized views
- applies performance indexes
- prepares refresh logging

This mirrors **real production database lifecycle management**.

---

## Materialized Views Strategy

### Why Materialized Views
- expensive joins pre‑computed
- predictable query latency
- BI‑friendly access patterns
- isolation from OLTP workloads

### Performance Validation
Queries are validated using:
- `EXPLAIN ANALYZE`
- buffer usage inspection
- index usage confirmation

Example:
- top‑N queries ordered by ingestion time
- index‑backed access paths
- sub‑millisecond execution times at 10k+ rows

---

## Refresh Control & Observability

Materialized views are refreshed explicitly and logged.

Features:
- controlled refresh execution
- optional concurrent refresh
- refresh timestamp logging
- operational visibility

This reflects how analytics systems are operated in production, not ad‑hoc querying.

---

## Data Volume Simulation
To validate performance characteristics, the project simulates:
- 10,000+ orders
- repeated refresh cycles
- index efficiency under load

This ensures decisions scale beyond toy datasets.

---

## Technology Stack

- **PostgreSQL** — analytical engine
- **SQL** — transformations and modeling
- **JSONB** — raw data preservation
- **Materialized Views** — analytics acceleration
- **Docker Compose** — reproducible local environment

The stack is intentionally **simple, explicit, and production‑realistic**.

---

## What This Project Demonstrates to the Market

### Core Data Engineering Skills
- OLTP vs Analytics separation
- idempotent ingestion patterns
- reproducible schema management
- analytical modeling
- performance tuning
- refresh orchestration

### Analytics Engineering Practices
- analytics‑first schema design
- materialized view strategy
- BI‑ready datasets
- predictable query performance

### Production Mindset
- no hidden magic
- explicit decisions
- observable behavior
- controlled execution paths

---

## Current Status
**Sprint 3 — Production‑Ready Analytics Layer: COMPLETED**

- Raw ingestion tables implemented
- Analytics tables defined
- Analytical views created
- Materialized views operational
- Indexing applied and validated
- Refresh logic implemented and logged
- Performance validated with real volume

---

## Next Planned Evolutions (Out of Sprint)
- Cloud deployment (Azure / Snowflake / BigQuery)
- dbt‑based transformations
- Orchestration (Prefect / Airflow)
- Incremental models with watermarks
- Data quality checks
- BI integration

These steps align the project with **enterprise‑grade analytics platforms**.

---

## Target Roles
This project is intentionally aligned with:
- Data Engineer
- Analytics Engineer
- Senior Analytics Engineer
- Modern BI / Analytics Platform roles
- Remote / Hybrid Data Engineering positions

---

## Final Note
PHC Analytics reflects **how data systems are actually built and operated**, not how they are presented in tutorials.

Clean, explicit, reproducible, and defensible.

That is the point of this project.
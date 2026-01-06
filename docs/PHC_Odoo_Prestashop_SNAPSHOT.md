# PHC Analytics — Odoo ↔ PrestaShop
## Snapshot de Entrega (MVP + Estado do Projeto)

**Data:** 2026-01-06
**Contexto:** Projeto PHC Analytics — MVP técnico e base de integração
**Estado:** Snapshot técnico para referência e retoma futura

---

## 1. Objetivo do Snapshot

Este documento regista **o estado exato do projeto no momento da entrega**, com o objetivo de:

- Criar um ponto de referência técnico
- Permitir retoma futura sem perda de contexto
- Servir como evidência de trabalho para portfólio técnico (Data Engineering)

---

## 2. Objetivo do Trabalho

- Criar um **ambiente Odoo local via Docker**
- Preparar base técnica para **integração Odoo ↔ PrestaShop**
- Trabalhar com **dados controlados / mock**
- Estrutura preparada para integração via **módulo Odoo**
- Sem dependência de bases de dados externas reais

---

## 3. Entregável Técnico

### 3.1 Ambiente Local (funcional)

- **Odoo 17**
- **PostgreSQL 15**
- Orquestração via **Docker Compose**

Serviços expostos:
- Odoo → `http://localhost:8069`
- PostgreSQL → `localhost:5432`

Validação:
```bash
docker compose ps
curl -I http://localhost:8069
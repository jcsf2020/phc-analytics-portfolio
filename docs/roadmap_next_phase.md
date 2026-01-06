# Roadmap Técnico — Próxima Fase (PHC Analytics)

## Objetivo do Documento
Definir de forma clara e técnica o estado atual do projeto PHC Analytics e o plano de evolução para a próxima fase, garantindo:
- Continuidade técnica
- Boas práticas de Data Engineering
- Reprodutibilidade
- Clareza para qualquer stakeholder técnico

Este documento funciona como:
- Mini RFC (Request for Comments)
- Referência de execução
- Base para validação futura do trabalho desenvolvido

---

## Fase 1 — Estado Atual (Concluído)

### 1.1 Pipeline de Dados
- Pipeline implementada em **Python (pandas)**
- Ingestão de dados mock (documentos PHC)
- Transformação para **Star Schema**:
  - FACT: `fact_documents`
  - DIMs: `dim_clients`, `dim_time`

### 1.2 Persistência
- Escrita em **Parquet**
- FACT particionada por `year_month`
- DIMs não particionadas (datasets pequenos)
- Estrutura compatível com Data Lake

### 1.3 Data Contract
- Inputs definidos (schema esperado)
- Outputs definidos (datasets gerados)
- Garantias explícitas:
  - colunas obrigatórias
  - tipos
  - partições
- Documento versionado em `docs/data_contract.md`

### 1.4 Quality Gates
- Validações automáticas sobre o FACT:
  - colunas obrigatórias
  - valores nulos críticos
  - consistência temporal
- Pipeline falha cedo se o contrato for violado

### 1.5 Testes Automáticos
- Testes com **pytest**
- Validação do contrato da pipeline:
  - escrita particionada
  - leitura com filtros (`partition pruning`)
  - integridade dos dados lidos
- Testes verdes localmente

### 1.6 Estado do Repositório
- Código organizado em `src/`
- Outputs ignorados via `.gitignore`
- Repositório limpo, versionado e reproduzível

**Estado da Fase 1: CONCLUÍDA E ESTÁVEL**

---

## Fase 2 — Novo Objetivo (Em Planeamento)

### 2.1 Objetivo Geral
Evoluir o projeto de um pipeline analítico isolado para um **cenário mais realista**, com:
- Sistema transacional (ERP)
- Integração via API
- Dados próximos de produção

---

### 2.2 Sistema Fonte — Odoo

- Instalação local do **Odoo via Docker**
- Utilização de dados controlados:
  - clientes
  - produtos
  - encomendas
- Odoo como **sistema transacional (source of truth)**

Objetivo:
- Simular um ambiente real de ERP
- Evitar dependência imediata de bases externas

---

### 2.3 Integração de Sistemas

- Integração entre Odoo e sistema externo (ex: PrestaShop)
- Comunicação via **API**
- Abordagem recomendada:
  - criação de **módulo no Odoo** responsável pela integração
  - extração dos dados relevantes para analytics

Dados-alvo:
- Encomendas
- Clientes
- Produtos

---

### 2.4 Evolução da Pipeline Analítica

- Substituir (ou complementar) dados mock por dados vindos do Odoo
- Manter:
  - Star Schema
  - Data Contract
  - Quality Gates
  - Testes automáticos
- Garantir que a pipeline continua reprodutível e validada

---

### 2.5 Valor Técnico da Fase 2
Esta fase permite demonstrar:
- Integração de sistemas reais
- Noções de ERP + API
- Engenharia de dados end-to-end
- Pensamento orientado a produção

---

## Próximos Passos (Execução)

1. Criar ambiente Docker com Odoo local
2. Explorar modelo de dados do Odoo (clientes, produtos, encomendas)
3. Definir contrato mínimo de extração
4. Criar módulo simples de integração
5. Ligar a pipeline analítica existente
6. Atualizar testes e quality gates

---

## Nota Final
Este roadmap foi desenhado para:
- Evoluir tecnicamente o projeto
- Reforçar o portfólio de Data Engineering
- Demonstrar maturidade profissional e boas práticas

Qualquer alteração futura deve ser feita de forma incremental e versionada.
# PHC Analytics — Data Engineering Analytics MVP

Projeto de Data Engineering + Analytics desenvolvido como MVP técnico, focado em pipeline de dados, cálculo de KPIs e camada analítica final, simulando um cenário real de dados empresariais (PHC ERP).

## Objetivo
Transformar dados operacionais em informação estratégica, com arquitetura preparada para ligação à BD PHC quando o schema real estiver disponível.

## Arquitetura
- data/                 # Fonte de dados mock
- src/phc_analytics/
  - staging/            # Ingestão e normalização
  - analytics/          # KPIs e séries temporais
- app.py                # Camada de apresentação (Streamlit)

## KPIs
- Vendas totais
- Número de documentos
- Número de clientes
- Ticket médio
- Faturação mensal
- Crescimento mês-a-mês
- Top clientes
- Vendas por tipo de documento

## Stack
Python, Pandas, Streamlit, uv  
Preparado para PostgreSQL, SQLAlchemy e orquestração.

## Execução
uv run streamlit run app.py

## Autor
João Fonseca — Data / Big Data Engineer

## Decisões Técnicas

- Separação entre ingestão, analytics e apresentação para facilitar manutenção e evolução.
- KPIs isolados em funções reutilizáveis para permitir cálculo via pandas ou SQL.
- Estrutura preparada para escalar de dados mock para base de dados real sem refatoração.

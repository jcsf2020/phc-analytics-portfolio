# PHC Analytics Portfolio
## Contexto do Projeto

Este projeto simula um cenário real de analytics empresarial baseado num ERP (PHC),
com o objetivo de transformar dados operacionais de vendas em informação analítica
útil para apoio à decisão.

O foco está em:
- Estruturar dados segundo boas práticas de **modelação dimensional**
- Criar uma **camada analítica reutilizável**
- Definir **KPIs de negócio claros** (vendas, margem, clientes, artigos)
- Preparar dados prontos a consumir por ferramentas de BI (Power BI / Tableau / Metabase)

Este tipo de pipeline é típico de contextos reais de **Data Analytics / Analytics Engineering**,
onde dados transacionais precisam de ser consolidados, validados e analisados.

## Objetivo
Demonstrar competências práticas em:
- Modelação dimensional (fact + dimensões)
- Transformação e análise de dados com Python
- Definição de KPIs de negócio
- Preparação de dados para ferramentas de BI

## Conteúdo do Projeto
- `01_mock_data_final.ipynb` — Notebook principal com todo o pipeline analítico
- `fact_venda.csv` — Tabela de factos (vendas)
- `dim_*.csv` — Tabelas de dimensão (clientes, artigos, tempo, vendedores)
- `outputs/` — KPIs e tabelas finais exportadas em CSV
- `src/phc_analytics/` — Package Python com código auxiliar

## KPIs Calculados
- Faturação total
- Margem total e %
- Nº de vendas
- Ticket médio
- Faturação por cliente
- Rankings de clientes e artigos

## Stack Técnica
- Python
- Pandas
- Jupyter Notebook
- Git / GitHub

## Estado
Versão inicial estável — v0.1.0

PHC Analytics — Data Engineering Portfolio

Projeto de Data Engineering e Analytics Engineering que simula um cenário real de dados empresariais (PHC ERP / e-commerce), com foco em pipelines de ingestão, normalização, processamento incremental e cálculo de KPIs de negócio.

Este projeto foi construído com mentalidade de produção, não como notebook exploratório.

Objetivo

Demonstrar competências práticas em:
	•	Arquitetura de pipelines de dados
	•	Ingestão de dados via API
	•	Normalização e padronização de schemas
	•	Processamento incremental com controlo de estado
	•	Modelação analítica e KPIs de negócio
	•	Qualidade, contratos de dados e testes automáticos

Arquitetura

data/
Dados mock e fontes externas

src/phc_analytics/
	•	staging/ — ingestão e normalização
	•	analytics/ — KPIs e métricas de negócio
	•	utils/ — utilitários comuns

app.py
Camada de apresentação (Streamlit)

out/
Outputs analíticos (facts, dimensions, KPIs)

Pipeline de Dados
	1.	Ingestão
Consumo de APIs (ex: PrestaShop), preparado para integração real com ERP / Odoo e persistência controlada de dados brutos.
	2.	Normalização
Padronização de schemas, suporte a múltiplos formatos de input, mapeamento de aliases e validação de tipos.
	3.	Incremental Processing
Pipeline incremental com watermarks por entidade, execução idempotente e estado persistido em ficheiro (_pipeline_state.json).
	4.	Camada Analítica
Geração de tabelas fact e dimensão, KPIs reutilizáveis e dados prontos para BI ou consumo downstream.

KPIs Implementados
	•	Faturação total
	•	Número de documentos
	•	Número de clientes
	•	Ticket médio
	•	Evolução temporal
	•	Rankings de clientes e produtos

Qualidade e Contratos de Dados
	•	Testes automáticos com pytest
	•	Validação de chaves primárias e estrangeiras
	•	Garantias de não-null e consistência
	•	Falha cedo quando o contrato de dados é violado

Stack Técnica

Python
Pandas
Streamlit
pytest
uv
Git / GitHub

Preparado para evolução para PostgreSQL, SQLAlchemy e orquestração (Prefect / Airflow).

Execução

make run

ou

uv run streamlit run app.py

Estado do Projeto

Pipeline funcional, incremental e testado.
Preparado para integração real com PrestaShop e Odoo.

Autor

João Fonseca
Data / Big Data Engineer
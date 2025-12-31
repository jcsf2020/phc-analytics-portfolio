# PHC Analytics — Data Contract (v1)

## Objetivo
Definir o contrato da pipeline `run_pipeline()`:
- **Inputs** (o que entra)
- **Outputs** (o que sai)
- **Garantias** (o que é assegurado: schema, tipos, qualidade, partições)

---

## 1) Entry Point

### Função
`src/phc_analytics/pipeline/run.py::run_pipeline`

### Assinatura (contrato de execução)
- `out_dir: str = "out"`
- `partition_fact: bool = False`

### Comportamento
- Executa ingestão → modelação (star schema) → quality gate → analytics → persistência.
- Se o **quality gate** falhar: levanta `ValueError("Quality gate failed")`.
- Se `partition_fact=True` e o FACT não tiver `year_month`: levanta `ValueError(...)`.

---

## 2) Input Contract (Staging)

### Fonte atual (mock)
`src/phc_analytics/staging/documents.py::load_documents_mock()`

### DataFrame esperado (colunas mínimas)
- `doc_id`
- `doc_date`
- `client_id`
- `client_name`
- `doc_type`
- `total`

### Regras base
- `doc_date` deve ser parseável para datetime (erros viram `NaT` quando normalizado).
- `doc_id` e `client_id` devem ser numéricos (erros viram `NA` quando normalizado).
- `total` deve ser numérico (erros viram `NaN` quando normalizado).

---

## 3) Model Contract (Star Schema)

### 3.1 FACT — `fact_documents`

**Builder**
`src/phc_analytics/models/fact_documents.py::build_fact_documents(df_docs)`

**Grain (granularidade)**
- 1 linha = 1 documento (chave: `doc_id`)

**Schema canónico (colunas)**
- `doc_id` (int)
- `doc_date` (datetime)
- `client_id` (int)
- `doc_type` (string/catégoria)
- `total` (float/decimal)
- `year_month` (string `YYYY-MM`)  *(quando usado para particionamento e queries por mês)*

**Regras do FACT**
- `doc_date` normalizado via `pd.to_datetime(..., errors="coerce")`
- `doc_id` e `client_id` normalizados para inteiros quando possível
- `total` normalizado para numérico
- Garantia de grain: `drop_duplicates(subset=["doc_id"], keep="last")`
- Registos sem `doc_id` válido são removidos: `dropna(subset=["doc_id"])`

---

### 3.2 DIM — `dim_clients`
**Builder**
`src/phc_analytics/models/dim_clients.py::build_dim_clients(df_docs)`

**Objetivo**
- Dimensão de clientes derivada do staging.

**Notas**
- Dimensão pequena; não é particionada.

---

### 3.3 DIM — `dim_time`
**Builder**
`src/phc_analytics/models/dim_time.py::build_dim_time(df_docs)`

**Objetivo**
- Dimensão de tempo baseada em `doc_date`.

**Notas**
- Dimensão pequena; não é particionada.

---

## 4) Quality Gate Contract

### Checker
`src/phc_analytics/quality/checks.py::run_quality_gate_fact_documents(fact_df)`

### Garantia
- A pipeline só “passa” se **todas** as checks retornarem `ok=True`.
- Caso contrário: `ValueError("Quality gate failed")`.

*(As regras concretas do quality gate vivem no módulo `quality/` e são parte do contrato: falhar = parar.)*

---

## 5) Analytics Contract

### KPIs (top cards)
`src/phc_analytics/analytics/kpis.py::kpis_top_cards(raw)`

### Série temporal (mensal)
`src/phc_analytics/analytics/timeseries.py::faturacao_mensal(raw)`

**Objetivo**
- Produzir métricas para consumo posterior (dashboard/relatórios).

---

## 6) Storage Contract (Persistência)

### Writers
`src/phc_analytics/storage/writer.py::write_parquet(...)`
`src/phc_analytics/storage/writer.py::write_csv(...)`

### Estrutura de output (base)
Dentro de `out_dir`:
- `parquet/`
- `csv/`

### Outputs sempre escritos
- Parquet:
  - `parquet/fact_documents...`
  - `parquet/dim_clients.parquet`
  - `parquet/dim_time.parquet`
- CSV (debug/partilha):
  - `csv/fact_documents.csv`
  - `csv/dim_clients.csv`

---

## 7) Partitioning Contract (FACT)

### Quando `partition_fact=False` (default)
- Escreve **um único ficheiro/dataset**:
  - `out_dir/parquet/fact_documents.parquet` (ou equivalente do writer)

### Quando `partition_fact=True`
- Escreve o FACT como **dataset particionado por `year_month`**:
  - `out_dir/parquet/fact_documents/year_month=YYYY-MM/*.parquet`

### Regra crítica
- `partition_fact=True` exige:
  - coluna `year_month` presente no FACT
  - formato `YYYY-MM`
  - sem nulos (ou nulos tratados antes)

### Nota importante (para evitar confusão)
Ao ler um **ficheiro** diretamente dentro de uma partição:
- Ex.: `pd.read_parquet('.../year_month=2024-03')`
- O pandas pode devolver **sem** a coluna `year_month` no DataFrame (depende do engine/leitura).
Ao ler o **dataset raiz** com filtro:
- Ex.: `pd.read_parquet(base, filters=[('year_month','==','2024-03')])`
- O pandas devolve o DataFrame com `year_month` e só lê a(s) partição(ões) necessária(s).

---

## 8) Data Lake Access Pattern (o essencial)

Quando fazemos:
`pd.read_parquet(base, filters=[('year_month','==','2024-03')])`

Isto significa:
- **Partition pruning**: só lê a partição `year_month=2024-03`
- **Predicate pushdown** (quando suportado): empurra filtros para o engine reduzir leitura

Isto é o padrão de acesso usado em:
- Spark / Trino / DuckDB
- BigQuery partitions / Athena partitions

---

## 9) Definition of Done (DoD) do contrato v1

Consideramos o contrato v1 “congelado” quando:
- A assinatura da pipeline é estável: `(out_dir, partition_fact)`
- O schema do FACT e DIMs está documentado
- O comportamento de particionamento está documentado
- Existem testes automáticos que validam:
  - schema
  - grain
  - partições e leitura com filtro
  - quality gate (pass/fail)

---

## 10) Execução (comandos de referência)

### Run normal (sem partições)
`uv run python -m src.phc_analytics.pipeline.run`

### Run com partições (via Python)
`uv run python -c "from src.phc_analytics.pipeline.run import run_pipeline; run_pipeline(out_dir='out_test', partition_fact=True); print('OK')"`

### Leitura por mês (dataset + filter)
`uv run python -c "import pandas as pd; base='out_test/parquet/fact_documents'; df=pd.read_parquet(base, filters=[('year_month','==','2024-03')]); print(len(df)); print(df.head())"`
from phc_analytics.staging.documents import load_documents_mock
from phc_analytics.models.fact_documents import build_fact_documents
from phc_analytics.models.dim_clients import build_dim_clients
from phc_analytics.models.dim_time import build_dim_time
from phc_analytics.analytics.kpis import kpis_top_cards
from phc_analytics.analytics.timeseries import faturacao_mensal
from phc_analytics.quality.checks import run_quality_gate_fact_documents
from phc_analytics.storage.writer import write_parquet, write_csv


def run_pipeline(out_dir: str = "out", partition_fact: bool = False):
    # 1) Ingestao
    raw = load_documents_mock()

    # 2) Modelacao (Star Schema)
    fact = build_fact_documents(raw)
    dim_clients = build_dim_clients(raw)
    dim_time = build_dim_time(raw)

    # 3) Quality Gate
    quality_results = run_quality_gate_fact_documents(fact)
    if not all(r.ok for r in quality_results):
        raise ValueError("Quality gate failed")

    # 4) Analytics
    kpis = kpis_top_cards(raw)
    monthly = faturacao_mensal(raw)

    # 5) Persistencia (Parquet + CSV)
    res = []

    # FACT: opcionalmente particionado por year_month
    if partition_fact:
        if "year_month" not in fact.columns:
            raise ValueError("partition_fact=True requires fact_documents to have column 'year_month'")
        res.append(write_parquet(fact, out_dir, "fact_documents", partition_cols=["year_month"]))
    else:
        res.append(write_parquet(fact, out_dir, "fact_documents"))

    # DIMs: nao particionadas (pequenas)
    res.append(write_parquet(dim_clients, out_dir, "dim_clients"))
    res.append(write_parquet(dim_time, out_dir, "dim_time"))

    # CSVs (debug/partilha)
    res.append(write_csv(fact, out_dir, "fact_documents"))
    res.append(write_csv(dim_clients, out_dir, "dim_clients"))

    return {
        "fact_documents": fact,
        "dim_clients": dim_clients,
        "dim_time": dim_time,
        "kpis": kpis,
        "monthly": monthly,
        "written": res,
    }


if __name__ == "__main__":
    out = run_pipeline()
    print("PIPELINE OK")
    for r in out["written"]:
        print(f"- {r.kind.upper()} {r.path} rows={r.rows}")

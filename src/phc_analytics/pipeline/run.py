from __future__ import annotations

import argparse
from typing import Any, Dict

from phc_analytics.staging.documents import load_documents_mock
from phc_analytics.models.fact_documents import build_fact_documents
from phc_analytics.models.dim_clients import build_dim_clients
from phc_analytics.models.dim_time import build_dim_time
from phc_analytics.analytics.kpis import kpis_top_cards
from phc_analytics.analytics.timeseries import faturacao_mensal
from phc_analytics.quality.checks import run_quality_gate_fact_documents
from phc_analytics.storage.writer import write_parquet, write_csv


def run_pipeline(out_dir: str = "out", partition_fact: bool = False) -> Dict[str, Any]:
    """Run the local (mock) analytics pipeline.

    Notes:
    - This runner currently uses mock ingestion (load_documents_mock).
    - Output is persisted to Parquet/CSV via storage.writer.
    """

    # 1) Ingestion
    raw = load_documents_mock()

    # 2) Modeling (star schema)
    fact = build_fact_documents(raw)
    dim_clients = build_dim_clients(raw)
    dim_time = build_dim_time(raw)

    # 3) Quality gate
    quality_results = run_quality_gate_fact_documents(fact)
    if not all(r.ok for r in quality_results):
        raise ValueError("Quality gate failed")

    # 4) Analytics
    kpis = kpis_top_cards(raw)
    monthly = faturacao_mensal(raw)

    # 5) Persistence (Parquet + CSV)
    written = []

    # FACT: optionally partitioned by year_month
    if partition_fact:
        if "year_month" not in fact.columns:
            raise ValueError(
                "partition_fact=True requires fact_documents to have column 'year_month'"
            )
        written.append(
            write_parquet(
                fact, out_dir, "fact_documents", partition_cols=["year_month"]
            )
        )
    else:
        written.append(write_parquet(fact, out_dir, "fact_documents"))

    # DIMs: not partitioned (small)
    written.append(write_parquet(dim_clients, out_dir, "dim_clients"))
    written.append(write_parquet(dim_time, out_dir, "dim_time"))

    # CSVs (debug/share)
    written.append(write_csv(fact, out_dir, "fact_documents"))
    written.append(write_csv(dim_clients, out_dir, "dim_clients"))

    return {
        "fact_documents": fact,
        "dim_clients": dim_clients,
        "dim_time": dim_time,
        "kpis": kpis,
        "monthly": monthly,
        "written": written,
    }


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="PHC Analytics pipeline runner (mock ingestion)"
    )
    p.add_argument("--out-dir", default="out", help="Output directory (default: out)")
    p.add_argument(
        "--partition-fact",
        action="store_true",
        help="Partition fact_documents by year_month when writing Parquet",
    )
    return p


if __name__ == "__main__":
    args = _build_arg_parser().parse_args()
    out = run_pipeline(out_dir=args.out_dir, partition_fact=args.partition_fact)
    print("PIPELINE OK")
    for r in out["written"]:
        # Be tolerant to minor schema differences in write result objects.
        kind = getattr(r, "kind", "unknown")
        path = getattr(r, "path", "")
        rows = getattr(r, "rows", "")
        print(f"- {str(kind).upper()} {path} rows={rows}")

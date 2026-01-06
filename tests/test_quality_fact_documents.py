from __future__ import annotations

from pathlib import Path
import pandas as pd

from phc_analytics.pipeline.run import run_pipeline


def test_quality_fact_documents(tmp_path: Path) -> None:
    out_dir = tmp_path / "out_q"
    run_pipeline(out_dir=str(out_dir), partition_fact=True)

    base = out_dir / "parquet" / "fact_documents"
    df = pd.read_parquet(str(base))  # leitura completa (pequeno dataset mock)

    # 1) schema mínimo
    required = {"doc_id", "doc_date", "client_id", "doc_type", "total", "year_month"}
    assert required.issubset(set(df.columns)), f"missing cols: {required - set(df.columns)}"

    # 2) nulos críticos
    assert df["doc_id"].notna().all()
    assert df["doc_date"].notna().all()
    assert df["client_id"].notna().all()
    assert df["total"].notna().all()

    # 3) domínios/regras
    assert (df["total"] >= 0).all(), "total has negatives"
    assert df["doc_type"].isin(["FATURA", "RECIBO", "GUIA"]).all(), "unexpected doc_type"

    # 4) unicidade (mock deve ter doc_id único)
    assert df["doc_id"].is_unique, "doc_id must be unique"

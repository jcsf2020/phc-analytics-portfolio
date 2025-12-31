from __future__ import annotations

from pathlib import Path

import pandas as pd

from phc_analytics.pipeline.run import run_pipeline


def test_pipeline_contract_partition_fact_filter(tmp_path: Path) -> None:
    """
    Contrato mínimo:
    - run_pipeline(partition_fact=True) escreve o FACT como dataset particionado por year_month
    - é possível ler o dataset com filters=[('year_month','==',...)] e o year_month vem na tabela lida
    """
    out_dir = tmp_path / "out_test"

    out = run_pipeline(out_dir=str(out_dir), partition_fact=True)

    dataset = out_dir / "parquet" / "fact_documents"
    assert dataset.is_dir(), "missing dataset out_dir/parquet/fact_documents"

    ym = "2024-03"
    df = pd.read_parquet(str(dataset), filters=[("year_month", "==", ym)])

    assert len(df) > 0, "expected some rows for partition"
    assert "year_month" in df.columns, "year_month missing after dataset read"
    assert (df["year_month"] == ym).all(), "filter not respected"

    # sanity: datas dentro do mês
    assert df["doc_date"].min().month == 3
    assert df["doc_date"].max().month == 3

    # output shape: garante que a pipeline devolve 'written'
    assert "written" in out and len(out["written"]) > 0

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class WriteResult:
    kind: str  # "parquet" | "csv"
    path: str
    rows: int


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_parquet(df: pd.DataFrame, out_dir: str, name: str, partition_cols: Optional[list[str]] = None) -> WriteResult:
    """
    Escreve DataFrame para Parquet.

    - out_dir: diretório base (ex: "out")
    - name: nome lógico (ex: "fact_documents")
    - partition_cols: opcional; particionamento estilo data lake (ex: ["year_month"])
    """
    base = Path(out_dir) / "parquet" / name
    _ensure_dir(base)

    if partition_cols:
        # dataset particionado (pasta com múltiplos ficheiros)
        df.to_parquet(base, index=False, partition_cols=partition_cols)
        return WriteResult(kind="parquet", path=str(base), rows=len(df))

    file_path = base.with_suffix(".parquet")  # out/parquet/fact_documents.parquet
    _ensure_dir(file_path.parent)
    df.to_parquet(file_path, index=False)
    return WriteResult(kind="parquet", path=str(file_path), rows=len(df))


def write_csv(df: pd.DataFrame, out_dir: str, name: str) -> WriteResult:
    """
    Escreve DataFrame para CSV (bom para debug/partilha rápida).
    """
    base = Path(out_dir) / "csv"
    _ensure_dir(base)

    file_path = base / f"{name}.csv"
    df.to_csv(file_path, index=False)
    return WriteResult(kind="csv", path=str(file_path), rows=len(df))

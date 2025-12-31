from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List
import pandas as pd


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str = ""


def check_not_null(df: pd.DataFrame, columns: Iterable[str]) -> CheckResult:
    nulls = df[list(columns)].isna().sum()
    bad = nulls[nulls > 0]

    if not bad.empty:
        return CheckResult(
            name="not_null_check",
            ok=False,
            details=f"Nulls encontrados: {bad.to_dict()}",
        )

    return CheckResult(name="not_null_check", ok=True)


def check_grain_unique(df: pd.DataFrame, grain: Iterable[str]) -> CheckResult:
    dup = df.duplicated(subset=list(grain)).sum()

    if dup > 0:
        return CheckResult(
            name="grain_unique_check",
            ok=False,
            details=f"{dup} linhas duplicadas no grain {list(grain)}",
        )

    return CheckResult(name="grain_unique_check", ok=True)


def run_quality_gate_fact_documents(df: pd.DataFrame) -> List[CheckResult]:
    results = []

    results.append(check_not_null(df, ["doc_id", "doc_date", "client_id", "total"]))
    results.append(check_grain_unique(df, ["doc_id"]))

    return results

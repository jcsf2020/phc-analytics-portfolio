from __future__ import annotations

import pandas as pd


def faturacao_mensal(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula faturação mensal a partir dos documentos.

    Retorna DataFrame com:
    - month (timestamp no 1º dia do mês)
    - vendas (soma de total)
    - documentos (nº docs únicos)
    """
    if df.empty:
        return pd.DataFrame(columns=["month", "vendas", "documentos"])

    tmp = (
        df.assign(month=df["doc_date"].dt.to_period("M").dt.to_timestamp())
        .groupby("month", as_index=False)
        .agg(
            vendas=("total", "sum"),
            documentos=("doc_id", "nunique"),
        )
        .sort_values("month")
    )

    return tmp


def crescimento_mensal(df_mensal: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula crescimento percentual mês-a-mês da faturação.

    Espera colunas:
    - month
    - vendas
    """
    if df_mensal.empty:
        return pd.DataFrame(columns=["month", "vendas", "crescimento_pct"])

    out = df_mensal.copy()
    out["crescimento_pct"] = out["vendas"].pct_change() * 100.0
    return out

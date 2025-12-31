import pandas as pd


def build_dim_time(df_docs: pd.DataFrame) -> pd.DataFrame:
    """
    Dimensão tempo.
    Grain: 1 linha = 1 dia.

    Espera:
      - doc_date (datetime)

    Devolve:
      - date
      - year
      - month
      - month_name
      - quarter
      - year_month
    """
    if df_docs is None or df_docs.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "year",
                "month",
                "month_name",
                "quarter",
                "year_month",
            ]
        )

    dates = pd.to_datetime(df_docs["doc_date"], errors="coerce").dropna().unique()
    dates = pd.to_datetime(dates)

    out = pd.DataFrame({"date": dates})
    out["year"] = out["date"].dt.year
    out["month"] = out["date"].dt.month
    out["month_name"] = out["date"].dt.month_name()
    out["quarter"] = out["date"].dt.to_period("Q").astype(str)
    out["year_month"] = out["date"].dt.to_period("M").astype(str)

    out = out.sort_values("date").reset_index(drop=True)

    return out

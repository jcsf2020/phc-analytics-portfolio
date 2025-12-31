import pandas as pd


def build_fact_documents(df_docs: pd.DataFrame) -> pd.DataFrame:
    """
    FACT documentos.
    Grain: 1 linha = 1 documento (doc_id).

    Espera colunas:
      - doc_id
      - doc_date
      - client_id
      - doc_type
      - total

    Devolve colunas:
      - doc_id
      - doc_date
      - year_month
      - client_id
      - doc_type
      - total
    """
    if df_docs is None or df_docs.empty:
        return pd.DataFrame(
            columns=[
                "doc_id",
                "doc_date",
                "year_month",
                "client_id",
                "doc_type",
                "total",
            ]
        )

    out = df_docs.copy()

    # Normalização mínima
    out["doc_date"] = pd.to_datetime(out["doc_date"], errors="coerce")
    out["year_month"] = out["doc_date"].dt.to_period("M").astype(str)
    out["doc_id"] = pd.to_numeric(out["doc_id"], errors="coerce").astype("Int64")
    out["client_id"] = pd.to_numeric(out["client_id"], errors="coerce").astype("Int64")
    out["total"] = pd.to_numeric(out["total"], errors="coerce")

    # Colunas canónicas
    out = out[
        ["doc_id", "doc_date", "year_month", "client_id", "doc_type", "total"]
    ].copy()

    # Garantir grain: 1 doc_id = 1 linha
    out = out.dropna(subset=["doc_id"]).drop_duplicates(subset=["doc_id"], keep="last")

    # Tipos finais
    out["doc_id"] = out["doc_id"].astype("int64", errors="ignore")
    out["client_id"] = out["client_id"].astype("int64", errors="ignore")

    return out

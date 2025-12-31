import pandas as pd


def build_dim_clients(df_docs: pd.DataFrame) -> pd.DataFrame:
    """
    Dimensão de clientes.
    Grain: 1 linha = 1 cliente.

    Espera colunas:
      - client_id
      - client_name

    Devolve colunas:
      - client_id
      - client_name
    """
    if df_docs is None or df_docs.empty:
        return pd.DataFrame(columns=["client_id", "client_name"])

    out = df_docs.copy()

    # Normalização
    out["client_id"] = pd.to_numeric(out["client_id"], errors="coerce").astype("Int64")
    out["client_name"] = out["client_name"].astype(str).str.strip()

    # Colunas canónicas
    out = out[["client_id", "client_name"]].copy()

    # Garantir grain: 1 cliente = 1 linha
    out = (
        out.dropna(subset=["client_id"])
        .drop_duplicates(subset=["client_id"], keep="last")
        .sort_values("client_id")
    )

    # Tipo final
    out["client_id"] = out["client_id"].astype("int64", errors="ignore")

    return out

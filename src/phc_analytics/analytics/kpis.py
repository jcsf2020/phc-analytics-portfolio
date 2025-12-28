from __future__ import annotations

from typing import Dict
import pandas as pd


def kpis_top_cards(df: pd.DataFrame) -> Dict[str, float]:
    """
    Calcula KPIs principais para o topo do dashboard.

    KPIs:
    - vendas_total: soma de 'total'
    - n_documentos: nº de documentos únicos
    - n_clientes: nº de clientes únicos
    - ticket_medio: média de 'total'

    Mentalidade Data Engineer:
    - Função pura (input -> output)
    - Sem dependência de UI
    - Fácil de testar e reutilizar
    """
    if df.empty:
        return {
            "vendas_total": 0.0,
            "n_documentos": 0,
            "n_clientes": 0,
            "ticket_medio": 0.0,
        }

    vendas_total = float(df["total"].sum())
    n_documentos = int(df["doc_id"].nunique())
    n_clientes = int(df["client_id"].nunique())
    ticket_medio = float(df["total"].mean())

    return {
        "vendas_total": vendas_total,
        "n_documentos": n_documentos,
        "n_clientes": n_clientes,
        "ticket_medio": ticket_medio,
    }

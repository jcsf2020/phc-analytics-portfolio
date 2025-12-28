from __future__ import annotations

from typing import Final
import runpy

import pandas as pd

MOCK_PATH: Final[str] = "data/mock_documents.py"


def load_documents_mock(path: str = MOCK_PATH) -> pd.DataFrame:
    """
    Carrega dados mock de documentos a partir de um script Python.

    Porque isto existe (mentalidade Data Engineer):
    - Separa "ingestão" da UI (app.py).
    - Amanhã trocas mock por BD/CSV/API sem refazer o dashboard.
    - Garante normalização mínima (tipos/datas) num único ponto.

    Espera que o script exporte uma variável 'df_documents' (pandas DataFrame).
    """
    g = runpy.run_path(path)

    if "df_documents" not in g:
        raise KeyError(
            f"'{path}' não expôs 'df_documents'. "
            "Garante que o mock_documents.py define df_documents."
        )

    df = g["df_documents"].copy()

    # Normalizar datas (garantir datetime)
    df["doc_date"] = pd.to_datetime(df["doc_date"], errors="coerce")

    # Validação mínima
    if df["doc_date"].isna().any():
        raise ValueError("Existem doc_date inválidas após parsing (NaT).")

    return df

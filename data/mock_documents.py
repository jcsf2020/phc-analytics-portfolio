import pandas as pd
import numpy as np

# -----------------------------
# Configurações base
# -----------------------------
N_DOCUMENTS = 500
START_DATE = "2023-01-01"
END_DATE = "2024-12-31"

np.random.seed(42)  # reprodutibilidade (conceito CRÍTICO)

# -----------------------------
# Gerar datas
# -----------------------------
dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D")
doc_dates = np.random.choice(dates, size=N_DOCUMENTS)

# -----------------------------
# Clientes
# -----------------------------
clients = {
    1: "Cliente A",
    2: "Cliente B",
    3: "Cliente C",
    4: "Cliente D",
    5: "Cliente E",
}

client_ids = np.random.choice(list(clients.keys()), size=N_DOCUMENTS)
client_names = [clients[cid] for cid in client_ids]

# -----------------------------
# Tipos de documento
# -----------------------------
doc_types = np.random.choice(
    ["FATURA", "RECIBO", "GUIA"],
    size=N_DOCUMENTS,
    p=[0.6, 0.3, 0.1],
)

# -----------------------------
# Valores
# -----------------------------
totals = np.round(np.random.uniform(50, 5000, size=N_DOCUMENTS), 2)

# -----------------------------
# DataFrame final
# -----------------------------
df_documents = pd.DataFrame(
    {
        "doc_id": range(1, N_DOCUMENTS + 1),
        "doc_date": pd.to_datetime(doc_dates),
        "client_id": client_ids,
        "client_name": client_names,
        "doc_type": doc_types,
        "total": totals,
    }
)

# -----------------------------
# Execução direta (debug)
# -----------------------------
if __name__ == "__main__":
    print(df_documents.head())
    print(df_documents.info())

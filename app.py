import streamlit as st
import pandas as pd

from src.phc_analytics.staging.documents import load_documents_mock
from src.phc_analytics.analytics.kpis import kpis_top_cards
from src.phc_analytics.analytics.timeseries import faturacao_mensal

# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="PHC Analytics",
    layout="wide",
)

# =========================================================
# CARREGAR DADOS (MOCK)
# =========================================================
df = load_documents_mock()
df["doc_date"] = pd.to_datetime(df["doc_date"])

# =========================================================
# SIDEBAR — FILTROS
# =========================================================
st.sidebar.markdown("## Navegue pelos botões")
st.sidebar.markdown("### Filtros")

anos_disponiveis = sorted(df["doc_date"].dt.year.unique())
ano_sel = st.sidebar.multiselect(
    "Ano",
    options=anos_disponiveis,
    default=anos_disponiveis,
)

meses_disponiveis = list(range(1, 13))
mes_sel = st.sidebar.multiselect(
    "Mês",
    options=meses_disponiveis,
    default=meses_disponiveis,
)

clientes_disponiveis = sorted(df["client_name"].unique())
cliente_sel = st.sidebar.multiselect(
    "Cliente",
    options=clientes_disponiveis,
    default=clientes_disponiveis,
)

# Aplicar filtros
df_f = df[
    (df["doc_date"].dt.year.isin(ano_sel))
    & (df["doc_date"].dt.month.isin(mes_sel))
    & (df["client_name"].isin(cliente_sel))
].copy()

# =========================================================
# HEADER
# =========================================================
st.markdown("# DASHBOARD ANALÍTICO")

# =========================================================
# KPIs — TOPO
# =========================================================
k = kpis_top_cards(df_f)

c1, c2, c3, c4 = st.columns(4)
c1.metric("VENDAS (TOTAL)", f"{k['vendas_total']:,.2f} €")
c2.metric("DOCUMENTOS", f"{k['n_documentos']}")
c3.metric("CLIENTES", f"{k['n_clientes']}")
c4.metric("TICKET MÉDIO", f"{k['ticket_medio']:,.2f} €")

st.divider()

# =========================================================
# GRÁFICOS SUPERIORES
# =========================================================
left, right = st.columns([1.2, 1])

with left:
    st.subheader("PROSPEÇÃO / MOVIMENTO NO TEMPO")

    tmp = faturacao_mensal(df_f)
    if tmp.empty:
        st.info("Sem dados para os filtros selecionados.")
    else:
        st.bar_chart(tmp.set_index("month")["documentos"])

with right:
    st.subheader("VENDAS (TOTAL) vs CUSTO (MKT) [SIMULADO]")

    tmp = faturacao_mensal(df_f)
    if tmp.empty:
        st.info("Sem dados para os filtros selecionados.")
    else:
        tmp["custo_mkt"] = tmp["vendas"] * 0.12
        tmp = tmp.set_index("month")[["vendas", "custo_mkt"]]
        st.line_chart(tmp)

st.divider()

# =========================================================
# GRÁFICOS INFERIORES
# =========================================================
b1, b2 = st.columns(2)

with b1:
    st.subheader("VENDAS POR TIPO DE DOCUMENTO")

    if df_f.empty:
        st.info("Sem dados para os filtros selecionados.")
    else:
        by_type = (
            df_f.groupby("doc_type", as_index=False)
            .agg(vendas=("total", "sum"))
            .sort_values("vendas", ascending=False)
            .set_index("doc_type")
        )
        st.bar_chart(by_type["vendas"])

with b2:
    st.subheader("TOP 5 CLIENTES POR VENDAS")

    if df_f.empty:
        st.info("Sem dados para os filtros selecionados.")
    else:
        top_clients = (
            df_f.groupby("client_name", as_index=False)
            .agg(vendas=("total", "sum"))
            .sort_values("vendas", ascending=False)
            .head(5)
            .set_index("client_name")
        )
        st.bar_chart(top_clients["vendas"])

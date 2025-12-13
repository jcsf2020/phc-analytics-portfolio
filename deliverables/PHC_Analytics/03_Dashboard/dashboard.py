from typing import Optional
import os
import pandas as pd
import streamlit as st

APP_TITLE = "PHC Analytics (Mock) — KPIs & Dashboards"

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")

# --- Helpers ---
from typing import Optional

def load_csv(name: str) -> Optional[pd.DataFrame]:
    path = os.path.join(DATA_DIR, name)
    if not os.path.exists(path):
        return None
    return pd.read_csv(path)

def fmt_eur(x: float) -> str:
    # formato simples (PT): separador milhar e 2 casas
    return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_num(x: float) -> str:
    return f"{x:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- Page ---
st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)
st.caption("Dashboard de demonstração baseado em modelo estrela e dados mock. Pronto para ligar ao PHC real quando houver acesso à BD.")

# Sidebar (filtros base - ficam “ativos” quando tivermos DF detalhado)
st.sidebar.header("Filtros")
st.sidebar.info("Nesta fase (mock), os filtros ficam prontos para ligar ao detalhe quando exportares `tabela_detalhe_vendas.csv`.")

# Tentativa de carregar outputs se já exportaste CSVs
kpi_cards = load_csv("kpi_cards.csv")
faturacao_mensal = load_csv("faturacao_mensal.csv")
margem_mensal = load_csv("margem_mensal.csv")
top_clientes = load_csv("top_clientes.csv")
clientes_inativos = load_csv("clientes_inativos.csv")
top_artigos = load_csv("top_artigos.csv")
top_artigos_margem = load_csv("top_artigos_margem.csv")

missing = [name for name, df in {
    "kpi_cards.csv": kpi_cards,
    "faturacao_mensal.csv": faturacao_mensal,
    "margem_mensal.csv": margem_mensal,
    "top_clientes.csv": top_clientes,
    "clientes_inativos.csv": clientes_inativos,
    "top_artigos.csv": top_artigos,
    "top_artigos_margem.csv": top_artigos_margem,
}.items() if df is None]

if missing:
    st.warning(
        "Ainda não encontrei alguns ficheiros em `outputs/`. "
        "Sem stress — a app abre na mesma.\n\n"
        f"Faltam: {', '.join(missing)}\n\n"
        "Próximo passo: exportar estes DataFrames para CSV a partir do notebook."
    )

tab_overview, tab_clients, tab_products = st.tabs(["Visão Geral", "Clientes", "Produtos"])

# --- Tab 1: Visão Geral ---
with tab_overview:
    st.subheader("Visão Geral")

    if kpi_cards is not None and "KPI" in kpi_cards.columns and "Valor" in kpi_cards.columns:
        # Mostra os KPIs em cards (4 por linha)
        cols = st.columns(4)
        for i, row in enumerate(kpi_cards.itertuples(index=False)):
            kpi = getattr(row, "KPI")
            val = getattr(row, "Valor")
            c = cols[i % 4]
            # tenta formatar se for valor monetário
            if "€" in kpi or "Faturação" in kpi or "Margem" in kpi or "Ticket" in kpi:
                try:
                    val_txt = fmt_eur(float(val))
                except Exception:
                    val_txt = str(val)
            else:
                try:
                    val_txt = fmt_num(float(val))
                except Exception:
                    val_txt = str(val)
            c.metric(label=kpi, value=val_txt)
    else:
        st.info("KPIs (kpi_cards) ainda não carregados. Exporta `kpi_cards.csv` para aparecerem aqui.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Faturação mensal")
        if faturacao_mensal is not None and {"periodo", "total_liquido"}.issubset(faturacao_mensal.columns):
            st.line_chart(faturacao_mensal.set_index("periodo")["total_liquido"])
        else:
            st.info("Exporta `faturacao_mensal.csv` com colunas `periodo` e `total_liquido`.")

    with col2:
        st.markdown("### Margem mensal (%)")
        if margem_mensal is not None and {"periodo", "margem_pct"}.issubset(margem_mensal.columns):
            st.line_chart(margem_mensal.set_index("periodo")["margem_pct"])
        else:
            st.info("Exporta `margem_mensal.csv` com colunas `periodo` e `margem_pct`.")

# --- Tab 2: Clientes ---
with tab_clients:
    st.subheader("Clientes")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### Top clientes por faturação")
        if top_clientes is not None:
            st.dataframe(top_clientes, use_container_width=True)
        else:
            st.info("Exporta `top_clientes.csv`.")

    with c2:
        st.markdown("### Clientes inativos (>180 dias)")
        if clientes_inativos is not None:
            st.dataframe(clientes_inativos, use_container_width=True)
        else:
            st.info("Exporta `clientes_inativos.csv`.")

# --- Tab 3: Produtos ---
with tab_products:
    st.subheader("Produtos / Serviços")

    p1, p2 = st.columns(2)

    with p1:
        st.markdown("### Top artigos por faturação")
        if top_artigos is not None:
            st.dataframe(top_artigos, use_container_width=True)
        else:
            st.info("Exporta `top_artigos.csv`.")

    with p2:
        st.markdown("### Top artigos por margem")
        if top_artigos_margem is not None:
            st.dataframe(top_artigos_margem, use_container_width=True)
        else:
            st.info("Exporta `top_artigos_margem.csv`.")
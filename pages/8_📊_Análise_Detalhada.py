# marketlens/pages/11_📊_Análise_Detalhada.py

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from view_utils import setup_sidebar
from utils.journal_utils import get_journal_entries
from utils.playbook_utils import get_playbook_setups
from utils.reporting_engine import calculate_dashboard_metrics
from utils.accounts_utils import get_trading_accounts

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Análise Detalhada")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.switch_page("pages/1_👤_Login.py")

user_id = st.session_state['user_info'].get('localId')

# --- CABEÇALHO ---
st.title("🔬 Análise Detalhada (Deep Dive)")
st.caption("Filtre e analise o seu histórico de operações para encontrar insights valiosos.")
st.markdown("---")

# --- CARREGAMENTO INICIAL DE DADOS ---
with st.spinner("A carregar histórico completo..."):
    df_journal_all = get_journal_entries(user_id)
    accounts = get_trading_accounts(user_id)
    setups = get_playbook_setups(user_id)

if df_journal_all.empty:
    st.info("Ainda não há operações registadas no seu diário para analisar."); st.stop()

# --- PAINEL DE FILTROS ---
with st.expander("🔍 Aplicar Filtros", expanded=True):
    filter_cols = st.columns(4)
    
    with filter_cols[0]:
        # Filtro de Datas
        date_options = {
            "Todos": (None, None),
            "Últimos 7 dias": (datetime.now() - timedelta(days=7), datetime.now()),
            "Este Mês": (datetime.now().replace(day=1), datetime.now()),
            "Últimos 90 dias": (datetime.now() - timedelta(days=90), datetime.now()),
            "Este Ano": (datetime.now().replace(month=1, day=1), datetime.now())
        }
        selected_date_range = st.selectbox("Período:", list(date_options.keys()))
        start_date, end_date = date_options[selected_date_range]

    with filter_cols[1]:
        # Filtro de Contas
        account_options = {"Todas as Contas": "all", **{acc['account_name']: acc['doc_id'] for acc in accounts}}
        selected_account_name = st.selectbox("Conta:", list(account_options.keys()))
        selected_account_id = account_options[selected_account_name]

    with filter_cols[2]:
        # Filtro de Ativos
        available_assets = sorted(df_journal_all['asset'].unique().tolist())
        selected_assets = st.multiselect("Ativo(s):", ["Todos"] + available_assets, default="Todos")

    with filter_cols[3]:
        # Filtro de Setups
        available_setups = [s['setup_name'] for s in setups]
        selected_setups = st.multiselect("Setup(s):", ["Todos"] + available_setups, default="Todos")

# --- LÓGICA DE FILTRAGEM ---
df_filtered = df_journal_all.copy()

# Aplica filtro de data
if start_date and end_date:
    df_filtered = df_filtered[(df_filtered['trade_date'] >= pd.to_datetime(start_date)) & (df_filtered['trade_date'] <= pd.to_datetime(end_date))]
# Aplica filtro de conta
if selected_account_id != "all":
    df_filtered = df_filtered.explode('accounts')
    df_filtered = df_filtered[df_filtered['accounts'] == selected_account_id]
# Aplica filtro de ativos
if "Todos" not in selected_assets:
    df_filtered = df_filtered[df_filtered['asset'].isin(selected_assets)]
# Aplica filtro de setups
if "Todos" not in selected_setups:
    df_filtered = df_filtered[df_filtered['selected_setup'].isin(selected_setups)]

# --- CÁLCULO DAS MÉTRICAS COM DADOS FILTRADOS ---
if df_filtered.empty:
    st.warning("Nenhuma operação encontrada com os filtros selecionados."); st.stop()

dashboard_data = calculate_dashboard_metrics(df_filtered, setups)
kpis = dashboard_data["kpis"]

if kpis["total_trades"] == 0:
    st.warning("Nenhuma operação finalizada encontrada com os filtros selecionados."); st.stop()

st.markdown("---")
st.subheader(f"Resultados para a Seleção ({kpis['total_trades']} operações)")

# --- RENDERIZAÇÃO DOS RESULTADOS FILTRADOS ---
kpi_cols = st.columns(4)
kpi_cols[0].metric("Resultado Líquido (USD)", f"${kpis['total_pnl']:,.2f}")
kpi_cols[1].metric("Taxa de Acerto", f"{kpis['win_rate']:.2f}%")
kpi_cols[2].metric("R/R Médio", f"1 : {kpis['avg_rr_ratio']:.2f}")
kpi_cols[3].metric("Expectativa", f"${kpis['expectancy']:,.2f}")

st.markdown("---")
st.subheader("Tabela de Operações Filtradas")

# Prepara a tabela de trades para exibição
recent_trades_filtered = dashboard_data["recent_trades"] # O motor já nos dá isto
st.dataframe(
    recent_trades_filtered,
    use_container_width=True,
    hide_index=True,
    column_config={
        "PnL (USD)": st.column_config.NumberColumn(format="$%.2f"),
        "RR": st.column_config.NumberColumn(format="1:%.2f")
    }
)


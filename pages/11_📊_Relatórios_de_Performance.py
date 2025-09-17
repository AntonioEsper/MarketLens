# synapse_desk/pages/11_📊_Relatórios_de_Performance.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from view_utils import setup_sidebar
from utils.journal_utils import get_journal_entries
from utils.reporting_engine import calculate_performance_metrics

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Relatórios de Performance")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("📊 Relatórios de Performance")
st.caption("Analise os seus resultados, identifique os seus pontos fortes e fracos, e evolua como trader.")
st.markdown("---")

# --- LÓGICA DA PÁGINA ---
user_id = st.session_state['user_info'].get('localId')
if not user_id:
    st.error("Não foi possível identificar o utilizador. Por favor, faça o login novamente.")
    st.stop()

# --- Carregamento e Processamento dos Dados ---
with st.spinner("A carregar e a analisar o seu histórico de operações..."):
    df_journal = get_journal_entries(user_id)
    
    if df_journal.empty:
        st.info("Ainda não há operações registadas para analisar.")
        st.stop()
        
    metrics, equity_curve = calculate_performance_metrics(df_journal)

if equity_curve.empty:
    st.info("Ainda não há operações finalizadas para gerar um relatório de performance.")
    st.stop()

# --- Exibição das Métricas Principais (KPIs) ---
st.header("Métricas Chave de Performance (KPIs)")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Resultado Líquido (PnL)", f"${metrics['total_pnl']:,.2f}")
    st.metric("Total de Operações Finalizadas", f"{metrics['total_trades']}")
with col2:
    st.metric("Taxa de Acerto (Win Rate)", f"{metrics['win_rate']:.2f}%")
    st.metric("Lucro Médio por Operação", f"${metrics['avg_win']:,.2f}")
with col3:
    # CORREÇÃO: Rótulo e formatação atualizados para a nova métrica
    st.metric("Retorno/Risco Médio (R/R)", f"1 : {metrics['profit_factor']:.2f}")
    st.metric("Prejuízo Médio por Operação", f"${metrics['avg_loss']:,.2f}")
    
st.markdown("---")

# --- Gráfico da Curva de Capital ---
st.header("Curva de Capital")
st.caption("Evolução do seu resultado acumulado ao longo do tempo.")

fig_equity = go.Figure()

fig_equity.add_trace(go.Scatter(
    x=list(range(1, len(equity_curve) + 1)),
    y=equity_curve.values, 
    mode='lines+markers',
    marker=dict(color='cyan', size=8),
    fill='tozeroy', 
    name='Capital',
    line=dict(color='cyan', width=2),
    fillcolor='rgba(0, 255, 255, 0.2)'
))

fig_equity.update_layout(
    plot_bgcolor='#131722',
    paper_bgcolor='#131722',
    font_color='white',
    xaxis_title='Número da Operação',
    yaxis_title='Resultado Acumulado (USD)',
    height=500
)

st.plotly_chart(fig_equity, use_container_width=True)


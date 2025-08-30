# pages/2_📈_Dashboard_Macro.py

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import streamlit.components.v1 as components

# --- VERIFICAÇÃO DE AUTENTICAÇÃO E CONFIGURAÇÃO DA BARRA LATERAL ---
if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login para aceder a esta página.")
    st.info("Navegue para a página 'Login' no menu à esquerda.")
    st.stop()

from view_utils import setup_sidebar
setup_sidebar()

# --- IMPORTAÇÕES DOS NOSSOS MÓDULOS ---
from utils.config import yahoo_finance_map, cot_market_map
from utils.data_loader import get_yfinance_data, get_cot_data
from utils.components import create_simple_line_chart
from utils.analysis import calculate_global_risk_gauge

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(layout="wide", page_title="Dashboard Macro")

# --- CABEÇALHO ---
st.title("📈 Dashboard Macroeconómico")
st.caption("A sua central de análise para a tomada de decisões.")
st.markdown("---")

# --- BARRA LATERAL: SELEÇÃO DE ATIVOS ---
with st.sidebar:
    st.markdown("---")
    st.header("Seleção de Ativo")
    lista_ativos = list(yahoo_finance_map.keys())
    ativo_selecionado = st.selectbox("Selecione o Ativo para Análise:", lista_ativos, index=lista_ativos.index("EUR/USD"))
    st.markdown("---")

# --- FUNÇÃO HELPER ---
def calculate_change(data_series):
    if data_series is None or len(data_series) < 2: return None, None
    latest_value = data_series.iloc[-1]
    previous_value = data_series.iloc[-2]
    change = ((latest_value - previous_value) / previous_value) * 100
    return latest_value, change

# --- WIDGET 1: GRÁFICO PRINCIPAL ---
ticker_selecionado = yahoo_finance_map.get(ativo_selecionado)
if ticker_selecionado:
    dados_ativo = get_yfinance_data(ticker_selecionado, period="2y") 
    if not dados_ativo.empty:
        dados_series = dados_ativo.iloc[:, 0] if isinstance(dados_ativo, pd.DataFrame) else dados_ativo
        latest_price, daily_change = calculate_change(dados_series)

        col_title, col_metric = st.columns([3, 1])
        with col_title:
            st.header(f"Análise para: {ativo_selecionado}")
        if latest_price is not None and daily_change is not None:
            with col_metric:
                st.metric("Última Cotação", f"{latest_price:,.4f}", f"{daily_change:.2f}% (D-1)")

        fig_principal = create_simple_line_chart(dados_series, "", yaxis_title="Preço", height=500)
        st.plotly_chart(fig_principal, use_container_width=True)
    else:
        st.warning("Não foi possível carregar os dados para o gráfico principal.")

st.markdown("---")

# --- WIDGET 2: O TRIO MACRO E O MEDIDOR DE RISCO (LAYOUT CORRIGIDO) ---
st.header("Contexto Macroeconómico Chave")

trio_macro_map = {"VIX": "^VIX", "DXY": "DX-Y.NYB", "US10Y": "^TNX"}
trio_macro_tickers = list(trio_macro_map.values())
dados_macro = get_yfinance_data(trio_macro_tickers, period="1y")

if not dados_macro.empty:
    # REQUISITO: Reduzido o medidor de risco para ser menor que os outros 3
    col1, col2, col3, col4 = st.columns([2, 3, 3, 3])
    
    with col1: # O Medidor de Risco
        st.subheader("Risco Global")
        risk_score, risk_verdict = calculate_global_risk_gauge(dados_macro['^VIX'].dropna(), dados_macro['DX-Y.NYB'].dropna())
        
        gauge_color = "#4caf50" # Verde (Risk-On)
        if "Neutro" in risk_verdict: gauge_color = "#ffc107" # Amarelo
        elif "Risk-Off" in risk_verdict: gauge_color = "#f44336" # Vermelho
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = risk_score,
            title = {'text': risk_verdict, 'font': {'size': 24}},
            gauge = {
                'axis': {'range': [-2, 2], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': gauge_color},
                'steps' : [
                     {'range': [-2, -1.5], 'color': 'rgba(244, 67, 54, 0.7)'},
                     {'range': [1.5, 2], 'color': 'rgba(76, 175, 80, 0.7)'}]
            }))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor='#131722', font_color='white')
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2: # VIX
        latest_vix, change_vix = calculate_change(dados_macro['^VIX'].dropna())
        st.metric("VIX", f"{latest_vix:.2f}", f"{change_vix:.2f}%")
        fig_vix = create_simple_line_chart(dados_macro['^VIX'].dropna(), "", color='#f44336', height=150)
        st.plotly_chart(fig_vix, use_container_width=True)
    with col3: # DXY
        latest_dxy, change_dxy = calculate_change(dados_macro['DX-Y.NYB'].dropna())
        st.metric("DXY", f"{latest_dxy:.2f}", f"{change_dxy:.2f}%")
        fig_dxy = create_simple_line_chart(dados_macro['DX-Y.NYB'].dropna(), "", color='#4caf50', height=150)
        st.plotly_chart(fig_dxy, use_container_width=True)
    with col4: # US10Y
        latest_us10y, change_us10y = calculate_change(dados_macro['^TNX'].dropna())
        st.metric("US10Y", f"{latest_us10y:.3f}%", f"{change_us10y:.2f}%")
        fig_us10y = create_simple_line_chart(dados_macro['^TNX'].dropna(), "", color='#2196f3', height=150)
        st.plotly_chart(fig_us10y, use_container_width=True)
else:
    st.warning("Não foi possível carregar os dados para o contexto macroeconómico.")

st.markdown("---")

# --- WIDGETS 3 E 4: ANÁLISE APROFUNDADA (SAZONALIDADE E COT) RESTAURADOS ---
st.header("Análise Aprofundada")
tab1, tab2 = st.tabs(["📊 Sazonalidade Anual", "📉 Posicionamento (COT)"])

with tab1:
    st.subheader(f"Comparativo de Performance Anual para {ativo_selecionado}")
    if ticker_selecionado:
        dados_sazonais = get_yfinance_data(ticker_selecionado, start="2018-01-01")
        if not dados_sazonais.empty:
            dados_series = dados_sazonais.iloc[:, 0] if isinstance(dados_sazonais, pd.DataFrame) else dados_sazonais
            dados_series.index = pd.to_datetime(dados_series.index)
            dados_anuais = dados_series.groupby(dados_series.index.year)
            
            fig_sazonalidade = go.Figure()
            current_year = datetime.now().year
            
            for year, data in dados_anuais:
                normalized_data = (data / data.iloc[0]) * 100
                fig_sazonalidade.add_trace(go.Scatter(
                    x=normalized_data.index.dayofyear, y=normalized_data, mode='lines', name=str(year),
                    line=dict(width=4 if year == current_year else 2)
                ))
            fig_sazonalidade.update_layout(
                title_text="Performance Anual Normalizada (Início do Ano = 100)",
                plot_bgcolor='#131722', paper_bgcolor='#131722', font_color='#D9D9D9'
            )
            st.plotly_chart(fig_sazonalidade, use_container_width=True)
        else:
            st.warning("Dados de sazonalidade não disponíveis.")

with tab2:
    st.subheader("Posicionamento dos Especuladores (Não-Comerciais)")
    st.warning("⚠️ Módulo em manutenção.")
    st.info("Estamos a trabalhar na implementação de uma nova fonte de dados mais robusta para o relatório COT, de forma a garantir a estabilidade da plataforma. A funcionalidade será restaurada em breve.")

st.markdown("---")

# --- NOVO WIDGET: VISÃO GERAL DO MERCADO (TRADINGVIEW) ---


st.header("Calendário Económico da Semana")
st.info("Eventos filtrados para alta importância (3 estrelas).")
components.html("""
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  {
    "colorTheme": "dark",
    "isTransparent": true,
    "width": "100%",
    "height": "600",
    "locale": "br",
    "importanceFilter": "1",
    "currencyFilter": "USD,EUR,GBP,JPY,AUD,CAD,CHF,CNY"
  }
  </script>
</div>
""", height=620)

with st.sidebar:
    st.markdown("### Logo MarketLens") # Placeholder para a logo
    st.title("MarketLens")
    st.caption(f"Versão 17.1 | Synapse Labs")
    st.markdown("---") # Adiciona uma linha divisória

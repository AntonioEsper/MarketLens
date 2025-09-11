# pages/2_📈_Dashboard_Macro.py

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# --- VERIFICAÇÃO DE AUTENTICAÇÃO E CONFIGURAÇÃO DA BARRA LATERAL ---
if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login para aceder a esta página.")
    st.info("Navegue para a página 'Login' no menu à esquerda.")
    st.stop()

from view_utils import setup_sidebar
setup_sidebar()

# --- IMPORTAÇÕES DOS NOSSOS MÓDULOS ---
# ALTERAÇÃO: Importa também a nova estrutura ASSET_CATEGORIES
from utils.config import yahoo_finance_map, cot_market_map, ASSET_CATEGORIES
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
# ***** INÍCIO DA ÚNICA ALTERAÇÃO *****
with st.sidebar:
    st.markdown("---")
    st.header("Seleção de Ativo")

    # Cria a lista de opções a partir da nova estrutura de categorias
    options_list = []
    for category, assets in ASSET_CATEGORIES.items():
        options_list.append(category)
        options_list.extend(assets)

    # Função para formatar a exibição dos títulos
    def format_asset_display(option):
        if option.startswith("---"):
            return f"--- {option.strip('- ')} ---"
        return option

    ativo_selecionado = st.selectbox(
        "Selecione o Ativo para Análise:",
        options=options_list,
        format_func=format_asset_display,
        index=1  # Padrão EUR/USD
    )

    # Se o utilizador selecionar um título, a aplicação para e pede para selecionar um ativo
    if ativo_selecionado.startswith("---"):
        st.warning("Por favor, selecione um ativo válido para análise.")
        st.stop()
    st.markdown("---")
# ***** FIM DA ÚNICA ALTERAÇÃO *****


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

st.markdown("---")

# --- WIDGET 2: O TRIO MACRO E O MEDIDOR DE RISCO ---
st.header("Contexto Macroeconómico Chave")

trio_macro_map = {"VIX": "^VIX", "DXY": "DX-Y.NYB", "US10Y": "^TNX"}
trio_macro_tickers = list(trio_macro_map.values())
dados_macro = get_yfinance_data(trio_macro_tickers, period="1y")

if not dados_macro.empty:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Medidor de Risco Global")
        risk_score, risk_verdict = calculate_global_risk_gauge(dados_macro['^VIX'].dropna(), dados_macro['DX-Y.NYB'].dropna())

        gauge_color = "#4caf50"
        if "Neutro" in risk_verdict: gauge_color = "#ffc107"
        elif "Risk-Off" in risk_verdict: gauge_color = "#f44336"

        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = risk_score,
            title = {'text': risk_verdict, 'font': {'size': 24}},
            gauge = {'axis': {'range': [-2, 2]}, 'bar': {'color': gauge_color}}
        ))
        fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=60, b=20), paper_bgcolor='#131722', font_color='white')
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col2:
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            latest_vix, change_vix = calculate_change(dados_macro['^VIX'].dropna())
            st.metric("VIX", f"{latest_vix:.2f}", f"{change_vix:.2f}%")
            fig_vix = create_simple_line_chart(dados_macro['^VIX'].dropna(), "", color='#f44336', height=150)
            st.plotly_chart(fig_vix, use_container_width=True)
        with subcol2:
            latest_dxy, change_dxy = calculate_change(dados_macro['DX-Y.NYB'].dropna())
            st.metric("DXY", f"{latest_dxy:.2f}", f"{change_dxy:.2f}%")
            fig_dxy = create_simple_line_chart(dados_macro['DX-Y.NYB'].dropna(), "", color='#4caf50', height=150)
            st.plotly_chart(fig_dxy, use_container_width=True)
        with subcol3:
            latest_us10y, change_us10y = calculate_change(dados_macro['^TNX'].dropna())
            st.metric("US10Y", f"{latest_us10y:.3f}%", f"{change_us10y:.2f}%")
            fig_us10y = create_simple_line_chart(dados_macro['^TNX'].dropna(), "", color='#2196f3', height=150)
            st.plotly_chart(fig_us10y, use_container_width=True)

st.markdown("---")

# --- WIDGETS 3 E 4: ANÁLISE APROFUNDADA ---
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

with tab2:
    st.subheader(f"Posicionamento Institucional vs. Varejo para {ativo_selecionado}")

    # Usa o novo cot_market_map para obter o CÓDIGO do contrato
    cot_contract_code = cot_market_map.get(ativo_selecionado)
    if cot_contract_code:
        # Passa o CÓDIGO para a nova função get_cot_data
        dados_cot = get_cot_data(cot_contract_code, years=2)

        if dados_cot is not None and not dados_cot.empty:
            latest_report = dados_cot.iloc[-1]

            net_noncomm = latest_report['noncomm_long'] - latest_report['noncomm_short']
            net_nonrept = latest_report['nonrept_long'] - latest_report['nonrept_short']

            col1_cot, col2_cot = st.columns(2)
            with col1_cot:
                st.metric("Pos. Líquida Institucional", f"{net_noncomm:,.0f}")
                st.metric("Pos. Líquida Varejo", f"{net_nonrept:,.0f}")

                with st.container(border=True):
                    st.subheader("💡 Synapse Insight")
                    if net_noncomm > 0 and net_nonrept < 0:
                        insight = "O dinheiro institucional está otimista (comprado), enquanto o varejo está pessimista (vendido). Este é um forte sinal de continuação da tendência."
                    elif net_noncomm < 0 and net_nonrept > 0:
                        insight = "O dinheiro institucional está pessimista (vendido), enquanto o varejo está otimista (comprado). Este é um forte sinal de alerta de reversão."
                    else:
                        insight = "Não há uma divergência clara entre o posicionamento."
                    st.markdown(insight)
            
            with col2_cot:
                labels = ['Institucional (Long)', 'Institucional (Short)', 'Varejo (Long)', 'Varejo (Short)']
                values = [
                    latest_report['noncomm_long'], latest_report['noncomm_short'],
                    latest_report['nonrept_long'], latest_report['nonrept_short']
                ]
                colors = ['#2ca02c', '#d62728', '#1f77b4', '#ff7f0e']

                fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, marker_colors=colors, hole=.4)])
                fig_pie.update_layout(title_text="Composição do Open Interest", plot_bgcolor='#131722', paper_bgcolor='#131722', font_color='#D9D9D9')
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("Não foi possível carregar os dados de posicionamento (COT) para este ativo.")


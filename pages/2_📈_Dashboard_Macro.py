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

# --- IMPORTAÇÕES DOS NOSSOS MÓDUTLOS ---
from utils.config import yahoo_finance_map, cot_market_map, ASSET_CATEGORIES
from utils.data_loader import get_yfinance_data, get_cot_data
from utils.components import create_simple_line_chart
from utils.analysis import calculate_global_risk_gauge
from utils.plot_utils import prepare_seasonality_data_for_lines, calculate_cot_percentages, style_cot_table

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

    options_list = []
    for category, assets in ASSET_CATEGORIES.items():
        options_list.append(category)
        options_list.extend(assets)

    def format_asset_display(option):
        if option.startswith("---"):
            return f"--- {option.strip('- ')} ---"
        return option

    ativo_selecionado = st.selectbox(
        "Selecione o Ativo para Análise:",
        options=options_list,
        format_func=format_asset_display,
        index=1
    )

    if ativo_selecionado.startswith("---"):
        st.warning("Por favor, selecione um ativo válido para análise.")
        st.stop()
    st.markdown("---")

# --- FUNÇÃO HELPER ---
def calculate_change(data_series):
    if data_series is None or data_series.empty or len(data_series) < 2: return None, None
    # Garante que estamos a trabalhar com valores numéricos
    data_series = pd.to_numeric(data_series, errors='coerce').dropna()
    if len(data_series) < 2: return None, None
    latest_value = data_series.iloc[-1]
    previous_value = data_series.iloc[-2]
    change = ((latest_value - previous_value) / previous_value) * 100
    return latest_value, change

# --- WIDGET 1: GRÁFICO PRINCIPAL ---
ticker_selecionado = yahoo_finance_map.get(ativo_selecionado)
if ticker_selecionado:
    dados_ativo_completo = get_yfinance_data(ticker_selecionado, period="5y")
    
    if not dados_ativo_completo.empty:
        # CORREÇÃO: Garante que estamos sempre a trabalhar com uma Série (coluna única) para os preços de fecho.
        dados_series_close = dados_ativo_completo.iloc[:, 0]
        
        latest_price, daily_change = calculate_change(dados_series_close)

        col_title, col_metric = st.columns([3, 1])
        with col_title:
            st.header(f"Análise para: {ativo_selecionado}")
        if latest_price is not None and daily_change is not None:
            with col_metric:
                st.metric("Última Cotação", f"{float(latest_price):,.4f}", f"{float(daily_change):.2f}% (D-1)")
        
        # CORREÇÃO: Lógica simplificada para garantir que o gráfico de linha seja sempre renderizado.
        st.subheader("Gráfico de Preços")
        fig_principal = go.Figure()
        fig_principal.add_trace(go.Scatter(
            x=dados_series_close.index,
            y=dados_series_close,
            mode='lines',
            name=ativo_selecionado,
            line=dict(color="#f6e33b", width=2)
        ))
        fig_principal.update_layout(
            height=500,
            plot_bgcolor='#131722',
            paper_bgcolor='#131722',
            font_color='white',
            yaxis_title='Preço',
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig_principal, use_container_width=True)

st.markdown("---")


# --- WIDGET 2: O TRIO MACRO E O MEDIDOR DE RISCO ---
st.header("Contexto Macroeconómico Chave")
trio_macro_map = {"VIX": "^VIX", "DXY": "DX-Y.NYB", "US10Y": "^TNX"}
trio_macro_tickers = list(trio_macro_map.values())
dados_macro = get_yfinance_data(trio_macro_tickers, period="1y")

if dados_macro is not None and not dados_macro.empty and all(ticker in dados_macro.columns for ticker in trio_macro_map.values()):
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
else:
    st.warning("Não foi possível carregar os dados do Trio Macroeconómico (VIX, DXY, US10Y). Tente atualizar a página.")
st.markdown("---")

# --- WIDGETS 3 E 4: ANÁLISE APROFUNDADA ---
st.header("Análise Aprofundada")
tab1, tab2 = st.tabs(["📊 Sazonalidade Anual", "📉 Posicionamento (COT)"])

with tab1:
    st.subheader(f"Comparativo de Performance Mensal para {ativo_selecionado}")
    st.caption("Variação percentual do preço, normalizada para cada ano.")
    
    df_seasonality_lines = prepare_seasonality_data_for_lines(dados_ativo_completo)
    if not df_seasonality_lines.empty:
        fig_season = go.Figure()
        current_year = datetime.now().year
        for year in df_seasonality_lines.columns:
            fig_season.add_trace(go.Scatter(
                x=df_seasonality_lines.index,
                y=df_seasonality_lines[year],
                mode='lines',
                name=str(year),
                line=dict(width=4 if year == current_year else 2, dash='solid' if year == current_year else 'dash')
            ))
        fig_season.update_layout(
            plot_bgcolor='#131722', paper_bgcolor='#131722', font_color='#D9D9D9',
            legend_title_text='Ano', yaxis_title="Variação %"
        )
        st.plotly_chart(fig_season, use_container_width=True)
    else:
        st.warning("Não foi possível calcular a sazonalidade para este ativo.")

with tab2:
    st.subheader(f"Análise de Posicionamento para {ativo_selecionado}")
    cot_contract_code = cot_market_map.get(ativo_selecionado)
    if cot_contract_code:
        dados_cot = get_cot_data(cot_contract_code, years=3)
        if dados_cot is not None and not dados_cot.empty:
            
            st.markdown("##### Evolução das Posições Compradoras (Long)")
            fig_cot_lines = go.Figure()
            fig_cot_lines.add_trace(go.Scatter(
                x=dados_cot.index, y=dados_cot['noncomm_long'],
                mode='lines', name='Institucional Long', line=dict(color='cyan')
            ))
            fig_cot_lines.add_trace(go.Scatter(
                x=dados_cot.index, y=dados_cot['nonrept_long'],
                mode='lines', name='Varejo Long', line=dict(color='magenta')
            ))
            fig_cot_lines.update_layout(height=400, plot_bgcolor='#131722', paper_bgcolor='#131722', font_color='#D9D9D9', legend_title_text='Player')
            st.plotly_chart(fig_cot_lines, use_container_width=True)
            st.markdown("---")

            st.markdown("##### Análise de Divergência Percentual (Último Relatório)")
            if "/" in ativo_selecionado:
                base_currency, quote_currency = ativo_selecionado.split('/')
                df_base_pct = calculate_cot_percentages(dados_cot)
                
                dados_cot_quote = get_cot_data(cot_market_map.get(quote_currency, cot_market_map.get("DXY")))
                df_quote_pct = calculate_cot_percentages(dados_cot_quote) if dados_cot_quote is not None else pd.DataFrame()

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**{base_currency}**")
                    if not df_base_pct.empty:
                        st.dataframe(df_base_pct.style.format("{:.2f}%").apply(lambda x: x.map(style_cot_table), axis=None), use_container_width=True)
                    else:
                        st.warning(f"Dados indisponíveis para {base_currency}")
                with col2:
                    st.markdown(f"**{quote_currency}**")
                    if not df_quote_pct.empty:
                        st.dataframe(df_quote_pct.style.format("{:.2f}%").apply(lambda x: x.map(style_cot_table), axis=None), use_container_width=True)
                    else:
                        st.warning(f"Dados indisponíveis para {quote_currency}")
            else:
                df_asset_pct = calculate_cot_percentages(dados_cot)
                if not df_asset_pct.empty:
                    st.dataframe(df_asset_pct.style.format("{:.2f}%").apply(lambda x: x.map(style_cot_table), axis=None), use_container_width=True)
                else:
                    st.warning(f"Não foi possível calcular a tabela para {ativo_selecionado}")
        else:
            st.warning("Não foi possível carregar os dados de posicionamento (COT) para este ativo.")
    else:
        st.info(f"O ativo {ativo_selecionado} não possui dados de posicionamento (COT) disponíveis.")


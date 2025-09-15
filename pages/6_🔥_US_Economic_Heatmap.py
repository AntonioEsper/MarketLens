# marketlens/pages/6_🔥_US_Economic_Heatmap.py

import streamlit as st
import pandas as pd
from view_utils import setup_sidebar
from utils.heatmap_engine import get_momentum_heatmap_data
# Importa as novas funções e configurações necessárias
from utils.scoring_engine import get_economic_data_from_firestore
from utils.config import FRED_SERIES_MAP
from utils.plot_utils import create_indicator_bar_chart

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="US Economic Heatmap")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("🔥 US Economic Momentum Heatmap")
st.caption("Análise da tendência dos principais indicadores económicos dos EUA e o seu impacto no USD e em Ações (Stocks).")
st.markdown("---")

# --- LÓGICA DO HEATMAP ---
with st.spinner("A carregar e a analisar o momentum económico..."):
    df_heatmap = get_momentum_heatmap_data()

if not df_heatmap.empty:
    
    def style_impact(impact_text):
        if "Bullish" in impact_text: return 'background-color: #006400; color: white;'
        elif "Bearish" in impact_text: return 'background-color: #8B0000; color: white;'
        return 'background-color: #424242; color: white;'

    def style_trend(trend_text):
        if "Acima" in trend_text: return 'color: #4caf50;'
        elif "Abaixo" in trend_text: return 'color: #f44336;'
        return ''

    display_columns = {"Indicador": "Indicador", "Último Valor": "Último Valor", "Data": "Data",
                       "Tendência": "Tendência (vs. Média 12M)", "Impacto USD": "Impacto USD", "Impacto Stocks": "Impacto Stocks"}
    df_display = df_heatmap[[col for col in display_columns.keys() if col in df_heatmap.columns]].rename(columns=display_columns)

    st.subheader("Resumo Estatístico do Impacto")
    col1, col2, col3 = st.columns(3)
    bullish_pct_usd = (df_heatmap['Impacto USD'] == 'Bullish').sum() / len(df_heatmap) * 100
    bearish_pct_usd = (df_heatmap['Impacto USD'] == 'Bearish').sum() / len(df_heatmap) * 100
    bullish_pct_stocks = (df_heatmap['Impacto Stocks'] == 'Bullish').sum() / len(df_heatmap) * 100
    bearish_pct_stocks = (df_heatmap['Impacto Stocks'] == 'Bearish').sum() / len(df_heatmap) * 100

    with col1:
        st.metric("Impacto Bullish (USD)", f"{bullish_pct_usd:.1f}%")
        st.metric("Impacto Bullish (Stocks)", f"{bullish_pct_stocks:.1f}%")
    with col2:
        st.metric("Impacto Neutro (USD)", f"{100 - bullish_pct_usd - bearish_pct_usd:.1f}%")
        st.metric("Impacto Neutro (Stocks)", f"{100 - bullish_pct_stocks - bearish_pct_stocks:.1f}%")
    with col3:
        st.metric("Impacto Bearish (USD)", f"{bearish_pct_usd:.1f}%")
        st.metric("Impacto Bearish (Stocks)", f"{bearish_pct_stocks:.1f}%")

    st.markdown("---")
    st.subheader("Tabela de Análise de Momentum")
    styled_df = df_display.style.apply(lambda x: x.map(style_impact), subset=['Impacto USD', 'Impacto Stocks'])\
                                .apply(lambda x: x.map(style_trend), subset=['Tendência (vs. Média 12M)'])\
                                .format({"Último Valor": "{:,.2f}"})
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # --- NOVA SECÇÃO: ANÁLISE INDIVIDUAL DE INDICADORES ---
    st.markdown("---")
    st.header("Análise Individual de Indicadores")
    
    us_indicators_list = [name for name, info in FRED_SERIES_MAP.items() if info["currency"] == "USD"]
    selected_indicator = st.selectbox("Selecione um indicador para análise detalhada:", us_indicators_list)

    if selected_indicator:
        series_id = FRED_SERIES_MAP[selected_indicator]['id']
        with st.spinner(f"A carregar histórico para {selected_indicator}..."):
            series_data = get_economic_data_from_firestore(series_id)
            
            # Chama a nossa "fábrica" de gráficos a partir do plot_utils
            fig = create_indicator_bar_chart(series_data, selected_indicator)
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Não há dados históricos suficientes para gerar o gráfico de {selected_indicator}.")

else:
    st.error("Não foi possível gerar o Heatmap. Verifique se o motor de dados económicos foi executado com sucesso.")

# --- FIM DO FICHEIRO ---
# marketlens/pages/6_🔥_US_Economic_Heatmap.py

import streamlit as st
import pandas as pd
from view_utils import setup_sidebar
from utils.heatmap_engine import get_momentum_heatmap_data # Importa a nossa nova função de motor

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="US Economic Heatmap")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("🔥 US Economic Momentum Heatmap")
st.caption("Análise da tendência dos principais indicadores económicos dos EUA.")
st.markdown("---")

# --- LÓGICA DO HEATMAP ---
with st.spinner("A carregar e a analisar o momentum económico..."):
    df_heatmap = get_momentum_heatmap_data()

if not df_heatmap.empty:
    
    # --- Lógica de Estilização ---
    def style_impact(impact_text):
        """Aplica cores à célula de Impacto."""
        if "Bullish" in impact_text:
            return 'background-color: #006400; color: white;'
        elif "Bearish" in impact_text:
            return 'background-color: #8B0000; color: white;'
        return ''

    def style_trend(trend_text):
        """Aplica cores à célula de Tendência."""
        if "Acima" in trend_text:
            return 'color: #4caf50;'
        elif "Abaixo" in trend_text:
            return 'color: #f44336;'
        return ''

    # Aplica a estilização ao DataFrame
    styled_df = df_heatmap.style.apply(
        lambda x: x.map(style_impact), subset=['Impacto']
    ).apply(
        lambda x: x.map(style_trend), subset=['Tendência (vs. Média 12M)']
    ).format({
        "Último Valor": "{:,.2f}"
    })

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

else:
    st.error("Não foi possível gerar o Heatmap. Verifique se o motor de dados económicos foi executado com sucesso.")


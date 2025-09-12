# marketlens/pages/10_🧪_DEV_Economic_Data.py
# NOTA: Esta é uma página temporária para desenvolvimento e teste do Sprint 1.
# Será removida ou integrada noutra secção no futuro.

import streamlit as st
from view_utils import setup_sidebar
import plotly.graph_objects as go

# --- IMPORTAÇÕES DOS NOVOS MÓDULOS DO SPRINT 1 ---
from utils.config import FRED_SERIES_MAP
from utils.economic_loader import get_economic_data

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="DEV | Dados Económicos")
setup_sidebar()

# Guarda de autenticação
if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CONTEÚDO DA PÁGINA DE TESTE ---
st.title("🧪 Teste do Carregador de Dados Económicos (Sprint 1)")
st.warning("Esta página é destinada apenas para fins de desenvolvimento e validação.")
st.markdown("---")

st.header("Seletor de Indicador Macroeconómico")
st.write(
    "Selecione um indicador da lista abaixo. Na primeira vez que carregar um indicador, "
    "os dados serão buscados da API do FRED (pode demorar um pouco). Nas vezes seguintes, "
    "os dados serão lidos instantaneamente do nosso cache no Firestore."
)

# Cria uma lista de nomes amigáveis para o seletor
series_options = list(FRED_SERIES_MAP.keys())
selected_series_name = st.selectbox("Selecione a série de dados:", options=series_options)

if selected_series_name:
    # Obtém o ID da série a partir do nosso mapa de configuração
    series_id = FRED_SERIES_MAP[selected_series_name]['id']
    
    # Botão para iniciar o carregamento dos dados
    if st.button(f"Carregar Dados para {selected_series_name}"):
        with st.spinner(f"A carregar dados para {series_id}..."):
            # Chama a nossa nova função principal
            df_economic_data = get_economic_data(
                series_name=selected_series_name,
                series_id=series_id
            )

        if df_economic_data is not None and not df_economic_data.empty:
            st.success(f"Dados para '{selected_series_name}' carregados com sucesso!")
            
            # Exibe os dados num gráfico interativo
            st.subheader("Gráfico Histórico")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_economic_data.index,
                y=df_economic_data['value'],
                mode='lines',
                name=selected_series_name
            ))
            fig.update_layout(
                title=f"Histórico de {selected_series_name}",
                plot_bgcolor='#131722',
                paper_bgcolor='#131722',
                font_color='#D9D9D9'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Exibe os dados brutos numa tabela expansível
            with st.expander("Ver Dados Brutos"):
                st.dataframe(df_economic_data)
        else:
            st.error("Não foi possível carregar os dados. Verifique a consola para mais detalhes.")
# --- FIM DA PÁGINA DE TESTE ---
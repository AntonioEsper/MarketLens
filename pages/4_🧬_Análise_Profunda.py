# marketlens/pages/4_🧬_Análise_Profunda.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from view_utils import setup_sidebar
from utils.config import ASSET_CATEGORIES
from utils.scoring_engine import (
    calculate_synapse_score, 
    get_cot_history_from_firestore,
    get_seasonality_from_firestore
)

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Análise Profunda")
setup_sidebar()

# Guarda de autenticação
if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- TÍTULO E SELEÇÃO DE ATIVO ---
st.title("🧬 Análise Profunda do Ativo")

# Criação da lista de ativos para o seletor
options_list = []
for category, assets in ASSET_CATEGORIES.items():
    options_list.extend(assets)

selected_asset = st.selectbox(
    "Selecione um ativo para analisar:",
    options=options_list,
    index=0
)
st.markdown("---")

# --- LÓGICA PRINCIPAL ---
if selected_asset:
    sanitized_asset_name = selected_asset.replace('/', '_')

    # --- NOVA SECÇÃO: RAIO-X DO SYNAPSE SCORE ---
    st.header(f"Raio-X do Synapse Score para {selected_asset}")
    
    with st.spinner("A calcular o score multifatorial..."):
        total_score, verdict, individual_scores = calculate_synapse_score(selected_asset)

    col1, col2, col3 = st.columns(3)
    col1.metric("Score Final", f"{total_score:+.0f}", verdict)
    
    # Exibe os scores individuais
    cot_score_value = individual_scores.get('COT', {}).get('score', 0)
    cot_score_text = individual_scores.get('COT', {}).get('text', 'N/A')
    col2.metric("Score de Posicionamento (COT)", f"{cot_score_value:+.0f}", cot_score_text)
    
    season_score_value = individual_scores.get('Sazonalidade', {}).get('score', 0)
    season_score_text = individual_scores.get('Sazonalidade', {}).get('text', 'N/A')
    col3.metric("Score de Sazonalidade", f"{season_score_value:+.0f}", season_score_text)
    
    st.markdown("---")

    # --- SECÇÃO DE ANÁLISE DE POSICIONAMENTO (COT) ---
    st.header(f"Análise de Posicionamento (COT) para {selected_asset}")
    with st.spinner("A carregar histórico de posicionamento..."):
        df_cot = get_cot_history_from_firestore(sanitized_asset_name)

    if df_cot is not None and not df_cot.empty:
        fig_cot = go.Figure()
        fig_cot.add_trace(go.Scatter(x=df_cot.index, y=df_cot['noncomm_long'], mode='lines', name='Institucional (Long)', line=dict(color='#2ca02c')))
        fig_cot.add_trace(go.Scatter(x=df_cot.index, y=df_cot['nonrept_long'], mode='lines', name='Varejo (Long)', line=dict(color='#1f77b4', dash='dash')))
        fig_cot.add_trace(go.Scatter(x=df_cot.index, y=df_cot['noncomm_short'], mode='lines', name='Institucional (Short)', line=dict(color='#d62728')))
        fig_cot.add_trace(go.Scatter(x=df_cot.index, y=df_cot['nonrept_short'], mode='lines', name='Varejo (Short)', line=dict(color='#ff7f0e', dash='dash')))
        fig_cot.update_layout(title_text=f"Evolução Histórica do Posicionamento - {selected_asset}", plot_bgcolor='#131722', paper_bgcolor='#131722', font_color='#D9D9D9')
        st.plotly_chart(fig_cot, use_container_width=True)
    else:
        st.info(f"Não foram encontrados dados de posicionamento (COT) para {selected_asset}.")

    st.markdown("---")
    
    # --- NOVA SECÇÃO: ANÁLISE DE SAZONALIDADE ---
    st.header(f"Análise de Sazonalidade para {selected_asset}")
    with st.spinner("A carregar dados de sazonalidade..."):
        df_seasonality = get_seasonality_from_firestore(sanitized_asset_name)

    if df_seasonality is not None and not df_seasonality.empty:
        # Garante que a coluna de retornos seja numérica
        df_seasonality['average_return'] = pd.to_numeric(df_seasonality['average_return'])
        
        # Converte o índice de mês (número) para nome do mês abreviado
        month_names = pd.to_datetime(df_seasonality.index, format='%m').strftime('%b')

        fig_season = go.Figure(data=[go.Bar(
            x=month_names,
            y=df_seasonality['average_return'],
            marker_color=['#2ca02c' if v > 0 else '#d62728' for v in df_seasonality['average_return']]
        )])
        fig_season.update_layout(
            title_text=f"Performance Média Mensal (Últimos 10 Anos) - {selected_asset}",
            xaxis_title="Mês",
            yaxis_title="Retorno Médio (%)",
            plot_bgcolor='#131722', 
            paper_bgcolor='#131722', 
            font_color='#D9D9D9'
        )
        st.plotly_chart(fig_season, use_container_width=True)
    else:
        st.info(f"Não foram encontrados dados de sazonalidade para {selected_asset}.")


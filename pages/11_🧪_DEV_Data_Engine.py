# marketlens/pages/10_🧪_DEV_Data_Engine.py

import streamlit as st
from view_utils import setup_sidebar
from utils.config import FRED_SERIES_MAP, ASSET_CATEGORIES

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="DEV | Motores de Dados")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- INTERFACE DA PÁGINA ---
st.title("🧪 Sala de Controlo e Laboratório de Testes")
st.caption("Esta página é uma ferramenta de desenvolvimento para popular o Firestore e validar a lógica de scoring.")
st.warning("A execução dos motores de dados pode consumir recursos. Use com moderação.")
st.markdown("---")

# --- ABAS PARA ORGANIZAÇÃO ---
tab_engines, tab_scoring_lab = st.tabs(["Motores de Dados", "Laboratório de Scoring"])

with tab_engines:
    st.header("Execução dos Motores de Coleta de Dados")
    
    # --- MOTOR DE DADOS ECONÓMICOS ---
    st.subheader("Motor de Dados Económicos (FRED)")
    if st.button("Executar Atualização de Dados Económicos (FRED)"):
        from utils.economic_engine import update_fred_data_in_firestore
        with st.status("A executar o motor de dados económicos...", expanded=True) as status:
            for message in update_fred_data_in_firestore():
                st.write(message)
            status.update(label="Motor do FRED concluído!", state="complete")

    st.markdown("---")

    # --- MOTOR DE DADOS DE POSICIONAMENTO ---
    st.subheader("Motor de Dados de Posicionamento (COT)")
    if st.button("Executar Atualização de Dados de Posicionamento (COT)"):
        from utils.cot_engine import update_cot_data_in_firestore
        with st.status("A executar o motor de dados do COT...", expanded=True) as status:
            for message in update_cot_data_in_firestore():
                st.write(message)
            status.update(label="Motor do COT concluído!", state="complete")

    st.markdown("---")

    # --- MOTOR DE DADOS DE SAZONALIDADE ---
    st.subheader("Motor de Dados de Sazonalidade")
    if st.button("Executar Cálculo e Armazenamento de Sazonalidade"):
        from utils.seasonality_engine import update_seasonality_data_in_firestore
        with st.status("A executar o motor de sazonalidade...", expanded=True) as status:
            for message in update_seasonality_data_in_firestore():
                st.write(message)
            status.update(label="Motor de sazonalidade concluído!", state="complete")


with tab_scoring_lab:
    st.header("🔬 Laboratório de Testes do Motor de Scoring")
    st.write("Use esta secção para validar a lógica de cálculo dos scores em tempo real.")
    st.markdown("---")

    # Importa as funções de scoring aqui para garantir que a versão mais recente seja usada
    from utils.scoring_engine import calculate_overall_economic_score, calculate_synapse_score
    
    # --- Painel de Teste para Scores Económicos por Moeda ---
    st.subheader("Validação do Score Económico Agregado por Moeda")
    if st.button("Calcular Scores Económicos"):
        currencies = sorted(list(set(info['currency'] for info in FRED_SERIES_MAP.values())))
        with st.spinner("A calcular scores económicos..."):
            for currency in currencies:
                score = calculate_overall_economic_score(currency)
                st.metric(label=f"Score Económico para {currency}", value=f"{score:.2f}")

    st.markdown("---")
    
    # --- Painel de Teste para o Synapse Score de um Ativo ---
    st.subheader("Validação do Synapse Score para um Ativo Específico")
    
    # Cria a lista de ativos a partir do ASSET_CATEGORIES
    asset_options = []
    for category, assets in ASSET_CATEGORIES.items():
        asset_options.extend(assets)
        
    selected_asset = st.selectbox("Selecione um Ativo para Testar:", options=asset_options)
    
    if st.button(f"Calcular Synapse Score para {selected_asset}"):
        with st.spinner(f"A analisar {selected_asset}..."):
            final_score, verdict, individual_scores = calculate_synapse_score(selected_asset)
            
            st.metric(label=f"Score Final para {selected_asset}", value=f"{final_score:.2f}", delta=verdict)
            
            st.write("Scores Individuais:")
            st.json(individual_scores)


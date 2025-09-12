# marketlens/pages/10_🧪_DEV_Data_Engine.py

import streamlit as st
from view_utils import setup_sidebar

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="DEV | Motores de Dados")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- INTERFACE DA PÁGINA ---
st.title("🧪 Sala de Controlo dos Motores de Dados")
st.caption("Esta página é uma ferramenta de desenvolvimento para popular o Firestore.")
st.warning("A execução destes motores pode consumir recursos. Use com moderação.")
st.markdown("---")

# --- MOTOR DE DADOS ECONÓMICOS ---
st.header("Motor de Dados Económicos (FRED)")
if st.button("Executar Atualização de Dados Económicos (FRED)"):
    from utils.economic_engine import update_fred_data_in_firestore
    
    with st.spinner("A conectar ao motor de dados económicos..."):
        # Esta função ainda não foi convertida para um gerador, será executada de uma vez.
        update_fred_data_in_firestore()
    st.success("Processo de atualização dos dados económicos concluído!")

st.markdown("---")

# --- MOTOR DE DADOS DE POSICIONAMENTO (COT) ---
st.header("Motor de Dados de Posicionamento (COT)")
if st.button("Executar Atualização de Dados de Posicionamento (COT)", key="cot_update_button"):
    from utils.cot_engine import update_cot_data_in_firestore
    
    # Usamos st.status para criar uma caixa que se atualiza com o progresso
    with st.status("A executar o motor de dados do COT...", expanded=True) as status:
        # A função agora é um gerador, então iteramos sobre as mensagens que ela emite
        for message in update_cot_data_in_firestore():
            st.write(message) # Exibe cada mensagem de progresso na caixa de status
        
        status.update(label="Motor do COT concluído!", state="complete")

st.markdown("---")

# --- MOTOR DE DADOS DE SAZONALIDADE ---
st.header("Motor de Dados de Sazonalidade")
if st.button("Executar Cálculo e Armazenamento de Sazonalidade"):
    from utils.seasonality_engine import update_seasonality_data_in_firestore
    
    # O motor de sazonalidade também deve ser um gerador para um melhor feedback
    with st.status("A executar o motor de sazonalidade...", expanded=True) as status:
        for message in update_seasonality_data_in_firestore():
            st.write(message)
        status.update(label="Motor de sazonalidade concluído!", state="complete")


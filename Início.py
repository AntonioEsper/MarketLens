# marketlens/Início.py

import streamlit as st
from streamlit import switch_page # Importação explícita
from view_utils import setup_sidebar
from firebase_config import db

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="MarketLens | Início",
    page_icon="🏠",
    layout="wide"
)

# --- GESTÃO DA BARRA LATERAL --
setup_sidebar()

# --- VERIFICAÇÃO DE AUTENTICAÇÃO ---
# ALTERAÇÃO PRINCIPAL: Se o utilizador não estiver logado, redireciona para a página de login.
if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    switch_page("pages/1_👤_Login.py")

# --- CONTEÚDO DA PÁGINA (Só será mostrado se o utilizador estiver logado) ---
st.title(f"🏠 Bem-vindo ao MarketLens, {st.session_state['user_info']['email']}!")
st.markdown("---")
st.header("A sua plataforma de análise de mercado financeiro.")
st.write("Utilize o menu à esquerda para navegar pelas diferentes ferramentas de análise.")

if db:
    st.sidebar.success("Conectado ao MarketLens")
else:
    st.sidebar.error("Falha na conexão com o MarketLens DB")
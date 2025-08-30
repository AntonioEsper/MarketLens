# marketlens/Início.py

import streamlit as st
from view_utils import setup_sidebar # Importação corrigida
from firebase_config import db

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="MarketLens | Início",
    page_icon="🏠",
    layout="wide"
)

# --- GESTÃO DA BARRA LATERAL ---
setup_sidebar()

# --- VERIFICAÇÃO DE AUTENTICAÇÃO ---
if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login para aceder ao conteúdo.")
    st.info("Navegue para a página 'Login' no menu à esquerda para entrar ou criar uma conta.")
    st.stop()

# --- CONTEÚDO DA PÁGINA ---
st.title(f"🏠 Bem-vindo ao MarketLens, {st.session_state['user_info']['email']}!")
st.markdown("---")
st.header("A sua plataforma de análise de mercado financeiro.")
st.write("Utilize o menu à esquerda para navegar pelas diferentes ferramentas de análise.")

if db:
    st.sidebar.success("Conectado ao Firebase")
else:
    st.sidebar.error("Falha na conexão com o Firebase")


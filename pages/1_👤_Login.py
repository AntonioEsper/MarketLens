# marketlens/pages/1_👤_Login.py

import streamlit as st
from firebase_admin import auth
from firebase_config import auth_client
from view_utils import setup_sidebar # Importa a nossa nova função

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="MarketLens | Login",
    page_icon="👤",
    layout="centered"
)

# --- GESTÃO DA BARRA LATERAL ---
# Chama a função para configurar a barra lateral (irá mostrar o botão de logout se estiver logado)
setup_sidebar()

# --- GESTÃO DE ESTADO DA SESSÃO ---
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

# --- INTERFACE ---
if st.session_state['user_info']:
    user_email = st.session_state['user_info'].get('email', 'Email não encontrado')
    st.title(f"👋 Bem-vindo, {user_email}!")
    st.success("Você já está autenticado.")
    st.info("Navegue para outra página usando o menu à esquerda.")

else:
    st.title("👤 Autenticação")
    st.markdown("---")
    tab_login, tab_register = st.tabs(["Entrar", "Registar"])

    with tab_login:
        st.header("Login")
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="seu@email.com")
            password = st.text_input("Palavra-passe", type="password")
            submit_button = st.form_submit_button("Entrar")

            if submit_button:
                if not email or not password:
                    st.error("Por favor, preencha todos os campos.")
                else:
                    try:
                        user = auth_client.sign_in_with_email_and_password(email, password)
                        st.session_state['user_info'] = user
                        # --- MELHORIA: REDIRECIONAMENTO AUTOMÁTICO ---
                        st.switch_page("Início.py")
                    except Exception as e:
                        st.error("Email ou palavra-passe inválidos. Por favor, tente novamente.")
    
    with tab_register:
        # (O código do separador de registo permanece o mesmo)
        st.header("Criar Nova Conta")
        with st.form("register_form"):
            new_email = st.text_input("Email", key="new_email", placeholder="seu@email.com")
            new_password = st.text_input("Palavra-passe", type="password", key="new_password")
            confirm_password = st.text_input("Confirmar Palavra-passe", type="password", key="confirm_password")
            register_button = st.form_submit_button("Registar")

            if register_button:
                if not new_email or not new_password or not confirm_password:
                    st.error("Por favor, preencha todos os campos.")
                elif new_password != confirm_password:
                    st.error("As palavras-passe não coincidem.")
                elif len(new_password) < 6:
                    st.error("A palavra-passe deve ter pelo menos 6 caracteres.")
                else:
                    try:
                        user = auth.create_user(email=new_email, password=new_password)
                        st.success(f"Conta criada com sucesso para o email: {user.email}")
                        st.info("Pode agora fazer login no separador 'Entrar'.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao criar a conta. Verifique se o email já está em uso.")

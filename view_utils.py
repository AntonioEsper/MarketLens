# marketlens/view_utils.py

import streamlit as st

def setup_sidebar():
    """
    Configura a barra lateral com base no estado de autenticação do utilizador.

    Se o utilizador estiver logado, esta função irá:
    1. Ocultar a página de "Login" do menu de navegação.
    2. Adicionar um botão de "Logout" à barra lateral.
    """
    # Verifica se a informação do utilizador existe e não é nula
    if 'user_info' in st.session_state and st.session_state['user_info'] is not None:
        
        # 1. Oculta a página de Login injetando CSS
        st.markdown("""
            <style>
                /* Seleciona o link da barra lateral que contém o nome do ficheiro da página de login */
                a[href*="1_👤_Login"] {
                    display: none; /* Oculta o elemento */
                }
            </style>
        """, unsafe_allow_html=True)
        
        # 2. Adiciona o botão de Logout à barra lateral
        if st.sidebar.button("Logout"):
            # Limpa todas as informações da sessão
            st.session_state.clear()
            # Re-executa o script para atualizar a página e refletir o estado de logout
            st.rerun()

# marketlens/pages/7_👤_Perfil.py

import streamlit as st
from view_utils import setup_sidebar
from utils.profile_utils import get_user_profile, update_user_profile, upload_avatar_to_storage

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Perfil de Utilizador")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("👤 Perfil de Utilizador")
st.caption("Mantenha as suas informações e preferências atualizadas.")
st.markdown("---")

# --- LÓGICA DA PÁGINA ---
user_id = st.session_state['user_info'].get('localId')

if user_id:
    with st.spinner("A carregar perfil..."):
        profile_data = get_user_profile(user_id)

    if profile_data is not None:
        # Extrai os dados existentes, com valores padrão caso não existam
        current_name = profile_data.get("name", "")
        current_bio = profile_data.get("bio", "")
        trader_types = ["Day Trader", "Swing Trader", "Position Trader", "Scalper", "Investidor"]
        current_type = profile_data.get("trader_type", None)
        # Define um avatar padrão se o utilizador ainda não tiver um
        avatar_url = profile_data.get("avatar_url", "https://i.imgur.com/626O2D6.png") 

        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.header("Avatar")
            st.image(avatar_url, width=200)
            
        with col2:
            st.header("Editar Informações")
            with st.form("profile_form"):
                name = st.text_input("Nome Completo", value=current_name)
                bio = st.text_area("Bio / Breve Descrição", value=current_bio, placeholder="Descreva o seu estilo de trading, objetivos, etc.")
                trader_type = st.selectbox("Tipo de Trader Principal", options=trader_types, index=trader_types.index(current_type) if current_type in trader_types else 0)
                
                # Novo campo para upload de imagem
                uploaded_avatar = st.file_uploader("Alterar Avatar", type=["png", "jpg", "jpeg"])

                submit_button = st.form_submit_button("Guardar Alterações")

                if submit_button:
                    new_profile_data = { "name": name, "bio": bio, "trader_type": trader_type }
                    
                    # Lógica para processar a nova imagem
                    if uploaded_avatar is not None:
                        with st.spinner("A fazer o upload do novo avatar..."):
                            avatar_bytes = uploaded_avatar.getvalue()
                            content_type = uploaded_avatar.type
                            new_avatar_url = upload_avatar_to_storage(user_id, avatar_bytes, content_type)
                            
                            if new_avatar_url:
                                new_profile_data["avatar_url"] = new_avatar_url

                    # Atualiza os dados no Firestore
                    success = update_user_profile(user_id, new_profile_data)
                    
                    if success:
                        st.success("Perfil atualizado com sucesso!")
                        st.balloons()
                        # Re-executa a página para mostrar o novo avatar imediatamente
                        st.rerun() 
                    else:
                        st.error("Ocorreu um erro ao atualizar o seu perfil. Tente novamente.")
    else:
        st.error("Não foi possível carregar os dados do seu perfil.")
else:
    st.error("Não foi possível identificar o utilizador. Por favor, faça o login novamente.")

# --- FIM DO FICHEIRO ---
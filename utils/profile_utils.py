# marketlens/utils/profile_utils.py

import streamlit as st
from firebase_config import db

def get_user_profile(user_id):
    """
    Busca o perfil de um utilizador no Firestore.
    """
    if not user_id:
        return None
    try:
        doc_ref = db.collection("user_profiles").document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            # Se o perfil não existe, retorna um dicionário vazio para ser preenchido
            return {}
    except Exception as e:
        st.error(f"Erro ao buscar o perfil do utilizador: {e}")
        return None

def update_user_profile(user_id, profile_data):
    """
    Cria ou atualiza o perfil de um utilizador no Firestore.
    """
    if not user_id or not profile_data:
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id)
        # merge=True garante que não apagamos dados existentes que não estão no formulário
        doc_ref.set(profile_data, merge=True)
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar o perfil do utilizador: {e}")
        return False

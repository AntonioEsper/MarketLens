# marketlens/utils/profile_utils.py

import streamlit as st
from firebase_config import db
from firebase_admin import storage

def get_user_profile(user_id):
    """
    Busca o perfil de um utilizador no Firestore.

    Args:
        user_id (str): O ID único do utilizador (fornecido pelo Firebase Auth).

    Returns:
        dict: Um dicionário com os dados do perfil, ou None se não for encontrado.
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

    Args:
        user_id (str): O ID único do utilizador.
        profile_data (dict): Um dicionário contendo os dados do perfil a serem guardados.

    Returns:
        bool: True se a operação for bem-sucedida, False caso contrário.
    """
    if not user_id or not profile_data:
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id)
        doc_ref.set(profile_data, merge=True) # merge=True garante que não apagamos dados existentes
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar o perfil do utilizador: {e}")
        return False

def upload_avatar_to_storage(user_id, file_bytes, content_type):
    """
    Envia uma imagem de avatar para o Firebase Storage.

    Args:
        user_id (str): O ID do utilizador para criar um caminho único.
        file_bytes (bytes): Os bytes da imagem.
        content_type (str): O tipo de conteúdo da imagem (ex: 'image/png').

    Returns:
        str: O URL público da imagem, ou None se falhar.
    """
    try:
        # Define o caminho único para o avatar no Storage (ex: 'avatars/user_123.png')
        file_extension = content_type.split('/')[-1]
        path_on_storage = f"avatars/{user_id}.{file_extension}"
        
        bucket = storage.bucket()
        blob = bucket.blob(path_on_storage)
        
        # Envia o ficheiro
        blob.upload_from_string(file_bytes, content_type=content_type)
        
        # Torna o ficheiro publicamente acessível
        blob.make_public()
        
        return blob.public_url
    except Exception as e:
        st.error(f"Erro ao fazer o upload do avatar: {e}")
        return None


# synapse_desk/utils/playbook_utils.py

import streamlit as st
from firebase_config import db
from datetime import datetime

def get_playbook_setups(user_id):
    """
    Busca todos os setups do playbook de um utilizador no Firestore.
    """
    if not user_id:
        return []
    try:
        setups_ref = db.collection("user_profiles").document(user_id).collection("playbook_setups")
        docs = setups_ref.order_by("created_at", direction="DESCENDING").stream()

        setups_list = []
        for doc in docs:
            setup = doc.to_dict()
            setup['doc_id'] = doc.id
            setups_list.append(setup)
        
        return setups_list
    except Exception as e:
        st.error(f"Erro ao buscar os setups do playbook: {e}")
        return []

def add_playbook_setup(user_id, setup_data):
    """
    Adiciona um novo setup ao playbook de um utilizador.
    """
    if not user_id or not setup_data:
        return False
    try:
        # Adiciona um timestamp de criação para ordenação
        setup_data['created_at'] = datetime.utcnow()
        setups_ref = db.collection("user_profiles").document(user_id).collection("playbook_setups")
        setups_ref.add(setup_data)
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar o setup ao playbook: {e}")
        return False

def update_playbook_setup(user_id, doc_id, setup_data):
    """
    Atualiza um setup existente no playbook de um utilizador.
    """
    if not user_id or not doc_id or not setup_data:
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("playbook_setups").document(doc_id)
        doc_ref.update(setup_data)
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar o setup: {e}")
        return False

def delete_playbook_setup(user_id, doc_id):
    """
    Apaga um setup do playbook de um utilizador.
    """
    if not user_id or not doc_id:
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("playbook_setups").document(doc_id)
        doc_ref.delete()
        return True
    except Exception as e:
        st.error(f"Erro ao apagar o setup: {e}")
        return False

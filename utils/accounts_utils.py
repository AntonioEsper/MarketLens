# synapse_desk/utils/accounts_utils.py

import streamlit as st
from firebase_config import db
from datetime import datetime

def get_trading_accounts(user_id):
    """
    Busca todas as contas de trading de um utilizador no Firestore.
    """
    if not user_id:
        return []
    try:
        accounts_ref = db.collection("user_profiles").document(user_id).collection("trading_accounts")
        docs = accounts_ref.order_by("created_at", direction="DESCENDING").stream()

        accounts_list = []
        for doc in docs:
            account = doc.to_dict()
            account['doc_id'] = doc.id
            accounts_list.append(account)
        
        return accounts_list
    except Exception as e:
        st.error(f"Erro ao buscar as contas de trading: {e}")
        return []

def add_trading_account(user_id, account_data):
    """
    Adiciona uma nova conta de trading para um utilizador.
    """
    if not user_id or not account_data:
        return False
    try:
        # Adiciona um timestamp de criação para ordenação
        account_data['created_at'] = datetime.utcnow()
        accounts_ref = db.collection("user_profiles").document(user_id).collection("trading_accounts")
        accounts_ref.add(account_data)
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar a conta de trading: {e}")
        return False

def update_trading_account(user_id, doc_id, account_data):
    """
    Atualiza uma conta de trading existente de um utilizador.
    """
    if not user_id or not doc_id or not account_data:
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("trading_accounts").document(doc_id)
        doc_ref.update(account_data)
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar a conta: {e}")
        return False

def delete_trading_account(user_id, doc_id):
    """
    Apaga uma conta de trading de um utilizador.
    """
    if not user_id or not doc_id:
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("trading_accounts").document(doc_id)
        doc_ref.delete()
        return True
    except Exception as e:
        st.error(f"Erro ao apagar a conta: {e}")
        return False

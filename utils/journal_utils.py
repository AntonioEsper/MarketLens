# synapse_desk/utils/journal_utils.py

import streamlit as st
from firebase_config import db
import pandas as pd
from datetime import datetime
from google.cloud.firestore_v1.base_query import FieldFilter

def get_journal_entries(user_id, status_filter="Todos"):
    """
    Busca todos os registos do diário de um utilizador, com um filtro opcional de status.
    CORREÇÃO: Utiliza a sintaxe recomendada 'FieldFilter' para as queries.
    """
    if not user_id: return pd.DataFrame()
    try:
        journal_ref = db.collection("user_profiles").document(user_id).collection("journal_entries")
        
        # Query simplificada ao Firebase, sem ordenação
        if status_filter == "Abertos":
            query = journal_ref.where(filter=FieldFilter("status", "in", ["Em Aberto", "Pendente"]))
        elif status_filter != "Todos":
            query = journal_ref.where(filter=FieldFilter("status", "==", status_filter))
        else:
            query = journal_ref

        docs = query.stream()
        trades_list = []
        for doc in docs:
            trade = doc.to_dict()
            trade['doc_id'] = doc.id
            if 'trade_date' in trade and isinstance(trade['trade_date'], str):
                trade['trade_date'] = pd.to_datetime(trade['trade_date'])
            trades_list.append(trade)
        
        if not trades_list:
            return pd.DataFrame()

        df = pd.DataFrame(trades_list)
        if 'trade_date' in df.columns:
            df = df.sort_values(by='trade_date', ascending=False)
        return df

    except Exception as e:
        st.error(f"Erro ao buscar o diário: {e}")
        return pd.DataFrame()

def add_journal_entry(user_id, entry_data):
    """Adiciona um único registo manual ao diário."""
    if not user_id or not entry_data: return False
    try:
        entry_data['created_at'] = datetime.utcnow()
        db.collection("user_profiles").document(user_id).collection("journal_entries").add(entry_data)
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar registo: {e}"); return False

def update_journal_entry(user_id, doc_id, entry_data):
    """Atualiza um registo existente no diário."""
    if not all([user_id, doc_id, entry_data]): return False
    try:
        if entry_data.get("status") == "Finalizado":
            entry_price = float(entry_data.get("entry_price", 0))
            exit_price = float(entry_data.get("exit_price", 0))
            direction = entry_data.get("direction")
            if entry_price > 0 and exit_price > 0:
                pnl = exit_price - entry_price if direction == "Compra" else entry_price - exit_price
                entry_data['pnl'] = pnl
        db.collection("user_profiles").document(user_id).collection("journal_entries").document(doc_id).update(entry_data)
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar o registo: {e}"); return False

def delete_journal_entry(user_id, doc_id):
    """Apaga um registo do diário."""
    if not all([user_id, doc_id]): return False
    try:
        db.collection("user_profiles").document(user_id).collection("journal_entries").document(doc_id).delete()
        return True
    except Exception as e:
        st.error(f"Erro ao apagar o registo: {e}"); return False


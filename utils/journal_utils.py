# synapse_desk/utils/journal_utils.py

import streamlit as st
from firebase_config import db
import pandas as pd
from datetime import datetime

def get_journal_entries(user_id, status_filter="Todos"):
    """
    Busca todos os registos do diário de um utilizador, com um filtro opcional de status.
    """
    if not user_id:
        return pd.DataFrame()
    try:
        journal_ref = db.collection("user_profiles").document(user_id).collection("journal_entries")
        
        # Constrói a query com base no filtro de status
        if status_filter != "Todos":
            query = journal_ref.where("status", "==", status_filter)
        else:
            query = journal_ref

        # Ordena pela data de criação para consistência
        docs = query.order_by("created_at", direction="DESCENDING").stream()

        trades_list = []
        for doc in docs:
            trade = doc.to_dict()
            trade['doc_id'] = doc.id
            # Garante que a data de trade seja um objeto datetime para ordenação
            if isinstance(trade.get('trade_date'), str):
                trade['trade_date'] = pd.to_datetime(trade['trade_date'])
            trades_list.append(trade)

        if not trades_list:
            return pd.DataFrame()

        df = pd.DataFrame(trades_list)
        # Ordena pelo campo de data do trade, que é mais relevante para o utilizador
        return df.sort_values(by="trade_date", ascending=False)

    except Exception as e:
        st.error(f"Erro ao buscar os registos do diário: {e}")
        return pd.DataFrame()

def add_journal_entry(user_id, entry_data, accounts_data):
    """
    Adiciona um novo registo ao diário, validando a moeda e calculando o risco.
    """
    if not all([user_id, entry_data, accounts_data]):
        return False
    try:
        # --- Lógica de Validação e Cálculo de Risco ---
        selected_accounts_names = entry_data.get("accounts", [])
        selected_accounts_details = [acc for acc in accounts_data if acc['account_name'] in selected_accounts_names]

        # Valida se todas as contas selecionadas têm a mesma moeda
        if selected_accounts_details:
            first_currency = selected_accounts_details[0].get('currency')
            if not all(acc.get('currency') == first_currency for acc in selected_accounts_details):
                st.error("Erro: As contas selecionadas para uma operação devem ter a mesma moeda.")
                return False
            # Armazena a moeda da operação
            entry_data['currency'] = first_currency
        
        # Calcula o risco financeiro com base no capital total das contas selecionadas
        total_capital = sum(acc.get('initial_capital', 0) for acc in selected_accounts_details)
        risk_percentage = entry_data.get("risk_percentage", 0)
        
        if total_capital > 0 and risk_percentage > 0:
            calculated_risk = total_capital * (risk_percentage / 100)
            entry_data['calculated_risk_value'] = calculated_risk

        # Adiciona um timestamp de criação para ordenação interna
        entry_data['created_at'] = datetime.utcnow()
        
        journal_ref = db.collection("user_profiles").document(user_id).collection("journal_entries")
        journal_ref.add(entry_data)
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar o registo ao diário: {e}")
        return False

def update_journal_entry(user_id, doc_id, entry_data):
    """
    Atualiza um registo existente no diário de um utilizador.
    """
    if not all([user_id, doc_id, entry_data]):
        return False
    try:
        # Lógica para recalcular o PnL quando a operação é finalizada
        if entry_data.get("status") == "Finalizado":
            entry_price = float(entry_data.get("entry_price", 0))
            exit_price = float(entry_data.get("exit_price", 0))
            direction = entry_data.get("direction")
            
            if entry_price > 0 and exit_price > 0:
                if direction == "Compra":
                    pnl = exit_price - entry_price
                else: # Venda
                    pnl = entry_price - exit_price
                # Assume 1 unidade de volume por agora. Pode ser expandido no futuro.
                entry_data['pnl'] = pnl
                # Adiciona uma data de saída
                entry_data['exit_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        doc_ref = db.collection("user_profiles").document(user_id).collection("journal_entries").document(doc_id)
        doc_ref.update(entry_data)
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar o registo: {e}")
        return False

def delete_journal_entry(user_id, doc_id):
    """
    Apaga um registo do diário de um utilizador.
    """
    if not all([user_id, doc_id]):
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("journal_entries").document(doc_id)
        doc_ref.delete()
        return True
    except Exception as e:
        st.error(f"Erro ao apagar o registo: {e}")
        return False


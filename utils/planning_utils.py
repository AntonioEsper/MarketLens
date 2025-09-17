# synapse_desk/utils/planning_utils.py

import streamlit as st
from firebase_config import db
from datetime import datetime

# --- Funções para o Plano Semanal ---

def get_current_week_id():
    """Gera um ID único para a semana atual no formato YYYY-Www (ex: 2025-W38)."""
    # %U - Week number of the year (Sunday as the first day of week)
    return datetime.now().strftime("%Y-W%U")

def get_weekly_plan(user_id, week_id):
    """
    Busca o plano de trading semanal de um utilizador no Firestore.
    Os planos são guardados numa subcoleção dentro do perfil do utilizador.
    """
    if not user_id or not week_id:
        return "" # Retorna uma string vazia se não houver plano
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("weekly_plans").document(week_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("plan_text", "")
        else:
            return "" # Retorna vazio se o documento para a semana ainda não foi criado
    except Exception as e:
        st.error(f"Erro ao buscar o plano semanal: {e}")
        return ""

def update_weekly_plan(user_id, week_id, plan_text):
    """
    Cria ou atualiza o plano de trading semanal de um utilizador no Firestore.
    """
    if not user_id or not week_id:
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("weekly_plans").document(week_id)
        doc_ref.set({"plan_text": plan_text})
        return True
    except Exception as e:
        st.error(f"Erro ao guardar o plano semanal: {e}")
        return False

# --- Funções para o Checklist Diário ---

def get_current_date_id():
    """Gera um ID único para a data atual no formato YYYY-MM-DD."""
    return datetime.now().strftime("%Y-%m-%d")

def get_daily_checklist(user_id, date_id):
    """
    Busca o checklist diário de um utilizador no Firestore.
    """
    if not user_id or not date_id:
        return {} # Retorna um dicionário vazio
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("daily_checklists").document(date_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        else:
            return {}
    except Exception as e:
        st.error(f"Erro ao buscar o checklist diário: {e}")
        return {}

def update_daily_checklist(user_id, date_id, checklist_data):
    """
    Cria ou atualiza o checklist diário de um utilizador no Firestore.
    """
    if not user_id or not date_id:
        return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("daily_checklists").document(date_id)
        doc_ref.set(checklist_data)
        return True
    except Exception as e:
        st.error(f"Erro ao guardar o checklist diário: {e}")
        return False

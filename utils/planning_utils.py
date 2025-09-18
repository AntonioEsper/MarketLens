# synapse_desk/utils/planning_utils.py

import streamlit as st
from firebase_config import db
from datetime import datetime, date

# --- Funções para o Plano Semanal ---

def get_week_id_from_date(selected_date: date):
    """Gera um ID único para a semana de uma data específica (YYYY-Www)."""
    return selected_date.strftime("%Y-W%U")

def get_weekly_plan(user_id, week_id):
    """Busca o plano de trading semanal estruturado de um utilizador."""
    if not user_id or not week_id: return {}
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("weekly_plans").document(week_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else {}
    except Exception as e:
        st.error(f"Erro ao buscar o plano semanal: {e}"); return {}

def get_all_weekly_plans(user_id):
    """Busca TODOS os planos semanais de um utilizador, ordenados do mais recente para o mais antigo."""
    if not user_id: return []
    try:
        plans_ref = db.collection("user_profiles").document(user_id).collection("weekly_plans")
        # CORREÇÃO DEFINITIVA: Usa a string "__name__" para ordenar pelo ID do documento.
        docs = plans_ref.order_by("__name__", direction='DESCENDING').stream()
        plans_list = []
        for doc in docs:
            plan = doc.to_dict()
            plan['week_id'] = doc.id
            plans_list.append(plan)
        return plans_list
    except Exception as e:
        st.error(f"Erro ao buscar o histórico de planos semanais: {e}"); return []

def update_weekly_plan(user_id, week_id, plan_data):
    """Cria ou atualiza um plano de trading semanal estruturado."""
    if not user_id or not week_id or not isinstance(plan_data, dict): return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("weekly_plans").document(week_id)
        doc_ref.set(plan_data); return True
    except Exception as e:
        st.error(f"Erro ao guardar o plano semanal: {e}"); return False

# --- Funções para o Checklist Diário ---

def get_date_id_from_date(selected_date: date):
    """Gera um ID único para uma data específica no formato YYYY-MM-DD."""
    return selected_date.strftime("%Y-%m-%d")

def get_daily_checklist(user_id, date_id):
    """Busca o checklist diário de um utilizador no Firestore."""
    if not user_id or not date_id: return {}
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("daily_checklists").document(date_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else {}
    except Exception as e:
        st.error(f"Erro ao buscar o checklist diário: {e}"); return {}

def get_all_daily_checklists(user_id):
    """Busca TODOS os checklists diários de um utilizador, ordenados do mais recente para o mais antigo."""
    if not user_id: return []
    try:
        checklists_ref = db.collection("user_profiles").document(user_id).collection("daily_checklists")
        # Ordena pelo ID do documento (que é a nossa date_id 'YYYY-MM-DD') em ordem descendente
        docs = checklists_ref.order_by("__name__", direction='DESCENDING').stream()
        checklists_list = []
        for doc in docs:
            checklist = doc.to_dict()
            checklist['date_id'] = doc.id
            checklists_list.append(checklist)
        return checklists_list
    except Exception as e:
        st.error(f"Erro ao buscar o histórico de checklists diários: {e}"); return []

def update_daily_checklist(user_id, date_id, checklist_data):
    """Cria ou atualiza o checklist diário de um utilizador no Firestore."""
    if not user_id or not date_id or not isinstance(checklist_data, dict): return False
    try:
        doc_ref = db.collection("user_profiles").document(user_id).collection("daily_checklists").document(date_id)
        doc_ref.set(checklist_data); return True
    except Exception as e:
        st.error(f"Erro ao guardar o checklist diário: {e}"); return False


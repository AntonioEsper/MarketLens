# synapse_desk/pages/8_📅_Plano_de_Trading.py

import streamlit as st
from view_utils import setup_sidebar
from utils.planning_utils import (
    get_current_week_id, get_weekly_plan, update_weekly_plan,
    get_current_date_id, get_daily_checklist, update_daily_checklist
)

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Plano de Trading")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("📅 Plano de Trading")
st.caption("Onde a preparação encontra a oportunidade. Defina a sua estratégia e execute com disciplina.")
st.markdown("---")

# --- LÓGICA DA PÁGINA ---
user_id = st.session_state['user_info'].get('localId')

if not user_id:
    st.error("Não foi possível identificar o utilizador. Por favor, faça o login novamente.")
    st.stop()

# --- ABAS PARA ORGANIZAÇÃO ---
tab_weekly, tab_daily = st.tabs(["🗓️ Plano Semanal", "✅ Checklist Diário (Pré-Trade)"])

# --- Aba do Plano Semanal ---
with tab_weekly:
    st.header(f"Plano Estratégico para a Semana Atual")
    
    week_id = get_current_week_id()
    st.subheader(f"Semana: {week_id}")

    with st.spinner("A carregar plano semanal..."):
        current_plan = get_weekly_plan(user_id, week_id)
    
    plan_text = st.text_area(
        "Escreva aqui a sua análise, viés, ativos a monitorizar e objetivos para a semana:",
        value=current_plan,
        height=400,
        placeholder="Ex: Viés de Risk-Off devido aos dados de inflação. Focar em vendas no EUR/USD. Monitorizar o Ouro para possíveis compras se o DXY mostrar fraqueza..."
    )

    if st.button("Guardar Plano Semanal"):
        if update_weekly_plan(user_id, week_id, plan_text):
            st.success("Plano semanal guardado com sucesso!")
            st.balloons()
        else:
            st.error("Ocorreu um erro ao guardar o plano. Tente novamente.")

# --- Aba do Checklist Diário ---
with tab_daily:
    st.header("Checklist e Tarefas Diárias")
    
    date_id = get_current_date_id()
    st.subheader(f"Data: {date_id}")
    
    with st.spinner("A carregar checklist diário..."):
        checklist_data = get_daily_checklist(user_id, date_id)

    with st.form("daily_checklist_form"):
        st.markdown("**Rotina Pré-Mercado:**")
        task1 = st.checkbox("Notícias e eventos do calendário económico verificados?", value=checklist_data.get("task1", False))
        task2 = st.checkbox("Níveis chave (suporte/resistência) nos principais ativos revistos?", value=checklist_data.get("task2", False))
        task3 = st.checkbox("Estado mental e emocional avaliado e pronto para operar?", value=checklist_data.get("task3", False))
        
        st.markdown("**Análise e Oportunidades do Dia:**")
        opportunities = st.text_area(
            "Quais as principais oportunidades ou hipóteses a monitorizar hoje? (Se não houver, escreva 'Nenhuma')",
            value=checklist_data.get("opportunities", ""),
            height=200,
            placeholder="Ex: Oportunidade de venda no GBP/JPY se o preço testar a resistência em 198.50 e mostrar um sinal de rejeição."
        )

        submit_button = st.form_submit_button("Guardar Checklist do Dia")

        if submit_button:
            new_checklist_data = {
                "task1": task1,
                "task2": task2,
                "task3": task3,
                "opportunities": opportunities
            }
            if update_daily_checklist(user_id, date_id, new_checklist_data):
                st.success("Checklist diário guardado com sucesso!")
            else:
                st.error("Ocorreu um erro ao guardar o checklist. Tente novamente.")

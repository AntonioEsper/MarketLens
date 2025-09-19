# synapse_desk/pages/1_📅_Plano_de_Trading.py

import streamlit as st
import pandas as pd
from view_utils import setup_sidebar
from datetime import date, timedelta
from utils.planning_utils import (
    get_week_id_from_date, get_weekly_plan, update_weekly_plan, get_all_weekly_plans,
    get_date_id_from_date, get_daily_checklist, update_daily_checklist, get_all_daily_checklists
)
from utils.config import ASSET_CATEGORIES
from utils.playbook_utils import get_playbook_setups
from utils.journal_utils import get_journal_entries

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Plano de Trading")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login."); st.stop()

# --- CABEÇALHO ---
st.title("📅 Plano de Trading")
st.caption("Onde a preparação encontra a oportunidade. Defina a sua estratégia e execute com disciplina.")

# --- LÓGICA DA PÁGINA ---
user_id = st.session_state['user_info'].get('localId')
if not user_id: st.error("Não foi possível identificar o utilizador."); st.stop()

# --- SELETOR DE DATA PARA NAVEGAÇÃO HISTÓRICA ---
st.markdown("---")
selected_date = st.date_input("Selecione uma data para ver ou editar o plano e checklist:", value=date.today())

# --- CARREGAMENTO DE DADOS ---
week_id = get_week_id_from_date(selected_date)
date_id = get_date_id_from_date(selected_date)
weekly_plan_data = get_weekly_plan(user_id, week_id)
daily_checklist_data = get_daily_checklist(user_id, date_id)
playbook_setups = get_playbook_setups(user_id)
setup_names = [s['setup_name'] for s in playbook_setups] if playbook_setups else []
all_assets = sorted([asset for category in ASSET_CATEGORIES.values() for asset in category if "---" not in asset])
all_journal_entries = get_journal_entries(user_id)

# --- ABAS PARA ORGANIZAÇÃO ---
tabs = st.tabs([f"🗓️ Plano Semanal (Semana de {selected_date.strftime('%d/%m')})", f"✅ Checklist Diário ({selected_date.strftime('%d/%m/%Y')})", "📈 Trades da Semana"])

# --- ABA 1: PLANO SEMANAL ---
with tabs[0]:
    with st.form(f"weekly_plan_form_{week_id}"):
        st.header(f"Plano Estratégico Semanal - {week_id}")
        focus = st.text_input("Foco Principal da Semana", value=weekly_plan_data.get("focus", ""))
        assets_watched = st.multiselect("Ativos em Observação", options=all_assets, default=weekly_plan_data.get("assets_watched", []))
        setups_in_focus = st.multiselect("Setups do Playbook em Foco", options=setup_names, default=weekly_plan_data.get("setups_in_focus", []))
        bull_scenario = st.text_area("Cenário Bullish Principal", value=weekly_plan_data.get("bull_scenario", ""), height=150)
        bear_scenario = st.text_area("Cenário Bearish Principal", value=weekly_plan_data.get("bear_scenario", ""), height=150)
        risk_limit_perc = st.number_input("Limite de Perda Semanal (%)", value=weekly_plan_data.get("risk_limit_perc", 1.0), min_value=0.1, max_value=10.0, step=0.1, format="%.2f")

        if st.form_submit_button("Guardar Plano Semanal", use_container_width=True):
            new_plan_data = {"focus": focus, "assets_watched": assets_watched, "setups_in_focus": setups_in_focus, "bull_scenario": bull_scenario, "bear_scenario": bear_scenario, "risk_limit_perc": risk_limit_perc}
            if update_weekly_plan(user_id, week_id, new_plan_data):
                st.success("Plano semanal guardado com sucesso!"); st.rerun()

    st.markdown("---"); st.header("Histórico de Planos Semanais")
    all_plans = get_all_weekly_plans(user_id)
    if not all_plans: st.info("Nenhum plano semanal guardado anteriormente.")
    else:
        for plan in all_plans:
            with st.expander(f"**Semana {plan['week_id']}** - Foco: {plan.get('focus', 'N/A')}"):
                st.write(f"**Ativos:** {', '.join(plan.get('assets_watched', [])) or 'N/A'}")
                st.write(f"**Setups:** {', '.join(plan.get('setups_in_focus', [])) or 'N/A'}")

# --- ABA 2: CHECKLIST DIÁRIO ---
with tabs[1]:
    with st.form(f"daily_checklist_form_{date_id}"):
        st.header(f"Checklist Pré-Mercado para {selected_date.strftime('%A, %d de %B')}")
        task1 = st.checkbox("Calendário económico verificado?", value=daily_checklist_data.get("task1", False))
        task2 = st.checkbox("Níveis chave revistos?", value=daily_checklist_data.get("task2", False))
        task3 = st.checkbox("Estado mental avaliado?", value=daily_checklist_data.get("task3", False))
        opportunities = st.text_area("Análise e Oportunidades do Dia", value=daily_checklist_data.get("opportunities", ""), height=200)

        if st.form_submit_button("Guardar Checklist do Dia", use_container_width=True):
            new_checklist_data = {"task1": task1, "task2": task2, "task3": task3, "opportunities": opportunities}
            if update_daily_checklist(user_id, date_id, new_checklist_data):
                st.success("Checklist diário guardado com sucesso!"); st.rerun()

    st.markdown("---"); st.header("Histórico de Checklists Diários")
    all_checklists = get_all_daily_checklists(user_id)
    if not all_checklists: st.info("Nenhum checklist diário guardado anteriormente.")
    else:
        for checklist in all_checklists:
            with st.expander(f"**Checklist de {checklist['date_id']}**"):
                st.checkbox("Calendário económico", value=checklist.get("task1", False), disabled=True, key=f"t1_{checklist['date_id']}")
                st.checkbox("Níveis chave", value=checklist.get("task2", False), disabled=True, key=f"t2_{checklist['date_id']}")
                st.checkbox("Estado mental", value=checklist.get("task3", False), disabled=True, key=f"t3_{checklist['date_id']}")
                st.text_area("Oportunidades:", value=checklist.get("opportunities", ''), disabled=True, key=f"opp_{checklist['date_id']}")

# --- ABA 3: TRADES DA SEMANA ---
with tabs[2]:
    st.header(f"Operações Executadas na Semana de {selected_date.strftime('%d/%m/%Y')}")
    start_of_week, end_of_week = selected_date - timedelta(days=selected_date.weekday()), selected_date + timedelta(days=6-selected_date.weekday())
    
    if not all_journal_entries.empty and 'trade_date' in all_journal_entries.columns:
        trades_this_week = all_journal_entries[(all_journal_entries['trade_date'].dt.date >= start_of_week) & (all_journal_entries['trade_date'].dt.date <= end_of_week)].copy()
        if not trades_this_week.empty:
            if 'pnl_usd' not in trades_this_week.columns:
                trades_this_week['pnl_usd'] = 0 # Adiciona PnL se não existir
            trades_this_week['Resultado'] = trades_this_week['pnl_usd'].apply(lambda pnl: 'Ganho' if pnl > 0 else ('Perda' if pnl < 0 else 'Empate'))
            trades_display = trades_this_week.rename(columns={'trade_date': 'Data/Hora', 'asset': 'Instrumento', 'direction': 'Direção', 'pnl_usd': 'PnL (USD)', 'selected_setup': 'Setup'})
            st.dataframe(trades_display[['Data/Hora', 'Instrumento', 'Direção', 'Resultado', 'PnL (USD)', 'Setup']], use_container_width=True, hide_index=True, column_config={"PnL (USD)": st.column_config.NumberColumn(format="$%.2f")})
        else: st.info("Nenhuma operação registada para esta semana.")
    else: st.info("Nenhuma operação registada no diário.")

# --- FIM DA PÁGINA ---
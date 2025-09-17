# synapse_desk/pages/9_📓_Journaling.py

import streamlit as st
import pandas as pd
from view_utils import setup_sidebar
from datetime import datetime
from utils.journal_utils import (
    get_journal_entries, add_journal_entry,
    update_journal_entry, delete_journal_entry
)
from utils.accounts_utils import get_trading_accounts
from utils.playbook_utils import get_playbook_setups
# CORREÇÃO: Importar o yahoo_finance_map do sítio certo
from utils.config import yahoo_finance_map

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Diário de Trading")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- LÓGICA DA PÁGINA ---
user_id = st.session_state['user_info'].get('localId')
if not user_id:
    st.error("Não foi possível identificar o utilizador. Por favor, faça o login novamente.")
    st.stop()

# --- CARREGAMENTO DE DADOS PARA OS FORMULÁRIOS ---
accounts = get_trading_accounts(user_id)
setups = get_playbook_setups(user_id)

# --- REFACTOR: Melhorar a exibição das contas ---
# Cria um dicionário para mapear o nome formatado de volta para o doc_id original.
account_options_map = {
    f"{acc['account_name']} ({acc.get('currency', 'USD')} {acc.get('initial_capital', 0):,.2f})": acc['doc_id']
    for acc in accounts
}
account_display_names = list(account_options_map.keys())

# --- CABEÇALHO ---
st.title("📓 Diário de Trading (Journaling)")
st.caption("Registe as suas operações para análise de performance e melhoria contínua.")
st.markdown("---")

# --- FORMULÁRIO PARA ADICIONAR NOVA OPERAÇÃO ---
with st.expander("➕ Adicionar Nova Operação", expanded=True):
    with st.form("new_trade_form", clear_on_submit=True):
        st.subheader("Detalhes da Operação")
        
        # --- Linha 1: Ativo, Direção, Setup ---
        col1, col2, col3 = st.columns(3)
        with col1:
            asset = st.selectbox("Ativo", options=list(yahoo_finance_map.keys()), index=0)
        with col2:
            direction = st.selectbox("Direção", options=["Compra", "Venda"])
        with col3:
            setup_names = [s['setup_name'] for s in setups] if setups else []
            selected_setup = st.selectbox("Setup do Playbook", options=setup_names, index=0 if setup_names else None)

        # ADIÇÃO: Linha para Data e Hora da Operação
        col_date, col_time, _ = st.columns([1, 1, 3])
        with col_date:
            trade_date_input = st.date_input("Data da Operação", value=datetime.now())
        with col_time:
            trade_time_input = st.time_input("Hora da Operação", value=datetime.now().time())

        st.markdown("---")
        st.subheader("Gestão da Operação")
        
        # --- Linha 2: Preços e Status ---
        col_risk1, col_risk2, col_risk3, col_risk4, col_risk5 = st.columns(5)
        with col_risk1:
            entry_price = st.number_input("Preço de Entrada", step=0.0001, format="%.5f")
        with col_risk2:
            stop_loss = st.number_input("Stop Loss", step=0.0001, format="%.5f")
        with col_risk3:
            target_price = st.number_input("Take Profit (Alvo)", step=0.0001, format="%.5f")
        with col_risk4:
            status = st.selectbox("Status", options=["Pendente", "Em Aberto", "Finalizado"])
        with col_risk5:
            exit_price = st.number_input("Preço de Saída", step=0.0001, format="%.5f", help="Preencha apenas se o status for 'Finalizado'")

        # --- Linha 3: Contas e Risco ---
        col_ac, col_risk_perc, col_risk_usd = st.columns([2, 1, 1])
        with col_ac:
            selected_accounts_display = st.multiselect("Conta(s) de Execução", options=account_display_names)
        with col_risk_perc:
            risk_perc = st.number_input("Risco por Operação (%)", min_value=0.1, max_value=100.0, value=1.0, step=0.1, format="%.2f")

        # --- LÓGICA DE CÁLCULO DE RISCO ---
        total_capital_selected = 0
        selected_account_data = [] # Inicializa a lista
        if selected_accounts_display:
            selected_doc_ids = [account_options_map[name] for name in selected_accounts_display]
            selected_account_data = [acc for acc in accounts if acc['doc_id'] in selected_doc_ids]
            total_capital_selected = sum(float(acc.get('initial_capital', 0)) for acc in selected_account_data)
        
        calculated_risk_usd = (risk_perc / 100) * total_capital_selected

        with col_risk_usd:
            st.metric(label="Risco Calculado (USD)", value=f"${calculated_risk_usd:,.2f}")

        # --- Linha 4: Notas ---
        notes = st.text_area("Notas e Racional da Operação", placeholder="Porque abriu esta operação? Qual o contexto de mercado?")
        
        # --- Botão de Submissão ---
        submit_button = st.form_submit_button("Registar Operação")
        if submit_button:
            selected_doc_ids_to_save = [account_options_map[name] for name in selected_accounts_display]

            # Combina a data e a hora fornecidas pelo utilizador
            trade_datetime = datetime.combine(trade_date_input, trade_time_input)

            new_trade_data = {
                "asset": asset, "direction": direction, "selected_setup": selected_setup,
                "entry_price": entry_price, "stop_loss": stop_loss, "target_price": target_price,
                "status": status, "exit_price": exit_price,
                "accounts": selected_doc_ids_to_save,
                "risk_percentage": risk_perc,
                "risk_usd": calculated_risk_usd,
                "notes": notes,
                # Usa a data e hora do formulário em vez de datetime.now()
                "trade_date": trade_datetime.strftime("%Y-%m-%d %H:%M:%S")
            }
            # CORREÇÃO: Passar o argumento 'accounts' que estava em falta
            if add_journal_entry(user_id, new_trade_data, accounts):
                st.success("Operação registada com sucesso!")
                st.rerun()
            else:
                st.error("Erro ao registar a operação.")

# --- HISTÓRICO DE OPERAÇÕES ---
st.markdown("---")
st.header("Histórico de Operações")
status_filter = st.selectbox("Filtrar por Status", options=["Todos", "Pendente", "Em Aberto", "Finalizado"], index=0)

df_journal = get_journal_entries(user_id, status_filter=status_filter)

if df_journal.empty:
    st.info("Nenhum registo encontrado para o filtro selecionado.")
else:
    for index, row in df_journal.iterrows():
        doc_id = row.get('doc_id')
        trade_date = pd.to_datetime(row['trade_date']).strftime('%d/%m/%Y %H:%M')
        
        trade_accounts_names = [
            f"{acc['account_name']} ({acc.get('currency', 'USD')} {acc.get('initial_capital', 0):,.2f})"
            for acc in accounts 
            if acc['doc_id'] in row.get('accounts', [])
        ]

        with st.expander(f"{row['asset']} ({row['direction']}) - {trade_date} - Status: {row['status']}"):
            with st.form(f"edit_form_{doc_id}"):
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Entrada", f"{row['entry_price']:.5f}")
                    st.metric("Saída", f"{row.get('exit_price', 0):.5f}" if row.get('exit_price') else "N/A")
                with c2:
                    st.metric("Stop Loss", f"{row['stop_loss']:.5f}")
                    st.metric("Alvo (TP)", f"{row['target_price']:.5f}")
                with c3:
                    st.write("**Setup:**")
                    st.info(f"{row.get('selected_setup', 'N/A')}")
                with c4:
                    st.write("**Conta(s):**")
                    st.info(", ".join(trade_accounts_names) if trade_accounts_names else "N/A")

                st.markdown("---")
                st.write("**Editar Operação:**")
                
                edit_c1, edit_c2, edit_c3 = st.columns(3)
                with edit_c1:
                    status_edit = st.selectbox("Status", options=["Pendente", "Em Aberto", "Finalizado"], index=["Pendente", "Em Aberto", "Finalizado"].index(row['status']), key=f"status_{doc_id}")
                with edit_c2:
                    entry_edit = st.number_input("Preço Entrada", value=float(row['entry_price']), format="%.5f", key=f"entry_{doc_id}")
                with edit_c3:
                    exit_edit = st.number_input("Preço Saída", value=float(row.get('exit_price', 0)), format="%.5f", key=f"exit_{doc_id}")

                edit_c4, edit_c5, edit_c6 = st.columns(3)
                with edit_c4:
                    sl_edit = st.number_input("Stop Loss", value=float(row['stop_loss']), format="%.5f", key=f"sl_{doc_id}")
                with edit_c5:
                    tp_edit = st.number_input("Take Profit", value=float(row['target_price']), format="%.5f", key=f"tp_{doc_id}")
                with edit_c6:
                    selected_display_edit = [
                        name for name, doc in account_options_map.items() if doc in row.get('accounts', [])
                    ]
                    accounts_edit_display = st.multiselect("Contas", options=account_display_names, default=selected_display_edit, key=f"acc_{doc_id}")
                    accounts_edit = [account_options_map[name] for name in accounts_edit_display]

                notes_edit = st.text_area("Notas", value=row.get('notes', ''), key=f"notes_{doc_id}")

                btn_c1, btn_c2, _ = st.columns([1, 1, 5])
                with btn_c1:
                    if st.form_submit_button("✔️ Guardar", use_container_width=True):
                        updated_data = { "status": status_edit, "entry_price": entry_edit, "exit_price": exit_edit,
                                         "stop_loss": sl_edit, "target_price": tp_edit, "accounts": accounts_edit, "notes": notes_edit }
                        if update_journal_entry(user_id, doc_id, updated_data):
                            st.success("Operação atualizada!"); st.rerun()
                with btn_c2:
                    if st.form_submit_button("❌ Apagar", type="primary", use_container_width=True):
                        if delete_journal_entry(user_id, doc_id):
                            st.success("Operação apagada!"); st.rerun()


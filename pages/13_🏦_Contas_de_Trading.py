# synapse_desk/pages/13_🏦_Contas_de_Trading.py

import streamlit as st
from view_utils import setup_sidebar
from utils.accounts_utils import (
    get_trading_accounts, add_trading_account,
    update_trading_account, delete_trading_account
)

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Contas de Trading")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("🏦 Contas de Trading")
st.caption("Registe e gira as suas contas de corretoras e mesas proprietárias.")
st.markdown("---")

# --- LÓGICA DA PÁGINA ---
user_id = st.session_state['user_info'].get('localId')
if not user_id:
    st.error("Não foi possível identificar o utilizador.")
    st.stop()

# --- FORMULÁRIO PARA ADICIONAR NOVA CONTA ---
with st.expander("➕ Adicionar Nova Conta de Trading", expanded=True):
    with st.form("new_account_form", clear_on_submit=True):
        st.subheader("Detalhes da Conta")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            account_name = st.text_input("Nome da Conta", placeholder="Ex: Conta Principal (Corretora X)")
            account_type = st.selectbox("Tipo de Conta", options=["Corretora Pessoal", "Mesa Proprietária (Avaliação)", "Mesa Proprietária (Financiado)"])
        with c2:
            initial_capital = st.number_input("Capital Inicial", min_value=0.0, step=100.0, format="%.2f")
        with c3:
            currency = st.selectbox("Moeda da Conta", options=["USD", "EUR", "GBP", "JPY"], index=0)

        submitted = st.form_submit_button("Adicionar Conta")
        if submitted:
            account_data = {
                "account_name": account_name, "initial_capital": initial_capital,
                "account_type": account_type, "currency": currency
            }
            if add_trading_account(user_id, account_data):
                st.success("Conta adicionada com sucesso!"); st.rerun()

st.markdown("---")
st.header("Suas Contas Registadas")

# --- EXIBIÇÃO DAS CONTAS EXISTENTES ---
accounts = get_trading_accounts(user_id)
if not accounts:
    st.info("Ainda não há contas registadas.")
else:
    for account in accounts:
        doc_id = account['doc_id']
        capital = account.get('initial_capital', 0.0)
        currency_symbol = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}.get(account.get('currency', 'USD'), '$')
        
        exp_title = f"**{account['account_name']}** | Capital: {currency_symbol}{capital:,.2f} | Tipo: {account['account_type']}"
        with st.expander(exp_title):
            with st.form(f"edit_form_{doc_id}"):
                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    name_edit = st.text_input("Nome", value=account['account_name'], key=f"name_{doc_id}")
                    type_opts = ["Corretora Pessoal", "Mesa Proprietária (Avaliação)", "Mesa Proprietária (Financiado)"]
                    type_edit = st.selectbox("Tipo", options=type_opts, index=type_opts.index(account['account_type']), key=f"type_{doc_id}")
                with ec2:
                    capital_edit = st.number_input("Capital", value=capital, format="%.2f", key=f"capital_{doc_id}")
                with ec3:
                    curr_opts = ["USD", "EUR", "GBP", "JPY"]
                    curr_edit = st.selectbox("Moeda", options=curr_opts, index=curr_opts.index(account.get('currency', 'USD')), key=f"curr_{doc_id}")

                btn_c1, btn_c2, btn_c3 = st.columns([1, 1, 5])
                with btn_c1:
                    if st.form_submit_button("Guardar", use_container_width=True):
                        updated_data = {"account_name": name_edit, "initial_capital": capital_edit, "account_type": type_edit, "currency": curr_edit}
                        if update_trading_account(user_id, doc_id, updated_data):
                            st.success("Conta atualizada!"); st.rerun()
                with btn_c2:
                    if st.form_submit_button("Apagar", type="primary", use_container_width=True):
                        if delete_trading_account(user_id, doc_id):
                            st.success("Conta apagada!"); st.rerun()


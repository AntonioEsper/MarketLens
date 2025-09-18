# marketlens/pages/3_⚙️_Gestão.py

import streamlit as st
from view_utils import setup_sidebar
from utils.profile_utils import get_user_profile, update_user_profile
from utils.accounts_utils import (
    get_trading_accounts, add_trading_account,
    update_trading_account, delete_trading_account
)

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Gestão")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("⚙️ Gestão")
st.caption("Gira o seu perfil de trader e as suas contas de trading num único local.")
st.markdown("---")

# --- LÓGICA DA PÁGINA ---
user_id = st.session_state['user_info'].get('localId')
if not user_id:
    st.error("Não foi possível identificar o utilizador. Por favor, faça o login novamente.")
    st.stop()

# --- ABAS PARA ORGANIZAÇÃO ---
tab_profile, tab_accounts = st.tabs(["👤 Perfil do Trader", "🏦 Contas de Trading"])

# --- ABA 1: PERFIL DO TRADER ---
with tab_profile:
    st.header("As suas Informações de Perfil")
    with st.spinner("A carregar perfil..."):
        profile_data = get_user_profile(user_id)

    if profile_data is not None:
        with st.form("edit_profile_form"):
            current_name = profile_data.get("name", "")
            current_bio = profile_data.get("bio", "")
            trader_types = ["Day Trader", "Swing Trader", "Position Trader", "Scalper", "Investidor"]
            current_type_index = trader_types.index(profile_data["trader_type"]) if "trader_type" in profile_data and profile_data["trader_type"] in trader_types else 0

            name = st.text_input("Nome ou Pseudónimo", value=current_name)
            bio = st.text_area("Bio / Breve Descrição", value=current_bio, height=150)
            trader_type = st.selectbox("Principal Estilo Operacional", options=trader_types, index=current_type_index)
            
            if st.form_submit_button("✔️ Guardar Perfil", use_container_width=True):
                new_profile_data = {"name": name, "bio": bio, "trader_type": trader_type}
                if update_user_profile(user_id, new_profile_data):
                    st.success("Perfil atualizado com sucesso!")
                    st.rerun()

# --- ABA 2: CONTAS DE TRADING ---
with tab_accounts:
    st.header("As suas Contas de Trading")
    
    # Formulário para adicionar nova conta
    with st.expander("➕ Adicionar Nova Conta de Trading"):
        with st.form("new_account_form", clear_on_submit=True):
            cols = st.columns([2, 1, 1])
            with cols[0]:
                acc_name = st.text_input("Nome da Conta", placeholder="Ex: Minha Conta FTMO")
            with cols[1]:
                acc_capital = st.number_input("Capital Inicial", min_value=0.0, format="%.2f")
            with cols[2]:
                acc_currency = st.selectbox("Moeda", ["USD", "EUR", "GBP", "JPY"])
            
            acc_type = st.selectbox("Tipo de Conta", ["Corretora Pessoal", "Mesa Proprietária (Avaliação)", "Mesa Proprietária (Financiado)"])
            
            if st.form_submit_button("Adicionar Conta", use_container_width=True):
                account_data = {"account_name": acc_name, "initial_capital": acc_capital, "account_type": acc_type, "currency": acc_currency}
                if add_trading_account(user_id, account_data):
                    st.success("Conta adicionada com sucesso!"); st.rerun()

    st.markdown("---")
    
    # Lista de contas existentes
    st.subheader("Contas Registadas")
    trading_accounts = get_trading_accounts(user_id)

    if not trading_accounts:
        st.info("Ainda não registou nenhuma conta de trading.")
    else:
        for account in trading_accounts:
            doc_id = account.get('doc_id')
            capital = float(account.get('initial_capital', 0))
            with st.expander(f"{account.get('account_name', 'N/A')} - {account.get('currency', 'USD')} {capital:,.2f}"):
                with st.form(f"edit_form_{doc_id}"):
                    ec1, ec2, ec3 = st.columns([2, 1, 1])
                    with ec1:
                        name_edit = st.text_input("Nome", value=account['account_name'], key=f"name_{doc_id}")
                    with ec2:
                        capital_edit = st.number_input("Capital", value=capital, format="%.2f", key=f"capital_{doc_id}")
                    with ec3:
                        curr_opts = ["USD", "EUR", "GBP", "JPY"]
                        curr_edit = st.selectbox("Moeda", options=curr_opts, index=curr_opts.index(account.get('currency', 'USD')), key=f"curr_{doc_id}")
                    
                    type_opts = ["Corretora Pessoal", "Mesa Proprietária (Avaliação)", "Mesa Proprietária (Financiado)"]
                    type_edit = st.selectbox("Tipo", options=type_opts, index=type_opts.index(account['account_type']), key=f"type_{doc_id}")

                    btn_c1, btn_c2, _ = st.columns([1, 1, 5])
                    with btn_c1:
                        if st.form_submit_button("Guardar", use_container_width=True):
                            updated_data = {"account_name": name_edit, "initial_capital": capital_edit, "account_type": type_edit, "currency": curr_edit}
                            if update_trading_account(user_id, doc_id, updated_data):
                                st.success("Conta atualizada!"); st.rerun()
                    with btn_c2:
                        if st.form_submit_button("Apagar", type="primary", use_container_width=True):
                            if delete_trading_account(user_id, doc_id):
                                st.success("Conta apagada!"); st.rerun()

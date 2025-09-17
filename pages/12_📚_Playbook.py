# synapse_desk/pages/12_📚_Playbook.py

import streamlit as st
from view_utils import setup_sidebar
from utils.playbook_utils import (
    get_playbook_setups, add_playbook_setup,
    update_playbook_setup, delete_playbook_setup
)
from utils.config import yahoo_finance_map

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Playbook de Setups")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("📚 Playbook de Setups")
st.caption("Formalize as suas estratégias. Defina as regras, opere com disciplina.")
st.markdown("---")

# --- LÓGICA DA PÁGINA ---
user_id = st.session_state['user_info'].get('localId')
if not user_id:
    st.error("Não foi possível identificar o utilizador. Por favor, faça o login novamente.")
    st.stop()

# --- FORMULÁRIO PARA ADICIONAR NOVO SETUP ---
with st.expander("➕ Adicionar Novo Setup ao Playbook", expanded=True):
    with st.form("new_setup_form", clear_on_submit=True):
        st.subheader("Detalhes do Setup")
        
        col1, col2 = st.columns(2)
        with col1:
            setup_name = st.text_input("Nome do Setup", placeholder="Ex: Retração à Média de 20 (H1)")
            assets = st.multiselect("Ativos Aplicáveis", options=list(yahoo_finance_map.keys()))
        with col2:
            timeframe = st.selectbox("Timeframe Principal", options=["M1", "M5", "M15", "H1", "H4", "Diário", "Semanal"])
        
        rules = st.text_area(
            "Regras de Entrada, Gestão e Saída",
            height=250,
            placeholder="Descreva as condições exatas para este setup.\n\nExemplo:\n1. Preço toca a MME 20 no H1.\n2. Aguardar por um candle de reversão claro (martelo, engolfo).\n3. Stop-loss posicionado abaixo da mínima do candle de sinal.\n4. Alvo no último topo/fundo relevante, com R:R mínimo de 1:2."
        )
        
        submitted = st.form_submit_button("Adicionar Setup")
        if submitted:
            if not all([setup_name, assets, timeframe, rules]):
                st.error("Por favor, preencha todos os campos para adicionar o setup.")
            else:
                setup_data = {
                    "setup_name": setup_name,
                    "assets": assets,
                    "timeframe": timeframe,
                    "rules": rules
                }
                if add_playbook_setup(user_id, setup_data):
                    st.success("Setup adicionado ao seu Playbook!")
                    st.rerun()
                else:
                    st.error("Ocorreu um erro ao guardar o setup.")

st.markdown("---")
st.header("Seu Arsenal de Setups")

# --- EXIBIÇÃO DOS SETUPS EXISTENTES ---
with st.spinner("A carregar setups do Playbook..."):
    setups = get_playbook_setups(user_id)

if not setups:
    st.info("O seu Playbook está vazio. Use o formulário acima para adicionar o seu primeiro setup.")
else:
    for setup in setups:
        doc_id = setup['doc_id']
        with st.expander(f"**{setup['setup_name']}** | Timeframe: {setup['timeframe']}"):
            
            with st.form(f"edit_form_{doc_id}"):
                st.subheader("Editar Setup")
                col1_edit, col2_edit = st.columns(2)
                
                with col1_edit:
                    name_edit = st.text_input("Nome do Setup", value=setup['setup_name'], key=f"name_{doc_id}")
                    assets_edit = st.multiselect("Ativos", options=list(yahoo_finance_map.keys()), default=setup.get('assets', []), key=f"assets_{doc_id}")
                with col2_edit:
                    tf_edit = st.selectbox("Timeframe", options=["M1", "M5", "M15", "H1", "H4", "Diário", "Semanal"], 
                                           index=["M1", "M5", "M15", "H1", "H4", "Diário", "Semanal"].index(setup['timeframe']), key=f"tf_{doc_id}")
                
                rules_edit = st.text_area("Regras", value=setup.get('rules', ''), height=250, key=f"rules_{doc_id}")

                col_actions = st.columns([1, 1, 5])
                with col_actions[0]:
                    if st.form_submit_button("Guardar", use_container_width=True):
                        updated_data = {"setup_name": name_edit, "assets": assets_edit, "timeframe": tf_edit, "rules": rules_edit}
                        if update_playbook_setup(user_id, doc_id, updated_data):
                            st.success("Setup atualizado!")
                            st.rerun()
                
                with col_actions[1]:
                    if st.form_submit_button("Apagar", type="primary", use_container_width=True):
                        if delete_playbook_setup(user_id, doc_id):
                            st.success("Setup apagado do seu Playbook!")
                            st.rerun()

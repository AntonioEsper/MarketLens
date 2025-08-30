# marketlens/pages/9_📓_Journaling.py

import streamlit as st
from view_utils import setup_sidebar
from firebase_config import db
from datetime import date
import pandas as pd # Importa a biblioteca Pandas

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="MarketLens | Journaling",
    page_icon="📓",
    layout="wide"
)

# --- GESTÃO DA BARRA LATERAL E AUTENTICAÇÃO ---
setup_sidebar()

# Guarda de autenticação
if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login para aceder a esta página.")
    st.info("Navegue para a página 'Login' no menu à esquerda.")
    st.stop()

# --- CONTEÚDO DA PÁGINA DE JOURNALING ---

st.title("📓 Diário de Trading (Journaling)")
st.markdown("---")

st.header("Registar Nova Operação")

# --- FORMULÁRIO PARA INSERIR DADOS ---
with st.form("journal_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        trade_asset = st.text_input("Ativo", placeholder="Ex: PETR4, EUR/USD")
        trade_date = st.date_input("Data da Operação", value=date.today())

    with col2:
        trade_type = st.selectbox("Tipo de Operação", ["Compra", "Venda"])
        entry_price = st.number_input("Preço de Entrada", min_value=0.0, format="%.5f")

    with col3:
        exit_price = st.number_input("Preço de Saída (opcional)", min_value=0.0, format="%.5f")
        trade_result = st.selectbox("Resultado", ["Positivo", "Negativo", "Neutro", "Em Aberto"], index=3)

    trade_strategy = st.text_area("Estratégia Utilizada", placeholder="Descreva a sua estratégia, gatilhos de entrada, etc.")
    trade_notes = st.text_area("Notas e Emoções", placeholder="Descreva como se sentiu, o que aprendeu, etc.")

    submit_button = st.form_submit_button("Registar Operação")

# --- LÓGICA DE SUBMISSÃO ---
if submit_button:
    if not trade_asset:
        st.error("O campo 'Ativo' é obrigatório.")
    else:
        try:
            user_id = st.session_state['user_info']['localId']
            trade_data = {
                "asset": trade_asset, "date": str(trade_date), "type": trade_type,
                "entry_price": entry_price, "exit_price": exit_price, "result": trade_result,
                "strategy": trade_strategy, "notes": trade_notes
            }
            db.collection("users").document(user_id).collection("journal").add(trade_data)
            st.success("Operação registada com sucesso na base de dados!")
            st.balloons()
        except Exception as e:
            st.error(f"Ocorreu um erro ao registar a operação: {e}")

st.markdown("---")
st.header("Minhas Operações Registadas")

# --- LÓGICA PARA LER E EXIBIR OS DADOS ---
try:
    user_id = st.session_state['user_info']['localId']
    # Acede à coleção 'journal' do utilizador logado
    journal_ref = db.collection("users").document(user_id).collection("journal")
    # Obtém todos os documentos (operações) da coleção
    docs = journal_ref.stream()

    # Cria uma lista para armazenar os dados de cada operação
    trades_list = []
    for doc in docs:
        trade = doc.to_dict()
        trade['id'] = doc.id # Guarda também o ID do documento, pode ser útil no futuro
        trades_list.append(trade)

    # Verifica se foram encontradas operações
    if trades_list:
        # Converte a lista de dicionários para um DataFrame do Pandas
        df = pd.DataFrame(trades_list)
        
        # Reordena as colunas para uma visualização mais lógica
        column_order = ['date', 'asset', 'type', 'entry_price', 'exit_price', 'result', 'strategy', 'notes', 'id']
        # Filtra para usar apenas as colunas que existem no DataFrame
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # Exibe o DataFrame como uma tabela interativa na aplicação
        st.dataframe(df)
    else:
        st.info("Nenhuma operação registada até ao momento. Utilize o formulário acima para começar.")

except Exception as e:
    st.error("Não foi possível carregar o histórico de operações.")
    st.error(f"Detalhe do erro: {e}")

# marketlens/utils/economic_loader.py

import streamlit as st
import pandas as pd
from fredapi import Fred
from datetime import datetime, timedelta
from io import StringIO # CORREÇÃO: Importa a classe StringIO

# --- INICIALIZAÇÃO DAS CONEXÕES ---
try:
    fred_api_key = st.secrets["FRED_API_KEY"]
    fred = Fred(api_key=fred_api_key)
except Exception as e:
    st.error("Chave da API do FRED não encontrada ou inválida nos segredos.")
    fred = None

if 'db' in st.session_state:
    db = st.session_state['db']
else:
    from firebase_config import initialize_firebase_admin
    db = initialize_firebase_admin()

# --- FUNÇÃO PRINCIPAL DE CARREGAMENTO DE DADOS ---
def get_economic_data(series_name: str, series_id: str, cache_days: int = 30):
    if not fred or not db:
        st.error("A conexão com o FRED ou Firestore não está disponível.")
        return None

    doc_ref = db.collection("macro_data").document(series_id)
    
    try:
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            last_updated = data['last_updated'].replace(tzinfo=None)
            
            if datetime.utcnow() - last_updated < timedelta(days=cache_days):
                print(f"CACHE HIT: Carregando '{series_name}' do Firestore.")
                # CORREÇÃO: Usa StringIO para ler a string JSON, resolvendo o FutureWarning.
                df = pd.read_json(StringIO(data['data_json']), orient='split')
                return df

        print(f"CACHE MISS: Buscando '{series_name}' da API do FRED.")
        data_series = fred.get_series(series_id)
        
        if data_series.empty:
            st.warning(f"Nenhum dado encontrado para a série '{series_name}' ({series_id}).")
            return None
            
        df = pd.DataFrame(data_series, columns=['value']).dropna()
        data_json = df.to_json(orient='split')
        
        payload = {
            'series_name': series_name,
            'last_updated': datetime.utcnow(),
            'data_json': data_json
        }
        doc_ref.set(payload)
        print(f"CACHE WRITE: Dados de '{series_name}' atualizados no Firestore.")

        return df

    except Exception as e:
        st.error(f"Ocorreu um erro ao obter os dados para '{series_name}': {e}")
        return None

# --- FIM DO MÓDULO economic_loader.py ---
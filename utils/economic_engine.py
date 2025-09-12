# marketlens/utils/economic_engine.py

import streamlit as st
import pandas as pd
from fredapi import Fred
from .config import FRED_SERIES_MAP
from firebase_config import db # Importa a nossa instância do Firestore

def update_fred_data_in_firestore():
    """
    Função principal do motor de dados económicos.

    Itera sobre todos os indicadores definidos no FRED_SERIES_MAP,
    busca o seu histórico completo na API do FRED e armazena os
    dados numa coleção dedicada no Firestore.

    Esta função foi desenhada para ser executada sob demanda para popular
    ou atualizar o nosso "data warehouse".
    """
    
    # Validação inicial para garantir que a conexão com o Firestore está ativa.
    if not db:
        st.error("A conexão com o Firestore não está disponível. O motor de dados não pode continuar.")
        return

    try:
        # Inicializa a API do FRED com a chave guardada nos segredos do Streamlit.
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
    except Exception as e:
        st.error(f"Não foi possível inicializar a API do FRED. Verifique a sua chave. Erro: {e}")
        return

    st.info(f"Iniciando a atualização de {len(FRED_SERIES_MAP)} séries de dados económicos...")
    
    success_count = 0
    # Itera sobre cada item no nosso dicionário de configuração.
    for series_name, series_info in FRED_SERIES_MAP.items():
        series_id = series_info['id']
        
        with st.spinner(f"Processando: {series_name}..."):
            try:
                # 1. BUSCAR DADOS DA API DO FRED
                # Busca o histórico completo da série de dados.
                data = fred.get_series(series_id)
                data = data.dropna() # Remove quaisquer valores nulos.

                if data.empty:
                    st.warning(f"Não foram encontrados dados para {series_name} ({series_id}).")
                    continue

                # 2. PREPARAR DADOS PARA O FIRESTORE
                # Converte os dados para um formato JSON (string).
                # O Firestore lida bem com strings longas e este formato preserva
                # a estrutura de data e valor.
                data_json = data.to_json(orient='split', date_format='iso')

                # 3. ARMAZENAR DADOS NO FIRESTORE
                # Define o caminho no Firestore: /economic_data/{Nome da Série}
                # Usamos o nome amigável como ID do documento para facilitar a identificação.
                doc_ref = db.collection("economic_data").document(series_name)
                
                # Guarda os dados. O método 'set' cria o documento se não existir
                # ou sobrescreve-o se já existir.
                doc_ref.set({
                    "series_id": series_id,
                    "currency_impact": series_info['currency'],
                    "last_updated": pd.Timestamp.now().isoformat(),
                    "history_json": data_json
                })
                
                st.write(f"✅ {series_name}: Dados históricos guardados com sucesso no Firestore.")
                success_count += 1

            except Exception as e:
                st.error(f"❌ Falha ao processar {series_name}. Erro: {e}")

    st.success(f"Operação concluída! {success_count} de {len(FRED_SERIES_MAP)} séries foram atualizadas com sucesso.")

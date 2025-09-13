# marketlens/utils/economic_engine.py

import pandas as pd
import streamlit as st
from firebase_config import db
from fredapi import Fred
from .config import FRED_SERIES_MAP

def update_fred_data_in_firestore():
    """
    Motor que busca o histórico de dados económicos do FRED e os armazena no Firestore.
    Esta função foi atualizada para ser um gerador, emitindo mensagens de status.
    """
    try:
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
    except Exception as e:
        yield f"❌ Falha ao inicializar a API do FRED. Verifique a sua API Key. Erro: {e}"
        return

    if not FRED_SERIES_MAP:
        yield "❌ O `FRED_SERIES_MAP` no ficheiro de configuração está vazio."
        return

    total_series = len(FRED_SERIES_MAP)
    yield f"ℹ️ A iniciar a atualização para {total_series} séries económicas..."

    for i, (series_name, series_info) in enumerate(FRED_SERIES_MAP.items()):
        series_id = series_info.get("id")
        if not series_id:
            yield f"({i+1}/{total_series}) ⚠️ Aviso: Série '{series_name}' não tem um ID definido. A ignorar."
            continue
        
        try:
            yield f"({i+1}/{total_series}) 🔄 A buscar dados para '{series_name}'..."
            
            # Busca os dados da API do FRED
            df_series = fred.get_series(series_id).dropna()

            if not df_series.empty:
                # Converte o índice para string para ser compatível com JSON/Firestore
                df_series.index = df_series.index.strftime('%Y-%m-%d')
                # Converte a Série para um dicionário
                data_to_store = df_series.to_dict()

                # O nome do documento será o ID da série para garantir unicidade
                doc_ref = db.collection("economic_data").document(series_id)
                doc_ref.set({"history": data_to_store, "name": series_name})

                yield f"({i+1}/{total_series}) ✅ Sucesso: Dados de '{series_name}' guardados no Firestore."
            else:
                yield f"({i+1}/{total_series}) ⚠️ Aviso: Não foram encontrados dados para '{series_name}'."

        except Exception as e:
            yield f"({i+1}/{total_series}) ❌ Falha ao processar {series_name}. Erro: {e}"

    yield "✅ Processo Concluído!"


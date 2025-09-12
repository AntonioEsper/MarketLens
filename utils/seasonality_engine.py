# marketlens/utils/seasonality_engine.py

import streamlit as st
import pandas as pd
import yfinance as yf
from firebase_config import db
from .config import yahoo_finance_map

def update_seasonality_data_in_firestore(years=15):
    """
    Busca o histórico de preços para todos os ativos, calcula a sazonalidade
    mensal média e armazena os resultados no Firestore.
    """
    st.info("🚀 A iniciar o motor de dados de Sazonalidade...")
    
    if not yahoo_finance_map:
        st.error("O mapa de ativos do Yahoo Finance (`yahoo_finance_map`) não foi encontrado.")
        return

    # Usamos os nomes dos ativos do mapa como a nossa lista de tarefas.
    asset_list = list(yahoo_finance_map.keys())
    total_assets = len(asset_list)
    progress_bar = st.progress(0, text=f"A processar 0 de {total_assets} ativos...")

    for i, asset_name in enumerate(asset_list):
        ticker = yahoo_finance_map.get(asset_name)
        if not ticker:
            continue

        progress_text = f"A processar {i+1} de {total_assets}: {asset_name}"
        progress_bar.progress((i + 1) / total_assets, text=progress_text)
        
        try:
            st.write(f"🔄 A buscar histórico de {years} anos para **{asset_name}** ({ticker})...")
            
            # Busca um longo período de dados históricos para o cálculo.
            hist_data = yf.download(ticker, period=f"{years}y", progress=False, auto_adjust=True)

            if hist_data.empty or 'Close' not in hist_data.columns:
                st.warning(f"⚠️ Não foram encontrados dados de preços suficientes para {asset_name}. A saltar.")
                continue

            # Calcula a sazonalidade.
            hist_data['month'] = hist_data.index.month
            hist_data['returns'] = hist_data['Close'].pct_change()
            monthly_seasonality = hist_data.groupby('month')['returns'].mean() * 100

            # Prepara os dados para o Firestore (um dicionário de strings).
            # Ex: {'1': 0.5, '2': -1.2, ...}
            seasonality_dict = {str(month): avg_return for month, avg_return in monthly_seasonality.to_dict().items()}
            
            # Sanitiza o nome do ativo para ser um ID de documento válido.
            sanitized_asset_name = asset_name.replace('/', '_')
            
            # Guarda no Firestore.
            doc_ref = db.collection("seasonality_data").document(sanitized_asset_name)
            doc_ref.set(seasonality_dict)

            st.write(f"✅ Padrão de sazonalidade para **{asset_name}** guardado com sucesso.")

        except Exception as e:
            st.error(f"❌ Falha ao processar sazonalidade para {asset_name}. Erro: {e}")

    progress_bar.empty()
    st.success("🎉 **Motor de dados de Sazonalidade concluído!** A sua base de dados está atualizada.")
# --- FIM DO MÓDULO seasonality_engine.py ---
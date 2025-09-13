# marketlens/utils/seasonality_engine.py

import pandas as pd
import streamlit as st
from firebase_config import db
from .config import yahoo_finance_map
from .data_loader import get_yfinance_data

def update_seasonality_data_in_firestore():
    """
    Motor que calcula a performance média mensal de cada ativo e armazena no Firestore.
    Esta função foi refatorada para ser um gerador, emitindo mensagens de status.
    """
    assets_to_process = yahoo_finance_map
    if not assets_to_process:
        yield "❌ O `yahoo_finance_map` no ficheiro de configuração está vazio."
        return

    total_assets = len(assets_to_process)
    yield f"ℹ️ A iniciar o cálculo de sazonalidade para {total_assets} ativos..."

    for i, (asset_name, ticker) in enumerate(assets_to_process.items()):
        # Ignora os indicadores que não são relevantes para a análise de sazonalidade de preço
        if asset_name in ["DXY", "VIX"]:
            continue
            
        try:
            yield f"({i+1}/{total_assets}) 🔄 A buscar histórico de preços para {asset_name}..."
            
            # Busca um longo período de dados para um cálculo robusto
            df_price = get_yfinance_data(ticker, period="15y")

            if df_price is not None and not df_price.empty:
                # Usa a primeira coluna como referência de preço
                price_series = df_price.iloc[:, 0]
                
                # Calcula os retornos mensais
                monthly_returns = price_series.pct_change(periods=21).dropna() # Usa ~21 dias de trading num mês
                
                # Agrupa os retornos por mês
                seasonality_data = monthly_returns.groupby(monthly_returns.index.month).agg(['mean', 'std', lambda x: (x > 0).sum() / len(x)])
                seasonality_data.columns = ['mean_return', 'std_dev', 'positive_months_pct']
                
                # Mapeia o número do mês para o nome abreviado
                month_map = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
                seasonality_data.index = seasonality_data.index.map(month_map)
                
                # Converte os dados para um formato adequado para o Firestore
                data_to_store = (seasonality_data * 100).to_dict(orient='index') # Guarda como percentagens

                # Sanitiza o nome do ativo para ser um ID de documento válido
                sanitized_asset_name = asset_name.replace('/', '_')
                doc_ref = db.collection("seasonality_data").document(sanitized_asset_name)
                doc_ref.set(data_to_store)

                yield f"({i+1}/{total_assets}) ✅ Sucesso: Sazonalidade de {asset_name} guardada no Firestore."
            else:
                yield f"({i+1}/{total_assets}) ⚠️ Aviso: Não foram encontrados dados de preços para {asset_name}."

        except Exception as e:
            yield f"({i+1}/{total_assets}) ❌ Falha ao processar {asset_name}. Erro: {e}"

    yield "✅ Processo Concluído!"


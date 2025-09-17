# synapse_desk/utils/data_loader.py

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# --- FUNÇÃO DE CARREGAMENTO DE DADOS DE PREÇOS ---

@st.cache_data(ttl=900) # Cache de 15 minutos para dados de preço
def get_yfinance_data(tickers, period="5y", start=None, end=None, include_ohlc=False):
    """
    Busca dados de preços do Yahoo Finance de forma robusta.

    Args:
        tickers (str or list): O(s) ticker(s) do(s) ativo(s).
        period (str, optional): O período a ser buscado (ex: "1y", "5y"). Defaults to "5y".
        start (str, optional): Data de início (YYYY-MM-DD). Defaults to None.
        end (str, optional): Data de fim (YYYY-MM-DD). Defaults to None.
        include_ohlc (bool, optional): Se True, tenta retornar as colunas Open, High, Low, Close.
                                     Defaults to False.

    Returns:
        pd.DataFrame: Um DataFrame com os dados do ativo. Retorna um DataFrame vazio em caso de erro.
    """
    try:
        data = yf.download(
            tickers=tickers,
            period=period,
            start=start,
            end=end,
            progress=False,
            auto_adjust=True # auto_adjust=True já remove colunas como "Adj Close"
        )
        if data.empty:
            return pd.DataFrame()
        
        # Se for um único ticker e pedimos OHLC, retorna o DataFrame completo
        if isinstance(tickers, str) and include_ohlc:
            return data
            
        # Para múltiplos tickers, ou se não pedimos OHLC, retorna apenas o 'Close'
        if 'Close' in data.columns:
            return data[['Close']]
        else:
            # Fallback para o caso de retornar uma única série ou múltiplos tickers
            if isinstance(data.columns, pd.MultiIndex):
                return data.get('Close', pd.DataFrame())
            else:
                return data.to_frame(name=tickers)

    except Exception as e:
        st.error(f"Erro ao buscar dados do yfinance para {tickers}: {e}")
        return pd.DataFrame()


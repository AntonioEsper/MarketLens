# marketlens/utils/data_loader.py

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from fredapi import Fred
import investpy # Importa a nova biblioteca para o calendário

# --- CONFIGURAÇÃO DAS APIs ---
try:
    FRED_API_KEY = st.secrets["FRED_API_KEY"]
    fred = Fred(api_key=FRED_API_KEY)
except (KeyError, Exception):
    st.error("Chave da API do FRED não encontrada ou inválida. Por favor, configure em .streamlit/secrets.toml")
    st.stop()

# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---

@st.cache_data(ttl=900)
def get_yfinance_data(tickers, period=None, start=None, end=None):
    """
    Busca dados de preços de fecho do Yahoo Finance.
    - Aceita tanto 'period' (ex: "1y") quanto 'start'/'end' dates.
    """
    try:
        data = yf.download(
            tickers=tickers, 
            period=period, 
            start=start,
            end=end,
            progress=False, 
            auto_adjust=True
        )
        
        if data.empty:
            st.warning(f"Não foram encontrados dados no yfinance para: {tickers}")
            return pd.DataFrame()

        # Extrai a coluna 'Close' para múltiplos ou um único ticker
        if isinstance(data.columns, pd.MultiIndex):
            return data['Close']
        elif 'Close' in data.columns:
            return data[['Close']] 
        else:
            return data

    except Exception as e:
        st.error(f"Erro ao buscar dados do yfinance para {tickers}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=86400)
def get_fred_data(series_id):
    """
    Busca uma única série de dados da API do FRED.
    """
    try:
        data = fred.get_series(series_id)
        return data.dropna()
    except Exception as e:
        st.error(f"Erro ao buscar dados do FRED para a série {series_id}: {e}")
        return pd.Series(dtype=float)

@st.cache_data(ttl=604800)
def get_cot_data(series_id):
    """
    Busca dados do Commitment of Traders (COT) a partir do FRED.
    (Atualmente em manutenção no frontend, mas a função permanece para consistência)
    """
    return get_fred_data(series_id)

@st.cache_data(ttl=3600) # Cache de 1 hora
def get_economic_calendar_data(countries=['united states', 'euro zone', 'united kingdom', 'japan'], importance_level='high'):
    """
    Busca os eventos do calendário económico para a semana corrente.
    """
    try:
        df = investpy.news.economic_calendar(
            countries=countries,
            importance=importance_level
        )
        # Assegura que a coluna 'date' está no formato datetime
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
        return df[['date', 'time', 'currency', 'event', 'importance']]
    except Exception as e:
        st.error(f"Ocorreu um erro ao buscar os dados do Calendário Económico: {e}")
        return pd.DataFrame()


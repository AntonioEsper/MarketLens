# marketlens/utils/data_loader.py

import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from sodapy import Socrata

# --- CONFIGURAÇÃO DAS APIs ---
try:
    cftc_client = Socrata("publicreporting.cftc.gov", None)
except Exception as e:
    st.error(f"Não foi possível inicializar o cliente da API da CFTC: {e}")
    cftc_client = None

# --- FUNÇÕES DE CARREGAMENTO DE DADOS ---

@st.cache_data(ttl=900)
def get_yfinance_data(tickers, period=None, start=None, end=None, include_ohlc=False):
    """ Busca dados de preços do Yahoo Finance. """
    try:
        data = yf.download(
            tickers=tickers, period=period, start=start, end=end,
            progress=False, auto_adjust=True
        )
        if data.empty:
            return pd.DataFrame()
        
        # Se for um único ticker e precisarmos de OHLC, retorna o DF completo
        if isinstance(tickers, str) and include_ohlc:
            return data
            
        # Para múltiplos tickers, ou se não precisarmos de OHLC, retorna apenas o 'Close'
        if isinstance(data.columns, pd.MultiIndex):
            # Para múltiplos tickers, yfinance retorna um MultiIndex. Pegamos apenas o 'Close'.
            return data.get('Close', pd.DataFrame())
        elif 'Close' in data.columns:
            return data[['Close']]
        else:
            # Fallback para o caso de retornar uma única série (sem coluna 'Close')
            return data.to_frame(name='Close')

    except Exception as e:
        st.error(f"Erro ao buscar dados do yfinance para {tickers}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=604800) # Cache de 7 dias
def get_cot_data(contract_code, years=3):
    """
    Busca dados do Commitment of Traders (COT) da API da CFTC,
    usando a estratégia de filtragem correta baseada no contract_code.
    """
    if not cftc_client:
        st.error("Cliente da API da CFTC não está disponível.")
        return None

    try:
        # ID do dataset para "Legacy Combined Report", conforme a pesquisa
        dataset_id = "jun7-fc8e"
        
        start_date = (datetime.now() - pd.DateOffset(years=years)).strftime('%Y-%m-%dT00:00:00.000')
        
        # Constrói a query SoQL usando o cftc_contract_market_code, a forma robusta de filtrar
        query = (
            f"cftc_contract_market_code = '{contract_code}' "
            f"AND report_date_as_yyyy_mm_dd >= '{start_date}'"
        )
        
        results = cftc_client.get(dataset_id, where=query, order="report_date_as_yyyy_mm_dd DESC", limit=500)
        
        if not results:
            st.warning(f"Não foram encontrados dados do COT para o código de contrato: {contract_code}")
            return None

        df = pd.DataFrame.from_records(results)
        
        # Colunas essenciais que precisamos para a análise "Institucional vs. Varejo"
        required_columns = [
            'report_date_as_yyyy_mm_dd',
            'noncomm_positions_long_all',
            'noncomm_positions_short_all',
            'nonrept_positions_long_all',
            'nonrept_positions_short_all'
        ]

        for col in required_columns:
            if col not in df.columns:
                st.error(f"A coluna esperada '{col}' não foi encontrada nos dados da CFTC.")
                return None
        
        # Converte as colunas para os tipos corretos
        df['report_date_as_yyyy_mm_dd'] = pd.to_datetime(df['report_date_as_yyyy_mm_dd'])
        numeric_cols = required_columns[1:] # Todas menos a data
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df = df.dropna(subset=numeric_cols)
        
        # Renomeia as colunas para um formato mais limpo para o dashboard
        rename_map = {
            'noncomm_positions_long_all': 'noncomm_long',
            'noncomm_positions_short_all': 'noncomm_short',
            'nonrept_positions_long_all': 'nonrept_long',
            'nonrept_positions_short_all': 'nonrept_short'
        }
        df = df.rename(columns=rename_map)

        df = df.set_index('report_date_as_yyyy_mm_dd').sort_index()

        return df[['noncomm_long', 'noncomm_short', 'nonrept_long', 'nonrept_short']]

    except Exception as e:
        st.error(f"Ocorreu um erro ao buscar os dados do COT para o contrato {contract_code}: {e}")
        return None

# Manteremos a função do FRED para o futuro Synapse Score
@st.cache_data(ttl=86400)
def get_fred_data(series_id):
    """ Busca uma única série de dados da API do FRED. """
    try:
        from fredapi import Fred
        fred = Fred(api_key=st.secrets["FRED_API_KEY"])
        data = fred.get_series(series_id)
        return data.dropna()
    except Exception as e:
        st.error(f"Erro ao buscar dados do FRED para a série {series_id}: {e}")
        return pd.Series(dtype=float)


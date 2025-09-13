# marketlens/utils/heatmap_engine.py

import pandas as pd
import streamlit as st
from .config import FRED_SERIES_MAP
from .scoring_engine import get_economic_data_from_firestore # Reutiliza a nossa função de leitura

@st.cache_data(ttl=3600) # Cache de 1 hora
def get_momentum_heatmap_data():
    """
    Cria a tabela para o "Heatmap de Momentum Económico" usando os dados do FRED
    armazenados no nosso Firestore.

    1. Itera sobre os indicadores dos EUA definidos no config.
    2. Lê o histórico de cada um a partir do Firestore.
    3. Calcula o "Momentum" (último valor vs. média de 12 meses).
    4. Determina o "Impacto" (Bullish/Bearish) com base no momentum.
    """
    results = []
    
    # Filtra apenas os indicadores dos EUA
    us_indicators = {name: info for name, info in FRED_SERIES_MAP.items() if info["currency"] == "USD"}

    for series_name, series_info in us_indicators.items():
        series_id = series_info.get("id")
        impact_direction = series_info.get("impact_on_currency", "positive")
        
        series_data = get_economic_data_from_firestore(series_id)
        
        if series_data is not None and not series_data.empty and len(series_data) >= 12:
            latest_value = series_data.iloc[-1]
            latest_date = series_data.index[-1].strftime('%d-%b-%Y')
            sma_12 = series_data.rolling(window=12).mean().iloc[-1]
            
            # Determina a tendência e o impacto
            trend = "Acima da Média"
            impact = "Bullish"
            if latest_value < sma_12:
                trend = "Abaixo da Média"
                impact = "Bearish"
            
            # Inverte o impacto para indicadores negativos (ex: desemprego)
            if impact_direction == 'negative':
                impact = "Bearish" if impact == "Bullish" else "Bullish"

            results.append({
                "Indicador": series_name,
                "Último Valor": latest_value,
                "Data do Valor": latest_date,
                "Tendência (vs. Média 12M)": trend,
                "Impacto": impact
            })

    if not results:
        st.error("Não foi possível gerar o Heatmap. Execute o motor de dados económicos primeiro.")
        return pd.DataFrame()

    return pd.DataFrame(results)


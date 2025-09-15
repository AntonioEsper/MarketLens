# marketlens/utils/heatmap_engine.py

import pandas as pd
import streamlit as st
from .config import FRED_SERIES_MAP
# CORREÇÃO: Reutiliza a função de leitura do scoring_engine para manter a consistência
from .scoring_engine import get_economic_data_from_firestore 

@st.cache_data(ttl=3600) # Cache de 1 hora
def get_momentum_heatmap_data():
    """
    Cria a tabela para o "Heatmap de Momentum Económico" com análise de impacto duplo.
    Esta versão foi refatorada para ler dinamicamente do FRED_SERIES_MAP.
    """
    results = []
    
    # Filtra apenas os indicadores dos EUA que estão no nosso mapa de configuração
    us_indicators = {
        name: info for name, info in FRED_SERIES_MAP.items() 
        if info.get("currency") == "USD"
    }

    if not us_indicators:
        st.error("Nenhum indicador económico dos EUA encontrado no ficheiro de configuração (config.py).")
        return pd.DataFrame()

    for series_name, series_info in us_indicators.items():
        series_id = series_info.get("id")
        impact_on_currency = series_info.get("impact_on_currency", "positive")
        impact_on_stocks = series_info.get("impact_on_stocks", "positive")
        
        # Usa a nossa função de leitura padronizada do Firestore
        series_data = get_economic_data_from_firestore(series_id)
        
        if series_data is not None and not series_data.empty and len(series_data) >= 12:
            latest_value = series_data.iloc[-1]
            latest_date = series_data.index[-1].strftime('%d-%b-%Y')
            sma_12 = series_data.rolling(window=12).mean().iloc[-1]
            
            is_above_average = latest_value > sma_12
            trend_text = "Acima da Média" if is_above_average else "Abaixo da Média"

            impact_usd = "Neutro"
            if (is_above_average and impact_on_currency == 'positive') or \
               (not is_above_average and impact_on_currency == 'negative'):
                impact_usd = "Bullish"
            elif (is_above_average and impact_on_currency == 'negative') or \
                 (not is_above_average and impact_on_currency == 'positive'):
                impact_usd = "Bearish"
            
            impact_stocks = "Neutro"
            if (is_above_average and impact_on_stocks == 'positive') or \
               (not is_above_average and impact_on_stocks == 'negative'):
                impact_stocks = "Bullish"
            elif (is_above_average and impact_on_stocks == 'negative') or \
                 (not is_above_average and impact_on_stocks == 'positive'):
                impact_stocks = "Bearish"

            results.append({
                "Indicador": series_name,
                "Último Valor": latest_value,
                "Data": latest_date,
                "Tendência": trend_text,
                "Impacto USD": impact_usd,
                "Impacto Stocks": impact_stocks
            })

    if not results:
        st.error("Não foi possível gerar o Heatmap. Execute o motor de dados económicos primeiro para popular o Firestore.")
        return pd.DataFrame()

    return pd.DataFrame(results)


# Módulo de Análise do MarketLens
# Contém a nova lógica de negócio para o Dashboard Macro.

import pandas as pd
from datetime import datetime

def calculate_global_risk_gauge(vix_series, dxy_series):
    """
    Calcula um score de risco global e um veredito com base no VIX e na tendência do DXY.
    Retorna um score (-2 a +2) e um texto (Risk-On, Neutro, Risk-Off).
    """
    if vix_series.empty or dxy_series.empty or len(dxy_series) < 20:
        return 0, "Indeterminado"

    # Pega nos dados mais recentes
    latest_vix = vix_series.iloc[-1]
    
    # Lógica de tendência para o DXY (baseada numa média móvel de 20 dias)
    dxy_sma20 = dxy_series.rolling(window=20).mean().iloc[-1]
    latest_dxy = dxy_series.iloc[-1]
    dxy_trend_is_up = latest_dxy > dxy_sma20

    # Lógica de Scoring
    score = 0
    # VIX é o principal indicador
    if latest_vix > 25:
        score -= 2 # Muito Risk-Off
    elif latest_vix > 20:
        score -= 1 # Risk-Off
    elif latest_vix < 15:
        score += 2 # Muito Risk-On
    elif latest_vix < 18:
        score += 1 # Risk-On
        
    # DXY é o indicador secundário de confirmação
    if dxy_trend_is_up and score <= 0:
        score -= 0.5 # Confirmação de aversão ao risco
    elif not dxy_trend_is_up and score >= 0:
        score += 0.5 # Confirmação de apetite por risco

    # Normaliza o score para o intervalo [-2, 2]
    score = max(-2, min(2, score))

    # Lógica de Veredito
    if score >= 1.5:
        return score, "Risk-On 🔥"
    elif score > -1.5:
        return score, "Neutro ↔️"
    else:
        return score, "Risk-Off 🛡️"


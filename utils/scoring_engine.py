# marketlens/utils/scoring_engine.py

import pandas as pd
import streamlit as st
from firebase_config import db
from .config import FRED_SERIES_MAP, cot_market_map

# --- FUNÇÕES DE LEITURA DO FIRESTORE ---

def get_cot_history_from_firestore(asset_name):
    """Lê o histórico de dados do COT para um ativo a partir do Firestore."""
    sanitized_name = asset_name.replace('/', '_')
    doc_ref = db.collection("cot_data").document(sanitized_name)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index)
        return df.sort_index()
    return pd.DataFrame()

def get_seasonality_from_firestore(asset_name):
    """Lê os dados de sazonalidade para um ativo a partir do Firestore."""
    sanitized_name = asset_name.replace('/', '_')
    doc_ref = db.collection("seasonality_data").document(sanitized_name)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        df = pd.DataFrame.from_dict(data)
        return df
    return pd.DataFrame()

def get_economic_data_from_firestore(series_id):
    """Lê o histórico de uma série económica a partir do Firestore."""
    doc_ref = db.collection("economic_data").document(series_id)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict().get("history", {})
        series = pd.Series(data)
        series.index = pd.to_datetime(series.index)
        return series.sort_index()
    return pd.Series(dtype=float)

# --- FUNÇÕES DE CÁLCULO DE SCORE INDIVIDUAL ---

def score_cot_positioning(asset_name):
    """Calcula o score com base no posicionamento líquido do COT."""
    if asset_name not in cot_market_map:
        # CORREÇÃO: Retorna None em vez de uma string para manter a consistência do tipo de dados.
        return None, "N/A"
    
    df_cot = get_cot_history_from_firestore(asset_name)
    if df_cot.empty or len(df_cot) < 4:
        return 0, "Insuficiente"
    
    latest_report = df_cot.iloc[-1]
    net_noncomm = latest_report['noncomm_long'] - latest_report['noncomm_short']
    avg_net_noncomm = (df_cot['noncomm_long'] - df_cot['noncomm_short']).rolling(window=4).mean().iloc[-1]

    if net_noncomm > 0 and net_noncomm > avg_net_noncomm:
        return 1, "Bullish"
    elif net_noncomm < 0 and net_noncomm < avg_net_noncomm:
        return -1, "Bearish"
    return 0, "Neutro"

def score_seasonality(asset_name):
    """Calcula o score com base no padrão de sazonalidade para o mês atual."""
    df_seasonality = get_seasonality_from_firestore(asset_name)
    if df_seasonality.empty:
        return 0, "Neutro"

    current_month_name = pd.Timestamp.now().strftime('%b')
    if current_month_name in df_seasonality.index:
        avg_return = df_seasonality.loc[current_month_name, 'mean_return']
        if avg_return > 0.5:
            return 1, "Bullish"
        elif avg_return < -0.5:
            return -1, "Bearish"
    return 0, "Neutro"

def score_economic_indicator(series_data, impact_direction):
    """Calcula o score para um único indicador económico baseado no seu momentum."""
    if series_data.empty or len(series_data) < 12:
        return 0
        
    sma_12 = series_data.rolling(window=12).mean().iloc[-1]
    latest_value = series_data.iloc[-1]

    score = 0
    if latest_value > sma_12:
        score = 1
    elif latest_value < sma_12:
        score = -1

    if impact_direction == 'negative':
        score *= -1
    return score

# --- FUNÇÕES DE CÁLCULO DE SCORE AGREGADO ---

def calculate_overall_economic_score(currency):
    """Calcula o score económico agregado para uma determinada moeda."""
    total_score, count = 0, 0
    for series_name, series_info in FRED_SERIES_MAP.items():
        if series_info.get("currency") == currency:
            series_id = series_info.get("id")
            impact = series_info.get("impact_on_currency", "positive")
            series_data = get_economic_data_from_firestore(series_id)
            if not series_data.empty:
                total_score += score_economic_indicator(series_data, impact)
                count += 1
    return total_score / count if count > 0 else 0

def calculate_synapse_score(asset_name):
    """Função MESTRE que calcula o score final e os scores individuais para um ativo."""
    scores = {}
    
    cot_score, _ = score_cot_positioning(asset_name)
    scores['COT'] = cot_score

    seasonality_score, _ = score_seasonality(asset_name)
    scores['Sazonalidade'] = seasonality_score
    
    if "/" in asset_name:
        base_currency, quote_currency = asset_name.split('/')
        base_econ_score = calculate_overall_economic_score(base_currency)
        quote_econ_score = calculate_overall_economic_score(quote_currency)
        scores['Economia'] = round(base_econ_score - quote_econ_score, 2)
    else:
        scores['Economia'] = round(calculate_overall_economic_score("USD"), 2)

    # Filtra os scores nulos antes de somar
    valid_scores = [s for s in scores.values() if s is not None]
    final_score = sum(valid_scores)
    
    verdict = "Neutro"
    if final_score >= 1.5: verdict = "Very Bullish"
    elif final_score > 0.5: verdict = "Bullish"
    elif final_score <= -1.5: verdict = "Very Bearish"
    elif final_score < -0.5: verdict = "Bearish"

    return final_score, verdict, scores


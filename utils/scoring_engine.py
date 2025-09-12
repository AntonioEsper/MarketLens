# marketlens/utils/scoring_engine.py

import streamlit as st
import pandas as pd
from datetime import datetime
from firebase_config import db
from .config import cot_market_map, FRED_SERIES_MAP

# --- FUNÇÕES DE LEITURA DO FIRESTORE ---

def get_cot_history_from_firestore(sanitized_asset_name):
    """Lê o histórico de dados do COT do Firestore para um ativo específico."""
    try:
        doc_ref = db.collection("cot_data").document(sanitized_asset_name)
        doc = doc_ref.get()
        if doc.exists:
            data_dict = doc.to_dict()
            df = pd.DataFrame.from_dict(data_dict, orient='index')
            df.index = pd.to_datetime(df.index)
            # Converte colunas para numérico, tratando erros
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df.dropna()
            return df.sort_index()
        
        # --- MODIFICAÇÃO PARA DIAGNÓSTICO ---
        # Se o documento não for encontrado, exibe um aviso para nos ajudar a depurar.
        st.warning(f"Diagnóstico: Documento '{sanitized_asset_name}' não foi encontrado na coleção 'cot_data' do Firestore.")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"Erro ao ler dados do COT do Firestore para {sanitized_asset_name}: {e}")
        return pd.DataFrame()

def get_economic_data_from_firestore(series_id):
    """Lê o histórico de dados económicos do Firestore para uma série específica."""
    try:
        doc_ref = db.collection("economic_data").document(series_id)
        doc = doc_ref.get()
        if doc.exists:
            data_dict = doc.to_dict()
            df = pd.DataFrame(list(data_dict.items()), columns=['date', 'value'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna()
            return df.sort_index()
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao ler dados económicos do Firestore para {series_id}: {e}")
        return pd.DataFrame()

def get_seasonality_from_firestore(sanitized_asset_name):
    """Lê os dados de sazonalidade do Firestore para um ativo específico."""
    try:
        doc_ref = db.collection("seasonality_data").document(sanitized_asset_name)
        doc = doc_ref.get()
        if doc.exists:
            data_dict = doc.to_dict()
            df = pd.DataFrame.from_dict(data_dict, orient='index', columns=['average_return'])
            df.index = df.index.astype(int)
            return df.sort_index()
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao ler dados de sazonalidade do Firestore para {sanitized_asset_name}: {e}")
        return pd.DataFrame()

# --- FUNÇÕES DE CÁLCULO DE SCORE ---

def score_cot_positioning(asset_name):
    """Calcula o score de posicionamento do COT."""
    sanitized_name = asset_name.replace('/', '_')
    if asset_name not in cot_market_map:
        return 0, "N/A"

    df_cot = get_cot_history_from_firestore(sanitized_name)
    if df_cot.empty or len(df_cot) < 2:
        return 0, "Dados Insuficientes"

    latest = df_cot.iloc[-1]
    net_noncomm = latest['noncomm_long'] - latest['noncomm_short']
    
    score = 0
    if net_noncomm > 0:
        score = 2
        text = "Bullish"
    elif net_noncomm < 0:
        score = -2
        text = "Bearish"
    else:
        score = 0
        text = "Neutro"
        
    return score, text

def score_economic_momentum(currency):
    """Calcula um score de momentum económico agregado para uma moeda."""
    total_score = 0
    relevant_series_count = 0
    
    for series_name, series_info in FRED_SERIES_MAP.items():
        if series_info['currency'] == currency:
            relevant_series_count += 1
            df_econ = get_economic_data_from_firestore(series_info['id'])
            
            if not df_econ.empty and len(df_econ) >= 3:
                latest_value = df_econ['value'].iloc[-1]
                previous_value = df_econ['value'].iloc[-4] if len(df_econ) > 3 else df_econ['value'].iloc[0]
                
                if "Unemployment" in series_name:
                    if latest_value < previous_value: total_score += 1
                    elif latest_value > previous_value: total_score -= 1
                else:
                    if latest_value > previous_value: total_score += 1
                    elif latest_value < previous_value: total_score -= 1

    if relevant_series_count == 0:
        return 0, "N/A"
    
    avg_score = total_score / relevant_series_count
    
    if avg_score > 0.5: text = "Positivo"
    elif avg_score < -0.5: text = "Negativo"
    else: text = "Neutro"

    final_score = round(max(min(total_score, 2), -2))
    
    return final_score, text


def score_seasonality(asset_name):
    """Calcula o score de sazonalidade para o mês atual."""
    sanitized_name = asset_name.replace('/', '_')
    df_season = get_seasonality_from_firestore(sanitized_name)

    if df_season.empty:
        return 0, "N/A"

    current_month = datetime.now().month
    
    if current_month in df_season.index:
        monthly_return = df_season.loc[current_month, 'average_return']
        
        score = 0
        text = "Neutro"
        if monthly_return > 0.5:
            score = 2
            text = "Bullish"
        elif monthly_return < -0.5:
            score = -2
            text = "Bearish"
        return score, text
    
    return 0, "N/A"

# --- FUNÇÃO MESTRE ---

def calculate_synapse_score(asset_name):
    """
    Função mestre que calcula o score final para um ativo.
    """
    individual_scores = {}

    cot_score, cot_text = score_cot_positioning(asset_name)
    individual_scores['COT'] = {"score": cot_score, "text": cot_text}

    seasonality_score, seasonality_text = score_seasonality(asset_name)
    individual_scores['Sazonalidade'] = {"score": seasonality_score, "text": seasonality_text}

    total_score = cot_score + seasonality_score
    
    if total_score >= 3: verdict = "Very Bullish"
    elif total_score > 0: verdict = "Bullish"
    elif total_score <= -3: verdict = "Very Bearish"
    elif total_score < 0: verdict = "Bearish"
    else: verdict = "Neutral"

    return total_score, verdict, individual_scores


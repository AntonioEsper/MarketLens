# marketlens/utils/plot_utils.py

import pandas as pd
import streamlit as st

def prepare_seasonality_data_for_lines(df_price):
    """
    Prepara os dados de preços para o gráfico de linhas de sazonalidade.
    Normaliza os preços para que todos os anos comecem num ponto comum (0)
    para uma comparação visual justa da performance.
    """
    # CORREÇÃO: Remove a dependência da coluna 'Close' e usa a primeira coluna disponível.
    if df_price is None or df_price.empty:
        return pd.DataFrame()

    # Faz uma cópia para evitar erros de manipulação de dados (SettingWithCopyWarning)
    df = df_price.copy()

    # Usa o nome da primeira coluna como a coluna de preços
    price_col_name = df.columns[0]
    
    df['year'] = df.index.year
    df['month'] = df.index.month
    
    # Agrupa por ano e mês para obter o preço de fecho médio de cada mês
    monthly_prices = df.groupby(['year', 'month'])[price_col_name].mean().unstack(level='year')
    
    # Verifica se os dados são válidos antes de normalizar
    if monthly_prices.empty or (monthly_prices.iloc[0] == 0).any():
        return pd.DataFrame()

    # Normaliza os dados para começar em 0
    normalized_prices = (monthly_prices / monthly_prices.iloc[0] - 1) * 100
    
    # Mapeia o número do mês para o nome abreviado
    month_map = {
        1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
    }
    normalized_prices.index = normalized_prices.index.map(month_map)
    
    return normalized_prices

def calculate_cot_percentages(df_cot):
    """
    Calcula o percentual de posições Long vs. Short para Institucional e Varejo.
    """
    if df_cot is None or df_cot.empty:
        return pd.DataFrame()

    latest_report = df_cot.iloc[-1]
    
    total_noncomm = latest_report['noncomm_long'] + latest_report['noncomm_short']
    total_nonrept = latest_report['nonrept_long'] + latest_report['nonrept_short']
    
    if total_noncomm == 0 or total_nonrept == 0:
        return pd.DataFrame()

    data = {
        'Long': [
            (latest_report['noncomm_long'] / total_noncomm) * 100,
            (latest_report['nonrept_long'] / total_nonrept) * 100
        ],
        'Short': [
            (latest_report['noncomm_short'] / total_noncomm) * 100,
            (latest_report['nonrept_short'] / total_nonrept) * 100
        ]
    }
    
    result_df = pd.DataFrame(data, index=['Institucional', 'Varejo'])
    return result_df

def style_cot_table(val):
    """
    Aplica o estilo de cor à tabela de percentagens do COT.
    """
    if not isinstance(val, (int, float)):
        return ''
    if val > 60:
        return 'background-color: #006400; color: white;'
    elif val < 40:
        return 'background-color: #8B0000; color: white;'
    else:
        return ''


# marketlens/utils/plot_utils.py

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
from .data_loader import get_yfinance_data # Importa o nosso carregador de dados de preço

def prepare_seasonality_data_for_lines(df_price):
    """Prepara os dados de preços para o gráfico de linhas de sazonalidade."""
    if df_price is None or df_price.empty:
        return pd.DataFrame()
    df = df_price.copy()
    price_col_name = df.columns[0]
    df['year'] = df.index.year
    df['month'] = df.index.month
    monthly_prices = df.groupby(['year', 'month'])[price_col_name].mean().unstack(level='year')
    if monthly_prices.empty or (monthly_prices.iloc[0] == 0).any():
        return pd.DataFrame()
    normalized_prices = (monthly_prices / monthly_prices.iloc[0] - 1) * 100
    month_map = {1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun', 7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'}
    normalized_prices.index = normalized_prices.index.map(month_map)
    return normalized_prices

def calculate_cot_percentages(df_cot):
    """Calcula o percentual de posições Long vs. Short para Institucional e Varejo."""
    if df_cot is None or df_cot.empty:
        return pd.DataFrame()
    latest_report = df_cot.iloc[-1]
    total_noncomm = latest_report['noncomm_long'] + latest_report['noncomm_short']
    total_nonrept = latest_report['nonrept_long'] + latest_report['nonrept_short']
    if total_noncomm == 0 or total_nonrept == 0:
        return pd.DataFrame()
    data = {'Long': [(latest_report['noncomm_long'] / total_noncomm) * 100, (latest_report['nonrept_long'] / total_nonrept) * 100],
            'Short': [(latest_report['noncomm_short'] / total_noncomm) * 100, (latest_report['nonrept_short'] / total_nonrept) * 100]}
    return pd.DataFrame(data, index=['Institucional', 'Varejo'])

def style_cot_table(val):
    """Aplica o estilo de cor à tabela de percentagens do COT."""
    if not isinstance(val, (int, float)): return ''
    if val > 60: return 'background-color: #006400; color: white;'
    elif val < 40: return 'background-color: #8B0000; color: white;'
    return ''

def create_indicator_bar_chart(series_data, series_name):
    """Cria um gráfico de barras com os últimos 12 meses de um indicador económico."""
    if series_data is None or series_data.empty or len(series_data) < 12:
        return None
    last_12_months = series_data.loc[series_data.index.max() - pd.DateOffset(months=12):]
    if last_12_months.empty: return None
    average_12m = last_12_months.mean()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=last_12_months.index, y=last_12_months.values, name=series_name,
                         marker_color=['#4caf50' if v > average_12m else '#f44336' for v in last_12_months.values]))
    fig.add_trace(go.Scatter(x=last_12_months.index, y=[average_12m] * len(last_12_months), mode='lines',
                             name=f'Média ({average_12m:,.2f})', line=dict(color='yellow', dash='dash')))
    fig.update_layout(title=f'Histórico Mensal: {series_name}', plot_bgcolor='#131722', paper_bgcolor='#131722',
                      font_color='white', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

# --- NOVA FUNÇÃO PARA O GRÁFICO DE OPERAÇÕES DO JOURNALING 3.0 ---
def create_trade_chart(ticker, entry_date, exit_date, entry_price, exit_price, stop_loss):
    """
    Cria um gráfico de linha para uma operação específica, com anotações de entrada, saída e stop.
    """
    try:
        # Busca um período de tempo ligeiramente maior para dar contexto ao gráfico
        start_chart = pd.to_datetime(entry_date) - pd.Timedelta(days=5)
        # Se não houver data de saída, usa a data atual para definir o fim do gráfico
        end_chart = pd.to_datetime(exit_date if exit_date else datetime.now()) + pd.Timedelta(days=5)

        # Usa o nosso data_loader para buscar os dados de preço (OHLC)
        df_price = get_yfinance_data(ticker, start=start_chart.strftime('%Y-%m-%d'), end=end_chart.strftime('%Y-%m-%d'), include_ohlc=True)

        if df_price is None or df_price.empty or 'Close' not in df_price.columns:
            st.warning("Não foi possível obter dados de preço para gerar o gráfico.")
            return None

        fig = go.Figure()
        
        # Adiciona o gráfico de linha do preço de fecho
        fig.add_trace(go.Scatter(x=df_price.index, y=df_price['Close'], mode='lines', name='Preço', line=dict(color='grey', width=1)))

        # Adiciona as linhas horizontais para os níveis chave
        fig.add_hline(y=entry_price, line_width=2, line_dash="dash", line_color="cyan", annotation_text="Entrada", annotation_position="bottom right")
        fig.add_hline(y=stop_loss, line_width=2, line_dash="dash", line_color="red", annotation_text="Stop Loss", annotation_position="top right")
        if exit_price:
            fig.add_hline(y=exit_price, line_width=2, line_dash="dash", line_color="magenta", annotation_text="Saída", annotation_position="bottom right")

        fig.update_layout(
            title="Visualização Gráfica da Operação",
            plot_bgcolor='#131722', paper_bgcolor='#131722', font_color='white',
            showlegend=False, yaxis_title="Preço"
        )
        return fig

    except Exception as e:
        st.warning(f"Não foi possível gerar o gráfico da operação: {e}")
        return None


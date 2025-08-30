# Módulo de Componentes Visuais do MarketLens
# Contém funções reutilizáveis que geram elementos de UI, como gráficos.

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from .config import yahoo_finance_map
from .data_loader import get_yfinance_data

def create_simple_line_chart(data_series, title, color='#3b82f6', yaxis_title='Valor', height=300):
    """
    Cria um gráfico de linha simples e limpo com Plotly.
    - Adicionado parâmetro de 'height' para controlar a altura.
    - Lógica interna mais robusta para lidar com os dados.
    """
    if data_series is None or data_series.empty:
        return None
        
    fig = go.Figure()
    
    # Garante que os dados sejam sempre uma Série (1-dimensional)
    if isinstance(data_series, pd.DataFrame):
        if not data_series.empty:
            data_series = data_series.iloc[:, 0]
        else:
            return None

    fig.add_trace(go.Scatter(
        x=data_series.index, 
        y=data_series, 
        mode='lines', 
        name=title, 
        line=dict(color=color, width=2)
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=18)),
        plot_bgcolor='#131722',
        paper_bgcolor='#131722',
        font_color='#D9D9D9',
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title=yaxis_title,
        height=height, # Usa o novo parâmetro de altura
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    return fig

# NOTA: Outras funções de componentes visuais serão adicionadas aqui conforme necessário.
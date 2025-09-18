# marketlens/Início.py

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from view_utils import setup_sidebar
from utils.journal_utils import get_journal_entries
from utils.playbook_utils import get_playbook_setups
from utils.reporting_engine import calculate_dashboard_metrics
from utils.accounts_utils import get_trading_accounts

# --- FUNÇÕES AUXILIARES DE RENDERIZAÇÃO (COM SUPORTE A TEMAS) ---

def create_calendar_plot(pnl_data: pd.Series, theme: dict):
    """Cria um gráfico de heatmap para o mês atual, com cores de fundo contextuais."""
    plotly_layout = theme['plotly_layout']
    if pnl_data.empty:
        fig = go.Figure().update_layout(title_text="Sem dados para exibir", **plotly_layout)
        return fig

    today = datetime.now().date()
    start_date, end_date = today.replace(day=1), pd.to_datetime(today.replace(day=1)) + pd.offsets.MonthEnd(1)
    all_days = pd.date_range(start=start_date, end=end_date, freq='D')
    
    df_cal = pd.DataFrame(index=all_days).join(pnl_data.rename('pnl')).fillna(0)
    df_cal['day_of_week'] = df_cal.index.dayofweek
    df_cal['week_of_month'] = (df_cal.index.day - 1) // 7
    df_cal['day_text'] = df_cal.index.day
    
    fig = go.Figure(go.Heatmap(
        x=df_cal['week_of_month'], y=df_cal['day_of_week'], z=df_cal['pnl'], text=df_cal['day_text'], texttemplate="%{text}",
        colorscale=[[0, theme['loss_color']], [0.5, theme['calendar_neutral']], [1, theme['win_color']]],
        zmid=0, showscale=False, hoverongaps=False, hovertemplate='<b>%{customdata|%d/%m/%Y}</b><br>Resultado: $%{z:,.2f}<extra></extra>', customdata=df_cal.index
    ))
    fig.update_layout(
        **plotly_layout, height=300,
        yaxis=dict(autorange='reversed', showgrid=False, zeroline=False, tickvals=list(range(7)), ticktext=['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']),
        xaxis=dict(showgrid=False, zeroline=False, visible=False), title=dict(text=f"Performance Diária ({start_date.strftime('%B %Y')})", x=0.5), margin=dict(t=50, b=20, l=20, r=20)
    )
    return fig

def create_synapse_score_chart(score_data: dict, theme: dict):
    plotly_layout = theme['plotly_layout']
    categories = ['Taxa de Acerto', 'Rácio Lucro/Prejuízo', 'Fator de Lucro']
    win_rate, awl_ratio, profit_factor = score_data.get('win_rate', 0), score_data.get('avg_win_loss_ratio', 0), score_data.get('profit_factor', 0)
    awl_score, pf_score = min(awl_ratio, 3) / 3 * 100, min(profit_factor, 3) / 3 * 100
    
    fig = go.Figure(go.Scatterpolar(r=[win_rate, awl_score, pf_score], theta=categories, fill='toself', line=dict(color='cyan'), fillcolor='rgba(0, 255, 255, 0.4)'))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], color='grey'), angularaxis=dict(color=plotly_layout['font_color'])),
        **plotly_layout, showlegend=False, height=250, margin=dict(t=40, b=40, l=40, r=40)
    )
    return fig

def create_asset_pie_chart(asset_data: pd.Series, theme: dict):
    plotly_layout = theme['plotly_layout']
    if asset_data.empty:
        fig = go.Figure().update_layout(title_text="Sem dados de ativos", **plotly_layout)
        return fig
    
    fig = go.Figure(data=[go.Pie(labels=asset_data.index, values=asset_data.values, hole=.3, textinfo='percent', hoverinfo='label+value')])
    fig.update_layout(**plotly_layout, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5), height=350, margin=dict(t=40, b=20, l=20, r=20))
    return fig

def render_styled_trades_table(df, theme: dict):
    """Converte o DataFrame de trades recentes numa tabela HTML com estilos."""
    def style_row(row):
        resultado_color = theme['win_font'] if row['Resultado'] == 'Ganho' else theme['loss_font']
        direcao_color = theme['win_font'] if row['Direção'] == 'Compra' else theme['loss_font']
        pnl_str = f"${row['PnL (USD)']:,.2f}"
        rr_str = f"1:{row['RR']:.2f}" if pd.notna(row['RR']) else "N/A"
        return f"<tr><td>{row['Data']}</td><td>{row['Ativo']}</td><td style='color: {direcao_color};'>{row['Direção']}</td><td style='color: {resultado_color};'>{row['Resultado']}</td><td style='color: {resultado_color}; text-align: right;'>{pnl_str}</td><td style='text-align: right;'>{rr_str}</td></tr>"
    
    header = "".join([f"<th>{col}</th>" for col in df.columns])
    rows_html = "".join([style_row(row) for _, row in df.iterrows()])
    table_html = f"""<style>.styled-table {{ width: 100%; border-collapse: collapse; color: {theme['plotly_layout']['font_color']}; }} .styled-table th, .styled-table td {{ padding: 8px 4px; text-align: left; border-bottom: 1px solid {theme['table_border']}; }} .styled-table th {{ font-weight: bold; background-color: {theme['table_header_bg']}; }}</style><table class='styled-table'><thead><tr>{header}</tr></thead><tbody>{rows_html}</tbody></table>"""
    st.markdown(table_html, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DE TEMA E ESTILOS ---
THEMES = {
    "dark": {"plotly_layout": {"plot_bgcolor":'rgba(0,0,0,0)', "paper_bgcolor":'rgba(0,0,0,0)', "font_color":'white'}, "calendar_neutral": "rgba(44, 44, 44, 0.8)", "table_header_bg": "rgba(44, 44, 44, 0.8)", "table_border": "#3c3c3c", "win_color": "rgba(102, 187, 106, 0.8)", "loss_color": "rgba(239, 83, 80, 0.8)", "win_font": "#66BB6A", "loss_font": "#EF5350"},
    "light": {"plotly_layout": {"plot_bgcolor":'rgba(255,255,255,0)', "paper_bgcolor":'rgba(255,255,255,0)', "font_color":'#1E1E1E'}, "calendar_neutral": "#E8E8E8", "table_header_bg": "#F0F2F6", "table_border": "#dddddd", "win_color": "rgba(102, 187, 106, 0.8)", "loss_color": "rgba(239, 83, 80, 0.8)", "win_font": "#1a936f", "loss_font": "#c94c4c"}
}
if 'theme' not in st.session_state: st.session_state.theme = "dark"
active_theme = THEMES[st.session_state.theme]

light_theme_css = """<style>body { background-color: #FFFFFF; } .main { background-color: #FFFFFF; } [data-testid="stSidebar"] { background-color: #F0F8FF; } [data-testid="stSidebar"] * { color: #1E1E1E !important; } h1, h2, h3, h4, h5, h6, p, label, .st-emotion-cache-1c7y2kd { color: #1E1E1E !important; } [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #1E1E1E !important; } .stSelectbox div[data-baseweb="select"] > div { color: #1E1E1E !important; }</style>"""
if st.session_state.theme == "light": st.markdown(light_theme_css, unsafe_allow_html=True)

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(page_title="MarketLens | Dashboard", page_icon="🏠", layout="wide")
setup_sidebar()

with st.sidebar:
    st.markdown("---")
    button_text = "Mudar para Tema Claro ☀️" if st.session_state.theme == "dark" else "Mudar para Tema Escuro 🌙"
    if st.button(button_text, use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"; st.rerun()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None: st.switch_page("pages/0_👤_Login.py")
user_id = st.session_state['user_info'].get('localId'); user_email = st.session_state['user_info'].get('email')
accounts = get_trading_accounts(user_id)
account_options = {"Geral (Todas as Contas)": "all", **{acc['account_name']: acc['doc_id'] for acc in accounts}}

# --- FILTROS DO DASHBOARD ---
st.title("🏠 Dashboard Analítico")
selected_account_name = st.selectbox("Selecione a Conta para Análise:", options=list(account_options.keys()))
st.markdown("---")

# --- LÓGICA DE FILTRAGEM E CÁLCULO ---
with st.spinner("A analisar o seu histórico de operações..."):
    df_journal_all = get_journal_entries(user_id)
    if df_journal_all.empty: st.info("Bem-vindo! Registe a sua primeira operação no Diário para começar."); st.stop()

    if (selected_account_id := account_options[selected_account_name]) != "all":
        df_journal_all = df_journal_all.explode('accounts')
        df_filtered = df_journal_all[df_journal_all['accounts'] == selected_account_id].copy()
    else: df_filtered = df_journal_all.copy()

    setups = get_playbook_setups(user_id)
    dashboard_data = calculate_dashboard_metrics(df_filtered, setups)
    kpis = dashboard_data["kpis"]

    if kpis["total_trades"] == 0: st.warning(f"Ainda não há operações finalizadas para a conta '{selected_account_name}'."); st.stop()

# --- RENDERIZAÇÃO DO DASHBOARD ---
st.subheader("Performance Geral")
kpi_cols = st.columns(5)
kpi_cols[0].metric("Resultado Líquido (USD)", f"${kpis['total_pnl']:,.2f}")
kpi_cols[1].metric("Taxa de Acerto", f"{kpis['win_rate']:.2f}%")
kpi_cols[2].metric("R/R Médio", f"1 : {kpis['avg_rr_ratio']:.2f}")
kpi_cols[3].metric("Expectativa", f"${kpis['expectancy']:,.2f}")
kpi_cols[4].metric("Total de Operações", f"{kpis['total_trades']}")
st.markdown("---")

st.subheader("Curva de Capital")
fig_equity = go.Figure(go.Scatter(x=list(range(1, len(dashboard_data["equity_curve"]) + 1)), y=dashboard_data["equity_curve"].values, mode='lines', fill='tozeroy', name='Capital', line=dict(color='cyan', width=2), fillcolor='rgba(0, 255, 255, 0.2)'))
fig_equity.update_layout(xaxis_title='Número da Operação', yaxis_title='Resultado Acumulado (USD)', height=400, margin=dict(t=30, b=30, l=20, r=20), **active_theme['plotly_layout'])
st.plotly_chart(fig_equity, use_container_width=True)
st.markdown("---")

col1, col2, col3 = st.columns([4, 3, 3])
with col1:
    st.subheader("Análise Temporal")
    fig_calendar = create_calendar_plot(dashboard_data["calendar_data"], active_theme)
    st.plotly_chart(fig_calendar, use_container_width=True)
    st.markdown("##### Trades Recentes")
    render_styled_trades_table(dashboard_data["recent_trades"], active_theme)

with col2:
    st.subheader("Synapse Score")
    score_data = dashboard_data["synapse_score_data"]
    st.metric("Pontuação de Performance", f"{score_data['score']:.1f} / 100")
    fig_score = create_synapse_score_chart(score_data, active_theme)
    st.plotly_chart(fig_score, use_container_width=True)
    st.markdown("---")
    st.subheader("Sumário Diário")
    daily_summary = dashboard_data["daily_summary"]
    st.metric("Média Dia Vencedor", f"${daily_summary['avg_win_day']:,.2f}")
    st.metric("Pior Dia", f"${daily_summary['worst_day_pnl']:,.2f}", delta=daily_summary['worst_day_date'])

with col3:
    st.subheader("Ativos Negociados")
    fig_pie = create_asset_pie_chart(dashboard_data["asset_distribution"], active_theme)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("---")
    st.subheader("Sumário Semanal")
    weekday_summary = dashboard_data["weekday_summary"]
    st.metric("Melhor Dia da Semana", weekday_summary['best_day'], delta=f"${weekday_summary['best_day_pnl']:,.2f}")
    st.metric("Pior Dia da Semana", weekday_summary['worst_day'], delta=f"${weekday_summary['worst_day_pnl']:,.2f}")


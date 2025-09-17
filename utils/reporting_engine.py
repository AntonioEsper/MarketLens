# marketlens/utils/reporting_engine.py

import pandas as pd
import numpy as np
from datetime import datetime

def calculate_dashboard_metrics(df_journal, setups_data):
    """
    Calcula um conjunto abrangente de métricas para o Dashboard Analítico 4.0.
    """
    # --- Passo 1: Filtrar operações finalizadas e preparar dados ---
    df = df_journal[
        (df_journal['status'] == 'Finalizado') &
        (df_journal['exit_price'].notna()) &
        (df_journal['exit_price'] > 0)
    ].copy()

    if df.empty:
        # Retorna uma estrutura vazia e completa para evitar erros na UI
        return {
            "kpis": {"total_pnl": 0, "win_rate": 0, "avg_rr_ratio": 0, "expectancy": 0, "total_trades": 0},
            "equity_curve": pd.Series(dtype=float),
            "calendar_data": pd.Series(dtype=float), "time_summary": {"pnl_week": 0, "pnl_month": 0, "pnl_year": 0},
            "daily_summary": {"avg_win_day": 0, "avg_loss_day": 0, "best_day_pnl": 0, "best_day_date": "N/A", "worst_day_pnl": 0, "worst_day_date": "N/A"},
            "synapse_score_data": {"win_rate": 0, "avg_win_loss_ratio": 0, "profit_factor": 0, "score": 0},
            "recent_trades": pd.DataFrame(),
            "asset_distribution": pd.Series(dtype=float),
            "weekday_summary": {"best_day": "N/A", "best_day_pnl": 0, "worst_day": "N/A", "worst_day_pnl": 0}
        }

    numeric_cols = ['entry_price', 'exit_price', 'stop_loss', 'risk_usd']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['risk_usd'] = df['risk_usd'].fillna(0)
    df['trade_date'] = pd.to_datetime(df['trade_date'])

    # --- Passo 2: Recalcular P&L e R-Múltiplo ---
    stop_distance_points = abs(df['entry_price'] - df['stop_loss'])
    pnl_points = np.where(df['direction'] == 'Compra', df['exit_price'] - df['entry_price'], df['entry_price'] - df['exit_price'])
    df['r_multiple'] = np.divide(pnl_points, stop_distance_points, out=np.zeros_like(pnl_points, dtype=float), where=stop_distance_points != 0)
    df['pnl_usd'] = df['r_multiple'] * df['risk_usd']

    # --- Passo 3: Cálculos de Agrupamento ---
    df['trade_day'] = df['trade_date'].dt.date
    daily_pnl = df.groupby('trade_day')['pnl_usd'].sum()
    df['day_of_week_name'] = df['trade_date'].dt.day_name()
    weekday_pnl = df.groupby('day_of_week_name')['pnl_usd'].sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']).fillna(0)
    weekday_pnl.index = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

    # --- Passo 4: Cálculo dos KPIs ---
    total_pnl = df['pnl_usd'].sum()
    total_trades = len(df)
    wins = df[df['pnl_usd'] > 0]
    losses = df[df['pnl_usd'] < 0]
    num_wins = len(wins)
    win_rate = (num_wins / total_trades) * 100 if total_trades > 0 else 0
    avg_win_usd = wins['pnl_usd'].mean() if num_wins > 0 else 0
    avg_loss_usd = abs(losses['pnl_usd'].mean()) if not losses.empty else 0
    risked_trades = df[df['risk_usd'] > 0]
    avg_risk_per_trade = risked_trades['risk_usd'].mean() if not risked_trades.empty else 0
    avg_rr_ratio = avg_win_usd / avg_risk_per_trade if avg_risk_per_trade > 0 else 0
    win_rate_dec = win_rate / 100
    loss_rate_dec = 1 - win_rate_dec
    expectancy = (win_rate_dec * avg_win_usd) - (loss_rate_dec * avg_loss_usd)
    kpis = {"total_pnl": total_pnl, "win_rate": win_rate, "avg_rr_ratio": avg_rr_ratio, "expectancy": expectancy, "total_trades": total_trades}

    # --- Passo 5: Cálculos de Sumário ---
    today = datetime.now().date()
    current_week_start = today - pd.to_timedelta(today.weekday(), unit='d')
    daily_pnl.index = pd.to_datetime(daily_pnl.index)
    pnl_this_week = daily_pnl[daily_pnl.index.date >= current_week_start].sum()
    pnl_this_month = daily_pnl[(daily_pnl.index.month == today.month) & (daily_pnl.index.year == today.year)].sum()
    pnl_this_year = daily_pnl[daily_pnl.index.year == today.year].sum()
    time_summary = {"pnl_week": pnl_this_week, "pnl_month": pnl_this_month, "pnl_year": pnl_this_year}
    
    winning_days = daily_pnl[daily_pnl > 0]
    losing_days = daily_pnl[daily_pnl < 0]
    avg_win_day = winning_days.mean() if not winning_days.empty else 0
    avg_loss_day = losing_days.mean() if not losing_days.empty else 0
    best_day_pnl = daily_pnl.max() if not daily_pnl.empty else 0
    worst_day_pnl = daily_pnl.min() if not daily_pnl.empty else 0
    best_day_date = daily_pnl.idxmax().strftime('%d/%m/%Y') if best_day_pnl > 0 else "N/A"
    worst_day_date = daily_pnl.idxmin().strftime('%d/%m/%Y') if worst_day_pnl < 0 else "N/A"
    daily_summary = {"avg_win_day": avg_win_day, "avg_loss_day": avg_loss_day, "best_day_pnl": best_day_pnl, "best_day_date": best_day_date, "worst_day_pnl": worst_day_pnl, "worst_day_date": worst_day_date}

    # Melhor e pior dia da semana
    best_weekday = weekday_pnl.idxmax() if not weekday_pnl.empty else "N/A"
    worst_weekday = weekday_pnl.idxmin() if not weekday_pnl.empty else "N/A"
    weekday_summary = {"best_day": best_weekday, "best_day_pnl": weekday_pnl.max(), "worst_day": worst_weekday, "worst_day_pnl": weekday_pnl.min()}

    # --- Passo 6: Dados para o Synapse Score ---
    total_gross_profit = wins['pnl_usd'].sum()
    total_gross_loss = abs(losses['pnl_usd'].sum())
    profit_factor = total_gross_profit / total_gross_loss if total_gross_loss > 0 else total_gross_profit
    avg_win_loss_ratio = avg_win_usd / avg_loss_usd if avg_loss_usd > 0 else avg_win_usd
    
    # Normalização dos fatores para o Score
    win_rate_score = win_rate
    awl_score = min(avg_win_loss_ratio, 3) / 3 * 100
    pf_score = min(profit_factor, 3) / 3 * 100
    synapse_score = (win_rate_score + awl_score + pf_score) / 3

    synapse_score_data = {"win_rate": win_rate, "avg_win_loss_ratio": avg_win_loss_ratio, "profit_factor": profit_factor, "score": synapse_score}

    # --- Passo 7: Preparar Dados para Gráficos e Tabelas ---
    df_sorted = df.sort_values(by='trade_date', ascending=False)
    equity_curve = df_sorted.sort_values(by='trade_date')['pnl_usd'].cumsum()
    
    recent_trades = df_sorted.head(5).copy()
    recent_trades['Resultado'] = np.where(recent_trades['pnl_usd'] > 0, 'Ganho', 'Perda')
    recent_trades['Data'] = recent_trades['trade_date'].dt.strftime('%d/%m/%Y')
    recent_trades.rename(columns={'asset': 'Ativo', 'direction': 'Direção', 'pnl_usd': 'PnL (USD)', 'r_multiple': 'RR'}, inplace=True)
    recent_trades = recent_trades[['Data', 'Ativo', 'Direção', 'Resultado', 'PnL (USD)', 'RR']]

    asset_distribution = df['asset'].value_counts()
    
    # --- Passo 8: Montar Dicionário de Retorno ---
    return {
        "kpis": kpis, "equity_curve": equity_curve, "calendar_data": daily_pnl,
        "time_summary": time_summary, "daily_summary": daily_summary,
        "synapse_score_data": synapse_score_data, "recent_trades": recent_trades,
        "asset_distribution": asset_distribution, "weekday_summary": weekday_summary
    }


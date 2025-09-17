# synapse_desk/utils/reporting_engine.py

import pandas as pd
import numpy as np

def calculate_performance_metrics(df_journal):
    """
    Calcula um conjunto de métricas de performance a partir de um DataFrame de trades.
    Esta versão é mais robusta, filtrando apenas trades finalizados e recalculando o PnL.
    """
    # --- Passo 1: Filtrar apenas operações finalizadas ---
    df_finalized = df_journal[
        (df_journal['status'] == 'Finalizado') &
        (df_journal['exit_price'].notna()) &
        (df_journal['exit_price'] > 0)
    ].copy()

    if df_finalized.empty:
        default_metrics = {"total_pnl": 0, "total_trades": 0, "win_rate": 0, "avg_win": 0, "avg_loss": 0, "profit_factor": 0}
        return default_metrics, pd.Series(dtype=float)

    # --- Passo 2: Preparar os dados ---
    for col in ['entry_price', 'exit_price', 'stop_loss', 'risk_usd']:
        if col in df_finalized.columns:
            df_finalized[col] = pd.to_numeric(df_finalized[col], errors='coerce')
        else:
            df_finalized[col] = np.nan
    df_finalized['risk_usd'].fillna(0, inplace=True)
    df_finalized.dropna(subset=['entry_price', 'exit_price', 'stop_loss'], inplace=True)

    if df_finalized.empty:
        default_metrics = {"total_pnl": 0, "total_trades": 0, "win_rate": 0, "avg_win": 0, "avg_loss": 0, "profit_factor": 0}
        return default_metrics, pd.Series(dtype=float)

    # --- Passo 3: Recalcular o PnL em USD ---
    stop_distance_points = abs(df_finalized['entry_price'] - df_finalized['stop_loss'])
    pnl_points = np.where(
        df_finalized['direction'] == 'Compra',
        df_finalized['exit_price'] - df_finalized['entry_price'],
        df_finalized['entry_price'] - df_finalized['exit_price']
    )
    r_multiple = np.divide(pnl_points, stop_distance_points, out=np.zeros_like(pnl_points, dtype=float), where=stop_distance_points!=0)
    df_finalized['pnl_usd'] = r_multiple * df_finalized['risk_usd']

    # --- Passo 4: Cálculos das Métricas ---
    total_pnl = df_finalized['pnl_usd'].sum()
    total_trades = len(df_finalized)
    wins = df_finalized[df_finalized['pnl_usd'] > 0]
    num_wins = len(wins)
    win_rate = (num_wins / total_trades) * 100 if total_trades > 0 else 0
    avg_win = wins['pnl_usd'].mean() if num_wins > 0 else 0
    avg_loss = df_finalized[df_finalized['pnl_usd'] < 0]['pnl_usd'].mean() if not df_finalized[df_finalized['pnl_usd'] < 0].empty else 0

    # CORREÇÃO: Lógica para calcular o Rácio Retorno/Risco Médio
    # 1. Calcula o risco médio apenas das operações onde o risco foi definido (>0)
    risked_trades = df_finalized[df_finalized['risk_usd'] > 0]
    avg_risk_per_trade = risked_trades['risk_usd'].mean() if not risked_trades.empty else 0

    # 2. Calcula o rácio do lucro médio pelo risco médio
    if avg_risk_per_trade > 0 and avg_win > 0:
        avg_rr_ratio = avg_win / avg_risk_per_trade
    else:
        avg_rr_ratio = 0

    metrics = {
        "total_pnl": total_pnl, "total_trades": total_trades, "win_rate": win_rate,
        "avg_win": avg_win, "avg_loss": avg_loss, 
        "profit_factor": avg_rr_ratio  # Substitui o cálculo antigo pelo novo
    }

    # --- Passo 5: Cálculo da Curva de Capital ---
    df_finalized.sort_values(by='trade_date', inplace=True)
    equity_curve = df_finalized['pnl_usd'].cumsum()

    return metrics, equity_curve


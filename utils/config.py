# marketlens/utils/config.py

# --- ESTRUTURA DE CATEGORIAS DE ATIVOS ---
ASSET_CATEGORIES = {
    "--- Forex Majors ---": [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD"
    ],
    "--- Forex Crosses ---": [
        "EUR/JPY", "GBP/JPY", "EUR/GBP", "AUD/JPY", "NZD/JPY", "CAD/JPY"
    ],
    "--- Commodities ---": [
        "Ouro", "Prata", "Petróleo WTI"
    ],
    "--- Índices Globais ---": [
        "US500", "US100", "US30", "DAX", "FTSE 100", "Nikkei 225"
    ],
    "--- US Stocks (MAG7) ---": [
        "Apple", "Microsoft", "Google", "Amazon", "NVIDIA", "Meta", "Tesla"
    ]
}

# --- MAPEAMENTO ATUALIZADO PARA O YAHOO FINANCE ---
yahoo_finance_map = {
    # Forex Majors
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "USD/CHF": "CHF=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "NZD/USD": "NZDUSD=X",
    # Forex Crosses
    "EUR/JPY": "EURJPY=X", "GBP/JPY": "GBPJPY=X", "EUR/GBP": "EURGBP=X",
    "AUD/JPY": "AUDJPY=X", "NZD/JPY": "NZDJPY=X", "CAD/JPY": "CADJPY=X",
    # Commodities
    "Ouro": "GC=F", "Prata": "SI=F", "Petróleo WTI": "CL=F",
    # Índices Globais
    "US500": "^GSPC", "US100": "^IXIC", "US30": "^DJI", "DAX": "^GDAXI",
    "FTSE 100": "^FTSE", "Nikkei 225": "^N225",
    # US Stocks (MAG7)
    "Apple": "AAPL", "Microsoft": "MSFT", "Google": "GOOGL", "Amazon": "AMZN",
    "NVIDIA": "NVDA", "Meta": "META", "Tesla": "TSLA"
}

# --- MAPEAMENTO ATUALIZADO PARA O COT (CFTC) ---
cot_market_map = {
    # Forex
    "EUR/USD": "099741", "GBP/USD": "096742", "USD/JPY": "097741",
    "USD/CHF": "092741", "AUD/USD": "232741", "USD/CAD": "090741",
    "NZD/USD": "112741", "JPY": "097741", "CHF": "092741",
    "AUD": "232741", "CAD": "090741", "NZD": "112741", "EUR": "099741",
    "GBP": "096742",
    # Commodities
    "Ouro": "088691", "Prata": "084691", "Petróleo WTI": "067651",
    # Índices
    "US500": "13874P", "US100": "20974P", "US30": "124601",
    # Indicadores
    "DXY": "098662"
}

# --- MAPEAMENTO PARA SÉRIES DE DADOS ECONÓMICOS DO FRED (CORRIGIDO) ---
FRED_SERIES_MAP = {
    # --- Estados Unidos (USD) ---
    "US GDP Growth Rate QoQ": {"id": "A191RP1Q027SBEA", "currency": "USD", "impact_on_currency": "positive"},
    # CORREÇÃO: ID alterado para a série de inflação YoY mais comum e direta.
    "US Inflation Rate YoY": {"id": "CPALTT01USM659N", "currency": "USD", "impact_on_currency": "positive"},
    "US Interest Rate": {"id": "FEDFUNDS", "currency": "USD", "impact_on_currency": "positive"},
    "US Unemployment Rate": {"id": "UNRATE", "currency": "USD", "impact_on_currency": "negative"},
    "US Non-Farm Payrolls": {"id": "PAYEMS", "currency": "USD", "impact_on_currency": "positive"},
    "US Retail Sales MoM": {"id": "MRTSSM44X72USS", "currency": "USD", "impact_on_currency": "positive"},
    # CORREÇÃO: ID alterado para o código oficial do ISM Manufacturing PMI.
    "US Manufacturing PMI": {"id": "NAPM", "currency": "USD", "impact_on_currency": "positive"},
    # CORREÇÃO: ID alterado para o código oficial do ISM Services PMI.
    "US Services PMI": {"id": "NMFBAI", "currency": "USD", "impact_on_currency": "positive"},
    
    # --- Zona Euro (EUR) ---
    "Eurozone GDP Growth Rate QoQ": {"id": "CLVMNACSCAB1GQEA19", "currency": "EUR", "impact_on_currency": "positive"},
    # CORREÇÃO: ID alterado para a série de inflação HICP YoY mais comum.
    "Eurozone Inflation Rate YoY": {"id": "CPHPTT01EZM659N", "currency": "EUR", "impact_on_currency": "positive"},
    # CORREÇÃO: ID alterado para a taxa de depósito do BCE, um indicador chave.
    "Eurozone Interest Rate": {"id": "ECBDFR", "currency": "EUR", "impact_on_currency": "positive"},
    "Eurozone Unemployment Rate": {"id": "LRUNTTTTEZM156S", "currency": "EUR", "impact_on_currency": "negative"},

    # --- Japão (JPY) ---
    "Japan Inflation Rate YoY": {"id": "JPNCPIALLMINMEI", "currency": "JPY", "impact_on_currency": "positive"},
    "Japan Unemployment Rate": {"id": "LRUNTTTTJPM156S", "currency": "JPY", "impact_on_currency": "negative"},
    
    # --- Reino Unido (GBP) ---
    "UK Inflation Rate YoY": {"id": "GBRCPIALLMINMEI", "currency": "GBP", "impact_on_currency": "positive"},
    "UK Unemployment Rate": {"id": "LMUNRRTTGBM156S", "currency": "GBP", "impact_on_currency": "negative"},
}


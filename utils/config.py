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
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "USD/CHF": "CHF=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "NZD/USD": "NZDUSD=X",
    "EUR/JPY": "EURJPY=X", "GBP/JPY": "GBPJPY=X", "EUR/GBP": "EURGBP=X",
    "AUD/JPY": "AUDJPY=X", "NZD/JPY": "NZDJPY=X", "CAD/JPY": "CADJPY=X",
    "Ouro": "GC=F", "Prata": "SI=F", "Petróleo WTI": "CL=F",
    "US500": "^GSPC", "US100": "^IXIC", "US30": "^DJI", "DAX": "^GDAXI",
    "FTSE 100": "^FTSE", "Nikkei 225": "^N225",
    "Apple": "AAPL", "Microsoft": "MSFT", "Google": "GOOGL", "Amazon": "AMZN",
    "NVIDIA": "NVDA", "Meta": "META", "Tesla": "TSLA"
}

# --- MAPEAMENTO ATUALIZADO PARA O COT (CFTC) ---
cot_market_map = {
    "EUR/USD": "099741", "GBP/USD": "096742", "USD/JPY": "097741",
    "USD/CHF": "092741", "AUD/USD": "232741", "USD/CAD": "090741",
    "NZD/USD": "112741", "JPY": "097741", "CHF": "092741",
    "AUD": "232741", "CAD": "090741", "NZD": "112741", "EUR": "099741",
    "GBP": "096742", "Ouro": "088691", "Prata": "084691", "Petróleo WTI": "067651",
    "US500": "13874P", "US100": "20974P", "US30": "124601", "DXY": "098662"
}

# --- MAPEAMENTO PARA SÉRIES DE DADOS ECONÓMICOS DO FRED (EXPANDIDO FINAL) ---
FRED_SERIES_MAP = {
    # --- Crescimento ---
    "US GDP Growth Rate QoQ":  {"id": "A191RP1Q027SBEA", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "positive"},
    
    # --- Inflação ---
    "US Inflation Rate YoY (CPI)": {"id": "CPALTT01USM659N", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    "US Producer Price Index YoY (PPI)": {"id": "PPIACO", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    "US Core PCE YoY": {"id": "PCEPILFE", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    
    # --- Política Monetária ---
    "US Interest Rate (Fed Funds)": {"id": "FEDFUNDS", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    
    # --- Mercado de Trabalho ---
    "US Non-Farm Payrolls": {"id": "PAYEMS", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "positive"},
    "US Unemployment Rate": {"id": "UNRATE", "currency": "USD", "impact_on_currency": "negative", "impact_on_stocks": "negative"},
    "US JOLTS Job Openings": {"id": "JTSJOL", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "positive"},
    "US Wage Growth YoY": {"id": "CES0500000003", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    "US Initial Jobless Claims": {"id": "ICSA", "currency": "USD", "impact_on_currency": "negative", "impact_on_stocks": "negative"},
    
    # --- Consumo ---
    "US Retail Sales MoM": {"id": "MRTSSM44X72USS", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "positive"},
    
    # --- Atividade Empresarial ---
    "US Manufacturing PMI (ISM)": {"id": "NAPM", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "positive"},
    "US Services PMI (ISM)": {"id": "NMFBAI", "currency": "USD", "impact_on_currency": "positive", "impact_on_stocks": "positive"},

    # --- Outras Economias (para análise de Forex) ---
    "Eurozone GDP Growth Rate QoQ": {"id": "CLVMNACSCAB1GQEA19", "currency": "EUR", "impact_on_currency": "positive", "impact_on_stocks": "positive"},
    "Eurozone Inflation Rate YoY": {"id": "CPHPTT01EZM659N", "currency": "EUR", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    "Eurozone Interest Rate": {"id": "ECBDFR", "currency": "EUR", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    "Eurozone Unemployment Rate": {"id": "LRUNTTTTEZM156S", "currency": "EUR", "impact_on_currency": "negative", "impact_on_stocks": "negative"},
    "Japan Inflation Rate YoY": {"id": "JPNCPIALLMINMEI", "currency": "JPY", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    "Japan Unemployment Rate": {"id": "LRUNTTTTJPM156S", "currency": "JPY", "impact_on_currency": "negative", "impact_on_stocks": "negative"},
    "UK Inflation Rate YoY": {"id": "GBRCPIALLMINMEI", "currency": "GBP", "impact_on_currency": "positive", "impact_on_stocks": "negative"},
    "UK Unemployment Rate": {"id": "LMUNRRTTGBM156S", "currency": "GBP", "impact_on_currency": "negative", "impact_on_stocks": "negative"},
}


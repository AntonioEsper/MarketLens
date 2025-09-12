# marketlens/utils/config.py

# --- ESTRUTURA DE CATEGORIAS DE ATIVOS ---
# Esta estrutura é a base para o menu lateral e para o nosso novo scanner.
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
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"
    ]
}

# --- MAPEAMENTO PARA O YAHOO FINANCE ---
# Contém todos os tickers necessários para a API yfinance.
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
    "AAPL": "AAPL", "MSFT": "MSFT", "GOOGL": "GOOGL", "AMZN": "AMZN",
    "NVDA": "NVDA", "META": "META", "TSLA": "TSLA",
    # Indicadores Chave (não estão no menu, mas usados internamente)
    "DXY": "DX-Y.NYB", "VIX": "^VIX", "US10Y": "^TNX"
}

# --- MAPEAMENTO PARA O COT (CFTC) ---
# Contém os códigos de contrato para a API da CFTC.
cot_market_map = {
    # Forex
    "EUR/USD": "099741", "GBP/USD": "096742", "USD/JPY": "097741",
    "USD/CHF": "092741", "AUD/USD": "232741", "USD/CAD": "090741",
    "NZD/USD": "112741",
    # Commodities
    "Ouro": "088691", "Prata": "084691", "Petróleo WTI": "067651",
    # Índices
    "US500": "13874P", "US100": "20974P", "US30": "124601",
    # Indicadores
    "DXY": "098662", "US10Y": "043602"
}

# --- MAPEAMENTO PARA SÉRIES DE DADOS ECONÓMICOS DO FRED ---
# Mapeia um nome amigável para a série de ID do FRED e a moeda que impacta.
FRED_SERIES_MAP = {
    "US Inflation (CPI)": {"id": "CPIAUCSL", "currency": "USD"},
    "US Unemployment Rate": {"id": "UNRATE", "currency": "USD"},
    "US Non-Farm Payrolls": {"id": "PAYEMS", "currency": "USD"},
    "US Retail Sales": {"id": "RSXFS", "currency": "USD"},
    "US Interest Rate": {"id": "FEDFUNDS", "currency": "USD"},
    "Eurozone Inflation (HICP)": {"id": "CP00_EU_HICP_MANR", "currency": "EUR"},
    "Eurozone GDP Growth": {"id": "CLVMNACSCAB1GQEA19", "currency": "EUR"},
    "Eurozone Unemployment Rate": {"id": "LRUNTTTTEZM156S", "currency": "EUR"},
    "Japan Inflation (CPI)": {"id": "JPNCPIALLMINMEI", "currency": "JPY"}
}


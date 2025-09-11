# Módulo de Configuração do MarketLens
# Contém dicionários e listas de configuração global.

# --- NOVA ESTRUTURA DE CATEGORIAS DE ATIVOS ---
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
    "NVIDIA": "NVDA", "Meta": "META", "Tesla": "TSLA",
    # Indicadores Chave (não aparecerão no menu, mas são usados internamente)
    "DXY": "DX-Y.NYB", "VIX": "^VIX", "US10Y": "^TNX"
}

# --- MAPEAMENTO ATUALIZADO PARA O COT (CFTC) ---
cot_market_map = {
    # Mapeamentos existentes e novos
    "EUR/USD": "099741", "GBP/USD": "096742", "USD/JPY": "097741",
    "USD/CHF": "092741", "AUD/USD": "232741", "USD/CAD": "090741",
    "NZD/USD": "112741", "Ouro": "088691", "Prata": "084691",
    "Petróleo WTI": "067651", "US500": "13874P", "US100": "20974P",
    "DXY": "098662", "US10Y": "043602"
    # Nota: Nem todos os novos ativos (ex: Ações) têm um relatório COT.
    # O dashboard irá lidar com isso de forma inteligente.
}


# Mapeamento de nomes de ativos para o formato do widget do TradingView (sem alterações)
tradingview_map = {
    "EUR/USD": "FX:EURUSD", "GBP/USD": "FX:GBPUSD", "USD/JPY": "FX:USDJPY",
    "US500": "SP:SPX", "US100": "NASDAQ:NDX", "US30": "DJ:DJI",
    "Ouro": "COMEX:GC1!", "Petróleo WTI": "NYMEX:CL1!",
    "BTC/USD": "COINBASE:BTCUSD", "ETH/USD": "COINBASE:ETHUSD",
    "DXY": "TVC:DXY", "VIX": "TVC:VIX"
}


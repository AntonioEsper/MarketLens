# Módulo de Configuração do MarketLens
# Contém dicionários e listas de configuração global.

# Mapeamento de nomes de ativos para tickers do Yahoo Finance (sem alterações)
yahoo_finance_map = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "USD/CHF": "CHF=X", 
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "NZD/USD": "NZDUSD=X", "EUR/JPY": "EURJPY=X", 
    "AUD/JPY": "AUDJPY=X", "EUR/GBP": "EURGBP=X", "GBP/JPY": "GBPJPY=X", "CHF/JPY": "CHFJPY=X",
    "US500": "^GSPC", "US100": "^IXIC", "US30": "^DJI", "DAX": "^GDAXI", "HK50": "^HSI",
    "Ouro": "GC=F", "Prata": "SI=F", "Petróleo WTI": "CL=F", "DXY": "DX-Y.NYB", "VIX": "^VIX",
    "BTC/USD": "BTC-USD", "ETH/USD": "ETH-USD"
}

# Mapeamento de nomes de ativos para os CÓDIGOS de contrato da API da CFTC
# FASE 1 DA RECONSTRUÇÃO: Esta é a nossa nova "Fonte da Verdade", baseada na sua pesquisa.
cot_market_map = {
    "EUR/USD": "099741",
    "GBP/USD": "096742",
    "USD/JPY": "097741",
    "USD/CHF": "092741",
    "AUD/USD": "232741",
    "USD/CAD": "090741",
    "NZD/USD": "112741",
    "Ouro": "088691",
    "Prata": "084691",
    "Petróleo WTI": "067651",
    "US500": "13874P",
    "US100": "20974P",
    "DXY": "098662",
    "US10Y": "043602"
}

# Mapeamento de nomes de ativos para o formato do widget do TradingView (sem alterações)
tradingview_map = {
    "EUR/USD": "FX:EURUSD", "GBP/USD": "FX:GBPUSD", "USD/JPY": "FX:USDJPY",
    "US500": "SP:SPX", "US100": "NASDAQ:NDX", "US30": "DJ:DJI",
    "Ouro": "COMEX:GC1!", "Petróleo WTI": "NYMEX:CL1!",
    "BTC/USD": "COINBASE:BTCUSD", "ETH/USD": "COINBASE:ETHUSD",
    "DXY": "TVC:DXY", "VIX": "TVC:VIX"
}


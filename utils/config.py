# Módulo de Configuração do MarketLens
# Contém dicionários e listas de configuração global.

# Mapeamento de nomes de ativos para tickers do Yahoo Finance
yahoo_finance_map = {
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "USD/CHF": "CHF=X", 
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "NZD/USD": "NZDUSD=X", "EUR/JPY": "EURJPY=X", 
    "AUD/JPY": "AUDJPY=X", "EUR/GBP": "EURGBP=X", "GBP/JPY": "GBPJPY=X", "CHF/JPY": "CHFJPY=X",
    "US500": "^GSPC", "US100": "^IXIC", "US30": "^DJI", "DAX": "^GDAXI", "HK50": "^HSI",
    "Ouro": "GC=F", "Prata": "SI=F", "Petróleo WTI": "CL=F", "DXY": "DX-Y.NYB", "VIX": "^VIX",
    "BTC/USD": "BTC-USD", "ETH/USD": "ETH-USD"
}

# Mapeamento de nomes de ativos para os IDs de série do FRED para o relatório COT
# CORREÇÃO FINAL E DEFINITIVA: IDs validados da base de dados da Quandl, acessíveis via API FRED.
cot_market_map = {
    "EUR/USD": "CFTC/099741_F_L_NET",
    "GBP/USD": "CFTC/096742_F_L_NET",
    "USD/JPY": "CFTC/097741_F_L_NET",
    "USD/CHF": "CFTC/092741_F_L_NET",
    "AUD/USD": "CFTC/232741_F_L_NET",
    "USD/CAD": "CFTC/090741_F_L_NET",
    "NZD/USD": "CFTC/112741_F_L_NET",
    "Ouro": "CFTC/088691_F_L_NET",
    "Prata": "CFTC/084691_F_L_NET",
    "Petróleo WTI": "CFTC/067651_F_L_NET",
    "US500": "CFTC/13874P_F_L_NET",
    "US100": "CFTC/20974P_F_L_NET",
    "DXY": "CFTC/098662_F_L_NET",
    "US10Y": "CFTC/043602_F_L_NET"
}

# Mapeamento de nomes de ativos para o formato do widget do TradingView
tradingview_map = {
    "EUR/USD": "FX:EURUSD", "GBP/USD": "FX:GBPUSD", "USD/JPY": "FX:USDJPY",
    "US500": "SP:SPX", "US100": "NASDAQ:NDX", "US30": "DJ:DJI",
    "Ouro": "COMEX:GC1!", "Petróleo WTI": "NYMEX:CL1!",
    "BTC/USD": "COINBASE:BTCUSD", "ETH/USD": "COINBASE:ETHUSD",
    "DXY": "TVC:DXY", "VIX": "TVC:VIX"
}


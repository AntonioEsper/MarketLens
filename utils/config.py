# synapse_desk/utils/config.py

# --- ESTRUTURA DE CATEGORIAS DE ATIVOS ---
ASSET_CATEGORIES = {
    "--- Forex Majors ---": [
        "EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD"
    ],
    "--- Forex Crosses ---": [
        "EUR/JPY", "GBP/JPY", "EUR/GBP", "AUD/JPY", "NZD/JPY", "CAD/JPY",
        # Adições
        "EUR/AUD", "EUR/CAD", "GBP/AUD", "GBP/CAD", "AUD/CAD", "AUD/NZD", "CHF/JPY"
    ],
    "--- Commodities ---": [
        "Ouro", "Prata", "Petróleo WTI",
        # Adições
        "Platina", "Cobre"
    ],
    "--- Índices Globais (Américas) ---": [
        "US500", "US100", "US30"
    ],
    # EXPANSÃO: Novas categorias para Índices Europeus e Asiáticos
    "--- Índices Globais (Europa) ---": [
        "DAX", "FTSE 100", "CAC 40", "Euro Stoxx 50"
    ],
    "--- Índices Globais (Ásia) ---": [
        "Nikkei 225", "Hang Seng", "Shanghai Comp."
    ],
    # EXPANSÃO: Nova categoria para Criptomoedas
    "--- Criptomoedas ---": [
        "Bitcoin", "Ethereum"
    ],
    "--- US Stocks (MAG7) ---": [
        "Apple", "Microsoft", "Google", "Amazon", "NVIDIA", "Meta", "Tesla"
    ],
}

# --- MAPEAMENTO PARA A API DO YAHOO FINANCE ---
# Este dicionário traduz o nome amigável do ativo para o ticker que o yfinance espera.
yahoo_finance_map = {
    # Forex Majors
    "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X", "USD/CHF": "CHF=X",
    "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X", "NZD/USD": "NZDUSD=X",
    # Forex Crosses
    "EUR/JPY": "EURJPY=X", "GBP/JPY": "GBPJPY=X", "EUR/GBP": "EURGBP=X",
    "AUD/JPY": "AUDJPY=X", "NZD/JPY": "NZDJPY=X", "CAD/JPY": "CADJPY=X",
    # Adições Crosses
    "EUR/AUD": "EURAUD=X", "EUR/CAD": "EURCAD=X", "GBP/AUD": "GBPAUD=X",
    "GBP/CAD": "GBPCAD=X", "AUD/CAD": "AUDCAD=X", "AUD/NZD": "AUDNZD=X", "CHF/JPY": "CHFJPY=X",
    # Commodities
    "Ouro": "GC=F", "Prata": "SI=F", "Petróleo WTI": "CL=F",
    # Adições Commodities
    "Platina": "PL=F", "Cobre": "HG=F",
    # Índices Américas
    "US500": "^GSPC", "US100": "^IXIC", "US30": "^DJI",
    # Índices Europa
    "DAX": "^GDAXI", "FTSE 100": "^FTSE", "CAC 40": "^FCHI", "Euro Stoxx 50": "^STOXX50E",
    # Índices Ásia
    "Nikkei 225": "^N225", "Hang Seng": "^HSI", "Shanghai Comp.": "000001.SS",
    # Criptomoedas
    "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD",
    # US Stocks
    "Apple": "AAPL", "Microsoft": "MSFT", "Google": "GOOGL", "Amazon": "AMZN",
    "NVIDIA": "NVDA", "Meta": "META", "Tesla": "TSLA"
}

# --- MAPEAMENTO ATUALIZADO PARA O RELATÓRIO COT (COMMITMENT OF TRADERS) ---
cot_market_map = {
    # Moedas
    "USD": "098662",
    "EUR": "099741",
    "JPY": "097741",
    "GBP": "096742",
    "AUD": "232741",
    "NZD": "112741",
    "CAD": "090741",
    "CHF": "092741",
    "MXN": "095741",
    # Commodities
    "Ouro": "088691",
    "Prata": "084691",
    "Petróleo WTI": "067651",
    "Platina": "076651", # Adicionado
    "Cobre": "085692",   # Adicionado
    # Índices
    "S&P 500": "138741",
    "Nasdaq 100": "209741",
    "Dow Jones": "124601",
    "Russell 2000": "239741",
    "VIX": "1170E1"
}
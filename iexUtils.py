import pandas as pd

EXCLUDE_SYMBOLS = ["ALZH", "CDAY", "DFBH", "ELOX", "LASR", "LTN^"]

def getAllSymbols():
    return pd.read_json("https://api.iextrading.com/1.0/ref-data/symbols")

def filterEnabledSymbols(symbols):
    return symbols[symbols.isEnabled == True]

def filterCommonStockSymbols(symbols):
    return symbols[symbols.type == "cs"]

def getHistoricalData(symbol, timeSpan):
    return pd.read_json("https://api.iextrading.com/1.0/stock/"+symbol+"/chart/"+timeSpan)

def getBatchHistoricalData(symbols, timeSpan):
    assert len(symbols) <= 100
    print("Getting batch hv")
    return pd.read_json("https://api.iextrading.com/1.0/stock/market/batch?symbols="+",".join(symbols)+"&types=chart&range="+timeSpan)
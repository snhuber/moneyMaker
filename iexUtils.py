import pandas as pd

def getAllSymbols():
    return pd.read_json("https://api.iextrading.com/1.0/ref-data/symbols")

def filterEnabledSymbols(symbols):
    return symbols[symbols.isEnabled == True]

def filterCommonStockSymbols(symbols):
    return symbols[symbols.type == "cs"]

def getHistoricalData(symbol, timeSpan):
    return pd.read_json("https://api.iextrading.com/1.0/stock/"+symbol+"/chart/"+timeSpan)
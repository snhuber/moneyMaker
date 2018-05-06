import pandas as pd
import datetime

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
    return pd.read_json("https://api.iextrading.com/1.0/stock/market/batch?symbols="+",".join(symbols)+"&types=chart&range="+timeSpan)

def getEarnings(symbol):
    return pd.read_json("https://api.iextrading.com/1.0/stock/"+symbol+"/earnings")

def getBatchEarnings(symbols):
    assert len(symbols) <= 100
    return pd.read_json("https://api.iextrading.com/1.0/stock/market/batch?symbols="+",".join(symbols)+"&types=earnings")

def getDaysData(symbol, date):
    return pd.read_json("https://api.iextrading.com/1.0/stock/"+symbol+"/chart/date/"+datetime.datetime.strftime(date, "%Y%m%d"))
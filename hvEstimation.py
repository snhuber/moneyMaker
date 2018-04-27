import pandas as pd
import iexUtils
import datetime
import numpy as np
from sklearn.externals import joblib

DAYS_FOR_2_YR = 504
DAYS_FOR_1_YR = 252

def filterStock(stock, columnsSelected):
    return stock[columnsSelected]

def addCGR(stock):
    price = np.array(stock.close)
    price_t1 = np.roll(price, 1)
    lnratio = price/price_t1
    cgr = np.log(lnratio)
    cgr[0] = None
    stock['cgr'] = cgr

def computeVol2Yr(stock):
    return np.std(stock.cgr[len(stock)-DAYS_FOR_2_YR:])

def historicalVolatilityOneStock(symbol):
    stock = iexUtils.getHistoricalData(symbol, "2y")
    stock = stock.reset_index()
    filterStock(stock, ['date', 'volume', 'close'])
    addCGR(stock)
    return computeVol2Yr(stock)

def main():
    symbolsData = iexUtils.getAllSymbols()
    symbolsData = iexUtils.filterEnabledSymbols(symbolsData)
    symbolsData = iexUtils.filterCommonStockSymbols(symbolsData)
    symbols = symbolsData.symbol.tolist()

    volatilities = joblib.load('historicalStockData.pkl')['volatilities']
    idx = 0
    for symbol in symbols:
        print(idx)
        if idx < 2900:
            idx += 1
            continue
        if symbol in iexUtils.EXCLUDE_SYMBOLS:
            continue
        print(symbol)
        vol2Yr = historicalVolatilityOneStock(symbol)
        volatilities.loc[idx] = [symbol, vol2Yr]
        idx += 1
        if idx % 100 == 0:
            joblib.dump({"lastUpdate": datetime.datetime.now(), "volatilities": volatilities}, 'historicalStockData.pkl')

    joblib.dump({"lastUpdate": datetime.datetime.now(), "volatilities": volatilities}, 'historicalStockData.pkl')

if __name__ == '__main__':
    main()
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
    return np.nanstd(stock.cgr)

def computeDrift2Yr(stock):
    return np.nanmean(stock.cgr)

def historicalVolatilityAndDriftOneStock(symbol):
    stock = iexUtils.getHistoricalData(symbol, "2y")
    stock = stock.reset_index()
    filterStock(stock, ['date', 'volume', 'close'])
    addCGR(stock)
    return computeVol2Yr(stock), computeDrift2Yr(stock)

def main():
    symbolsData = iexUtils.getAllSymbols()
    symbolsData = iexUtils.filterEnabledSymbols(symbolsData)
    symbolsData = iexUtils.filterCommonStockSymbols(symbolsData)
    symbols = symbolsData.symbol.tolist()

    stockData = joblib.load('historicalStockData.pkl')['data']
    idx = 0
    for symbol in symbols:
        try:
            # if idx < 3700:
            #     idx += 1
            #     continue
            print(idx)
            print(symbol)
            vol2Yr, drift2Yr = historicalVolatilityAndDriftOneStock(symbol)
            stockData.loc[symbol]['vols2Yr'] = vol2Yr
            stockData.loc[symbol]['vols2YrUpdated'] = datetime.datetime.now()
            stockData.loc[symbol]['drift2Yr'] = drift2Yr
            stockData.loc[symbol]['drift2YrUpdated'] = datetime.datetime.now()
            idx += 1
            if idx % 100 == 0:
                joblib.dump({"data": stockData}, 'historicalStockData.pkl')
        except:
            idx += 1
            if idx % 100 == 0:
                joblib.dump({"data": stockData}, 'historicalStockData.pkl')

    joblib.dump({"data": stockData}, 'historicalStockData.pkl')

if __name__ == '__main__':
    main()
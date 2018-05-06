import iexUtils
from sklearn.externals import joblib
from earnings import Earning
from OHLC import OHLC
import datetime

def main():
    symbolsData = iexUtils.getAllSymbols()
    symbolsData = iexUtils.filterEnabledSymbols(symbolsData)
    symbolsData = iexUtils.filterCommonStockSymbols(symbolsData)
    symbols = symbolsData.symbol.tolist()

    stockData = joblib.load('historicalStockData.pkl')['data']

    idx = 0
    for symbol in symbols:
        # if idx < 4500:
        #     idx += 1
        #     continue
        print(idx)
        print(symbol)
        try:
            earningsData = iexUtils.getEarnings(symbol)['earnings']
        except:
            continue

        earnings = []
        for earningData in earningsData:
            if earningData['actualEPS'] == None or earningData['consensusEPS'] == None or earningData['estimatedEPS'] == None or earningData['announceTime'] == None or earningData['fiscalPeriod'] == None:
                continue
            reportDate = datetime.datetime.strptime(earningData['EPSReportDate'], "%Y-%m-%d")
            if reportDate >= datetime.datetime.strptime("2018-05-04", "%Y-%m-%d"):
                continue
            earning = Earning(earningData['actualEPS'], earningData['consensusEPS'], earningData['estimatedEPS'], earningData['announceTime'], earningData['EPSSurpriseDollar'], reportDate, earningData['fiscalPeriod'])
            earning.addOHLC(symbol)
            earnings.append(earning)
        if symbol not in stockData.index:
            stockData.loc[symbol] = [None, None, None, None, None, None]
        stockData.loc[symbol]['earnings'] = earnings
        stockData.loc[symbol]['earningsUpdated'] = datetime.datetime.now()

        idx += 1
        if idx % 100 == 0:
            joblib.dump({"data": stockData}, 'historicalStockData.pkl')


if __name__ == '__main__':
    main()
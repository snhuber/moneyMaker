import iexUtils
from sklearn.externals import joblib

def main():
    stockData = joblib.load('historicalStockData.pkl')['data']
    idx = 0
    for sym, row in stockData.iterrows():
        print(idx, sym)
        quote = iexUtils.getQuote(sym)
        stockData.loc[sym, 'avgTotalVolume30'] = quote.avgTotalVolume
        idx += 1
        if idx % 100 == 0:
            joblib.dump({"data": stockData}, 'historicalStockData.pkl')

if __name__ == '__main__':
    main()
import argparse
import datetime
import optionUtils
from option import Option
from stock import Stock
from sklearn.externals import joblib

def get2yrVolatility(symbol):
    dictionary = joblib.load('historicalStockData.pkl')
    volatilities = dictionary['volatilities']
    return float(volatilities[volatilities.Symbol == symbol]['2yrVol'])

def main(symbol):
    stock = Stock(symbol, 44.93)

    hv2yr = get2yrVolatility(symbol)

    callStrike = 45.0
    putStrike = 44.5
    callBid = 2.61
    callAsk = 2.67
    putBid = 2.85
    putAsk = 2.92

    expiryDate = datetime.date(2018, 5, 11)
    earningsDate = datetime.date(2018, 5, 10)
    currentDate = datetime.date.today()
    daysToEarn = (earningsDate - currentDate).days

    call = Option(hv2yr, callStrike, True, callBid, callAsk, expiryDate)
    call.setDaySigma(stock)
    put = Option(hv2yr, putStrike, False, putBid, putAsk, expiryDate)
    put.setDaySigma(stock)

    print("Call XSigma:", call.daySigma/hv2yr)
    print("Put XSigma:", put.daySigma/hv2yr)

    if call.daysToExpiry >= 2.0:
        callTimedecay = optionUtils.calcTimedecay(stock, call)
        putTimedecay = optionUtils.calcTimedecay(stock, put)
        print("One day time decay:", callTimedecay + putTimedecay)
    else:
        print("No time decay with one day remaining")


parser = argparse.ArgumentParser(description='Strangle tracker')
parser.add_argument('symbol',
    help='Stock symbol')

if __name__ == '__main__':
    namespace = parser.parse_args()
    args = vars(namespace)
    main(**args)
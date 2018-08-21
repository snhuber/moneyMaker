import datetime
from option import Option
from stock import Stock
import time

# TODO: repopulate from strangleCandidates or by selecting stocks
WATCH_LIST = ['AMD']

def get2yrVolatility(symbol):
    dictionary = joblib.load('historicalStockData.pkl')
    volatilities = dictionary['volatilities']
    return float(volatilities[volatilities.Symbol == symbol]['2yrVol'])

def main():
	# TODO: take from command line
	user = 'Daniel'
	# TODO: take from command line
	# TODO: execute trades automatically if profit > margin or delta gap > margin
	simulation = True
	# TODO: take from command line
	numberOfMinutesBetweenObservations = 0.125

	while True:
		# TODO: check if during trading hours
		for symbol in WATCH_LIST:
			# TODO: load earnings date dynamically
			earningsDate = datetime.date(2050, 1, 1)
			# TODO: load stock price dynamically
			stockPrice = 1
			hv2yr = get2yrVolatility(symbol)
			stock = Stock(symbol, stockPrice)
			# TODO: load options info dynamically and select options based on stock price
			options = [Option(hv2yr, 1, True, 1, 1, 1)]
			for option in options:
				option.setDaySigma(stock)

			# TODO: compute delta for options

			# TODO: check if folder for user/stock/earnings_date/put(call)_strike exists already and create file if it doesn't
			# TODO: write stock price, option price, XSigma, delta, time decay
		time.sleep(60*numberOfMinutesBetweenObservations)

if __name__ == '__main__':
	main()
import argparse
import datetime
from datetime import date
from option import Option
from stock import Stock
import os
import time
import pandas as pd
from sklearn.externals import joblib
import ibUtils

# TODO: repopulate from strangleCandidates or by selecting stocks
WATCH_LIST = ['AMD']

def get2yrVolatility(symbol):
    dictionary = joblib.load('historicalStockData.pkl')
    volatilities = dictionary['data']
    return float(volatilities[volatilities.index == symbol]['vols2Yr'])

def main(user, executeTrades, timeInterval):
	# TODO: use executeTrades flag to decide whether to trade automatically
	# TODO: execute trades automatically if profit > margin or delta gap > margin

	ib = ibUtils.connect()

	print(user, executeTrades, timeInterval)
	while True:
		print(datetime.datetime.now())
		# TODO: check if during trading hours
		for symbol in WATCH_LIST:
			contract = ibUtils.getStockQualifiedContract(symbol, ib)
			ticker = ibUtils.getTicker(contract, ib)

			# TODO: load earnings date dynamically
			earningsDate = datetime.date(2018, 9, 5)
			expiryDate = datetime.date(2018, 9, 11)
			# TODO: load stock price dynamically
			stockPrice = ticker.last
			print(stockPrice)
			hv2yr = get2yrVolatility(symbol)
			stock = Stock(symbol, stockPrice)
			# TODO: load options info dynamically and select options based on stock price
			options = [Option(hv2yr, 22, True, 1.08, 1.10, expiryDate)]
			for option in options:
				option.setDaySigma(stock)

			# TODO: compute delta for options

			traderExists = os.path.isdir(os.path.join(os.getcwd(), user))
			stockExists = os.path.isdir(os.path.join(os.getcwd(), user, symbol))
			earningsDateExists = os.path.isdir(os.path.join(os.getcwd(), user, symbol, earningsDate.strftime("%d%b%Y")))

			if not traderExists:
				os.mkdir(os.path.join(os.getcwd(), user))

			if not stockExists:
				os.mkdir(os.path.join(os.getcwd(), user, symbol))

			if not earningsDateExists:
				os.mkdir(os.path.join(os.getcwd(), user, symbol, earningsDate.strftime("%d%b%Y")))

			for option in options:
				putCall = "call" if option.call else "put"
				optionPath = os.path.join(os.getcwd(), user, symbol, earningsDate.strftime("%d%b%Y"), putCall+"_"+str(option.strike)+".csv")
				optionExists = os.path.exists(optionPath)
				date = datetime.datetime.now().strftime("%d%b%Y%H%M%S")
				if not optionExists:
					df = pd.DataFrame(columns=["Datetime", "StockPrice", "OptionPrice", "XSigma", "Delta", "TimeDecayOneDay"])
					df.to_csv(optionPath, index=False)

				df = pd.read_csv(optionPath)
				# TODO: make delta real
				# TODO: make time decay real
				df = df.append(pd.Series({"Datetime": date, "StockPrice": stock.currentPrice, "OptionPrice": option.cost, "XSigma": option.daySigma/hv2yr, "Delta": 1, "TimeDecayOneDay": 1}, name=date), ignore_index=True)
				df.to_csv(optionPath, index=False)
		time.sleep(60*timeInterval)

parser = argparse.ArgumentParser(description='Strangle tracker')
parser.add_argument('user', help='The user (which folder data will be stored in)')
parser.add_argument('--executeTrades', dest='executeTrades', action='store_true', help='Whether or not to actually execute trades or to just track data')
parser.add_argument('timeInterval', type=float, default=15, help='The number of minutes between readings')
parser.set_defaults(executeTrades=False)

if __name__ == '__main__':
	namespace = parser.parse_args()
	args = vars(namespace)
	main(**args)
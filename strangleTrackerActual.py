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
from dateutil.tz import tzlocal
from pytz import timezone
from tradingCalendar import USTradingCalendar

# TODO: make more robust to errors: security might not exist, option may have empty bid/ask queue, otranche might diverge, etc

# TODO: repopulate from strangleCandidates or by selecting stocks
# TODO: add parameter for which watch list to use
WATCH_LIST = ['AMD']
EVANS_WATCH_LIST = ['NFLX', 'MSFT', 'FB', 'SNAP', 'AAPL', 'INTC', 'AMZN']
TESTING_WATCH_LIST = ['WDAY', 'TECD', 'KIRK', 'PSEC']
# WDAY: small, AMBA, TECD: large, KIRK, PSEC: medium

def get2yrVolatility(symbol):
    dictionary = joblib.load('historicalStockData.pkl')
    volatilities = dictionary['data']
    return float(volatilities[volatilities.index == symbol]['vols2Yr'])

def main(user, executeTrades, timeInterval, test):
	# TODO: use executeTrades flag to decide whether to trade automatically
	# TODO: execute trades automatically if profit > margin or delta gap > margin
	# TODO: setup tracking for a purchased strangle (i.e. email if profit > margin, or earnings is the next day, or delta spread is large)
	# TODO: analysis tools (option price vs xsigma over time, line for stock price, bar for earnings date), (option prices at different strikes over time), (option price vs delta over time)

	if test:
		print("--------------TEST MODE---------------")

	print(user, executeTrades, timeInterval)
	while True:
		if not test:
			print("Connecting to IB...")
			ib = ibUtils.connect()
		cal = USTradingCalendar()
		eastern = timezone("US/Eastern")
		currentTime = datetime.datetime.now(eastern)
		currentDate = datetime.date.today()
		easternHour = currentTime.hour
		easternMinute = currentTime.minute
		isDuringMarketHours = (easternHour == 6 and easternMinute > 30) or (easternHour > 6 and easternHour < 16)
		isWeekday = currentDate.isoweekday() in range(1, 6)
		isTradingHoliday = currentDate in cal.holidays(start=currentDate, end=currentDate + datetime.timedelta(days=1))
		if (not isDuringMarketHours or not isWeekday or isTradingHoliday) and (not test):
			print("It is either not during market hours or is a holiday. Sleeping until next observation...")
			time.sleep(60*timeInterval)
			continue

		for symbol in TESTING_WATCH_LIST:
			print("\nSymbol:", symbol)
			print(datetime.datetime.now())
			print("Getting contract...")
			if not test:
				contract = ibUtils.getStockQualifiedContract(symbol, ib)
			print("Getting ticker...")
			if not test:
				ticker = ibUtils.getTicker(contract, ib)
			print("Getting earnings date...")
			if not test:
				earningsDate = ibUtils.getNextEarningsDate(contract, ib)
			else:
				earningsDate = datetime.date(2018, 10, 23)

			if not test:
				stockPrice = ticker.marketPrice()
				print("Getting option details...")
				nextExpiry, optionTickers = ibUtils.getOptions(contract, stockPrice, earningsDate, ib)
			else:
				stockPrice = 23.53
				nextExpiry = datetime.date(2018, 11, 16)

			hv2yr = get2yrVolatility(symbol)
			stock = Stock(symbol, stockPrice)
			
			if not test:
				options = []
				for optionTicker in optionTickers:
					if not optionTicker.bid or optionTicker.bid <= 0 or not optionTicker.ask or optionTicker.ask <= 0:
						continue
					else:
						options.append(Option(hv2yr, optionTicker.contract.strike, optionTicker.contract.right == 'C', optionTicker.bid, optionTicker.ask, nextExpiry))
			else:
				options = [Option(hv2yr, 22.0, True, 3.30, 3.35, nextExpiry),
					   		Option(hv2yr, 23.0, True, 3.30, 3.35, nextExpiry),
					   		Option(hv2yr, 24.0, True, 3.30, 3.35, nextExpiry),
					   		Option(hv2yr, 25.0, True, 3.30, 3.35, nextExpiry),
					   		Option(hv2yr, 22.0, False, 3.30, 3.35, nextExpiry),
					   		Option(hv2yr, 23.0, False, 3.30, 3.35, nextExpiry),
					   		Option(hv2yr, 24.0, False, 3.30, 3.35, nextExpiry),
					   		Option(hv2yr, 25.0, False, 3.30, 3.35, nextExpiry)]
			for option in options:
				option.setDaySigma(stock)
				if option.daySigma == None:
					continue
				option.setDelta(stock, hv2yr)
				option.setTimeDecay(stock)

			# TODO: compute delta for options

			cwd = os.getcwd()
			if not test:
				traderPath = os.path.join(cwd, user)
				
			else:
				testPath = os.path.join(cwd, "test")
				traderPath = os.path.join(testPath, user)
				testExists = os.path.isdir(testPath)
				if not testExists:
					os.mkdir(testPath)

			stockPath = os.path.join(traderPath, symbol)
			earningsDatePath = os.path.join(stockPath, earningsDate.strftime("%d%b%Y"))
			expiryDatePath = os.path.join(earningsDatePath, nextExpiry.strftime("%d%b%Y"))

			traderExists = os.path.isdir(traderPath)
			stockExists = os.path.isdir(stockPath)
			earningsDateExists = os.path.isdir(earningsDatePath)
			expiryDateExists = os.path.isdir(expiryDatePath)

			if not traderExists:
				os.mkdir(traderPath)

			if not stockExists:
				os.mkdir(stockPath)

			if not earningsDateExists:
				os.mkdir(earningsDatePath)

			if not expiryDateExists:
				os.mkdir(expiryDatePath)

			for option in options:
				if option.daySigma == None:
					continue
				putCall = "call" if option.call else "put"
				optionPath = os.path.join(expiryDatePath, putCall+"_"+str(option.strike)+".csv")
				optionExists = os.path.exists(optionPath)
				date = datetime.datetime.now().strftime("%d%b%Y%H%M%S")
				if not optionExists:
					df = pd.DataFrame(columns=["Datetime", "StockPrice", "OptionPrice", "XSigma", "Delta", "TimeDecayOneDay"])
					df.to_csv(optionPath, index=False)

				df = pd.read_csv(optionPath)
				df = df.append(pd.Series({"Datetime": date, "StockPrice": stock.currentPrice, "OptionPrice": option.cost, "XSigma": option.daySigma/hv2yr, "Delta": option.delta, "TimeDecayOneDay": option.timeDecay}, name=date), ignore_index=True)
				df.to_csv(optionPath, index=False)

		ib.disconnect()
		print("Sleeping between observations...\n")
		ib.sleep(60*timeInterval)

parser = argparse.ArgumentParser(description='Strangle tracker')
parser.add_argument('user', help='The user (which folder data will be stored in)')
parser.add_argument('--executeTrades', dest='executeTrades', action='store_true', help='Whether or not to actually execute trades or to just track data')
parser.add_argument('timeInterval', type=float, default=15, help='The number of minutes between readings')
parser.add_argument('--test', dest='test', action='store_true', help='Whether to use static test data rather than live data (useful for working outside of trading hours)')
parser.set_defaults(executeTrades=False, test=False)

if __name__ == '__main__':
	namespace = parser.parse_args()
	args = vars(namespace)
	main(**args)
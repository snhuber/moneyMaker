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

# TODO: repopulate from strangleCandidates or by selecting stocks
WATCH_LIST = ['AMD']

def get2yrVolatility(symbol):
    dictionary = joblib.load('historicalStockData.pkl')
    volatilities = dictionary['data']
    return float(volatilities[volatilities.index == symbol]['vols2Yr'])

def main(user, executeTrades, timeInterval):
	# TODO: use executeTrades flag to decide whether to trade automatically
	# TODO: execute trades automatically if profit > margin or delta gap > margin

	print("Connecting to IB...")
	ib = ibUtils.connect()

	print(user, executeTrades, timeInterval)
	while True:
		cal = USTradingCalendar()
		eastern = timezone("US/Eastern")
		currentTime = datetime.datetime.now(eastern)
		currentDate = datetime.date.today()
		easternHour = currentTime.hour
		easternMinute = currentTime.minute
		isDuringMarketHours = (easternHour == 6 and easternMinute > 30) or (easternHour > 6 and easternHour < 17)
		isWeekday = currentDate.isoweekday() in range(1, 6)
		isTradingHoliday = currentDate in cal.holidays(start=currentDate, end=currentDate + datetime.timedelta(days=1))
		if not isDuringMarketHours or not isWeekday or isTradingHoliday:
			print("It is either not during market hours or is a holiday. Sleeping until next observation...")
			time.sleep(60*timeInterval)
			continue

		for symbol in WATCH_LIST:
			print("\nSymbol:", symbol)
			print("Getting contract...")
			contract = ibUtils.getStockQualifiedContract(symbol, ib)
			print("Getting ticker...")
			ticker = ibUtils.getTicker(contract, ib)
			print("Getting earnings date...")
			earningsDate = ibUtils.getNextEarningsDate(contract, ib)

			expiryDate = datetime.date(2018, 9, 11)

			stockPrice = ticker.marketPrice()
			print("Getting option details...")
			nextExpiry, optionTickers = ibUtils.getOptions(contract, stockPrice, earningsDate, ib)
			print(optionTickers)
			hv2yr = get2yrVolatility(symbol)
			stock = Stock(symbol, stockPrice)
			# TODO: load options info dynamically and select options based on stock price
			options = [Option(hv2yr, opt.contract.strike, opt.contract.right == 'C', opt.bid, opt.ask, nextExpiry) for opt in optionTickers]
			# print(options)
			# options = list(filter(lambda x: ((stockPrice < x.strike) and x.call) or ((stockPrice > x.strike) and not x.call), options))
			for option in options:
				print(option.expiry, option.strike, option.call, option.bid, option.ask, stockPrice)
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

		print("Sleeping between observations...\n")
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
import ib_insync
from ib_insync import *
import xml.etree.ElementTree as etree
import datetime

def connect():
	ib = IB()
	ib.connect('127.0.0.1', 4001, clientId=10)
	return ib

def getStockQualifiedContract(symbol, ib):
	contract = Stock(symbol, 'SMART', 'USD')
	ib.qualifyContracts(contract)
	return contract

def getTicker(contract, ib):
	ticker = ib.reqMktData(contract, "", False, False)
	while ticker.last != ticker.last: ib.sleep(0.01)
	ib.cancelMktData(contract)
	return ticker

def getNextEarningsDate(contract, ib):
	xmlCalendarReport = ib.reqFundamentalData(contract, "CalendarReport")
	root = etree.fromstring(xmlCalendarReport)
	company = root[0]
	earningsList = company.find('EarningsList')
	earnings = earningsList[0]
	period = earnings.find('Period').text
	date = earnings.find(period).text
	return datetime.datetime.strptime(date, "%m/%d/%Y")

def getOptions(contract, marketPrice, earningsDate, ib):
	# contract = Option(symbol, exchange='SMART', )
	# contractDetails = ib.reqContractDetails(contract)
	# contracts = [cd.summary for cd in contractDetails]
	# print(contracts[0])
	dateformat = "%Y%m%d"
	chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
	smartChain = list(filter(lambda x: x.exchange == 'SMART', chains))[0]
	nextExpiry = None
	for expiry in sorted(smartChain.expirations):
		date = datetime.datetime.strptime(expiry, dateformat)
		if date > earningsDate:
			nextExpiry = expiry
			break

	idx = None
	intStrikes = list(filter(lambda x: int(x) == x, sorted(smartChain.strikes)))
	for i, strike in enumerate(intStrikes):
		if marketPrice < strike:
			idx = i
			break

	sixStrikes = intStrikes[idx-3:idx+3]

	options = [Option(contract.symbol, nextExpiry, strike, right, 'SMART')
			for right in ['P', 'C']
			for strike in sixStrikes]

	ib.qualifyContracts(*options)
	# tickers = ib.reqTickers(*options)
	tickers = []
	print("Requesting option market data...")
	for option in options:
		ticker = ib.reqMktData(option, "", True, False)
		# Needed to make sure the data gets properly loaded, reqMktData is supposed to
		# be blocking but doesn't seem to actually be
		while ticker.bid != ticker.bid or ticker.ask != ticker.ask: ib.sleep(0.01)
		tickers.append(ticker)
	return datetime.datetime.strptime(nextExpiry, dateformat).date(), tickers



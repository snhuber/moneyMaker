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
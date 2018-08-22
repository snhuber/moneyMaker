import ib_insync
from ib_insync import *

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
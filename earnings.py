import datetime
import iexUtils
from OHLC import OHLC

class Earning(object):
    def __init__(self, actualEPS, consensusEPS, estimatedEPS, announceTime, EPSSurpriseDollar, EPSReportDate, fiscalPeriod):
        self.actualEPS = actualEPS
        self.consensusEPS = consensusEPS
        self.estimatedEPS = estimatedEPS
        self.announceTime = announceTime
        self.EPSSurpriseDollar = EPSSurpriseDollar
        self.EPSReportDate = EPSReportDate
        self.quarter = fiscalPeriod.split()[0]
        self.year = fiscalPeriod.split()[1]
        self.beforeEarnings = None
        self.afterEarnings = None

    def calculateOHLC(self, date, data):
        daysData = data.loc[datetime.datetime.strftime(date, "%Y-%m-%d")]
        return daysData.open, daysData.high, daysData.low, daysData.close

    def addOHLC(self, symbol):
        beforeDelta = datetime.timedelta(days=-1*(self.announceTime == "BTO"))
        afterDelta = datetime.timedelta(days=self.announceTime == "AMC")

        beforeDate = self.EPSReportDate + beforeDelta
        afterDate = self.EPSReportDate + afterDelta
        if beforeDate.weekday() == 6:
            beforeDate = beforeDate + datetime.timedelta(days=-2)
        if afterDate.weekday() == 5:
            afterDate = afterDate + datetime.timedelta(days=2)

        historicalData = iexUtils.getHistoricalData(symbol, "5y")
        historicalData = historicalData.set_index(historicalData.date)
        while not datetime.datetime.strftime(beforeDate, "%Y-%m-%d") in historicalData.index:
            beforeDate = beforeDate + datetime.timedelta(days=-1)
        while not datetime.datetime.strftime(afterDate, "%Y-%m-%d") in historicalData.index:
            afterDate = afterDate + datetime.timedelta(days=1)

        beforeOpen, beforeHigh, beforeLow, beforeClose = self.calculateOHLC(beforeDate, historicalData)
        afterOpen, afterHigh, afterLow, afterClose = self.calculateOHLC(afterDate, historicalData)

        beforeOHLC = OHLC(beforeOpen, beforeHigh, beforeLow, beforeClose)
        afterOHLC = OHLC(afterOpen, afterHigh, afterLow, afterClose)

        self.beforeEarnings = beforeOHLC
        self.afterEarnings = afterOHLC


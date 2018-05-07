import iexUtils
from sklearn.externals import joblib
from hvEstimation import historicalVolatilityAndDriftOneStock
import math
import datetime
from earnings import Earning
import pandas as pd

def tryFillNaNs():
    stockData = joblib.load('historicalStockData.pkl')['data']

    for sym, row in stockData.iterrows():
        earningsUpdated = row['earningsUpdated']
        volUpdated = row['vols2YrUpdated']
        driftUpdated = row['drift2YrUpdated']
        if pd.isnull(earningsUpdated):
            print("Updating earnings:", sym)

            try:
                earningsData = iexUtils.getEarnings(sym)['earnings']
            except:
                stockData.loc[sym, 'earningsUpdated'] = datetime.datetime.now()
                continue

            earnings = []
            for earningData in earningsData:
                if earningData['actualEPS'] == None or earningData['consensusEPS'] == None or earningData['estimatedEPS'] == None or earningData['announceTime'] == None or earningData['fiscalPeriod'] == None:
                    stockData.loc[sym, 'earningsUpdated'] = datetime.datetime.now()
                    continue
                reportDate = datetime.datetime.strptime(earningData['EPSReportDate'], "%Y-%m-%d")
                if reportDate >= datetime.datetime.strptime("2018-05-04", "%Y-%m-%d"):
                    stockData.loc[sym, 'earningsUpdated'] = datetime.datetime.now()
                    continue
                earning = Earning(earningData['actualEPS'], earningData['consensusEPS'], earningData['estimatedEPS'], earningData['announceTime'], earningData['EPSSurpriseDollar'], reportDate, earningData['fiscalPeriod'])
                earning.addOHLC(sym)
                earnings.append(earning)
            stockData.loc[sym, 'earnings'] = earnings
            stockData.loc[sym, 'earningsUpdated'] = datetime.datetime.now()

        if pd.isnull(volUpdated) or pd.isnull(driftUpdated):
            print("Updating drift and vol:", sym)
            vol2Yr, drift2Yr =historicalVolatilityAndDriftOneStock(sym)
            stockData.loc[sym, 'vols2Yr'] = vol2Yr
            stockData.loc[sym, 'vols2YrUpdated'] = datetime.datetime.now()
            stockData.loc[sym, 'drift2Yr'] = drift2Yr
            stockData.loc[sym, 'drift2YrUpdated'] = datetime.datetime.now()

    joblib.dump({"data": stockData}, 'historicalStockData.pkl')
from sklearn.externals import joblib
import numpy as np
import pandas as pd
from strangleTrackerActual import EVANS_WATCH_LIST
import ibUtils
import datetime

# TODO: add some parameters for what list of stocks to explore (e.g. all, or evans watch list, or our watch list)
# TODO: add a function to report meanSigma for a given stock

def calculateCandidateInfo(data, symbol):
    xsigmas = []
    for earning in data['earnings']:
        cgr = np.log(earning.afterEarnings.closePrice/earning.beforeEarnings.closePrice)
        xsigma = (cgr - data['drift2Yr'])/data['vols2Yr']
        xsigmas.append(abs(xsigma))
    return np.max(xsigmas), np.min(xsigmas), np.mean(xsigmas)

def main():
    stockData = joblib.load('historicalStockData.pkl')['data']

    sigmas = []
    for sym, row in stockData.iterrows():
        if ((not isinstance(row['earnings'], list)) and pd.isnull(row['earnings'])) or row['earnings'] == [] or pd.isnull(row['vols2Yr']) or pd.isnull(row['drift2Yr']) or len(row['earnings']) < 4 or row['avgTotalVolume30'] < 100000:
            continue
        maxSigma, minSigma, meanSigma = calculateCandidateInfo(row, sym)
        sigmas.append((meanSigma, sym))

    ib = ibUtils.connect()
    today = datetime.date.today()
    upcoming = []
    for sigma in sigmas:
        contract = ibUtils.getStockQualifiedContract(sigma[1], ib)
        nextEarnings = ibUtils.getNextEarningsDate(contract, ib)
        # TODO: figure out better way to catch this error
        if nextEarnings == None:
            continue

        if (nextEarnings.date() - today).days < 10:
            upcoming.append(sigma)

    for upcomingStock in upcoming:
        print(upcomingStock)

if __name__ == '__main__':
    main()
from sklearn.externals import joblib
import numpy as np
import pandas as pd

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

    print(sorted(sigmas))

if __name__ == '__main__':
    main()
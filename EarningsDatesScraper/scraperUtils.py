import pickle
import importlib
mainScraper = importlib.import_module('mainScraper')


# Update the earnings dates pickles
def updateEarningsDates():
    print("Updating earnings dates pickle through scraping...")
    mainScraper.main(12)
    print("Earnings dates pickle updated")

# Retrieve an earnings date
def getNextEarningsDate(ticker):
    fileName = "earningsDates.pickle"
    pkl_file = open(fileName, 'rb')
    d = pickle.load(pkl_file)
    print(d[ticker])

# Example
updateEarningsDates()
getNextEarningsDate("HOV")
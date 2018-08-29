import datetime
import pickle

import importlib
nasdaqScraper = importlib.import_module('nasdaqScraper')
import importlib
yahooScraper = importlib.import_module('yahooScraper')



def main():
    # Get the earnings dates
    today = datetime.datetime.today()
    currentDay = today
    daysInAdvance = 5
    earningsDates = []
    earningsDatesNasdaq = []
    earningsDatesYahoo = []
    print("Getting the earnings dates for the next " + str(daysInAdvance) + " days...")

    # Go through each date and scrape from each website
    for _ in range(daysInAdvance):
        print(currentDay.strftime('%Y-%m-%d') + ":")

        # Get the earnings dates from nasdaq
        print("\tScraping from https://www.nasdaq.com/")
        earningsDatesNasdaq += nasdaqScraper.get(currentDay)
        
        # Get the earnings dates from nasdaq
        print("\tScraping from https://biz.yahoo.com/")
        earningsDatesYahoo += yahooScraper.get(currentDay)

        # Increment to the next day
        currentDay += datetime.timedelta(1)

    # Concatenate dates
    earningsDates += earningsDatesNasdaq
    earningsDates += earningsDatesYahoo

    updatePickle(earningsDates)

# Opens pickle file, pulls dictionary, deletes dictionary, and adds new dictionary.
# If file isn't present, it creates a file (should be "git.ignore"ed).
def updatePickle(earningsDates):
    # Add them to pickle
    fileName = "earningsDates.pickle"
    file = open(fileName, "w+")
    earningsDictionaryNew = {}
    for eD in earningsDates:
        ticker = earningsDates[0]
        date = earningsDates[1]
        earningsDictionaryNew[ticker] = date

    with open(fileName, 'wb') as handle:
        pickle.dump(earningsDictionaryNew, handle, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
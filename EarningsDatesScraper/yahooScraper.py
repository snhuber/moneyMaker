from bs4 import BeautifulSoup
import urllib.request
import requests
import datetime
import re


def get(date):
    # Get the soup from the URL after adding the date
    dateStr = date.strftime('%Y-%m-%d')
    yahooSauce = requests.get("https://finance.yahoo.com/calendar/earnings?day=" + dateStr, headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0"}).text
    soup = BeautifulSoup(yahooSauce, 'html.parser')

    # Check if the format is the same
    if (formatChanged(soup)):
        return []

    # Check if there is data
    if (noData(soup)):
        return []
    
    earningsDates = retrieveEarningsDates(soup, date)

    return earningsDates



def retrieveEarningsDates(soup, date):
    # The ticker is found in links with classes 'Fw(b)'
    tickerTd = soup.findAll(lambda tag: tag.name=='a' and tag.has_attr('data-symbol')
        and 'Fw(b)' in tag.get('class'))


    # Go through all the tickers, find their dates, and add them to earningDates
    earningsDates = []
    for td in tickerTd:
        # Get the ticker from contents
        ticker = str(td.contents[0])

        # Get the time from the next next sibling 'td'
        date = datetime.datetime(date.year, date.month, date.day)
        timeTd = td.parent.findNext('td').findNext('td')
        # The time is either written in contents or in a span.
        time = datetime.timedelta(hours = 12)
        if (timeTd.find('span')):
            timeIndicator = timeTd.find('span').contents[0]
            if (timeIndicator == 'Before Market Open'):
                time = datetime.timedelta(hours = 6.5)
            elif (timeIndicator == 'After Market Close'):
                time = datetime.timedelta(hours = 12 + 1)
            else:
                print("\t\tunknown time, time set as noon for " + ticker)
        else:
            # The time is written as '4:30AM EST'
            timeIndicator = timeTd.contents[0]
            hour = float(timeIndicator[0 : timeIndicator.find(":")]) + 12 * ('PM' in timeIndicator)
            minute = float(timeIndicator[timeIndicator.find(":") + 1 : timeIndicator.find(":") + 3])
            time = datetime.timedelta(hours = hour, minutes = minute)
            
        earningsDateTime = date + time
        earningsDates.append((ticker, earningsDateTime))

    return earningsDates


# Returns true if format changed
def formatChanged(soup):
    # Check if information is still in the same td.
    try:
        tickerTd = soup.findAll(lambda tag: tag.name=='a' and tag.has_attr('data-symbol')
            and 'Fw(b)' in tag.get('class'))
        if (tickerTd != []):
            td = tickerTd[0]
            ticker = td.contents[0]
            timeTd = td.parent.findNext('td').findNext('td')
    except Exception as e:
        print("\t\tThe format has changed")
        return True

    return False


# Returns true if there is no data
def noData(soup):
    tickerTd = soup.findAll(lambda tag: tag.name=='a' and tag.has_attr('data-symbol')
        and 'Fw(b)' in tag.get('class'))
    if (tickerTd == []):
        print("\t\tThere is no data this date")
        return True

    return False
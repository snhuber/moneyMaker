from bs4 import BeautifulSoup
import urllib.request
import datetime

def get(date):
	# Get the soup from the URL after adding the date
	nasdaqURLNoDate = 'https://www.nasdaq.com/earnings/earnings-calendar.aspx?date='
	dateStr = date.strftime('%Y-%m-%d')
	nasdaqURL = nasdaqURLNoDate + dateStr
	nasdaqReq = urllib.request.Request(nasdaqURL)
	nasdaqSauce = urllib.request.urlopen(nasdaqReq).read()
	soup = BeautifulSoup(nasdaqSauce, 'html.parser')

	# Check if the format is the same
	if (formatChanged(soup)):
		return []

	# Check if there is data
	if (noData(soup)):
		return []

	earningDates = retrieveEarningDates(soup, date)

	return earningDates


def retrieveEarningDates(soup, date):
	# Data is stored in the table with id ECCompaniesTable which has columns for the Name and Time
	# the earnings report is released.
	table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ECCompaniesTable")

	# From the table, the company names and tickers are in links that have ids/
	companyList = table.findAll(lambda tag: tag.name=='a' and tag.has_attr('id'))

	# From the table, the times are signified with a link with an image signifying if earnings are
	# reported at the opening or closing time that day.
	timeList = table.findAll(lambda tag: tag.name=='a' and tag.has_attr('title'))

	# Go through both lists and populate earningsDates
	earningsDates = []
	for companyI in range(len(companyList)):
		# Get the tickers which are in parentheses in the company name.
		fullName = companyList[companyI].get_text()
		ticker = str(fullName[fullName.find("(") + 1 : fullName.find(")")])

		# Get the date without time as a datetime object then add the time to open or close
		# depending on the timeList.
		date = datetime.datetime(date.year, date.month, date.day)
		time = datetime.timedelta(hours = 12)
		if (timeList[companyI].get('title') == "Pre-market Quotes"):
			time = datetime.timedelta(hours = 6.5)
		elif (timeList[companyI].get('title') == "After Hours Quotes"):
			time = datetime.timedelta(hours = 12 + 1)
		else:
			print("\t\tunknown time, time set as noon for " + ticker)

		earningsDateTime = date + time
		earningsDates.append((ticker, earningsDateTime))

	return earningsDates


# Returns true if format changed
def formatChanged(soup):
	# Check if information is still in the same table.
	try:
		table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ECCompaniesTable")

		if (table != None):
			companyList = table.findAll(lambda tag: tag.name=='a' and tag.has_attr('id'))
			timeList = table.findAll(lambda tag: tag.name=='a' and tag.has_attr('title'))

			if (not companyList or not timeList):
				print("\t\tThe format has changed")
				return True
	except Exception as e:
		print("\t\tThe format has changed")
		return True

	return False


# Returns true if there is no data
def noData(soup):
	table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="ECCompaniesTable")
	if (table == None):
		print("\t\tThere is no data this date")
		return True

	return False

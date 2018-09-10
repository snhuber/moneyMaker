import argparse
import os
import analysisUtils
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl

def main(user, stock, earningsDateStrFormat, expiryDateStrFormat, putStrike, callStrike):
	userPath = analysisUtils.getUserPath(user)
	expiryPath = analysisUtils.getExpiryPath(user, stock, earningsDateStrFormat, expiryDateStrFormat)
	optionsFilesNames = analysisUtils.getAllOptionsFiles(expiryPath)
	callFilesNames = list(filter(lambda x: x.startswith("call"), optionsFilesNames))
	putFilesNames = list(filter(lambda x: x.startswith("put"), optionsFilesNames))

	# plotting stock price and option price
	fig, ax1 = plt.subplots()
	ax1.set_xlabel('datetime')
	ax1.set_ylabel('stock price', color='b')
	ax1.tick_params('y', colors='b')
	ax2 = ax1.twinx()
	ax2.set_ylabel('option price')
	ax2.tick_params('y')
	for callFileName in callFilesNames:
		callPath = analysisUtils.getOptionPath(expiryPath, callFileName)
		call = analysisUtils.getOption(callPath)
		datetimes = [datetime.datetime.strptime(s, "%d%b%Y%H%M%S") for s in call['Datetime']]
		stockPrice = call['StockPrice']
		optionPrice = call['OptionPrice']
		ax1.plot(datetimes, stockPrice, 'b')
		ax2.plot(datetimes, optionPrice, 'r')

	for putFileName in putFilesNames:
		putPath = analysisUtils.getOptionPath(expiryPath, putFileName)
		put = analysisUtils.getOption(putPath)
		datetimes = [datetime.datetime.strptime(s, "%d%b%Y%H%M%S") for s in put['Datetime']]
		stockPrice = put['StockPrice']
		optionPrice = put['OptionPrice']
		ax1.plot(datetimes, stockPrice, 'b')
		ax2.plot(datetimes, optionPrice, 'g')

	ax1.axvline(x=datetime.datetime.strptime(earningsDateStrFormat, "%d%b%Y"))
	fig.tight_layout()
	plt.show()

	# plotting stock price and xsigma
	fig, ax1 = plt.subplots()
	ax1.set_xlabel('datetime')
	ax1.set_ylabel('stock price', color='b')
	ax1.tick_params('y', colors='b')
	ax2 = ax1.twinx()
	ax2.set_ylabel('xsigma')
	ax2.tick_params('y')
	for callFileName in callFilesNames:
		callPath = analysisUtils.getOptionPath(expiryPath, callFileName)
		call = analysisUtils.getOption(callPath)
		datetimes = [datetime.datetime.strptime(s, "%d%b%Y%H%M%S") for s in call['Datetime']]
		stockPrice = call['StockPrice']
		optionPrice = call['XSigma']
		ax1.plot(datetimes, stockPrice, 'b')
		ax2.plot(datetimes, optionPrice, 'r')

	for putFileName in putFilesNames:
		putPath = analysisUtils.getOptionPath(expiryPath, putFileName)
		put = analysisUtils.getOption(putPath)
		datetimes = [datetime.datetime.strptime(s, "%d%b%Y%H%M%S") for s in put['Datetime']]
		stockPrice = put['StockPrice']
		optionPrice = put['XSigma']
		ax1.plot(datetimes, stockPrice, 'b')
		ax2.plot(datetimes, optionPrice, 'g')

	ax1.axvline(x=datetime.datetime.strptime(earningsDateStrFormat, "%d%b%Y"))
	fig.tight_layout()
	plt.show()

	# plotting xsigma and option price for the selected strangle
	strangleCallPath = analysisUtils.getOptionPath(expiryPath, 'call_'+str(float(callStrike))+'.csv')
	stranglePutPath = analysisUtils.getOptionPath(expiryPath, 'put_'+str(float(putStrike))+'.csv')
	strangleCall = analysisUtils.getOption(strangleCallPath)
	stranglePut = analysisUtils.getOption(stranglePutPath)
	callDatetimes = [datetime.datetime.strptime(s, "%d%b%Y%H%M%S") for s in strangleCall['Datetime']]
	putDatetimes = [datetime.datetime.strptime(s, "%d%b%Y%H%M%S") for s in stranglePut['Datetime']]
	bothDatetimes = []
	sumValue = []
	for i, callDatetime in enumerate(callDatetimes):
		if callDatetime in putDatetimes:
			idx = putDatetimes.index(callDatetime)
			bothDatetimes.append(callDatetime)
			sumValue.append(strangleCall['OptionPrice'][i] + stranglePut['OptionPrice'][idx])

	fig, ax1 = plt.subplots()
	ax1.set_xlabel('datetime')
	ax1.set_ylabel('option price')
	ax1.tick_params('y')
	ax2 = ax1.twinx()
	ax2.set_ylabel('xsigma')
	ax2.tick_params('y')
	ax1.plot(callDatetimes, strangleCall['OptionPrice'], 'r')
	ax1.plot(putDatetimes, stranglePut['OptionPrice'], 'b')
	ax2.plot(callDatetimes, strangleCall['XSigma'], 'g')
	ax2.plot(putDatetimes, stranglePut['XSigma'], 'y')
	ax1.plot(bothDatetimes, sumValue, 'k')
	ax1.axvline(x=datetime.datetime.strptime(earningsDateStrFormat, "%d%b%Y"))
	plt.show()

parser = argparse.ArgumentParser(description='Analysis')
parser.add_argument('user', help='The user (which folder data will be stored in)')
parser.add_argument('--stock', help='The stock to analyze')
parser.add_argument('--earningsDateStrFormat', help='The earnings date to analyze (format: ddMonYYYY')
parser.add_argument('--expiryDateStrFormat', help='The expiry date to analyze (format: ddMonYYYY')
parser.add_argument('--putStrike', help='The put to view')
parser.add_argument('--callStrike', help='The call to view')


if __name__ == '__main__':
	namespace = parser.parse_args()
	args = vars(namespace)
	main(**args)
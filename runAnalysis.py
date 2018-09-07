import argparse
import os
import analysisUtils

def main(user, stock, earningsDateStrFormat, expiryDateStrFormat):
	userPath = analysisUtils.getUserPath(user)
	expiryPath = analysisUtils.getExpiryPath(user, stock, earningsDateStrFormat, expiryDateStrFormat)
	optionsFilesNames = analysisUtils.getAllOptionsFiles(expiryPath)
	callFilesNames = list(filter(lambda x: x.startswith("call"), optionsFilesNames))
	putFilesNames = list(filter(lambda x: x.startswith("put"), optionsFilesNames))

	firstCallPath = analysisUtils.getOptionPath(expiryPath, callFilesNames[0])
	firstCall = analysisUtils.getOption(firstCallPath)
	print(firstCall)

parser = argparse.ArgumentParser(description='Analysis')
parser.add_argument('user', help='The user (which folder data will be stored in)')
parser.add_argument('--stock', help='The stock to analyze')
parser.add_argument('--earningsDateStrFormat', help='The earnings date to analyze (format: ddMonYYYY')
parser.add_argument('--expiryDateStrFormat', help='The expiry date to analyze (format: ddMonYYYY')


if __name__ == '__main__':
	namespace = parser.parse_args()
	args = vars(namespace)
	main(**args)
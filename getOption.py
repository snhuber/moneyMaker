import sys
from ib_insync import *
import datetime

def getOption(ib, ticker='SPY', exchange='SMART', currency='USD', optType='C', year=None, day=None, month=None, strike=0.0, date=None):
    """
    getOption returns a single contract based on the provided parameters or a LookupError if no contract exists.
    Either year (YYYY), day (D or DD), and month (M or MM) or date (YYMMDD) can be provided.

    Inputs
    ---------------
        ib                  - [ib object] the ib client to be used
        ticker              - [string] the ticker symbol of the option contract. 'SPY' default
        exchange            - [string] the exchange to use. 'SMART' default
        currency            - [string] the currency to use. 'USD' default
        optType             - [string] the type of option ('P' or 'C' for put and call). 'C' is default
        year                - [int] the desired expiry year (YYYY)
        day                 - [int] the desired expiry day (D or DD)
        month               - [int] the desired expiry month (M or MM)
        strike              - [float] the desired strike price
        date                - [int] the desired expiry date (YYMMDD). either date or year/month/day will be used

    Outputs
    ---------------
        contract            - [ib contract] the desired option contract

    """
    
    # add leading 0s to month and day as necessary
    monthDayLen = 2
    while len(str(month)) < monthDayLen:
        month = '0' + str(month)

    while len(str(day)) < monthDayLen:
        day = '0' + str(day)

    # use the date or year/month/day params to get expiry date
    if date == None:
        date = str(year)[-2:] + str(month) + str(day)
    else:
        date = str(date)

    # compute the integer and fraction parts of the strike
    # 105.5 -> intPart = 105; fractPart = 5
    intPart = str(int(strike))
    fractPart = str(round(strike % 1, 3))[2:]

    # add leading 0s to strike price to match local symbol lookup format
    fractLen = 3
    intLen = 5
    while len(fractPart) < fractLen:
        fractPart = fractPart + '0'

    while len(intPart) < intLen:
        intPart = '0' + intPart

    # construct the local symbol attribute
    # format: <ticker>   <YYMMDD><optType><Strike> where <strike> has 5 integer digits and 3 fraction digits
    localSymbol = ticker + ' '*3 + date + optType + intPart + fractPart

    # collect option and contracts
    option = Option(ticker, exchange=exchange, localSymbol=localSymbol, currency=currency)
    contracts = ib.reqContractDetails(option)

    # if no contracts were returned, raise LookupError
    if len(contracts) == 0:
        raise LookupError("No option exists with ticker:", ticker, "exchange:", exchange, "type:", optType, "date (YYMMDD):", date, "strike:", strike)

    # return first contract summary!
    return contracts[0].summary


if __name__ == '__main__':

    ############################################
    #           Example program                #
    ############################################

    # setup IB client 
    ib = IB()
    ib.connect('127.0.0.1', 4001, clientId=421)

    # print option
    print(getOption(ib, ticker='SPY', exchange='SMART', optType='P', date=190621, strike=215))
    
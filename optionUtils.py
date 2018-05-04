import numpy as np
import datetime
import math

def csnd(point):
    return (1.0 + math.erf(point/math.sqrt(2.0)))/2.0

def durationVolatility(dayVolatility, duration):
    return dayVolatility*np.sqrt(duration)

def lnmeanshift(sigma):
    return 1.0*math.exp(-1.0*(sigma*sigma/2))

def calcTimedecay(stock, option):
    timedecayDays = float(option.daysToExpiry) - 1
    newDurSigma = durationVolatility(option.daySigma, timedecayDays)
    price1Day = otranche(stock, option, newDurSigma)
    timedecay = (option.cost - price1Day)
    return timedecay

def otranche(stock, option, sigma):
    sspread = (math.log(option.strike/stock.currentPrice))/sigma
    if option.call:
        binborder = np.linspace(sspread, 5.00, num=24, dtype=float)
    else:
        binborder = np.linspace(-5.0, sspread, num=24, dtype=float)
    size = len(binborder)
    binedgeprob = np.zeros(size)

    for i in range(0,size):
        binedgeprob[i] = csnd(binborder[i])
    size = size - 1
    binprob = np.zeros(size)
    binmidprice = np.zeros(size)
    binvalue = np.zeros(size)

    for i in range(0, size):
        binprob[i] = binedgeprob[i+1] - binedgeprob[i]
        binmidprice[i] = ((stock.currentPrice*math.exp(((binborder[i+1]+binborder[i])/2.0)
        *sigma))*lnmeanshift(sigma)) - option.strike
        binvalue[i] = binmidprice[i]*binprob[i]

    if option.call:
        optionprice = np.sum(binvalue[0:(i+1)])
    else:
        optionprice = (np.sum(binvalue[0:(i+1)]))*-1.0

    return optionprice
import datetime
import optionUtils
import numpy as np
import math

class Option(object):
    def __init__(self, hv2yr, strike, call, bid, ask, expiry):
        self.hv2yr = hv2yr
        self.strike = strike
        self.call = call
        self.bid = bid
        self.ask = ask
        self.expiry = expiry
        self.daysToExpiry = (self.expiry - datetime.date.today()).days
        self.cost = self.bid + 0.6*(self.ask - self.bid)
        self.daySigma = None
        self.durSigma = None
        self.delta = None

    def setDaySigma(self, stock):
        try:
            seedsigma = 1e-6
            cutoff = 1e-4
            tempop = 0.0
            price2 = 0.0
            deriv = 0.0
            durseed = optionUtils.durationVolatility(seedsigma, self.daysToExpiry)
            self.daySigma = 0.06 if self.call else 0.01
            self.durSigma = optionUtils.durationVolatility(self.daySigma, self.daysToExpiry)

            while np.abs(tempop - self.cost) > cutoff:
                tempop = optionUtils.otranche(stock, self, self.durSigma)
                price2 = optionUtils.otranche(stock, self, self.durSigma+durseed)
                deriv = (price2-tempop)/seedsigma
                self.daySigma -= (tempop-self.cost)/deriv
                self.durSigma = optionUtils.durationVolatility(self.daySigma, self.daysToExpiry)
        except:
            self.daySigma = 0
            self.durSigma = 0

    def setDelta(self, stock, hv):
        rfir = 0.01
        d1 = math.log(stock.currentPrice/self.strike) + ((rfir/365) + (hv**2)/2)*self.daysToExpiry
        durvol = hv*math.sqrt(self.daysToExpiry)
        delta = optionUtils.csnd(d1/durvol)
        self.delta = delta

    def setTimeDecay(self, stock):
        if self.daySigma == 0 or self.durSigma == 0:
            self.timeDecay = 0
        elif self.daysToExpiry < 2:
            print("WARNING: One day to expiry, setting time decay to 0")
            self.timeDecay = 0
        else:
            oneDayDurSigma = optionUtils.durationVolatility(self.daySigma, self.daysToExpiry-1)
            oneDayPrice = optionUtils.otranche(stock, self, oneDayDurSigma)
            self.timeDecay = self.cost - oneDayPrice

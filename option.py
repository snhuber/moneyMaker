class Option(object):
    def __init__(self, hv2yr, strike, call, bid, ask, expiry):
        self.hv2yr = hv2yr
        self.strike = strike
        self.call = call
        self.bid = bid
        self.ask = ask
        self.expiry = expiry

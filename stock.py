from earnings import Earning

class Stock(object):
    def __init__(self, symbol, price):
        self.symbol = symbol
        self.currentPrice = price
        self.earnings = None

    def saveEarnings(earnings):
        self.earnings = earnings
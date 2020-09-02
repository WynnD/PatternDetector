from .detector import Detector
from patterndetector.data import Data

class EngulfingCandleDetector(Detector):
    def __init__(self, data: Data):
        super().__init__(data)
    
    @property
    def name(self):
        return 'Engulfing Candle'

    def isPattern(self, ticker):
        openPrice = self.data.getOpeningPriceNDaysAgo(ticker, days=0)
        openPrice2 = self.data.getOpeningPriceNDaysAgo(ticker, days=1)
        closePrice = self.data.getClosingPriceNDaysAgo(ticker, days=0)
        closePrice2 = self.data.getClosingPriceNDaysAgo(ticker, days=1)
        return (closePrice > openPrice2 and openPrice < closePrice2 and openPrice2 > closePrice2 and openPrice < closePrice) or (openPrice > closePrice2 and closePrice < openPrice2 and closePrice2 > openPrice2 and closePrice < openPrice)

from .detector import Detector

class OutsideDayDetector(Detector):
    def __init__(self, tickers):
        super().__init__(tickers)

    def detect(self, ticker, relativeVolThreshold=2, volumeThreshold=200000):
        percentChangeYesterday = self.getPercentChangeNDaysAgo(ticker, days=0)
        isEngulfingCandle = self.isEngulfingCandle(ticker)
        
        if isEngulfingCandle:
            try:
                avgVolume = self.getAverageVolume(ticker)
            except:
                return False
            volume = self.getVolumeNDaysAgo(ticker, 0)
            relativeVol = volume / avgVolume
            if relativeVol > relativeVolThreshold and avgVolume > volumeThreshold:
                return {
                    'ticker': ticker,
                    'percent_change': percentChangeYesterday,
                    'volume': volume,
                    'relative_vol': relativeVol
                }
        else: 
            return False

    def isPattern(self, ticker):
        openPrice = self.getOpeningPriceNDaysAgo(ticker, days=0)
        openPrice2 = self.getOpeningPriceNDaysAgo(ticker, days=1)
        closePrice = self.getClosingPriceNDaysAgo(ticker, days=0)
        closePrice2 = self.getClosingPriceNDaysAgo(ticker, days=1)
        return (closePrice > openPrice2 and openPrice < closePrice2 and openPrice2 > closePrice2 and openPrice < closePrice) or (openPrice > closePrice2 and closePrice < openPrice2 and closePrice2 > openPrice2 and closePrice < openPrice)

    def getPercentChangeNDaysAgo(self, ticker, days):
        dayClose = self.data[ticker]['Close'][-days-1]
        dayBeforeClose = self.data[ticker]['Close'][-days-2]
        return ((dayClose-dayBeforeClose)/dayBeforeClose) * 100

    def getAverageVolume(self, ticker):
        return np.mean(self.data[ticker]["Volume"])

    def getVolumeNDaysAgo(self, ticker, days):
        return self.data[ticker]['Volume'][-days-1]

    def getOpeningPriceNDaysAgo(self, ticker, days):
        return self.data[ticker]['Open'][-days-1]

    def getClosingPriceNDaysAgo(self, ticker, days):
        return self.data[ticker]['Close'][-days-1]

    def getHighPriceNDaysAgo(self, ticker, days):
        return self.data[ticker]['High'][-days-1]

    def getLowPriceNDaysAgo(self, ticker, days):
        return self.data[ticker]['Low'][-days-1]

    def insertResult(self, pattern, ticker, data):
        try:
            self.results[pattern][ticker] = data
        except:
            self.results[pattern] = {}
            self.results[pattern][ticker] = data

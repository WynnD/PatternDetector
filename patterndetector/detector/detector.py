from abc import ABC, abstractmethod
from patterndetector.data import Data
from patterndetector.result import Results

class Detector(ABC):
    def __init__(self, data: Data):
        super().__init__()
        self.data = data

    @property
    @abstractmethod
    def name(self):
        pass

    def detect(self, ticker, relativeVolThreshold=1.5, volumeThreshold=200000):

        percentChangeYesterday = self.data.getPercentChangeNDaysAgo(ticker, days=0)

        patternDetected = self.isPattern(ticker)

        if patternDetected:
            avgVolume = self.data.getAverageVolume(ticker)
            volume = self.data.getVolumeNDaysAgo(ticker, 0)
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
        else: 
            return False

    @abstractmethod
    def isPattern(self, ticker):
        pass

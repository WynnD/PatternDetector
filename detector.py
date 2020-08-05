import numpy as np
import datetime
from datetime import date
import dateutil.relativedelta
import datetime
from time import time
import yfinance as yf
from tqdm import tqdm
import sys
import os

from stocklist import NasdaqController

class OutsideDayDetector:
    def __init__(self, patterns):
        super().__init__()
        self.patterns = patterns
        self.data = {}
        self.results = {}

        StocksController = NasdaqController(True)
        self.tickers = StocksController.getList()

    ''' for stock in list of stocks, get trading range (open to close) for two days ago and one day ago. 
            if range on day T-1 surrounds day T-2 and volume is < 2 rel vol print the ticker along with trading range and vol vs relative vol.

        functions:
            getTradingRange(daysAgo) returns dict or tuple (open, close)
            isBullish(range) returns whether the trading range is bullish (positive)
            getRelativeVolume(numDays) returns the relative volume for the range given

    '''

    def detectOutsideDay(self, ticker, relativeVolThreshold=2, volumeThreshold=200000):

        percentChangeYesterday = self.getPercentChangeNDaysAgo(ticker, days=0)

        outsideDay = self.isOutsideDay(ticker)

        if outsideDay:
            avgVolume = self.getAverageVolume(ticker)
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

    def detectEngulfingCandles(self, ticker, relativeVolThreshold=2, volumeThreshold=200000):
        percentChangeYesterday = self.getPercentChangeNDaysAgo(ticker, days=0)

        isEngulfingCandle = self.isEngulfingCandle(ticker)

        if isEngulfingCandle:
            avgVolume = self.getAverageVolume(ticker)
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

    def isEngulfingCandle(self, ticker):
        openPrice = self.getOpeningPriceNDaysAgo(ticker, days=0)
        openPrice2 = self.getOpeningPriceNDaysAgo(ticker, days=1)
        closePrice = self.getClosingPriceNDaysAgo(ticker, days=0)
        closePrice2 = self.getClosingPriceNDaysAgo(ticker, days=1)
        return (closePrice > openPrice2 and openPrice < closePrice2 and openPrice2 > closePrice2 and openPrice < closePrice) or (openPrice > closePrice2 and closePrice < openPrice2 and closePrice2 > openPrice2 and closePrice < openPrice)

    def isOutsideDay(self, ticker):
        openPrice = self.getOpeningPriceNDaysAgo(ticker, days=0)
        closePrice = self.getClosingPriceNDaysAgo(ticker, days=0)
        lowPrice = self.getLowPriceNDaysAgo(ticker, days=0)
        highPrice = self.getHighPriceNDaysAgo(ticker, days=0)

        closePrice2 = self.getClosingPriceNDaysAgo(ticker, days=1)
        openPrice2 = self.getOpeningPriceNDaysAgo(ticker, days=1)
        lowPrice2 = self.getLowPriceNDaysAgo(ticker, days=1)
        highPrice2 = self.getHighPriceNDaysAgo(ticker, days=1)

        return (closePrice > openPrice2 and openPrice < closePrice2 and openPrice2 > closePrice2 and openPrice < closePrice) or (openPrice > closePrice2 and closePrice < openPrice2 and closePrice2 > openPrice2 and closePrice < openPrice) and lowPrice < lowPrice2 and highPrice > highPrice2

    def isPositiveDay(self, openPrice, closePrice):
        return openPrice < closePrice

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

    def getDataDetectAndPrint(self):
        print('Getting all ticker data')
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=4)
        if self.marketsAreClosed():
            currentDate = currentDate + dateutil.relativedelta.relativedelta(days=1)
        num_analyzed = 0
        for ticker in tqdm(self.tickers):
            sys.stdout = open(os.devnull, "w")
            data = yf.download(ticker, pastDate, currentDate)
            sys.stdout = sys.__stdout__
            num_analyzed += 1
            if not data.empty and len(data) > 1:
                self.data[ticker] = data
                outsideDayData = self.detectOutsideDay(ticker)
                engulfingCandleData = self.detectEngulfingCandles(ticker)
                if outsideDayData:
                    self.insertResult('Outside Day', ticker, outsideDayData)
                elif engulfingCandleData:
                    self.insertResult('Engulfing Candle', ticker, engulfingCandleData)
        
        self.printAllData()

    def marketsAreClosed(self):
        now = datetime.datetime.now()
        # monday is 0 sunday is 6 
        day = now.weekday()
        hour = now.hour
        minute = now.minute
        if day > 4:
            return True
        elif hour < 8 or (hour == 8 and minute < 30) or hour > 14: # is earlier than 8:30am or is later than 3pm
            return True
        else:
            return False

    def insertResult(self, pattern, ticker, data):
        try:
            self.results[pattern][ticker] = data
        except:
            self.results[pattern] = {}
            self.results[pattern][ticker] = data

    def detectPatterns(self):
        self.results = {}
        for ticker in self.data:
            for pattern in self.patterns:
                if pattern == 'outsideday':
                    outsideDayData = self.detectOutsideDay(ticker)
                    if outsideDayData:
                        self.results[pattern][ticker] = outsideDayData
                else:
                    print("Unknown pattern")


    def getData(self, months=5):
        print('Getting all ticker data')
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=4)
        for ticker in tqdm(self.tickers):
            sys.stdout = open(os.devnull, "w")
            try:
                data = yf.download(ticker, pastDate, currentDate)
                sys.stdout = sys.__stdout__
                if not data.empty:
                    self.data[ticker] = data
            except:
                print(f"Could not download data for ticker '{ticker}'")

    def printData(self, data):
        print(f"""Ticker: {data['ticker']}
Change: { (data['percent_change']):.2f}%
Volume: {data['volume']}
RelativeVol: {data['relative_vol']:.2f}
""")

    def printAllData(self):
        for pattern in self.results:
            print(f"\n##### Tickers matching '{pattern}' pattern #####\n")
            for ticker in self.results[pattern]:
                data = self.results[pattern][ticker]
                self.printData(data)

    def main(self):
        self.getDataDetectAndPrint()
        # self.getData()
        # currentDate = datetime.datetime.strptime(
        #     date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        # startTime = time()
        # self.detectPatterns()
        # self.printData()


if __name__ == "__main__":
    patterns = ['outsideday'] # in future, get patterns from command line
    OutsideDayDetector(patterns).main()
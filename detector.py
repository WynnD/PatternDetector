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
from db import DetectorDatabase

class OutsideDayDetector:
    def __init__(self, patterns):
        super().__init__()
        self.patterns = patterns
        self.data = {}
        self.output = {}

        self.db = DetectorDatabase()
        StocksController = NasdaqController(self.db)
        self.tickers = StocksController.getList()

    ''' for stock in list of stocks, get trading range (open to close) for two days ago and one day ago. 
            if range on day T-1 surrounds day T-2 and volume is < 2 rel vol print the ticker along with trading range and vol vs relative vol.

        functions:
            getTradingRange(daysAgo) returns dict or tuple (open, close)
            isBullish(range) returns whether the trading range is bullish (positive)
            getRelativeVolume(numDays) returns the relative volume for the range given

    '''

    def detectOutsideDay(self, ticker, relativeVolThreshold=2):
        closePrice2DaysAgo = self.getClosingPriceNDaysAgo(ticker, days=1)
        closePriceYesterday = self.getClosingPriceNDaysAgo(ticker, days=0)
        openPrice2DaysAgo = self.getOpeningPriceNDaysAgo(ticker, days=1)
        openPriceYesterday = self.getOpeningPriceNDaysAgo(ticker, days=0)

        percentChangeYesterday = self.getPercentChangeNDaysAgo(ticker, days=0)

        outsideDay = self.isOutsideDay(openPriceYesterday, closePriceYesterday, openPrice2DaysAgo, closePrice2DaysAgo)

        if outsideDay:
            avgVolume = self.getAverageVolume(ticker)
            volume = self.getVolumeNDaysAgo(ticker, 0)
            relativeVol = volume / avgVolume
            if relativeVol > relativeVolThreshold:
                return {
                    'ticker': ticker,
                    'percent_change': percentChangeYesterday,
                    'volume': volume,
                    'relative_vol': relativeVol
                }
        else: 
            return False

    def isOutsideDay(self, openPrice, closePrice, openPrice2, closePrice2):
        return (closePrice > openPrice2 and openPrice < closePrice2 and openPrice2 > closePrice2 and openPrice < closePrice) or (openPrice > closePrice2 and closePrice < openPrice2 and closePrice2 > openPrice2 and closePrice < openPrice)

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

    def getDataDetectAndPrint(self):
        print('Getting all ticker data')
        currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        pastDate = currentDate - dateutil.relativedelta.relativedelta(months=4)
        num_analyzed = 0
        for ticker in self.tickers:
            self.
            if not data.empty:
                self.db.insertTickerData(ticker, data)
                outsideDayData = self.detectOutsideDay(ticker)
                if outsideDayData:
                    self.printData(outsideDayData)
            except:
                continue

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
                    self.db.insertTickerData(ticker, data)
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
            print(f"Tickers matching '{pattern}' pattern")
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
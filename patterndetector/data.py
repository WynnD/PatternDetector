import numpy as np
import sys
import os
from patterndetector.stocklist import StockList
from tqdm import tqdm
import asyncio
import yfinance as yf
from time import sleep
from concurrent.futures import ThreadPoolExecutor
from patterndetector.helpers import isMarketClosed

class Data:
    def __init__(self):
        self.data = {}
        self.tickers = StockList().tickers

    async def pullData(self):
        print('Getting all ticker data')
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=50)
        futures = []
        for ticker in self.tickers:
            futures.append(
                loop.run_in_executor(executor, self.pullTickerData, ticker))
        [await f for f in tqdm(asyncio.as_completed(futures), total=len(futures))]

    def pullTickerData(self, ticker):
        data = None
        if '$' in ticker or '.' in ticker:
            return
        try:
            delay = 1
            sys.stdout = open(os.devnull, "w")
            data = yf.Ticker(ticker).history(period="4mo")
            while data.empty and delay < 16:
                sleep(delay)
                delay *= 2
                data = yf.Ticker(ticker).history(period="4mo")
            sys.stdout = sys.__stdout__
            if not data.empty and len(data) > 1:
                if not isMarketClosed():
                    data = data[:-1]
                self.data[ticker] = data
        except:
            pass

    def getData(self, ticker):
        return self.data[ticker]
    
    def getAllData(self):
        return self.data

    def getTickers(self):
        return self.tickers

    def addData(self, ticker, data):
        self.data[ticker] = data

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

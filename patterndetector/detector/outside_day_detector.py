import numpy as np
import datetime
from datetime import date
import dateutil.relativedelta
import datetime
from time import time, sleep
import yfinance as yf
from tqdm import tqdm
import sys
import os
import argparse
from email.mime.text import MIMEText
import smtplib
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .detector import Detector
from stocklist import NasdaqController
from patterndetector.data.data import Data


COMMASPACE = ', '

class EngulfingCandleDetector(Detector):
    def __init__(self, data: Data):
        super().__init__()
        self.data = data

    def detectOutsideDay(self, ticker, relativeVolThreshold=2, volumeThreshold=200000):

        percentChangeYesterday = self.data.getPercentChangeNDaysAgo(ticker, days=0)

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
        percentChangeYesterday = self.data.getPercentChangeNDaysAgo(ticker, days=0)
        isEngulfingCandle = self.data.isEngulfingCandle(ticker)
        
        if isEngulfingCandle:
            try:
                avgVolume = self.data.getAverageVolume(ticker)
            except:
                return False
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

    def isPattern(self, ticker):
        openPrice = self.data.getOpeningPriceNDaysAgo(ticker, days=0)
        openPrice2 = self.data.getOpeningPriceNDaysAgo(ticker, days=1)
        closePrice = self.data.getClosingPriceNDaysAgo(ticker, days=0)
        closePrice2 = self.data.getClosingPriceNDaysAgo(ticker, days=1)
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

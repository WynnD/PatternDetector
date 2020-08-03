from ftplib import FTP
import sqlite3
import yfinance as yf
import os
import sys
import errno
from tqdm import tqdm
from datetime import date
import datetime
import dateutil.relativedelta

from db import DetectorDatabase


class NasdaqController:

    def __init__(self, db, updateTickers=True, useCache=True, months=4):

        self.db = db
        self.months = months
        self.useCache = useCache
        self.tickers = []
        self.filenames = {
            "otherlisted": "data/otherlisted.txt",
            "nasdaqlisted": "data/nasdaqlisted.txt"
        }

        self.currentDate = datetime.datetime.strptime(
            date.today().strftime("%Y-%m-%d"), "%Y-%m-%d")
        self.pastDate = self.currentDate - dateutil.relativedelta.relativedelta(months)

        # Update lists only if update = True
        if updateTickers == True:
            self.db.clearData()
            self.refreshTickers()
            self.refreshPriceData()
        else:
            self.tickers = self.db.selectAllTickers()

    def getTickers(self):
        return self.tickers

    def refreshTickers(self):
        self.tickers = []

        self.ftp = FTP("ftp.nasdaqtrader.com")
        self.ftp.login()
        self.ftp.cwd("SymbolDirectory")

        for filename, filepath in self.filenames.items():
            if not os.path.exists(os.path.dirname(filepath)):
                try:
                    os.makedirs(os.path.dirname(filepath))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            self.ftp.retrbinary("RETR " + filename +
                                ".txt", open(filepath, 'wb').write)

        for filename, filepath in self.filenames.items():
            print(f'Reading stock tickers in file: {filename}')
            with open(filepath, "r") as file_reader:
                for i, line in tqdm(enumerate(file_reader, 0)):
                    if i == 0:
                        continue

                    line = line.strip().split("|")

                    if line[0] == "" or line[1] == "":
                        continue

                    # add tickers here
                    self.db.insertTicker(line[0])
                    self.tickers.append(line[0])
            self.db.commitChanges()

    def refreshPriceData(self):
        print('Refreshing all ticker data')
        # if database doesn't have data to a certain date, find newest date for that stock and then retrieve
        for ticker in self.tickers:
            self.refreshTickerData(ticker)

    def refreshTickerData(self, ticker):
        newestDbDate = self.db.getMostRecentDate(ticker)
        fromDate = self.pastDate
        print(newestDbDate)
        if self.useCache and newestDbDate < self.currentDate: # if db doesn't hold data as far back as we want, retrieve data from newestDbDate <-> toDate
            fromDate = newestDbDate

        data = self.getDataFromApi(ticker, fromDate)

        if data:
            self.db.insertTickerData(ticker, data)

    def getDataFromApi(self, ticker, fromDate):
        sys.stdout = open(os.devnull, "w")
        try:
            data = yf.download(ticker, fromDate, self.currentDate)
            sys.stdout = sys.__stdout__
            if not data.empty:
                return data
            else:
                return False
        except:
            print(f"Could not download data for ticker '{ticker}'")
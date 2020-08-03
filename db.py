import sqlite3
import numpy as np

class DetectorDatabase:
    def __init__(self):
        super().__init__()
        self.connection = sqlite3.connect('pattern_detector.db')
        self.db_cursor = self.connection.cursor()

        self.db_cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS tickers (
                ticker  TEXT            PRIMARY KEY
            );''')
        
        self.db_cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS datapoints (
                ticker      INTEGER NOT NULL,
                date        TEXT NOT NULL,
                high        REAL NOT NULL,
                low         REAL NOT NULL,
                open        REAL NOT NULL,
                close       REAL NOT NULL
            );''')

    def insertTicker(self, ticker):
        self.db_cursor.execute(
        f'''
        INSERT OR REPLACE INTO tickers(ticker)
        VALUES ('{ticker}');
        ''')

    def selectAllTickers(self):
        tickers = self.db_cursor.execute(f'SELECT * FROM tickers')
        return map(lambda x: x[0], tickers)

    def insertTickerData(self, ticker, data):
        for index in data.index:
            self.insertDataRow(ticker, data, index)
        
        self.connection.commit()

    def insertDataRow(self, ticker, data, index):
        date = index.strftime('%Y-%m-%d 00:00:00.000')
        high = data['High'][index]
        low = data['Low'][index]
        close = data['Close'][index]
        open_price = data['Open'][index]
        self.db_cursor.execute(
            f'''
            INSERT OR IGNORE INTO datapoints (ticker, date, high, low, open, close)
            VALUES ('{ticker}','{date}', {high}, {low}, {open_price}, {close});
            ''')
    
    def getTickerData(self, ticker, dateFrom, dateTo):
        self.db_cursor.execute(
            '''
            SELECT * FROM datapoints WHERE ####datefrom dateto###
            '''
        )

    def getMostRecentDate(self, ticker):
        date = self.db_cursor.execute(f'SELECT date FROM datapoints WHERE ticker = "{ticker}" ORDER BY date DESC LIMIT 1);')
        if date:
            print(date)
        else:
            return False

    def getOldestDate(self, ticker):
        date = self.db_cursor.execute(f'SELECT date FROM datapoints WHERE ticker = "{ticker}" ORDER BY date ASC LIMIT 1);')
        if date:
            print(date)
        else:
            return False

    def clearData(self):
        self.db_cursor.execute('DROP TABLE IF EXISTS datapoints;')
        self.db_cursor.execute('''
            CREATE TABLE datapoints (
                ticker      INTEGER,
                date        TEXT,
                high        REAL NOT NULL,
                low         REAL NOT NULL,
                open        REAL NOT NULL,
                close       REAL NOT NULL,
                PRIMARY KEY (ticker, date)
            );'''
        )
        self.connection.commit()
    
    def commitChanges(self):
        self.connection.commit()
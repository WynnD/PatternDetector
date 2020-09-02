import os
import sys
import asyncio
from tqdm import tqdm
from argparse import ArgumentParser
from datetime import datetime

from patterndetector.detector.engulfing_candle_detector import EngulfingCandleDetector
from patterndetector.detector.outside_day_detector import OutsideDayDetector
from patterndetector.result import Results
from patterndetector.data import Data
from patterndetector.email import EmailGenerator

class PatternDetector:
    def __init__(self):
        super().__init__()
        self.results = Results()
        self.data = Data()
        self.detectors = [EngulfingCandleDetector(self.data), OutsideDayDetector(self.data)]

        parser = ArgumentParser()
        parser.add_argument('from_email', help='email address to send from')
        parser.add_argument('to_email', nargs='*', help='email address to send to')
        parser.add_argument('--patterns', nargs='*', help='patterns to analyze')
        args = parser.parse_args()
        self.to_email = args.to_email
        self.from_email = args.from_email
        if args.patterns:
            self.patterns = args.patterns
        else:
            self.patterns = ['outsideday']

    def getDataDetectAndPrint(self):
        num_analyzed = num_failed = 0
        print("Analyzing all tickers")
        num_failed = 0
        for ticker in tqdm(self.data.getTickers()):
            try:
                self.detectPatterns(ticker)
                num_analyzed += 1
            except:
                num_failed += 1
        print(f"{num_analyzed} tickers analyzed with {num_failed} failures")

        self.sendEmail()

    def detectPatterns(self, ticker):
        for Detector in self.detectors:
            data = Detector.detect(ticker)
            if data:
                self.results.addResult(Detector.name, ticker, data)

    def sendEmail(self):
        email = EmailGenerator(self.results)
        email.sendEmail(self.from_email, self.to_email)

    async def main(self):
        start = datetime.now()
        await self.data.pullData()
        self.getDataDetectAndPrint()
        print(f'Runtime (HH:MM:SS.SSSSSS): {datetime.now()-start}')


if __name__ == "__main__":
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(PatternDetector().main())
    loop.close()

class Results:
    def __init__(self):
        self.results = {}

    def getPatternResults(self, pattern):
        return self.results[pattern]

    def getAllResults(self):
        return self.results
    
    def addResult(self, pattern, ticker, data):
        try:
            self.results[pattern][ticker] = data
        except:
            self.results[pattern] = {}
            self.results[pattern][ticker] = data
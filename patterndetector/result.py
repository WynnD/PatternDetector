class Results:
    def __init__(self):
        self.results = {}

    def getPatternResults(self, pattern):
        return self.results[pattern]

    def getAllResults(self):
        return self.results
    
    def addResult(self, ticker, pattern, data):
        self.results[ticker][pattern] = data
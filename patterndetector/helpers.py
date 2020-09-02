from datetime import datetime

def isPositiveDay(openPrice, closePrice):
    return openPrice < closePrice

def isMarketClosed():
    current = datetime.now()
    # monday is 0 sunday is 6 
    day = current.weekday()
    hour = current.hour
    minute = current.minute
    if day > 4: # is weekend
        return True
    elif hour < 8 or (hour == 8 and minute < 30) or hour > 14: # is earlier than 8:30am or is later than 3pm
        return True
    else: # weekday but markets are closed
        return False
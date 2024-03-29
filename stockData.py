import sys, os
import pandas as pd
import pandas_datareader.data as web
import numpy as np
from datetime import datetime, timedelta, date
import calendar


def to_week_day(start, end):
    if start.isoweekday() == 6:
        start += timedelta(days=2)
    elif start.isoweekday() == 7:
        start += timedelta(days=1)
    if end.isoweekday() == 6:
        end += timedelta(days=-1)
    elif end.isoweekday == 7:
        end += timedelta(days=-2)

    return start, end


class StockData():
    def __init__(self):
        self.quote = pd.DataFrame()
        self.pp = 0
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.s1 = 0
        self.s2 = 0
        self.s3 = 0

    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def webQuery(self,symbol, start, end):
        quote = web.DataReader(symbol, 'av-daily-adjusted', start, end, api_key=os.getenv('ALPHAVANTAGE_API_KEY'))
        nameDays=[]
        for s in quote.index:
            s = datetime(int(s[:4]), int(s[5:7]), int(s[8:]))
            nameDays.append(s.strftime("%A"))
        quote.insert(0, 'Day', nameDays)
        return quote

    def movingAverage(self, period):
        self.quote['MAV ' + str(period)]=self.quote['close'].rolling(period).mean()
        # closePrice = self.quote['close']
        # datapointNb = len(closePrice)
        # if datapointNb < period:
        #     print("Not enough data to compute the moving average")
        # else:
        #     mav = [np.nan] * (period-1)
        #     i = 0
        #     while i+period <= datapointNb:
        #         mav.append(np.cumsum(closePrice[i:i+period]))
        #         i+=1
        #     self.quote['MAV ' + str(period)]=mav/period

    def pprs(self):
        close = self.stock['close'][-1]
        high = self.stock['high'][-1]
        low = self.stock['low'][-1]
        self.pp =  (high + low + close)/3
        self.r1 = 2*self.pp  - low
        self.s1 = 2*self.pp - high
        self.r2 = self.pp + high - low
        self.s2 = self.pp - high + low
        self.r3 = high + 2*(self.pp - low)
        self.s3 = low - 2*(high - self.pp)

    def getTickerData(self,symbol, startDate, endDate):
        start = pd.to_datetime(startDate)
        end = pd.to_datetime(endDate)

        start, end = to_week_day(start, end)
        myQuotes = os.listdir('./quotes/')
        filename = symbol + '.csv'
        if filename in myQuotes:
            self.quote = pd.read_csv('./quotes/' + filename, sep=';', index_col=0, parse_dates=True)
            if start - self.quote.index[0] < timedelta(days=0):
                start, end = to_week_day(start, self.quote.index[0] - timedelta(days=1))
                prevData = self.webQuery(symbol,start, end)
                self.quote = prevData.append(self.quote)
            if end - self.quote.index[-1] > timedelta(days=0):
                start, end = to_week_day(self.quote.index[-1], end)
                newData = self.webQuery(symbol, start, end)
                self.quote.append(newData)
        else:
            self.quote = self.webQuery(symbol, start, end)

        self.quote = self.quote.drop_duplicates()


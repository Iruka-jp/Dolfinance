import sys, os
import pandas
import pandas_datareader.data as web
import numpy as np
from datetime import datetime, timedelta, date
import calendar



class StockData():
    def __init__(self):
        self.quote = pandas.DataFrame()
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
        self.quote = web.DataReader(symbol, 'av-daily-adjusted', start, end, api_key=os.getenv('ALPHAVANTAGE_API_KEY'))
        nameDays=[]
        for s in self.quote.index:
            s = datetime(int(s[:4]), int(s[5:7]), int(s[8:]))
            nameDays.append(s.strftime("%A"))
        self.quote.insert(0, 'Day', nameDays)

    def movingAverage(self, period):
        closePrice = self.quote['close']
        datapointNb = len(closePrice)
        if datapointNb < period:
            print("Not enough data to compute the moving average")
        else:
            mav = [np.nan] * (period - 1)
            i = 0
            while i+period < datapointNb:
                mav.append(np.cumsum(closePrice[i:i+period]))
                i+=1
            self.quote['MAV ' + str(period)]=mav
            print(self.quote)

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
        startDate = str(startDate)
        endDate = str(endDate)
        start = datetime(int(startDate[:4]), int(startDate[5:7]), int(startDate[8:10]))
        end = datetime(int(endDate[:4]), int(endDate[5:7]), int(endDate[8:10]))
        if start.isoweekday() == 6:
            start += timedelta(days=2)
        elif start.isoweekday() == 7:
            start += timedelta(days=1)
        if end.isoweekday() == 6:
            end += timedelta(days=-1)
        elif end.isoweekday == 7:
            end += timedelta(days=-2)

        myQuotes = os.listdir('./quotes/')
        filename = symbol + '.csv'
        if filename in myQuotes:
            self.quote = pandas.read_csv('./quotes/' + filename, sep=';', index_col=0, parse_dates=True)
            if start - self.quote.index[0] < timedelta(days=0):
                prevData = self.webQuery(symbol, start, self.quote.index[0] - timedelta(days=1))
                self.quote = prevData.append(self.quote)
            if end - self.quote.index[-1] > timedelta(days=0):
                newData = self.webQuery(symbol, self.quote.index[-1] + timedelta(days=1), end)
                self.quote.append(newData)
        else:
            self.webQuery(symbol, start, end)

        self.quote = self.quote.drop_duplicates()

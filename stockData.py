import sys, os
import pandas
import pandas_datareader.data as web
from datetime import datetime, timedelta, date
import calendar



class StockData():
    def __init__(self):
        self.quote = pandas.DataFrame()

    def daterange(start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def webQuery(self,symbol, start, end):
        self.quote = web.DataReader(symbol, 'yahoo', start, end)
        nameDays=[]
        for s in self.quote.index:
            nameDays.append(s.strftime("%A"))
        self.quote.insert(0, 'Day', nameDays)


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

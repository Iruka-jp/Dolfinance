import sys
import numpy as np
from stockData import StockData

from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtWebEngineWidgets import QWebEngineView

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as po

class TechAnalysis(QtWidgets.QMainWindow):
    def __init__(self):
        super(TechAnalysis, self).__init__()
        self.ui = uic.loadUi('techanalysis.ui', self)
        self.ui.startDateInput.setDate(QtCore.QDate().currentDate().addMonths(-1))
        self.ui.endDateInput.setDate(QtCore.QDate().currentDate().addDays(-1))
        self.stock = StockData()
        self.ui.getData.clicked.connect(self.plotStock)

    def plotStock(self):
        ticker = self.ui.stockTicker.text()
        startDate = self.ui.startDateInput.date().toString('yyyy-MM-dd')
        endDate = self.ui.endDateInput.date().toString('yyyy-MM-dd')
        self.stock.getTickerData(ticker, startDate, endDate)
        self.stock.quote.to_csv(path_or_buf='quotes/'+ ticker +'.csv', sep=';')

        fig = make_subplots(
            rows=2, cols=1,
            row_width=[0.2, 0.8],
            shared_xaxes=True,
            vertical_spacing=0.05,
            specs=[[{"type": "Candlestick"}],
                   [{"type": "Candlestick"}]],
        )

        # fig.add_trace(
        #     go.Candlestick(x=self.stock.quote.index,
        #                    open=self.stock.quote['Open'],
        #                    high=self.stock.quote['High'],
        #                    low=self.stock.quote['Low'],
        #                    close=self.stock.quote['Close'],
        #                    name='Price'),
        #     row=1, col=1
        # )
        fig.add_trace(
            go.Candlestick(x=self.stock.quote.index,
                           open=self.stock.quote['open'],
                           high=self.stock.quote['high'],
                           low=self.stock.quote['low'],
                           close=self.stock.quote['close'],
                           name='Price'),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                x=self.stock.quote.index,
                y=self.stock.quote['volume'],
                name='Volume'
            ),
            row=2, col=1
        )

        fig.update_layout(xaxis_rangeslider_visible=False,
                          title=ticker)

        fn = '/plot.html'
        raw_html = '<html><head><meta charset="utf-8" />'
        raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
        raw_html += '<body>'
        raw_html += po.plot(fig, include_plotlyjs=False, output_type='div', filename=fn, auto_open=False)
        raw_html += '</body></html>'

        # fig_view = QWebEngineView()
        # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
        # for large figures.
        self.ui.plotFrame.setHtml(raw_html)
        self.ui.plotFrame.show()
        self.ui.plotFrame.raise_()

        lay = QtWidgets.QVBoxLayout(self.ui.plotFrame)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.ui.plotFrame)

        #########################
        # FOR TEST REMOVE AFTER #
        #########################
        #self.stock.movingAverage(50)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = TechAnalysis()
    window.show()
    sys.exit(app.exec_())
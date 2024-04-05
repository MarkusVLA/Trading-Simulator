from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QLinearGradient, QBrush, QColor, QPen
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
import pandas as pd
import numpy as np
from candle_stick import CandlestickItem
from PyQt5.QtGui import QFont


class MarketPlotCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
    
    def initUI(self):
        # Main layout setup
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        pg.setConfigOption('background', '#383838')
        pg.setConfigOption('foreground', 'w')  
        self.font = QFont('Segoe UI', 20)
        self.plotWidget = self.createPlotWidget(DateAxisItem(orientation='bottom'))
        self.volumePlotWidget = self.createPlotWidget(DateAxisItem(orientation='bottom'), max_height=300)
        self.capitalPlotWidget = self.createPlotWidget(DateAxisItem(orientation='bottom'), max_height=300)

        self.plotWidget.setXLink(self.volumePlotWidget)
        self.volumePlotWidget.setXLink(self.capitalPlotWidget)


    def createPlotWidget(self, axis, max_height=None):
        plot_widget = pg.PlotWidget(axisItems={'bottom': axis})
        plot_widget.showGrid(x=True, y=True, alpha=0.1)
        plot_widget.getPlotItem().getAxis('left').tickFont = self.font
        plot_widget.getPlotItem().getAxis('bottom').tickFont = self.font
        plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if max_height:
            plot_widget.setMaximumHeight(max_height)
        self.mainLayout.addWidget(plot_widget)
        return plot_widget

    def plot(self, df):
        self.reset()

        time = pd.to_datetime(df.index).astype(np.int64) // 10**9
        
        candlestickData = []
        
        for t, row in zip(time, df.itertuples()):
            candlestickData.append((t, row.Open, row.Close, row.Low, row.High))
        candlestickItem = CandlestickItem(candlestickData)
        self.plotWidget.addItem(candlestickItem)
        
        volumeBars = pg.BarGraphItem(x=time, height=df['Volume'].values, width=0.8 * (time[1] - time[0]), brush='b')
        self.volumePlotWidget.addItem(volumeBars)

        for signal, symbol, color in [(1, 't1', 'b'), (2, 't', 'r')]:
            signals = df[df['Signal'] == signal]
            signalTime = pd.to_datetime(signals.index).astype(np.int64) // 10**9
            signalPrices = signals['Close'].values
            offset = np.ones_like(signalPrices) * (0.2 if signal == 1 else -0.2)
            self.plotWidget.plot(signalTime, signalPrices + offset, pen=None, symbol=symbol, symbolSize=10, symbolBrush=color)

        

        self.capitalPlotWidget.plot(time, df['Capital'].astype(np.float64).values, pen='y')






    def reset(self):
        self.plotWidget.clear()
        self.volumePlotWidget.clear()
        self.capitalPlotWidget.clear()

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mplfinance as mpf



class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=8, height=8, dpi=100, plot_type='Close'):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.plot_type = plot_type 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def plot(self, df):
        df = df.tail(300)
        self.axes.clear()
        if self.plot_type == 'Close':
            self.figure.clear()
            ax1 = self.figure.add_subplot(111)
            mpf.plot(df,
                     type='candle', 
                     style='yahoo',
                     ax=ax1, 
                     show_nontrading=False, 
                     mav=(15), 
                     volume=False)

        elif self.plot_type == 'Capital':
            self.axes.plot(df.index, df['Capital'], label='Capital', color='darkblue', linewidth=2, linestyle='-', alpha=0.8)
            buys = df[df['Signal'] == 1]
            sells = df[df['Signal'] == 2]
            self.axes.scatter(buys.index, df.loc[buys.index, 'Capital'], color='green', label='Buy', marker='^', s=50, edgecolor='black', alpha=0.7)
            self.axes.scatter(sells.index, df.loc[sells.index, 'Capital'], color='red', label='Sell', marker='v', s=50, edgecolor='black', alpha=0.7)
            self.axes.set_ylabel('Capital')
        self.draw()
import sys
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QSlider
import matplotlib.pyplot as plt
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from data_feeder import DataFeeder
from trader import Trader
import pandas as pd
import mplfinance as mpf


plt.rcParams.update({
    'figure.facecolor': '#313231',  
    'axes.facecolor': '#313231', 
    'axes.edgecolor': 'white',
    'axes.labelcolor': 'white',
    'axes.grid': True,  
    'grid.alpha': 0.3,  
    'grid.color': "white",  
    'grid.linestyle': '--',  
    'grid.linewidth': 0.6,  
    'text.color': 'white',
    'xtick.color': 'white',
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'ytick.color': 'white',
    'figure.titleweight': 'bold',
    'figure.titlesize': 'large',
    'legend.edgecolor': 'white',
    'legend.facecolor': '#313231',
    'legend.framealpha': 0.6,
    'legend.fontsize': 'medium',
    'lines.linewidth': 2,
    'lines.markersize': 7,
    'scatter.edgecolors': 'white',
})


class StreamRedirect:
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        self.widget.append(text)

    def flush(self):
        pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Live Stock Data')
        self.setGeometry(800, 100, 1200, 1200)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        main_layout = QHBoxLayout(self.main_widget)

        # Left side layout for inputs and plots
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Right side layout for text window and controls
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)

        # Input fields and load data button
        self.symbol_input = QLineEdit("AAPL", self)
        self.start_input = QLineEdit("2024-03-20", self)
        self.end_input = QLineEdit("2024-03-21", self)
        self.time_frame_input = QComboBox(self)
        self.time_frame_input.addItems(["1m", "5m", "15m", "30m", "1h", "1d"])
        self.load_button = QPushButton('Load Data', self)
        self.load_button.clicked.connect(self.load_data)

        # Add widgets to left side layout
        left_layout.addWidget(QLabel("Symbol:"))
        left_layout.addWidget(self.symbol_input)
        left_layout.addWidget(QLabel("Start Date (YYYY-MM-DD):"))
        left_layout.addWidget(self.start_input)
        left_layout.addWidget(QLabel("End Date (YYYY-MM-DD):"))
        left_layout.addWidget(self.end_input)
        left_layout.addWidget(QLabel("Time Frame:"))
        left_layout.addWidget(self.time_frame_input)
        left_layout.addWidget(self.load_button)

        # Simulation speed slider
        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMaximumWidth(200)  # Set a maximum width to control the slider's length
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(1000)
        self.speed_slider.setValue(100)
        left_layout.addWidget(QLabel("Simulation Speed:"))
        left_layout.addWidget(self.speed_slider)

        # Plot canvases
        self.canvas_close = PlotCanvas(self, width=8, height=9, plot_type='Close')
        left_layout.addWidget(self.canvas_close)
        self.canvas_capital = PlotCanvas(self, width=8, height=9, plot_type='Capital')
        left_layout.addWidget(self.canvas_capital)

        # Info label and start simulation button on the left side
        self.info_label = QLabel("Holding: \nTotal Value: ", self)
        left_layout.addWidget(self.info_label)
        self.start_simulation_button = QPushButton('Start Simulation', self)
        self.start_simulation_button.clicked.connect(self.start_simulation)
        self.start_simulation_button.setEnabled(False)
        left_layout.addWidget(self.start_simulation_button)

        # Text window for displaying information on the right side
        self.text_window = QTextEdit(self)
        self.text_window.setReadOnly(True)
        self.text_window.setMaximumWidth(400)  # Make the text window a bit smaller
        right_layout.addWidget(self.text_window)

        # Redirect stdout to text window
        sys.stdout = StreamRedirect(self.text_window)

        # Initialize data feeder and trader manager
        self.data_feeder = None
        self.manager = None

        # Connect the simulation speed slider
        self.speed_slider.valueChanged.connect(self.adjust_speed)

        # Timer for updating simulation data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

    def load_data(self):
        try:
            # Fetching the symbol and other inputs only when the "Load Data" button is pressed
            symbol = self.symbol_input.text()
            start_date = self.start_input.text()
            end_date = self.end_input.text()
            time_frame = self.time_frame_input.currentText()

            # Using the fetched inputs to load data
            self.data_feeder = DataFeeder(symbol, start_date, end_date, time_frame)
            self.manager = Trader(initial_capital=1000.0)
            self.manager.addStock(symbol)

            # Enabling the "Start Simulation" button after successfully loading data
            self.start_simulation_button.setEnabled(True)
            self.text_window.append("Data loaded successfully for symbol: {}".format(symbol))
        except Exception as e:
            self.text_window.append("Error loading data: {}".format(str(e)))


    def update_data(self):
        try:
            df = self.traderCycle()
            if df is not False:
                self.canvas_close.plot(df)
                self.canvas_capital.plot(df)
                total_value = self.manager.calculateTotalValue()
                holding = self.manager.getHolding(self.symbol_input.text())
                self.info_label.setText(f"Holding: {holding}\nTotal Value: ${total_value:,.2f}")
        except Exception as e:
            self.text_window.append("Error updating data: {}".format(str(e)))



    def traderCycle(self):
        row = self.data_feeder.getNextRow()
        if row is not None:
            self.manager.distributeData(
                stock=self.symbol_input.text(), 
                Datetime=row.name,
                Open=row['Open'],
                High=row['High'],
                Low=row['Low'],
                Close=row['Close'],  
                Volume=row['Volume'],  
            )
        else:
            return False
        dataF = self.manager.getLiveDataFrame().getFrame()
        self.manager.saveActions()  # Exports to JSON
        return dataF
    

    def start_simulation(self):
        self.timer.setInterval(self.speed_slider.value())
        self.timer.start()
        self.start_simulation_button.setEnabled(False)

    def adjust_speed(self, value):
        max_value = self.speed_slider.maximum()
        interval = max_value - value + 1  # Adding 1 to avoid division by zero
        self.timer.setInterval(interval)
        if self.timer.isActive():
            self.timer.start(interval)


class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=8, height=6, dpi=100, plot_type='Close'):
        fig = Figure(figsize=(width, height), dpi=dpi)  # Set facecolor to black

        self.axes = fig.add_subplot(111)
        self.plot_type = plot_type 
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

    def plot(self, df):

        self.axes.clear()
        if self.plot_type == 'Close':
            self.figure.clear()
            ax1 = self.figure.add_subplot(111)
            mpf.plot(df,
                        type='candle', 
                        style='charles',
                        ax=ax1, 
                        show_nontrading=False, 
                        mav=(3,6,9), 
                        volume=False)


        elif self.plot_type == 'Capital':

            self.axes.plot(df.index, df['Capital'], label='Capital', color='r')            
            self.axes.set_ylabel('Capital', color='w')  

        self.axes.set_title(f'{self.plot_type} Over Time', color='white')
        self.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
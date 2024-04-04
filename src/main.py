import sys
import matplotlib.dates as mdates
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QSlider
from PyQt5.QtCore import QTimer, Qt
from data_feeder import DataFeeder
from trader import Trader
from setup import *
from plot_canvas import MarketPlotCanvas



class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Trader simulator')
        self.setGeometry(800, 100, 1200, 900)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        main_layout = QHBoxLayout(self.main_widget)

        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)
        self.symbol_input = QLineEdit("AAPL", self)
        self.start_capital = QLineEdit("1000", self)
        self.start_input = QLineEdit("2024-03-20", self)
        self.end_input = QLineEdit("2024-03-21", self)
        self.time_frame_input = QComboBox(self)
        self.time_frame_input.addItems(["1m", "5m", "15m", "30m", "1h", "1d"])
        self.load_button = QPushButton('Start', self)
        self.load_button.clicked.connect(self.load_data)

        left_layout.addWidget(QLabel("Symbol:"))
        left_layout.addWidget(self.symbol_input)
        left_layout.addWidget(QLabel("Starting capital:"))
        left_layout.addWidget(self.start_capital)

        left_layout.addWidget(QLabel("Start Date (YYYY-MM-DD):"))
        left_layout.addWidget(self.start_input)
        left_layout.addWidget(QLabel("End Date (YYYY-MM-DD):"))
        left_layout.addWidget(self.end_input)
        left_layout.addWidget(QLabel("Time Frame:"))
        left_layout.addWidget(self.time_frame_input)
        left_layout.addWidget(self.load_button)

        self.speed_slider = QSlider(Qt.Horizontal, self)
        self.speed_slider.setMaximumWidth(200)  
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(1000)
        self.speed_slider.setValue(100)
        left_layout.addWidget(QLabel("Simulation Speed:"))
        left_layout.addWidget(self.speed_slider)

        self.market_plot = MarketPlotCanvas(self)
        left_layout.addWidget(self.market_plot)

        self.info_label = QLabel("Holding: \nTotal Value: ", self)
        left_layout.addWidget(self.info_label)

        self.text_window = QTextEdit(self)
        self.text_window.setReadOnly(True)
        self.text_window.setMaximumWidth(400)  # Make the text window a bit smaller
        right_layout.addWidget(self.text_window)
        self.data_feeder = None
        self.manager = None

        self.speed_slider.valueChanged.connect(self.adjust_speed)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

    def load_data(self):
        try:
            self.market_plot.reset()
            symbol = self.symbol_input.text()
            start_date = self.start_input.text()
            end_date = self.end_input.text()
            time_frame = self.time_frame_input.currentText()
            starting_capital = float(self.start_capital.text())

            self.data_feeder = DataFeeder(symbol, start_date, end_date, time_frame)
            if self.data_feeder.data.empty:
                self.text_window.append(f"Error loading data for {symbol}")
                return

            self.manager = Trader(initial_capital=starting_capital)
            self.manager.addStock(symbol)


            self.text_window.append("Data loaded successfully for symbol: {}".format(symbol))

            self.start_simulation()
            
        except Exception as e:
            print("Error loading data: {}".format(str(e)))


    def update_data(self):
        try:
            df = self.traderCycle()
            if df is not False:
                self.market_plot.plot(df)
                total_value = self.manager.calculateTotalValue()
                holding = self.manager.getHolding(self.symbol_input.text())
                self.info_label.setText(f"Holding: {holding}\nTotal Value: ${total_value:,.2f}")
        except Exception as e:
            print("Error updating data: {}".format(str(e)))



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
            self.manager.saveActions()
            return False
        
        dataF = self.manager.getLiveDataFrame().getFrame()
        return dataF
    

    def start_simulation(self):
        self.timer.setInterval(self.speed_slider.value())
        self.timer.start()

    def adjust_speed(self, value):
        max_value = self.speed_slider.maximum()
        interval = max_value - value  
        self.timer.setInterval(interval)
        if self.timer.isActive():
            self.timer.start(interval)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
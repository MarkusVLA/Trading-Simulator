from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QSlider
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
from data_feeder import DataFeeder
from trader import Trader
from plot_canvas import MarketPlotCanvas

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Trader Simulator')
        self.setGeometry(800, 100, 1200, 900)
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        main_layout = QHBoxLayout(self.main_widget)
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)
        
        self.symbol_input = QLineEdit("AAPL,GOOGL", self)
        self.start_capital = QLineEdit("1000", self)
        self.start_input = QLineEdit("2024-03-20", self)
        self.end_input = QLineEdit("2024-03-21", self)
        self.time_frame_input = QComboBox(self)
        self.time_frame_input.addItems(["1m", "5m", "15m", "30m", "1h", "1d"])
        self.load_button = QPushButton('Start', self)
        self.load_button.clicked.connect(self.load_data)

        left_layout.addWidget(QLabel("Symbols:"))
        left_layout.addWidget(self.symbol_input)
        left_layout.addWidget(QLabel("Starting Capital:"))
        left_layout.addWidget(self.start_capital)
        left_layout.addWidget(QLabel("Start Date (YYYY-MM-DD):"))
        left_layout.addWidget(self.start_input)
        left_layout.addWidget(QLabel("End Date (YYYY-MM-DD):"))
        left_layout.addWidget(self.end_input)
        left_layout.addWidget(QLabel("Time Frame:"))
        left_layout.addWidget(self.time_frame_input)
        left_layout.addWidget(self.load_button)
        main_layout.setStretch(0, 1)  # Give less space to control panel
        main_layout.setStretch(1, 5)  # Give more space to graph
        

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
        font = QFont()
        font.setPointSize(18)
        self.info_label.setFont(font)
        left_layout.addWidget(self.info_label)

        # New stock selection dropdown setup
        self.stock_selection = QComboBox(self)
        left_layout.addWidget(QLabel("Select Stock:"))
        left_layout.addWidget(self.stock_selection)
        self.stock_selection.currentTextChanged.connect(self.on_stock_selection_changed)

        self.text_window = QTextEdit(self)
        self.text_window.setReadOnly(True)
        self.text_window.setMaximumWidth(400)
        right_layout.addWidget(self.text_window)

        self.data_feeders = {}
        self.manager = Trader(initial_capital=float(self.start_capital.text()))

        self.speed_slider.valueChanged.connect(self.adjust_speed)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)


    def load_data(self):
        self.market_plot.reset()
        symbol = []
        symbols = self.symbol_input.text().split(",")
        start_date = self.start_input.text()
        end_date = self.end_input.text()
        time_frame = self.time_frame_input.currentText()

        for symbol in symbols:
            self.manager.addStock(symbol)  # Add stock to Trader
            self.data_feeders[symbol] = DataFeeder(symbol, start_date, end_date, time_frame)
            if self.data_feeders[symbol].data.empty:
                self.text_window.append(f"Error loading data for {symbol}")
                return

        self.text_window.append(f"Data loaded successfully for symbols: {', '.join(symbols)}")
        self.stock_selection.clear()
        self.stock_selection.addItems(symbols) 
        if symbols:
            self.stock_selection.setCurrentIndex(0) 
        self.start_simulation()


    def update_data(self):        
        for symbol, feeder in self.data_feeders.items():
            row = feeder.getNextRow()
            if row is not None:
                self.manager.distributeData(
                    stock=symbol, 
                    Datetime=row.name,
                    Open=row['Open'],
                    High=row['High'],
                    Low=row['Low'],
                    Close=row['Close'],  
                    Volume=row['Volume'],
                )
            # else:
                # self.manager.saveActions()

        self.update_gui_for_stock(self.stock_selection.currentText())


    def update_gui_for_stock(self, symbol):
        if symbol in self.data_feeders: 
            total_value = self.manager.calculateTotalValue()
            holding = self.manager.getHolding(symbol) 
            self.info_label.setText(f"Holding for {symbol}: {holding}           Total Value: ${total_value:,.2f}")
            df = self.manager.getLiveDataFrame(symbol)
        if df.shape[0] >= 2:
                self.market_plot.plot(df, mav=9)

    def on_stock_selection_changed(self):
        selected_symbol = self.stock_selection.currentText()
        if selected_symbol in self.data_feeders:
            self.update_gui_for_stock(selected_symbol)
       

    def start_simulation(self):
        self.timer.setInterval(self.speed_slider.value())
        self.timer.start()

    def adjust_speed(self, value):
        max_value = self.speed_slider.maximum()
        interval = max_value - value
        self.timer.setInterval(interval)

if __name__ == "__main__":
    print("You are running the wrong file. Please run app.py")

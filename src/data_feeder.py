
import pandas as pd
import yfinance as yf


class DataFeeder:
    
    def __init__(self, symbol:str, start:str, end:str, interval:str):
        # Download stock data
        self.symbol = symbol
        self.start_date = start
        self.end_date = end
        self.data = yf.download(self.symbol, start=self.start_date, end=self.end_date, interval=interval)
        self.current_index = 0 

    def getNextRow(self):
        if self.current_index < len(self.data):
            row = self.data.iloc[self.current_index]
            self.current_index += 1
            return row
        else:
            return None

    def reset(self):
        self.current_index = 0 

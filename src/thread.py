import pandas as pd
from random import randint
from frame import TradeFrame
import datetime

class Thread:

    def __init__(self, stock_name:str):
        self.stock_name = stock_name
        self.frame = TradeFrame()

        # Window periods
        self.short_term_window = 12
        self.long_term_window = 26
        self.rsi_period = 14


    def getStockName(self) -> str:
        return self.stock_name
    
    def getTradeFrame(self) -> TradeFrame:
        return self.frame
    
    def getLastInfo(self):
        return self.frame.getLastRow()
    
    def getLastClosePrice(self):
        last_row = self.frame.getLastRow()
        if last_row is not None and not last_row.empty:
            return last_row['Close'].iloc[0]
        else:
            print("No data available to fetch the last close price.")
            return None

    def decideRandom(self):
        return randint(0, 2)

    
    def exportFrame(self):
        self.frame.exportFrame(f"tmp/{self.stock_name}_trade_frame_{datetime.date.today()}.json")
        return True
    
    def loadFrame(self, path:str):
        self.frame.loadFrame(path)
        return True

    def addRowAndDecide(self, newRow, capital: int):

        success = self.frame.addRow(newRow)
        if not success: 
            print("Failed to add new row.")
            return 0
        
        df = self.frame.getFrame()
        decision = self.decideRandom()
        
        last_datetime = df.iloc[-1]['Datetime']
        # Save thread actions to dataframe.
        self.frame.updateActions(last_datetime, decision, capital)        
        return decision
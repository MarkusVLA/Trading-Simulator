import pandas as pd
from random import randint
from frame import TradeFrame
from datetime import datetime
from strategy import *
from random import randint

class Thread:

    def __init__(self, stock_name: str):
        self.stock_name = stock_name
        self.frame = TradeFrame()
        self.time = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")

    def getStockName(self) -> str:
        return self.stock_name
    
    def getTradeFrame(self) -> TradeFrame:
        return self.frame
    
    def getLastInfo(self):
        return self.frame.getLastRow()
    
    def exportFrame(self):
        self.frame.exportFrame(f"tmp/{self.stock_name}_trade_frame_{self.time}.json")
    
    def loadFrame(self, path: str):
        self.frame.loadFrame(path)    
    
    def getLastClosePrice(self):
        last_row = self.frame.getLastRow()
        if last_row is not None and not last_row.empty:
            return last_row['Close'].iloc[0]
        else:
            print("No data available to fetch the last close price.")
            return None

    def updateFrame(self, datetime: str, **kwargs):
        if not self.frame.upsertRow(datetime, **kwargs):
            print("Failed to update or add new row.")
            return False
        return True

    def getSignal(self):
        return applyFourierTransform(self.frame.getFrame())
        # return randint(0,2)
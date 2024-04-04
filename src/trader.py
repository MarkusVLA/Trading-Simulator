from thread import Thread
from random import randint


class Trader:

    def __init__(self, initial_capital:float = 1000.0) -> None:
        self.change = initial_capital
        self.threads = {}  
        self.stocks_owned = {} 

    def addStock(self, stock: str):
        self.threads[stock] = Thread(stock)
        if stock not in self.stocks_owned:
            self.stocks_owned[stock] = 0

    def getActions(self) -> dict:
        trade_frames = {}
        for stock, trader in self.threads.items():
            trade_frames[stock] = trader.getTradeFrame().getFrame()

        return trade_frames
    
    def getLiveDataFrame(self):
        return list(self.threads.values())[0].getTradeFrame()
    
    def saveActions(self):
        for trader in self.threads.values():
            trader.exportFrame()


    def distributeData(self, stock: str, **kwargs):
        if stock in self.threads.keys():
            datetime = kwargs.get('Datetime') 
            if datetime is None:
                print("Datetime is required.")
                return False
            del kwargs['Datetime']

            if not self.threads[stock].updateFrame(datetime, **kwargs):
                print(f"Failed to update frame for stock: {stock}")
                return

            signal = self.threads[stock].getSignal() # Signal from algo
            action = self.actOnSignal(stock, signal) # Action by bot
            self.threads[stock].updateFrame(
                datetime, 
                Signal = action,
                Capital = self.calculateTotalValue(),
                Holding = self.stocks_owned[stock]
            ) 

        else:
            print(f"No trader found for stock: {stock}, unable to distribute data.")


    def actOnSignal(self, stock:str, signal):

        last_close_price = self.threads[stock].getLastClosePrice()
        # shares_to_transact =  int(self.change * 0.80 / last_close_price)
        shares_to_transact = 1
        transaction_cost = last_close_price * shares_to_transact

        if signal == 1 and self.change >= transaction_cost:
            self.change -= transaction_cost
            self.stocks_owned[stock] += shares_to_transact
            return 1
        
        elif signal == 2 and self.stocks_owned[stock] > 0:
            self.change += transaction_cost
            self.stocks_owned[stock] -= shares_to_transact
            return 2
        
        else:
            return 0
        

    def calculateTotalValue(self):
        total_value = self.change
        for stock, quantity in self.stocks_owned.items():
            current_price = self.threads[stock].getLastClosePrice() if stock in self.threads else 0
            total_value += current_price * quantity if current_price else 0
        return total_value
    
    def getHolding(self, symbol:str):
        return self.stocks_owned[symbol]

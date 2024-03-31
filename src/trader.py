from thread import Thread

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
    
    def setCapitalInFrame(self):
        list(self.threads.values())[0].getTradeFrame().se


    def saveActions(self):
        for trader in self.threads.values():
            trader.exportFrame()
    
    def distributeData(self, stock: str, datetime: str, open_price, high_price, low_price, close_price, adj_close_price, volume):
        if stock in self.threads.keys():
            row = [datetime, open_price, high_price, low_price, close_price, adj_close_price, volume]
            signal = self.threads[stock].addRowAndDecide(row, self.calculateTotalValue())
            self.actOnSignal(stock, signal, close_price)
        else:
            print(f"No trader found for stock: {stock}, unable to distribute data.")
        

    def actOnSignal(self, stock: str, signal: int, price: float):

        shares_to_transact = 1
        transaction_cost = price * shares_to_transact

        if signal == 1 and self.change >= transaction_cost:
            self.change -= transaction_cost
            self.stocks_owned[stock] += shares_to_transact
        elif signal == 2 and self.stocks_owned[stock] > 0:
            self.change += transaction_cost
            self.stocks_owned[stock] -= shares_to_transact

    
    def calculateTotalValue(self):
        total_value = self.change
        for stock, quantity in self.stocks_owned.items():
            current_price = self.threads[stock].getLastClosePrice() if stock in self.threads else 0
            total_value += current_price * quantity if current_price else 0
        return total_value

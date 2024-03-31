import pandas as pd

class TradeFrame:
    
    def __init__(self, time=15) -> None:
        self.time = time
        self.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Signal', 'Capital']
        self.data = {column: [] for column in self.columns}
        self.frame = pd.DataFrame(data=self.data)

    def getFrame(self):
        return self.frame
    
    def getLastRow(self):
        if not self.frame.empty: return self.frame.tail(1)
        else: return None
    
    def setFrame(self, dataF: pd.DataFrame):
        self.frame = dataF
        return True

    def exportFrame(self, path:str):
        self.frame.to_json(path, orient='records', date_format='iso')
        return True

    def addRow(self, row:list):
        row_with_default_signal = row + [None, None]  # Default signal value
        if len(row_with_default_signal) != len(self.columns):
            print("Error: The row does not have the correct number of elements.")
            return False

        new_row_df = pd.DataFrame([row_with_default_signal], columns=self.columns)
        self.frame = pd.concat([self.frame, new_row_df], ignore_index=True)
        return True
    

    def updateActions(self, datetime:str, signal:int, capital:int):
        row_indices = self.frame[self.frame['Datetime'] == datetime].index
        if not row_indices.empty:
            for row_index in row_indices:
                self.frame.at[row_index, 'Signal'] = signal
                self.frame.at[row_index, 'Capital'] = capital
            return True
        else:
            print(f"Error: No row found with the specified datetime {datetime}.")
            return False
        

    
    def loadFrame(self, path:str):
        self.frame = pd.read_json(path, convert_dates=['Datetime'])
        return True

    def __str__(self) -> str:
        return str(self.frame)

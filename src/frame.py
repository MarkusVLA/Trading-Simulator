import pandas as pd

class TradeFrame:
    
    def __init__(self):
        self.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Signal', 'Capital', 'Holding']
        self.frame = pd.DataFrame(columns=self.columns)
        self.frame.index.name = 'Datetime'

    def getFrame(self):
        return self.frame
    
    def getLastRow(self):
        return self.frame.iloc[-1:] if not self.frame.empty else None
      
    def setFrame(self, dataF: pd.DataFrame):
        self.frame = dataF
        if 'Datetime' not in self.frame.columns:
            self.frame.index.name = 'Datetime'
        return True

    def exportFrame(self, path:str):
        self.frame.to_json(path, orient='index', date_format='iso')
        return True

    def upsertRow(self, datetime: str, **kwargs):
        """
        Update an existing row with the given datetime if it exists, 
        or insert a new row if it doesn't. Additional data for the row 
        can be provided as keyword arguments.
        """
        
        if datetime in self.frame.index:
            # Update existing row
            for key, value in kwargs.items():
                if key in self.frame.columns:
                    self.frame.at[datetime, key] = value
        else:
            new_row_data = {key: value for key, value in kwargs.items() if key in self.columns}
            new_row_df = pd.DataFrame([new_row_data], index=[pd.to_datetime(datetime)])
            new_row_df = new_row_df.dropna(axis=1, how='all') 
            new_row_df = new_row_df.fillna(0)  
            for col in self.frame.columns:
                if col not in new_row_df:
                    new_row_df[col] = 0  
            self.frame = pd.concat([self.frame, new_row_df[self.frame.columns]])
        return True
    

    def loadFrame(self, path:str):
        self.frame = pd.read_json(path, convert_dates=['Datetime'], orient='index')
        self.frame.index.name = 'Datetime'
        return True

    def __str__(self) -> str:
        return str(self.frame)

import pandas as pd

class TradeFrame:
    
    def __init__(self):
        self.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Signal', 'Capital', 'Holding']
        # Initialize DataFrame with DatetimeIndex
        self.frame = pd.DataFrame(columns=self.columns)
        self.frame.index.name = 'Datetime'

    def getFrame(self):
        return self.frame
    
    def getLastRow(self):
        if not self.frame.empty: 
            return self.frame.iloc[-1:]
        else: 
            return None
    
    def setFrame(self, dataF: pd.DataFrame):
        self.frame = dataF
        if 'Datetime' not in self.frame.columns:
            self.frame.index.name = 'Datetime'
        return True

    def exportFrame(self, path:str):
        # When exporting, include the index (Datetime) in the export
        self.frame.to_json(path, orient='index', date_format='iso')
        return True

    def upsertRow(self, datetime: str, **kwargs):
        """
        Update an existing row with the given datetime if it exists, 
        or insert a new row if it doesn't. Additional data for the row 
        can be provided as keyword arguments.
        """

        print(f"upsert: {datetime}")
        
        if datetime in self.frame.index:
            # Update existing row
            for key, value in kwargs.items():
                if key in self.frame.columns:
                    self.frame.at[datetime, key] = value
        else:
            # Insert new row
            new_row_data = {}
            for key, value in kwargs.items():
                if key in self.columns:  # Ensure 'Datetime' is not in columns
                    new_row_data[key] = value

            # Append the new row to the DataFrame
            self.frame = self.frame.append(pd.DataFrame([new_row_data], index=[pd.to_datetime(datetime)]))
        
        return True

    def loadFrame(self, path:str):
        # Ensure that 'Datetime' is considered the index when loading
        self.frame = pd.read_json(path, convert_dates=['Datetime'], orient='index')
        self.frame.index.name = 'Datetime'
        return True

    def __str__(self) -> str:
        return str(self.frame)

import pandas as pd

class TradeFrame:
    

    def __init__(self):
        self.columns = ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Signal', 'Capital', 'Holding']
        self.frame = pd.DataFrame(columns=self.columns)

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

    def upsertRow(self, datetime: str, **kwargs):
        """
        Update an existing row with the given datetime if it exists, 
        or insert a new row if it doesn't. Additional data for the row 
        can be provided as keyword arguments.
        """

        print(f"upsert: {datetime}")

        # Check if the datetime exists in the DataFrame
        row_indices = self.frame[self.frame['Datetime'] == datetime].index

        if not row_indices.empty:
            # If row exists, update it
            for row_index in row_indices:
                for key, value in kwargs.items():
                    self.frame.at[row_index, key] = value
        else:
            # If row does not exist, create and insert a new row
            new_row_data = {'Datetime': datetime}
            # Ensure only columns other than 'Datetime' are considered for additional data
            for key, value in kwargs.items():
                if key in self.frame.columns and key != 'Datetime':
                    new_row_data[key] = value

            new_row_df = pd.DataFrame([new_row_data])
            self.frame = pd.concat([self.frame, new_row_df], ignore_index=True)
        
        return True


    
    def loadFrame(self, path:str):
        self.frame = pd.read_json(path, convert_dates=['Datetime'])
        return True

    def __str__(self) -> str:
        return str(self.frame)

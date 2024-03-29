from alpha_vantage.timeseries import TimeSeries

def fetch_data_alpha_vantage(symbol, api_key='BTYCZ3XQ4UTBF6D4'):
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min', outputsize='full')
    return data

# Example usage
api_key = 'YOUR_ALPHA_VANTAGE_API_KEY'  # Replace with your actual API key
symbol = 'MSFT'  # Example stock symbol
data = fetch_data_alpha_vantage(symbol, api_key)
print(data.head())

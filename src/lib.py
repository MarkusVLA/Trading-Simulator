import pandas as pd
import yfinance as yf
from random import randint
import numpy as np

class Trader:
    
    def __init__(self, short_window=40, long_window=100):
        self.short_window = short_window
        self.long_window = long_window

    def decideRandom(self, prices, volumes):
        return randint(0,2)

    def calculate_rsi(self, prices, window=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def decideRSI(self, prices, volumes):
        if len(prices) < 50:  # Ensure there's enough data for analysis (for both RSI and SMA)
            return 0  # Do nothing if not enough data
        
        rsi = self.calculate_rsi(prices)
        sma50 = prices.rolling(window=50).mean()

        # Current and previous conditions to filter out only the crossover
        current_rsi = rsi.iloc[-1]
        previous_rsi = rsi.iloc[-2]
        price_above_sma = prices.iloc[-1] > sma50.iloc[-1]
        price_below_sma = prices.iloc[-1] < sma50.iloc[-1]

        if current_rsi > 30 and previous_rsi <= 30 and price_above_sma:
            return 1  # Buy signal
        elif current_rsi < 70 and previous_rsi >= 70 and price_below_sma:
            return 2  # Sell signal
        return 0  # Do nothing
    
    def decideMACDVolume(self, prices, volumes):
        if len(prices) < 30 or len(volumes) < 10:  # Ensure there's enough data for analysis
            return 0  # Do nothing if not enough data

        # Calculate MACD and Signal line
        ema12 = prices.ewm(span=12, adjust=False).mean()
        ema26 = prices.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal_line = macd.ewm(span=9, adjust=False).mean()

        # Volume Filter: Check if current volume is above the recent average
        avg_volume_last_10 = volumes[-10:].mean()
        current_volume = volumes.iloc[-1]

        # MACD Crossover Strategy with Volume Filter
        if macd.iloc[-2] < signal_line.iloc[-2] and macd.iloc[-1] > signal_line.iloc[-1] and current_volume > avg_volume_last_10:
            return 1  # Buy signal
        elif macd.iloc[-2] > signal_line.iloc[-2] and macd.iloc[-1] < signal_line.iloc[-1] and current_volume > avg_volume_last_10:
            return 2  # Sell signal
        return 0  # Do nothing
    
    
    def decideFourier(self, prices, volumes):
        if len(prices) < 30:  # Ensure there's enough data for analysis
            return 0  # Do nothing if not enough data
        
        # Apply Fourier Transform
        prices_fft = np.fft.fft(prices)
        frequencies = np.fft.fftfreq(len(prices))
        
        amplitudes = np.abs(prices_fft)[1:]
        dominant_freq_index = np.argmax(amplitudes) + 1  # +1 to correct for the excluded zero frequency
        dominant_frequency = frequencies[dominant_freq_index]
        dominant_amplitude = amplitudes[dominant_freq_index - 1]  # Correcting index for zero frequency
        phase = np.angle(prices_fft[dominant_freq_index])

        if np.sin(phase) > 0:  # Upcoming upswing
            return 1  # Buy signal
        elif np.sin(phase) < 0:  # Upcoming downturn
            return 2  # Sell signal
        return 0  # Do nothing

    

def simulate_trading(data_frame, trading_strategy, starting_cash=1000):

    if not isinstance(data_frame.index, pd.DatetimeIndex):
        data_frame.index = pd.to_datetime(data_frame.index)

    positions = []
    cash = starting_cash 
    stock_quantity = 0  
    profit_loss = 0  

    for date, row in data_frame.iterrows():
        current_prices = data_frame.loc[:date, 'Close']
        decision = trading_strategy(current_prices)
        price = row['Close']
        
        if decision == 1 and cash >= price:  
            stock_quantity += 1  
            cash -= price 
            positions.append(('Buy', date, price, stock_quantity))
        
        elif decision == 2 and stock_quantity > 0: 
            stock_quantity -= 1  
            cash += price
            profit_loss += (price - positions[-1][2])  
            positions.append(('Sell', date, price, stock_quantity))
    
    final_value = cash + (stock_quantity * data_frame['Close'].iloc[-1])
    profit_loss += final_value - starting_cash 

    return positions, profit_loss


def calculate_performance_score(final_profit_loss, dataF, starting_capital):
    high_price = dataF['Close'].max()
    low_price = dataF['Close'].min()
    max_shares = starting_capital / low_price
    max_possible_gain = (high_price - low_price) * max_shares
    performance_score = (final_profit_loss / max_possible_gain) * 100 if max_possible_gain != 0 else 0
    return performance_score
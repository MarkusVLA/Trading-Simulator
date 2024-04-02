import numpy as np
import pandas as pd


def decideMACDVolume(df):
    # Ensure there's enough data for analysis
    if len(df) < 30:
        return 0  # Hold signal due to insufficient data

    # Calculate MACD and Signal line
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal_line = macd.ewm(span=9, adjust=False).mean()

    # Add MACD and signal line to the dataframe (optional)
    df['MACD'] = macd
    df['Signal_Line'] = signal_line

    # Volume Filter: Check if current volume is above the recent average
    avg_volume_last_10 = df['Volume'].tail(10).mean()
    current_volume = df['Volume'].iloc[-1]

    # MACD Crossover Strategy with Volume Filter
    if macd.iloc[-2] < signal_line.iloc[-2] and macd.iloc[-1] > signal_line.iloc[-1] and current_volume > avg_volume_last_10:
        return 1  # Buy signal
    elif macd.iloc[-2] > signal_line.iloc[-2] and macd.iloc[-1] < signal_line.iloc[-1] and current_volume > avg_volume_last_10:
        return 2  # Sell signal
    return 0  # Hold signal


def applyFourierTransform(df):
    """
    Apply Fourier Transform to the closing prices to identify dominant frequencies.
    """
    if len(df) < 30:
        return 0
    
    close_fft = np.fft.fft(np.asarray(df['Close'].tolist()))
    fft_df = pd.DataFrame({'fft': close_fft})
    fft_df['absolute'] = fft_df['fft'].apply(lambda x: np.abs(x))
    fft_df['angle'] = fft_df['fft'].apply(lambda x: np.angle(x))
    
    # Select the dominant frequencies. This example arbitrarily chooses frequencies.
    dominant_freqs = fft_df.sort_values('absolute', ascending=False).head(3)
    
    # Inverse transform using dominant frequencies only for reconstruction
    fft_list = np.asarray(fft_df['fft'].tolist())
    fft_list[np.abs(fft_list) < np.max(dominant_freqs['absolute'])] = 0
    reconstructed_prices = np.fft.ifft(fft_list)
    
    df['reconstructed'] = reconstructed_prices
    
    # Generate buy/sell signals based on the direction of the reconstructed signal
    if df.iloc[-2]['reconstructed'] < df.iloc[-1]['reconstructed'] and df.iloc[-1]['Close'] < df.iloc[-1]['reconstructed']:
        return 1  # Buy signal
    elif df.iloc[-2]['reconstructed'] > df.iloc[-1]['reconstructed'] and df.iloc[-1]['Close'] > df.iloc[-1]['reconstructed']:
        return 2  # Sell signal
    return 0  # Hold signal
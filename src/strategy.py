import numpy as np
import pandas as pd



def applyFourierTransform(df):
    """
    Apply Fourier Transform to the closing prices to identify dominant frequencies.
    """
    if len(df) < 20:
        return 0
    
    close_fft = np.fft.fft(np.asarray(df['Close'].tolist()))
    fft_df = pd.DataFrame({'fft': close_fft})
    fft_df['absolute'] = fft_df['fft'].apply(lambda x: np.abs(x))
    fft_df['angle'] = fft_df['fft'].apply(lambda x: np.angle(x))
    
    dominant_freqs = fft_df.sort_values('absolute', ascending=False).head(3)
    
    fft_list = np.asarray(fft_df['fft'].tolist())
    fft_list[np.abs(fft_list) < np.max(dominant_freqs['absolute'])] = 0
    reconstructed_prices = np.fft.ifft(fft_list)
    
    df['reconstructed'] = reconstructed_prices
    
    if df.iloc[-2]['reconstructed'] < df.iloc[-1]['reconstructed'] and df.iloc[-1]['Close'] < df.iloc[-1]['reconstructed']:
        return 1 
    elif df.iloc[-2]['reconstructed'] > df.iloc[-1]['reconstructed'] and df.iloc[-1]['Close'] > df.iloc[-1]['reconstructed']:
        return 2  
    return 0  
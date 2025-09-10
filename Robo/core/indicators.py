import pandas as pd
import numpy as np

def sma(df, window):
    return df['Close'].rolling(window).mean()

def atr(df, window=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window).mean()

def rsi(df, window=14):
    delta = df['Close'].diff()
    up, down = delta.clip(lower=0), -1*delta.clip(upper=0)
    ma_up = up.ewm(alpha=1/window, adjust=False).mean()
    ma_down = down.ewm(alpha=1/window, adjust=False).mean()
    rs = ma_up / ma_down
    return 100 - (100 / (1 + rs))

def compute_indicators(df):
    df = df.copy()
    df['SMA_20'] = sma(df, 20)
    df['SMA_50'] = sma(df, 50)
    df['ATR_14'] = atr(df)
    df['RSI_14'] = rsi(df)
    df['Volatility'] = df['Close'].pct_change().rolling(21).std() * np.sqrt(252)
    return df

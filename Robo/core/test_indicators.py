import pandas as pd
import numpy as np
from core.indicators import sma, atr, rsi, compute_indicators

def test_sma():
    df = pd.DataFrame({'Close': [1,2,3,4,5]})
    result = sma(df, 3)
    assert np.isnan(result.iloc[1])
    assert result.iloc[2] == 2
    assert result.iloc[4] == 4

def test_atr():
    df = pd.DataFrame({'High': [2,3,4], 'Low': [1,2,3], 'Close': [1.5,2.5,3.5]})
    result = atr(df, 2)
    assert len(result) == 3
    assert np.isnan(result.iloc[0])

def test_rsi():
    df = pd.DataFrame({'Close': [1,2,3,2,1,2,3,4,5,6]})
    result = rsi(df, 3)
    assert len(result) == 10
    assert result.iloc[1] == 100.0

def test_compute_indicators():
    df = pd.DataFrame({
        'Close': np.arange(1, 51),
        'High': np.arange(2, 52),
        'Low': np.arange(1, 51)
    })
    out = compute_indicators(df)
    assert 'SMA_20' in out.columns
    assert 'SMA_50' in out.columns
    assert 'ATR_14' in out.columns
    assert 'RSI_14' in out.columns
    assert 'Volatility' in out.columns

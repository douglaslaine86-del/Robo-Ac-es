import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
import os

class DataProvider:
    def __init__(self):
        url = os.getenv('DATABASE_URL', 'sqlite:///data/stock_data.db')
        self.engine = create_engine(url)

    def get_history(self, symbol, start=None, end=None, period='2y'):
        ticker = yf.Ticker(symbol)
        try:
            df = ticker.history(start=start, end=end, period=period)
            if df.empty:
                return None
            df = df.reset_index()
            df.rename(columns={'Date':'Datetime'}, inplace=True)
            return df
        except Exception:
            return None

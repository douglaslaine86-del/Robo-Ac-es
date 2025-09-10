
# api/main.py atualizado com endpoint /realtime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import datetime as dt
from services.data_provider import DataProvider
from core.indicators import compute_indicators

app = FastAPI(title='Stock Analyzer API')
provider = DataProvider()

class BacktestRequest(BaseModel):
    symbol: str
    start: str
    end: str

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.get('/price/{symbol}')
def price(symbol: str):
    df = provider.get_history(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail='Symbol not found')
    return df.tail(50).to_dict(orient='records')

@app.post('/indicators')
def indicators(req: BacktestRequest):
    df = provider.get_history(req.symbol, req.start, req.end)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail='No data')
    return compute_indicators(df).to_dict(orient='records')

# Endpoint mock de tempo real (simulação de Profit)
@app.get('/realtime/{symbol}')
def realtime(symbol: str):
    now = dt.datetime.now()
    times = pd.date_range(end=now, periods=30, freq='1min')
    base_price = 100 + np.random.randn() * 5
    close = np.cumsum(np.random.randn(len(times))) + base_price
    open_ = close + np.random.randn(len(times)) * 0.2
    high = np.maximum(open_, close) + np.random.rand(len(times)) * 0.3
    low = np.minimum(open_, close) - np.random.rand(len(times)) * 0.3
    df = pd.DataFrame({'Datetime': times,
                       'Open': open_,
                       'High': high,
                       'Low': low,
                       'Close': close})
    return df.to_dict(orient='records')

import pandas as pd
from services.data_provider import DataProvider
from core.indicators import compute_indicators

provider = DataProvider()

df = provider.get_history('AAPL', period='1y')
if df is None:
    print('Sem dados')
else:
    df = compute_indicators(df)
    df['signal'] = (df['SMA_20'] > df['SMA_50']).astype(int)
    df['positions'] = df['signal'].diff().fillna(0)
    # Exporta para CSV para uso no Profit
    df[['Datetime','Close','SMA_20','SMA_50','positions']].to_csv('sinais_profit.csv', index=False)
    print('Arquivo sinais_profit.csv gerado com sucesso!')
    print(df[['Datetime','Close','SMA_20','SMA_50','positions']].tail(20))

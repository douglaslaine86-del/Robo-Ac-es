from services.data_provider import DataProvider

symbols = ['AAPL','MSFT','GOOG']
provider = DataProvider()
for s in symbols:
    df = provider.get_history(s, period='2y')
    print(s, '->', None if df is None else len(df))

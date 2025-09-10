import requests

TWELVE_DATA_API_KEY = "d8aa993b9ae14784b7a833406cc52c88"

symbols = ["winv25", "wdof25"]
for symbol in symbols:
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1min&outputsize=10&apikey={TWELVE_DATA_API_KEY}"
    r = requests.get(url)
    print(f"\nResultado para {symbol}:")
    print(r.json())

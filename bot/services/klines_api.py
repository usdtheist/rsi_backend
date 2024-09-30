from binance.client import Client
from bot.services.trading_functions  import calculate_rsi
# import talib
# import numpy as np

class GetKliesApi:
  def __init__(self, api_key, api_secret, pair="WUSDT", interval="1m"):
    self.api_key = api_key
    self.api_secret = api_secret
    self.pair = pair
    self.interval = interval
    self.closed_prices = []

  def run(self):
    print("coin", self.pair)
    limit = 100
    client =  Client(self.api_key, self.api_secret)
    klines = client.get_klines(symbol=self.pair, interval=self.interval, limit=limit)
    print(klines)
    self.closed_prices = [float(kline[4]) for kline in klines]
    print("close_price")
    print(self.closed_prices)

    # rsi_6 = talib.RSI(np.array(self.closed_prices), timeperiod=6)[-1]
    # rsi_14 = talib.RSI(np.array(self.closed_prices), timeperiod=14)[-1]
    rsi_6 = calculate_rsi(self.closed_prices, window=6)
    rsi_14 = calculate_rsi(self.closed_prices, window=14)

    print("THE RSI 6= ", rsi_6)
    print("THE RSI 14= ", rsi_14)

    print('Returning closed klines ----------------------------------------------------')
    return self.closed_prices[-99:]

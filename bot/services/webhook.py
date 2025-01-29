import websocket
import json
import ssl
import asyncio
import logging
from bot.services.trading_functions import start_trading, calculate_rsi, sell_everything
from decimal import Decimal
from api.models import Coin

RSI_PERIOD = 14

class WebSocketClient:
  def __init__(self, socket_url, closes, interval="1m", coin="WUSDT"):
    self.coin = coin
    self.socket_url = socket_url
    self.closes = closes
    self.opens = []
    self.interval = interval
    self.db_coin = Coin.objects.get(name=coin)

  def on_open(self, ws):
    print(f'Opened connection to {self.socket_url}')

  def on_close(self, ws):
    print(f'Closed connection to {self.socket_url}')

  def on_message(self, ws, message):
    print(f'Received message from {self.socket_url}')
    try:
      json_message = json.loads(message)
      candle = json_message['k']
      is_candle_closed = candle['x']
      close = candle['c']

      if is_candle_closed:
        print(f"Candle closed at: {close} -------------------")
        self.closes.append(float(close))
        self.closes = self.closes[-100:]
        self.opens = []
      else:
        print(f"Candle open at: {close}")
        self.opens = [float(close)]

      if self.db_coin.bottom_value > Decimal(close):
        print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
        print('db value', self.db_coin.bottom_value, 'coin value', Decimal(close))
        print('-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-')
        sell_everything(self.db_coin)
      elif len(self.closes) >= RSI_PERIOD:
        rsi_6 = round(calculate_rsi(self.closes + self.opens, window=6), 2)
        rsi_14 = round(calculate_rsi(self.closes + self.opens, window=14), 2)

        print(f"====================================================>>>>>>>>    THE RSI 6: {rsi_6} of {self.coin}({self.interval})")
        print(f"====================================================>>>>>>>>    THE RSI 14: {rsi_14} of {self.coin}({self.interval})")

        start_trading(rsi_6, rsi_14, self.interval, self.coin)

    except Exception as e:
      print(f"Error processing message: {e}")

  def on_error(self, ws, error):
    print(f"Error on {self.socket_url}: {error}")

  def on_ping(self, ws, message):
    print(f"Ping received from {self.socket_url}")

  def on_pong(self, ws, message):
    print(f"Pong received from {self.socket_url}")

  def run(self):
    ws = websocket.WebSocketApp(
      self.socket_url,
      on_open=self.on_open,
      on_close=self.on_close,
      on_message=self.on_message,
      on_error=self.on_error,
      on_ping=self.on_ping,
      on_pong=self.on_pong
    )
    while True:
      try:
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
      except KeyboardInterrupt:
        print(f"WebSocket connection to {self.socket_url} manually closed")
        break
      except Exception as e:
        print(f"WebSocket connection error on {self.socket_url}: {e}. Retrying in 5 seconds...")
        asyncio.sleep(5)

import websocket
import json
import ssl
import asyncio
import logging
from bot.services.trading_functions import start_trading, calculate_rsi

RSI_PERIOD = 14

class WebSocketClient:
  def __init__(self, socket_url, closes, interval="1m", coin="WUSDT"):
    self.coin = coin
    self.socket_url = socket_url
    self.closes = closes
    self.opens = []
    self.interval = interval
    self.logger = self.setup_logger(coin.lower(), interval)

  def setup_logger(self, coin, interval):
    logger = logging.getLogger(f"{coin}_{interval}")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(f"log/{coin}_{interval}_rsi_values.log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

  def on_open(self, ws):
    self.logger.info(f'Opened connection to {self.socket_url}')

  def on_close(self, ws):
    self.logger.info(f'Closed connection to {self.socket_url}')

  def on_message(self, ws, message):
    print(f'Received message from {self.socket_url}')
    try:
      json_message = json.loads(message)
      candle = json_message['k']
      is_candle_closed = candle['x']
      close = candle['c']

      if is_candle_closed:
        self.logger.info(f"Candle closed at: {close} -------------------")
        self.closes.append(float(close))
        self.closes = self.closes[-100:]
        self.opens = []
      else:
        self.logger.info(f"Candle open at: {close}")
        self.opens = [float(close)]

      if len(self.closes) >= RSI_PERIOD:
        rsi_6 = round(calculate_rsi(self.closes + self.opens, window=6), 2)
        rsi_14 = round(calculate_rsi(self.closes + self.opens, window=14), 2)

        self.logger.info(f"====================================================>>>>>>>>    THE RSI 6: {rsi_6}")
        self.logger.info(f"====================================================>>>>>>>>    THE RSI 14: {rsi_14}")
        self.logger.info("-=-=-=-=-=-=-=-=-=-=-")
        # if rsi_6 <= 30 or rsi_14 <= 30 or rsi_6 >= 70 or rsi_14 >= 70:
        start_trading(rsi_6, rsi_14, self.interval, self.coin, self.logger)

    except Exception as e:
      self.logger.error(f"Error processing message: {e}")

  def on_error(self, ws, error):
    self.logger.error(f"Error on {self.socket_url}: {error}")

  def on_ping(self, ws, message):
    self.logger.info(f"Ping received from {self.socket_url}")

  def on_pong(self, ws, message):
    self.logger.info(f"Pong received from {self.socket_url}")

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
        self.logger.info(f"WebSocket connection to {self.socket_url} manually closed")
        break
      except Exception as e:
        self.logger.error(f"WebSocket connection error on {self.socket_url}: {e}. Retrying in 5 seconds...")
        asyncio.sleep(5)

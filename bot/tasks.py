from celery import shared_task
from bot.services.webhook import WebSocketClient
from bot.services.klines_api import GetKliesApi
import asyncio

@shared_task
def register_webhook(api_key, secret_key, interval, coin):
  closed_klines = GetKliesApi(api_key, secret_key, interval=interval).run()
  socket_url = f"wss://stream.binance.com:9443/ws/{coin.lower()}@kline_{interval}"
  client = WebSocketClient(socket_url, closed_klines, interval=interval, coin=coin)
  client.run()
